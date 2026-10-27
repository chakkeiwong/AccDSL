"""Exact finite reference: immutable supplied evidence and conservative replay."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location('exact_time', ROOT/'data/accounting-master/exact-information-time-20261026/projection.py')
_time = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_time)
PROFILE = 'FiniteVintageInference/1'

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

def identity(value): return sha256(canonical(value)).hexdigest()
def source_identity(text): return sha256(text.encode()).hexdigest()
def fmt(x): return str(x.numerator)+'/'+str(x.denominator)

class Unresolved(ValueError): pass
class Ineligible(ValueError): pass
class Incompatible(ValueError): pass

def need(condition, reason):
    if not condition: raise ValueError(reason)

def fields(obj, keys, name):
    need(isinstance(obj, dict) and set(obj)==set(keys), name+'_fields')

def rational(value):
    need(isinstance(value,str) and re.fullmatch(r'[0-9]+/[1-9][0-9]*',value), 'nonnegative_exact_rational_required')
    q=Fraction(value);need(fmt(q)==value,'canonical_rational_required');return q

def vector(values, states, name):
    need(isinstance(values,dict) and set(values)==set(states),name+'_state_coverage')
    for v in values.values():
        if v is not None:rational(v)
    if any(v is None for v in values.values()):raise Unresolved(name+'_probability_unknown')
    return {s:rational(values[s]) for s in states}

def validate(request):
    fields(request,['profile','model','actor','cutoff','heads','evidence','sources'],'request')
    need(request['profile']==PROFILE,'request_profile')
    model=request['model']
    fields(model,['profile','states','prior','observation_model','factorization'],'model')
    need(model['profile']=='FinitePersistentTypeModel/1','model_profile')
    states=model['states']
    need(isinstance(states,list) and states and all(isinstance(s,str) and s for s in states) and len(set(states))==len(states),'distinct_named_states')
    need(isinstance(model['observation_model'],str) and model['observation_model'],'observation_model_identity')
    need(model['factorization']=='conditionally_independent_given_type','explicit_factorization_required')
    prior=vector(model['prior'],states,'prior');need(sum(prior.values())==1,'normalized_prior_required')
    actor=request['actor'];need(isinstance(actor,str) and actor,'actor_required')
    cutoff=_time.instant(request['cutoff'])
    heads=request['heads'];records=request['evidence'];sources=request['sources']
    need(isinstance(heads,list) and all(isinstance(h,str) for h in heads) and len(heads)==len(set(heads)),'distinct_heads')
    need(isinstance(records,dict) and isinstance(sources,dict),'evidence_and_sources')
    for h,source in sources.items():need(isinstance(source,str) and source_identity(source)==h,'source_content_mismatch')
    for h,record in records.items():
        need(identity(record)==h,'evidence_content_mismatch')
        fields(record,['profile','slot','information_id','available_at','source_sha256','supersedes','disposition','likelihood'],'record')
        need(record['profile']=='FiniteObservation/1','observation_profile')
        need(isinstance(record['slot'],str) and record['slot'],'slot_required')
        need(isinstance(record['information_id'],str) and record['information_id'],'information_identity_required')
        need(record['source_sha256'] in sources,'source_missing')
        need(record['supersedes'] is None or isinstance(record['supersedes'],str),'supersedes_identity')
        need(isinstance(record['available_at'],dict),'availability_map')
        need(record['disposition'] in ['observation','retraction'],'disposition')
        if record['disposition']=='retraction':need(record['likelihood'] is None,'retraction_has_no_likelihood')
        else:
            need(isinstance(record['likelihood'],dict) and set(record['likelihood'])==set(states),'likelihood_state_coverage')
            for value in record['likelihood'].values():
                if value is not None:rational(value)
    visited=set();slots=set();information_ids=set();factor_values=[]
    for head in heads:
        need(head in records,'head_missing')
        slot=records[head]['slot'];need(slot not in slots,'conflicting_active_slot_heads');slots.add(slot)
        information_id=records[head]['information_id']
        need(information_id not in information_ids,'duplicate_active_information');information_ids.add(information_id)
        h=head;chain=set();child_time=None
        while h is not None:
            need(h not in chain,'replacement_cycle');chain.add(h)
            need(h in records,'replacement_ancestry_missing')
            r=records[h];need(r['slot']==slot,'replacement_slot_mismatch')
            need(r['information_id']==information_id,'replacement_information_mismatch')
            stamp=r['available_at'].get(actor)
            if stamp is None:raise Unresolved('availability_unknown:'+h)
            at=_time.instant(stamp)
            if at>cutoff:raise Ineligible('after_cutoff:'+h)
            need(child_time is None or at<=child_time,'replacement_precedes_parent_availability')
            child_time=at;visited.add(h);h=r['supersedes']
        r=records[head]
        values={s:Fraction(1) for s in states} if r['disposition']=='retraction' else vector(r['likelihood'],states,'likelihood')
        factor_values.append((head,values))
    need(visited==set(records),'unselected_evidence_records')
    need({r['source_sha256'] for r in records.values()}==set(sources),'unselected_source_content')
    return states,prior,factor_values

def calculate(prior,factors,initial_normalizer=Fraction(1)):
    posterior=dict(prior);normalizer=initial_normalizer;trace=[]
    for head,likelihood in factors:
        mass={s:posterior[s]*likelihood[s] for s in posterior};scale=sum(mass.values())
        if not scale:raise Incompatible('zero_normalizer:'+head)
        normalizer*=scale;posterior={s:mass[s]/scale for s in posterior}
        trace.append(dict(head=head,increment=fmt(scale),posterior={s:fmt(q) for s,q in posterior.items()}))
    return posterior,normalizer,trace

def evaluate(request,checkpoint=None):
    """No mutation. A stale valid checkpoint causes prior replay; corrupt ones refuse."""
    try:
        request=deepcopy(request)
        states,prior,factors=validate(request)
        route='from_prior';reason=None;start=0;initial=Fraction(1)
        if checkpoint is not None:
            fields(checkpoint,['profile','request','result'],'checkpoint')
            need(checkpoint['profile']=='FiniteInferenceCheckpoint/1','checkpoint_profile')
            old=checkpoint['request'];verified=evaluate(old)
            need(verified['status']=='complete' and verified==checkpoint['result'],'checkpoint_calculation_mismatch')
            for key in ['model','actor','cutoff']:need(old[key]==request[key],'checkpoint_'+key+'_mismatch')
            oldheads=old['heads']
            if request['heads'][:len(oldheads)]==oldheads:
                route='verified_prefix';start=len(oldheads)
                prior={s:rational(verified['posterior'][s]) for s in states}
                initial=rational(verified['normalizer'])
            else:
                route='replay_prior';reason='active_evidence_prefix_changed'
        posterior,normalizer,trace=calculate(prior,factors[start:],initial)
        return dict(profile=PROFILE,status='complete',request_sha256=identity(request),model_sha256=identity(request['model']),actor=request['actor'],cutoff=request['cutoff'],heads=list(request['heads']),posterior={s:fmt(q) for s,q in posterior.items()},normalizer=fmt(normalizer),route=route,replay_reason=reason,reused_prefix_count=start,executed_suffix=trace,source_admission=False,real_company_likelihood_validated=False)
    except Unresolved as e:return dict(profile=PROFILE,status='unresolved',reason=str(e))
    except Ineligible as e:return dict(profile=PROFILE,status='ineligible',reason=str(e))
    except Incompatible as e:return dict(profile=PROFILE,status='incompatible',reason=str(e))
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as e:return dict(profile=PROFILE,status='invalid',reason=str(e))

def make_checkpoint(request):
    result=evaluate(request)
    need(result['status']=='complete','checkpoint_requires_complete_result')
    return dict(profile='FiniteInferenceCheckpoint/1',request=deepcopy(request),result=result)
