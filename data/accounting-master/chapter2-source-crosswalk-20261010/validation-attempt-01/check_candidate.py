"""Verify the bounded source crosswalk and final manuscript without rebuilding."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import difflib
import hashlib
import json
import os
import re
import subprocess
import time

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-quality-inventory-20261010'
NEW = ROOT / 'docs/design/proposal/manuscript-service-access-20261010'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    checks, inputs = [], {}

    def ck(name, value):
        checks.append(dict(id=name, passed=bool(value)))

    def verify(mapping, name):
        bad = [p for p, h in mapping.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
        ck(name, not bad)
        if not bad:
            inputs.update(mapping)
        return bad

    base = read(OUT / 'baseline.json')
    prior_path = ROOT / base['prior_manifest']
    ck('prior manifest unchanged', sha(prior_path) == base['prior_manifest_sha256'])
    prior = read(prior_path)
    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    verify({reloc.get(p, p): h for p, h in prior['artifact_hashes'].items()},
           '877 prior references preserved, using saved live pointers')
    ck('prior reference population', len(prior['artifact_hashes']) == 877)
    protected = read(OUT / 'integration-baseline.json')
    verify(protected['protected_hashes'], 'all 56 baseline manuscript files preserved')
    ck('baseline file population', len(protected['protected_hashes']) == 56)
    ck('frozen ordered diagnosis', sha(OUT / 'ordered-reading.md') == protected['diagnosis_sha256'])
    ck('original diagnosis crosswalk preserved',
       sha(ROOT / protected['diagnosis_crosswalk_preserved_path']) == protected['crosswalk_sha256'])

    inventory = read(OUT / 'ledger-inventory.json')
    crosswalk = read(OUT / 'claim-query-crosswalk.json')
    rows, groups = crosswalk['rows'], crosswalk['author_groups']
    source_hashes = {x['path']: x['sha256'] for x in inventory['inputs']}
    verify(source_hashes, 'all 25 crosswalk input hashes')
    ck('declared input population', len(source_hashes) == 25 and inventory['input_count'] == 25)
    source_data = {p: read(ROOT / p) for p in source_hashes}
    expected = set()
    for p, data in source_data.items():
        for key in ('units', 'material_units', 'claims', 'narrative_claims', 'queries'):
            expected.update(f'{p}#/{key}/{i}' for i in range(len(data.get(key, []))))
        for i, matter in enumerate(data.get('matters', [])):
            expected.add(f'{p}#/matters/{i}')
            expected.update(f'{p}#/matters/{i}/assertions/{j}' for j in range(len(matter['assertions'])))
        expected.update(f'{p}#/body/paragraphs/{i}' for i in range(len(data.get('body', {}).get('paragraphs', []))))
    identities = [r['identity'] for r in rows]
    ck('all raw record identities represented exactly once', set(identities) == expected and len(identities) == len(expected))
    raw_equal = True
    for row in rows:
        value = source_data[row['input_path']]
        for token in row['json_pointer'].split('/')[1:]:
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        if row['record_kind'] == 'legal_source_body':
            value = {k: v for k, v in value.items() if k != 'assertions'}
        raw_equal &= value == row['content'] and row['input_sha256'] == source_hashes[row['input_path']]
        raw_equal &= row['identity'] == row['input_path'] + '#' + row['json_pointer']
    ck('JSON pointers retain exact original record content', raw_equal)
    counts = dict(Counter(r['record_kind'] for r in rows))
    ck('502 records retain their six distinct kinds', counts == crosswalk['counts_by_kind'] == {
        'retained_source_unit': 190, 'retained_source_paragraph': 10, 'legal_source_body': 8,
        'explicit_assertion': 91, 'legal_assertion': 39, 'query': 164})
    assigned = [(record, g['id']) for g in groups for record in g['records']]
    ck('82 groups assign every record once', len(groups) == 82 and len(assigned) == len(rows)
       and dict(assigned) == {r['identity']: r['author_disposition_group'] for r in rows})
    ck('no pending assignments or semantic completion claim', crosswalk['pending'] == 0
       and not crosswalk['semantic_completeness'] and crosswalk['readiness'] == 'not_ready')
    anchors_ok = True
    for g in groups:
        if g['disposition'] in {'exact_support', 'mechanism_reuse'}:
            anchors_ok &= bool(g.get('anchors'))
        for a in g.get('anchors', []):
            p = ROOT / a['path']; text = p.read_text()
            anchors_ok &= sha(p) == a['sha256'] and a['quote'] in text
            anchors_ok &= text[:text.index(a['quote'])].count('\n') + 1 == a['line']
    ck('support anchors bind actual baseline paragraphs', anchors_ok)

    check_manuscript(ck, verify, inputs, rows, groups)
    for name in ['baseline.json', 'integration-baseline.json', 'ledger-inventory.json',
                 'claim-query-crosswalk.json', 'author-dispositions.json', 'render-manifest.json',
                 'author-review.md', 'source-boundary.md', 'surface-audit.json', 'surface-disposition.md']:
        inputs[rel(OUT / name)] = sha(OUT / name)
    diff = ['git', 'diff', '--check', '--', rel(OUT), rel(NEW),
            'docs/plans/accounting-chapter2-source-crosswalk-20261010.md']
    result = subprocess.run(diff, cwd=ROOT, capture_output=True, text=True)
    ck('scoped git diff check', result.returncode == 0)
    report = dict(checker_sha256=sha(Path(__file__)), inputs=inputs, checks=checks,
                  passed=sum(c['passed'] for c in checks), failed=sum(not c['passed'] for c in checks),
                  pdf=read(OUT / 'render-manifest.json')['pdf'], counts_by_kind=counts,
                  started_at=started, wall_seconds=time.monotonic() - timer,
                  command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 ' + rel(Path(__file__)))
    save('candidate-checks.json', report)
    print(json.dumps({k: report[k] for k in ['passed', 'failed', 'wall_seconds']}))
    assert not report['failed'], [c['id'] for c in checks if not c['passed']]


def check_manuscript(ck, verify, inputs, rows, groups):
    old = {p.relative_to(OLD): p for p in OLD.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
    new = {p.relative_to(NEW): p for p in NEW.rglob('*') if p.suffix in {'.tex', '.bib', '.lark'}}
    ck('all 48 inherited source files retained', old.keys() == new.keys() and len(old) == 48)
    changed, delta = [], []
    for n, p in sorted(new.items()):
        a, b = old[n].read_text(), p.read_text()
        inputs[rel(p)] = sha(p)
        if a != b:
            changed.append(str(n))
            delta.extend(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                             fromfile=rel(old[n]), tofile=rel(p)))
    ck('only five declared source files changed', set(changed) == {
        'accounting-product-proposal.tex', 'sections/apple-pronouncements.tex',
        'sections/apple-legal.tex', 'sections/apple-disruption.tex', 'sections/apple-quality-inventory.tex'})
    ck('title change is version only', (NEW / 'accounting-product-proposal.tex').read_text().replace(
        'Version 2.24', 'Version 2.23') == (OLD / 'accounting-product-proposal.tex').read_text())
    body = (NEW / 'sections/apple-quality-inventory.tex').read_text()
    old_body = (OLD / 'sections/apple-quality-inventory.tex').read_text()
    addition = body[len(old_body):]
    ck('inventory prose preserved with one added subsection', body.startswith(old_body)
       and addition.count('\\subsection{') == 1 and '\\label{sec:apple-service-access}' in addition)
    a = '\n'.join(p.read_text() for n, p in sorted(old.items()) if p.suffix == '.tex')
    b = '\n'.join(p.read_text() for n, p in sorted(new.items()) if p.suffix == '.tex')
    displays = lambda s: re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}', s, re.S)
    ck('all 48 displays byte-identical', len(displays(a)) == 48 and displays(a) == displays(b))
    bib = (NEW / 'references.bib').read_text()
    keys = re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib)
    ck('all 66 bibliography entries byte-identical', bib == (OLD / 'references.bib').read_text() and len(keys) == 66)
    cites = lambda s: {k.strip() for q in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}', s) for k in q.split(',')}
    ck('citations retained and resolved', cites(a) <= cites(b) <= set(keys))
    labels = re.findall(r'\\label\{([^}]+)\}', b)
    refs = re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}', b)
    ck('unique labels and resolved references', len(labels) == len(set(labels)) and set(refs) <= set(labels))
    log = (NEW / 'accounting-product-proposal.log').read_text()
    ck('clean final LuaLaTeX log', not any(t in log for t in ['Warning', 'Overfull', 'Underfull', '! ']))
    ck('clean bibliography log', not re.search(r'Warning--|error message|I couldn.t open', (NEW / 'accounting-product-proposal.blg').read_text()))
    render = read(OUT / 'render-manifest.json')
    pdf = ROOT / render['pdf']['path']
    ck('final PDF hash and 167 pages', sha(pdf) == render['pdf']['sha256']
       == '3ce23bc9b84d25f22d23d7b806c274ce302ca28f38c43c0afbdfca920ecb8211'
       and len(fitz.open(pdf)) == render['pdf']['pages'] == 167)
    verify({r['path']: r['sha256'] for r in render['images']}, 'all 40 final rendered image hashes')
    first = read(OUT / 'build-01/render-manifest.json')
    first_images = {r['page']: ROOT / r['path'] for r in first['images']}
    from PIL import Image, ImageChops
    unchanged = [r['page'] for r in render['images'] if ImageChops.difference(
        Image.open(ROOT / r['path']).convert('RGB'), Image.open(first_images[r['page']]).convert('RGB')).getbbox() is None]
    ck('reading reuse binds only unchanged final pixels', unchanged == render['unchanged_from_read_attempt_01']
       and set(range(11, 41)) <= set(unchanged)
       and sorted(set(r['page'] for r in render['images']) - set(unchanged)) == [41, 42])
    review = (OUT / 'author-review.md').read_text()
    ck('author review binds final PDF with independent pending', render['pdf']['sha256'] in review
       and 'independent_reader_pending' in review)
    receipt = read(OUT / 'build-02/receipt.json')
    ck('successful final build receipt matches PDF', receipt['exit_code'] == 0 and receipt['pdf_sha256'] == sha(pdf))
    (OUT / 'manuscript-delta.diff').write_text(''.join(delta))

    starts = ['Adequate components and saleable inventory', 'Developer support has a separate economic cause.',
              'Access also depends on how a service uses data', 'Suppose a content agreement permits']
    anchors = [dict(path=rel(NEW / 'sections/apple-quality-inventory.tex'), sha256=sha(NEW / 'sections/apple-quality-inventory.tex'),
                    quote=s, line=body[:body.index(s)].count('\n') + 1) for s in starts]
    mapping = {'/claims/0': 0, '/claims/1': 1, '/claims/2': 1, '/claims/3': 1,
               '/claims/6': 0, '/claims/8': 0, '/claims/23': 2, '/claims/24': 2,
               '/queries/0': 0, '/queries/1': 1, '/queries/2': 3, '/queries/6': 2, '/queries/11': 2}
    affected = [r for r in rows if r['author_disposition_group'] == 'service-access-missing']
    resolved = [dict(identity=r['identity'], record_kind=r['record_kind'],
                     disposition='query remains unresolved' if r['record_kind'] == 'query' else 'mechanism explained; retained source detail not all repeated',
                     anchor=anchors[mapping[r['json_pointer']]]) for r in affected]
    ck('repair maps eight assertions and five still-open queries', len(resolved) == 13
       and sum(r['record_kind'] == 'query' for r in resolved) == 5)
    save('candidate-resolution.json', dict(pdf=render['pdf'], baseline_group='service-access-missing',
        crosswalk_sha256=sha(OUT / 'claim-query-crosswalk.json'), section='2.19.1', records=resolved,
        factual_queries_closed=0, author_explanatory_gap='repaired', independent_reader='pending', readiness='not_ready'))
    inputs[rel(OUT / 'candidate-resolution.json')] = sha(OUT / 'candidate-resolution.json')


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists(), 'Closed units are immutable.'
    main()
