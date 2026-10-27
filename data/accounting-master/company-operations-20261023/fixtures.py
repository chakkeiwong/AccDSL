"""Economic input transformations; no reference output generation."""
from copy import deepcopy
from fractions import Fraction as Q
from operations import q, wire, REPEAT


def split_operations(body, first_share=Q(1,2)):
    """Split linear operations at their original instant, retaining array order."""
    result=deepcopy(body);claims={}
    for op in body['operations']:
        if op['kind'] in ['purchase','delivery']:
            key=op['payload']['claim_id']
            claims[key]=[(key+'-a',first_share),(key+'-b',1-first_share)]
    ops=[]
    for op in body['operations']:
        kind=op['kind']
        if kind not in REPEAT:
            ops.append(deepcopy(op));continue
        for suffix,factor in [('a',first_share),('b',1-first_share)]:
            child=deepcopy(op);child['id']+='-'+suffix;p=child['payload']
            if kind in ['purchase','delivery']:
                p['units']=wire(q(p['units'])*factor);p['claim_id']+='-'+suffix
            elif kind in ['collection','supplier_payment']:
                allocations=[]
                for a in p['allocations']:
                    for cid,claim_share in claims.get(a['claim_id'],[(a['claim_id'],Q(1))]):
                        allocations.append({'claim_id':cid,'amount':wire(q(a['amount'])*factor*claim_share)})
                p['allocations']=allocations
            elif kind=='plant_addition':
                p['cost']=wire(q(p['cost'])*factor);p['asset_id']+='-'+suffix
            else:p['amount']=wire(q(p['amount'])*factor)
            ops.append(child)
    result['operations']=ops
    return result
