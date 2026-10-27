#!/usr/bin/env python3
"""Verify blocked inventory receipts and the admitted individual 2019-11 PDF."""
import hashlib
import json
from pathlib import Path
import fitz

root=Path(__file__).resolve().parent
repo=root.parents[2]
ledger=json.loads((root/'source-ledger.json').read_text())
checks=[]
def check(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for attempt in ledger['attempts']:
    for kind in ['headers','body']:
        check(attempt['id']+' '+kind+' hash',sha(repo/attempt[kind])==attempt[kind+'_sha256'])
    check(attempt['id']+' HTTP status',str(attempt['http_status']) in (repo/attempt['headers']).read_text().splitlines()[0])
check('Cloudflare homepage receipt','Cloudflare' in (root/'sources/fasb-home.html').read_text())
check('storage listing denied','AccessDenied' in (root/'sources/storage-root.body').read_text())
pdf=root/'sources/asu-2019-11.pdf'
check('2019-11 PDF hash',sha(pdf)==ledger['official_individual_pdf_sha256']=='7c8d70296f152278d6b469715d1ae46475dca3c8cc335fe6fcbf31cc75dea5b4')
check('source bytes',pdf.stat().st_size==292080)
with fitz.open(pdf) as doc:
    check('34 pages',len(doc)==34)
    for phrase in ['2019-11','November 2019','Codification Improvements to Topic 326']:
        check('cover '+phrase,phrase in doc[0].get_text())
    text='\n'.join(p.get_text() for p in doc)
    for paragraph in ['326-20-15-2','326-20-30-11','326-20-35-3','326-20-45-2','460-10-25-2','460-10-30-5','460-10-35-4']:
        check('selected ID not in this ASU '+paragraph,paragraph not in text)
for e in ledger['pages']+ledger['renders']:
    check('hash '+e['path'],sha(repo/e['path'])==e['sha256'])
for e in ledger['spans']:
    raw=(repo/e['path']).read_text()
    check('exact span '+e['id'],raw[e['start']:e['end']].strip()==e['span'])
    check('span hash '+e['id'],hashlib.sha256(e['span'].encode()).hexdigest()==e['sha256'])
check('visual reading boundary',ledger['visually_inspected']==[26])
check('inventory remains incomplete',ledger['not_a_complete_inventory'] is True)
check('current chain unverified','complete current change chain not verified' in ledger['authority'])
failed=[x['name'] for x in checks if not x['pass']]
(root/'check-run.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
