"""Finite authored Bayes models with explicit conflict and proposed repair."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def exact(value):
    if not isinstance(value,str):raise ValueError('exact_rational_required')
    try:return Q(value)
    except (ValueError,ZeroDivisionError):raise ValueError('exact_rational_required')

def update(model):
    if set(model)!={'id','prior','likelihood','provenance'}:raise ValueError('model_fields')
    if not isinstance(model['id'],str) or not model['id']:raise ValueError('model_identity')
    if not isinstance(model['provenance'],str) or not model['provenance'].strip():raise ValueError('model_provenance')
    prior=model['prior'];likelihood=model['likelihood']
    if not isinstance(prior,dict) or not prior or not isinstance(likelihood,dict) or set(prior)!=set(likelihood):raise ValueError('same_type_support_required')
    p={k:exact(v) for k,v in prior.items()}
    if any(v<0 for v in p.values()):raise ValueError('negative_prior')
    if sum(p.values())!=1:raise ValueError('prior_not_one')
    known={k:exact(v) for k,v in likelihood.items() if v is not None}
    if any(not 0<=v<=1 for v in known.values()):raise ValueError('likelihood_range')
    result=dict(model=deepcopy(model),model_sha256=digest(model),type_support=list(prior),source_admission=False,posterior=None)
    if len(known)!=len(prior):return {**result,'status':'unresolved','reason':'likelihood_unknown','normalizer':None}
    unnormalized={k:p[k]*known[k] for k in p};z=sum(unnormalized.values())
    result.update(normalizer=str(z),unnormalized={k:str(v) for k,v in unnormalized.items()})
    if z==0:return {**result,'status':'conflict','reason':'zero_probability_evidence','repair_required':True}
    return {**result,'status':'conditional_posterior','posterior':{k:str(v/z) for k,v in unnormalized.items()},'repair_required':False}

def propose_repair(conflict,proposal):
    if conflict!=update(conflict['model']):raise ValueError('changed_original_result')
    if conflict['status']!='conflict':raise ValueError('original_conflict_required')
    if set(proposal)!={'supersedes','reason','model'}:raise ValueError('repair_fields')
    if proposal['supersedes']!=conflict['model_sha256']:raise ValueError('repair_target')
    if not isinstance(proposal['reason'],str) or not proposal['reason'].strip():raise ValueError('repair_reason')
    if proposal['model']['id']==conflict['model']['id']:raise ValueError('new_model_identity_required')
    revised=update(proposal['model'])
    return dict(status='proposed_model_repair',original=deepcopy(conflict),proposal=deepcopy(proposal),candidate=revised,
                automatic_replacement=False,source_admission=False,actual_model_correct=False)

def conditional_strata(prior,values):
    if set(prior)!=set(values):raise ValueError('strata_support_mismatch')
    masses={k:exact(v) for k,v in prior.items()}
    if any(v<0 for v in masses.values()) or sum(masses.values())!=1:raise ValueError('strata_measure')
    return dict(status='supplied_finite_type_representation',rows=[dict(type=k,mass=str(masses[k]),conditional_value=values[k]) for k in prior],
                type_coverage=list(prior),within_type_scope='One deterministic value per supplied type only',
                smc_integration=False,real_history_coverage=False)
