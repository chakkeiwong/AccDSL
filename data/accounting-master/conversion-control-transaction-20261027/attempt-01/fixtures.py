from copy import deepcopy
from hashlib import sha256
import json
PROFILE='ConditionalAcquisitionTransactionPartition/1'
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def bind(r):
    p=r['payload'];p['source']['declaration_sha256']=digest(p['declaration']);p['evidence_sha256']=digest(p['source']);r['expected_payload_sha256']=digest(p);return r
def request():
    rows=[dict(id=id,kind=k,role=role,amount=value,rationale='Independently supplied synthetic allocation,not a derived loan or business valuation.') for id,k,role,value in [
      ('new_cash','cash_transfer','acquisition_consideration','80/1'),('old_debt','debt_claim_settlement','debt_settlement','20/1'),
      ('fee','service_fee','acquisition_cost','5/1'),('separate','other_separate_transfer','other_separate','3/1')]]
    c=dict(subject='P',actor='researcher',at='2026-10-27T01:00:00Z',cutoff='2026-10-27T03:00:00Z')
    d=dict(context=c,currency='USD',unit='currency_unit',inventory=[r['id'] for r in rows],components=rows,inventory_coverage='supplied_complete',allocation_assessment='supplied_complete')
    src=dict(text='Synthetic component inventory and transaction allocation.',rationale='No actual conversion-to-control measurement is admitted.',subject='P',actor='researcher',at=c['at'],available_at='2026-10-27T02:00:00Z',declaration_sha256=digest(d))
    return bind(dict(profile=PROFILE,payload=dict(declaration=d,source=src,evidence_sha256=digest(src)),expected_payload_sha256=''))
def expected(r,totals,total=None,deps=None,unavailable=False):
    p=r['payload'];out=dict(profile=PROFILE,source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,
      request_sha256=digest(r),scope_assessment='supplied_assertions_only',declaration=deepcopy(p['declaration']),source=deepcopy(p['source']),debt_as_prior_equity=False,goodwill=None,journals=[],report=None)
    if deps:return dict(out,status='unresolved',dependencies=sorted(deps),known_partial_totals={} if unavailable else totals,partition_total=None,request=deepcopy(r))
    return dict(out,status='conditional_partition',dependencies=['actual_inventory_and_allocation','actual_measurements_and_period_authority',
      'control_business_and_preexisting_debt_analysis','acquired_basis_tax_and_reports'],totals=totals,partition_total=total,acquisition_consideration=totals['acquisition_consideration'],
      scope='Arithmetic partition of supplied component measurements only; not goodwill or actual acquisition accounting.')
TOTALS=dict(acquisition_consideration='80/1',debt_settlement='20/1',acquisition_cost='5/1',other_separate='3/1')
def cases():
    rows=[]
    def add(id,r,totals=TOTALS,total='108/1',deps=None,unavailable=False):bind(r);rows.append(dict(id=id,request=r,expected=expected(r,totals,total,deps,unavailable)))
    add('complete',request())
    r=request();r['payload']['declaration']['components'][1]['amount']='0/1';add('explicit_zero',r,{**TOTALS,'debt_settlement':'0/1'},'88/1')
    r=request();r['payload']['declaration']['components'][1]['amount']=None;add('unknown_debt',r,{**TOTALS,'debt_settlement':'0/1'},None,['component_amount:old_debt'])
    r=request();r['payload']['declaration']['components'][1]['role']='unknown';add('unknown_role',r,{**TOTALS,'debt_settlement':'0/1'},None,['component_role:old_debt'])
    for k in ['inventory_coverage','allocation_assessment']:
        r=request();r['payload']['declaration'][k]='unresolved';add(k,r,TOTALS,None,[k])
    for name,date,dep in [('late','2026-10-28T00:00:00Z','source_after_cutoff'),('unknown_time',None,'source_availability_unknown')]:
        r=request();r['payload']['source']['available_at']=date;add(name,r,TOTALS,None,[dep],True)
    r=request();d=r['payload']['declaration'];d['components'][0]['amount']='30/1'
    d['components'].append(dict(id='extra_cash',kind='cash_transfer',role='acquisition_consideration',amount='50/1',rationale='Second independently declared consideration component.'));d['inventory'].append('extra_cash');add('split_consideration',r)
    return rows
