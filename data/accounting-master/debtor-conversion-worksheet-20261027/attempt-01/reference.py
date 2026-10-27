from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json,re
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('debt_scope_v1',H.parent/'acquisition-debt-relationship-20261027/reference.py')
scope=importlib.util.module_from_spec(spec);spec.loader.exec_module(scope)
PROFILE='ConditionalDebtorConversionWorksheet/1'
FLAGS=scope.FLAGS;need=scope.need;fields=scope.fields;digest=scope.digest;moment=scope.moment
ACCOUNTS=['cash','equipment','debt','opening_capital','issued_equity','settlement_gain']
def number(x):
    need(isinstance(x,str) and len(x)<60 and re.fullmatch(r'-?[0-9]+/[1-9][0-9]*',x),'exact_number')
    return F(x)
def fmt(v):v=F(v);return str(v.numerator)+'/'+str(v.denominator)
def serial(x):
    if isinstance(x,F):return fmt(x)
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,list):return [serial(v) for v in x]
    return x
def report(request):
    try:
        need(len(json.dumps(request,allow_nan=False))<150000,'request_size')
        fields(request,['profile','payload','expected_payload_sha256'],'envelope')
        need(request['profile']==PROFILE,'profile');p=request['payload'];need(digest(p)==request['expected_payload_sha256'],'payload_binding')
        fields(p,['scope_request','scope_result_sha256','schedule','source','evidence_sha256'],'payload')
        sc=scope.derive(p['scope_request']);need(sc['status']!='invalid','invalid_scope')
        need(digest(sc)==p['scope_result_sha256'],'scope_result_binding')
        s=p['schedule'];fields(s,['currency','unit','opening_at','close_at','opening','premises','measurement'],'schedule')
        need(s['currency']=='USD' and s['unit']=='currency_unit','units')
        c=sc['context'];need(moment(s['opening_at'])<moment(c['at'])<moment(s['close_at'])<=moment(c['cutoff']),'schedule_dates')
        src=p['source'];fields(src,['text','rationale','subject','actor','available_at','schedule_sha256'],'source')
        scope.text(src['text'],'source_text');scope.text(src['rationale'],'source_rationale')
        need(src['subject']==c['subject'] and src['actor']==c['actor'],'source_context')
        need(src['schedule_sha256']==digest(s),'schedule_source_binding');need(p['evidence_sha256']==digest(src),'evidence_binding')
        opening=s['opening'];fields(opening,ACCOUNTS,'opening')
        opening={k:number(v) for k,v in opening.items()}
        need(opening==dict(cash=F(30),equipment=F(100),debt=F(-100),opening_capital=F(-30),issued_equity=F(0),settlement_gain=F(0)),'selected_opening')
        prem=s['premises'];fields(prem,['debt_classification','issued_classification','tax','fees','interest','other_activity','cash_legs'],'premises')
        domains=dict(debt_classification=['financial_liability','unresolved'],issued_classification=['equity','unresolved'],
                     tax=['explicit_zero_current_and_deferred','unresolved'],fees=['explicit_none','unresolved'],
                     interest=['explicit_none','unresolved'],other_activity=['explicit_none','unresolved'],cash_legs=['explicit_none','unresolved'])
        deps=[]
        for k,domain in domains.items():
            need(prem[k] in domain,'premise_'+k)
            if prem[k]=='unresolved':deps.append('premise:'+k)
        m=s['measurement'];fields(m,['equity_fv_reliable','equity_fair_value','liability_fair_value'],'measurement')
        need(m['equity_fv_reliable'] in ['yes','no','unknown'],'measurement_reliability')
        for k in ['equity_fair_value','liability_fair_value']:
            if m[k] is not None:need(number(m[k])>=0,'nonnegative_'+k)
        if m['equity_fv_reliable']=='yes':
            basis='equity_fair_value';value=m['equity_fair_value']
        elif m['equity_fv_reliable']=='no':
            basis='liability_fair_value';value=m['liability_fair_value']
        else:basis=None;value=None;deps.append('equity_fair_value_reliability')
        if basis and value is None:deps.append('measurement:'+basis)
        if src['available_at'] is None:deps.append('measurement_source_availability_unknown')
        elif moment(src['available_at'])>moment(c['cutoff']):deps.append('measurement_source_after_cutoff')
        if sc['status']!='conditional_scope' or sc['route']!='debtor_int19_method_required':deps.append('required_debtor_scope')
        f=sc['assertions']
        if f['liability_extinguished']!='yes':deps.append('whole_liability_extinguishment_required')
        if f['partial_extinguishment']!='no':deps.append('partial_or_unknown_extent_method')
        out=dict(profile=PROFILE,**FLAGS,request_sha256=digest(request),scope_result=deepcopy(sc),
                 schedule=deepcopy(s),source=deepcopy(src),scope_assessment='supplied_assertions_only')
        if deps:return dict(out,status='method_required',dependencies=sorted(set(deps)),request=deepcopy(request),report=None)
        E=number(value);L=-opening['debt'];gain=L-E
        journal=dict(id='full-debt-equity-exchange',at=c['at'],entity=c['subject'],
                     entries=dict(debt=L,issued_equity=-E,settlement_gain=-gain),cash_movement=F(0))
        need(sum(journal['entries'].values())==0,'journal_balance')
        close=deepcopy(opening)
        for k,v in journal['entries'].items():close[k]+=v
        need(sum(close.values())==0,'trial_balance')
        assets=close['cash']+close['equipment'];liabilities=-close['debt']
        contributed=-close['opening_capital']-close['issued_equity'];earnings=-close['settlement_gain']
        eq=contributed+earnings;need(assets-liabilities==eq,'balance_sheet')
        rep=dict(balance_sheet=dict(assets=dict(cash=close['cash'],equipment=close['equipment']),assets_total=assets,
                  liabilities=dict(financial_debt=liabilities),liabilities_total=liabilities,
                  equity=dict(opening_contributed=-close['opening_capital'],new_issued_equity=E,current_earnings=earnings),equity_total=eq),
          income=dict(settlement_result=gain,tax=F(0),profit=gain,other_comprehensive_income=F(0),total_comprehensive_income=gain),
          cash_flow=dict(opening_cash=opening['cash'],operating=F(0),investing=F(0),financing=F(0),net_change=F(0),closing_cash=close['cash']),
          equity_reconciliation=dict(opening=F(30),shares_issued=E,profit=gain,oci=F(0),closing=eq),
          noncash_exchange=dict(debt_extinguished=L,equity_recognised=E,settlement_result=gain))
        need(rep['equity_reconciliation']['opening']+E+gain==eq,'equity_bridge')
        return serial(dict(out,status='conditional_debtor_worksheet',measurement_basis=basis,measurement=E,
          opening=opening,legal_journals=[journal],closing=close,report=rep,
          outstanding=['actual_source_and_period_authority','actual_measurement_and_classification','tax_and_full_disclosures',
                       'creditor_and_acquisition_relationship_accounting','partial_conversion_and_modification']))
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:300] or type(exc).__name__)
