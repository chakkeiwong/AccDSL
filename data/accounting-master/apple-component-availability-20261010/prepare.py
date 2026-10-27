"""Retain and verify annual-06; no semantic or product acceptance inferred."""
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
PRIOR = ROOT / 'data/accounting-master/apple-competition-transition-20261010/run-manifest.json'
PLAN = ROOT / 'docs/plans/accounting-apple-component-availability-20261010.md'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))
norm = lambda s: ' '.join(s.split())


def save(name, obj):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def verify(hashes):
    bad = [name for name, h in hashes.items() if not (ROOT / name).is_file() or sha(ROOT / name) != h]
    assert not bad, bad[:8]


def main():
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    prior = read(PRIOR)
    assert sha(PRIOR) == read(PRIOR.with_name('completion.json'))['manifest_sha256']
    verify(prior['artifact_hashes'])
    pointers = []
    for name in POINTERS:
        p = OUT / 'pointers-before' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        assert not p.exists()
        shutil.copy2(ROOT / name, p)
        pointers.append(dict(historical_path=name, preserved_path=rel(p), sha256=sha(p)))
    save('baseline.json', dict(recorded_at=started.isoformat(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        prior_manifest=rel(PRIOR), prior_manifest_sha256=sha(PRIOR),
        prior_completion_sha256=sha(PRIOR.with_name('completion.json')),
        prior_artifact_count=len(prior['artifact_hashes']), pointer_relocations=pointers,
        requirements_path='docs/plans/accounting-mission-requirements.md',
        requirements_sha256=sha(ROOT / 'docs/plans/accounting-mission-requirements.md'),
        baseline_pdf=prior['pdf']))
    coverage_path = PRIOR.with_name('coverage-update.json')
    inventory_path = ROOT / 'data/accounting-master/apple-risk-coverage-20261010/risk-coverage.json'
    inputs = {rel(p): sha(p) for p in [PRIOR, PRIOR.with_name('completion.json'), PLAN, coverage_path, inventory_path]}
    checks, originals = [], []
    ck = lambda name, ok: checks.append(dict(id=name, passed=bool(ok)))
    mk = lambda name, ok: originals.append(dict(id=name, passed=bool(ok)))
    txt = ROOT / 'docs/design/cases/apple/annual-2024.txt'
    pdf = ROOT / 'docs/design/cases/apple/annual-2024.pdf'
    for p in [txt, pdf]:
        inputs[rel(p)] = sha(p)
        ck(rel(p) + ' pinned hash', sha(p) == prior['artifact_hashes'][rel(p)])
    t = txt.read_text()
    doc = fitz.open(pdf)
    original = norm(' '.join(p.get_text() for p in doc))
    r = next(r for r in read(inventory_path)['records'] if r['source'] == 'annual' and r['index'] == 6)
    entry = next(r for r in read(coverage_path)['records'] if r['source'] == 'annual' and r['index'] == 6)
    ck('annual-06 unworked at entry', entry['retention_status'] == 'no prior retained reading')
    q = t[r['start']:r['body_end']]
    p = OUT / 'sources/annual-06.txt'
    p.parent.mkdir(exist_ok=True)
    with p.open('x') as f:
        f.write(q)
    ck('exact full inventory body', q == (ROOT / r['body_path']).read_text())
    body = t[r['heading_end']:r['body_end']]
    furniture = list(re.finditer(r'Apple Inc\. \| 2024 Form 10-K \| 8', body))
    ck('one retained footer', len(furniture) == 1)
    meaningful = body[:furniture[0].start()]
    units = []
    for i, m in enumerate(re.finditer(r'\S.*?(?=\n\s*\n|\Z)', meaningful, re.S), 1):
        a, b = r['heading_end'] + m.start(), r['heading_end'] + m.end()
        quote = t[a:b]
        unit = dict(id=f'annual-06.p{i}', source='annual', start=a, end=b, quote=quote,
                    quote_sha256=hashlib.sha256(quote.encode()).hexdigest())
        units.append(unit)
        ck(unit['id'] + ' exact source', t[a:b] == quote)
        mk(unit['id'] + ' original page 11 text', norm(quote) in norm(doc[10].get_text()))
    ck('two complete paragraphs', len(units) == 2 and norm(meaningful) == norm(' '.join(x['quote'] for x in units)))
    mk('heading original page 11', norm(t[r['start']:r['heading_end']]) in norm(doc[10].get_text()))
    dependencies = []
    selected = [('apple-commitments-20261008', 'units', 'annual.note.12.supply'),
                ('apple-commitments-20261008', 'units', 'annual.note.12.custom'),
                ('apple-perimeter-20261009', 'dependencies', 'annual.outsourcing_risk'),
                ('apple-competition-transition-20261010', 'units', 'annual-04.p1')]
    for name, collection, ident in selected:
        p = ROOT / 'data/accounting-master' / name / 'source-claim-supplement.json'
        manifest = p.with_name('run-manifest.json')
        d = read(p)[collection]
        x = d[ident] if isinstance(d, dict) else next(x for x in d if x['id'] == ident)
        a = x.get('start', x.get('source_start'))
        b = x.get('end', x.get('source_end'))
        quote = x['quote']
        inputs.update({rel(p): sha(p), rel(manifest): sha(manifest)})
        ck(ident + ' frozen supplement', read(manifest)['artifact_hashes'][rel(p)] == sha(p))
        ck(ident + ' exact source', t[a:b] == quote)
        mk(ident + ' original text', norm(quote) in original)
        dependencies.append(dict(id=ident, source='annual', start=a, end=b, quote=quote,
            quote_sha256=hashlib.sha256(quote.encode()).hexdigest(), prior_supplement=rel(p),
            prior_manifest=rel(manifest), role='retained context; not a new risk-body closure'))
    p1, p2 = (norm(x['quote']) for x in units)
    anchors = [(p1, a) for a in ['single or limited sources', 'available from multiple sources',
        'has in the past experienced', 'Such disruptions could occur in the future',
        'extend or renew these agreements on similar terms, or at all',
        'business failure for the supplier or consolidation']] + [(p2, a) for a in [
        'only one source', 'suppliers’ yields have matured', 'common components',
        'has been delayed or constrained', 'have been adversely affected',
        'identify and obtain sufficient quantities from an alternative source']]
    for quote, anchor in anchors:
        mk('source qualification: ' + anchor, anchor in quote)
    save('source-claim-supplement.json', dict(spans={'annual-06': dict(source='annual',
        start=r['start'], end=r['body_end'], heading_end=r['heading_end'], quote=q,
        quote_sha256=sha(OUT / 'sources/annual-06.txt'), path=rel(OUT / 'sources/annual-06.txt'),
        page=11, printed_page=8)}, units=units, dependencies=dependencies,
        coverage=dict(risk_bodies=1, paragraphs=2, dependencies=4,
                      meaning='Bounded author preparation; independent semantic acceptance pending')))
    save('source-checks.json', dict(checker_sha256=sha(Path(__file__)), inputs=inputs,
        checks=checks, passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks)))
    save('meaning-checks.json', dict(inputs={**inputs, rel(Path(__file__)): sha(Path(__file__)),
        rel(OUT / 'source-claim-supplement.json'): sha(OUT / 'source-claim-supplement.json')},
        checks=originals, passed=sum(c['passed'] for c in originals), failed=sum(not c['passed'] for c in originals),
        status='Original text and qualification anchors only; author meaning review recorded separately'))
    p = OUT / 'inspection/page-011.png'
    p.parent.mkdir(exist_ok=True)
    doc[10].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(p)
    save('inspection/manifest.json', [dict(path=rel(p), sha256=sha(p), page=11, pdf=rel(pdf))])
    coverage = read(coverage_path)
    entry = next(x for x in coverage['records'] if x['source'] == 'annual' and x['index'] == 6)
    entry.update(retention_status='complete body retained', new_unit=rel(OUT),
        added_evidence=dict(path=rel(OUT / 'source-claim-supplement.json'), sha256=sha(OUT / 'source-claim-supplement.json')))
    for source in ['annual', 'interim']:
        for status in coverage['counts'][source]:
            coverage['counts'][source][status] = sum(x['source'] == source and x['retention_status'] == status for x in coverage['records'])
    coverage.update(prior_coverage=rel(coverage_path), prior_coverage_sha256=sha(coverage_path), not_semantic_completion=True)
    save('coverage-update.json', coverage)
    save('source-run-receipt.json', dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(Path(__file__)),
        started_at=started.isoformat(), wall_seconds=time.monotonic()-timer,
        exit_code=0 if all(c['passed'] for c in checks+originals) else 1))
    print(json.dumps(dict(source_checks=sum(c['passed'] for c in checks),
                         original_checks=sum(c['passed'] for c in originals),
                         failed=sum(not c['passed'] for c in checks+originals))))
    assert all(c['passed'] for c in checks+originals)


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'baseline.json').exists()
    main()
