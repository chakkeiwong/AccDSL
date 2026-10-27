"""Finite retained-source readiness reference; does not construct CompanyState."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from requirements import OPS, COMPOSED, REQUIREMENTS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACKET = HERE.parent/'real-package-connection-20261015/portable-exchanges.json'
PACKET_SHA = 'b4218e0c0812ec8b3480658db05a071914a0db0041f41d0c101de721781c594b'
PROFILE = 'RetainedCompanyInputReadinessDraft/1'
GROUPS = ('annual_refs','interim_refs','annual_opening_refs','interim_comparison_refs')
TARGETS = {OPS: HERE.parent/'company-operations-20261023/operations.py',
           COMPOSED: HERE.parent/'company-composed-profile-20261024/company_program.py'}

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def digest(value):
    return sha256(canonical(value)).hexdigest()

def closed(properties):
    return dict(type='object',properties=properties,required=list(properties),additionalProperties=False)

def schema():
    text={'type':'string','minLength':1}
    h={'type':'string','pattern':'^[0-9a-f]{64}$'}
    ref=closed({'kind':text,'schema':text,'digest':h})
    assumption=closed({'id':text,'requirement_id':{'enum':[r['id'] for r in REQUIREMENTS]},
        'statement':text,'provenance':text,'disposition':{'const':'proposed_not_admitted'}})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'packet_sha256':h,'issuer':{'const':'Apple'},
        'package_ref':ref,'view_ref':ref,'target':{'enum':list(TARGETS)},
        'target_implementation_sha256':h,'information_mode':{'const':'named_retained_sources'},
        'assumptions':{'type':'array','items':assumption}})}

def load_packet(raw=None):
    raw=PACKET.read_bytes() if raw is None else raw
    if sha256(raw).hexdigest()!=PACKET_SHA:raise ValueError('retained packet bytes changed')
    return json.loads(raw)

def record(packet, ref):
    value=packet['record_registry'][ref['digest']]
    if (value['kind'],value['schema'])!=(ref['kind'],ref['schema']):raise ValueError('reference type')
    actual=sha256(('accdsl.portable.v1/'+value['schema']).encode()+b'\0'+canonical(value)).hexdigest()
    if actual!=ref['digest']:raise ValueError('record digest')
    return deepcopy(value)

def fixture(target=OPS, view='combined'):
    packet=load_packet()
    return {'profile':PROFILE,'packet_sha256':PACKET_SHA,'issuer':'Apple',
        'package_ref':deepcopy(packet['aliases']['apple.package']),
        'view_ref':deepcopy(packet['aliases']['view.'+view]),'target':target,
        'target_implementation_sha256':sha256(TARGETS[target].read_bytes()).hexdigest(),
        'information_mode':'named_retained_sources','assumptions':[]}

def observation(packet, ref):
    source=record(packet,ref);b=source['body']
    context=record(packet,b['context_ref'])['body']
    if context['issuer']!='Apple':raise ValueError('cross issuer observation')
    return {'ref':deepcopy(ref),'record':source,'context':context}

def evaluate(request, raw=None):
    Draft202012Validator(schema()).validate(request)
    packet=load_packet(raw)
    if request['packet_sha256']!=PACKET_SHA:raise ValueError('request packet identity')
    if request['package_ref']!=packet['aliases']['apple.package']:raise ValueError('package identity')
    names=['annual','interim','combined']
    if request['view_ref'] not in [packet['aliases']['view.'+v] for v in names]:raise ValueError('view outside retained package')
    target=request['target']
    if request['target_implementation_sha256']!=sha256(TARGETS[target].read_bytes()).hexdigest():raise ValueError('target identity')
    ids=[a['id'] for a in request['assumptions']]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate assumption identity')
    view=record(packet,request['view_ref'])['body']
    sources={r['digest'] for r in view['source_refs']}
    package=record(packet,request['package_ref'])['body']
    report=record(packet,packet['aliases']['apple.reported-statements'])['body']
    inventory=[{'ref':r,'record':record(packet,r)} for r in package['inventory_refs']]
    collections={k:deepcopy(report[k]) for k in GROUPS}
    selected={k:[observation(packet,r) for r in report[k]
        if record(packet,r)['body']['source_ref']['digest'] in sources] for k in GROUPS}
    readings=[r for k in GROUPS for r in selected[k]]
    obligations={r['body']['code']:{'kind':r['kind'],'schema':r['schema'],'digest':h}
        for h,r in packet['record_registry'].items() if r['kind']=='Obligation' and r['body']['issuer']=='Apple'}
    dependencies=[]
    for spec in REQUIREMENTS:
        refs=[x['ref'] for x in readings if x['record']['body']['row_id'].removeprefix('opening.') in spec['row_ids']]
        dependencies.append({'id':spec['id'],'target_fields':spec['target_fields'][target],
            'evidence_refs':refs,'obligation_refs':[obligations[c] for c in spec['obligation_codes']],
            'unavailable_state':spec['missing'],'unsupported_scope':spec['unsupported'][target],
            'required_for_selected_execution':spec['id']!='information',
            'affects':spec['affects'],'next':spec['next'],
            'assumption_ids':[a['id'] for a in request['assumptions'] if a['requirement_id']==spec['id']]})
    derived=[]
    for group in ['annual_refs','interim_refs']:
        rows={o['record']['body']['row_id']:o for o in selected[group]}
        keys=['balance.debt_current','balance.debt_noncurrent']
        if not all(k in rows for k in keys):continue
        inputs=[rows[k] for k in keys]
        if inputs[0]['context']!=inputs[1]['context']:raise ValueError('incompatible debt-caption contexts')
        if any(x['record']['body']['value']['tag']!='known_displayed' for x in inputs):raise ValueError('non-numeric debt caption')
        amounts=[x['record']['body']['value']['amount'] for x in inputs]
        total=sum((Fraction(int(a['n']),int(a['d'])) for a in amounts),Fraction())
        derived.append({'id':group+'.displayed_term_debt_sum','classification':'conditional_derivation',
            'operation':'sum_displayed_captions','input_refs':[x['ref'] for x in inputs],
            'amount':{'n':str(total.numerator),'d':str(total.denominator)},'context':inputs[0]['context'],
            'premise':'Arithmetic on two same-context displayed term-debt captions only.',
            'limitation':'Not total debt, exact latent principal, an instrument allocation or an executable input.'})
    return {'profile':PROFILE,'request_sha256':digest(request),'request':deepcopy(request),
        'status':'blocked','executable_opening':None,'executed':False,
        'known_evidence':selected,'conditional_derivations':derived,
        'explicit_assumptions':deepcopy(request['assumptions']),'dependencies':dependencies,
        'unavailable_required_state':[d['id'] for d in dependencies if d['unavailable_state'] and d['required_for_selected_execution']],
        'unsupported_target_scope':[d['id'] for d in dependencies if d['unsupported_scope']],
        'preserved_package':{'inventory':inventory,'original_statement_collections':collections,
            'statement_report':record(packet,packet['aliases']['apple.reported-statements']),
            'package':record(packet,request['package_ref']),
            'obligations':{c:record(packet,r) for c,r in obligations.items()},
            'family':record(packet,packet['aliases']['apple.family']),
            'connected_result':record(packet,packet['aliases']['apple.connected']),
            'interpretation':'Retained context only; observation admission remains restricted to the requested view.'},
        'decision_scope':'Selected finite target cannot execute these retained inputs; no company-wide impossibility or feasibility conclusion.'}

def verify_result(request,result):
    try:return canonical(evaluate(request))==canonical(result)
    except (ValueError,KeyError,TypeError,ValidationError):return False
