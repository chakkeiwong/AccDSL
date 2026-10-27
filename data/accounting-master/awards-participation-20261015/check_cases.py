from pathlib import Path
from fractions import Fraction as F
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];checks=[];cases=[]
def ck(n,a,b):checks.append({'name':n,'actual':str(a),'expected':str(b),'passed':a==b})
def enc(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
 if isinstance(x,list):return [enc(v) for v in x]
 return x
def case(name,opening=None):
 c={'id':name,'opening':opening or {'cash':F(10000),'capital':F(-10000)},'events':[],'snapshots':[]};cases.append(c);return c,dict(c['opening'])
def event(c,s,n,d):
 d={k:F(str(v)) for k,v in d.items()};ck(c['id']+'/'+n+'/balanced',sum(d.values()),0)
 for k,v in d.items():s[k]=s.get(k,F(0))+v
 ck(c['id']+'/'+n+'/trial-balance',sum(s.values()),0)
 c['events'].append({'id':n,'debits_positive':d});c['snapshots'].append(dict(s))
c,s=case('service-equity');cum=[]
for year,n,expected in [(1,90,900),(2,80,1600),(3,75,2250)]:
 value=F(n*10*3*year,3);charge=value-s.get('expense',F(0));event(c,s,f'year-{year}',{'expense':charge,'award-equity':-charge});ck(f'equity/year-{year}',s['expense'],expected);cum.append(value)
ck('equity/annual-charges',[cum[0],cum[1]-cum[0],cum[2]-cum[1]],[900,700,650])
c,s=case('nonmarket-failure',{'cash':F(10000),'capital':F(-10000),'expense':F(1600),'award-equity':F(-1600)})
event(c,s,'condition-failed',{'expense':-1600,'award-equity':1600});ck('nonmarket/zero-total',s['expense'],0)
c,s=case('market-failure',{'cash':F(10000),'capital':F(-10000),'expense':F(1600),'award-equity':F(-1600)})
event(c,s,'other-conditions-satisfied',{'expense':650,'award-equity':-650});ck('market/retain-total',s['expense'],2250)
c,s=case('cancellation',{'cash':F(1000),'capital':F(-1000)})
event(c,s,'year-one',{'expense':100,'award-equity':-100});event(c,s,'accelerate',{'expense':200,'award-equity':-200})
event(c,s,'payment',{'award-equity':320,'expense':10,'cash':-330});ck('cancellation/expense',s['expense'],310);ck('cancellation/cash',s['cash'],670);ck('cancellation/equity',-s['capital']-s['award-equity']-s['expense'],670)
c,s=case('cash-remeasurement')
for year,n,fv,expected in [(1,90,3,900),(2,80,6,3200),(3,75,8,6000)]:
 value=F(n*10*fv*year,3);charge=value+s.get('liability',F(0));event(c,s,f'year-{year}',{'expense':charge,'liability':-charge});ck(f'cash/year-{year}',-s['liability'],expected)
event(c,s,'settlement-value',{'expense':750,'liability':-750});event(c,s,'payment',{'liability':6750,'cash':-6750})
ck('cash/final-expense',s['expense'],6750);ck('cash/no-liability',s['liability'],0);ck('cash/paid',10000-s['cash'],s['expense'])
for choice in ['cash','shares']:
 c,s=case('holder-choice-'+choice)
 event(c,s,'service',{'expense':120,'liability':-100,'award-equity':-20});event(c,s,'remeasure',{'expense':30,'liability':-30})
 event(c,s,'settle',{'liability':130,'cash' if choice=='cash' else 'award-equity':-130})
 ck('holder-'+choice+'/expense',s['expense'],150);ck('holder-'+choice+'/liability',s['liability'],0)
 ck('holder-'+choice+'/equity-component',-s['award-equity'],20 if choice=='cash' else 150)
c,s=case('issuer-choice-no-obligation')
event(c,s,'service',{'expense':100,'award-equity':-100});event(c,s,'choose-higher-cash',{'award-equity':120,'expense':10,'cash':-130})
ck('issuer-choice/expense',s['expense'],110);ck('issuer-choice/cash',10000-s['cash'],130)
profit=F(120);div_o=F(20);div_p=F(4);remaining=profit-div_o-div_p
ordinary=remaining*F(100,120)+div_o;participating=remaining*F(20,120)+div_p
ck('participation/remaining',remaining,96);ck('participation/ordinary',ordinary,100);ck('participation/other',participating,20);ck('participation/conservation',ordinary+participating,profit)
ck('participation/ordinary-eps',ordinary/100,1);ck('participation/other-eps',participating/10,2)
cases.append({'id':'participation','profit':profit,'ordinary_count':100,'participating_count':10,'participation_weights':[1,2],'dividends':[20,4],'class_earnings':[ordinary,participating],'rights':'Uncapped profit participation, no senior claims, unchanged quantities all period; loss rights not assumed'})
proceeds=10*(5+2);increment=F(10)-F(proceeds,10);ck('options/proceeds',proceeds,70);ck('options/increment',increment,3);ck('options/eps',F(100)/(100+increment),F(100,103));ck('options/omit-service-error',F(10)-F(50,10)-increment,2)
cases.append({'id':'options-future-service','profit':100,'shares':100,'options':10,'cash_exercise':5,'period_average_future_service':2,'average_market_price':10,'increment':increment,'diluted_eps':F(100,103)})
cash_eps=F(90,100);share_eps=F(90+10,100+20);ck('eps-choice/cash',cash_eps,F('0.9'));ck('eps-choice/shares',share_eps,F(5,6));ck('eps-choice/share-dilutive',share_eps<cash_eps,True);ck('eps-choice/incorrect-numerator',F(90,120),F('0.75'))
cases.append({'id':'eps-cash-or-shares','reported_profit':90,'basic_shares':100,'liability_remeasurement_addback':10,'assumed_shares':20,'cash_eps':cash_eps,'share_eps':share_eps,'scope':'No tax or other changes, no participation, full-period contract, continuing-operations dilution screen assumed'})
base=ROOT/'docs/design/research/p08-v3-preparation';sources=[]
for ext in ['pdf','txt']:
 p=base/f'eu-2023-1803-original.{ext}';sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
text=(base/'eu-2023-1803-original.txt').read_text();lines=text.split(chr(10));spans=[]
for a,b in [(26204,26372),(26426,26705),(14984,15044),(15430,15610),(15907,15948)]:
 spans.append({'start_line':a,'end_line':b,'text':'\n'.join(lines[a-1:b])})
(OUT/'source-support.json').write_text(json.dumps({'sources':sources,'spans':spans,'scope':'Historical EU2023/1803 IFRS2/IAS33 conditional method; not US GAAP or current-law certification'},indent=2)+'\n')
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'case_groups':len(cases),'cases':enc(cases),'checks':checks,'sources':sources}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','count','case_groups']}));assert out['passed']
