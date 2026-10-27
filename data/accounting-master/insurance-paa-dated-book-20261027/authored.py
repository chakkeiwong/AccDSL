"""Independent dated requests and full financial expectations for the old PAA case."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json

def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()

def fmt(value):
    value = Q(value); return f'{value.numerator}/{value.denominator}'

CLASSES = {'cash':'asset', 'held_coverage':'asset', 'held_claims':'asset',
           'issued_coverage':'liability', 'issued_claims':'liability', 'capital':'equity',
           'issued_revenue':'income', 'held_recovery_income':'income',
           'issued_claims_expense':'expense', 'held_coverage_expense':'expense', 'equipment':'asset'}
CASES = {'base': ('1/1','0/1','21/1','119/1','47/1','27/1','6/1'),
         'separate_transferred_risk': ('3/2','0/1','43/2','239/2','95/2','55/2','13/2'),
         'nonperformance_loss': ('1/1','2/1','19/1','117/1','45/1','25/1','4/1')}
FINDINGS = ['one_year_each_issued_contract','one_year_each_held_contract','boundaries_complete',
    'uniform_service_and_risk_release','no_acquisition_cashflows','no_investment_components',
    'no_significant_financing','remaining_coverage_not_onerous','claims_settle_within_one_year',
    'held_recognition_conditions','separate_transferred_risk_supported','nonperformance_supported',
    'operating_cash_classification_supplied']
NOTES = [{'id':'scope','label':'Conditional PAA interim example','status':'unresolved',
          'reason':'Synthetic group/calendar/measurement facts; actual source, accounting and full note acceptance remain unresolved.'}]

def fixture(case='base', chart='named', complement=False):
    transferred, nonperformance, *_ = CASES[case]
    coverage = {'start':'2024-01-01','end_exclusive':'2025-01-01'}
    payload = dict(case_id=case, chart=chart, complement=complement, entity='I', currency='XCU',
        calendar=dict(coverage=coverage, recognition='2024-01-01', cutoff='2024-07-02',
            interpretation='Synthetic elapsed-day service boundary; July2 is 183 of 366 days',
            event_order='premiums, gross service, held service, claims measurement, claims paid, recovery measurement, recovery paid'),
        groups=dict(issued=dict(id='PAA.ISSUED.2024', owner='I', role='issued', annual_cohort='2024',
            coverage=deepcopy(coverage), recognition='2024-01-01'),
            held=dict(id='PAA.HELD.2024', owner='I', role='held', annual_cohort='2024',
            coverage=deepcopy(coverage), recognition='2024-01-01',underlying_group='PAA.ISSUED.2024')),
        amounts=dict(opening_cash='20/1',premium='120/1',held_premium='24/1',incurred_claims='40/1',
            paid_claims='30/1',issued_risk='2/1',quota='1/2',paid_recovery='15/1',
            transferred_risk=transferred,nonperformance=nonperformance),
        findings={name:True for name in FINDINGS},
        cash_policy={'activity':'operating','premise':'Supplied classification for this synthetic insurance example; no accounting admission'},
        source_edition='AASB17-compiled-Dec2022:F2023C00382', assumption_scope='synthetic conditional example')
    return dict(profile='InsurancePAADatedBook/1', payload=payload, payload_sha256=digest(payload))

def bind(body):
    body['payload_sha256'] = digest(body['payload']); return body

def expected(case='base', chart='named', complement=False):
    """Explicit journals and endpoint targets; never import the candidate."""
    _, _, recovery, assets, equity, profit, held_claims = CASES[case]
    roles = {key:('paa.'+key if chart=='named' else 'A'+str(100+i)) for i,key in enumerate(CLASSES)}
    extra = Q(17) if complement else Q(0)
    opening = {roles[key]:'0/1' for key in CLASSES}
    opening.update({roles['cash']:'20/1',roles['capital']:fmt(-20-extra),roles['equipment']:fmt(extra)})
    journals = [
        ('premium_received','2024-01-01',{'cash':'120/1','issued_coverage':'-120/1'},'120/1','PAA.ISSUED.2024'),
        ('held_premium_paid','2024-01-01',{'held_coverage':'24/1','cash':'-24/1'},'-24/1','PAA.HELD.2024'),
        ('issued_service','2024-07-02',{'issued_coverage':'60/1','issued_revenue':'-60/1'},None,'PAA.ISSUED.2024'),
        ('held_service','2024-07-02',{'held_coverage_expense':'12/1','held_coverage':'-12/1'},None,'PAA.HELD.2024'),
        ('incurred_claims','2024-07-02',{'issued_claims_expense':'42/1','issued_claims':'-42/1'},None,'PAA.ISSUED.2024'),
        ('claims_paid','2024-07-02',{'issued_claims':'30/1','cash':'-30/1'},'-30/1','PAA.ISSUED.2024'),
        ('recovery_measured','2024-07-02',{'held_claims':recovery,'held_recovery_income':fmt(-Q(recovery))},None,'PAA.HELD.2024'),
        ('recovery_received','2024-07-02',{'cash':'15/1','held_claims':'-15/1'},'15/1','PAA.HELD.2024')]
    balances = deepcopy(opening); stages=[]; flows=[]
    for index,(identity,at,postings,cash,group) in enumerate(journals):
        mapped={roles[k]:v for k,v in postings.items()}
        for account,value in mapped.items(): balances[account]=fmt(Q(balances[account])+Q(value))
        if cash is not None: flows.append(dict(event_id='paa.'+identity,date=at,amount=cash,activity='operating',origin=group+'/'+identity))
        stages.append(dict(id='paa.'+identity,date=at,group=group,postings=mapped,balances=deepcopy(balances),step=fmt(index+1)))
    closing={roles[key]:value for key,value in dict(cash='101/1',held_coverage='12/1',held_claims=held_claims,
        issued_coverage='-60/1',issued_claims='-12/1',capital=fmt(-20-extra),issued_revenue='-60/1',
        held_recovery_income=fmt(-Q(recovery)),issued_claims_expense='42/1',held_coverage_expense='12/1',equipment=fmt(extra)).items()}
    assert balances==closing
    lines={kind:[] for kind in ['asset','liability','equity','income','expense']}
    for key,kind in CLASSES.items():
        sign=-1 if kind in ['liability','equity','income'] else 1
        lines[kind].append(dict(id=key,label=key,classification=kind,accounts=[roles[key]],
            opening=fmt(sign*Q(opening[roles[key]])),closing=fmt(sign*Q(closing[roles[key]]))))
    financial=dict(statement_lines=lines,opening_totals=dict(asset=fmt(20+extra),liability='0/1',equity=fmt(20+extra),income='0/1',expense='0/1'),
        closing_totals=dict(asset=fmt(Q(assets)+extra),liability='72/1',equity=fmt(20+extra),income=fmt(60+Q(recovery)),expense='54/1'),
        balance_sheet=dict(total_assets=fmt(Q(assets)+extra),total_liabilities='72/1',equity_including_profit=fmt(Q(equity)+extra)),
        income=dict(income=fmt(60+Q(recovery)),expenses='54/1',profit=profit),
        equity=dict(opening=fmt(20+extra),direct_movements='0/1',profit=profit,closing=fmt(Q(equity)+extra),
            by_account={roles['capital']:'0/1'},movements=[]),
        reconciliations=dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
    return dict(roles=roles,opening=opening,closing=closing,stages=stages,flows=flows,financial=financial,
        cash=dict(opening_cash='20/1',closing_cash='101/1',net_movement='81/1',activities={
            'operating':dict(receipts='135/1',payments='54/1',net='81/1'),
            'investing':dict(receipts='0/1',payments='0/1',net='0/1'),
            'financing':dict(receipts='0/1',payments='0/1',net='0/1')}))
