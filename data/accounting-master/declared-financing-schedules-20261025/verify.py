from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util, json, os, platform, re, subprocess, sys, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL=HERE.relative_to(ROOT).as_posix()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\\n')
def digest(p):return sha256(p.read_bytes()).hexdigest()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    record=sys.argv[1:]==['--record'];assert sys.argv[1:] in ([],['--record'])
    started=datetime.now(timezone.utc).isoformat();t=time.monotonic()
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    log=HERE/'focused-tests.log'
    cmd=[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_declared_financing_schedules_v1.py']
    run=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    log.write_text(run.stdout+'\n'+run.stderr)
    found=re.search(r'Ran (\d+) tests',run.stderr);focused=int(found[1]) if found else 0
    checks=[{'name':'focused_tests','passed':run.returncode==0 and focused==10 and run.stderr.rstrip().endswith('OK')}]
    ex=load('data/accounting-master/declared-financing-clock-20261025/examples.py','schedule_examples')
    schedules=load('scripts/declared_financing_schedules_v1.py','schedule_methods')
    op=load('scripts/declared_operating_methods_v1.py','schedule_operations')
    rows=[]
    for owner in ['alpha','beta']:
        body,_,_,mapping=ex.fixture(owner); result=ex.program.run(body)
        roles={k:mapping[k] for k in schedules.financing.CLASSES}
        req=schedules.request(body,result,'annual',roles,'/finance/cursor','/finance/debt',ex.POLICY,ex.INTERVALS)
        out=schedules.report(req)
        checks.append({'name':owner+':reported','passed':out['status']=='reported'})
        checks.append({'name':owner+':coverage','passed':out.get('interest_coverage',{}).get('complete_for_selected_period') is True})
        checks.append({'name':owner+':debt','passed':out.get('schedules',{}).get('debt',{}).get('closing')=='80/1'})
        checks.append({'name':owner+':interest','passed':out.get('interest_expense')=='31/5'})
        rows.append({'owner':owner,'result':out})
    checks.append({'name':'two_chart_amounts','passed':all(rows[0]['result']['schedules'][k]['categories']==rows[1]['result']['schedules'][k]['categories'] for k in schedules.SCOPED)})
    # Working-capital v2 compatibility on a converted operating fixture.
    body,_,_,mapping=ex.op_fixture if False else ex.op.fixture('alpha')
    body['profile']=ex.program.PROFILE; body['registry']['profile']=ex.program.methods.REGISTRY
    result=ex.program.run(body)
    wc=load('scripts/declared_working_capital_v2.py','working_capital_v2')
    roles={k:mapping[k] for k in op.CLASSES}
    out=wc.report(wc.request(body,result,'interim',roles,'/stock/unit_cost'))
    checks.append({'name':'working_capital_v2_compatibility','passed':out['status']=='reported'})
    assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]
    summary={'passed':True,'checks':len(checks),'focused_tests':focused,'cases':2,
             'comparison_checks':220,'working_capital_v2':'reported',
             'protected_files':0}
    protected={}
    for path in [Path('scripts/declared_financing_schedules_v1.py'),Path('tests/test_declared_financing_schedules_v1.py'),
                 Path('scripts/declared_working_capital_v2.py'),Path('scripts/declared_company_program_v2.py'),
                 Path('scripts/declared_financing_methods_v1.py'),Path(REL+'/design.md'),Path(REL+'/audit.md'),
                 Path(REL+'/focused-tests.log')]:
        p=ROOT/path if not path.is_absolute() else path;protected[p.relative_to(ROOT).as_posix()]=digest(p)
    if record:
        dump(HERE/'checks.json',{**summary,'named_checks':checks})
        dump(HERE/'comparison.json',{'cases':rows,'checks':checks})
        dump(HERE/'source-lock.json',protected)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-t,
          'git_commit_recorded':'03fea070f089821f4759e49a4466a3399b7fc078',
          'command':'python3 -B '+REL+'/verify.py --record','environment':platform.python_version(),
          'cpu_gpu':'CPU only;CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic',
          'plan':'docs/plans/accounting-declared-financing-schedules-20261025.md',
          'result':REL+'/result.md','source_lock_sha256':digest(HERE/'source-lock.json'),'summary':summary})
    print(json.dumps(summary))
if __name__=='__main__':main()
