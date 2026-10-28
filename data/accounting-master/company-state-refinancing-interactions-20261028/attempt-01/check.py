"""Exact full-path comparator and dependency/refusal diagnostics for SIM-F066."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, json, platform, subprocess, sys, time, traceback
import fixture as f
import views

B=Path(__file__).resolve().parent; ROOT=f.ROOT
OUT=B/sys.argv[1]; OUT.mkdir(exist_ok=False)
START=time.monotonic(); checks=[]; runs=[]; controls=[]
def save(name,value):
    raw=json.dumps(value,sort_keys=True,indent=2).encode()
    if name.endswith('.gz'):raw=gzip.compress(raw,mtime=0)
    (OUT/name).write_bytes(raw)
def check(name,actual,expected):
    ok=actual==expected
    checks.append(dict(id=name,actual=actual,expected=expected,passed=ok))
    if not ok:raise AssertionError((name,actual,expected))

JOURNALS=[dict(cash=20,revenue=-20),dict(cash=80,new_debt=-80),
          dict(cash=20,capital=-20),dict(cash=-100,debt=100),
          dict(cash=-4,fee=4),dict(interest=2,interest_payable=-2),
          dict(cash=-2,interest_payable=2),dict(current_tax=Q(7,2),tax_payable=Q(-7,2)),
          dict(cash=Q(-7,2),tax_payable=Q(7,2))]
FLOW=[(20,'operating'),(80,'financing'),(20,'financing'),(-100,'financing'),
      (-4,'operating'),(0,None),(-2,'operating'),(0,None),(Q(-7,2),'operating')]

def native_run(name,body):
    before=deepcopy(body); result=f.program.run(body)
    check(name+'.input_unchanged',body,before)
    runs.append(dict(case=name,program=body,result=result))
    return result

def run():
    for owner in ['alpha','beta']:
        b,m=f.make(owner); before=deepcopy(b); joined=views.complete(b,m,f.TAX)
        check(owner+'.wrapper_status',joined['status'],'evaluated')
        check(owner+'.wrapper_input',b,before)
        result=joined['result']; full=joined['program']; view=joined['view']
        runs.append(dict(case=owner+'.joined',program=full,result=result,view=view))
        check(owner+'.complete',result['status'],'complete_provisional')
        check(owner+'.replay',f.program.verify(full,result),True)
        check(owner+'.trace_length',len(result['trace']),10)
        expected=deepcopy(b['opening']['balances'])
        for i,(delta,(net,activity)) in enumerate(zip(JOURNALS,FLOW)):
            trans=result['trace'][i]['result']['transition']
            journal={k:'0/1' for k in expected}
            for role,amount in delta.items():
                journal[m[role]]=f.fmt(amount); expected[m[role]]=f.fmt(Q(expected[m[role]])+amount)
            check(owner+f'.{i}.journal',trans['journal'],journal)
            after=trans['after']
            check(owner+f'.{i}.all_balances',after['balances'],expected)
            check(owner+f'.{i}.cash_flow',f.fmt(sum(Q(x['amount']) for x in trans['flows'])),f.fmt(net))
            check(owner+f'.{i}.flow_activity',[x['activity'] for x in trans['flows']],[] if activity is None else [activity])
            command=full['commands'][i]['event']
            check(owner+f'.{i}.date',after['date'],command['date'])
            check(owner+f'.{i}.seen',after['seen'],[c['event']['id'] for c in full['commands'][:i+1]])
            check(owner+f'.{i}.old_debt',after['memory']['finance']['old_debt'],'-100/1' if i<3 else '0/1')
            check(owner+f'.{i}.new_debt',after['memory']['finance']['new_debt'],'0/1' if i<1 else '-80/1')
            check(owner+f'.{i}.shares',after['memory']['ownership'],dict(old='100/1',new='0/1' if i<2 else '10/1'))
            check(owner+f'.{i}.complement',after['memory']['complement'],b['opening']['memory']['complement'])
            for flow in trans['flows']:
                check(owner+f'.{i}.flow_identity',{k:flow[k] for k in ['event_id','date','entity','book','currency']},
                      dict(event_id=command['id'],date=command['date'],**{k:b['opening']['context'][k] for k in ['entity','book','currency']}))
        report=result['trace'][-1]['result']
        check(owner+'.report_status',report['status'],'reported')
        check(owner+'.assets',report['balance_sheet']['total_assets'],'421/2')
        check(owner+'.liabilities',report['balance_sheet']['total_liabilities'],'80/1')
        check(owner+'.profit',report['income']['profit'],'21/2')
        check(owner+'.equity',report['equity']['closing'],'261/2')
        check(owner+'.cash',report['cash_flows']['closing_cash'],'81/2')
        check(owner+'.net_financing',report['cash_flows']['activities']['financing']['net'],'0/1')
        check(owner+'.net_operating',report['cash_flows']['activities']['operating']['net'],'21/2')
        check(owner+'.tax',view['tax'],'7/2');check(owner+'.old_ownership',view['old_fraction'],'10/11')
        check(owner+'.new_ownership',view['new_fraction'],'1/11')
        check(owner+'.admission_flags',[result[k] for k in ['source_admission','accounting_admission','fiscal_complete']], [False]*3)
        state=result['trace'][6]['result']['transition']['after']
        args=(state,b['schemas'],m,f.TAX)
        check(owner+'.fresh_reuse',views.reuse(view,*args)['status'],'conditional')
        early=result['trace'][0]['result']['transition']['after']
        old=views.derive(early,b['schemas'],m,f.TAX)
        check(owner+'.old_tax',old['tax'],'5/1');check(owner+'.old_ownership_cache',old['old_fraction'],'1/1')
        check(owner+'.stale_reuse',views.reuse(old,*args)['status'],'stale')
        blocked=views.complete(b,m,f.TAX,old)
        check(owner+'.stale_blocks_settlement',blocked['status'],'stale')
        check(owner+'.stale_has_no_joined_result','result' in blocked,False)
        controls.append(dict(case=owner+'.stale_full_path',result=blocked))
        # Native balance alone accepts the wrong supplied tax. This is a negative comparator.
        wrong=native_run(owner+'.stale_tax_negative',f.finish(b,m,old['tax']))
        check(owner+'.wrong_tax_still_balances',wrong['status'],'complete_provisional')
        check(owner+'.wrong_tax_cash',wrong['current']['balances'][m['cash']],'39/1')
        check(owner+'.wrong_tax_differs',wrong['current']['balances'][m['cash']]!=result['current']['balances'][m['cash']],True)
        if owner=='beta':continue
        # These dependencies can change without changing immediate cash.
        for label,mutate in [
            ('date',lambda x:x.update(date='2027-02-01')),
            ('event_id',lambda x:x['seen'].__setitem__(0,'distinct.receipt')),
            ('ownership',lambda x:x['memory']['ownership'].update(new='20/1')),
            ('complement',lambda x:x['memory']['complement'].update(tag='new-known-history'))]:
            changed=deepcopy(state);mutate(changed)
            r=views.reuse(view,changed,b['schemas'],m,f.TAX)
            check(label+'.same_cash',changed['balances'][m['cash']],state['balances'][m['cash']])
            check(label+'.refuse_cached',r['status'],'stale');controls.append(dict(case=label,result=r))
        for label,change,status in [('rate',{'rate':'1/5'},'stale'),('source',{'source':'different supplied evidence'},'stale'),
                                    ('basis',{'basis':'ForeignBasis/1'},'unsupported'),
                                    ('unknown_rate',{'rate':None},'unresolved'),('unknown_deductibility',{'fee_deductible':None},'unresolved'),
                                    ('boolean_as_integer',{'recognition':1},'invalid'),('negative_rate',{'rate':'-1/4'},'invalid')]:
            policy={**deepcopy(f.TAX),**change};r=views.reuse(view,state,b['schemas'],m,policy)
            check(label+'.policy',r['status'],status);controls.append(dict(case=label,result=r))
        missing=deepcopy(f.TAX);del missing['source']
        check('missing_source',views.derive(state,b['schemas'],m,missing)['status'],'unresolved')
        changed=deepcopy(view);changed['tax']='0/1'
        check('cached_value_tamper',views.reuse(changed,*args)['status'],'stale')
        changed=deepcopy(state);changed['balances'][m['payroll']]='1/1';changed['balances'][m['cash']]=f.fmt(Q(changed['balances'][m['cash']])-1)
        check('unmodeled_income_not_ignored',views.derive(changed,b['schemas'],m,f.TAX)['status'],'unsupported')
        native_controls=[]
        x=deepcopy(b);x['commands'][3]['event']['date']='2027-01-02';native_controls.append(('debt_clock_mismatch',x,3))
        x=deepcopy(b);x['commands'][4]['event']['date']='2026-12-31';native_controls.append(('backdated_fee',x,4))
        x=deepcopy(b);x['commands'][4]['event']['id']=x['commands'][1]['event']['id'];native_controls.append(('duplicate_identity',x,4))
        x=deepcopy(b);x['commands'][2]['event']['inputs']['shares']['type']['dimensions']={'currency:USD':1};native_controls.append(('share_unit_mismatch',x,None))
        x=deepcopy(b);x['registry']['context']['entity']='Foreign';native_controls.append(('wrong_entity',x,None))
        x=deepcopy(b);x['opening']['profile']='ConditionalSharedTaxBook/1';native_controls.append(('foreign_tax_schema',x,None))
        x=deepcopy(b);x['commands'][3]['event']['inputs']['amount']['value']=f.program.engine.known('101/1');native_controls.append(('old_obligation_overpaid',x,3))
        for label,x,n in native_controls:
            r=native_run(label,x)
            if n is None:check(label+'.invalid',r['status'],'invalid')
            else:
                check(label+'.stopped',r['status'],'stopped_provisional')
                check(label+'.prefix_length',len(r['trace']),n)
                check(label+'.atomic_prefix',r['current'],result['trace'][n-1]['result']['transition']['after'])
                check(label+'.remainder',r['remaining_commands'],x['commands'][n:])
    return dict(passed=True,checks=len(checks),native_programs=len(runs),dependency_controls=len(controls))

try:
    summary=run();save('verification.json',summary)
except Exception:
    save('failure.json',dict(error=traceback.format_exc(),checks_passed=sum(c['passed'] for c in checks)))
    raise
finally:
    save('checks.json.gz',checks);save('native-results.json.gz',runs);save('dependency-controls.json.gz',controls)
    paths={Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and str(ROOT) in str(x.__file__) and str(x.__file__).endswith('.py')}
    paths.add(Path(__file__).resolve())
    save('source-hashes.json',{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
    save('manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' '+sys.argv[1],
        environment=sys.executable,python=platform.python_version(),cpu_gpu='CPU only; no GPU framework imported',
        data_version='Explicit synthetic exact-rational premises; no empirical data',seeds='N/A deterministic',
        wall_seconds=time.monotonic()-START,plan='docs/plans/'+B.name+'.md',result=str(B.relative_to(ROOT)/'result.md'),
        artifacts=str(OUT.relative_to(ROOT))))
print(json.dumps(summary,sort_keys=True))
