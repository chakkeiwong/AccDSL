from pathlib import Path
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('scope_test_fixtures',H.parent/'acquisition-debt-relationship-20261027/fixtures.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
digest=old.digest
PROFILE='ConditionalDebtorConversionWorksheet/1'
def bind(r):
    p=r['payload'];p['source']['schedule_sha256']=digest(p['schedule'])
    p['evidence_sha256']=digest(p['source']);r['expected_payload_sha256']=digest(p);return r
def scope_pair(role='debtor',changes=None):
    q=old.request(role,changes)
    q['payload']['context'].update(at='2026-10-27T01:00:00Z',cutoff='2026-10-27T03:00:00Z')
    q['payload']['source'].update(at='2026-10-27T01:00:00Z',available_at='2026-10-27T02:00:00Z');old.bind(q)
    # Expected scopes come from independently specified cases, not candidate calls.
    if role=='creditor':
        exp=old.expected(q,'conditional_scope','creditor_method_required',old.CREDITOR+['noncontrolling_investment_relationship_and_method'],['interpretation19_does_not_address_creditor'])
    elif changes=={'original_terms':'yes'}:
        exp=old.expected(q,'conditional_scope','debtor_int19_excluded',old.BASE+['alternative_debtor_method'],['original_terms'])
    elif changes=={'partial_extinguishment':'yes'}:
        exp=old.expected(q,'conditional_scope','debtor_int19_method_required',old.DEBTOR+['consideration_allocation','remaining_liability_modification_assessment'])
    elif changes=={'liability_extinguished':'unknown'}:
        exp=old.expected(q,'conditional_scope','debtor_int19_method_required',old.DEBTOR+['extinguishment_not_established:unknown'])
    else:exp=old.expected(q,'conditional_scope','debtor_int19_method_required',old.DEBTOR)
    return q,exp
def request(E='70/1',reliable='yes',liability='60/1',role='debtor',changes=None):
    q,exp=scope_pair(role,changes)
    s=dict(currency='USD',unit='currency_unit',opening_at='2026-10-27T00:00:00Z',close_at='2026-10-27T02:00:00Z',
      opening=dict(cash='30/1',equipment='100/1',debt='-100/1',opening_capital='-30/1',issued_equity='0/1',settlement_gain='0/1'),
      premises=dict(debt_classification='financial_liability',issued_classification='equity',tax='explicit_zero_current_and_deferred',
                    fees='explicit_none',interest='explicit_none',other_activity='explicit_none',cash_legs='explicit_none'),
      measurement=dict(equity_fv_reliable=reliable,equity_fair_value=E,liability_fair_value=liability))
    src=dict(text='Synthetic complete debtor schedule; no actual measured source.',rationale='Explicit hypothetical valuation and zero-tax/no-cash premises.',
      subject=q['payload']['context']['subject'],actor='researcher',available_at='2026-10-27T02:00:00Z',schedule_sha256=digest(s))
    p=dict(scope_request=q,scope_result_sha256=digest(exp),schedule=s,source=src,evidence_sha256=digest(src))
    return bind(dict(profile=PROFILE,payload=p,expected_payload_sha256=''))

def measured_expected(r,E,gain,basis):
    # The case table supplies both E and gain independently, rather than deriving
    # an expectation by calling the candidate's valuation or journal functions.
    from fractions import Fraction as F
    def n(x):v=F(x);return str(v.numerator)+'/'+str(v.denominator)
    q,sc=scope_pair();p=r['payload']
    closing={**p['schedule']['opening'],'debt':'0/1','issued_equity':n(-F(E)),'settlement_gain':n(-F(gain))}
    rep=dict(balance_sheet=dict(assets=dict(cash='30/1',equipment='100/1'),assets_total='130/1',
             liabilities=dict(financial_debt='0/1'),liabilities_total='0/1',
             equity=dict(opening_contributed='30/1',new_issued_equity=E,current_earnings=gain),equity_total='130/1'),
      income=dict(settlement_result=gain,tax='0/1',profit=gain,other_comprehensive_income='0/1',total_comprehensive_income=gain),
      cash_flow=dict(opening_cash='30/1',operating='0/1',investing='0/1',financing='0/1',net_change='0/1',closing_cash='30/1'),
      equity_reconciliation=dict(opening='30/1',shares_issued=E,profit=gain,oci='0/1',closing='130/1'),
      noncash_exchange=dict(debt_extinguished='100/1',equity_recognised=E,settlement_result=gain))
    return dict(profile=PROFILE,source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,
      request_sha256=digest(r),scope_result=sc,schedule=deepcopy(p['schedule']),source=deepcopy(p['source']),scope_assessment='supplied_assertions_only',
      status='conditional_debtor_worksheet',measurement_basis=basis,measurement=E,opening=deepcopy(p['schedule']['opening']),
      legal_journals=[dict(id='full-debt-equity-exchange',at='2026-10-27T01:00:00Z',entity='S',
        entries=dict(debt='100/1',issued_equity=n(-F(E)),settlement_gain=n(-F(gain))),cash_movement='0/1')],closing=closing,report=rep,
      outstanding=['actual_source_and_period_authority','actual_measurement_and_classification','tax_and_full_disclosures',
                   'creditor_and_acquisition_relationship_accounting','partial_conversion_and_modification'])
def cases():
    rows=[]
    for name,E,gain,reliable,liab,basis in [
      ('gain','70/1','30/1','yes','60/1','equity_fair_value'),
      ('zero','100/1','0/1','yes','60/1','equity_fair_value'),
      ('loss','120/1','-20/1','yes','60/1','equity_fair_value'),
      ('liability_fallback',None,'40/1','no','60/1','liability_fair_value')]:
        r=request(E,reliable,liab);rows.append(dict(id=name,request=r,expected=measured_expected(r,liab if E is None else E,gain,basis)))
    return rows
def unresolved():
    rows=[]
    for field in ['debt_classification','issued_classification','tax','fees','interest','other_activity','cash_legs']:
        r=request();r['payload']['schedule']['premises'][field]='unresolved';bind(r)
        rows.append((field,r,['premise:'+field]))
    rows.append(('missing_equity',request(E=None),['measurement:equity_fair_value']))
    rows.append(('missing_liability',request(E=None,reliable='no',liability=None),['measurement:liability_fair_value']))
    rows.append(('unknown_reliability',request(reliable='unknown'),['equity_fair_value_reliability']))
    rows.append(('creditor',request(role='creditor'),['required_debtor_scope']))
    rows.append(('original_terms',request(changes={'original_terms':'yes'}),['required_debtor_scope']))
    rows.append(('partial',request(changes={'partial_extinguishment':'yes'}),['partial_or_unknown_extent_method']))
    rows.append(('not_extinguished',request(changes={'liability_extinguished':'unknown'}),['whole_liability_extinguishment_required']))
    for name,when,dep in [('late','2026-10-28T00:00:00Z','measurement_source_after_cutoff'),('unknown_source',None,'measurement_source_availability_unknown')]:
        r=request();r['payload']['source']['available_at']=when;bind(r);rows.append((name,r,[dep]))
    return rows
