from pathlib import Path
from fractions import Fraction as F
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
checks=[];cases=[]
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
def emit(name,data):cases.append({'id':name,'values':{k:str(v) for k,v in data.items()}})
def bs(name,cash,assets,liabilities,equity):ck(name+'/balance',cash+assets==liabilities+equity)
# Independent inputs and equations; no authored expected JSON read.
physical=F(100)*(1-F(2,10));oldinspect=F(20)*(1-F(2,4));newinspect=F(24)
ck('inspection/old',oldinspect==10);ck('inspection/physical',physical==80)
asset=physical+newinspect;cash=F(100)-24;eq=F(190)-oldinspect
bs('inspection/replaced',cash,asset,0,eq);ck('inspection/asset',asset==104)
dep=F(100,10)+F(24,4);bs('inspection/year',cash,asset-dep,0,eq-dep)
ck('inspection/end',asset-dep==88 and eq-dep==164);bs('inspection/service',cash-3,asset-dep,0,eq-dep-3)
ck('inspection/double-cohort-rejected',physical+oldinspect+newinspect!=asset)
emit('inspection',{'physical':physical,'derecognized':oldinspect,'replacement_asset':asset,'annual_dep':dep,'closing_asset':asset-dep,'closing_equity':eq-dep})
A=F(80);L=F(100);q=F(1,4);gain=q*(L-A);remA=A*(1-q);remL=L*(1-q);pv=F('70.4')/F('1.1');adj=pv-remL;newA=remA+adj
ck('lease/termination-gain',gain==5);ck('lease/pv',pv==64);ck('lease/asset',newA==49)
bs('lease/event',120,newA,pv,100+gain);ck('lease/journal',L-pv==(A-newA)+gain)
interest=pv*F(1,10);cash=F(120)-F('70.4');profit=gain-newA-interest;bs('lease/end',cash,0,0,100+profit)
ck('lease/end-values',cash==F('49.6') and profit==F('-50.4'));ck('lease/variable',F(2)*3==6)
bs('lease/usage-paid',cash-6,0,0,100+profit-6)
emit('lease',{'gain':gain,'pv':pv,'remaining_asset':newA,'interest':interest,'cash_end':cash,'usage_charge':6})
D0=F(1000);P0=F(900);D1=F(1100);P1=F(920);oci=-(D1-D0)+(P1-P0);psc=F(150);D2=D1-psc
settled=F(200);planpaid=F(170);companypaid=F(20);sg=settled-planpaid-companypaid;D3=D2-settled;P3=P1-planpaid
ck('benefits/oci',oci==-80);ck('benefits/settlement',sg==10);ck('benefits/net-post',D3-P3==0)
eq=F(400)+oci+psc+sg;cash=F(500)-companypaid;bs('benefits/post',cash,0,D3-P3,eq)
rate=F(1,20);yearfrac=F(1,2);di=D3*rate*yearfrac;pi=P3*rate*yearfrac;service=F(30);D4=D3+di+service;P4=P3+pi;netinterest=di-pi
ck('benefits/gross-interest',di==pi==F('18.75'));ck('benefits/gross-end',D4==F('798.75') and P4==F('768.75'))
bs('benefits/end',cash,0,D4-P4,eq-service-netinterest);ck('benefits/end-equity',eq-service-netinterest==450)
ck('benefits/old-interest-base-wrong',(D0-P0)*rate*yearfrac==F('2.5') and netinterest==0)
emit('benefits',{'oci':oci,'psc_gain':psc,'settlement_gain':sg,'closing_D':D4,'closing_P':P4,'cash':cash,'equity':eq-service-netinterest})
D=F(100);P=F(130);C=F(10);adj0=max(P-D-C,0);newD=D-20;newC=F(15);adj1=max(P-newD-newC,0)
ck('ceiling/initial',adj0==20);ck('ceiling/after',adj1==35);ck('ceiling/net',20-(adj1-adj0)==5 and (P-newD-adj1)-(P-D-adj0)==5)
emit('ceiling',{'past_service_gain':20,'oci_loss':adj1-adj0,'asset_before':P-D-adj0,'asset_after':P-newD-adj1})
nominal=F(121);rate=F(1,10);pv=nominal/(1+rate)**2;year1=pv*rate;year2=(pv+year1)*rate
ck('multi-employer/pv',pv==100);ck('multi-employer/interest',year1==10 and year2==11);ck('multi-employer/settlement',pv+year1+year2==nominal)
emit('multi-employer',{'pv':pv,'interest1':year1,'interest2':year2,'payment':nominal})
paths=['docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt']
sources=[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'checks':checks,'cases':cases,'sources':sources,'meaning':'Exact independent arithmetic, statement conservation and source pins; no actual accounting compliance or actuarial calibration'}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'checks':len(checks),'cases':len(cases)}));assert out['passed']
