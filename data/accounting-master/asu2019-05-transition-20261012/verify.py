#!/usr/bin/env python3
"""Bounded source and closeout verification of the 2019-05 relief inquiry."""
import hashlib
import json
from pathlib import Path
import fitz

root=Path(__file__).resolve().parent
repo=root.parents[2]
ledger=json.loads((root/'source-ledger.json').read_text())
source=[]
closeout=[]
def add(group,name,ok):
    group.append({'name':name,'pass':bool(ok)})
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
pdf=root/'sources/asu-2019-05.pdf'
add(source,'exact PDF',sha(pdf)==ledger['source_sha256']=='8821a35452ab12128c772b377de095497dd94df654c258cb7a2e325e29346d60')
add(source,'PDF bytes',pdf.stat().st_size==231576)
with fitz.open(pdf) as doc:
    add(source,'20 pages',len(doc)==20)
    for phrase in ['2019-05','May 2019','Targeted Transition Relief','An Amendment of the FASB']:
        add(source,'cover '+phrase,phrase in doc[0].get_text())
    whole='\n'.join(p.get_text() for p in doc)
    for paragraph in ['326-20-30-11','326-20-35-3','326-20-45-2','460-10-30-5']:
        add(source,'not in this ASU '+paragraph,paragraph not in whole)
for item in ledger['pages']:
    add(source,'text '+str(item['page']),sha(root/'sources'/f"pdf-page-{item['page']}.txt")==item['sha256'])
for item in ledger['renders']:
    add(source,'render '+str(item['page']),sha(root/f"page-{item['page']}.png")==item['sha256'])
for item in ledger['spans']:
    raw=(root/'sources'/f"pdf-page-{item['pdf_page']}.txt").read_text()
    add(source,'span '+item['id'],raw[item['start']:item['end']].strip()==item['span'])
    add(source,'span hash '+item['id'],hashlib.sha256(item['span'].encode()).hexdigest()==item['sha256'])
election=next(x['span'] for x in ledger['spans'] if x['id']=='election')
for phrase in ['irrevocably','326-20-15-2(a)(2)','eligible items in Subtopic 825-10']:
    add(source,'eligibility '+phrase,phrase in election)
add(source,'visual boundary',ledger['visually_inspected']==[12])
add(source,'current ASC boundary','current Codification not verified' in ledger['authority'])

for name in ['result.md','source-ledger.json','sources/asu-2019-05.headers']:
    add(closeout,name,(root/name).is_file())
result=(root/'result.md').read_text()
add(closeout,'decision table','| Decision | Primary criterion |' in result)
add(closeout,'current boundary','no broader stability claim' in result)
add(closeout,'readiness','**not_ready**' in result)
add(closeout,'Version 2.33 frozen',sha(repo/'docs/design/proposal/manuscript-jpmorgan-commitments-20261012/accounting-product-proposal.pdf')=='48bce1dae3f6b23b88a540489d064258870250673a57fce0ae681cc7ce598496')
add(closeout,'source checks passed',all(x['pass'] for x in source))
for filename,items in [('check-run.json',source),('closeout-checks.json',closeout)]:
    failed=[x['name'] for x in items if not x['pass']]
    (root/filename).write_text(json.dumps({'checks':len(items),'failed':failed,'results':items},indent=2)+'\n')
print(json.dumps({'source_checks':len(source),'closeout_checks':len(closeout),'failed':[x['name'] for x in source+closeout if not x['pass']]}))
raise SystemExit(not all(x['pass'] for x in source+closeout))
