"""Source-bound registered-note summaries; no source or contract admission."""
from copy import deepcopy
from datetime import datetime
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import temporal_measurement_constraints_v1 as temporal
PDF='docs/design/cases/apple/annual-2024.pdf'
TEXT='docs/design/cases/apple/annual-2024.txt'
PDF_SHA='ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88'
TEXT_SHA='caaf182340d3846ff54cf967a2d3da7dce82505170665943ea7227e6bed8336e'
PROFILE='RetainedRegisteredNoteSummaries/1'
HEADINGS=['The 0.000% 2025 Notes','The 0.875% 2025 Notes','The 2026 Notes','The 2027 Notes','The 1.375% 2029 Notes','The 3.050% 2029 Notes','The 2031 Notes','The 2042 Notes']
QUALIFICATIONS=[('qualification','The following description of the Notes is a summary','The Notes'),('additional_issuance','Each of the Notes were issued','The 0.000% 2025 Notes'),('ranking','Ranking','Payment on the Notes'),('payment_currency_calendar','Payment on the Notes','Payment of Additional Amounts'),('additional_amounts','Payment of Additional Amounts','Redemption for Tax Reasons'),('tax_redemption','Redemption for Tax Reasons','Optional Redemption'),('optional_redemption','Optional Redemption','Covenants'),('covenants','Covenants','Events of Default'),('default','Events of Default','Modification and Waivers'),('amendment','Modification and Waivers','Discharge, Defeasance and Covenant Defeasance'),('defeasance','Discharge, Defeasance and Covenant Defeasance','Book-Entry and Settlement'),('settlement','Book-Entry and Settlement','Exhibit 10.19')]

def need(ok,reason):
    if not ok:raise ValueError(reason)
def fmt(v):
    v=Q(v);return f'{v.numerator}/{v.denominator}'
def norm(s):return ' '.join(s.split())
def date(s):return datetime.strptime(s,'%B %d, %Y').date().isoformat()
def digest(v):return temporal.core.digest(v)
def span(source,start,end):
    return dict(extraction=TEXT,extraction_sha256=TEXT_SHA,start=start,end_exclusive=end,quote=source[start:end],quote_sha256=sha256(source[start:end].encode()).hexdigest(),physical_page=source[:start].count(chr(12))+1)
def match(pattern,s):
    m=re.search(pattern,s);need(m is not None,'source_pattern:'+pattern[:60]);return m

def value_type(currency,rate=False):
    return dict(kind='rational',context=dict(issuer_cik='0000320193',perimeter='Apple_Inc_legal_issuer_summary',basis='Exhibit4.1_as_reported',value_layer='reported_contract_summary'),dimensions={'time:year':-1} if rate else {'currency:'+currency:1},scale='1/1')

def observation(amount,currency,when,quantity,ref,rate=False):
    typ=dict(value_type=value_type(currency,rate),time=dict(kind='instant',at=when),quantity=quantity)
    temporal.measurement_type(typ)
    amount=fmt(amount)
    return dict(type=typ,interval=dict(lower=amount,upper=amount,lower_inclusive=True,upper_inclusive=True),interval_premise=dict(id='reported.'+quantity,status='proposed',meaning='Literal stated quantity only; source-summary reading is not independent admission'),source_ref=ref)

