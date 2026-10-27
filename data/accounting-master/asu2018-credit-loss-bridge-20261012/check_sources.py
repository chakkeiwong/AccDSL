#!/usr/bin/env python3
"""Integrity and paragraph-disposition checks for the official 2018 bridge."""
import hashlib
import json
import re
from pathlib import Path
import fitz

root = Path(__file__).resolve().parent
repo = root.parents[2]
checks = []
def check(name, ok):
    checks.append({'name': name, 'pass': bool(ok)})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    return json.loads((root / name).read_text())

ledger, pages, renders = [load(n) for n in ['source-ledger.json','source-pages.json','render-manifest.json']]
pdf = repo / pages['pdf']
check('PDF hash', sha(pdf) == ledger['sha256'] == pages['sha256'] == 'f2cd9eec5fed48e083116dc0fd81a7b50ba130d921d494af2152f1586ff09441')
check('PDF bytes', pdf.stat().st_size == 237295)
with fitz.open(pdf) as doc:
    check('20 pages', len(doc) == 20)
    for phrase in ['2018-19', 'November 2018', 'An Amendment of the FASB']:
        check('cover ' + phrase, phrase in doc[0].get_text())
    whole = '\n'.join(p.get_text() for p in doc)
    for paragraph in ['326-20-30-11','326-20-35-3','326-20-45-2','460-10-25-2','460-10-30-5','460-10-35-4']:
        check('not in this ASU ' + paragraph, paragraph not in whole)
check('20 retained text pages', len(pages['pages']) == 20)
for item in pages['pages']:
    check('text ' + str(item['pdf_page']), sha(repo / item['path']) == item['sha256'])
for item in renders['renders']:
    check('render ' + str(item['pdf_page']), sha(repo / item['path']) == item['sha256'])
check('three visually read pages', renders['visually_inspected'] == [12,13,14])
for e in ledger['entries']:
    raw = (repo / e['path']).read_text()
    check(e['id'] + ' span', raw[e['start']:e['end']].strip() == e['span'])
    check(e['id'] + ' hash', hashlib.sha256(e['span'].encode()).hexdigest() == e['sha256'])
    check(e['id'] + ' boundary', e['claim_class'] == 'historical_amendment_only')
check('eight entries', len(ledger['entries']) == 8)
status = (root / 'sources/pdf-page-15.txt').read_text()
check('15-3 status action', '326-20-15-3' in status and 'Amended' in status)
check('15-2 absent from status', '326-20-15-2' not in status)
exception = (root / 'sources/pdf-page-14.txt').read_text()
check('operating lease exclusion', 'Receivables arising from operating leases' in exception)
check('transition date markup noted', 'mixed typography' in next(x for x in ledger['entries'] if x['id']=='transition')['reading'])
a = (repo / 'data/accounting-master/asu2016-credit-loss-20261012/sources/pdf-page-108.txt').read_text()
p13 = (root / 'sources/pdf-page-13.txt').read_text()
s = a.index('c. \nOff-balance-sheet')
ca = a[s:a.index('326-20-15-3', s)]
s = p13.index('c. \nOff-balance-sheet')
cb = p13[s:] + '\n'.join(exception.splitlines()[1:]).split('326-20-15-3')[0]
compact = lambda x: re.sub(r'\s+', '', x)
check('2016/2018 c equality', compact(ca) == compact(cb) and ledger['comparison']['normalized_equal'])
check('current chain boundary', 'full chain not verified' in ledger['authority'])
failed = [x['name'] for x in checks if not x['pass']]
(root / 'check-run.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
