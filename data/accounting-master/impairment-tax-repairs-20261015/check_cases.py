from pathlib import Path
from fractions import Fraction as F
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
checks=[];cases=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
def emit(n,d):cases.append({'id':n,'values':{k:str(v) for k,v in d.items()}})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# These calculations start with independent opening inputs, not expected outputs.
assets=[F(40),F(40),F(60),F(60),F(40)];loss1=sum(assets[:2])-70
after=[assets[0]-loss1/2,assets[1]-loss1/2,*assets[2:]];loss2=sum(after)-207
alloc=[x/sum(after)*loss2 for x in after];end=[x-y for x,y in zip(after,alloc)]
ck('corporate/first',loss1==10);ck('corporate/second',loss2==23)
ck('corporate/allocation',alloc==[F('3.5'),F('3.5'),F(6),F(6),F(4)])
ck('corporate/end',end==[F('31.5'),F('31.5'),F(54),F(54),F(36)])
ck('corporate/total',sum(end)==207 and sum(assets)-sum(end)==loss1+loss2)
ck('corporate/wrong-double-count',sum(assets)-207!=loss2)
emit('corporate-assets',{'first_loss':loss1,'second_loss':loss2,'closing_total':sum(end)})
p=F(4,5);g=F(40);full=g/p;net=F(200)
for rec,expected in [(F(220),(F(30),F(24),F(6),F(16),F(216))),(F(180),(F(70),F(60),F(10),F(0),F(180)))]:
 loss=net+full-rec;gl=min(loss,full);al=loss-gl;recognized=gl*p+al;unrecognized=gl*(1-p);remain=g-gl*p;total=net-al+remain
 ck('partial/'+str(rec),(loss,recognized,unrecognized,remain,total)==expected)
 ck('partial/bridge/'+str(rec),net+g-recognized==total)
 ck('partial/test/'+str(rec),total+(full-gl)*(1-p)==rec)
 emit('partial-'+str(rec),{'test_loss':loss,'recognized_loss':recognized,'notional_unrecognized':unrecognized,'reported_total':total})
loss=F(200)+100+full+20-270;gl=full+20;al=loss-gl;subal=al*F(2,3);parental=al*F(1,3)
parentloss=full*p+20+subal*p+parental;nciloss=subal*(1-p)
ck('larger/test',loss==100);ck('larger/recognized',parentloss+nciloss==90)
ck('larger/attribution',parentloss==86 and nciloss==4)
ck('larger/balance',F(200)+100+40+20-parentloss-nciloss==270)
emit('larger-unit',{'parent_loss':parentloss,'nci_loss':nciloss,'notional_goodwill_loss':full*(1-p)})
A=F(140);tb=F(100);surplus=F(40);t=F(1,4);rec=F(90);imp=A-rec;oci=min(imp,surplus);pl=imp-oci;dtl=(A-tb)*t;dta=(tb-rec)*t
ck('revaluation/loss',oci==40 and pl==10);ck('revaluation/tax',dtl==10 and dta==F('2.5'))
netoci=-oci+dtl;netpl=-pl+dta
ck('revaluation/net',netoci==-30 and netpl==F('-7.5'))
ck('revaluation/bridge',A-dtl+netoci+netpl==rec+dta==F('92.5'))
recovery=F(130);rev=recovery-rec;plrev=min(pl,rev);ocirev=rev-plrev;newdtl=(recovery-tb)*t
ck('reversal/origin',plrev==10 and ocirev==30)
ck('reversal/tax',plrev-dta==F('7.5') and ocirev-newdtl==F('22.5'))
ck('reversal/bridge',rec+dta+(plrev-dta)+(ocirev-newdtl)==recovery-newdtl==F('122.5'))
ck('rate-change/oci',(A-tb)*(F('0.30')-t)==2)
emit('revaluation-tax',{'profit_net':netpl,'oci_net':netoci,'reversal_profit_net':plrev-dta,'reversal_oci_net':ocirev-newdtl})
price=F(150);fair=F(150);taxbase=F(100);dt=(fair-taxbase)*t;ident=fair-dt;goodwill=price-ident
ck('acquisition/dtl',dt==F('12.5'));ck('acquisition/goodwill',goodwill==F('12.5'));ck('acquisition/bridge',fair+goodwill-dt==price)
emit('acquisition',{'identifiable_net':ident,'dtl':dt,'goodwill':goodwill})
ck('investment/ordinary-liability',F(60)*F(1,5)==12)
for control in [False,True]:
 for no_reverse in [False,True]:
  exception=control and no_reverse;ck('investment/two-conditions/'+str((control,no_reverse)),exception==((control,no_reverse)==(True,True)))
cash0=F(100);current_due=F(7);equity0=F(100)
ck('pillar/current-recognition',cash0-current_due==equity0-current_due)
cash1=cash0-current_due;remaining_payable=F(0)
ck('pillar/settlement-bridge',cash1==equity0-current_due+remaining_payable)
ck('pillar/wrong-dtl-distinguishes-target',F(40)*F('0.15')!=0)
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
source_dir=OUT/'sources';source_dir.mkdir(exist_ok=True)
for src,name in [('/tmp/accdsl-eu2023-2468.pdf','eu2023-2468.pdf'),('/tmp/accdsl-eu2023-2468.txt','eu2023-2468.txt')]:
 dest=source_dir/name
 if dest.exists():assert sha(dest)==sha(Path(src))
 else:shutil.copy2(src,dest)
paths=['docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',str((source_dir/'eu2023-2468.pdf').relative_to(ROOT)),str((source_dir/'eu2023-2468.txt').relative_to(ROOT))]
sources=[{'path':p,'sha256':sha(ROOT/p)} for p in paths]
amendment=(source_dir/'eu2023-2468.txt').read_text()
for phrase in ['neither recognise nor disclose information about deferred tax','disclose separately its current tax expense','known or reasonably estimable']:
 ck('pillar/source-clause/'+phrase,phrase in amendment)
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'checks':checks,'cases':cases,'sources':sources,'meaning':'Exact conditional arithmetic and source integrity; IAS12 scope verified by source reading, not the multiplication check'}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'checks':len(checks),'case_groups':len(cases)}));assert out['passed']
