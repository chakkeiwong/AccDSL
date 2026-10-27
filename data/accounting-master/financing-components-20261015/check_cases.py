from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
checks=[];cases=[]
def ck(name,actual,expected):
 checks.append({'name':name,'actual':str(actual),'expected':str(expected),'passed':actual==expected})
def enc(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
 if isinstance(x,list):return [enc(v) for v in x]
 return x
def case(name):
 c={'id':name,'opening':{'cash':F(200),'capital':F(-200)},'events':[],'snapshots':[]};cases.append(c);return c,dict(c['opening'])
def event(c,s,name,changes):
 changes={k:F(str(v)) for k,v in changes.items()};ck(c['id']+'/'+name+'/balanced',sum(changes.values()),0)
 for k,v in changes.items():s[k]=s.get(k,F(0))+v
 ck(c['id']+'/'+name+'/trial-balance',sum(s.values()),0)
 c['events'].append({'id':name,'debits_positive':changes});c['snapshots'].append(dict(s))
c,s=case('transaction-option')
event(c,s,'premium',{'cash':-6,'option':6})
event(c,s,'first-value',{'option':10,'intrinsic-reserve':-12,'cost-reserve':2})
ck('transaction/first-option',s['option'],16)
event(c,s,'expiry-value',{'option':4,'intrinsic-reserve':-8,'cost-reserve':4})
ck('transaction/cumulative-intrinsic',s['intrinsic-reserve'],-20);ck('transaction/cumulative-cost',s['cost-reserve'],6)
event(c,s,'inventory-purchase',{'inventory':120,'cash':-120})
event(c,s,'settlement',{'cash':20,'option':-20})
event(c,s,'intrinsic-basis',{'intrinsic-reserve':20,'inventory':-20})
event(c,s,'cost-basis',{'cost-reserve':-6,'inventory':6})
ck('transaction/inventory-cost',s['inventory'],106);ck('transaction/cash-before-sale',s['cash'],94)
event(c,s,'sale',{'cash':130,'revenue':-130})
event(c,s,'cost-of-sales',{'inventory':-106,'expense':106})
ck('transaction/closing-cash',s['cash'],224);ck('transaction/profit',-s['revenue']-s['expense'],24)
ck('transaction/equity-bridge',F(200)+24+14-14,224)
c,s=case('time-period-option')
event(c,s,'premium',{'cash':-6,'option':6})
event(c,s,'first-value',{'option':-4,'cost-reserve':4})
event(c,s,'first-amortisation',{'expense':3,'cost-reserve':-3})
ck('time-period/first-reserve',s['cost-reserve'],1);ck('time-period/first-expense',s['expense'],3)
first=dict(s)
event(c,s,'expiry-value',{'option':-2,'cost-reserve':2})
event(c,s,'last-amortisation',{'expense':3,'cost-reserve':-3})
ck('time-period/final-reserve',s['cost-reserve'],0);ck('time-period/final-expense',s['expense'],6)
c={'id':'early-discontinuation','opening':first,'events':[],'snapshots':[]};cases.append(c);s=dict(first)
event(c,s,'release-net-reserve',{'expense':1,'cost-reserve':-1})
ck('discontinuation/expense',s['expense'],4);ck('discontinuation/retained-asset',s['option'],2)
rows=[]
for name,a0,h0,at,ht,expected_oci,expected_profit in [
 ('actual-higher-first',6,4,3,3,-1,-2),('actual-higher-expiry',6,4,0,0,-4,-2),
 ('actual-lower-first',2,3,1,'2.5','-0.5','-0.5'),('actual-lower-expiry',2,3,0,0,-2,0)]:
 a0,h0,at,ht=map(lambda v:F(str(v)),[a0,h0,at,ht]);da=at-a0;dh=ht-h0
 assert da<=0 and dh<=0,'This check deliberately covers same-direction declining positive time value only'
 oci=dh if a0>h0 else -min(abs(da),abs(dh));profit=da-oci
 ck('alignment/'+name+'/oci',oci,F(str(expected_oci)));ck('alignment/'+name+'/profit',profit,F(str(expected_profit)))
 ck('alignment/'+name+'/reconciliation',oci+profit,da)
 rows.append({'id':name,'actual_initial':a0,'aligned_initial':h0,'actual_current':at,'aligned_current':ht,'cumulative_oci':oci,'cumulative_profit':profit})
ck('alignment/second-period-oci',rows[3]['cumulative_oci']-rows[2]['cumulative_oci'],F('-1.5'))
ck('alignment/second-period-profit',rows[3]['cumulative_profit']-rows[2]['cumulative_profit'],F('0.5'))
cases.append({'id':'alignment','rows':rows,'scope':'Positive time values declining in the same direction; not a universal signed collar selector'})
ck('collar/terminal-oci',F('1.2')-F('1.2'),0);ck('collar/nonzero-interim',F('1.2')!=0,True)
cases.append({'id':'zero-cost-collar','initial_time_value':'0','interim_time_value':'6/5','expiry_time_value':'0'})
ck('rebalancing/pre-reserve',min(18,14),14);ck('rebalancing/pre-profit',18-min(18,14),4)
ck('rebalancing/period-reserve',min(18,14)-min(12,10),4);ck('rebalancing/period-profit',(18-14)-(12-10),2)
ck('rebalancing/layered-change',100*(95-80)+10*(95-90),1550)
ck('rebalancing/wrong-old-reference',110*(95-80)-(100*(95-80)+10*(95-90)),100)
ck('rebalancing/undesignated-next-gain',F(10)*F(1,10),1);ck('rebalancing/designated-next-gain',F(10)*F(9,10),9)
cases.append({'id':'rebalancing','retained_layer':{'quantity':100,'reference':80},'added_layer':{'quantity':10,'reference':90},'later_price':95,'layered_change':1550,'pre_change_reserve':14,'pre_change_profit':4,'undesignated_fraction':'1/10','scope':'Zero-discount layer illustration; designated gain still requires effectiveness test'})
source=ROOT/'docs/design/research/p08-v1/aasb9.txt';text=source.read_text();spans=[]
for lo,hi in [('6.5.5','6.5.7'),('6.5.15','6.6'),('B6.5.7','B6.5.22'),('B6.5.29','B6.6.1')]:
 a=re.search(r'(?m)^[\f ]*'+re.escape(lo)+r'\s',text).start();m=re.search(r'(?m)^[\f ]*'+re.escape(hi)+r'\s',text[a+len(lo):]);assert m,(lo,hi)
 z=a+len(lo)+m.start();spans.append({'start_clause':lo,'end_exclusive':hi,'start_offset':a,'end_offset':z,'text':text[a:z]})
sources=[]
for suffix in ['pdf','txt']:
 p=ROOT/f'docs/design/research/p08-v1/aasb9.{suffix}';sources.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
ck('source/expected-pdf',sources[0]['sha256'],'8f5a87c67a76c193bedeee8ea7f3f21556b3886eee4184a62c7045256b3f84f0')
(OUT/'source-support.json').write_text(json.dumps({'sources':sources,'clauses':spans,'cover':text.split('\f')[0],'scope':'Historical 2024/2025 conditional Australian for-profit Tier 1 example; no current-law admission'},indent=2)+'\n')
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'case_groups':len(cases),'cases':enc(cases),'checks':checks,'sources':sources}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['passed','count','case_groups']}));assert out['passed']
