"""Integrity/located-source checks; does not automate accounting interpretation."""
from pathlib import Path
import hashlib,json,time,fitz
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
start=time.perf_counter();checks=[];records=[]
def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
sources=[
('108','data/accounting-master/transition-dependencies-20261012/acquisition/aasb108.pdf','6990be18b6624012e21a403dd29c1203622d7a7b3ebca1352fe6e686a660bf00',['F2023C00187','31 December 2022','reliable information','authorised for issue','prior period errors','earliest prior period','Hindsight','Tier 2'], 'Complete 17 physical pages; interpretation in source-review.md'),
('116','docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb116-compiled-dec2022.pdf','0646458b6cfaba125fbadc1cd9b27c72067d0d82e2ff580aa2f48a31dcee3183',['F2023C00192','31 December 2022','systematic basis','residual value','available for use','straight-line'], 'Selected 43–62A, not a new full reading'),
('112','docs/design/proposal/methods/preparation-20261005-v1/02-authority/sources/aasb112-compiled-sep2023.pdf','cd51f104a7d88a38b033ab5e27b4877647c0f08c57ca0c782c75c7f245bf6fe2',['F2023C00930','29 September 2023','tax base','shall not be discounted','directly in equity','opening balance of retained earnings'], 'Selected 7,12,15–17,46–47,51/51A,53,57–62A'),
('133',str((OUT/'aasb133-compmar20.pdf').relative_to(ROOT)),'2867b2c15dbfc5cd3d05906d453caf75d988c33f7fd6a07b11bd53de713a0d8f',['F2021C00879','30 June 2021','1 July 2021','public market','process of filing','An entity that discloses earnings per share'], 'Physical 1,5–7,40–41; scope only')]
for key,path,expected,terms,scope in sources:
    p=ROOT/path;actual=hashlib.sha256(p.read_bytes()).hexdigest()
    check('hash:'+key,actual==expected)
    doc=fitz.open(p);text=' '.join(' '.join(page.get_text().split()) for page in doc)
    for term in terms:check(key+':'+term,term.casefold() in text.casefold())
    records.append({'source':key,'path':path,'sha256':actual,'pages':len(doc),'inspected_scope':scope})
check('full-108-extracts',all((OUT/f'aasb108-pages-{x}.txt').exists() for x in ['1-6','7-10','11-14','15-17']))
check('no-current-authority-claim','no subsequent amendment chain' in (OUT/'source-review.md').read_text())
check('private-scope-explicit','voluntary EPS' in (ROOT/'docs/design/proposal/methods/error-estimate-bridge-20261014.md').read_text())
result={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'sources':records,'role':'Integrity and source location only; source interpretation remains separate','wall_seconds':time.perf_counter()-start}
(OUT/'source-checks.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({'passed':result['passed'],'check_count':len(checks),'failed':[c['name'] for c in checks if not c['passed']]}))
if not result['passed']:raise SystemExit(1)
