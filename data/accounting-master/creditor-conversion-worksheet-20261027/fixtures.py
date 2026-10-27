from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import importlib.util
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('debtor_independent_fixtures',H.parent/'debtor-conversion-worksheet-20261027/fixtures.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
digest=base.digest;PROFILE='ConditionalCreditorConversionWorksheet/1'
def n(x):v=F(x);return str(v.numerator)+'/'+str(v.denominator)
def bind(r):
    p=r['payload'];p['source']['schedule_sha256']=digest(p['schedule']);p['evidence_sha256']=digest(p['source']);r['expected_payload_sha256']=digest(p);return r
def request(allowance='30/1',shares='70/1'):
    q,sc=base.scope_pair('creditor')
    s=dict(currency='USD',unit='currency_unit',opening_at='2026-10-27T00:00:00Z',assessment_at='2026-10-27T00:30:00Z',close_at='2026-10-27T02:00:00Z',
      opening=dict(cash='30/1',gross_loan='100/1',allowance='0/1',shares='0/1',capital='-130/1',impairment_expense='0/1',disposal_expense='0/1'),
      premises=dict(loan_classification='amortised_cost',business_model='hold_to_collect',cash_flow_condition='sppi',direct_rights_expiry='yes',whole_asset='yes',
        new_share_classification='aasb9_fvtpl_no_oci_election',significant_influence='no',joint_control='no',hedging='explicit_none',prior_oci='explicit_none',
        tax='explicit_zero_current_and_deferred',fees='explicit_none',interest='explicit_none',other_activity='explicit_none',cash_legs='explicit_none'),
      measurement=dict(assessed_allowance=allowance,share_fair_value=shares,initial_transaction_price=shares,closing_share_fair_value=shares))
    src=dict(text='Synthetic creditor measurement and relationship assertions.',rationale='No control,influence,joint control or separate relationship; separately assessed allowance and share value are supplied,not inferred.',
             subject='P',actor='researcher',available_at='2026-10-27T02:00:00Z',schedule_sha256=digest(s))
    p=dict(scope_request=q,scope_result_sha256=digest(sc),schedule=s,source=src,evidence_sha256=digest(src))
    return bind(dict(profile=PROFILE,payload=p,expected_payload_sha256=''))
def prefix(r,sc=None):
    if sc is None:_,sc=base.scope_pair('creditor')
    p=r['payload'];return dict(profile=PROFILE,source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,
      request_sha256=digest(r),scope_result=deepcopy(sc),schedule=deepcopy(p['schedule']),source=deepcopy(p['source']),scope_assessment='supplied_assertions_only')
def expected(r,A,E,disposal,profit,total):
    # Components are predeclared in the case table, including total and disposal.
    op=deepcopy(r['payload']['schedule']['opening']);assessed={**op,'allowance':n(-F(A)),'impairment_expense':A}
    close={**assessed,'gross_loan':'0/1','allowance':'0/1','shares':E,'disposal_expense':n(-F(disposal))}
    rep=dict(balance_sheet=dict(assets=dict(cash='30/1',gross_loan='0/1',loss_allowance='0/1',shares=E),assets_total=total,
      liabilities_total='0/1',equity=dict(contributed='130/1',current_earnings=profit),equity_total=total),
      income=dict(impairment_result=n(-F(A)),disposal_result=disposal,tax='0/1',profit=profit,other_comprehensive_income='0/1',total_comprehensive_income=profit),
      cash_flow=dict(opening_cash='30/1',operating='0/1',investing='0/1',financing='0/1',net_change='0/1',closing_cash='30/1'),
      equity_reconciliation=dict(opening='130/1',owner_transactions='0/1',profit=profit,oci='0/1',closing=total),
      noncash_exchange=dict(gross_loan_removed='100/1',allowance_removed=A,net_carrying_removed=n(100-F(A)),shares_received=E,disposal_result=disposal))
    journals=[dict(id='pre-exchange-impairment',at='2026-10-27T00:30:00Z',entity='P',entries=dict(impairment_expense=A,allowance=n(-F(A))),cash_movement='0/1'),
       dict(id='loan-rights-expiry-share-recognition',at='2026-10-27T01:00:00Z',entity='P',entries=dict(shares=E,allowance=A,disposal_expense=n(-F(disposal)),gross_loan='-100/1'),cash_movement='0/1')]
    return dict(**prefix(r),status='conditional_creditor_worksheet',opening=op,assessed=assessed,legal_journals=journals,closing=close,report=rep,
       outstanding=['actual_source_and_period_authority','actual_classification_and_expected_losses','actual_fair_value_and_tax',
                    'control_acquisition_and_preexisting_relationship','partial_exchange_and_measurement_differences'])
def cases():
    rows=[]
    for name,A,E,D,P,T in [('allowance_then_exchange','30/1','70/1','0/1','-30/1','100/1'),
      ('zero_allowance_loss','0/1','70/1','-30/1','-30/1','100/1'),('zero','0/1','100/1','0/1','0/1','130/1'),
      ('gain','0/1','120/1','20/1','20/1','150/1'),('additional_loss','30/1','60/1','-10/1','-40/1','90/1')]:
        r=request(A,E);rows.append(dict(id=name,request=r,expected=expected(r,A,E,D,P,T)))
    return rows
def unresolved():
    rows=[]
    def add(name,r,deps,sc=None):
        bind(r);ex=dict(**prefix(r,sc),status='method_required',dependencies=sorted(deps),request=deepcopy(r),report=None)
        rows.append(dict(id=name,request=r,expected=ex))
    for field in request()['payload']['schedule']['premises']:
        r=request();r['payload']['schedule']['premises'][field]='unresolved';add(field,r,['premise:'+field])
    for field in request()['payload']['schedule']['measurement']:
        r=request();r['payload']['schedule']['measurement'][field]=None;add(field,r,['measurement:'+field])
    for field in ['significant_influence','joint_control']:
        r=request();r['payload']['schedule']['premises'][field]='yes';add('positive_'+field,r,['premise:'+field])
    for field,dep in [('initial_transaction_price','initial_measurement_difference_method'),('closing_share_fair_value','subsequent_measurement_method')]:
        r=request();r['payload']['schedule']['measurement'][field]='80/1';add(field+'_different',r,[dep])
    for name,date,dep in [('late','2026-10-28T00:00:00Z','measurement_source_after_cutoff'),('unknown_availability',None,'measurement_source_availability_unknown')]:
        r=request();r['payload']['source']['available_at']=date;add(name,r,[dep])
    for key,deps,scdeps in [
      ('creditor_gains_control',['control_or_acquisition_method'],base.old.CREDITOR+['acquisition_scope_and_measurements','separate_books_method']),
      ('partial_extinguishment',['partial_exchange_method'],base.old.CREDITOR+['noncontrolling_investment_relationship_and_method']),
      ('settles_preexisting_relationship',['separate_relationship_method'],base.old.CREDITOR+['noncontrolling_investment_relationship_and_method','separate_relationship_transaction_and_settlement'])]:
        r=request();q=r['payload']['scope_request'];q['payload']['assertions'][key]='yes';base.old.bind(q)
        sc=base.old.expected(q,'conditional_scope','creditor_method_required',scdeps,['interpretation19_does_not_address_creditor'])
        r['payload']['scope_result_sha256']=digest(sc);add(key,r,deps,sc)
    return rows
