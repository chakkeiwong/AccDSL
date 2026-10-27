"""Authored examples. Expected amounts are supplied independently of the oracle."""
from copy import deepcopy
from fractions import Fraction as F

ISSUED='fcf ra csm loss acquisition_asset acquisition_gross lrc lic remaining_units investment allocation_carrying allocated_oci paa_cost_remaining unearned_premium'.split()
HELD='fcf_asset cost_csm loss_recovery'.split()
ACCOUNTS='cash underlying derivative equity profit oci revenue service_expense finance held_result'.split()
def amounts(v):
    if isinstance(v,bool) or v is None: return v
    if isinstance(v,(int,F)): return F(v)
    if isinstance(v,dict): return {k:amounts(x) for k,x in v.items()}
    if isinstance(v,list): return [amounts(x) for x in v]
    return v
def state(cash=200,issued=None,held=None,equity=None):
    s={'issued':dict(model='none',**{k:F(0) for k in ISSUED}),
       'replacement':dict(model='none',**{k:F(0) for k in ISSUED}),
       'held':{k:F(0) for k in HELD},'accounts':{k:F(0) for k in ACCOUNTS}}
    s['accounts'].update(cash=F(cash),equity=F(cash if equity is None else equity))
    s['issued'].update(amounts(issued or {})); s['held'].update(amounts(held or {})); return s
def close(old,updates=None,p=0,finance=0,held=0,oci=0):
    s=deepcopy(old)
    for role,values in (updates or {}).items(): s[role].update(amounts(values))
    a=s['accounts']; a['profit']+=F(p); a['finance']+=F(finance); a['held_result']+=F(held); a['oci']+=F(oci); a['equity']+=F(p)+F(oci)
    return s
CASES=[]
def case(key,method,event,opening,closing=None,detail=None,prior=None,codes=()):
    c=dict(id=key,input=amounts(dict(method_id=method,**event)),opening=opening,closing=closing or deepcopy(opening),detail=amounts(detail or {}),prior=prior,status='unresolved' if codes else 'resolved',diagnostics=list(codes))
    CASES.append(c); return c['closing']
