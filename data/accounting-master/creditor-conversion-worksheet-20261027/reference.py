from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('debtor_numeric_helpers',H.parent/'debtor-conversion-worksheet-20261027/reference.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
scope=helpers.scope;need=scope.need;fields=scope.fields;digest=scope.digest;moment=scope.moment
num=helpers.number;serial=helpers.serial;FLAGS=scope.FLAGS
PROFILE='ConditionalCreditorConversionWorksheet/1'
ACCOUNTS=['cash','gross_loan','allowance','shares','capital','impairment_expense','disposal_expense']
PREMISES=dict(loan_classification='amortised_cost',business_model='hold_to_collect',cash_flow_condition='sppi',
 direct_rights_expiry='yes',whole_asset='yes',new_share_classification='aasb9_fvtpl_no_oci_election',
 significant_influence='no',joint_control='no',hedging='explicit_none',prior_oci='explicit_none',
 tax='explicit_zero_current_and_deferred',fees='explicit_none',interest='explicit_none',other_activity='explicit_none',cash_legs='explicit_none')
def report(request):
    try:
        need(len(json.dumps(request,allow_nan=False))<160000,'request_size')
        fields(request,['profile','payload','expected_payload_sha256'],'envelope');need(request['profile']==PROFILE,'profile')
        p=request['payload'];need(digest(p)==request['expected_payload_sha256'],'payload_binding')
        fields(p,['scope_request','scope_result_sha256','schedule','source','evidence_sha256'],'payload')
        sc=scope.derive(p['scope_request']);need(sc['status']!='invalid','invalid_scope');need(digest(sc)==p['scope_result_sha256'],'scope_result_binding')
        s=p['schedule'];fields(s,['currency','unit','opening_at','assessment_at','close_at','opening','premises','measurement'],'schedule')
        need(s['currency']=='USD' and s['unit']=='currency_unit','units');c=sc['context']
        need(moment(s['opening_at'])<moment(s['assessment_at'])<moment(c['at'])<moment(s['close_at'])<=moment(c['cutoff']),'schedule_dates')
        src=p['source'];fields(src,['text','rationale','subject','actor','available_at','schedule_sha256'],'source')
        scope.text(src['text'],'source_text');scope.text(src['rationale'],'source_rationale')
        need(src['subject']==c['subject'] and src['actor']==c['actor'],'source_context')
        need(src['schedule_sha256']==digest(s),'schedule_source_binding');need(p['evidence_sha256']==digest(src),'evidence_binding')
        fields(s['opening'],ACCOUNTS,'opening');op={k:num(v) for k,v in s['opening'].items()}
        need(op==dict(cash=F(30),gross_loan=F(100),allowance=F(0),shares=F(0),capital=F(-130),impairment_expense=F(0),disposal_expense=F(0)),'selected_opening')
        prem=s['premises'];fields(prem,PREMISES,'premises');deps=[]
        for k,value in PREMISES.items():
            allowed=[value,'unresolved']+(['yes'] if k in ['significant_influence','joint_control'] else [])
            need(prem[k] in allowed,'premise_'+k)
            if prem[k]!=value:deps.append('premise:'+k)
        m=s['measurement'];fields(m,['assessed_allowance','share_fair_value','initial_transaction_price','closing_share_fair_value'],'measurement')
        for k in m:
            if m[k] is None:deps.append('measurement:'+k)
            else:need(num(m[k])>=0,'nonnegative_'+k)
        if m['assessed_allowance'] is not None:need(num(m['assessed_allowance'])<=100,'allowance_exceeds_gross')
        if m['share_fair_value'] is not None and m['initial_transaction_price'] is not None:
            if num(m['share_fair_value'])!=num(m['initial_transaction_price']):deps.append('initial_measurement_difference_method')
        if m['share_fair_value'] is not None and m['closing_share_fair_value'] is not None:
            if num(m['share_fair_value'])!=num(m['closing_share_fair_value']):deps.append('subsequent_measurement_method')
        if src['available_at'] is None:deps.append('measurement_source_availability_unknown')
        elif moment(src['available_at'])>moment(c['cutoff']):deps.append('measurement_source_after_cutoff')
        if sc['status']!='conditional_scope' or sc['route']!='creditor_method_required':deps.append('required_creditor_scope')
        if sc['assertions']['creditor_gains_control']!='no':deps.append('control_or_acquisition_method')
        if sc['assertions']['partial_extinguishment']!='no':deps.append('partial_exchange_method')
        if sc['assertions']['settles_preexisting_relationship']!='no':deps.append('separate_relationship_method')
        out=dict(profile=PROFILE,**FLAGS,request_sha256=digest(request),scope_result=deepcopy(sc),schedule=deepcopy(s),source=deepcopy(src),scope_assessment='supplied_assertions_only')
        if deps:return dict(out,status='method_required',dependencies=sorted(set(deps)),request=deepcopy(request),report=None)
        A=num(m['assessed_allowance']);E=num(m['share_fair_value']);D=F(100)-A-E
        journals=[dict(id='pre-exchange-impairment',at=s['assessment_at'],entity=c['subject'],entries=dict(impairment_expense=A,allowance=-A),cash_movement=F(0)),
                  dict(id='loan-rights-expiry-share-recognition',at=c['at'],entity=c['subject'],entries=dict(shares=E,allowance=A,disposal_expense=D,gross_loan=F(-100)),cash_movement=F(0))]
        close=deepcopy(op);assessed=None
        for i,j in enumerate(journals):
            need(sum(j['entries'].values())==0,'journal_balance')
            for k,v in j['entries'].items():close[k]+=v
            if i==0:assessed=deepcopy(close)
        need(sum(close.values())==0,'trial_balance')
        profit=-A-D;assets=F(30)+E;equity=F(130)+profit;need(assets==equity,'balance_sheet')
        rep=dict(balance_sheet=dict(assets=dict(cash=F(30),gross_loan=F(0),loss_allowance=F(0),shares=E),assets_total=assets,
            liabilities_total=F(0),equity=dict(contributed=F(130),current_earnings=profit),equity_total=equity),
          income=dict(impairment_result=-A,disposal_result=-D,tax=F(0),profit=profit,other_comprehensive_income=F(0),total_comprehensive_income=profit),
          cash_flow=dict(opening_cash=F(30),operating=F(0),investing=F(0),financing=F(0),net_change=F(0),closing_cash=F(30)),
          equity_reconciliation=dict(opening=F(130),owner_transactions=F(0),profit=profit,oci=F(0),closing=equity),
          noncash_exchange=dict(gross_loan_removed=F(100),allowance_removed=A,net_carrying_removed=F(100)-A,shares_received=E,disposal_result=-D))
        return serial(dict(out,status='conditional_creditor_worksheet',opening=op,assessed=assessed,legal_journals=journals,closing=close,report=rep,
          outstanding=['actual_source_and_period_authority','actual_classification_and_expected_losses','actual_fair_value_and_tax',
                       'control_acquisition_and_preexisting_relationship','partial_exchange_and_measurement_differences']))
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:300] or type(exc).__name__)
