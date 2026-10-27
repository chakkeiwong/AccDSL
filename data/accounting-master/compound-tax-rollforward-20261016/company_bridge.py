"""Closed finite company projection; OrderedEPS is called only after replay."""
from fractions import Fraction as Q
import hashlib
import json
import re

from reference_company import ROOT, OUT, replay_base, derive_company, report_request, eps_oracle, digest, file_ref

PREMISES = json.loads((OUT/'premises.json').read_text())
LOCK = {item['path']:item['sha256'] for item in json.loads((OUT/'input-lock.json').read_text())['files']}
LOCK.update({item['path']:item['sha256'] for item in json.loads((OUT/'runtime-input-lock.json').read_text())['files']})
BASE_PATH = 'data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json'
BASE_REF = dict(path=BASE_PATH,sha256=LOCK[BASE_PATH],anchor='complete P5 company opening, thirteen events and annual close')
assert BASE_REF['sha256'] == json.loads((ROOT/'data/accounting-master/company-eps-join-20261016/base-packet-lock.json').read_text())['sha256']
SUPPORT = file_ref(OUT/'premises.json','explicit synthetic par-compound fiscal, rights and company premises')
SUPPORT['sha256'] = LOCK[SUPPORT['path']]


def shape(value,template):
    if value is None:
        return True
    if isinstance(template,dict):
        return isinstance(value,dict) and set(value)==set(template) and all(shape(value[k],v) for k,v in template.items())
    return type(value) is type(template)


def missing(value):
    return value is None or isinstance(value,dict) and any(missing(v) for v in value.values())


def noncanonical(value,template):
    if isinstance(template,dict):
        return any(noncanonical(value[k],v) for k,v in template.items())
    if isinstance(template,str) and re.fullmatch(r'[0-9]+(?:/[0-9]+)?',template):
        try:
            return str(Q(value)) != value
        except (ValueError,ZeroDivisionError):
            return True
    return False


def bridge(request,resolve_bytes=None):
    result = dict(wire='CompanyTaxEPS/1',status='rejected',reason=None,company=None,eps=None,mutations=[])
    def refuse(status,reason):
        result.update(status=status,reason=reason)
        return result
    if not isinstance(request,dict) or set(request)!={'wire','operation','world','base_packet','premises','eps'}:
        return refuse('rejected','request_shape')
    if request['wire']!='CompanyTaxEPS/1' or request['operation']!='report':
        return refuse('rejected','operation')
    if request['world'] not in ('conversion','redemption'):
        return refuse('unsupported','settlement_world')
    if request['base_packet'] != BASE_REF:
        return refuse('rejected','base_binding')
    if not shape(request['premises'],PREMISES):
        return refuse('rejected','premise_shape')
    if missing(request['premises']):
        return refuse('unresolved','missing_premise')
    if noncanonical(request['premises'],PREMISES):
        return refuse('rejected','noncanonical_rational')
    p=request['premises']
    if any(not p['scope'][k] for k in ('complete_instrument_inventory','complete_ordinary_share_history')) or not p['new_instrument']['tax']['complete_consequences']:
        return refuse('unresolved','incomplete_premises')
    if p != PREMISES:
        return refuse('unsupported','outside_company_profile')
    reader=resolve_bytes or (lambda p:p.read_bytes())
    for ref in (dict(path=path,sha256=value) for path,value in LOCK.items()):
        try:
            payload=reader(ROOT/ref['path'])
        except OSError:
            return refuse('unresolved','input_bytes_missing')
        if hashlib.sha256(payload).hexdigest()!=ref['sha256']:
            return refuse('rejected','input_bytes_changed')
    base=replay_base()
    company=derive_company(request['world'],p,base)
    projection=report_request(request['world'],company,p,SUPPORT)
    if request['eps'] != projection:
        return refuse('rejected','company_eps_projection_mismatch')
    eps=eps_oracle.calculate(projection)
    if eps['status']!='conditional_complete':
        return refuse(eps['status'],'eps_not_admitted')
    result.update(status='conditional_complete',company=company,eps=eps)
    return result
