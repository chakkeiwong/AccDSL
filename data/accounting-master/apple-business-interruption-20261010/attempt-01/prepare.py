"""Prepare the annual-02 business-interruption source unit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, subprocess, sys, time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PLAN = ROOT / 'docs/plans/accounting-apple-business-interruption-20261010.md'
FRONTIER = ROOT / 'data/accounting-master/apple-risk-coverage-20261010'
PRIOR_UNIT = ROOT / 'data/accounting-master/apple-macroeconomic-20261010'
PRIOR = PRIOR_UNIT / 'run-manifest.json'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    p = OUT / name; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f: f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


SELECTED = [
    ('apple-commitments-20261008', 'units', 'annual.note.12.supply', 'single/limited component sources, shortages and commodity prices'),
    ('apple-perimeter-20261009', 'dependencies', 'annual.distribution', 'distribution channel context'),
    ('apple-perimeter-20261009', 'dependencies', 'annual.manufacturing_mda', 'outsourcing and manufacturing context'),
    ('apple-liquidity-20261009', 'dependencies', 'annual.liquidity', 'cash, debt and contractual requirements'),
    ('apple-litigation-risk-20261010', 'spans', 'annual.operation-insurance', 'partial prior insurance dependency'),
]


def baseline():
    assert not (OUT / 'baseline.json').exists()
    prior = read(PRIOR)
    reloc = {x['historical_path']: x['preserved_path'] for x in prior['pointer_relocations']}
    assert sha(PRIOR) == read(PRIOR.with_name('completion.json'))['manifest_sha256']
    for name, digest in prior['artifact_hashes'].items():
        p = ROOT / reloc.get(name, name)
        assert sha(p) == digest, name
    pointers = []
    for name in POINTERS:
        dst = OUT / 'pointers-before' / name; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dst); pointers.append(dict(historical_path=name, preserved_path=rel(dst), sha256=sha(dst)))
    save('baseline.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        prior_manifest=rel(PRIOR), prior_manifest_sha256=sha(PRIOR), prior_completion=rel(PRIOR.with_name('completion.json')),
        prior_completion_sha256=sha(PRIOR.with_name('completion.json')), prior_artifact_count=len(prior['artifact_hashes']),
        prior_pointer_relocations=prior['pointer_relocations'], pointer_relocations=pointers,
        requirements_path='docs/plans/accounting-mission-requirements.md', requirements_sha256=sha(ROOT/'docs/plans/accounting-mission-requirements.md')))
    print(json.dumps(dict(prior_artifacts=len(prior['artifact_hashes']), pointers=len(pointers))))


def sources():
    assert (OUT / 'baseline.json').exists() and not (OUT / 'source-checks.json').exists()
    checks, refs = [], []
    ck = lambda name, ok: checks.append(dict(id=name, passed=bool(ok)))
    annual = ROOT / 'docs/design/cases/apple/annual-2024.txt'; interim = ROOT / 'docs/design/cases/apple/interim-2025q1.txt'
    at, it = annual.read_text(), interim.read_text()
    coverage = read(FRONTIER / 'risk-coverage.json')
    rec = next(x for x in coverage['records'] if x['source'] == 'annual' and x['index'] == 2)
    for p in [annual, interim, ROOT/'docs/design/cases/apple/annual-2024.pdf', ROOT/'docs/design/cases/apple/interim-2025q1.html',
              PLAN, ROOT/'docs/plans/accounting-mission-requirements.md', FRONTIER/'risk-coverage.json',
              PRIOR_UNIT/'source-claim-supplement.json', PRIOR_UNIT/'run-manifest.json', PRIOR_UNIT/'completion.json']:
        refs.append(dict(path=rel(p), sha256=sha(p)))
    inventory = ROOT / rec['body_path']
    ck('annual-02 exact inventory body', at[rec['start']:rec['body_end']] == inventory.read_text())
    ck('annual-02 prior status is partial only', rec['retention_status'] == 'partial dependency only' and len(rec['prior_overlaps']) == 1)
    overlap = rec['prior_overlaps'][0]
    overlap_source = at[overlap['start']:overlap['end']]
    ck('partial insurance dependency literal', overlap_source == (ROOT/'data/accounting-master/apple-litigation-risk-20261010/sources/annual.operation-insurance.txt').read_text())
    footer = at.find('Apple Inc. | 2024 Form 10-K | 6', rec['heading_end'], rec['body_end'])
    semantic_end = footer if footer >= 0 else rec['body_end']; semantic = at[rec['heading_end']:semantic_end]
    paragraphs=[]
    for m in re.finditer(r'\S.*?(?=\n\s*\n|\Z)', semantic, flags=re.S):
        a,b=rec['heading_end']+m.start(),rec['heading_end']+m.end();q=at[a:b]
        f=OUT/'sources'/f'annual-02-paragraph-{len(paragraphs)+1:02}.txt';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(q)
        paragraphs.append(dict(index=len(paragraphs)+1,start=a,end=b,quote=q,sha256=hashlib.sha256(q.encode()).hexdigest(),path=rel(f),file_sha256=sha(f)))
        ck(f'annual-02 paragraph {len(paragraphs)} exact',at[a:b]==q)
    ck('annual-02 known page-furniture boundary',semantic_end==39447 and rec['body_end']==39480)
    ck('annual-02 paragraph population is six',len(paragraphs)==6)
    ck('annual-02 semantic partition preserves text',' '.join(semantic.split())==' '.join(' '.join(p['quote'] for p in paragraphs).split()))
    selected=[]
    for unit,kind,key,role in SELECTED:
        supplement=ROOT/'data/accounting-master'/unit/'source-claim-supplement.json';manifest=supplement.with_name('run-manifest.json')
        d,m=read(supplement),read(manifest); ck(f'{key} manifest binding',m['artifact_hashes'][rel(supplement)]==sha(supplement))
        refs += [dict(path=rel(supplement),sha256=sha(supplement)),dict(path=rel(manifest),sha256=sha(manifest))]
        if kind=='dependencies': entry=d['dependencies'][key]
        elif kind=='spans': entry=d['spans'][key]
        else: entry=next(x for x in d['units'] if x['id']==key)
        source_id=entry.get('source_id',entry.get('source','annual'));source_path=annual if source_id=='annual' else interim;st=entry.get('start',entry.get('source_start'));en=entry.get('end',entry.get('source_end'));q=entry['quote']
        expected=entry.get('span_sha256',entry.get('sha256'));actual=hashlib.sha256(q.encode()).hexdigest()
        ck(f'{key} exact interval',source_path.read_text()[st:en]==q);ck(f'{key} quote hash',expected is None or actual==expected);ck(f'{key} extraction hash',sha(source_path)==(read(supplement).get('sources',{}).get(source_id,{}).get('extraction_sha256') or sha(source_path)))
        selected.append(dict(unit=unit,supplement=rel(supplement),supplement_sha256=sha(supplement),manifest=rel(manifest),manifest_sha256=sha(manifest),kind=kind,id=key,role=role,source_id=source_id,start=st,end=en,quote=q,quote_sha256=actual,stored_quote_sha256=expected,source_path=rel(source_path),source_sha256=sha(source_path),interpretation=entry.get('interpretation','Prior bounded source reading; meaning remains scoped.')))
    save('source-claim-supplement.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),body=dict(source='annual',heading=dict(start=rec['start'],end=rec['heading_end'],quote=at[rec['start']:rec['heading_end']]),body_start=rec['heading_end'],semantic_end=semantic_end,body_end=rec['body_end'],source_path=rel(annual),source_sha256=sha(annual),inventory_body_path=rec['body_path'],inventory_body_sha256=rec['body_sha256'],page=9,page_furniture=at[semantic_end:rec['body_end']],paragraphs=paragraphs),prior_partial_dependency=dict(start=overlap['start'],end=overlap['end'],path=overlap['json_path'],unit=overlap['unit'],quote_sha256=hashlib.sha256(overlap_source.encode()).hexdigest(),quote=overlap_source),selected_dependencies=selected,inputs=refs,limits=['No event, route, loss amount, policy limit, probability, journal or forecast inferred.','Past U.S.–China restrictions are retained as source examples, not current operative events.','Insurance wording remains a partial risk dependency, not a policy or recovery asset.']))
    report=dict(checker_sha256=sha(Path(__file__)),inputs=refs,checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),selected_dependencies=len(selected),annual_paragraphs=len(paragraphs));save('source-checks.json',report);assert report['failed']==0,[x for x in checks if not x['passed']];print(json.dumps({k:report[k] for k in ['passed','failed','selected_dependencies','annual_paragraphs']}))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1';action=sys.argv[1];start=time.monotonic();started=datetime.now(timezone.utc);code=0
    try:
        if action=='baseline':baseline()
        elif action=='sources':sources()
        else:raise SystemExit('expected baseline or sources')
    except BaseException:code=1;raise
    finally:
        with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,started_at=started.isoformat(),wall_seconds=time.monotonic()-start,exit_code=code))+'\n')
