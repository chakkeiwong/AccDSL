"""Unresolved evidence intake only; positive recovery is outside this version."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

H=Path(__file__).resolve().parent; R=H.parents[2]
C=H.parent/'credit-claim-continuity-20261027/attempt-01'
PROFILE='UnresolvedCreditRecoveryIntake/1'
FLAGS={'posts':False,'mutations':[],'accounting_admission':False,
       'legal_forgiveness':'not_assessed','receipt_admission':False,'recovery_admission':False}
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return sha256(canonical(x).encode()).hexdigest()
def need(ok,reason):
    if not ok:raise ValueError(reason)
def protected():
    lock=json.loads((H/'source-lock.json').read_text())
    for p,h in lock.items():need(sha256((R/p).read_bytes()).hexdigest()==h,'source_drift:'+p)
    return lock
def retained(ident):
    row=next((x for x in json.loads((C/'cases.json').read_text()) if x['result']['case_id']==ident),None)
    need(row is not None,'outside_retained_cases')
    need(digest(row['result'])==row['record_sha256'],'retained_record_hash')
    return row
def request(ident):
    row=retained(ident);x=row['result']
    return {'profile':PROFILE,'case_id':ident,'claim_record_sha256':row['record_sha256'],
        'native_request_sha256':x['native_request_sha256'],'native_result_sha256':x['native_result_sha256'],
        'context_sha256':digest(x['context']),'receipt':None,'allocation':None,
        'legal_assessment':None,'accounting_proposal':None,'cash_flow_proposal':None}
def project(body):
    protected();need(type(body) is dict,'request_shape')
    need(set(body)=={'profile','case_id','claim_record_sha256','native_request_sha256',
        'native_result_sha256','context_sha256','receipt','allocation','legal_assessment',
        'accounting_proposal','cash_flow_proposal'},'request_shape')
    need(body['profile']==PROFILE,'profile')
    row=retained(body['case_id']);claim=row['result']
    need(body['claim_record_sha256']==row['record_sha256'],'claim_binding')
    for name in ['native_request_sha256','native_result_sha256']:
        need(body[name]==claim[name],name)
    need(body['context_sha256']==digest(claim['context']),'context_binding')
    need(claim['financial_derecognized'] is True,'financial_close_required')
    need(all(claim[k]==FLAGS[k] for k in ['posts','mutations','accounting_admission','legal_forgiveness','recovery_admission']),'retained_scope')
    receipt=body['receipt']
    if receipt is not None:
        need(type(receipt) is dict,'receipt_shape')
        ident=receipt.get('historical_source_event_id');source=receipt.get('historical_source_event_sha256')
        old=[m for m in claim['movements'] if m['component']=='collections']
        need(not any((ident is not None and ident==m['source_event_id']) or
                     (source is not None and source==m['source_event_sha256']) for m in old),
             'receipt_already_in_history')
        raise ValueError('new_receipt_outside_unresolved_intake_profile')
    for name in ['allocation','legal_assessment','accounting_proposal','cash_flow_proposal']:
        need(body[name] is None,name+'_outside_unresolved_intake_profile')
    components=[{'movement_index':m['movement_index'],'movement_sha256':digest(m),'component':deepcopy(m)}
                for m in claim['movements'] if m['component'] in ['uncollected','writeoff']]
    return {'profile':PROFILE,'status':'unresolved','case_id':body['case_id'],
        'request_sha256':digest(body),'claim_record_sha256':row['record_sha256'],
        'historical_claim':deepcopy(claim),'historical_components':components,
        'closure_date':claim['timeline'][-1]['date'],'receipt':None,'allocation':None,
        'legal_assessment':None,'accounting_proposal':None,'cash_flow_proposal':None,
        'missing_evidence':['new_receipt_source_amount_date_currency_and_availability',
            'allocation_to_historical_components_or_separately_supported_claim',
            'legal_scope_assessment','post_derecognition_accounting_authority_and_facts',
            'entity_specific_cash_flow_classification'],
        'financial_effects':[],'support_boundary':'positive_recovery_not_implemented',**deepcopy(FLAGS)}
def assess(body):
    try:return project(body)
    except (ValueError,TypeError,KeyError,OSError) as exc:
        return {'profile':PROFILE,'status':'rejected','reason':str(exc),**deepcopy(FLAGS)}
def validate(body,record,identity):
    try:
        need(digest(record)==identity,'record_hash');need(canonical(project(body))==canonical(record),'record_mismatch')
        return {'status':'verified_unresolved','record_sha256':identity}
    except (ValueError,TypeError,KeyError,OSError) as exc:return {'status':'rejected','reason':str(exc)}
