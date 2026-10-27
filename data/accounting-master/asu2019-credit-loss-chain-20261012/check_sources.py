#!/usr/bin/env python3
"""Check source identity, exact anchors and the bounded scope comparison."""
import hashlib
import json
import re
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
checks = []
def check(name, ok):
    checks.append({'name': name, 'pass': bool(ok)})
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):
    return json.loads((ROOT / name).read_text())

ledger = load('source-ledger.json')
pages = load('source-pages.json')
renders = load('render-manifest.json')
pdf = REPO / pages['source_pdf']
check('exact PDF identity', sha(pdf) == ledger['sha256'] == pages['sha256'] == '6e60702ea3bf5055375de2fd498e2a0b4b5377600a7c33ea23cbf4c4138f7dc7')
check('PDF bytes', pdf.stat().st_size == 634688)
with fitz.open(pdf) as doc:
    check('131 pages', len(doc) == 131)
    cover = doc[0].get_text()
    for term in ['2019-04', 'April 2019', 'An Amendment of the FASB']:
        check('cover ' + term, term in cover)
    full = '\n'.join(page.get_text() for page in doc)
    for paragraph in ['326-20-30-11', '326-20-35-3', '326-20-45-2', '460-10-25-2', '460-10-30-5', '460-10-35-4']:
        check('no literal occurrence in this ASU: ' + paragraph, paragraph not in full)
check('11 retained text pages', len(pages['pages']) == 11)
for p in pages['pages']:
    check('text hash ' + str(p['pdf_page']), sha(REPO / p['path']) == p['sha256'])
for p in renders['renders']:
    check('render hash ' + str(p['pdf_page']), sha(REPO / p['path']) == p['sha256'])
check('render review separated', set(renders['inspected_pages']) == {49, 50, 88, 91} and renders['uninspected_pages'] == [87])
check('eight spans', len(ledger['entries']) == 8)
for e in ledger['entries']:
    raw = (REPO / e['path']).read_text()
    check(e['id'] + ' exact span', raw[e['start']:e['end']].strip() == e['span'])
    check(e['id'] + ' span hash', hashlib.sha256(e['span'].encode()).hexdigest() == e['sha256'])
    check(e['id'] + ' historical limit', e['claim_class'] == 'historical_amendment_only')
a = (REPO / 'data/accounting-master/asu2016-credit-loss-20261012/sources/pdf-page-108.txt').read_text()
b = (ROOT / 'sources/pdf-page-50.txt').read_text()
ca = a[a.index('c. \nOff-balance-sheet'):a.index('326-20-15-3')]
cb = b[b.index('c. \nOff-balance-sheet'):b.index('d. \nReinsurance recoverables')]
compact = lambda x: re.sub(r'\s+', '', x)
check('off-balance c equality', compact(ca) == compact(cb))
for key, value in [('2016_compact_sha256', ca), ('2019_compact_sha256', cb)]:
    check(key, hashlib.sha256(compact(value).encode()).hexdigest() == ledger['comparison'][key])
check('new reinsurance d', 'd. \nReinsurance recoverables' in b)
transition = (ROOT / 'sources/pdf-page-88.txt').read_text()
check('earlier 2018-19 official lead', 'No. 2018-19' in transition)
check('omitted original remainder explicit', 'unchanged.]' in transition)
check('current applicability not claimed', 'complete change chain not verified' in ledger['authority'])
failed = [c['name'] for c in checks if not c['pass']]
(ROOT / 'check-run.json').write_text(json.dumps({'checks': len(checks), 'failed': failed, 'results': checks}, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'failed': failed}))
raise SystemExit(bool(failed))
