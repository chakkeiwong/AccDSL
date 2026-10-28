"""Original loss40/30/30/negative10 case over retained reconciliation/lot engine."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('retained_loss_examples',ROOT/'data/accounting-master/conditional-tax-losses-20261024/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
m=ex.m


def reconciliation(year, taxable):
    body=ex.future_request(taxable);info=body['information_request']
    start,end=f'{year}-01-01',f'{year+1}-01-01'
    opening=deepcopy(info['report_request']['opening'])
    opening['date']=start;opening['period']=dict(start=start,end_exclusive=end)
    opening['tax_closed_until']=start
    opening['source']['premise']=f'Independent synthetic {year} opening for tax reconciliation; not financial carry'
    for member in opening['leases']:
        for right in member['component']['rights']:right['last_measurement_date']=start
    info['report_request']=m.tax.information.reports.request(opening,[])
    info['report_request_sha256']=m.book.digest(info['report_request'])
    info['interval']=dict(start=start,end_exclusive=end,activity_through=f'{year}-12-31')
    body['allocations'][0]['id']=f'supplied-taxable-{year}'
    body['allocations'][0]['origin']['reference']=f'Explicit synthetic income{taxable} in {year}; no tax-law or financial carry claim'
    body['information_sha256']=m.book.digest(info)
    return body


def initial(year=2026):
    r=reconciliation(year,'-40/1');info=r['information_request']
    return dict(profile=m.STATE,context=deepcopy(info['report_request']['opening']['context']),
        jurisdiction=info['information']['jurisdiction']['value'],regime=info['information']['regime']['value'],
        cursor=f'{year}-01-01',lots=[],seen=[],history=[],opening_inventory=ex.known(True))


def step(state,year,taxable,uses=(),generation=None,cap='30/1'):
    return m.request(state,reconciliation(year,taxable),f'loss-step-{year}',ex.model(),ex.known(cap),
        [dict(lot_id=ident,amount=amount) for ident,amount in uses],
        dict(id=generation,eligible=ex.known(True),expiry=ex.no_expiry()) if generation else None)


def generate():
    return step(initial(),2026,'-40/1',generation='loss-2026',cap='0/1')


def rehash(body):
    body['state_sha256']=m.book.digest(body['state'])
    body['reconciliation_sha256']=m.book.digest(body['reconciliation_request'])
