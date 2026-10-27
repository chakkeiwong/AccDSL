from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];checks=[];cases=[]
def ck(n,a,b):checks.append({'name':n,'actual':str(a),'expected':str(b),'passed':a==b})
def enc(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
 if isinstance(x,list):return [enc(v) for v in x]
 return x
def case(n,opening):
 c={'id':n,'opening':{k:F(str(v)) for k,v in opening.items()},'events':[],'snapshots':[]};cases.append(c);return c,dict(c['opening'])
def event(c,s,n,d):
 d={k:F(str(v)) for k,v in d.items()};ck(c['id']+'/'+n+'/balanced',sum(d.values()),0)
 for k,v in d.items():s[k]=s.get(k,F(0))+v
 ck(c['id']+'/'+n+'/trial-balance',sum(s.values()),0)
 c['events'].append({'id':n,'debits_positive':d});c['snapshots'].append(dict(s))
c,s=case('revolving',{'cash':200,'deposits':-180,'capital':-20});limit=100;capacity=100
event(c,s,'initial-provision',{'expense':2,'provision':-2})
event(c,s,'first-draw',{'loan':40,'cash':-40,'expense':'2.5','provision':'0.5','allowance':-3});capacity-=40
ck('revolving/first-capacity',capacity,60);ck('revolving/first-equity',20-s['expense'],F('15.5'));ck('revolving/first-provision',-s['provision'],F('1.5'))
event(c,s,'repayment',{'cash':10,'loan':-10,'allowance':'0.6','provision':'-0.3','expense':'-0.3'});capacity+=10
ck('revolving/restored-capacity',capacity,70);ck('revolving/repayment-loan',s['loan'],30);ck('revolving/repayment-loss',-s['allowance']-s['provision'],F('4.2'))
event(c,s,'second-draw',{'loan':20,'cash':-20,'allowance':'-1.6','provision':'0.6','expense':1});capacity-=20
ck('revolving/final-capacity',capacity,50);ck('revolving/capacity-plus-loan',capacity+s['loan'],limit);ck('revolving/final-equity',20-s['expense'],F('14.8'))
ck('revolving/final-loss',-s['allowance']-s['provision'],F('5.2'));ck('revolving/loss-expense',s['expense'],-s['allowance']-s['provision']);ck('revolving/final-assets',s['cash']+s['loan']+s['allowance'],196)
c,s=case('inseparable-loss',{'loan':4,'cash':96,'capital':-100})
event(c,s,'combined-loss',{'expense':6,'allowance':-4,'provision':-2});ck('inseparable/net-loan',s['loan']+s['allowance'],0);ck('inseparable/claim-preserved',s['loan'],4)
c,s=case('integral-fee-loan',{'cash':200,'capital':-200})
event(c,s,'fee-received',{'cash':2,'deferred-fee':-2});event(c,s,'loan-originated',{'loan':100,'cash':-100});event(c,s,'fee-incorporated',{'deferred-fee':2,'loan':-2})
rate=F('107.8')/s['loan']-1;ck('fee/effective-rate',rate,F('0.1'));interest=s['loan']*rate
event(c,s,'accretion',{'loan':interest,'interest-income':-interest});event(c,s,'collection',{'cash':'107.8','loan':'-107.8'})
ck('fee/loan-closed',s['loan'],0);ck('fee/net-cash',s['cash']-200,F('9.8'));ck('fee/income',-s['interest-income'],F('9.8'))
c,s=case('fee-expiry',{'cash':200,'capital':-200})
event(c,s,'receipt',{'cash':2,'deferred-fee':-2});event(c,s,'expiry',{'deferred-fee':2,'revenue':-2});ck('fee-expiry/revenue',-s['revenue'],2)
c,s=case('service-fee',{'cash':200,'capital':-200})
event(c,s,'receipt',{'cash':2,'contract-liability':-2});event(c,s,'first-service',{'contract-liability':1,'revenue':-1});ck('service/first-revenue',-s['revenue'],1)
event(c,s,'second-service',{'contract-liability':1,'revenue':-1});ck('service/closed-liability',s['contract-liability'],0)
c,s=case('eligible-part-sale',{'loan':100,'capital':-100})
sold=F(100)*F(45,45+55);ck('sale/allocated-carrying',sold,45)
event(c,s,'transfer',{'cash':46,'loan':-sold,'gain':sold-46});ck('sale/retained-loan',s['loan'],55);ck('sale/gain',-s['gain'],1);ck('sale/net-assets',s['cash']+s['loan'],101)
ck('sale/nominal-ratio-gain-error',F(46)-F(100)*F('0.4')-(-s['gain']),5)
c,s=case('retained-substantially-all-risk',{'loan':100,'capital':-100})
event(c,s,'financing',{'cash':46,'funding':-46});ck('retained-risk/loan',s['loan'],100);ck('retained-risk/net-assets',s['cash']+s['loan']+s['funding'],100)
c,s=case('guarantee-continuing-involvement',{'loan':100,'capital':-100})
guarantee=F(20);retained=min(s['loan'],guarantee);associated=guarantee+3
event(c,s,'transfer',{'cash':103,'retained-asset':retained,'loan':-100,'associated-liability':-associated});ck('guarantee/initial-net',s['cash']+s['retained-asset']+s['associated-liability'],100)
event(c,s,'service-and-impairment',{'associated-liability':1,'income':-1,'expense':2,'allowance':-2})
ck('guarantee/interim-net',s['cash']+s['retained-asset']+s['allowance']+s['associated-liability'],99)
event(c,s,'no-claim-expiry',{'allowance':2,'expense':-2,'associated-liability':22,'retained-asset':-20,'income':-2})
ck('guarantee/closed-asset',s['retained-asset'],0);ck('guarantee/closed-liability',s['associated-liability'],0);ck('guarantee/net-income',-s['income']-s['expense'],3);ck('guarantee/cash',s['cash'],103)
sources=[];spans=[]
for name,parts in [('aasb9',[('3.2.2','3.3'),('B3.2.13','B3.2.14'),('B5.4.1','B5.4.5'),('B5.5.39','B5.5.41'),('5.5.20','5.6')]),('aasb7',[('B8E','B8F')])]:
 for ext in ['pdf','txt']:
  p=ROOT/f'docs/design/research/p08-v1/{name}.{ext}';sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 text=(ROOT/f'docs/design/research/p08-v1/{name}.txt').read_text()
 for lo,hi in parts:
  a=re.search(r'(?m)^[\f ]*'+re.escape(lo)+r'\s',text).start();m=re.search(r'(?m)^[\f ]*'+re.escape(hi)+r'\s',text[a+len(lo):]);assert m,(name,hi)
  z=a+len(lo)+m.start();spans.append({'source':name,'first':lo,'end_exclusive':hi,'start_offset':a,'end_offset':z,'text':text[a:z]})
(OUT/'source-support.json').write_text(json.dumps({'sources':sources,'spans':spans,'scope':'Historical Australian 2024/2025 conditional illustration, not current-law or credit calibration'},indent=2)+'\n')
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'case_groups':len(cases),'cases':enc(cases),'checks':checks,'sources':sources}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','count','case_groups']}));assert out['passed']