def construct(root=ROOT):
    pdf=(root/PDF).read_bytes();raw=(root/TEXT).read_bytes()
    need(sha256(pdf).hexdigest()==PDF_SHA,'pdf_identity');need(sha256(raw).hexdigest()==TEXT_SHA,'extraction_identity')
    source=raw.decode();start=source.index('DESCRIPTION OF DEBT SECURITIES');stop=source.index('Exhibit 10.19',start)
    rows=[]
    for n,heading in enumerate(HEADINGS):
        a=source.index(heading,start);a=source.index('We issued',a)
        b=source.index('was outstanding.',a)+len('was outstanding.')
        need(b<stop,'series_bounds');literal=source[a:b];s=norm(literal)
        issue=match(r'^We issued ([€£])([0-9,]+) aggregate principal amount of (.+?) on ([A-Za-z]+ [0-9]+, [0-9]{4})\.',s)
        maturity=match(r'The maturity date of .+? is ([A-Za-z]+ [0-9]+, [0-9]{4}),? and',s)
        interest=match(r'interest at a rate of ([0-9.]+)% per annum is paid (annually|semi-annually) on (.+?) of each year, beginning on ([A-Za-z]+ [0-9]+, [0-9]{4}), and on the maturity date\.',s)
        outstanding=match(r'As of ([A-Za-z]+ [0-9]+, [0-9]{4}), ([€£])([0-9,]+) aggregate principal amount of .+? was outstanding\.',s)
        currency={'€':'EUR','£':'GBP'}[issue[1]];need(issue[1]==outstanding[2],'currency_consistency')
        ident='exhibit4.1.series.'+str(n+1);when=date(outstanding[1]);ref='sha256:'+TEXT_SHA+':'+str(a)+'-'+str(b)
        issued=fmt(issue[2].replace(',',''));held=fmt(outstanding[3].replace(',',''));rate=fmt(Q(interest[1])/100)
        row=dict(id=ident,source_heading=heading,identity_kind='provisional_source_series_label',isin=None,issuer='Apple Inc.',issuer_scope='solely Apple Inc., not subsidiaries; subject to stated context',source_span=span(source,a,b),currency=currency,issue_date=date(issue[4]),issued_principal=issued,observation_date=when,outstanding_principal=held,annual_rate=rate,maturity_label=date(maturity[1]),payment_frequency=interest[2],payment_month_days=interest[3].split(' and '),first_payment_label=date(interest[4]),effective_settlement_dates=None,reported_carrying_amount=None,as_of_2024_09_28_outstanding=None,governing_instrument_instance=None,source_admission=False,accounting_admission=False)
        row['native_observations']={
            'issued_principal':observation(issued,currency,row['issue_date'],ident+'.issued_principal',ref),
            'outstanding_principal':observation(held,currency,when,ident+'.outstanding_principal',ref),
            'annual_rate':observation(rate,currency,when,ident+'.annual_rate',ref,rate=True)}
        annualized=temporal.joint.types.product_type(row['native_observations']['outstanding_principal']['type']['value_type'],row['native_observations']['annual_rate']['type']['value_type'])
        year_type={**value_type(currency),'dimensions':{'time:year':1}}
        row['conditional_nominal_annual_coupon']=dict(amount=fmt(Q(held)*Q(rate)),currency=currency,assumption='Unchanged face for one full nominal year with stated rate; no date adjustment, accrual basis, tax, default, redemption or realized payment assertion',supplied_year_fraction='1/1',annualized_product_type=annualized,native_amount_type=temporal.joint.types.product_type(annualized,year_type))
        rows.append(row)
    quals=[]
    for ident,left,right in QUALIFICATIONS:
        a=source.index(left,start);b=source.index(right,a+len(left));quals.append(dict(id=ident,source_span=span(source,a,b)))
    return dict(profile=PROFILE,status='source_bound_summary_only',source=dict(pdf=PDF,pdf_sha256=PDF_SHA,extraction=TEXT,extraction_sha256=TEXT_SHA),rows=rows,qualification_spans=quals,population=dict(kind='eight_debt_series_in_registered_securities_summary',series_count=8,complete_company_term_debt=False,legal_instrument_ids_complete=False),source_admission=False,accounting_admission=False,historical_information='unresolved exact-byte availability/actor access',as_of_note9_link=None,executable_opening=None,policy_input=None,probability_model=None,unresolved=['Governing2013/2018 indentures and applicable supplemental/series terms','Complete debt and amendment/cancellation population','September28 instrument holdings versus October18 observation','Per-instrument USD conversion, carrying adjustments and hedge links','Business-day adjustment rules and historical calendars','Actor access and exact historical byte availability','Accounting recognition and measurement eligibility'])

def validate(card,root=ROOT):
    expected=construct(root)
    need(card==expected,'source_semantic_binding')
    return True

def pair_relation(a,b):
    return dict(profile=temporal.PROFILE,observations=dict(a=deepcopy(a),b=deepcopy(b)),relations=[dict(id='caller_proposed_equality',kind='same_time',terms=[dict(observation='a',coefficient='1/1'),dict(observation='b',coefficient='-1/1')],rhs='0/1',identity_premise=dict(id='diagnostic.only',status='proposed',meaning='Adverse-control attempt to equate two source quantities; never an admitted issuer relation'))])
