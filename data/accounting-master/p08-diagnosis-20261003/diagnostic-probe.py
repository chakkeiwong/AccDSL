from contextlib import redirect_stdout
from datetime import datetime, timezone
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import fcntl
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path('/home/chakwong/python/AccDSL')
OUT = ROOT / 'data/accounting-master/p08-diagnosis-20261003'
OUT.mkdir(exist_ok=True)
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests')]
from accounting_master_support import digest, load_json, release_hashes, verify_hashes
from run_accounting_master import CONTROLS, ProcessTimeout, stable_hash
from corporate_financing_v1 import AuthorityBook, Contract, comparison_cases, comparison_economics, compare_same_facts
from corporate_authority_eu_v1 import EUAuthorityPreparation
from check_accounting_p08 import check_comparison
from test_accounting_master import MasterTests, response

def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

started = datetime.now(timezone.utc).isoformat()
timer = time.monotonic()
with (ROOT/'data/accounting-master/runner.lock').open() as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state = load_json(ROOT/'data/accounting-master/state.json')
    run = ROOT/state['runs'][-1]
    assert load_json(run/'manifest.json').get('finished_at'), 'Master still running'
    protected = release_hashes(ROOT)
    for phase in state['phases'].values():
        if phase['status'] == 'accepted_internal':
            protected.update(phase['evidence_hashes'])
    assert not verify_hashes(ROOT, protected), 'Existing protected-evidence mismatch'
    inputs = set(CONTROLS)
    inputs.update('data/accounting-master/'+name for name in ['state.json','next-plan.json','next-plan.md','active-process.json','controller-review.json','controller-tests.json','events.jsonl'])
    inputs.update(['scripts/corporate_financing_v1.py', 'scripts/corporate_authority_eu_v1.py', 'scripts/corporate_authority_eu_recovery_v1.py', 'scripts/check_accounting_p08.py','tests/test_accounting_p08.py'])
    for folder in [ROOT/'data/accounting-master/deliverables/P08',*sorted((ROOT/'docs/design/research').glob('p08-*'))]:
        inputs.update(str(p.relative_to(ROOT)) for p in folder.rglob('*') if p.is_file())
    before = {p:digest(ROOT/p) for p in sorted(inputs) if (ROOT/p).is_file()}
    write('input-hashes.json', before)
    code_before = {p:v for p,v in before.items() if p.startswith(('scripts/', 'tests/'))}
    env = {**os.environ, 'CUDA_VISIBLE_DEVICES':'-1', 'PYTHONDONTWRITEBYTECODE':'1'}
    command = [sys.executable, '-B', 'scripts/check_accounting_p08.py', '--check']
    check_start = time.monotonic()
    with (OUT/'checker.stdout.json').open('w') as out, (OUT/'checker.stderr.log').open('w') as err:
        try:
            completed = subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=err,timeout=120)
            process = {'exit_code':completed.returncode, 'reason':None}
        except subprocess.TimeoutExpired:
            process = {'exit_code':None,'reason':'diagnostic_timeout'}
    process['wall_seconds'] = round(time.monotonic()-check_start,3)
    write('checker-process.json', process)
    try:
        checked = load_json(OUT/'checker.stdout.json')
        check_summary = {k:checked.get(k) for k in ['passed','errors','checks','acceptance','manifest']}
    except Exception as e:
        check_summary = {'parse_error':repr(e)}
    write('checker-summary.json', check_summary)
    print('CHECKER',json.dumps({'process':process, 'passed':check_summary.get('passed'), 'errors':check_summary.get('errors'), 'checks':check_summary.get('checks'), 'acceptance':check_summary.get('acceptance')},ensure_ascii=False),flush=True)

    probes = {}
    authority = AuthorityBook()
    comparison = compare_same_facts(authority=authority)
    probes['engineering_vs_completion'] = {'validation_findings':check_comparison(comparison,authority),'criterion_status':comparison['criterion_status'],'supported_regimes':[r['standard'] for r in comparison['rows'] if r['status']=='supported_bounded']}
    eu_contract = replace(Contract(),basis='EU-endorsed IFRS',jurisdiction='EU',tier='EU listed consolidated',book='consolidated')
    for name, call in [('eu_current_admission',lambda:authority.admit(eu_contract)),('eu_current_dispatch',lambda:comparison_cases('EU-endorsed IFRS',comparison_economics(Contract()),authority))]:
        try:
            probes[name] = {'returned':call()}
        except Exception as e:
            probes[name] = {'exception':type(e).__name__,'message':str(e)}
    with patch.object(EUAuthorityPreparation,'require_admitted',return_value=True):
        try:
            authority.admit(eu_contract)
            probes['eu_admission_after_stubbed_dependency_success'] = {'admitted':True}
        except Exception as e:
            probes['eu_admission_after_stubbed_dependency_success'] = {'admitted':False,'exception':type(e).__name__,'message':str(e),'scope':'Disposable control-flow probe only; no actual source dependency is admitted.'}

    t = MasterTests();t.setUp()
    try:
        plans=[];calls=[]
        def worker(role,phase,packet,folder,attempt):
            calls.append(role)
            if role=='plan':
                return response('PLAN',steps=['Inspect all authority, implement both regimes, update all validation and report'])
            if role in ('implement','repair'):
                plans.append(stable_hash(packet['approved']))
                t.write_work(phase, 'partial-attempt-'+str(attempt))
                raise ProcessTimeout('synthetic timeout after preserving partial work')
            return response('AGREE')
        master=t.master(worker=worker)
        t.run_quiet(master,max_phases=1)
        first={'roles':calls[:],'plan_hashes':plans[:],'checks_called':t.checked[:],'status':master.state['phases']['P00']['status']}
        calls.clear();plans.clear()
        second=t.master(worker=worker)
        t.run_quiet(second,max_phases=1)
        probes['timeout_recovery']={'first_invocation':first,'second_invocation':{'roles':calls[:],'plan_hashes':plans[:],'checks_called':t.checked[:],'status':second.state['phases']['P00']['status']},'scope':'Existing isolated controller test fixture with injected workers; no model or real master invoked.'}
    finally:
        t.doCleanups()

    t=MasterTests();t.setUp()
    try:
        def check(phase,folder):
            return {'passed':True,'tests':1,'acceptance':{'engineering':True,'phase_criteria_complete':False},'criteria':{'criterion_3':'incomplete'}}
        master=t.master(check=check)
        t.run_quiet(master,max_phases=1)
        probes['incomplete_checks_with_agree']={'phase_status':master.state['phases']['P00']['status'],'injected_checks':check(None,None),'scope':'Latent acceptance-defence probe with deliberately mistaken AGREE, not observed P08 acceptance.'}
    finally:
        t.doCleanups()
    write('control-flow-probes.json',probes)
    print('PROBES',json.dumps(probes,ensure_ascii=False),flush=True)

    mismatches=verify_hashes(ROOT,before)
    protected_mismatches=verify_hashes(ROOT,protected)
    write('manifest.json',{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'wall_seconds':round(time.monotonic()-timer,3),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':[sys.executable,*sys.argv],'checker_command':command,'python':platform.python_version(),'executable':sys.executable,'hardware':'CPU only; CUDA_VISIBLE_DEVICES=-1; standard-library checks; no accelerator framework imported','seeds':'N/A: deterministic diagnostics','data_version':'P08 source dossiers v1-v5 at input-hashes.json','plan':'docs/plans/accounting-p08-root-cause-analysis-20261003.md','result':'data/accounting-master/p08-diagnosis-20261003/checker-summary.json','code_hashes':code_before,'protected_files':len(protected),'protected_mismatches':protected_mismatches,'input_mismatches':mismatches,'scope':'Engineering diagnosis; no acceptance or authority promotion'})
    assert not mismatches and not protected_mismatches
    print('INPUTS_AND_PROTECTED_EVIDENCE_UNCHANGED',True,flush=True)
