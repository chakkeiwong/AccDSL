"""Check exact retained source identity and located clauses, not interpretation."""
from pathlib import Path
import hashlib,json,time,fitz
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];started=time.perf_counter()
checks=[];sources=[]
def check(n,ok):checks.append({'name':n,'passed':bool(ok)})
records=[('102',OUT.parent/'ppe-cost-boundary/sources/aasb102-compiled-dec2021.pdf','b24a207371d5673d4e81d850326bea39a6bd240884b6d9c36ae9edf6c5556c83',['F2022C00496','31 December 2021','normal capacity','planned maintenance','abnormally high production','Unallocated overheads','abnormal amounts','selling costs','depreciation','cost of sales','Tier 2'],'Cover/scope/operative paragraphs/AppendicesA/B/compilation; physical1,3–14'),('116',ROOT/'docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb116-compiled-dec2022.pdf','0646458b6cfaba125fbadc1cd9b27c72067d0d82e2ff580aa2f48a31dcee3183',['F2023C00192','31 December 2022','costs of conversion of inventories','straight-line'],'Reuse inspected43–62A; production depreciation48–49')]
for name,p,expected,terms,scope in records:
    h=hashlib.sha256(p.read_bytes()).hexdigest();d=fitz.open(p);text=' '.join(' '.join(x.get_text().split()) for x in d)
    check(name+':hash',h==expected)
    for term in terms:check(name+':'+term,term.casefold() in text.casefold())
    sources.append({'name':name,'path':str(p.relative_to(ROOT)),'sha256':h,'scope':scope})
p=ROOT/'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf';d=fitz.open(p);text=' '.join(' '.join(x.get_text().split()) for x in d)
for term in ['31 December 2022','commercial substance','control','probable']:check('15:'+term,term.casefold() in text.casefold())
sources.append({'name':'15','path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Reuse prior inspected9/31–38 simple-delivery admission, no new full reading'})
method=' '.join((ROOT/'docs/design/proposal/methods/production-cost-20261015.md').read_text().split())
for term in ['pretax','no WIP','normal annual capacity','no portable OperationRequest','Pre-check arithmetic']:check('scope:'+term,term.casefold() in method.casefold())
r={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'sources':sources,'wall_seconds':time.perf_counter()-started,'role':'source integrity/location; substantive review recorded separately'}
(OUT/'source-checks.json').write_text(json.dumps(r,indent=2)+chr(10))
print(json.dumps({'passed':r['passed'],'check_count':len(checks),'failed':[c['name'] for c in checks if not c['passed']]}))
if not r['passed']:raise SystemExit(1)
