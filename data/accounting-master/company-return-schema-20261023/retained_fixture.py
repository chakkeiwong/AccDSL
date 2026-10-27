"""Explicit projection of retained P facts; interface labels are authored here."""
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as Q
import json
from return_schema import PROFILE, ROLES, NUMBERS, TAX_NUMBERS, FINDINGS, SETTLE_NUMBERS, canonical, validate

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PACKET=ROOT/'data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json'


def exact(value):
    q=Q(value);return str(q.numerator)+'/'+str(q.denominator)


def from_source(raw):
    # The locked original packet contains build timing floats outside financial records.
    source=json.loads(raw);reg=source['record_registry'];a=source['aliases']
    item=lambda key:reg[a[key]['digest']]['body']
    state=item('opening');component=state['returns'];settlement=item('event.returns');sale=item('event.recovered-sale')
    tax=item('event.tax-h1')['parameters']
    ptr=lambda key,suffix='':'/record_registry/'+a[key]['digest']+'/body'+suffix
    out={'profile':PROFILE,'name':'P retained return module',
        'source':{'packet_sha256':sha256(raw).hexdigest(),'opening_sha256':a['opening']['digest'],'meaning':'retained_synthetic_case'},
        'context':{'entity':'P','book_role':'legal','currency':state['currency'],'case_id':'retained_company_composition'},
        'period':{'start':state['date'],'end_exclusive':'2026-01-01'},
        'accounts':{k:k for k in ROLES},
        'component':{'id':'return_component','source_pointer':ptr('opening','/returns'),
            **{k:exact(component[k]) for k in NUMBERS},'settled':component['settled']},
        'tax':{'method':tax['return_tax_timing'],'rate':exact(tax['rate']),
            'source_pointer':ptr('event.tax-h1','/parameters'),'opening_source_pointer':ptr('opening','/books/P'),
            'refund_tax_base':'0/1','recovery_tax_base':'0/1',
            'opening_dta':exact(state['books']['P']['dta']),'opening_dtl':exact(-Q(state['books']['P']['dtl'])),
            **{k:tax[k] for k in FINDINGS}},'lots':[],
        'events':[{'id':'return_settlement','kind':'settle','method':settlement['method'],
            'date':settlement['date'],'source_pointer':ptr('event.returns'),
            'component_id':'return_component','lot_id':'recovered',
            **{k:exact(settlement['parameters'][k]) for k in SETTLE_NUMBERS},
            **{k:settlement['parameters'][k] for k in ['all_rights_closed','handling_is_selling_cost']}},
            {'id':'recovered_sale','kind':'sell','method':sale['method'],'date':sale['date'],
             'source_pointer':ptr('event.recovered-sale'),'lot_id':'recovered',
             'fraction':exact(sale['parameters']['fraction']),'proceeds':exact(sale['parameters']['proceeds']),
             'performance_complete':sale['parameters']['performance_complete']}]}
    # Zero opening tax bases follow the retained taxable-history premise and its DTA/DTL,
    # not a historical observation or a universal tax rule.
    return validate(out)


def bound_to_retained(body,raw):
    try:
        validate(body);expected=from_source(raw)
        # User-facing module name is metadata. All labels and source pointers in
        # this finite import are prescribed by its documented projection.
        expected['name']=body['name']
        return canonical(body)==canonical(expected)
    except Exception:return False


def fixture():
    raw=PACKET.read_bytes();prior=json.loads(PACKET.with_name('validation-01.json').read_text())
    assert sha256(raw).hexdigest()==prior['packet_sha256'] and prior['failed']==0
    return from_source(raw),raw
