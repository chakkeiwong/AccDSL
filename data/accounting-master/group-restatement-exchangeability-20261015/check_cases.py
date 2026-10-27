"""Exact documentary calculations. This is not the product runtime."""
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
checks=[]; groups={}
def check(name,actual,expected):
 checks.append({'name':name,'passed':actual==expected,'actual':str(actual),'expected':str(expected)})
def balance(name,entries):
 check(name+'/debits-equal-credits',sum(entries.values()),0)
 return {k:str(v) for k,v in entries.items()}

# Consolidated amounts independently compared with the external-only history.
sold=F(2,5); external_cost=F(60)*sold; unsold_cost=F(60)*(1-sold)
unrealised=(F(100)-60)*(1-sold)
check('inventory/external-cost',external_cost,24)
check('inventory/remaining-group-cost',unsold_cost,36)
check('inventory/unrealised-profit',unrealised,24)
check('inventory/remaining-sub-cost',100*(1-sold),60)
check('inventory/group-profit',60-external_cost,36)
check('inventory/combined-profit-before-elimination',(100-60)+(60-40),60)
check('inventory/elimination-cogs-credit',100-unrealised,76)
check('inventory/eliminated-cogs',60+40-76,external_cost)
check('inventory/closing-cash',90+50+60,200)
check('inventory/group-equity',200+60-external_cost,236)
check('inventory/assets-less-liabilities',200+unsold_cost,236)
groups['inventory']={'receivable_payable':balance('inventory/balance-elimination',{'debit-payable':100,'credit-receivable':-100}),
 'investment':balance('inventory/investment-elimination',{'debit-sub-opening-equity':50,'credit-investment':-50}),
 'performance':balance('inventory/performance-elimination',{'debit-internal-revenue':100,'credit-cogs':-76,'credit-inventory':-24})}

# A documentary match predicate, independent of a future matching implementation.
key={'seller':'P','buyer':'S','event':'sale-17','currency':'LC','perimeter':'v1','cutoff':'R','branch':'base'}
def admissible(left,right):
 return all(left.get(k)==right.get(k)==v for k,v in key.items())
check('join/exact-pair',admissible(key,key),True)
for k,v in {'seller':'X','buyer':'T','event':'sale-18','currency':'USD','perimeter':'v2','cutoff':'R+1','branch':'alternative'}.items():
 check('join/reject-'+k,admissible(key,{**key,k:v}),False)
check('join/amount-agreement-cannot-prove-identity',100==100 and not admissible(key,{**key,'buyer':'T'}),True)
check('join/allocated-invoice-parts',40+60,100)
check('join/duplicate-part-fails',40+60+40==100,False)
check('join/unexplained-balance-difference',100-90,10)
groups['joins']={'rule':'Identity and allocation checks precede arithmetic elimination; unresolved differences remain explicit.'}

# Whole-period fixed net monetary exposure; price-index change is not a cash flow.
ratio=F(150,100); cash=F(100); inventory=F(60); debt=F(80); capital=F(80)
monetary_loss=(cash-debt)*(ratio-1)
check('inflation/capital',capital*ratio,120)
check('inflation/inventory',inventory*ratio,90)
check('inflation/cash-unchanged',cash,100)
check('inflation/debt-unchanged',debt,80)
check('inflation/cash-purchasing-loss',cash*(ratio-1),50)
check('inflation/debt-purchasing-gain',debt*(ratio-1),40)
check('inflation/net-monetary-loss',monetary_loss,10)
check('inflation/equity',cash+inventory*ratio-debt,110)
check('inflation/equity-rollforward',capital*ratio-monetary_loss,110)
check('inflation/cash-bridge',cash*ratio-cash*(ratio-1),cash)
check('inflation/no-transaction-flow',cash-cash,0)
check('inflation/wrongly-indexed-monetary-net-overstatement',(cash-debt)*(ratio-1),10)
check('inflation/nrv-loss',inventory*ratio-84,6)
check('inflation/nrv-equity',cash+84-debt,104)
groups['inflation']={'journal':balance('inflation/restatement',{'debit-inventory':30,'debit-monetary-loss':10,'credit-restated-capital':-40}),
 'nrv_journal':balance('inflation/nrv',{'debit-write-down':6,'credit-inventory':-6})}
