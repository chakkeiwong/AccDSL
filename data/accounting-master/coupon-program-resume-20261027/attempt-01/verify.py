"""Compare selected chunked resumes with full independent financial histories."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,resource,subprocess,sys,time,traceback
import resume as r
s=r.s; prior=r.prior
H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()

def verify(out,source,sid,sel,ident,prefix,pid,plan,accepted,status):
    assert out['profile']==r.CHECKPOINT and out['status']==status
    for flag in s.FLAGS:assert out[flag] is False
    assert out['source_carry_sha256']==sid==s.identity(source)
    assert out['selection_sha256']==ident==s.identity(sel)
    assert out['prefix_sha256']==pid==s.identity(prefix)
    assert out['plan_sha256']==s.identity(plan)
    assert out['opening_sha256']==s.identity(sel['opening'])
    assert out['interpretation']=='selected_same_period_resume_no_durable_commit'
    assert out['cursor']==accepted and out['remaining']==plan['suffix'][accepted:]
    assert out['origin_archive']==source['result']['history_archive']
    before_count=len(plan['prefix_instructions'])
    instructions=plan['prefix_instructions']+plan['suffix'][:accepted]
    current,trace=prior.expected(source,instructions)
    assert out['current']==current and len(out['trace'])==accepted
    commands=s.program(sel,plan['suffix'])['commands']
    for i,(got,want) in enumerate(zip(out['trace'],trace[before_count:])):
        assert got['index']==i and got['command']==commands[i]
        assert got['before_sha256']==s.identity(want['before'])
        assert got['after_sha256']==s.identity(want['after'])
        assert got['request']==s.rt.call(want['before'],sel['registry'],commands[i])
        assert got['proposal']['status']=='proposed'
        for key in ('after','journal','flows'):assert got['proposal']['transition'][key]==want[key]
    assert out['trace_bytes']==2+sum(len(s.rt.core.canonical(v)) for v in out['trace'])
    assert out['trace_bytes']<=plan['trace_limit']
    body=s.program(sel,instructions)
    assert out['report']==prior.oracle.report_oracle(body,current)
    if status in ('complete','paused_budget'):
        assert out['stop'] is None
        assert (accepted==len(plan['suffix']))==(status=='complete')
    else:
        stop=out['stop'];assert stop['index']==accepted and stop['command']==commands[accepted]
        assert stop['before_sha256']==s.identity(current)
        if status=='refused':
            assert stop['proposal']['status']=='invalid'
            assert stop['after_sha256']==s.identity(current)
            t=stop['proposal'].get('transition',stop['proposal'])
            assert not {'after','journal','flows'}&set(t)
        else:
            assert status=='resource_limited' and stop['reason']=='trace_size_limit'
            assert out['trace_bytes']+stop['candidate_bytes']>plan['trace_limit']
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False)
    start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];pins={};summary={'status':'FAIL','error':'unfinished'}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+'\n')
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def reject(n,fn):
        try:fn()
        except (AssertionError,ValueError,KeyError,TypeError) as e:
            controls.append(dict(name=n,reason=str(e)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old=prior.prior.prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'coupon-continuation-scope-20261027/attempt-01'
        ck('upstream_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():
            ck('source:'+n,digest(R/n)==v);pins[n]=v
        modules=[Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(R)]
        for p in modules+list(B.glob('*.json'))+[H/'resume.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-coupon-program-resume-20261027.md']:
            pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('resume.py','verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        sources=[v for v in json.loads((H.parent/'coupon-carry-20261027/attempt-01/cases.json').read_text()) if ':R6:draw:' in v['case']]
        prefix_instructions=[dict(id='prefix-first',date='2028-01-02',amount='1/1')]
        good=[dict(id='suffix-first',date='2028-01-04',amount='1/4'),dict(id='suffix-second',date='2028-01-05',amount='1/2'),dict(id='suffix-third',date='2028-01-06',amount='1/1')]
        suffixes={'success':good,'unaffordable':[good[0],{**good[1],'amount':'5/1'},good[2]],
            'duplicate':[good[0],{**good[1],'id':'suffix-first'},good[2]],
            'backward':[good[0],{**good[1],'date':'2028-01-03'},good[2]]}
        save('inputs-and-expectations.json',dict(origins=[dict(case=x['case'],sha256=s.identity(x)) for x in sources],prefix=prefix_instructions,suffixes=suffixes,chunks=[1,2,64],success_accepted=3,refusal_accepted=1,trace_limit=8388608))
        prior.prior.prior.native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        early=None
        for source in sources:
            sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel)
            prefix=s.run(source,sid,sel,ident,prefix_instructions);pid=s.identity(prefix)
            for name,suffix in suffixes.items():
                plan=r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,suffix);plan_id=s.identity(plan)
                target_count=3 if name=='success' else 1;target_status='complete' if name=='success' else 'refused'
                uninterrupted=s.run(source,sid,sel,ident,prefix_instructions+suffix)
                finals=[];chunk_records=[]
                # The first all-versus-one comparison is the early diagnostic.
                for chunk in (64,1,2):
                    snapshots=[];out=None
                    for step in range(4):
                        out=r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,chunk,out,s.identity(out) if out is not None else None)
                        count=min(target_count,(step+1)*chunk)
                        status=target_status if (name=='success' and count==3) or (name!='success' and (step+1)*chunk>1) else 'paused_budget'
                        ck(source['case']+':'+name+':chunk'+str(chunk)+':'+str(step),verify(out,source,sid,sel,ident,prefix,pid,plan,count,status))
                        snapshots.append(cp(out))
                        if out['status']!='paused_budget':break
                    else:raise AssertionError('no_bounded_terminal_result')
                    ck('terminal_status',out['status']==target_status and out['cursor']==target_count)
                    ck('uninterrupted_current',out['current']==uninterrupted['execution']['current'])
                    ck('uninterrupted_report',out['report']==uninterrupted['report'])
                    for a,b in zip(out['trace'],uninterrupted['execution']['trace'][len(prefix_instructions):]):
                        ck('uninterrupted_transition',a['proposal']==b['result'] and a['request']==b['request'])
                    if target_status=='refused':
                        ck('same_refusal',out['stop']['proposal']==uninterrupted['execution']['stop']['result'])
                    finals.append(out);chunk_records.append(dict(chunk=chunk,checkpoints=snapshots))
                    if chunk==1 and early is None:
                        ck('early_all_and_one_identical',finals[0]==finals[1]);early=True
                        save('early-diagnostic.json',dict(status='PASS',case=source['case']+':'+name,checkpoint_sha256=s.identity(out)))
                        print(json.dumps(dict(progress='early_complete_checkpoint_match',case=source['case'])),flush=True)
                ck('all_chunk_sizes_identical',finals[0]==finals[1]==finals[2])
                cases.append(dict(case=source['case']+':'+name,source_carry_sha256=sid,selection_sha256=ident,prefix_sha256=pid,plan=plan,uninterrupted=uninterrupted,chunk_runs=chunk_records))
        source=sources[0];sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel)
        prefix=s.run(source,sid,sel,ident,prefix_instructions);pid=s.identity(prefix)
        plan=r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,good);plan_id=s.identity(plan)
        paused=r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,1)
        complete=r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,64)
        ck('terminal_complete_unchanged',r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,1,complete,s.identity(complete))==complete)
        failed_plan=r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,suffixes['unaffordable']);fid=s.identity(failed_plan)
        refused=r.run(source,sid,sel,ident,prefix,pid,failed_plan,fid,64)
        ck('terminal_refusal_unchanged',r.run(source,sid,sel,ident,prefix,pid,failed_plan,fid,1,refused,s.identity(refused))==refused)
        # Exact first-row budget permits one row, then must stop even across chunks.
        boundary=paused['trace_bytes'];limited=r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,good,boundary);lid=s.identity(limited)
        once=r.run(source,sid,sel,ident,prefix,pid,limited,lid,1)
        limited_out=r.run(source,sid,sel,ident,prefix,pid,limited,lid,1,once,s.identity(once))
        limited_all=r.run(source,sid,sel,ident,prefix,pid,limited,lid,64)
        ck('trace_budget_accumulates',limited_out==limited_all and verify(limited_out,source,sid,sel,ident,prefix,pid,limited,1,'resource_limited'))
        ck('terminal_limit_unchanged',r.run(source,sid,sel,ident,prefix,pid,limited,lid,1,limited_out,s.identity(limited_out))==limited_out)
        save('trace-limit-control.json',dict(limit=boundary,paused=once,result=limited_out))
        controls.append(dict(name='cumulative_trace_boundary',accepted=1,limit=boundary))
        for name,change in [('skip_cursor',lambda z:z.update(cursor=2)),('drop_trace',lambda z:z.update(trace=[])),('reset_trace_budget',lambda z:z.update(trace_bytes=2)),('drop_history',lambda z:z['origin_archive'].update(refusal=None)),('wrong_report',lambda z:z['report']['cash_flows'].update(closing_cash='0/1')),('wrong_opening',lambda z:z.update(opening_sha256=pid)),('false_admission',lambda z:z.update(accounting_admission=True)),('mark_complete',lambda z:z.update(status='complete'))]:
            bad=cp(paused);change(bad)
            reject(name,lambda z=bad:r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,1,z,s.identity(z)))
        bad=cp(refused);bad['cursor']=2
        reject('skip_refused_command',lambda:r.run(source,sid,sel,ident,prefix,pid,failed_plan,fid,1,bad,s.identity(bad)))
        changed=r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,[good[0],{**good[1],'amount':'1/4'},good[2]])
        reject('changed_suffix_with_old_checkpoint',lambda:r.run(source,sid,sel,ident,prefix,pid,changed,s.identity(changed),1,paused,s.identity(paused)))
        reject('stale_checkpoint_id',lambda:r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,1,paused,'0'*64))
        bad_source=cp(source);bad_source['result']['history_archive']['refusal']=None
        reject('stale_source',lambda:r.run(bad_source,sid,sel,ident,prefix,pid,plan,plan_id,1))
        bad_sel=cp(sel);bad_sel['opening']['memory']['used']=False
        reject('changed_selection',lambda:r.run(source,sid,bad_sel,s.identity(bad_sel),prefix,pid,plan,plan_id,1))
        bad_prefix=cp(prefix);bad_prefix['execution']['trace'][0]['result']['call_sha256']='0'*64
        reject('reidentified_corrupt_prefix_metadata',lambda:r.make_plan(source,sid,sel,ident,prefix_instructions,bad_prefix,s.identity(bad_prefix),good))
        too_many=[dict(id='cap-'+str(i),date='2028-01-04',amount='1/100') for i in range(65)]
        reject('65_command_plan',lambda:r.make_plan(source,sid,sel,ident,prefix_instructions,prefix,pid,too_many))
        reject('zero_chunk',lambda:r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,0))
        reject('boolean_chunk',lambda:r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,True))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),chunk_comparisons=len(cases)*3,assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='selected bounded same-period coupon resume; no durable commit')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        prior.prior.prior.native.Engine.apply=old
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact conformance',data_version='source-lock.json',plan='docs/plans/accounting-coupon-program-resume-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
