from pathlib import Path
from fractions import Fraction as F
import json,hashlib
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
c,s=case('covered-contracts-and-estimate-change',{'cash':50,'capital':-50})
covered=48+1-41;uncovered=70+1-59;recovery=F(covered,2)
ck('loss/covered',covered,8);ck('loss/uncovered',uncovered,12);ck('loss/group',covered+uncovered,20);ck('loss/recovery',recovery,4)
event(c,s,'issued-recognition',{'cash':100,'issued-liability':-120,'issued-loss':20})
event(c,s,'held-premium',{'cash':'-26.5','held-fcf':'24.5','held-cost-csm':2})
event(c,s,'initial-loss-recovery',{'held-cost-csm':4,'held-income':-4})
ck('recognition/held-asset',s['held-fcf']+s['held-cost-csm'],F('30.5'));ck('recognition/net-equity',s['cash']+s['held-fcf']+s['held-cost-csm']+s['issued-liability'],34)
ck('recognition/wrong-whole-group-excess',F(20,2)-recovery,6)
issued_lc=F(20);held_lrc=F(4)
event(c,s,'covered-claims-revised',{'issued-liability':4,'issued-loss':-4,'held-fcf':-2,'held-expense':2});issued_lc-=4;held_lrc-=2
ck('revision/issued-loss-component',issued_lc,16);ck('revision/held-loss-recovery',held_lrc,F((44+1-41),2));ck('revision/held-asset',s['held-fcf']+s['held-cost-csm'],F('28.5'))
ck('revision/held-csm-unchanged',s['held-cost-csm'],6);ck('revision/net-equity',s['cash']+s['held-fcf']+s['held-cost-csm']+s['issued-liability'],36)
event(c,s,'issued-service',{'issued-liability':116,'issued-revenue':-100,'issued-loss':-16,'claims-expense':114,'cash':-114})
event(c,s,'held-service',{'held-fcf':'-22.5','held-cost-csm':-6,'premium-allocation':'26.5','held-expense':2,'held-income':-22,'cash':22})
ck('terminal/cash',s['cash'],F('31.5'));ck('terminal/issued-liability',s['issued-liability'],0);ck('terminal/held-asset',s['held-fcf']+s['held-cost-csm'],0)
expense=sum(v for k,v in s.items() if k not in ['cash','capital','issued-liability','held-fcf','held-cost-csm']);ck('terminal/lifetime-loss',expense,F('18.5'));ck('terminal/equity',50-expense,s['cash'])
ck('terminal/service-period-result',F(2)-F('6.5'),F('-4.5'));ck('terminal/lifetime-bridge',F(-16)+2-F('4.5'),F('-18.5'))
cases.append({'id':'late-entry-counterfactual','initial_loss_recovery':0,'ordinary_held_asset':'53/2','initial_equity':30,'reason':'Treaty entered after original underlying recognition; B119C condition fails'})
ck('late-entry/equity',F('123.5')+F('26.5')-120,30)
c,s=case('future-service-csm',{'cash':150,'fcf':-80,'csm':-20,'capital':-50})
event(c,s,'adverse-fifteen',{'fcf':-15,'csm':15});ck('csm/remaining',-s['csm'],5)
event(c,s,'adverse-ten',{'fcf':-10,'csm':5,'service-loss':5});lc=F(5)
ck('csm/exhausted',s['csm'],0);ck('csm/total-liability',-s['fcf']-s['csm'],105)
event(c,s,'favourable-eight',{'fcf':8,'service-loss':-5,'csm':-3});lc-=5
ck('csm/loss-component-cleared',lc,0);ck('csm/restored',-s['csm'],3);ck('csm/final-liability',-s['fcf']-s['csm'],100);ck('csm/profit-reversal-capped',s['service-loss'],0)
c,s=case('fixed-claim-oci',{'cash':150,'claim-liability':-100,'capital':-50})
ck('finance/opening-pv',F(121)/F('1.1')**2,100)
event(c,s,'year-one',{'claim-liability':-21,'finance-expense':10,'oci-expense':11})
ck('finance/first-equity',s['cash']+s['claim-liability'],29)
event(c,s,'year-two',{'finance-expense':11,'oci-expense':-11})
event(c,s,'payment',{'claim-liability':121,'cash':-121})
ck('finance/profit-total',s['finance-expense'],21);ck('finance/oci-total',s['oci-expense'],0);ck('finance/claim-closed',s['claim-liability'],0);ck('finance/final-cash',s['cash'],29)
cases.append({'id':'all-profit-counterfactual','year_one_finance_expense':21,'year_two_finance_expense':0,'total_finance':21,'final_equity':29})
ck('finance/total-policy-invariance',21+0,s['finance-expense']+s['oci-expense'])
base=ROOT/'docs/design/research/p08-v3-preparation';sources=[]
for ext in ['pdf','txt']:
 p=base/f'eu-2023-1803-original.{ext}';sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
lines=(base/'eu-2023-1803-original.txt').read_text().split(chr(10));spans=[]
for a,b in [(55013,55194),(55310,55443),(55490,55600),(55685,55759),(57554,57594),(57918,57978),(58228,58265),(58421,58489)]:spans.append({'start_line':a,'end_line':b,'text':'\n'.join(lines[a-1:b])})
(OUT/'source-support.json').write_text(json.dumps({'sources':sources,'spans':spans,'scope':'Historical EU IFRS17 nonparticipating GMM conditional cases; supplied valuation'},indent=2)+'\n')
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'case_groups':len(cases),'cases':enc(cases),'checks':checks,'sources':sources};(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','count','case_groups']}));assert out['passed']
