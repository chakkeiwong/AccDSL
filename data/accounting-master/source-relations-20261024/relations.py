"""Finite statement relations; local intervals never imply joint feasibility."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import json,sys
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
STATE=HERE.parent/'source-constrained-state-20261024';sys.path.insert(0,str(STATE))
import partial_state as state
from partial_state import canonical,digest,closed,OPS,COMPOSED
PROFILE='SourceMeasurementRelationsDraft/1'
LEDGERS={'annual':HERE.parent/'apple-statement-network-20261013/relationship-ledger.json',
         'interim':HERE.parent/'apple-interim-network-20261013/relationship-ledger.json'}

def sha(p):return sha256(p.read_bytes()).hexdigest()
def rat(x):return f'{x.numerator}/{x.denominator}'
def load_ledger(group):
    path=LEDGERS[group];name=path.relative_to(ROOT).as_posix()
    blobs=state.prior.load_packet()['blobs']
    matches=[h for h,b in blobs.items() if b['path']==name]
    if len(matches)!=1 or sha(path)!=matches[0]:raise ValueError('retained ledger bytes changed')
    return json.loads(path.read_text())
def schema():
    text={'type':'string','minLength':1};h={'type':'string','pattern':'^[0-9a-f]{64}$'}
    ref=closed({'kind':text,'schema':text,'digest':h})
    term=closed({'coefficient':{'type':'string','pattern':r'^(?:0|-?[1-9][0-9]*)/[1-9][0-9]*$'},'observation_ref':ref})
    hypothesis=closed({'id':text,'provenance':text,'disposition':{'const':'proposed_not_admitted'}})
    relation=closed({'id':text,'ledger_group':{'enum':['annual','interim']},
        'source_pointer':{'type':'string','pattern':r'^/relations/(?:0|[1-9][0-9]*)$'},
        'source_record_sha256':h,'terms':{'type':'array','minItems':1,'items':term},
        'target_ref':ref,'measurement_identity':{'oneOf':[{'type':'null'},hypothesis]}})
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**closed({
        'profile':{'const':PROFILE},'state_request':state.schema(),'state_result_sha256':h,
        'ledgers':{'type':'array','minItems':1,'items':closed({'group':{'enum':['annual','interim']},'path':text,'sha256':h})},
        'relations':{'type':'array','minItems':1,'items':relation}})}

def normalized(terms):
    out={}
    for t in terms:
        key=t['observation_ref']['digest'];out[key]=out.get(key,Q(0))+Q(t['coefficient'])
    return {k:v for k,v in out.items() if v}

def interval_sum(terms,intervals):
    weights=normalized(terms);lo=hi=Q(0);li=ui=True
    for key,a in weights.items():
        if key not in intervals or intervals[key] is None:return {'status':'unresolved','missing':sorted(k for k in weights if intervals.get(k) is None)}
        x=intervals[key];low,high=Q(x['lower']),Q(x['upper'])
        if low>high or (low==high and not(x['lower_inclusive'] and x['upper_inclusive'])):raise ValueError('empty interval')
        if a>0:l,u,lc,uc=a*low,a*high,x['lower_inclusive'],x['upper_inclusive']
        else:l,u,lc,uc=a*high,a*low,x['upper_inclusive'],x['lower_inclusive']
        lo+=l;hi+=u;li=li and lc;ui=ui and uc
    zero=(lo<0 or (lo==0 and li)) and (hi>0 or (hi==0 and ui))
    return {'status':'conditional_interval','interval':{'lower':rat(lo),'upper':rat(hi),
        'lower_inclusive':li,'upper_inclusive':ui},'zero_contained':zero,
        'meaning':'Local residual range over interval operands; cross-relation feasibility uncomputed.'}

def displayed_residual(terms,values):
    weights=normalized(terms);missing=[k for k in weights if k not in values or values[k].get('tag')!='known_displayed']
    if missing:return {'status':'unresolved','missing':sorted(missing)}
    value=Q(0)
    for key,a in weights.items():
        v=values[key]['amount'];value+=a*Q(int(v['n']),int(v['d']))
    return {'status':'displayed_arithmetic','residual':rat(value),'zero':value==0}

def fixture(state_request=None):
    body=state.fixture() if state_request is None else deepcopy(state_request);result=state.evaluate(body)
    selected={c['id']:c['observation']['ref'] for c in result['constraints']}
    groups=[p['id'] for p in body['periods']];ledgers=[];relations=[]
    for group in groups:
        path=LEDGERS[group];ledger=load_ledger(group)
        ledgers.append({'group':group,'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)})
        for i,r in enumerate(ledger['relations']):
            terms=r.get('terms');target=r.get('target')
            if not terms or group+'.'+str(target) not in selected:continue
            if any(group+'.'+t['row'] not in selected for t in terms):continue
            relations.append({'id':group+'.'+r['id'],'ledger_group':group,'source_pointer':'/relations/'+str(i),
                'source_record_sha256':digest(r),'terms':[{'coefficient':rat(Q(t['coefficient'])),
                    'observation_ref':selected[group+'.'+t['row']]} for t in terms],
                'target_ref':selected[group+'.'+target],'measurement_identity':None})
    return {'profile':PROFILE,'state_request':body,'state_result_sha256':digest(result),'ledgers':ledgers,'relations':relations}

def evaluate(body):
    Draft202012Validator(schema()).validate(body)
    expected=fixture(body['state_request']);comparison=deepcopy(body)
    hypothesis_ids=[]
    for r in comparison['relations']:
        h=r['measurement_identity']
        if h is not None:hypothesis_ids.append(h['id'])
        r['measurement_identity']=None
    if len(hypothesis_ids)!=len(set(hypothesis_ids)):raise ValueError('duplicate identity hypothesis')
    if comparison!=expected:raise ValueError('source relation binding mismatch')
    partial=state.evaluate(body['state_request'])
    observations={c['observation']['ref']['digest']:c['observation'] for c in partial['constraints']}
    values={k:o['record']['body']['value'] for k,o in observations.items()}
    intervals={c['observation']['ref']['digest']:c['underlying_measurement']['interval'] for c in partial['constraints']}
    results=[];dispositions=[];preserved={}
    for group in [l['group'] for l in body['ledgers']]:
        ledger=load_ledger(group);preserved[group]=deepcopy(ledger)
        selected={r['source_pointer']:r for r in body['relations'] if r['ledger_group']==group}
        for i,r in enumerate(ledger['relations']):
            pointer='/relations/'+str(i);chosen=selected.get(pointer)
            if chosen is None:
                reason='cross_period_shape' if 'terms' not in r else 'operands_outside_balance_snapshot_subset'
                dispositions.append({'id':group+'.'+r['id'],'source_pointer':pointer,'source_record':deepcopy(r),
                    'status':'deferred','reason':reason,
                    'next':'Extend context-aware statement/period bindings; preserve diagnostic role and dash/unknown conventions separately.'})
                continue
            terms=deepcopy(chosen['terms'])+[{'coefficient':'-1/1','observation_ref':chosen['target_ref']}]
            keys=[t['observation_ref']['digest'] for t in terms]
            contexts=[observations[k]['context'] for k in keys]
            if any(c!=contexts[0] for c in contexts):raise ValueError('incompatible observation contexts')
            sources={observations[k]['record']['body']['source_ref']['digest'] for k in keys}
            if len(sources)!=1:raise ValueError('cross source relation')
            arithmetic=displayed_residual(terms,values);interval=interval_sum(terms,intervals)
            hypothesis=chosen['measurement_identity']
            if hypothesis is None:local='not_asserted'
            elif interval['status']=='unresolved':local='unresolved'
            elif interval['zero_contained']:local='locally_compatible_only'
            else:local='locally_incompatible'
            results.append({'id':chosen['id'],'displayed':arithmetic,'conditional_residual':interval,
                'measurement_identity':deepcopy(hypothesis),'identity_status':local,'context':contexts[0],
                'normalized_coefficients':{k:rat(v) for k,v in normalized(terms).items()}})
            dispositions.append({'id':group+'.'+r['id'],'source_pointer':pointer,'source_record':deepcopy(r),
                'status':'bound_displayed_relation','reason':None,'next':'Underlying identity needs a separate supported or proposed premise.'})
    return {'profile':PROFILE,'request_sha256':digest(body),'status':'partial_relations',
        'relations':results,'ledger_dispositions':dispositions,'preserved_ledgers':preserved,
        'state_result_sha256':digest(partial),'dependencies':deepcopy(partial['dependencies']),
        'joint_feasibility':'uncomputed','actual_history':'unknown','executable_opening':None,'executed':False}

def verify_result(body,result):
    try:return canonical(evaluate(body))==canonical(result)
    except Exception:return False
