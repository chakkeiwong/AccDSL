"""Explicit fiscal policy and independent retained-schedule expectations."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import insurance_fiscal_book_v1 as fiscal
spec=importlib.util.spec_from_file_location('fiscal_base_examples',ROOT/'data/accounting-master/insurance-loss-book-20261025/examples.py')
base_ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(base_ex)


def fixture(chart='named',case='loss-service-finance',complement=True):
    q=base_ex.fixture(chart,case,complement);r=fiscal.base.propose(q)
    assert r['status']=='proposed_provisional',r
    retained=next(a for a,v in q['opening']['accounts'].items() if v['classification']=='equity')
    return {'profile':fiscal.PROFILE,'base_request':q,'base_result':r,'base_result_sha256':fiscal.core.digest(r),
        'fiscal_policy':{'kind':'calendar_years_2025_2027','event_completeness':'unknown',
            'premise':'Explicit hypothetical calendar-year observations for the retained dates; unobserved business is not inferred absent.'},
        'retained_account':retained,'memory_policies':{p:{'kind':'preserve',
            'provenance':'Explicit carry of continuing insurance state and unrelated memory'} for p in q['opening']['memory_types']}}


def checked_case(chart='named',case='loss-service-finance',complement=True):
    q=fixture(chart,case,complement);original=deepcopy(q);r=fiscal.propose(q)
    assert r['status']=='proposed_provisional',r
    assert q==original and all(r[k] is False for k in fiscal.FLAGS)
    carries=[e['result'] for e in r['execution']['trace'] if e['command']['kind']=='carry']
    reports=[e['result'] for e in r['execution']['trace'] if e['command']['kind']=='report']
    assert [x['report']['income']['profit'] for x in carries]==['0/1','-5/1','10/1']
    assert [x['income']['profit'] for x in reports]==['-5/1','10/1']
    assert [x['report']['cash_flows']['activities']['operating']['payments'] for x in carries]==['0/1','50/1','45/1']
    assert [x['report']['cash_flows']['closing_cash'] for x in carries]==['200/1','150/1','105/1']
    assert [x['report']['balance_sheet']['total_liabilities'] for x in carries]==['100/1','55/1','0/1']
    extra=17 if complement else 0
    assert [x['report']['equity']['closing'] for x in carries]==[fiscal.base.fmt(n+extra) for n in [100,95,105]]
    assert r['next_opening_report']['income']['profit']=='0/1'
    assert r['next_opening_report']['cash_flows']['closing_cash']=='105/1'
    assert len(r['execution']['trace'])==11 and len(r['transformations'])==3
    assert r['loss_origins']==q['base_result']['native_result']['report']['loss_origins']
    assert r['execution']['current']['memory']==q['base_result']['execution']['current']['memory']
    return {'request':q,'result':r,'expected':{'annual_profit':['0/1','-5/1','10/1'],
        'annual_payments':['0/1','50/1','45/1'],'closing_cash':['200/1','150/1','105/1'],
        'liabilities':['100/1','55/1','0/1'],'complement':complement,'native_dates_preserved':True}}


if __name__=='__main__':
    row=checked_case();print(json.dumps({'status':row['result']['status'],'expected':row['expected']}))