def examples():
    CASES.clear(); zero=state()
    contract=dict(contract_id='contract-X',portfolio_id='portfolio-A',cohort='2024',profitability='other',contract_role='issued')
    grouping=dict(group_id='unrestricted-business-key-842',portfolio_id='portfolio-A',cohort='2024',profitability='other',contract_role='issued',membership='admitted',contracts=[contract])
    case('group-membership','grouping.assess@1',grouping,zero,detail=dict(group_id=grouping['group_id'],member_count=1,contract_role='issued'))
    case('group-unknown','grouping.assess@1',dict(grouping,membership='unknown'),zero,codes=['membership_unresolved'])
    e=dict(paid=8,target_group='issued-A',allocations=[dict(allocation_id='allocation-1',group_id='issued-A',amount=8)])
    a1=case('acquisition-allocated','acquisition.allocate@1',e,zero,close(zero,dict(issued=dict(acquisition_asset=8,acquisition_gross=8),accounts=dict(cash=192))),dict(allocated=8,unallocated=0))
    a2=case('acquisition-impaired','acquisition.recoverability@1',dict(recoverable=5),a1,close(a1,dict(issued=dict(acquisition_asset=5)),p=-3),dict(asset=5,impairment_expense=3),'acquisition-allocated')
    a3=case('acquisition-reversed','acquisition.recoverability@1',dict(recoverable=7),a2,close(a2,dict(issued=dict(acquisition_asset=7)),p=2),dict(asset=7,impairment_expense=-2),'acquisition-impaired')
    a4=case('gmm-acquisition-transfer','gmm.recognize@1',dict(premium=100,claims=90,ra=2,units=2),a3,close(a3,dict(issued=dict(model='GMM',fcf=92,ra=2,csm=1,acquisition_asset=0,acquisition_gross=0,remaining_units=2),accounts=dict(cash=292))),dict(transferred_acquisition=7,initial_loss=0,csm=1),'acquisition-reversed')
    case('gmm-half-service','gmm.service@1',dict(owner='issued',units=1,expected_claims=45,ra_release=1,actual_claims=45),a4,close(a4,dict(issued=dict(fcf=46,ra=1,csm=F(1,2),remaining_units=1),accounts=dict(cash=247,revenue=F(93,2),service_expense=45)),p=F(3,2)),dict(revenue=F(93,2),csm_release=F(1,2),claims_expense=45),'gmm-acquisition-transfer')
    f=state(200,dict(model='GMM',fcf=80,csm=20,remaining_units=2),equity=100)
    f1=case('future-adverse-15','gmm.future@1',dict(fcf_change=15),f,close(f,dict(issued=dict(fcf=95,csm=5))),dict(loss_change=0,profit_change=0,csm=5))
    f2=case('future-exhausts-csm','gmm.future@1',dict(fcf_change=10),f1,close(f1,dict(issued=dict(fcf=105,csm=0,loss=5)),p=-5),dict(loss_change=5,profit_change=-5,csm=0),'future-adverse-15')
    case('future-reverses-loss','gmm.future@1',dict(fcf_change=-8),f2,close(f2,dict(issued=dict(fcf=97,csm=3,loss=0)),p=5),dict(loss_change=-5,profit_change=5,csm=3),'future-exhausts-csm')
    b=state(50)
    b1=case('onerous-issued','gmm.recognize@1',dict(premium=100,claims=118,ra=2,units=1),b,close(b,dict(issued=dict(model='GMM',fcf=120,ra=2,loss=20,remaining_units=1),accounts=dict(cash=150)),p=-20),dict(transferred_acquisition=0,initial_loss=20,csm=0))
    treaty=dict(entry_date='2024-01-01',recognition_date='2024-01-01',coverage_start='2024-01-01',underlying_recognition='2024-01-01',share=F(1,2),covered_loss=8,covered_claims=48,premium=F(53,2),transferred_ra=F(1,2),covered_group='issued-A',issued_group='issued-A',coverage_mapping='admitted',allocations=[dict(contract_id='covered-C',covered=True,premium=41,claims=48,ra=1),dict(contract_id='uncovered-U',covered=False,premium=59,claims=70,ra=1)])
    b2=case('partial-treaty','reinsurance.recognize@1',treaty,b1,close(b1,dict(held=dict(fcf_asset=F(49,2),cost_csm=6,loss_recovery=4),accounts=dict(cash=F(247,2))),p=4,held=4),dict(expected_recovery=24,initial_loss_recovery=4,held_asset=F(61,2)),'onerous-issued')
    b3=case('covered-estimate-change','reinsurance.change@1',dict(cause='covered_claim_estimate',issued_csm_treatment='loss_reversal',old_covered_claims=48,new_covered_claims=44,new_covered_loss=4,share=F(1,2)),b2,close(b2,dict(issued=dict(fcf=116,loss=16),held=dict(fcf_asset=F(45,2),loss_recovery=2)),p=2,held=-2),dict(issued_loss_reversal=4,held_expense=2,recovery_cap=2),'partial-treaty')
    case('joint-service-settlement','reinsurance.settle@1',dict(claims=114,recovery=22,transferred_ra=F(1,2)),b3,close(b3,dict(issued=dict(fcf=0,ra=0,csm=0,loss=0,remaining_units=0),held=dict(fcf_asset=0,cost_csm=0,loss_recovery=0),accounts=dict(cash=F(63,2),revenue=100,service_expense=98)),p=F(-9,2),held=F(-13,2)),dict(issued_profit=2,held_result=F(-13,2),issued_revenue=100),'covered-estimate-change')
    case('late-treaty','reinsurance.recognize@1',dict(treaty,entry_date='2024-01-02',recognition_date='2024-01-02'),b1,close(b1,dict(held=dict(fcf_asset=F(49,2),cost_csm=2),accounts=dict(cash=F(247,2)))),dict(expected_recovery=24,initial_loss_recovery=0,held_asset=F(53,2)),'onerous-issued')
    case('held-collectability','reinsurance.nonperformance@1',dict(loss=1),b2,close(b2,dict(held=dict(fcf_asset=F(47,2))),p=-1,held=-1),dict(collectability_expense=1,csm_change=0),'partial-treaty')
    mod=state(200,dict(model='GMM',fcf=100,ra=10,csm=30,remaining_units=3),equity=70)
    me=dict(equivalent_premium=60,actual_extra=10,removed_fcf=40,removed_ra=4,removed_units=1,new_fcf=52,new_ra=4,new_units=1,modification_test='derecognize',existing_right=False)
    m1=case('modification-replacement','modification.replace@1',me,mod,close(mod,dict(issued=dict(fcf=60,ra=6,csm=20,remaining_units=2),replacement=dict(model='GMM',fcf=52,ra=4,csm=8,remaining_units=1),accounts=dict(cash=210))),dict(deemed_or_transfer=50,actual_cash_change=10,old_csm=20,loss=0))
    m2=case('modified-old-service','gmm.service@1',dict(owner='issued',units=2,expected_claims=54,ra_release=6,actual_claims=54),m1,close(m1,dict(issued=dict(fcf=0,ra=0,csm=0,remaining_units=0),accounts=dict(cash=156,revenue=80,service_expense=54)),p=26),dict(revenue=80,csm_release=20,claims_expense=54),'modification-replacement')
    case('modified-new-service','gmm.service@1',dict(owner='replacement',units=1,expected_claims=48,ra_release=4,actual_claims=48),m2,close(m2,dict(replacement=dict(fcf=0,ra=0,csm=0,remaining_units=0),accounts=dict(cash=108,revenue=140,service_expense=102)),p=12),dict(revenue=60,csm_release=8,claims_expense=48),'modified-old-service')
    case('third-party-transfer','contract.transfer@1',dict(third_party_premium=50,removed_fcf=40,removed_ra=4,removed_units=1),mod,close(mod,dict(issued=dict(fcf=60,ra=6,csm=20,remaining_units=2),accounts=dict(cash=150))),dict(deemed_or_transfer=50,actual_cash_change=-50,old_csm=20,loss=0))
    short=state(200,dict(model='GMM',fcf=100,ra=10,csm=6,remaining_units=3),equity=94)
    case('modification-exhausts-csm','modification.replace@1',me,short,close(short,dict(issued=dict(fcf=60,ra=6,csm=0,loss=4,remaining_units=2),replacement=dict(model='GMM',fcf=52,ra=4,csm=8,remaining_units=1),accounts=dict(cash=210)),p=-4),dict(deemed_or_transfer=50,actual_cash_change=10,old_csm=0,loss=4))
    case('modification-value-unknown','modification.replace@1',dict(me,equivalent_premium=None),mod,codes=['equivalent_premium_unresolved'])
    model_examples(zero)
    return deepcopy(CASES)

