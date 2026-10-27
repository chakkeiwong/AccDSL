"""Draft partial state with explicit periods; no execution or latent allocation."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as Q
from pathlib import Path
import re, sys
from jsonschema import Draft202012Validator, FormatChecker
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
READINESS=HERE.parent/'real-company-input-readiness-20261024'
sys.path.insert(0,str(READINESS))
import readiness as prior
from readiness import canonical,digest,closed,OPS,COMPOSED
PROFILE='SourceConstrainedCompanyStateDraft/1'
CONTEXT_KEYS=['issuer','perimeter','basis','period','unit','measurement_kind']

def schema():
    text={'type':'string','minLength':1};h={'type':'string','pattern':'^[0-9a-f]{64}$'}
    day={'type':'string','pattern':r'^\d{4}-\d{2}-\d{2}$','format':'date'}
    ref=closed({'kind':text,'schema':text,'digest':h})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'name':text,
        'source':closed({'target':{'enum':[OPS,COMPOSED]},'view':{'enum':['annual','interim','combined']},
            'readiness_request_sha256':h,'readiness_result_sha256':h}),
        'periods':{'type':'array','minItems':1,'items':closed({'id':text,'kind':{'enum':['fiscal_year','interim']},
            'source_anchor':ref,'source_period':text,'start':day,'end_exclusive':day})},
        'bindings':{'type':'array','minItems':1,'items':closed({'id':text,'observation_ref':ref,
            'period_id':text,'measurement_date':day,'context':closed({k:text for k in CONTEXT_KEYS}),
            'interpretation':closed({'mode':{'enum':['display_only','assumed_rounding']},
                'assumption_id':{'type':['string','null'],'minLength':1}})})},
        'assumptions':{'type':'array','items':closed({'id':text,'rule':{'const':'nearest_ties_away_from_zero'},
            'quantum':{'type':'string','pattern':r'^(?:0|[1-9][0-9]*)/[1-9][0-9]*$'},
            'provenance':text,'disposition':{'const':'proposed_not_admitted'}})},
        'requirement_ids':{'type':'array','minItems':1,'items':text}})}

def validate(body):
    Draft202012Validator(schema(),format_checker=FormatChecker()).validate(body)
    def printable(x):
        if isinstance(x,dict):
            for k,v in x.items():printable(k);printable(v)
        elif isinstance(x,list):
            for v in x:printable(v)
        elif isinstance(x,str):
            x.encode('utf-8',errors='strict')
            if any(ord(c)<32 or ord(c)==127 or c in '\x85\u2028\u2029' for c in x):raise ValueError('single-line scalar')
    printable(body)
    for group in ['periods','bindings','assumptions']:
        ids=[r['id'] for r in body[group]]
        if len(ids)!=len(set(ids)):raise ValueError('duplicate '+group)
    if len(body['requirement_ids'])!=len(set(body['requirement_ids'])):raise ValueError('duplicate requirement')
    periods={p['id']:p for p in body['periods']}
    previous=None
    for p in body['periods']:
        start,end=map(date.fromisoformat,[p['start'],p['end_exclusive']])
        if start>=end:raise ValueError('empty or reversed period')
        if previous is not None and start!=previous:raise ValueError('nonconsecutive explicit periods')
        previous=end
    assumptions={a['id']:a for a in body['assumptions']}
    for a in assumptions.values():
        if Q(a['quantum'])<=0:raise ValueError('positive quantum required')
    used=set();refs=[]
    for b in body['bindings']:
        if b['period_id'] not in periods:raise ValueError('unknown period')
        p=periods[b['period_id']]
        if date.fromisoformat(b['measurement_date'])+timedelta(days=1)!=date.fromisoformat(p['end_exclusive']):raise ValueError('snapshot date not period close')
        if b['context']['period']!=b['measurement_date']:raise ValueError('context snapshot date')
        i=b['interpretation']
        if i['mode']=='display_only' and i['assumption_id'] is not None:raise ValueError('display-only assumption')
        if i['mode']=='assumed_rounding':
            if i['assumption_id'] not in assumptions:raise ValueError('unknown rounding premise')
            used.add(i['assumption_id'])
        refs.append(b['observation_ref']['digest'])
    if len(refs)!=len(set(refs)):raise ValueError('duplicate observation')
    if used!=set(assumptions):raise ValueError('unused assumption')
    return body

def upstream(target,view):
    request=prior.fixture(target,view);return request,prior.evaluate(request)

def fixture(target=OPS,view='combined'):
    request,result=upstream(target,view)
    body={'profile':PROFILE,'name':'Apple retained fiscal snapshots',
        'source':{'target':target,'view':view,'readiness_request_sha256':digest(request),'readiness_result_sha256':digest(result)},
        'periods':[],'bindings':[],'assumptions':[],
        'requirement_ids':[d['id'] for d in result['dependencies']]}
    for group,kind in [('annual_refs','fiscal_year'),('interim_refs','interim')]:
        rows=result['known_evidence'][group]
        if not rows:continue
        anchor=next(r for r in rows if r['record']['body']['row_id']=='operations.products_revenue')
        literal=anchor['context']['period']
        match=re.fullmatch(r'.+: (\d{4}-\d{2}-\d{2}) through (\d{4}-\d{2}-\d{2})',literal)
        if match is None:raise ValueError('unsupported source-period literal')
        start,last=match.groups();end=(date.fromisoformat(last)+timedelta(days=1)).isoformat()
        pid=group.removesuffix('_refs')
        body['periods'].append({'id':pid,'kind':kind,'source_anchor':anchor['ref'],
            'source_period':literal,'start':start,'end_exclusive':end})
        for row in rows:
            b=row['record']['body']
            if not b['row_id'].startswith('balance.'):continue
            body['bindings'].append({'id':pid+'.'+b['row_id'],'observation_ref':row['ref'],
                'period_id':pid,'measurement_date':row['context']['period'],'context':row['context'],
                'interpretation':{'mode':'display_only','assumption_id':None}})
    return validate(body)

def rational(x):return f'{x.numerator}/{x.denominator}'

def rounding_interval(displayed,quantum):
    d,q=Q(displayed),Q(quantum)
    if q<=0 or (d/q).denominator!=1:raise ValueError('display not on positive quantum grid')
    return {'lower':rational(d-q/2),'upper':rational(d+q/2),
        'lower_inclusive':d>0,'upper_inclusive':d<0}

def evaluate(body):
    validate(body)
    expected=fixture(body['source']['target'],body['source']['view'])
    comparison=deepcopy(body);comparison['name']=expected['name'];comparison['assumptions']=[]
    for b in comparison['bindings']:b['interpretation']={'mode':'display_only','assumption_id':None}
    if comparison!=expected:raise ValueError('source/context/period/dependency binding mismatch')
    request,result=upstream(body['source']['target'],body['source']['view'])
    observations={o['ref']['digest']:o for g in prior.GROUPS for o in result['known_evidence'][g]}
    assumptions={a['id']:a for a in body['assumptions']};constraints=[]
    for b in body['bindings']:
        source=observations[b['observation_ref']['digest']];value=source['record']['body']['value']
        c={'id':b['id'],'observation':deepcopy(source),'interpretation':deepcopy(b['interpretation']),
            'underlying_measurement':{'status':'unresolved','interval':None},'account_mapping':'unresolved'}
        if b['interpretation']['mode']=='assumed_rounding':
            if value['tag']!='known_displayed':raise ValueError('rounding needs numeric displayed evidence')
            a=assumptions[b['interpretation']['assumption_id']];v=value['amount']
            interval=rounding_interval(Q(int(v['n']),int(v['d'])),a['quantum'])
            c['underlying_measurement']={'status':'conditional_on_proposed_rounding','interval':interval}
        constraints.append(c)
    return {'profile':PROFILE,'program_sha256':digest(body),'source':deepcopy(body['source']),
        'status':'partial_description','periods':[{**p,'day_count':(date.fromisoformat(p['end_exclusive'])-date.fromisoformat(p['start'])).days} for p in body['periods']],
        'constraints':constraints,'assumptions':deepcopy(body['assumptions']),
        'dependencies':deepcopy(result['dependencies']),
        'unavailable_required_state':deepcopy(result['unavailable_required_state']),
        'unsupported_target_scope':deepcopy(result['unsupported_target_scope']),
        'actual_history':{'feasibility':'unknown','measure':None,'joint_constraints_solved':False},
        'executable_opening':None,'executed':False,
        'coverage':'Selected retained annual/interim balance captions; all other evidence and obligations remain in the bound readiness result.'}

def verify_result(body,result):
    try:return canonical(evaluate(body))==canonical(result)
    except Exception:return False
