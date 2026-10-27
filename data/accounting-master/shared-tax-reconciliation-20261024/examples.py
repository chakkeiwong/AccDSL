"""Explicit hypothetical reconciliation controls; never real tax assessments."""
from copy import deepcopy
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import shared_tax_reconciliation_v1 as m

def information_control():
    rows=json.loads((ROOT/'data/accounting-master/shared-tax-readiness-20261024/cases.json').read_text())
    return deepcopy(next(r['request'] for r in rows if r['case']=='hypothetical_information_supplied'))

def control(extra=None):
    info=information_control()
    info['information']['rate']['value']='1/4'
    info['information']['income/revenue/current_adjustment']['value']='-24/1'
    model={'profile':m.MODEL,'selected':{'status':'known','value':True,
        'provenance':{'kind':'assumption','reference':'Hypothetical uniform-rate/no-credit arithmetic test'}}}
    items=[{'id':'retained-return','account':'revenue','amount':'-24/1',
        'origin':{'kind':'native_return','event_id':'return_settlement'}}]
    if extra is not None:
        amount=m.numeric(extra)
        info['information']['income/other_gains/current_adjustment']['value']=m.book.fmt(amount)
        items.append({'id':'explicit-extra','account':'other_gains','amount':extra,
            'origin':{'kind':'assumption','reference':'Synthetic additional adjustment for arithmetic test only; no legal treatment inferred'}})
    return m.request(info,model,items)

def rehash(body):
    body['information_sha256']=m.book.digest(body['information_request']);return body

def cases():
    rows=[]
    def add(name,body,status):rows.append({'case':name,'request':deepcopy(body),'expected_status':status})
    base=control();positive=control('40/1')
    add('mixed_negative_expression',base,'loss_route_required')
    add('hypothetical_positive_expression',positive,'conditional_gross_current_tax')
    add('hypothetical_zero_expression',control('19/1'),'conditional_gross_current_tax')
    x=deepcopy(positive);x['allocations']=x['allocations'][1:];add('native_adjustment_missing',x,'invalid')
    x=deepcopy(positive);item=deepcopy(x['allocations'][0]);item['id']='different-id';x['allocations'].append(item)
    add('native_adjustment_duplicated',x,'invalid')
    x=deepcopy(positive);x['allocations'][0]['amount']='-23/1';add('native_amount_changed',x,'invalid')
    x=deepcopy(positive);x['allocations'][0]['origin']['event_id']='invented';add('native_event_invented',x,'invalid')
    x=deepcopy(positive);x['allocations'][1]['amount']='39/1';add('account_sum_mismatch',x,'invalid')
    x=deepcopy(positive);x['allocations'][1]['id']=x['allocations'][0]['id'];add('allocation_id_duplicate',x,'invalid')
    x=deepcopy(positive);x['allocations'][1]['account']='cash';add('nonincome_allocation',x,'invalid')
    x=deepcopy(positive);x['information_request']['information']['basis/rou/opening']['value']='1/1'
    add('opening_asset_basis_mismatch',rehash(x),'invalid')
    x=deepcopy(positive);x['information_request']['information']['lease/lease1/B/closing_liability_tax_base']['value']='1/1'
    add('terminated_right_basis_mismatch',rehash(x),'invalid')
    x=deepcopy(positive)
    for when in ['opening','closing']:
        for side,account in [('asset','rou'),('liability','lease_liability')]:
            for right,amount in [('A','1/3'),('B','2/3')]:
                x['information_request']['information']['lease/lease1/'+right+'/'+when+'_'+side+'_tax_base']['value']=amount
            x['information_request']['information']['basis/'+account+'/'+when]['value']='1/1'
    add('exact_fraction_basis_reconciliation',rehash(x),'conditional_gross_current_tax')
    x=deepcopy(positive);x['model']['selected']['value']=False;add('model_false',x,'unsupported')
    x=deepcopy(positive);x['model']['selected']={'status':'unknown','reason':'No model selected'};add('model_unknown',x,'unresolved')
    x=deepcopy(positive);x['model']['selected']['value']=1;add('integer_model_finding',x,'invalid')
    x=deepcopy(positive);x['model']['profile']='unknown';add('unknown_model',x,'invalid')
    x=deepcopy(positive);x['information_sha256']='0'*64;add('forged_information_digest',x,'invalid')
    x=deepcopy(positive);del x['information_request']['information']['loss_route'];add('missing_information',rehash(x),'unresolved')
    x=deepcopy(positive);x['information_request']['information']['interval_coverage']['value']=False
    add('false_information_finding',rehash(x),'unsupported')
    saved=json.loads((ROOT/'data/accounting-master/shared-tax-readiness-20261024/cases.json').read_text())
    x=deepcopy(positive);x['information_request']=deepcopy(next(r['request'] for r in saved if r['case']=='stopped_prefix_with_all_declarations'))
    add('stopped_native_prefix',rehash(x),'unresolved')
    x=deepcopy(positive);x['allocations'][1]['origin']['kind']='source_reference';add('additional_origin_not_assumption',x,'invalid')
    x=deepcopy(base);x['information_request']['information']['loss_route']['value']='caller says pay refund now'
    add('loss_text_cannot_enable_refund',rehash(x),'loss_route_required')
    x=deepcopy(positive);x['information_request']['information']['rate']['value']='0/1'
    add('explicit_zero_rate',rehash(x),'conditional_gross_current_tax')
    return rows