def model_examples(zero):
    for expensed in (False,True):
        prefix='paa-expensed' if expensed else 'paa-deferred'; cost=0 if expensed else 12
        ev=dict(premium=120,acquisition_paid=12,coverage_years=1,eligibility='admitted',expense_election=expensed,units=2)
        p1=case(prefix,'paa.recognize@1',ev,zero,close(zero,dict(issued=dict(model='PAA',lrc=120-cost,paa_cost_remaining=cost,unearned_premium=120,remaining_units=2),accounts=dict(cash=308)),p=-12 if expensed else 0),dict(lrc=120-cost,acquisition_expense=12 if expensed else 0,cash_change=108))
        p2=case(prefix+'-half','paa.service@1',dict(units=1),p1,close(p1,dict(issued=dict(lrc=60-F(cost,2),paa_cost_remaining=F(cost,2),unearned_premium=60,remaining_units=1),accounts=dict(revenue=60,service_expense=F(cost,2))),p=60-F(cost,2)),dict(revenue=60,acquisition_expense=F(cost,2),lrc=60-F(cost,2)),prefix)
        if not expensed:
            case('paa-onerous-addition','paa.onerous@1',dict(remaining_fcf=70,facts_indicate_onerous=True),p2,close(p2,dict(issued=dict(lrc=70,loss=16)),p=-16),dict(additional_loss=16,lrc=70),prefix+'-half')
            p3=case('paa-coverage-end','paa.service@1',dict(units=1),p2,close(p2,dict(issued=dict(lrc=0,paa_cost_remaining=0,unearned_premium=0,remaining_units=0),accounts=dict(revenue=120,service_expense=12)),p=54),dict(revenue=60,acquisition_expense=6,lrc=0),prefix+'-half')
            p4=case('paa-claim-incurred','paa.claim@1',dict(payment=F(242,5),years=2,incurrence_rate=F(1,10),ra=2,rate_origin='claim_incurrence',rate_date='2024-12-31',claim_date='2024-12-31'),p3,close(p3,dict(issued=dict(lic=42,ra=2,fcf=2,allocation_carrying=40),accounts=dict(service_expense=54)),p=-42),dict(claim_pv=40,lic=42,incurrence_rate=F(1,10)),'paa-coverage-end')
            fe=dict(payment=F(242,5),incurrence_rate=F(1,10),current_rate=0,remaining_years=1,ra_release=1,rate_origin='claim_incurrence',rate_date='2024-12-31',claim_date='2024-12-31')
            p5=case('paa-lic-first-finance','paa.finance@1',fe,p4,close(p4,dict(issued=dict(lic=F(247,5),ra=1,fcf=1,allocation_carrying=44),accounts=dict(revenue=121)),p=-3,finance=-4,oci=F(-22,5)),dict(profit_finance_expense=4,oci_income=F(-22,5),current_finance_expense=F(42,5),ra_release=1,lic=F(247,5)),'paa-claim-incurred')
            p6=case('paa-lic-final-finance','paa.finance@1',dict(fe,remaining_years=0),p5,close(p5,dict(issued=dict(lic=F(242,5),ra=0,fcf=0,allocation_carrying=F(242,5)),accounts=dict(revenue=122)),p=F(-17,5),finance=F(-22,5),oci=F(22,5)),dict(profit_finance_expense=F(22,5),oci_income=F(22,5),current_finance_expense=0,ra_release=1,lic=F(242,5)),'paa-lic-first-finance')
            case('paa-claim-paid','paa.settle@1',dict(payment=F(242,5)),p6,close(p6,dict(issued=dict(lic=0,allocation_carrying=0),accounts=dict(cash=F(1298,5)))),dict(cash_paid=F(242,5),revenue=0),'paa-lic-final-finance')
    ve=dict(premium=100,pool=100,policyholder_share=F(4,5),claims=10,ra=2,units=2,participation='admitted',insurance='admitted',role='issued')
    v1=case('vfa-recognized','vfa.recognize@1',ve,zero,close(zero,dict(issued=dict(model='VFA',fcf=92,ra=2,csm=8,investment=80,remaining_units=2),accounts=dict(underlying=100))),dict(investment_component=80,fcf=92,csm=8))
    v2=case('vfa-pool-appreciation','vfa.pool@1',dict(new_pool=120,policyholder_share=F(4,5),holding='held',finance_policy='all_profit'),v1,close(v1,dict(issued=dict(fcf=108,csm=12,investment=96),accounts=dict(underlying=120))),dict(asset_gain=20,liability_finance_expense=20,fee_to_csm=4,investment_component=96),'vfa-recognized')
    v3=case('vfa-first-service','vfa.service@1',dict(units=1,claims=5,ra_release=1),v2,close(v2,dict(issued=dict(fcf=102,ra=1,csm=6,remaining_units=1),accounts=dict(cash=195,revenue=12,service_expense=5)),p=7),dict(service_revenue=12,csm_release=6,profit=7,investment_revenue=0),'vfa-pool-appreciation')
    v4=case('vfa-final-service','vfa.service@1',dict(units=1,claims=5,ra_release=1),v3,close(v3,dict(issued=dict(fcf=96,ra=0,csm=0,remaining_units=0),accounts=dict(cash=190,revenue=24,service_expense=10)),p=7),dict(service_revenue=12,csm_release=6,profit=7,investment_revenue=0),'vfa-first-service')
    case('vfa-investment-repaid','vfa.settle@1',dict(investment_payment=96),v4,close(v4,dict(issued=dict(fcf=0,investment=0),accounts=dict(cash=214,underlying=0))),dict(investment_paid=96,investment_revenue=0,investment_expense=0),'vfa-final-service')
    ge=dict(change=6,derivative_gain=6,change_kind='financial_guarantee',mitigation=False,strategy='none',economic_offset='unknown',credit_not_dominant='unknown')
    case('vfa-guarantee-no-mitigation','vfa.guarantee@1',ge,v1,close(v1,dict(issued=dict(fcf=98,csm=2),accounts=dict(derivative=6)),p=6,finance=6),dict(csm=2,loss=0,derivative_gain=6,profit_change=6),'vfa-recognized')
    case('vfa-guarantee-mitigated','vfa.guarantee@1',dict(ge,mitigation=True,strategy='prior_documented',economic_offset='admitted',credit_not_dominant='admitted'),v1,close(v1,dict(issued=dict(fcf=98),accounts=dict(derivative=6))),dict(csm=8,loss=0,derivative_gain=6,profit_change=0),'vfa-recognized')
    case('vfa-adverse-cost-loss','vfa.guarantee@1',dict(ge,change=15,derivative_gain=0,change_kind='nonfinancial'),v1,close(v1,dict(issued=dict(fcf=107,csm=0,loss=7)),p=-7),dict(csm=0,loss=7,derivative_gain=0,profit_change=-7),'vfa-recognized')
    r=state(200,dict(model='GMM',fcf=100,allocation_carrying=100),equity=100)
    ev=dict(payment=144,allocation_rate=F(1,5),current_rate=F(1,10),remaining_years=2,elapsed_years=0,allocation_basis='prospective_revised')
    r1=case('variable-prospective-remeasurement','finance.variable@1',ev,r,close(r,dict(issued=dict(fcf=F(14400,121))),oci=F(-2300,121)),dict(profit_finance_expense=0,oci_income=F(-2300,121),current_liability=F(14400,121),allocation_carrying=100))
    r2=case('variable-first-finance','finance.variable@1',dict(ev,elapsed_years=1),r1,close(r1,dict(issued=dict(fcf=F(1440,11),allocation_carrying=120)),p=-20,finance=-20,oci=F(980,121)),dict(profit_finance_expense=20,oci_income=F(980,121),current_liability=F(1440,11),allocation_carrying=120),'variable-prospective-remeasurement')
    case('variable-final-finance','finance.variable@1',dict(ev,remaining_years=1,elapsed_years=1),r2,close(r2,dict(issued=dict(fcf=144,allocation_carrying=144)),p=-24,finance=-24,oci=F(120,11)),dict(profit_finance_expense=24,oci_income=F(120,11),current_liability=144,allocation_carrying=144),'variable-first-finance')
