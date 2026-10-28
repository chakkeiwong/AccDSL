"""Explicit scope supplement; it cannot certify actual company completeness."""
from copy import deepcopy
from fractions import Fraction as Q
from quotient import Refusal, check, digest, require
from paths import enumerate_paths

FIELDS={'profile','model_sha256','represented','excluded','unresolved_candidates','source_premise'}
def evaluate(model,partition,policy,scenarios,scope,max_nodes=1000):
    require(type(scope) is dict and set(scope)==FIELDS,'scope_fields')
    require(scope['profile']=='AuthoredFiniteScope/1','scope_profile')
    require(scope['model_sha256']==digest(model),'scope_model_mismatch')
    for field in ['represented','excluded','unresolved_candidates']:
        value=scope[field]
        require(type(value) is list and all(type(x) is str and x for x in value),'scope_list')
        require(len(value)==len(set(value)),'duplicate_scope_entry')
    require(bool(scope['represented']),'represented_scope_required')
    require(not(set(scope['represented'])&set(scope['excluded'])),'scope_overlap')
    require(type(scope['source_premise']) is str and bool(scope['source_premise']),'scope_source')
    cert=check(model,partition)
    require(cert['status']=='accepted','partition_not_accepted')
    paths=enumerate_paths(model,scenarios,policy,max_nodes=max_nodes)
    dep=dict(model=model,partition=partition,policy=policy,scenarios=scenarios,scope=scope,max_nodes=max_nodes)
    result=dict(status=paths['status'],bindings={k:digest(v) for k,v in dep.items()},
        scope=deepcopy(scope),traversal=paths,source_admission=False,real_population_complete=False,
        mechanism_meanings_verified=False,unresolved_candidates_preserved=True,probabilities_inferred=False,
        finite_cash_range=None,finite_unpaid_range=None,closure='conditional_on_supplied_model_only')
    if paths['status']=='exact':
        histories=[x['history'] for x in paths['paths']]
        cash=[Q(h[-1]['current_output']['cash']) for h in histories]
        result['finite_cash_range']=[str(min(cash)),str(max(cash))]
        if 'unpaid' in model['requested_outputs']['step']:
            unpaid=[Q(h[-1]['output']['unpaid']) for h in histories]
            result['finite_unpaid_range']=[str(min(unpaid)),str(max(unpaid))]
    return result

def reuse(saved,*args,**kwargs):
    fresh=evaluate(*args,**kwargs)
    require(saved==fresh,'stale_scope_result')
    return deepcopy(fresh)
