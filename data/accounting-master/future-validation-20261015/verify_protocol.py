from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import hashlib,json,subprocess,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
started=time.perf_counter();checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
base=json.loads((OUT/'baseline.json').read_text());old=ROOT/base['candidate']
ck('pdf-preserved',sha(old/'accounting-product-proposal.pdf')==base['pdf_sha256'])
for x in base['source_files']:ck('source/'+x['path'],sha(old/x['path'])==x['sha256'])
for r in json.loads((OUT/'ledger-additions.json').read_text())['records']:
 n=r['name'];a=json.loads((OUT/'six-ledgers-before'/f'{n}.json').read_text());b=json.loads((ROOT/'docs/design/research'/f'{n}.json').read_text())
 ck(n+'/historical-prefix',b['records'][:r['before']]==a['records']);ck(n+'/historical-date',a['date']==b['date'])
 ck(n+'/added-count',len(b['records'])==r['after'])
s=json.loads((OUT/'source-support.json').read_text());ck('paper-hash',sha(ROOT/s['local_path'])==s['sha256'])
def loss(atoms,y):
 assert sum(p for x,p in atoms)==1
 return sum(p*abs(x-y) for x,p in atoms)-F(1,2)*sum(p*q*abs(x-z) for x,p in atoms for z,q in atoms)
law=[(F(5),F(1,2)),(F(7),F(1,2))];point=[(F(6),F(1))]
for y,a,b in [(5,F(1,2),F(1)),(6,F(1,2),F(0))]:
 ck('two-point-loss/'+str(y),loss(law,F(y))==a);ck('point-loss/'+str(y),loss(point,F(y))==b)
ck('gaussian-variance',1/(1/F(4)+1)==F(4,5));ck('gaussian-mean',F(4,5)*2==F(8,5))
ck('cash-mean',100+10*F(8,5)==116);ck('cash-variance',100*F(4,5)==80)
origin=datetime(2025,3,15,tzinfo=timezone.utc)
ck('partly-elapsed-year',datetime(2025,1,1,tzinfo=timezone.utc)<origin<datetime(2026,1,1,tzinfo=timezone.utc))
ck('all-future-year',datetime(2026,1,1,tzinfo=timezone.utc)>origin)
ck('condition',2*1+1==3);ck('intervention',F(1,2)*(2*1+0)+F(1,2)*(2*1+1)==F(5,2))
method=(ROOT/'docs/design/proposal/methods/future-validation-20261015.md').read_text()
ledger=(OUT/'protocol-ledger.md').read_text()
for t in ['E1.','E2.','E3.','E4.','E5.','E6.','136','31','first release','finite first moment','unresolved mass','under_budgeted','101, 202 and 303']:
 ck('required-design/'+t,t in method)
for t in ['Promotion criterion','Promotion veto','Continuation veto','Repair trigger','Explanatory diagnostics','Must not conclude','Provenance','Failure mode','Earliest diagnostic','Promotion status','Pre-mortem','Post-write red team']:
 ck('required-ledger/'+t,t in ledger)
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out={'passed':all(c['passed'] for c in checks),'count':len(checks),'checks':checks,'wall_seconds':time.perf_counter()-started,'meaning':'Source integrity, independent illustrative arithmetic and protocol-field presence; not empirical validity or human review'}
(OUT/'protocol-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','count','meaning']}));assert out['passed']
