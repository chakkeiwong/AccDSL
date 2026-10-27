"""Exact annual-07/08 source preparation; recognition remains unevaluated."""
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
PRIOR = ROOT / 'data/accounting-master/apple-component-availability-20261010/run-manifest.json'
PLAN = ROOT / 'docs/plans/accounting-apple-quality-inventory-20261010.md'
POINTERS = ['docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md', 'docs/plans/accounting-master-current.md']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))
norm = lambda s: ' '.join(s.split())


def save(name, value):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(hashes):
    bad = [n for n, h in hashes.items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
    assert not bad, bad[:8]


def main():
    started, timer = datetime.now(timezone.utc), time.monotonic()
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
    save('baseline.json', dict(recorded_at=started.isoformat(),
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        prior_manifest=rel(PRIOR), prior_manifest_sha256=sha(PRIOR),
        prior_completion_sha256=sha(PRIOR.with_name('completion.json')),
        prior_artifact_count=len(prior['artifact_hashes']), pointer_relocations=pointers,
        requirements_path='docs/plans/accounting-mission-requirements.md',
        requirements_sha256=sha(ROOT / 'docs/plans/accounting-mission-requirements.md'), baseline_pdf=prior['pdf']))
    inventory = ROOT / 'data/accounting-master/apple-risk-coverage-20261010/risk-coverage.json'
    coverage_path = PRIOR.with_name('coverage-update.json')
    txt, pdf = (ROOT / ('docs/design/cases/apple/annual-2024.' + suffix) for suffix in ['txt', 'pdf'])
    inputs = {rel(p): sha(p) for p in [PRIOR, PRIOR.with_name('completion.json'), PLAN, inventory, coverage_path, txt, pdf]}
    checks, meaning = [], []
    ck = lambda n, b: checks.append(dict(id=n, passed=bool(b)))
    mk = lambda n, b: meaning.append(dict(id=n, passed=bool(b)))
    for p in [txt, pdf]:
        ck(rel(p) + ' pinned hash', sha(p) == prior['artifact_hashes'][rel(p)])
    t, doc = txt.read_text(), fitz.open(pdf)
    original, page = norm(' '.join(p.get_text() for p in doc)), norm(doc[11].get_text())
    coverage = read(coverage_path)
    spans, units = {}, []
    for index, count in [(7, 1), (8, 2)]:
        r = next(x for x in read(inventory)['records'] if x['source'] == 'annual' and x['index'] == index)
        entry = next(x for x in coverage['records'] if x['source'] == 'annual' and x['index'] == index)
        ident = f'annual-{index:02}'
        ck(ident + ' unworked at entry', entry['retention_status'] == 'no prior retained reading')
        q = t[r['start']:r['body_end']]
        p = OUT / 'sources' / (ident + '.txt')
        p.parent.mkdir(exist_ok=True)
        with p.open('x') as f:
            f.write(q)
        ck(ident + ' full body exact', q == (ROOT / r['body_path']).read_text())
        body = t[r['heading_end']:r['body_end']]
        ck(ident + ' no page furniture', 'Apple Inc. |' not in body and '\f' not in body)
        row_units = []
        for i, m in enumerate(re.finditer(r'\S.*?(?=\n\s*\n|\Z)', body, re.S), 1):
            a, b = r['heading_end'] + m.start(), r['heading_end'] + m.end()
            quote = t[a:b]
            row = dict(id=ident + f'.p{i}', source='annual', start=a, end=b, quote=quote,
                       quote_sha256=hashlib.sha256(quote.encode()).hexdigest())
            row_units.append(row)
            ck(row['id'] + ' exact source', t[a:b] == quote)
            mk(row['id'] + ' original page 12', norm(quote) in page)
        ck(ident + ' expected full partition', len(row_units) == count and norm(body) == norm(' '.join(x['quote'] for x in row_units)))
        mk(ident + ' heading original page 12', norm(t[r['start']:r['heading_end']]) in page)
        spans[ident] = dict(source='annual', start=r['start'], end=r['body_end'], heading_end=r['heading_end'],
            quote=q, quote_sha256=sha(p), path=rel(p), page=12, printed_page=9)
        units += row_units
    dependencies = []
    for name, key, ident in [('apple-assets-20261008', 'dependencies', 'annual.fifo'),
                             ('apple-assets-20261008', 'units', 'annual.note.5.expense'),
                             ('apple-commitments-20261008', 'units', 'annual.note.12.purchases'),
                             ('apple-commitments-20261008', 'dependencies', 'annual.mda_manufacturing'),
                             ('apple-perimeter-20261009', 'dependencies', 'annual.outsourcing_risk')]:
        p = ROOT / 'data/accounting-master' / name / 'source-claim-supplement.json'
        manifest = p.with_name('run-manifest.json')
        values = read(p)[key]
        x = values[ident] if isinstance(values, dict) else next(x for x in values if x['id'] == ident)
        a, b = x.get('start', x.get('source_start')), x.get('end', x.get('source_end'))
        inputs.update({rel(p): sha(p), rel(manifest): sha(manifest)})
        ck(ident + ' frozen supplement', read(manifest)['artifact_hashes'][rel(p)] == sha(p))
        ck(ident + ' exact source', t[a:b] == x['quote'])
        mk(ident + ' original text', norm(x['quote']) in original)
        dependencies.append(dict(id=ident, source='annual', start=a, end=b, quote=x['quote'],
            quote_sha256=hashlib.sha256(x['quote'].encode()).hexdigest(), prior_supplement=rel(p), prior_manifest=rel(manifest)))
    paragraphs = {x['id']: norm(x['quote']) for x in units}
    for ident, anchors in {
        'annual-07.p1': ['third parties', 'personal injury', 'including health', 'outages, service slowdowns or errors',
                        'have not performed as anticipated', 'artificial intelligence features', 'no assurance',
                        'exploited by third parties', 'product liability claims, recalls', 'intangible assets',
                        'warranty and other expenses', 'delay in new product and service introductions'],
        'annual-08.p1': ['obsolete or exceed anticipated demand', 'cost exceeds net realizable value',
                        'necessary cancellation fee reserves', 'capital assets held at its suppliers’ facilities',
                        'inventory prepayments', 'If the Company determines', 'currently recoverable', 'no assurance'],
        'annual-08.p2': ['in advance of product announcements and shipments', 'typically for periods up to 150 days',
                        'forecast incorrectly', 'excess or insufficient', 'not fully utilize firm purchase commitments']}.items():
        for anchor in anchors:
            mk(ident + ' qualification: ' + anchor, anchor in paragraphs[ident])
    save('source-claim-supplement.json', dict(spans=spans, units=units, dependencies=dependencies,
        coverage=dict(risk_bodies=2, paragraphs=3, dependencies=5,
                      meaning='Author source preparation, not operative recognition or independent semantic acceptance')))
    save('source-checks.json', dict(checker_sha256=sha(Path(__file__)), inputs=inputs, checks=checks,
        passed=sum(x['passed'] for x in checks), failed=sum(not x['passed'] for x in checks)))
    save('meaning-checks.json', dict(inputs={**inputs, rel(Path(__file__)): sha(Path(__file__)),
        rel(OUT / 'source-claim-supplement.json'): sha(OUT / 'source-claim-supplement.json')}, checks=meaning,
        passed=sum(x['passed'] for x in meaning), failed=sum(not x['passed'] for x in meaning),
        status='Original text and qualification anchors; author interpretation separately reviewed'))
    p = OUT / 'inspection/page-012.png'
    p.parent.mkdir(exist_ok=True)
    doc[11].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(p)
    save('inspection/manifest.json', [dict(path=rel(p), sha256=sha(p), page=12, pdf=rel(pdf))])
    for index in [7, 8]:
        entry = next(x for x in coverage['records'] if x['source'] == 'annual' and x['index'] == index)
        entry.update(retention_status='complete body retained', new_unit=rel(OUT),
            added_evidence=dict(path=rel(OUT / 'source-claim-supplement.json'), sha256=sha(OUT / 'source-claim-supplement.json')))
    for source in coverage['counts']:
        for status in coverage['counts'][source]:
            coverage['counts'][source][status] = sum(x['source'] == source and x['retention_status'] == status for x in coverage['records'])
    coverage.update(prior_coverage=rel(coverage_path), prior_coverage_sha256=sha(coverage_path), not_semantic_completion=True)
    save('coverage-update.json', coverage)
    save('source-run-receipt.json', dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(Path(__file__)),
        started_at=started.isoformat(), wall_seconds=time.monotonic()-timer,
        exit_code=0 if all(x['passed'] for x in checks+meaning) else 1))
    print(json.dumps(dict(source_checks=sum(x['passed'] for x in checks), original_checks=sum(x['passed'] for x in meaning),
                         failed=sum(not x['passed'] for x in checks+meaning))))
    assert all(x['passed'] for x in checks+meaning), [x for x in checks+meaning if not x['passed']]


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'baseline.json').exists()
    main()
