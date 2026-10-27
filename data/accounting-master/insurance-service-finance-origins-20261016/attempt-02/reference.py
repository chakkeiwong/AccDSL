"""Finite documentary insurance origin exchanges; no state mutation."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import date
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
FINDINGS={'source_profile_applicable','opening_balances_supported','complete_events','information_view_valid','no_tax_fx_or_unrecorded_cash'}
class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason
def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(v,keys,reason):
    if not isinstance(v,dict) or set(v)!=set(keys):fail(reason)
def number(x):
    if x is None:fail('missing_amount','unresolved')
    if not isinstance(x,str) or len(x)>80:fail('number_encoding')
    try:y=Q(x)
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if str(y)!=x or abs(y)>10**12:fail('number_encoding')
    return y
def nonnegative(x):
    y=number(x)
    if y<0:fail('negative_amount')
    return y
def findings(v,keys):
    shape(v,keys,'finding_shape')
    for k,x in v.items():
        if x is None:fail('missing_'+k,'unresolved')
        if type(x)!=bool:fail('finding_encoding')
        if not x:fail('outside_'+k,'unsupported')
def day(x):
    try:d=date.fromisoformat(x)
    except (ValueError,TypeError):fail('date_encoding')
    if d.isoformat()!=x:fail('date_encoding')
    return d
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x
def calculate(req,reader=None):
    try:
        reader=reader or (lambda p:(ROOT/p).read_bytes())
        for item in json.loads((OUT/'input-lock-v2.json').read_text())['files']:
            try:raw=reader(item['path'])
            except FileNotFoundError:fail('missing_protected_input','unresolved')
            if hashlib.sha256(raw).hexdigest()!=item['sha256']:fail('changed_protected_input')
        shape(req,{'wire','operation','context','findings','data'},'request_shape')
        if req['wire']!='InsuranceOrigins/1':fail('wire')
        shape(req['context'],{'entity','group','currency','unit','rule'},'context_shape')
        if any(not isinstance(v,str) or not v for v in req['context'].values()):fail('context_encoding')
        if req['context']['unit']!='currency units' or req['context']['rule']!='EU2023/1803-original-IFRS17':fail('context')
        findings(req['findings'],FINDINGS)
        operations={'loss_schedule':loss_schedule,'recovery_change':recovery_change,'policy_switch':policy_switch,'derecognize':derecognize}
        if req['operation'] not in operations:fail('operation')
        r=operations[req['operation']](req['data'])
        return encode(dict(status='conditional_complete',reason='finite_origin_method',operation=req['operation'],context=req['context'],report=r,posts=False,mutations=[]))
    except Refusal as e:return dict(status=e.status,reason=e.reason,report=None,posts=False,mutations=[])
    except (ValueError,ZeroDivisionError):return dict(status='rejected',reason='numeric_domain',report=None,posts=False,mutations=[])

def loss_schedule(d):
    shape(d,{'opening_date','cash','liability','loss_component','periods','findings'},'loss_shape')
    findings(d['findings'],{'proportional_allocation_supported','csm_zero','no_new_estimates','claim_ra_releases_supported','all_finance_in_profit','no_investment_or_acquisition_component'})
    L=nonnegative(d['liability']);K=nonnegative(d['loss_component']);cash=nonnegative(d['cash']);t=day(d['opening_date'])
    if L<=0 or K>L:fail('loss_component_domain')
    equity=cash-L;opening_equity=equity;ratio=K/L;rows=[];journal=[];origins=[]
    service=Q(0);finance_total=Q(0)
    if not isinstance(d['periods'],list) or not 1<=len(d['periods'])<=32:fail('periods_shape')
    for i,p in enumerate(d['periods']):
        shape(p,{'date','information_date','finance_expense','claim_release','ra_release','actual_claims','coverage_end'},'period_shape')
        nt=day(p['date'])
        if nt<=t or day(p['information_date'])>nt or day(p['information_date'])<day(d['opening_date']):fail('period_chronology')
        fin=number(p['finance_expense']);claims=nonnegative(p['claim_release']);ra=nonnegative(p['ra_release']);actual=nonnegative(p['actual_claims'])
        if type(p['coverage_end'])!=bool:fail('coverage_encoding')
        if p['coverage_end']!=(i==len(d['periods'])-1):fail('coverage_sequence')
        if L+fin<=0:fail('finance_exhausts_liability','unsupported')
        loss_fin=ratio*fin;L+=fin;K+=loss_fin
        release=claims+ra
        if release>L or actual>cash:fail('release_or_cash_domain')
        lc=ratio*claims;lr=ratio*ra;reversal=lc+lr;revenue=release-reversal
        L-=release;K-=reversal;cash-=actual;period_service=revenue+reversal-actual
        service+=period_service;finance_total+=fin;equity+=period_service-fin;t=nt
        if L<0 or K<0 or K>L or K!=ratio*L:fail('loss_allocation_identity')
        if p['coverage_end'] and (L or K):fail('coverage_end_not_exhausted')
        if cash-L!=equity:fail('financial_identity')
        row=dict(date=p['date'],liability=L,loss_component=K,cash=cash,equity=equity,finance_expense=fin,loss_finance=loss_fin,
            claim_loss_release=lc,ra_loss_release=lr,loss_reversal=reversal,revenue=revenue,claims_expense=actual,service_profit=period_service,profit=period_service-fin)
        rows.append(row);origins.extend([dict(date=p['date'],kind='finance',loss_change=loss_fin),dict(date=p['date'],kind='claim_release',loss_change=-lc),dict(date=p['date'],kind='ra_release',loss_change=-lr)])
        journal.extend([dict(finance_expense=fin,liability=-fin),dict(liability=release,revenue=-revenue,loss_reversal=-reversal),dict(claims_expense=actual,cash=-actual)])
    return dict(rows=rows,journals=journal,loss_origins=origins,closing=rows[-1],ratio=ratio,total_service_profit=service,total_finance_expense=finance_total,total_profit=service-finance_total,opening_equity=opening_equity)

def recovery_change(d):
    keys={'cash','issued_claims','issued_ra','issued_loss','covered_claims','covered_loss','quota','held_ra','held_cost_csm','held_loss_recovery','covered_claim_decrease','findings'}
    shape(d,keys,'recovery_shape');findings(d['findings'],{'timely_treaty','covered_loss_allocation_supported','zero_rates','no_other_changes','full_remaining_service','quota_terms_supported'})
    x={k:nonnegative(v) for k,v in d.items() if k!='findings'}
    c=x['cash'];claims=x['issued_claims'];ra=x['issued_ra'];K=x['issued_loss'];covered=x['covered_claims'];ck=x['covered_loss'];q=x['quota'];decrease=x['covered_claim_decrease']
    hra=x['held_ra'];hc=x['held_cost_csm'];R=x['held_loss_recovery']
    if not 0<q<=1 or ck>K or covered>claims or K>claims+ra or decrease>min(ck,covered) or R!=ck*q:fail('recovery_domain')
    old_held=covered*q+hra+hc;old_issued=claims+ra;opening_equity=c+old_held-old_issued
    new_claims=claims-decrease;newK=K-decrease;newcovered=covered-decrease
    held_fcf_change=-decrease*q;newR=(ck-decrease)*q
    new_held=old_held+held_fcf_change;new_issued=old_issued-decrease
    if newR-R!=held_fcf_change:fail('recovery_origin_identity')
    change_profit=decrease+held_fcf_change
    changed=dict(issued_liability=new_issued,issued_loss=newK,held_asset=new_held,held_cost_csm=hc,held_loss_recovery=newR,
        issued_loss_reversal=decrease,held_profit=held_fcf_change,additional_component_expense=Q(0),cash=c,equity=c+new_held-new_issued)
    issued_revenue=new_issued-newK;issued_service=issued_revenue+newK-new_claims
    premium_allocation=new_held-newR;recovery=newcovered*q;held_service=recovery-premium_allocation-newR
    final_cash=c-new_claims+recovery
    if c<new_claims:fail('claims_funding','unsupported')
    if final_cash-opening_equity!=change_profit+issued_service+held_service:fail('recovery_financial_identity')
    return dict(opening_equity=opening_equity,change=changed,closing=dict(cash=final_cash,equity=final_cash,issued_liability=Q(0),held_asset=Q(0),issued_loss=Q(0),held_loss_recovery=Q(0)),
        issued_service=dict(revenue=issued_revenue,loss_reversal=newK,claim_expense=new_claims,profit=issued_service),
        held_service=dict(recovery=recovery,premium_allocation=premium_allocation,loss_recovery_reversal=newR,profit=held_service),total_profit=change_profit+issued_service+held_service,
        cash_flows=[dict(kind='claim_payment',amount=-new_claims),dict(kind='recovery_collection',amount=recovery)])

def policy_switch(d):
    shape(d,{'date','old_policy','new_policy','terminal','years','old_current_rate','old_allocation_rate','old_allocation_carrying','old_oci','post_change_cash','new_allocation_rate','periods','findings'},'switch_shape')
    findings(d['findings'],{'direct_participation_at_origin','holding_change_supported','old_assumptions_supported','no_remaining_service_csm_ra','frozen_assumptions','comparatives_unchanged','post_change_cash_supported','underlying_measurement_supported'})
    old=d['old_policy'];new=d['new_policy']
    if (old,new) not in {('88b','89b'),('89b','88b')}:fail('policy_pair')
    n=d['years'];start=day(d['date'])
    if type(n)!=int or not 1<=n<=10 or not isinstance(d['periods'],list) or len(d['periods'])!=n:fail('switch_horizon')
    T=nonnegative(d['terminal']);cr=number(d['old_current_rate']);ar=number(d['old_allocation_rate']);alloc=nonnegative(d['old_allocation_carrying']);oldO=number(d['old_oci']);cash=nonnegative(d['post_change_cash'])
    if T<=0 or cr<=-1 or ar<=-1:fail('rate_domain')
    L=T/(1+cr)**n
    if alloc*(1+ar)**n!=T or oldO!=alloc-L:fail('frozen_opening_identity')
    if new=='88b':
        nr=number(d['new_allocation_rate'])
        if nr<=-1 or L*(1+nr)**n!=T:fail('new_allocation_identity')
    elif d['new_allocation_rate'] is not None:fail('matching_has_no_systematic_rate')
    asset=L if new=='89b' else Q(0);equity=cash+asset-L;opening_eq=equity;initialL=L
    old_origin=oldO;newO=Q(0);assetO=Q(0);profit=Q(0);rows=[];newalloc=L
    for i,p in enumerate(d['periods'],1):
        shape(p,{'date','information_date','current_liability','asset_profit_income','asset_oci_income','actual_holdings','findings'},'switch_period_shape')
        findings(p['findings'],{'valuation_supported','all_changes_financial','no_interim_cash'})
        if day(p['date'])!=date(start.year+i,start.month,start.day) or not start<=day(p['information_date'])<=day(p['date']):fail('switch_chronology')
        if type(p['actual_holdings'])!=bool or p['actual_holdings']!=(new=='89b'):fail('holdings_mismatch','unsupported')
        actualL=nonnegative(p['current_liability']);ap=number(p['asset_profit_income']);ao=number(p['asset_oci_income'])
        total_fin=actualL-L
        old_current=T/(1+cr)**(n-i);old_alloc=alloc*(1+ar)**i
        frozenO=old_alloc-old_current;reclass_expense=frozenO-old_origin
        if new=='89b':
            if asset+ap+ao!=actualL:fail('underlying_return_identity')
            asset+=ap+ao;current_profit_expense=ap;assetO+=ao
        else:
            if ap or ao:fail('unheld_underlying_return')
            current_profit_expense=newalloc*nr;newalloc+=current_profit_expense
        current_oci=current_profit_expense-total_fin
        period_profit=ap-current_profit_expense-reclass_expense;period_oci=ao+current_oci+reclass_expense
        profit+=period_profit;newO+=current_oci;old_origin=frozenO;equity+=period_profit+period_oci;L=actualL
        if cash+asset-L!=equity:fail('switch_financial_identity')
        rows.append(dict(date=p['date'],liability=L,asset=asset,cash=cash,equity=equity,actual_total_finance=total_fin,asset_profit=ap,period_asset_oci=ao,
            current_profit_expense=current_profit_expense,current_oci=current_oci,old_reclassification_expense=reclass_expense,
            old_oci=old_origin,new_oci=newO,asset_oci=assetO,profit=period_profit,oci=period_oci,
            counterfactual_current=old_current,counterfactual_allocation=old_alloc))
    if L!=T or old_origin or newO or assetO:fail('terminal_finance_not_exhausted')
    if new=='89b':
        if asset!=T:fail('terminal_asset')
        cash+=asset;asset=Q(0)
    if cash<T:fail('settlement_funding','unsupported')
    cash-=T;L=Q(0)
    if cash!=equity or equity-opening_eq!=profit-oldO:fail('switch_closing_identity')
    return dict(rows=rows,opening_equity=opening_eq,initial_liability=initialL,initial_old_oci=oldO,total_profit=profit,total_oci=-oldO,
        closing=dict(cash=cash,asset=asset,liability=L,equity=equity,old_oci=old_origin,new_oci=newO),
        frozen_assumptions={k:d[k] for k in ('old_policy','terminal','years','old_current_rate','old_allocation_rate','old_allocation_carrying')})

def derecognize(d):
    shape(d,{'origin_policy','accumulated_oci','cash','other_assets','liability','transfer_cash','findings'},'derecognition_shape')
    findings(d['findings'],{'paragraph91_event','homogeneous_oci_origin','transfer_at_carrying','no_remaining_service_csm_ra','other_assets_unchanged','no_pending_policy_runoff'})
    policy=d['origin_policy']
    if policy not in ('88b','89b'):fail('oci_origin','unsupported')
    O=number(d['accumulated_oci']);cash=nonnegative(d['cash']);asset=nonnegative(d['other_assets']);L=nonnegative(d['liability']);paid=nonnegative(d['transfer_cash'])
    if paid!=L or paid>cash:fail('transfer_cash_identity')
    equity=cash+asset-L;recycle=O if policy=='88b' else Q(0);remaining=O-recycle
    return dict(profit_reclassification=recycle,oci_reclassification=-recycle,within_equity_transfer=Q(0),
        closing=dict(cash=cash-paid,other_assets=asset,liability=Q(0),equity=equity,oci=remaining),
        cash_flows=[dict(kind='transfer_payment',amount=-paid)],total_equity_change=Q(0),
        policy=policy,retained_oci_presentation='retained_in_oci' if policy=='89b' else 'recycled')
