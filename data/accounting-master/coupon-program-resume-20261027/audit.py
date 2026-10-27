"""Bounded supplementary controls, preserving the successful resume evidence."""
from pathlib import Path
from copy import deepcopy as cp
from datetime import datetime,timezone
from hashlib import sha256
import json,os,platform,subprocess,sys,time,traceback,resource
import verify as v
r=v.r;s=r.s;H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));a=sys.argv[1];assert a in ('01','02','03')
    A=H/('audit-attempt-'+a);A.mkdir(exist_ok=False);t=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];pins={};records=[];summary={'status':'FAIL','error':'unfinished'}
    def save(n,x):(A/n).write_text(json.dumps(x,indent=2)+'\n')
    def ck(n,x):
        checks.append(dict(name=n,passed=bool(x)))
        if not x:raise AssertionError(n)
    def reject(n,fn):
        try:fn()
        except (AssertionError,ValueError,KeyError,TypeError) as e:controls.append(dict(name=n,reason=str(e)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old=v.prior.prior.prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1');B=H/'attempt-02'
        ck('successful_baseline',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,h in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==h);pins[n]=h
        for p in list(B.glob('*.json'))+[H/'audit.py',H/'post-run-audit-plan.md',H/'repair-note.md']:pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        cases=json.loads((B/'cases.json').read_text());case=cases[0];plan=case['plan'];plan_id=s.identity(plan)
        source=next(x for x in json.loads((H.parent/'coupon-carry-20261027/attempt-01/cases.json').read_text()) if x['case']==case['case'].removesuffix(':success'))
        sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel);pi=plan['prefix_instructions']
        v.prior.prior.prior.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        prefix=s.run(source,sid,sel,ident,pi);pid=s.identity(prefix)
        ck('identified_prefix',pid==case['prefix_sha256'])
        paused=next(x for x in case['chunk_runs'] if x['chunk']==1)['checkpoints'][0]
        before={k:s.identity(x) for k,x in dict(source=source,selection=sel,prefix=prefix,plan=plan,checkpoint=paused).items()}
        exact=paused['trace_bytes']
        for limit,count,status in [(exact-1,0,'resource_limited'),(exact,1,'resource_limited')]:
            lp=r.make_plan(source,sid,sel,ident,pi,prefix,pid,plan['suffix'],limit);lid=s.identity(lp)
            out=r.run(source,sid,sel,ident,prefix,pid,lp,lid,64)
            ck('resource_full_comparison:'+str(limit),v.verify(out,source,sid,sel,ident,prefix,pid,lp,count,status))
            ck('resource_terminal_idempotent:'+str(limit),r.run(source,sid,sel,ident,prefix,pid,lp,lid,1,out,s.identity(out))==out)
            records.append(dict(limit=limit,result=out))
        wrong_plan=cp(plan);wrong_plan['trace_limit']-=1
        reject('different_budget_with_old_checkpoint',lambda:r.run(source,sid,sel,ident,prefix,pid,wrong_plan,s.identity(wrong_plan),1,paused,s.identity(paused)))
        for name,change in [('boolean_cursor',lambda z:z.update(cursor=True)),('negative_cursor',lambda z:z.update(cursor=-1)),('future_cursor',lambda z:z.update(cursor=4)),('unknown_status',lambda z:z.update(status='admitted')),('extra_checkpoint_field',lambda z:z.update(extra=True)),('removed_remaining',lambda z:z.update(remaining=[])),('changed_current_date',lambda z:z['current'].update(date='2028-01-01'))]:
            bad=cp(paused);change(bad)
            reject(name,lambda z=bad:r.run(source,sid,sel,ident,prefix,pid,plan,plan_id,1,z,s.identity(z)))
        bad=cp(prefix);bad['execution']['trace'][0]['request']['expected_registry_sha256']='0'*64
        ck('financial_oracle_alone_insufficient',v.prior.verify(bad,source,sid,sel,ident,pi))
        reject('reidentified_wrong_prefix_request',lambda:r.make_plan(source,sid,sel,ident,pi,bad,s.identity(bad),plan['suffix']))
        for label,limit in [('bool_limit',True),('zero_limit',0),('excess_limit',s.rt.MAX_TRACE_BYTES+1)]:
            reject(label,lambda x=limit:r.make_plan(source,sid,sel,ident,pi,prefix,pid,plan['suffix'],x))
        ck('inputs_unchanged',before=={k:s.identity(x) for k,x in dict(source=source,selection=sel,prefix=prefix,plan=plan,checkpoint=paused).items()})
        for n,h in pins.items():ck('preserved:'+n,digest(R/n)==h)
        summary=dict(status='PASS',assertions=len(checks),controls=len(controls),resource_boundaries=len(records),protected_files=len(pins),scope='supplementary malformed-prefix and exact byte-boundary checks')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        v.prior.prior.prior.native.Engine.apply=old
        for n,x in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('resource-cases.json',records)]:save(n,x)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+a,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-t,seeds='N/A exact controls',data_version='source-lock.json',plan=str((H/'post-run-audit-plan.md').relative_to(R)),result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
