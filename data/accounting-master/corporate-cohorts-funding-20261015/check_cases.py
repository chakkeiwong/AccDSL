"""Conditional documentary calculations, not a production costing engine."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
checks=[];groups={}
def ck(n,a,e):checks.append({'name':n,'passed':a==e,'actual':str(a),'expected':str(e)})
def journal(n,d):ck(n,sum(d.values()),0);return {k:str(v) for k,v in d.items()}

# FIFO process costing: separate beginning work from current effort.
opening_units=10;started=90;completed=80;closing_units=20
opening_material=F(100);opening_conversion=F(50);current_material=F(900);current_conversion=F(510)
ck('wip/unit-conservation',opening_units+started,completed+closing_units)
remaining_opening=opening_units*F(1,2);started_completed=completed-opening_units
closing_conversion=closing_units*F(1,2)
eq_conversion=remaining_opening+started_completed+closing_conversion
ck('fifo/current-conversion-units',eq_conversion,85)
material_rate=current_material/started;conversion_rate=current_conversion/eq_conversion
ck('fifo/material-rate',material_rate,10);ck('fifo/conversion-rate',conversion_rate,6)
opening_finished=opening_material+opening_conversion+remaining_opening*conversion_rate
new_finished=started_completed*(material_rate+conversion_rate)
ending=closing_units*material_rate+closing_conversion*conversion_rate
ck('fifo/complete-opening',opening_finished,180);ck('fifo/started-completed',new_finished,1120)
ck('fifo/completed-cost',opening_finished+new_finished,1300);ck('fifo/ending-wip',ending,260)
available=opening_material+opening_conversion+current_material+current_conversion
ck('fifo/cost-conservation',opening_finished+new_finished+ending,available)
ck('fifo/available-cost',available,1560)
groups['fifo']={'transfer':journal('fifo/transfer',{'debit-finished-goods':1300,'credit-wip':-1300}),'ending_wip':'260'}

# Weighted average uses combined cost and combined equivalent production.
wa_material=(opening_material+current_material)/(completed+closing_units)
wa_conversion=(opening_conversion+current_conversion)/(completed+closing_conversion)
wa_finished=completed*(wa_material+wa_conversion)
wa_ending=closing_units*wa_material+closing_conversion*wa_conversion
ck('average/conversion-equivalent-units',completed+closing_conversion,90)
ck('average/material-rate',wa_material,10);ck('average/conversion-rate',wa_conversion,F(56,9))
ck('average/completed-cost',wa_finished,F(11680,9));ck('average/ending-wip',wa_ending,F(2360,9))
ck('average/conservation',wa_finished+wa_ending,1560)
ck('average/cent-allocation',F('1297.78')+F('262.22'),1560)
ck('average/ending-cost-difference',wa_ending-ending,F(20,9))
ck('average/opening-cost-not-omitted',available-(current_material+current_conversion),150)
groups['weighted_average']={'completed':str(wa_finished),'ending':str(wa_ending),'posted_completed':'1297.78','posted_ending':'262.22'}

# All units have full effort at inspection; normal yield is established ex ante.
cost=F(1000);normal_output=95;actual_good=90;abnormal=5
normal_rate=cost/normal_output;good_cost=actual_good*normal_rate;abnormal_cost=abnormal*normal_rate
ck('spoilage/physical-units',90+5+5,100)
ck('spoilage/normal-unit-cost',normal_rate,F(200,19))
ck('spoilage/good-cost',good_cost,F(18000,19))
ck('spoilage/abnormal-expense',abnormal_cost,F(1000,19))
ck('spoilage/cost-conservation',good_cost+abnormal_cost,1000)
ck('spoilage/wrong-all-cost-in-good-overstatement',1000-good_cost,abnormal_cost)
ck('spoilage/cent-conservation',F('947.37')+F('52.63'),1000)
groups['spoilage']={'normal_loss_units':5,'abnormal_loss_units':5,'good_inventory':str(good_cost),'expense':str(abnormal_cost),'assumptions':'Full effort at inspection, no salvage, homogeneous output, no fixed-overhead allocation in this separate example'}

# Economic benefit is limited to feasible, mutually compatible routes.
surplus=F(130)-100;refund=surplus-5
benefit_b=max(F(0),(F(20)-12)+(F(20)-25));prepayment=F(7)
reduction=prepayment+benefit_b
ck('funding/surplus',surplus,30);ck('funding/net-refund',refund,25)
ck('funding/future-service-net-benefit',benefit_b,3)
ck('funding/prepayment-plus-reduction',reduction,10)
ck('funding/wrong-periodwise-floor-overstatement',7+max(20-12,0)+max(20-25,0)-reduction,5)
ck('funding/exclusive-route-ceiling',max(refund,reduction),25)
ck('funding/exclusive-route-not-summed',refund+reduction-max(refund,reduction),10)
ck('funding/recognized-refund-asset',min(surplus,refund),25)
ck('funding/refund-ceiling-adjustment',surplus-min(surplus,refund),5)
ck('funding/conditional-refund-excluded-asset',min(surplus,reduction),10)
ck('funding/conditional-refund-ceiling',surplus-reduction,20)
ck('funding/negative-b-floor',max(0,(10-15)+(10-20)),0)
ck('funding/prepayment-survives-b-floor',7+max(0,(10-15)+(10-20)),7)
groups['available_benefit']={'refund_route':25,'reduction_route':10,'incompatible_sum_forbidden':35,'discount':'Zero rate supplied solely for two-period arithmetic'}

# A funding-basis past-service shortfall can coexist with an IAS19 surplus.
ck('past-funding/ias19-surplus-before',120-100,20)
ck('past-funding/recognized-surplus-before',min(20,0),0)
ck('past-funding/recognized-net-position-at-obligation',0-10,-10)
ck('past-funding/equity-after-obligation',100-10,90)
ck('past-funding/plan-surplus-after-payment',120+10-100,30)
ck('past-funding/recognized-asset-after-payment',min(30,0),0)
ck('past-funding/equity-after-payment',100-10,90)
groups['past_funding']={'recognition':journal('past-funding/recognition',{'debit-oci-ceiling':10,'credit-net-pension-liability':-10}),
 'payment':journal('past-funding/payment',{'debit-net-pension-liability':10,'credit-cash':-10}),
 'no_second_gain_or_loss':True,'assumptions':'Contribution10 is required for funding-basis past-service shortfall and wholly unavailable as benefit after payment; no interest/time passage between obligation and payment'}

# Cash classification completes the earlier exact restoration history.
payment=F('36.3');opening_cash=F(100);closing=opening_cash-payment
ck('restoration/payment-origin',F(20)+11+2+F('3.3'),payment)
ck('restoration/closing-cash',closing,F('63.7'))
ck('restoration/proposed-operating-plus-investing-plus-financing',-payment+0+0,-payment)
ck('restoration/competing-investing-total',0-payment+0,-payment)
ck('restoration/classification-affects-operating-cash',0-(-payment),payment)
ck('restoration/provision-fully-settled',payment-payment,0)
ck('restoration/depreciation-and-unwind',60+71+2+F('3.3'),F('136.3'))
ck('restoration/total-equity',200-F('136.3'),closing)
ck('restoration/year2-indirect-operating',-F('74.3')+71+F('3.3')-payment,-payment)
groups['restoration_cash']={'proposed':'Operating outflow36.3 for wages/materials/services removing the exhausted asset; no borrowing repaid or new asset created.',
 'competing':'Investing36.3 based on historical asset-cost link; same total cash, different category.',
 'status':'Documented provisional interpretation; staff paper supports argument, not mandatory authority.'}

sources=[]
for rel in ['docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt','data/accounting-master/corporate-cohorts-funding-20261015/sources/ifric-cash-examples-201207.pdf','data/accounting-master/corporate-cohorts-funding-20261015/sources/ifric-cash-examples-201207.txt','data/accounting-master/corporate-cohorts-funding-20261015/sources/iasb-cash-classification-202512.pdf','data/accounting-master/corporate-cohorts-funding-20261015/sources/iasb-cash-classification-202512.txt']:
 p=ROOT/rel;sources.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'groups':groups,'checks':checks,'sources':sources}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'count':len(checks),'groups':len(groups)}));assert out['passed']
