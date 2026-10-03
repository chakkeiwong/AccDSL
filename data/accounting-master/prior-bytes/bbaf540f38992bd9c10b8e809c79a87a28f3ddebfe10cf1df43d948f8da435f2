#!/usr/bin/env python3
"""Deterministic reference checks for the design, not a product test suite.

Uses independently authored expectations and exact arithmetic. Z3 checks the
document's supported rational-linear constraints; no statistical claim follows.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import platform
import time
import z3

ROOT=Path(__file__).resolve().parents[1]
FIX=ROOT/'docs/design/fixtures'
checks=[]

def load(name): return json.loads((FIX/name).read_text())
def check(name, condition, detail):
    checks.append(dict(name=name,passed=bool(condition),detail=detail))
    if not condition: raise AssertionError(name+': '+str(detail))

def post(state, e, committed):
    """Local oracle for atomic double-entry/idempotency, deliberately small."""
    payload=json.dumps(e,sort_keys=True,separators=(',',':'))
    if e['id'] in committed:
        if committed[e['id']]!=payload: raise ValueError('EventIdentityConflict')
        return
    entries=[(p['account'],Q(p['signed_amount'])) for p in e['postings']]
    if sum(v for _,v in entries)!=0: raise ValueError('UnbalancedBatch')
    proposed=deepcopy(state)
    for a,v in entries: proposed[a]+=v
    state.clear(); state.update(proposed); committed[e['id']]=payload

def report_close(state, events, roles, period):
    selected=[e for e in events if e['period']==period]
    flows=defaultdict(Q)
    for e in selected:
        for p in e['postings']:
            if p['account']=='cash' and e['cash_class']:
                flows[e['cash_class']]+=Q(p['signed_amount'])
    profit=-sum(v for a,v in state.items() if roles[a] in ['income','expense'])
    revenue=-state['revenue']
    interest,tax=state['interest'],state['tax']
    # Closing is independent of the event generator; no cash arises here.
    for a in list(state):
        if roles[a] in ['income','expense']:
            state['retained']+=state[a];state[a]=Q(0)
    result=dict(cash=state['cash'],receivables=state['receivables'],inventory=state['inventory'],
        plant_net=state['plant_cost']+state['accum_depreciation'],tax_prepaid=state['tax_prepaid'],
        assets=sum(v for a,v in state.items() if roles[a] in ['asset','contra_asset']),
        payables=-state['payables'],debt=-state['debt'],
        equity=-sum(v for a,v in state.items() if roles[a]=='equity'),
        revenue=revenue,profit=profit,interest=interest,tax=tax,
        operating_cash=flows['operating'],investing_cash=flows['investing'],financing_cash=flows['financing'])
    check('balanced_'+period,sum(state.values())==0 and result['assets']==result['payables']+result['debt']+result['equity'],str(result))
    return result

def compare(name,actual,expected):
    check(name,all(actual[k]==Q(v) for k,v in expected.items()),{k:str(actual[k]) for k in expected})

def corporate():
    f=load('northstar.json'); state=defaultdict(Q,{k:Q(v) for k,v in f['opening'].items()}); committed={}
    check('opening_balance',sum(state.values())==0,'Signed account total is zero')
    periods={}
    for period in ['2024H1','2024H2']:
        for e in f['historical_events']:
            if e['period']==period:post(state,e,committed)
        periods[period]=report_close(state,f['historical_events'],f['accounts'],period)
        compare(period,periods[period],f['expected'][period])
    annual={k:sum(r[k] for r in periods.values()) for k in ['revenue','profit','operating_cash','investing_cash','financing_cash']}
    annual['cash_change']=state['cash']-Q(f['opening']['cash'])
    compare('annual_statements',annual,f['expected']['2024FY'])
    # Inverse construction from observed bridges. F,V remain a joint family.
    sales,collection,purchase,payment,cost,F,V=z3.Reals('sales collection purchase payment cost F V')
    constraints=[sales==260,35==20+sales-collection,20==30+purchase-cost,
        30==20+purchase-payment,cost==165,F>=0,V>=0,F+V==100,QZ('0.05')*(F+V)==5]
    solver=z3.Solver();solver.add(*constraints)
    check('reconstruction_feasible',solver.check()==z3.sat,'Closed scope annual bridge family')
    for x,value in [(collection,245),(purchase,155),(payment,145)]:
        solver.push();solver.add(x!=value); r=solver.check();solver.pop()
        check('recovered_'+str(x),r==z3.unsat,str(value))
    for fixed in [0,25,100]:
        solver.push();solver.add(F==fixed);r=solver.check();solver.pop()
        check('family_retains_fixed_'+str(fixed),r==z3.sat,'Different exposures with same historical interest')
    solver.push();solver.add(F==101);r=solver.check();solver.pop()
    check('impossible_debt_mix_rejected',r==z3.unsat,'Nonnegative floating amount forbids F=101')
    forecast=f['forecast']
    for branch,interest in [('fixed',Q(5)),('floating',Q(7))]:
        s=deepcopy(state); events=[]
        def e(name,entries,cls=None):
            record=dict(id='2025.'+name,period='2025_'+branch,date='2025-12-31',cash_class=cls,
                        postings=[dict(account=a,signed_amount=str(v)) for a,v in entries])
            events.append(record); post(s,record,{})
        demand=Q(forecast['demand_units']);price=Q(forecast['price']);cost=Q(forecast['unit_cost'])
        purchases=(demand+Q(forecast['target_inventory_units'])-s['inventory']/cost)*cost
        sales=demand*price; cogs=demand*cost
        collections=Q(forecast['current_sales_collection_fraction'])*sales+Q(forecast['legacy_receivable_collections'])
        suppliers=Q(forecast['old_payables_paid'])+Q(forecast['new_purchases_paid'])
        depreciation=Q(10)+Q(10)/5+Q(12)/12
        tax=(sales-cogs-Q(forecast['payroll'])-depreciation-interest)*Q(forecast['tax_rate'])
        e('sale',[('receivables',sales),('revenue',-sales)])
        e('collect',[('cash',collections),('receivables',-collections)],'operating')
        e('purchase',[('inventory',purchases),('payables',-purchases)])
        e('supplier',[('payables',suppliers),('cash',-suppliers)],'operating')
        e('deliver',[('cost_of_sales',cogs),('inventory',-cogs)])
        e('payroll',[('payroll',50),('cash',-50)],'operating')
        e('capex',[('plant_cost',20),('cash',-20)],'investing')
        e('depreciate',[('depreciation',depreciation),('accum_depreciation',-depreciation)])
        e('interest',[('interest',interest),('cash',-interest)],'operating')
        e('tax',[('tax',tax),('cash',-tax)],'operating')
        e('dividend',[('retained',8),('cash',-8)],'financing')
        result=report_close(s,events,f['accounts'],'2025_'+branch)
        compare('forecast_'+branch,result,f['expected']['2025_'+branch])
        check('direct_indirect_cash_'+branch,
              result['operating_cash']==result['profit']+depreciation-(s['receivables']-state['receivables'])-(s['inventory']-state['inventory'])-(s['payables']-state['payables']),
              'Profit + noncash depreciation - asset increases + liability increases')
    # Failure checks exercise atomicity and replay, not just successful sums.
    s=defaultdict(Q);done={}; good=dict(id='e',postings=[dict(account='cash',signed_amount='1'),dict(account='capital',signed_amount='-1')])
    post(s,good,done);post(s,good,done)
    check('event_idempotency',s['cash']==1,'Second identical event is a no-op')
    changed=deepcopy(good);changed['postings'][0]['signed_amount']='2'
    try:post(s,changed,done);raise AssertionError('Expected identity error')
    except ValueError as ex:check('event_identity_conflict',str(ex)=='EventIdentityConflict' and s['cash']==1,'Same ID different inputs rejected')
    changed['id']='bad'
    try:post(s,changed,done);raise AssertionError('Expected imbalance')
    except ValueError as ex:check('atomic_rejection',str(ex)=='UnbalancedBatch' and s['cash']==1 and 'bad' not in done,'No partial state/journal mutation')

def QZ(x):
    q=Q(x);return z3.RealVal(str(q.numerator)+'/'+str(q.denominator))

def bounds_and_weights():
    f=load('borrowings.json');F,V=z3.Reals('rounded_F rounded_V');D=F+V
    c=[F>=0,V>=0,D>=QZ('99.5'),D<QZ('100.5'),QZ('0.05')*D>=QZ('4.5'),QZ('0.05')*D<QZ('5.5')]
    I=QZ('.05')*F+QZ('.07')*V;s=z3.Solver();s.add(*c)
    for label,bound,comparison,attained in [('infimum','4.975',I<QZ('4.975'),True),('supremum','7.035',I>QZ('7.035'),False)]:
        s.push();s.add(comparison);r=s.check();s.pop()
        check('rounded_'+label+'_bound',r==z3.unsat,'Exact rational no-better-point certificate')
        s.push();s.add(I==QZ(bound));r=s.check();s.pop()
        check('rounded_'+label+'_attainment',(r==z3.sat)==attained,'Strict upper endpoint is not attained')
    # A sequence approaching the open supremum establishes sharpness, alongside its bound proof.
    for n in [10,100,1000]:
        s.push();s.add(F==0,D==QZ('100.5')-QZ(Q(1,n)));r=s.check();s.pop()
        check('upper_approach_'+str(n),r==z3.sat,'V = 100.5 - 1/n')
    prior=list(map(Q,f['mixture']['prior']));lik=list(map(Q,f['mixture']['likelihood_new_evidence']))
    mass=[a*b for a,b in zip(prior,lik)];postr=[x/sum(mass) for x in mass]
    check('finite_bayes',postr==list(map(Q,f['mixture']['expected_posterior'])),'New evidence changes weights; stress selection alone does not')
    check('joint_mixture',sum(w*x for w,x in zip(prior,[Q(5),Q(7)]))==Q('5.8'),'Mean from explicitly supplied weights only')
    check('partial_mass',prior[0]+prior[1]==1 and prior[1]==Q('.4'),'Unresolved .4 retained; no unconditional mean computed')

def temporal():
    f=load('temporal.json')
    for i,q in enumerate(f['queries']):
        eligible=[a for a in f['assertions'] if a['available']<=q['cutoff'] and (q.get('system_as_of') is None or a['ingested']<=q['system_as_of'])]
        if q.get('mode')=='original':eligible=[a for a in eligible if not a['supersedes']]
        else:
            superseded={x for a in eligible for x in a['supersedes']};eligible=[a for a in eligible if a['id'] not in superseded]
        check('temporal_query_'+str(i),{a['id'] for a in eligible}==set(q['expect']),q)
    check('restated_half_year',Q('260')-Q('110')==Q(f['expected_valid_h2']),'Original H1 has incompatible vintage; its subtraction is not a current-view H2')

def sector_checks():
    f=load('sectors.json');b=f['bank'];o={k:Q(v) for k,v in b['opening'].items()};e={k:Q(v) for k,v in b['events'].items()}
    a=dict(cash=o['cash']-e['external_transfer']+e['loan_interest_cash'],gross_loans=o['gross_loans']+e['origination'],allowance=e['allowance_target'],deposits=o['deposits']+e['origination']-e['external_transfer']+e['deposit_interest_accrued'],equity=o['equity']+e['loan_interest_cash']-e['deposit_interest_accrued']-(e['allowance_target']-o['allowance']))
    compare('bank_before_runoff',a,b['expected_before_runoff'])
    check('bank_funding',max(Q(0),Q(b['runoff'])-a['cash'])==Q(b['expected_draw'])<=Q(b['facility_limit']),'Draw 4 to settle runoff 25')
    check('bank_default_retained',Q(b['default_runoff'])-a['cash']-Q(b['facility_limit'])==Q(b['expected_unpaid']),'Unpaid 9 is an economic default outcome')
    check('bank_capital',a['equity']-Q(b['regulatory_deduction'])==Q(b['expected_CET1']) and a['gross_loans']*Q(b['risk_weight'])==Q(b['expected_RWA']),'Illustrative prudential assumptions, no Basel compliance claim')
    i=f['insurer'];v={k:Q(x) for k,x in i.items() if k!='expected'}
    revenue=v['premium']*v['service_fraction']; expense=v['gross_claim_estimate']+v['gross_risk_adjustment']
    recovery=v['gross_claim_estimate']*v['recovery_fraction']+v['ceded_risk_adjustment'];ceded_expense=v['ceded_premium']*v['service_fraction']
    profit=revenue-expense-ceded_expense+recovery
    a=dict(cash=v['opening_equity']+v['premium']-v['ceded_premium']-v['gross_claim_paid']+v['recovery_paid'],remaining_coverage_liability=v['premium']-revenue,incurred_claim_liability=expense-v['gross_claim_paid'],reinsurance_coverage_asset=v['ceded_premium']-ceded_expense,reinsurance_claim_asset=recovery-v['recovery_paid'],equity=v['opening_equity']+profit,profit=profit)
    a['assets']=a['cash']+a['reinsurance_coverage_asset']+a['reinsurance_claim_asset'];a['liabilities']=a['remaining_coverage_liability']+a['incurred_claim_liability']
    compare('insurance_rollforward',a,i['expected'])
    check('insurance_balance',a['assets']==a['liabilities']+a['equity'],'Gross and ceded state remain separate')
    c=f['consolidation'];v={k:Q(x) for k,x in c.items() if k!='expected'}
    nci=(1-v['ownership'])*v['sub_equity']
    check('consolidation',v['parent_cash']+v['sub_cash']+v['sub_plant']==v['parent_equity']+nci and nci==10,'Investment/equity elimination; intragroup loan leaves consolidated totals unchanged')
    check('disposal',v['disposal_proceeds']-v['investment']==v['expected_disposal_gain'] and v['parent_cash']+v['disposal_proceeds']==v['expected_after_disposal_cash'],'Loss of control removes subsidiary assets and NCI')
    inv=f['inventory'];lots=[(Q(x['quantity']),Q(x['unit_cost'])) for x in inv['purchases']];total=sum(q*p for q,p in lots)
    for name,seq in [('FIFO',lots),('LIFO',list(reversed(lots)))]:
        left=Q(inv['sold']);cost=Q(0)
        for qty,price in seq:
            take=min(left,qty);cost+=take*price;left-=take
        check('inventory_'+name,cost==Q(inv['expected'][name+'_cost']) and total-cost==Q(inv['expected'][name+'_stock']),'Same economic purchases, different permitted costing policies')
    avg=total/sum(q for q,p in lots);check('inventory_average',avg*Q(inv['sold'])==Q('72'),'Weighted-average cost comparator')

def main():
    started=time.monotonic();corporate();bounds_and_weights();temporal();sector_checks()
    report=dict(status='passed',date='2026-10-02',checks=checks,check_count=len(checks),
        scope='Design reference arithmetic, rational-linear solver, temporal selection and event oracle; no product implementation or accounting certification',
        environment=dict(python=platform.python_version(),z3=z3.get_version_string(),device='CPU utilities; no GPU framework',seed='N/A deterministic',git='unavailable'),
        command='python3 scripts/check_repair_conformance.py',plan='docs/plans/accounting-gap-repair-2026-10-02.md',wall_seconds=round(time.monotonic()-started,3),
        fixtures={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FIX.glob('*.json'))})
    path=ROOT/'docs/design/review/repair-conformance.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',checks=len(checks),report=str(path.relative_to(ROOT)))))

if __name__=='__main__':main()
