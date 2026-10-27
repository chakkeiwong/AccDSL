"""Pure member-boundary recovery and work-publication exchanges; no storage I/O."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'company-family-20261023'))
import family

CP='CompanyFamilyCheckpointDraft/1'
WORLD='CompanyFamilyWorkWorldDraft/1'
REQUEST='CompanyFamilyResumeRequestDraft/1'
def exact_fields(value,keys):
    if not isinstance(value,dict) or set(value)!=set(keys): raise ValueError('closed record fields')
def natural(value):
    if type(value) is not int or value<0: raise ValueError('nonnegative integer required')
def nonempty(value):
    if not isinstance(value,str) or not value.strip(): raise ValueError('nonempty identity required')
def hash_value(value):
    if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value): raise ValueError('digest required')
def initial(body,source,engine_sha256):
    family.validate(body); hash_value(engine_sha256)
    if sha256(source).hexdigest()!=body['common']['source_sha256']: raise ValueError('source identity')
    return {'profile':CP,'family_sha256':family.digest(body),'source_sha256':sha256(source).hexdigest(),
            'engine_sha256':engine_sha256,'next_index':0,'completed':[]}
def entry(member,source,engine):
    run=engine.wire(engine.execute(deepcopy(member['path']),source))
    return {'id':member['id'],'path_sha256':family.digest(member['path']),
            'result_sha256':family.digest(run),'status':run['status'],'result':run}
def validate_checkpoint(body,source,engine_sha256,checkpoint,engine):
    expected=initial(body,source,engine_sha256)
    exact_fields(checkpoint,expected)
    for key in ['profile','family_sha256','source_sha256','engine_sha256']:
        if checkpoint[key]!=expected[key]: raise ValueError('checkpoint dependency changed: '+key)
    natural(checkpoint['next_index'])
    if not isinstance(checkpoint['completed'],list) or checkpoint['next_index']!=len(checkpoint['completed']):
        raise ValueError('checkpoint prefix length')
    if checkpoint['next_index']>len(body['members']): raise ValueError('checkpoint exceeds member count')
    for i,saved in enumerate(checkpoint['completed']):
        if family.digest(entry(body['members'][i],source,engine))!=family.digest(saved):
            raise ValueError('checkpoint member does not replay: '+str(i))
    return checkpoint['next_index']
def final_result(body,source,completed):
    status=('empty_authored_family' if not completed else
            'evaluated_all_members' if all(m['status']=='complete_conditional' for m in completed) else
            'evaluated_with_incomplete_members')
    return dict(family.FLAGS,profile=family.PROFILE,status=status,family_sha256=family.digest(body),
                source_sha256=sha256(source).hexdigest(),members=deepcopy(completed),
                coverage='authored_members_only',weighting='unweighted')
def resume(body,source,engine_sha256,checkpoint,budget,engine):
    try:
        natural(budget)
        count=validate_checkpoint(body,source,engine_sha256,checkpoint,engine)
        out=deepcopy(checkpoint); end=min(count+budget,len(body['members']))
        for member in body['members'][count:end]: out['completed'].append(entry(member,source,engine))
        out['next_index']=end; complete=end==len(body['members'])
        return {'status':'work_complete' if complete else 'work_suspended','checkpoint':out,
                'validation_replayed_members':count,'newly_evaluated_members':end-count,
                'family_result':final_result(body,source,out['completed']) if complete else None,
                'physical_durability_established':False,'accounting_commit':False}
    except Exception as exc:
        return {'status':'invalid','reason':'resume_contract','detail':type(exc).__name__+':'+str(exc).splitlines()[0][:240],
                'checkpoint':None,'family_result':None,'physical_durability_established':False,'accounting_commit':False}
def new_world(owner,checkpoint):
    nonempty(owner)
    return {'profile':WORLD,'owner':owner,'generation':0,'checkpoint':deepcopy(checkpoint),'decisions':[]}
def request(ident,world,budget):
    return {'profile':REQUEST,'id':ident,'owner':world['owner'],'expected_generation':world['generation'],
            'expected_checkpoint_sha256':family.digest(world['checkpoint']),'budget':budget,
            'family_sha256':world['checkpoint']['family_sha256'],'source_sha256':world['checkpoint']['source_sha256'],
            'engine_sha256':world['checkpoint']['engine_sha256']}
def validate_request(value):
    exact_fields(value,['profile','id','owner','expected_generation','expected_checkpoint_sha256','budget','family_sha256','source_sha256','engine_sha256'])
    if value['profile']!=REQUEST: raise ValueError('request profile')
    nonempty(value['id']); nonempty(value['owner']); natural(value['expected_generation']); natural(value['budget'])
    for key in ['expected_checkpoint_sha256','family_sha256','source_sha256','engine_sha256']: hash_value(value[key])
def validate_world(body,source,engine_sha256,world,engine):
    exact_fields(world,['profile','owner','generation','checkpoint','decisions'])
    if world['profile']!=WORLD: raise ValueError('world profile')
    nonempty(world['owner']); natural(world['generation'])
    if not isinstance(world['decisions'],list) or world['generation']!=len(world['decisions']): raise ValueError('atomic world generation')
    current=initial(body,source,engine_sha256); ids=set()
    for generation,decision in enumerate(world['decisions']):
        exact_fields(decision,['request','response']); req=decision['request']; validate_request(req)
        if req['id'] in ids: raise ValueError('duplicate decision identity')
        ids.add(req['id'])
        expected=request(req['id'],{'owner':world['owner'],'generation':generation,'checkpoint':current},req['budget'])
        if family.digest(expected)!=family.digest(req): raise ValueError('decision chain request')
        work=resume(body,source,engine_sha256,current,req['budget'],engine)
        if work['status']=='invalid': raise ValueError('decision work invalid')
        response={'status':'published','generation':generation+1,'request_sha256':family.digest(req),
                  'opening_checkpoint_sha256':family.digest(current),'work':work}
        if family.digest(response)!=family.digest(decision['response']): raise ValueError('decision response replay')
        current=work['checkpoint']
    if family.digest(current)!=family.digest(world['checkpoint']): raise ValueError('partial or false publication')
    validate_checkpoint(body,source,engine_sha256,current,engine)
def publish(body,source,engine_sha256,world,req,engine):
    """Return a new immutable world; the caller models its atomic publication."""
    before=deepcopy(world)
    try:
        validate_world(body,source,engine_sha256,world,engine); validate_request(req)
        if req['owner']!=world['owner']: raise ValueError('work owner mismatch')
        prior=[d for d in world['decisions'] if d['request']['id']==req['id']]
        if prior:
            if family.digest(prior[0]['request'])!=family.digest(req):
                return {'status':'identity_conflict','world':before,'mutated':False}
            return {'status':'replayed','response':deepcopy(prior[0]['response']),'world':before,'mutated':False}
        expected=request(req['id'],world,req['budget'])
        if family.digest(expected)!=family.digest(req): return {'status':'stale_or_changed_request','world':before,'mutated':False}
        work=resume(body,source,engine_sha256,world['checkpoint'],req['budget'],engine)
        if work['status']=='invalid': return {'status':'invalid','reason':'work_refused','work':work,'world':before,'mutated':False}
        response={'status':'published','generation':world['generation']+1,'request_sha256':family.digest(req),
                  'opening_checkpoint_sha256':family.digest(world['checkpoint']),'work':work}
        after=deepcopy(world); after['generation']+=1; after['checkpoint']=deepcopy(work['checkpoint'])
        after['decisions'].append({'request':deepcopy(req),'response':deepcopy(response)})
        return {'status':'published','response':response,'world':after,'mutated':True}
    except Exception as exc:
        return {'status':'invalid','reason':'work_publication','detail':type(exc).__name__+':'+str(exc).splitlines()[0][:240],
                'world':before,'mutated':False}
