#!/usr/bin/env python3
"""Check official ASU 2019-10 identity and bounded date amendment reading."""
import hashlib
import json
from pathlib import Path
import fitz

root = Path(__file__).resolve().parent
repo = root.parents[2]
ledger = json.loads((root/'source-ledger.json').read_text())
checks = []
def check(name, ok):
    checks.append({'name':name,'pass':bool(ok)})
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

pdf = root/'sources/asu-2019-10.pdf'
check('official PDF hash', sha(pdf)=='0ccddf28a86796cf4d00253f451d0f7bdf061dd740ee557024542e44559a67b0')
check('source bytes', pdf.stat().st_size==321637)
with fitz.open(pdf) as doc:
    check('34 pages',len(doc)==34)
    for word in ['2019-10','November 2019','Effective Dates','An Amendment of the FASB']:
        check('cover '+word,word in doc[0].get_text())
    whole='\n'.join(p.get_text() for p in doc)
    for paragraph in ['326-20-30-11','326-20-35-3','326-20-45-2','460-10-30-5']:
        check('no literal change '+paragraph,paragraph not in whole)
check('46 bound acquisition/text/render files',len(ledger['files'])==46)
for item in ledger['files']:
    check('hash '+item['path'],sha(repo/item['path'])==item['sha256'])
check('7 selected spans',len(ledger['spans'])==7)
for e in ledger['spans']:
    raw=(repo/e['path']).read_text()
    check('span '+e['id'],raw[e['start']:e['end']].strip()==e['span'])
check('correct visual review list',ledger['visually_inspected_pages']==[12,14,15,23])
p15=(root/'sources/pdf-page-15.txt').read_text()
check('SEC filer/SRC distinction','excluding entities eligible' in p15)
check('later other-entity date','December 15, 2022 2021' in p15)
check('superseded old subparagraph','Subparagraph superseded by Accounting Standards Update No.' in p15)
p14=(root/'sources/pdf-page-14.txt').read_text()
check('2019-05 verified lead','No. 2019-05' in p14)
p23=(root/'sources/pdf-page-23.txt').read_text()
check('amendment status','326-10-65-1' in p23 and '2019-10' in p23)
check('current boundary','complete amendment chain unverified' in ledger['authority'])
failed=[c['name'] for c in checks if not c['pass']]
(root/'check-run.json').write_text(json.dumps({'checks':len(checks),'failed':failed,'results':checks},indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failed':failed}))
raise SystemExit(bool(failed))
