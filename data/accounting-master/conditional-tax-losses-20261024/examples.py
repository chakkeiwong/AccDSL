"""Distinct hypothetical loss-ledger periods; never native financial carry."""
from copy import deepcopy
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import conditional_tax_losses_v1 as m

def known(value):
    return {'status':'known','value':value,'provenance':{'kind':'assumption',
        'reference':'Hypothetical loss-ledger control; no actual tax rule or source admission'}}
def no_expiry():return {'kind':'none','provenance':known(True)['provenance']}
def dated(day):return {'kind':'date','end_exclusive':day,'provenance':known(True)['provenance']}
def original_request():
    rows=json.loads((ROOT/'data/accounting-master/shared-tax-reconciliation-20261024/cases.json').read_text())
    return deepcopy(next(r['request'] for r in rows if r['case']=='mixed_negative_expression'))
def initial():
    body=original_request();info=body['information_request']
    return {'profile':m.STATE,'context':deepcopy(info['report_request']['opening']['context']),
        'jurisdiction':info['information']['jurisdiction']['value'],'regime':info['information']['regime']['value'],
        'cursor':info['interval']['start'],'lots':[],'seen':[],'history':[],
        'opening_inventory':known(True)}
def model():return {'profile':m.MODEL,'selected':known(True)}
def generate():
    return m.request(initial(),original_request(),'generate-19',model(),known('0/1'),[],
        {'id':'loss-19','eligible':known(True),'expiry':no_expiry()})
def future_request(taxable='21/1'):
    body=original_request();info=body['information_request']
    opening=deepcopy(info['report_request']['opening'])
    opening['date']='2026-01-01';opening['period']={'start':'2026-01-01','end_exclusive':'2027-01-01'}
    opening['tax_closed_until']='2026-01-01'
    opening['source']['premise']='Separate hypothetical 2026 opening; not carry from the recorded 2024-2026 book.'
    opening['source']['numeric_lineage']='Opening amounts copied as explicit controls; period continuity of financial state is not claimed.'
    for member in opening['leases']:
        for right in member['component']['rights']:right['last_measurement_date']='2026-01-01'
    info['report_request']=m.tax.information.reports.request(opening,[])
    info['report_request_sha256']=m.book.digest(info['report_request'])
    info['interval']={'start':'2026-01-01','end_exclusive':'2027-01-01','activity_through':'2026-12-31'}
    info['information']['income/revenue/current_adjustment']['value']='0/1'
    info['information']['income/other_gains/current_adjustment']['value']=taxable
    body['information_sha256']=m.book.digest(info)
    body['allocations']=[{'id':'hypothetical-2026','account':'other_gains','amount':taxable,
        'origin':{'kind':'assumption','reference':'Independent 2026 taxable-income control; no forecast or financial-book carry'}}]
    return body
def use(amount='19/1',cap='21/1',taxable='21/1'):
    generated=m.propose(generate());assert generated['status']=='proposed',generated.get('reason')
    return m.request(generated['proposal']['after'],future_request(taxable),'use-2026',model(),known(cap),
        [] if amount=='0/1' else [{'lot_id':'loss-19','amount':amount}],None)
def rehash(body):
    body['state_sha256']=m.book.digest(body['state'])
    body['reconciliation_sha256']=m.book.digest(body['reconciliation_request'])
    return body
