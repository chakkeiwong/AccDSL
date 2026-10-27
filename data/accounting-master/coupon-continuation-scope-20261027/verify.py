"""Exact continuation witnesses distinguish equal balances from equal histories."""
from pathlib import Path
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
import json,os,platform,resource,subprocess,sys,time,traceback
import continue_coupon as c
s=c.s;prior=c.prior
H=Path(__file__).resolve().parent;R=H.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()

def verify(result,source,sid,sel,ident,pins,prefix,pid,instructions,accepted):
    assert result['profile']=='SelectedPartialCouponContinuation/1'
    for flag in s.FLAGS:assert result[flag] is False
    assert result['source_carry_sha256']==sid==s.identity(source)
    assert result['selection_sha256']==ident==s.identity(sel)
    assert result['prefix_sha256']==pid==s.identity(prefix)
    assert result['prefix_archive']==prefix and result['origin_archive']==source['result']['history_archive']
    assert result['prefix_instructions']==pins and result['instructions']==instructions
    assert result['report_opening_sha256']==s.identity(sel['opening'])
    assert result['interpretation']=='same_period_cumulative_report_exact_prefix_no_merging'
    before,pretrace=prior.expected(source,pins)
    expected,trace=prior.expected(source,pins+(instructions if accepted else []))
    e=result['execution'];assert e['profile']=='SelectedCouponContinuationStep/1'
    assert e['current']==expected and e['before_sha256']==s.identity(before) and e['after_sha256']==s.identity(expected)
    command=s.program(sel,instructions)['commands'][0]
    assert e['command']==command and e['request']==s.rt.call(before,sel['registry'],command)
    if accepted:
        assert e['status']==e['proposal']['status']=='proposed'
        for key in ('after','journal','flows'):assert e['proposal']['transition'][key]==trace[-1][key]
    else:
        assert e['status']==e['proposal']['status']=='invalid'
        t=e['proposal'].get('transition',e['proposal'])
        assert not {'after','journal','flows'}&set(t)
    body=s.program(sel,pins)
    assert result['report']==prior.oracle.report_oracle(body,expected)
    assert all(v=='0/1' for v in result['report']['reconciliations'].values())
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));a=sys.argv[1];assert a in ('01','02','03')
    A=H/('attempt-'+a);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+'\n')
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def reject(n,fn):
        try:fn()
        except (AssertionError,ValueError,KeyError,TypeError) as e:controls.append(dict(name=n,reason=str(e)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old=prior.prior.prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'coupon-schedule-invariant-20261027/attempt-01'
        ck('upstream_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        modules=[Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(R)]
        for p in modules+list(B.glob('*.json'))+[H/'verify.py',H/'continue_coupon.py',H/'contract.md',R/'docs/plans/accounting-coupon-continuation-scope-20261027.md']:pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('verify.py','continue_coupon.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        records=[v for v in json.loads((H.parent/'coupon-carry-20261027/attempt-01/cases.json').read_text()) if ':R6:draw:' in v['case']]
        schedules={'one':[dict(id='first',date='2028-01-02',amount='1/1')],
            'split':[dict(id='first',date='2028-01-02',amount='1/2'),dict(id='second',date='2028-01-03',amount='1/2')]}
        tests={'earlier_date':dict(id='fresh',date='2028-01-02',amount='1/1'),
            'used_only_in_split':dict(id='second',date='2028-01-04',amount='1/1'),
            'common_fresh':dict(id='fresh',date='2028-01-04',amount='1/1')}
        save('inputs-and-expectations.json',dict(origins=[dict(case=x['case'],sha256=s.identity(x)) for x in records],prefixes=schedules,continuations=tests,expected_prefix_cash='69/16',expected_prefix_claim='35/8',expected_later_cash='53/16',expected_later_claim='27/8',scope='full history unequal; restricted numeric projection equal'))
        prior.prior.prior.native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        for source in records:
            sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel);prefixes={};results={}
            for name,inst in schedules.items():
                pref=s.run(source,sid,sel,ident,inst);pid=s.identity(pref)
                ck(source['case']+':prefix:'+name,prior.verify(pref,source,sid,sel,ident,inst))
                prefixes[name]=pref
                for key,instruction in tests.items():
                    accepted=name=='one' or key=='common_fresh'
                    result=c.run(source,sid,sel,ident,inst,pref,pid,[instruction])
                    ck(source['case']+':'+name+':'+key,verify(result,source,sid,sel,ident,inst,pref,pid,[instruction],accepted))
                    results[name,key]=result
                    cases.append(dict(case=source['case']+':'+name+':'+key,selection=sel,selection_sha256=ident,source_carry_sha256=sid,accepted=accepted,result=result))
            one,split=[prefixes[k] for k in ('one','split')]
            x,y=[v['execution']['current'] for v in (one,split)]
            ck('prefix_financial_equality',x['balances']==y['balances'] and x['memory']==y['memory'])
            ck('prefix_history_inequality',x['date']!=y['date'] and x['seen']!=y['seen'] and x['flows']!=y['flows'])
            ck('prefix_full_report_inequality',one['report']!=split['report'])
            left,right=[results[k,'common_fresh'] for k in ('one','split')]
            x,y=[v['execution']['current'] for v in (left,right)]
            ck('common_future_financial_equality',x['balances']==y['balances'] and x['memory']==y['memory'] and x['date']==y['date'])
            ck('common_future_history_inequality',x['seen']!=y['seen'] and x['flows']!=y['flows'])
            for key in ('statement_lines','balance_sheet','income','equity','reconciliations'):
                ck('report_projection:'+key,left['report'][key]==right['report'][key])
            ck('full_report_distinction',left['report']!=right['report'])
            ck('gross_totals_equal',left['report']['cash_flows']['activities']==right['report']['cash_flows']['activities'])
        source=records[0];sid=s.identity(source);sel=s.select(source,sid);ident=s.identity(sel)
        inst=schedules['one'];pref=s.run(source,sid,sel,ident,inst);pid=s.identity(pref);instructions=[tests['common_fresh']]
        generic=s.program(sel,instructions);generic['opening']=cp(pref['execution']['current'])
        out=s.rt.run(generic);ck('midperiod_program_refusal',out['status']=='invalid' and out['reason']=='opening_report:opening_at_period_start')
        save('program-opening-boundary.json',dict(result=out,interpretation='program runner accepts fiscal openings; selected step uses unchanged typed event engine'))
        controls.append(dict(name='generic_midperiod_opening',reason=out['reason']))
        bad=cp(pref);bad['execution']['current']['memory']['paid2']='2/1'
        reject('changed_prefix_old_id',lambda:c.run(source,sid,sel,ident,inst,bad,pid,instructions))
        reject('changed_prefix_new_id',lambda:c.run(source,sid,sel,ident,inst,bad,s.identity(bad),instructions))
        reject('wrong_prefix_instruction',lambda:c.run(source,sid,sel,ident,schedules['split'],pref,pid,instructions))
        badsel=cp(sel);badsel['opening']['memory']['used']=False
        reject('changed_selection',lambda:c.run(source,sid,badsel,s.identity(badsel),inst,pref,pid,instructions))
        res=c.run(source,sid,sel,ident,inst,pref,pid,instructions)
        for name,change in [('lost_origin_refusal',lambda z:z['origin_archive'].update(refusal=None)),('lost_prefix',lambda z:z.update(prefix_archive={})),('wrong_report_opening',lambda z:z.update(report_opening_sha256=pid)),('erase_old_flow',lambda z:z['execution']['current']['flows'].pop(0)),('false_admission',lambda z:z.update(accounting_admission=True))]:
            bad=cp(res);change(bad);reject(name,lambda z=bad:verify(z,source,sid,sel,ident,inst,pref,pid,instructions,True))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='date and replay distinguish equal balances; restricted numeric continuation only')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        prior.prior.prior.native.Engine.apply=old
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+a,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact conformance',data_version='source-lock.json',plan='docs/plans/accounting-coupon-continuation-scope-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