rate=F(1,5)
for name,local,expected in [('cash',cash,20),('inventory',inventory*ratio,18),('debt',debt,16),('capital',capital*ratio,24),('loss',monetary_loss,2),('equity',110,22)]:
 check('translation/'+name,local*rate,expected)
check('translation/balance',20+18-16,24-2)
check('translation/unrestated-inventory-understatement',18-inventory*rate,6)
check('translation/prior-cash-at-prior-rate',cash*F(1,4),25)
check('translation/prior-cash-not-retranslated',cash*F(1,4)!=cash*ratio*rate,True)
groups['translation']={'rate':'1/5 USD per LC','prior_comparatives':'Retain original non-hyperinflationary presentation-currency comparatives.'}

# An external cash income at the middle index changes the monetary exposure.
first=20*(F(125,100)-1)*F(150,125)
second=50*(F(150,125)-1)
check('timing/first-interval-loss',first,6)
check('timing/second-interval-loss',second,10)
check('timing/total-monetary-loss',first+second,16)
check('timing/restated-cash-income',30*F(150,125),36)
check('timing/closing-equity',130+90-80,120+36-16)
check('timing/cash-purchasing-loss',100*(F(125,100)-1)*F(150,125)+130*(F(150,125)-1),56)
check('timing/cash-reconciliation',150+36-56,130)
groups['monetary_timing']={'indices':[100,125,150],'midpoint_cash_income':30,'monetary_loss':16}

# IFRIC7 opening deferred tax is remeasured first, then indexed.
cost=F(40); base=F(40); tax=F(1,5)
opening=cost*F(100,80); closing=cost*F(150,80)
opening_tax=(opening-base)*tax
check('first-application/opening-cost',opening,50)
check('first-application/closing-cost',closing,75)
check('first-application/opening-tax',opening_tax,2)
check('first-application/restated-opening-tax',opening_tax*ratio,3)
check('first-application/closing-tax',(closing-base)*tax,7)
check('first-application/tax-expense',(closing-base)*tax-opening_tax*ratio,4)
check('first-application/equity',(opening-opening_tax)*ratio-4,closing-7)
groups['opening_tax']={'tax_base':'40 throughout, supplied synthetic law','origin':'profit; no recognition exception in supplied facts'}

# Rate effects conditional on an admitted estimate, never proof of that estimate.
net_assets=F(1000); admitted=F(2,25); later=F(9,100); preferential=F(1,10)
check('rate/translated-net-assets',net_assets*admitted,80)
check('rate/subsequent-rate-difference',net_assets*(later-admitted),10)
check('rate/preferential-rate-difference',net_assets*(preferential-admitted),20)
check('rate/availability-ratio',F(5,1000),F(1,200))
check('rate/no-numerical-threshold-supplied',F(5,1000)>0,True)
check('transition/foreign-currency-payable-increase',100*(F(12)-10),200)
check('transition/foreign-operation-equity-change',1000*(admitted-preferential),-20)
groups['exchangeability']={'admitted_estimate':'0.08 USD/LC is supplied, not estimated by these checks',
 'availability':'5/1000 is descriptive; significance finding requires evidence',
 'transition':'Payable effect to opening retained earnings; foreign-operation translation effect to accumulated translation differences; no comparative restatement'}

sources=[]
for path in ['docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf','docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt','docs/design/research/p08-v4/202402862-text.response','docs/design/research/p08-v4/202402862.txt']:
 p=ROOT/path; sources.append({'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out={'passed':all(x['passed'] for x in checks),'count':len(checks),'groups':groups,'checks':checks,'sources':sources,'scope':'Exact documentary cases; not product implementation or actual-rate estimation'}
(OUT/'cases.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'count':len(checks),'groups':len(groups)}))
assert out['passed']