def cases():
    rows=[]
    def add(name,body,status):rows.append({'case':name,'request':deepcopy(body),'expected_status':status})
    generation=generate();usage=use()
    add('generate_19',generation,'proposed');add('consume_19_from_21',usage,'proposed')
    add('partial_use_7',use('7/1'),'proposed');add('zero_explicit_use',use('0/1'),'proposed')
    add('zero_taxable_profit',use('0/1','0/1','0/1'),'proposed')
    x=deepcopy(usage);x['state']['lots'][0]['expiry']=dated('2026-12-31')
    add('expiry_on_usage_day_blocks_use',rehash(x),'invalid')
    x['uses']=[];add('expiry_on_usage_day_expires_all',x,'proposed')
    x=deepcopy(usage);x['state']['lots'][0]['expiry']=dated('2027-01-01');x['uses'][0]['amount']='7/1'
    add('expiry_at_endpoint_allows_use_then_expires',rehash(x),'proposed')
    x=deepcopy(usage);x['state']['lots'][0]['expiry']=dated('2027-01-02');x['uses'][0]['amount']='7/1'
    add('expiry_after_endpoint_preserves_remainder',rehash(x),'proposed')
    x=deepcopy(usage);x['state']['lots'][0]['expiry']={'kind':'unknown','reason':'Expiry not supplied'}
    add('opening_expiry_unknown',rehash(x),'unresolved')
    x=deepcopy(generation);x['generation']['eligible']={'status':'unknown','reason':'Eligibility not supplied'}
    add('generation_eligibility_unknown',x,'unresolved')
    x=deepcopy(generation);x['generation']['eligible']=known(False);add('generation_ineligible',x,'unsupported')
    x=deepcopy(generation);x['generation']['expiry']={'kind':'unknown','reason':'No expiry premise'}
    add('generation_expiry_unknown',x,'unresolved')
    x=deepcopy(generation);x['generation']['expiry']=dated('2026-01-01');add('generation_expired_at_birth',x,'invalid')
    x=deepcopy(usage);x['state']['lots'][0]['eligible']={'status':'unknown','reason':'Origin eligibility unknown'}
    add('opening_eligibility_unknown',rehash(x),'unresolved')
    x=deepcopy(usage);x['state']['lots'][0]['eligible']=known(False);add('opening_ineligible',rehash(x),'unsupported')
    x=deepcopy(usage);x['state']['opening_inventory']={'status':'unknown','reason':'Opening loss inventory incomplete'}
    add('opening_inventory_unknown',rehash(x),'unresolved')
    x=deepcopy(usage);x['uses'][0]['amount']='20/1';add('lot_overuse',x,'invalid')
    x=deepcopy(usage);x['utilization_cap']=known('18/1');add('cap_exceeded',x,'invalid')
    add('profit_exceeded',use('19/1','21/1','18/1'),'invalid')
    x=deepcopy(usage);x['uses'].append(deepcopy(x['uses'][0]));add('duplicate_usage',x,'invalid')
    x=deepcopy(usage);x['step_id']='generate-19';add('duplicate_step',x,'invalid')
    x=deepcopy(usage);x['state']['regime']='different regime';add('regime_mismatch',rehash(x),'invalid')
    x=deepcopy(usage);x['state']['context']['currency']='EUR';add('currency_mismatch',rehash(x),'invalid')
    x=deepcopy(usage);x['state']['cursor']='2026-02-01';x['state']['history']=[];x['state']['seen']=[]
    add('stale_cursor',rehash(x),'invalid')
    x=deepcopy(usage);x['state_sha256']='0'*64;add('forged_state_identity',x,'invalid')
    x=deepcopy(usage);x['model']['selected']={'status':'unknown','reason':'No policy selection'};add('policy_unknown',x,'unresolved')
    x=deepcopy(usage);x['model']['selected']=known(False);add('policy_false',x,'unsupported')
    x=deepcopy(usage);x['utilization_cap']={'status':'unknown','reason':'Cap not supplied'};add('cap_unknown',x,'unresolved')
    x=deepcopy(usage);x['generation']={'id':'new','eligible':known(True),'expiry':no_expiry()};add('positive_cannot_generate',x,'invalid')
    x=deepcopy(generation);x['uses']=[{'lot_id':'loss-19','amount':'1/1'}];add('new_loss_not_usable_now',x,'invalid')
    x=deepcopy(usage);x['uses'][0]['amount']='0/1';add('zero_usage_is_explicit_empty_list',x,'invalid')
    return rows
