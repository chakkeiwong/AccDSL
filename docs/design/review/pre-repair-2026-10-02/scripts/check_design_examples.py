#!/usr/bin/env python3
"""Exact arithmetic audit of manuscript illustrations, not an AccDSL engine."""
from fractions import Fraction as F
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
checks=[]

def record(name, condition, details):
    assert condition, name
    checks.append({'name':name,'passed':True,'details':details})

def number(v):
    return str(v.numerator) if v.denominator==1 else str(v)

principal=F(100)
fixed=principal*F(5,100)
floating=principal*F(7,100)
record('historical_observational_equivalence',fixed==F(5),{'historical_rate':'.05','historical_interest':'5','same_postings_for_both_contracts':True})
for alpha in [F(0),F(1,4),F(1,2),F(3,4),F(1)]:
    interest=principal*(F(5,100)*alpha+F(7,100)*(1-alpha))
    record('interest_family_'+number(alpha),interest==7-2*alpha,{'alpha':number(alpha),'interest':number(interest)})
for name,charge in [('fixed',fixed),('floating',floating)]:
    opening_cash=F(95);opening_equity=F(-5)
    cash=opening_cash-charge;equity=opening_equity-charge
    record('scenario_balance_'+name,cash==principal+equity and charge-charge==0,
           {'cash':number(cash),'debt':'100','equity':number(equity),'profit':number(-charge)})
carrying=F(100);accretions=[]
for i in range(2):
    interest=carrying*F(5,100);carrying+=interest;accretions.append(interest)
record('zero_coupon_schedule',carrying==F(11025,100) and accretions==[F(5),F(525,100)],
       {'carrying_before_redemption':number(carrying),'period_interest':[number(x) for x in accretions]})
cash=F(10)*12;capital=F(10);premium=cash-capital;cost=F(3)
record('equity_issue_and_cost',(cash-cost)==capital+(premium-cost),
       {'net_cash':number(cash-cost),'share_capital':number(capital),'net_premium':number(premium-cost),'new_shares':'10'})
base=F(100)*F(2,100)*F(4,10);stress=F(100)*F(4,100)*F(5,10)
record('illustrative_credit_loss',base==F(8,10) and stress==2 and stress-base==F(12,10),
       {'base':number(base),'stress':number(stress),'increase':number(stress-base),'not_a_standard_compliance_model':True})
w=F(1,4)
mean=w*fixed+(1-w)*floating
variance=w*(fixed-mean)**2+(1-w)*(floating-mean)**2
record('illustrative_mixture',mean==7-2*w and variance==4*w*(1-w),
       {'illustrative_weight_only':number(w),'mean':number(mean),'between_explanation_variance':number(variance)})
out={'date':'2026-10-02','command':'python3 scripts/check_design_examples.py','target':'deterministic arithmetic in the LaTeX design document','method':'Python Fraction exact rational arithmetic; no stochastic run','checks':checks,'conclusion':'Manuscript illustration arithmetic passes; no product implementation, accounting compliance or forecast validity is established.'}
p=ROOT/'docs/design/review/example-checks.json';p.write_text(json.dumps(out,indent=2)+'\n')
print(f'{len(checks)} exact illustrative checks passed; {p.relative_to(ROOT)}')
