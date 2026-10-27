"""Complete raw-source retention, keeping author/independent acceptance separate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import fitz

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'data/accounting-master/apple-quality-inventory-20261010/run-manifest.json'
PLAN = ROOT / 'docs/plans/accounting-apple-remaining-risks-20261010.md'
INDICES = [9,10,11,12,13,14,15,16,17,20,22,23,24,25,27,28]
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))
norm = lambda s: ' '.join(s.split())
FURNITURE = r'Apple Inc\. \| 2024 Form 10-K \| \d+'
clean = lambda s: re.sub(FURNITURE, '', s).replace('\f', '')


def save(n, value):
    p = OUT / n
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(h):
    bad = [n for n, v in h.items() if not (ROOT / n).is_file() or sha(ROOT / n) != v]
    assert not bad, bad[:8]


def main():
    now, timer = datetime.now(timezone.utc), time.monotonic()
    prior = read(PRIOR)
    assert sha(PRIOR) == read(PRIOR.with_name('completion.json'))['manifest_sha256']
    verify(prior['artifact_hashes'])
    pointers = []
    for n in POINTERS:
        p = OUT / 'pointers-before' / n
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        shutil.copy2(ROOT / n, p)
        pointers.append(dict(historical_path=n, preserved_path=rel(p), sha256=sha(p)))
    save('baseline.json', dict(recorded_at=now.isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        prior_manifest=rel(PRIOR), prior_manifest_sha256=sha(PRIOR), prior_completion_sha256=sha(PRIOR.with_name('completion.json')),
        prior_artifact_count=len(prior['artifact_hashes']), pointer_relocations=pointers,
        requirements_path='docs/plans/accounting-mission-requirements.md',
        requirements_sha256=sha(ROOT / 'docs/plans/accounting-mission-requirements.md'), baseline_pdf=prior['pdf']))
    inventory = ROOT / 'data/accounting-master/apple-risk-coverage-20261010/risk-coverage.json'
    coverage_path = PRIOR.with_name('coverage-update.json')
    txt, pdf = [ROOT / ('docs/design/cases/apple/annual-2024.' + x) for x in ['txt','pdf']]
    inputs = {rel(p): sha(p) for p in [PRIOR,PRIOR.with_name('completion.json'),PLAN,inventory,coverage_path,txt,pdf]}
    coverage, t, doc = read(coverage_path), txt.read_text(), fitz.open(pdf)
    original = norm(clean(' '.join(p.get_text() for p in doc)))
    checks, originals, bodies, units, furniture = [], [], [], [], []
    ck = lambda n,b: checks.append(dict(id=n,passed=bool(b)))
    mk = lambda n,b: originals.append(dict(id=n,passed=bool(b)))
    ck('declared sixteen unfinished bodies', [x['index'] for x in coverage['records'] if x['source']=='annual' and x['retention_status']!='complete body retained']==INDICES)
    for p in [txt,pdf]:
        ck(rel(p)+' pinned hash', sha(p)==prior['artifact_hashes'][rel(p)])
    for index in INDICES:
        r = next(x for x in read(inventory)['records'] if x['source']=='annual' and x['index']==index)
        entry = next(x for x in coverage['records'] if x['source']=='annual' and x['index']==index)
        ident, q = f'annual-{index:02}', t[r['start']:r['body_end']]
        p = OUT / 'sources' / (ident+'.txt')
        p.parent.mkdir(exist_ok=True)
        with p.open('x') as f:f.write(q)
        ck(ident+' expected entry status', entry['retention_status']==('partial dependency only' if index in [15,27] else 'no prior retained reading'))
        ck(ident+' exact full raw body', q==(ROOT/r['body_path']).read_text() and sha(p)==r['body_sha256'])
        heading, body = t[r['start']:r['heading_end']], t[r['heading_end']:r['body_end']]
        mk(ident+' heading original',norm(heading) in original)
        mk(ident+' complete meaningful body original',norm(clean(body)) in original)
        rows = []
        for i,m in enumerate(re.finditer(r'\S.*?(?=\n\s*\n|\Z)',body,re.S),1):
            a,b = r['heading_end']+m.start(),r['heading_end']+m.end()
            quote = t[a:b]
            if not norm(clean(quote)):
                continue
            row = dict(id=ident+f'.p{len(rows)+1}',source='annual',start=a,end=b,quote=quote,
                quote_sha256=hashlib.sha256(quote.encode()).hexdigest(),comparison='Known annual footer/form feed removed only for original-text comparison')
            rows.append(row)
            ck(row['id']+' exact quote',t[a:b]==quote)
            mk(row['id']+' original text',norm(clean(quote)) in original)
        ck(ident+' full meaningful partition',norm(clean(body))==norm(' '.join(clean(x['quote']) for x in rows)))
        for m in re.finditer(FURNITURE+'|\f',q):
            furniture.append(dict(body=ident,start=r['start']+m.start(),end=r['start']+m.end(),quote=m.group(),role='Retained raw page furniture; excluded only from meaningful comparison'))
        bodies.append(dict(id=ident,source='annual',start=r['start'],end=r['body_end'],heading_end=r['heading_end'],
            heading=heading,quote=q,quote_sha256=sha(p),path=rel(p),units=[x['id'] for x in rows]))
        units += rows
    save('source-claim-supplement.json',dict(bodies=bodies,units=units,furniture=furniture,
        coverage=dict(risk_bodies=16,paragraph_fragments=len(units),status='New raw retention; author review required before disposition, independent semantics pending')))
    save('source-checks.json',dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,
        passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks)))
    save('meaning-checks.json',dict(inputs={**inputs,rel(Path(__file__)):sha(Path(__file__)),
        rel(OUT/'source-claim-supplement.json'):sha(OUT/'source-claim-supplement.json')},checks=originals,
        passed=sum(x['passed'] for x in originals),failed=sum(not x['passed'] for x in originals),
        status='Original-text equivalence only; not independent semantic acceptance'))
    images=[]
    for n in [12,13,14,15,17,18,19,20]:
        p=OUT/'inspection'/f'page-{n:03}.png';p.parent.mkdir(exist_ok=True)
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p)
        images.append(dict(path=rel(p),sha256=sha(p),page=n,pdf=rel(pdf)))
    save('inspection/manifest.json',images)
    save('source-run-receipt.json',dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__)),
        started_at=now.isoformat(),wall_seconds=time.monotonic()-timer,exit_code=0 if all(x['passed'] for x in checks+originals) else 1))
    print(json.dumps(dict(source_checks=sum(x['passed'] for x in checks),original_checks=sum(x['passed'] for x in originals),
        failed=sum(not x['passed'] for x in checks+originals),bodies=len(bodies),paragraph_fragments=len(units))))
    assert all(x['passed'] for x in checks+originals),[x for x in checks+originals if not x['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'baseline.json').exists()
    main()
