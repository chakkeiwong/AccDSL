"""Deterministic recovery exchanges, with immutable prior-result comparator."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import importlib.util,json,os,platform,subprocess,sys,time
from recovery import HERE,initial,resume,new_world,request,publish,validate_world,family

ROOT=HERE.parents[2]; REL=HERE.relative_to(ROOT).as_posix()
def context():
    p=HERE.parent/'company-family-20261023'
    spec=importlib.util.spec_from_file_location('recovery_family_fixtures',p/'verify.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    body,_,source,engine=module.fixtures()
    expected=json.loads((p/'result.json').read_text())
    locks=json.loads((p/'baseline.json').read_text())
    method={n:h for n,h in locks.items() if n.endswith('.py')}
    method[str((p/'family.py').relative_to(ROOT))]=sha256((p/'family.py').read_bytes()).hexdigest()
    method[str((HERE/'recovery.py').relative_to(ROOT))]=sha256((HERE/'recovery.py').read_bytes()).hexdigest()
    for n,h in method.items(): assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    return body,source,engine,expected,method
def protected():
    base=json.loads((HERE.parent/'company-expressions-20261023/baseline.json').read_text())
    for folder in ['company-expressions-20261023','company-family-20261023']:
        for p in (HERE.parent/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and 'control-before' not in p.parts:
                base[str(p.relative_to(ROOT))]=sha256(p.read_bytes()).hexdigest()
    return base
def conformance(smoke=False):
    body,source,engine,expected,method=context(); engine_hash=family.digest(method)
    checkpoint=initial(body,source,engine_hash); original=deepcopy(body); checks=[]; witnesses={}
    def check(name,value): checks.append({'name':name,'passed':bool(value)})
    first=resume(body,source,engine_hash,checkpoint,2,engine)
    final=resume(body,source,engine_hash,first['checkpoint'],10,engine)
    check('partial_budget_stops_between_members',first['status']=='work_suspended' and first['checkpoint']['next_index']==2)
    check('completed_result_matches_protected_family',family.digest(final['family_result'])==family.digest(expected))
    check('separate_validation_and_new_work_counts',final['validation_replayed_members']==2 and final['newly_evaluated_members']==4)
    check('input_and_checkpoint_immutable',body==original and checkpoint['completed']==[])
    check('work_complete_does_not_mean_accounting_complete',final['status']=='work_complete' and final['family_result']['status']=='evaluated_with_incomplete_members')
    if smoke: return {'passed':all(c['passed'] for c in checks),'checks':checks},body,method,final
    splits={}
    for budget in range(7):
        a=resume(body,source,engine_hash,checkpoint,budget,engine)
        b=resume(body,source,engine_hash,a['checkpoint'],6-budget,engine)
        check('split_result_'+str(budget),family.digest(b['family_result'])==family.digest(expected))
        check('split_count_'+str(budget),a['newly_evaluated_members']+b['newly_evaluated_members']==6)
        splits[str(budget)]={'first_status':a['status'],'first_new':a['newly_evaluated_members'],'second_new':b['newly_evaluated_members'],'result_sha256':family.digest(b['family_result'])}
    paused=resume(body,source,engine_hash,checkpoint,5,engine)
    check('partial_accounting_members_are_finished_work',paused['checkpoint']['next_index']==5 and [m['status'] for m in paused['checkpoint']['completed']].count('partial')==2)
    remaining=resume(body,source,engine_hash,paused['checkpoint'],1,engine)
    check('only_remaining_member_newly_evaluated',remaining['newly_evaluated_members']==1 and remaining['validation_replayed_members']==5)
    check('repeat_complete_budget_zero',family.digest(resume(body,source,engine_hash,final['checkpoint'],0,engine)['family_result'])==family.digest(expected))
    for bad in [True,False,-1,1.0,'1',None]:
        check('invalid_budget_'+repr(bad),resume(body,source,engine_hash,checkpoint,bad,engine)['status']=='invalid')
    def bad_checkpoint(name,edit):
        cp=deepcopy(first['checkpoint']); edit(cp); r=resume(body,source,engine_hash,cp,1,engine)
        witnesses[name]=r; check(name,r['status']=='invalid')
    bad_checkpoint('false_index',lambda c:c.__setitem__('next_index',True))
    bad_checkpoint('missing_prefix_member',lambda c:c['completed'].pop())
    bad_checkpoint('reordered_prefix',lambda c:c['completed'].reverse())
    bad_checkpoint('duplicate_prefix_member',lambda c:c['completed'].__setitem__(1,deepcopy(c['completed'][0])))
    bad_checkpoint('changed_family_digest',lambda c:c.__setitem__('family_sha256','f'*64))
    bad_checkpoint('changed_engine_digest',lambda c:c.__setitem__('engine_sha256','f'*64))
    bad_checkpoint('unknown_checkpoint_field',lambda c:c.__setitem__('probability',0.5))
    def forge(c):
        m=c['completed'][0]; m['result']['years'][0]['report']['lines']['cash']['value']='0/1'; m['result_sha256']=family.digest(m['result'])
    bad_checkpoint('rehashed_false_prefix',forge)
    changed=deepcopy(body); changed['name']='Changed model'
    check('changed_model_not_resume',resume(changed,source,engine_hash,first['checkpoint'],1,engine)['status']=='invalid')
    check('changed_source_not_resume',resume(body,source+b' ',engine_hash,first['checkpoint'],1,engine)['status']=='invalid')
    check('changed_method_not_resume',resume(body,source,'f'*64,first['checkpoint'],1,engine)['status']=='invalid')
    empty=deepcopy(body); empty['members']=[]; ecp=initial(empty,source,engine_hash)
    er=resume(empty,source,engine_hash,ecp,0,engine)
    check('empty_family_work_complete',er['status']=='work_complete' and er['family_result']['status']=='empty_authored_family')
    world=new_world('northstar-work',checkpoint); req=request('resume-1',world,2)
    published=publish(body,source,engine_hash,world,req,engine)
    check('publication_atomic_generation',published['status']=='published' and published['world']['generation']==1 and len(published['world']['decisions'])==1)
    check('publication_keeps_old_world',world==new_world('northstar-work',checkpoint))
    no_commit=publish(body,source,engine_hash,world,req,engine)
    check('lost_ack_no_commit_world',family.digest(no_commit)==family.digest(published))
    committed_retry=publish(body,source,engine_hash,published['world'],req,engine)
    check('lost_ack_committed_world',committed_retry['status']=='replayed' and not committed_retry['mutated'] and family.digest(committed_retry['response'])==family.digest(published['response']))
    check('retry_does_not_duplicate_work',family.digest(committed_retry['world'])==family.digest(published['world']))
    conflict=deepcopy(req); conflict['budget']=3
    refused=publish(body,source,engine_hash,published['world'],conflict,engine)
    check('changed_request_identity_conflicts',refused['status']=='identity_conflict' and refused['world']==published['world'])
    stale=deepcopy(req); stale['id']='new-id-stale-head'
    refused=publish(body,source,engine_hash,published['world'],stale,engine)
    check('new_request_stale_head_refused',refused['status']=='stale_or_changed_request' and not refused['mutated'])
    second_request=request('resume-2',published['world'],4)
    second=publish(body,source,engine_hash,published['world'],second_request,engine)
    check('second_publication_matches_final_family',family.digest(second['response']['work']['family_result'])==family.digest(expected))
    old_retry=publish(body,source,engine_hash,second['world'],req,engine)
    check('exact_retry_before_current_head_check',old_retry['status']=='replayed' and family.digest(old_retry['response'])==family.digest(published['response']))
    check('later_world_unchanged_on_old_retry',family.digest(old_retry['world'])==family.digest(second['world']))
    for name,mutate in [
        ('generation_without_decision',lambda w:w.__setitem__('generation',2)),
        ('checkpoint_without_decision',lambda w:w.__setitem__('checkpoint',deepcopy(final['checkpoint']))),
        ('decision_without_checkpoint',lambda w:w.__setitem__('checkpoint',deepcopy(checkpoint))),
        ('missing_published_decision',lambda w:w['decisions'].clear())]:
        corrupt=deepcopy(published['world']); mutate(corrupt)
        response=publish(body,source,engine_hash,corrupt,req,engine)
        check(name,response['status']=='invalid' and response['world']==corrupt and not response['mutated'])
    bad=deepcopy(req); bad['owner']='other-work'
    response=publish(body,source,engine_hash,world,bad,engine)
    check('owner_mismatch_refused',response['status']=='invalid' and response['world']==world)
    bad=deepcopy(req); bad['budget']=True
    response=publish(body,source,engine_hash,world,bad,engine)
    check('boolean_request_budget_refused',response['status']=='invalid' and response['world']==world)
    check('no_physical_durability_claim',final['physical_durability_established'] is False and final['accounting_commit'] is False)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'split_summaries':splits,'adverse':witnesses,
            'publication_example':{'initial':world,'first_request':req,'first_publication':published,'second_request':second_request,'second_publication':second}},body,method,final

def main():
    flags=set(sys.argv[1:]); assert flags <= {'--record','--smoke'} and len(flags)<=1
    record='--record' in flags; smoke='--smoke' in flags
    assert not record or not (HERE/'manifest.json').exists()
    baseline=json.loads((HERE/'baseline.json').read_text()) if (HERE/'baseline.json').exists() else protected()
    for n,h in baseline.items(): assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    started=datetime.now(timezone.utc).isoformat(); start=time.perf_counter()
    evidence,body,method,final=conformance(smoke); failed=[c['name'] for c in evidence['checks'] if not c['passed']]
    for n,h in baseline.items(): assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    if failed:
        dest=HERE/('failure-'+datetime.now(timezone.utc).strftime('%H%M%S')); dest.mkdir()
        for p in HERE.glob('*.py'): (dest/p.name).write_bytes(p.read_bytes())
        (dest/'failure.json').write_text(json.dumps(evidence,indent=2)+'\n')
    if record and not failed:
        for name,value in {'checks.json':evidence,'fixture.json':body,'method-lock.json':method,'final-result.json':final,'baseline.json':baseline}.items():
            (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
        m={'started_utc':started,'wall_seconds':time.perf_counter()-start,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+REL+'/verify.py --record','environment':'Python '+platform.python_version()+'; protected exact company engine','cpu_gpu':'CPU only; GPU intentionally hidden by CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),'random_seeds':'N/A: deterministic','data_version':baseline,'plan':'docs/plans/accounting-company-recovery-20261023.md','result':REL+'/result.md','files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    elif not smoke and not failed and (HERE/'manifest.json').exists():
        for name,value in [('checks.json',evidence),('fixture.json',body),('method-lock.json',method),('final-result.json',final)]:
            assert family.digest(json.loads((HERE/name).read_text()))==family.digest(value),name
        for n,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'protected_files':len(baseline),'recorded':record and not failed,'smoke':smoke,'wall_seconds':round(time.perf_counter()-start,3)}))
    return bool(failed)
if __name__=='__main__': raise SystemExit(main())
