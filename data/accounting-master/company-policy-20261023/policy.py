"""Non-executable illustrative receivable policy and exact path transformer."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
import json
import re

RAT=r'^(unknown|(?:0|-?[1-9][0-9]*)/[1-9][0-9]*)$'
PATH_SCHEMA=json.loads((Path(__file__).resolve().parent.parent/
    'company-operation-path-20261023/schema.json').read_text())


def schema():
    closed=lambda p:{'type':'object','properties':p,'required':list(p),'additionalProperties':False}
    text={'type':'string','minLength':1}
    sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
    rational={'type':'string','pattern':RAT}
    return closed({'profile':{'const':'SettlementPolicyDraft/1'},'policy_id':text,
        'parent_path_sha256':sha,'year_index':{'type':'integer','minimum':0},
        'delivery_operations':{'type':'array','minItems':1,'items':text},
        'collection_operations':{'type':'array','minItems':1,'items':text},
        'claim_ids':{'type':'array','minItems':1,'items':text},
        'fraction':rational,'installment_shares':{'type':'array','minItems':1,'items':rational},
        'rounding':{'const':'exact_rational_no_rounding'},
        'scope':{'const':'named_delivery_claims_only'},
        'real_behavior_evidence':{'const':False}})


def q(value):
    if not isinstance(value,str) or not re.fullmatch(RAT,value) or value=='unknown':
        raise ValueError('exact rational required')
    number=Q(value)
    if value!=str(number.numerator)+'/'+str(number.denominator):
        raise ValueError('canonical rational required')
    return number


def validate_policy(path,policy):
    if list(Draft202012Validator(PATH_SCHEMA,format_checker=FormatChecker()).iter_errors(path)):
        return {'status':'invalid','reason':'path_schema'}
    errors=list(Draft202012Validator(schema()).iter_errors(policy))
    if errors:return {'status':'invalid','reason':'policy_schema'}
    if policy['parent_path_sha256']!=digest(path):return {'status':'invalid','reason':'parent_path_identity'}
    if len(set(policy['delivery_operations']))!=len(policy['delivery_operations']):return {'status':'invalid','reason':'duplicate_delivery'}
    if len(set(policy['collection_operations']))!=len(policy['collection_operations']):return {'status':'invalid','reason':'duplicate_collection'}
    if len(set(policy['claim_ids']))!=len(policy['claim_ids']):return {'status':'invalid','reason':'duplicate_claim_target'}
    if len(policy['installment_shares'])!=len(policy['collection_operations']):return {'status':'invalid','reason':'installment_count'}
    if policy['fraction']=='unknown' or 'unknown' in policy['installment_shares']:
        return {'status':'unresolved','reason':'policy_fraction_or_share_unknown'}
    try:
        fraction=q(policy['fraction']);shares=[q(v) for v in policy['installment_shares']]
    except ValueError:return {'status':'invalid','reason':'rational'}
    if not 0<=fraction<=1 or any(x<0 for x in shares) or sum(shares,Q(0))!=1:
        return {'status':'invalid','reason':'fraction_domain'}
    definitions=[path['initial_year']]+path['continuations']
    if not 0<=policy['year_index']<len(definitions):return {'status':'invalid','reason':'year_index'}
    year=definitions[policy['year_index']];ops={o['id']:o for o in year['operations']}
    if len(ops)!=len(year['operations']):return {'status':'invalid','reason':'duplicate_operation_id'}
    if any(x not in ops or ops[x]['kind']!='delivery' for x in policy['delivery_operations']):
        return {'status':'invalid','reason':'delivery_binding'}
    if any(x not in ops or ops[x]['kind']!='collection' for x in policy['collection_operations']):
        return {'status':'invalid','reason':'collection_binding'}
    claims={ops[x]['payload']['claim_id']:ops[x] for x in policy['delivery_operations']}
    all_new=[o['payload']['claim_id'] for o in year['operations'] if o['kind'] in ['delivery','purchase']]
    if len(set(all_new))!=len(all_new):return {'status':'invalid','reason':'duplicate_issued_claim'}
    if set(claims)!=set(policy['claim_ids']):return {'status':'invalid','reason':'claim_binding'}
    if any(o['at']=='unknown' for o in year['operations']):
        return {'status':'unresolved','reason':'operation_instants_unknown'}
    if [o['at'] for o in year['operations']]!=sorted(o['at'] for o in year['operations']):
        return {'status':'invalid','reason':'operation_chronology'}
    operation_order={op['id']:i for i,op in enumerate(year['operations'])}
    if any(operation_order[d]>=operation_order[c]
           for d in policy['delivery_operations'] for c in policy['collection_operations']):
        return {'status':'invalid','reason':'collection_before_delivery'}
    for collection_id in policy['collection_operations']:
        allocations=ops[collection_id]['payload']['allocations']
        if len({a['claim_id'] for a in allocations})!=len(allocations):
            return {'status':'invalid','reason':'duplicate_allocation'}
        targets=[a['claim_id'] for a in allocations if a['claim_id'] in claims]
        if targets!=policy['claim_ids']:return {'status':'invalid','reason':'target_allocation_coverage'}
    for op in year['operations']:
        if op['kind']=='collection' and op['id'] not in policy['collection_operations']:
            if any(a['claim_id'] in claims for a in op['payload']['allocations']):
                return {'status':'unsupported','reason':'additional_target_claim_settlement'}
    for op in claims.values():
        p=op['payload']
        if 'unknown' in [p['units'],p['unit_price'],p['control_transferred']]:
            return {'status':'unresolved','reason':'delivery_inputs_unknown'}
        if p['control_transferred'] is not True:return {'status':'unsupported','reason':'control_transfer_not_established'}
        try:units,price=q(p['units']),q(p['unit_price'])
        except ValueError:return {'status':'invalid','reason':'invoice_rational'}
        if units<0 or price<0:return {'status':'invalid','reason':'negative_invoice_input'}
    return {'status':'validated_scoped_policy','evidence':'illustrative_only',
            'real_behavior_evidence':False}


def generate(path,policy):
    """Apply one declarative policy; retain every non-target input byte-for-byte."""
    checked=validate_policy(path,policy)
    if checked['status']!='validated_scoped_policy':return checked
    child=deepcopy(path);year=[child['initial_year']]+child['continuations']
    target=year[policy['year_index']];ops={o['id']:o for o in target['operations']}
    invoices={}
    for operation_id in policy['delivery_operations']:
        op=ops[operation_id];claim=op['payload']['claim_id']
        invoices[claim]=q(op['payload']['units'])*q(op['payload']['unit_price'])
    changes=[]
    for collection_id,share in zip(policy['collection_operations'],policy['installment_shares']):
        op=ops[collection_id]
        for allocation in op['payload']['allocations']:
            claim=allocation['claim_id']
            if claim in invoices:
                old=allocation['amount'];new=wire(invoices[claim]*q(policy['fraction'])*q(share))
                allocation['amount']=new
                changes.append({'operation_id':collection_id,'claim_id':claim,
                    'prior_amount':old,'generated_amount':new,'invoice_amount':wire(invoices[claim]),
                    'fraction':policy['fraction'],'installment_share':share})
    return {'status':'materialized_conditional_path','policy':deepcopy(policy),
            'policy_sha256':digest(policy),'parent_path_sha256':digest(path),
            'child_path_sha256':digest(child),'path':child,'allocation_trace':changes,
            'claim_totals':[{'claim_id':claim,'invoice_amount':wire(value),
                'generated_collections':wire(value*q(policy['fraction'])),
                'uncollected':wire(value*(1-q(policy['fraction'])))} for claim,value in invoices.items()],
            'execution_required':True,
            'information_admission':{'status':'unresolved','reason':'policy_information_not_admitted'},
            'real_behavior_evidence':False,'forecast_admission':False}


def qwire(value):return str(value.numerator)+'/'+str(value.denominator)


def verify_materialization(path,policy,materialized):
    expected=generate(path,policy)
    if expected.get('status')!='materialized_conditional_path':return expected
    if expected!=materialized:return {'status':'invalid','reason':'policy_materialization_mismatch'}
    return {'status':'verified_materialization','execution_required':True,
            'real_behavior_evidence':False,'forecast_admission':False}

def wire(value):
    if isinstance(value,Q):return qwire(value)
    if isinstance(value,dict):return {k:wire(v) for k,v in value.items()}
    if isinstance(value,list):return [wire(v) for v in value]
    return value

def canonical(value):
    import json
    return json.dumps(wire(value),sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def digest(value):
    import hashlib
    return hashlib.sha256(canonical(value)).hexdigest()
