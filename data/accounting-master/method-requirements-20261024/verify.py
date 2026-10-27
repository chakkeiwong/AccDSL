"""Independent unit semantics plus selected legacy differential evidence."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import io
import json
import os
import platform
import subprocess
import sys
import time
import unittest

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-method-requirements-20261024.md'
NEXT = 'docs/plans/accounting-method-requirement-authoring-20261024.md'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def conformance():
    from bridge import compare
    observations, examples, difference, dependencies = compare()
    checks = []
    def check(name, value):
        checks.append({'name':name,'passed':bool(value)})
    for row in observations:
        check(row['case']+'.legacy_comparison',row['matched'])
        check(row['case']+'.input_unchanged',row['input_unchanged'])
        check(row['case']+'.no_admission',all(row['result'][k] is False for k in
              ['executed','source_admission','accounting_admission','method_eligible']))
    check('legacy_precedence_difference_exposed',difference['legacy_status']=='unresolved'
          and difference['selected_status']=='invalid' and difference['global_equivalence_claim'] is False)
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_method_requirements_v1.py')
    capture = io.StringIO()
    result = unittest.TextTestRunner(stream=capture,verbosity=1).run(suite)
    check('independent_unit_suite',result.wasSuccessful() and result.testsRun==11)
    if not result.wasSuccessful():
        print(capture.getvalue(),file=sys.stderr)
    prior = HERE.parent/'language-architecture-refresh-20261024'
    locks = json.loads((prior/'source-lock.json').read_text())
    for p in dependencies:
        if p.is_relative_to(HERE) or p == ROOT/'scripts/method_requirements_v1.py':
            continue
        name = str(p.relative_to(ROOT))
        if name in locks:
            check('consistent_prior_lock:'+name,locks[name]==sha(p))
        else:
            locks[name] = sha(p)
    for p in [prior/'inventory.json',prior/'checks.json',prior/'manifest.json',ROOT/PLAN,ROOT/NEXT]:
        locks[str(p.relative_to(ROOT))] = sha(p)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    output = {'passed':all(c['passed'] for c in checks),'checks':checks,
              'unit_tests':result.testsRun,'legacy_cases':len(observations),
              'comparisons':observations,'precedence_difference':difference}
    return output, examples, locks


def main():
    mode = sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    if mode=='--replay':
        recorded = json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in recorded[group].items():
                assert sha(ROOT/name)==h,name
    result, examples, locks = conformance()
    summary = {'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
               'unit_tests':result['unit_tests'],'legacy_cases':result['legacy_cases'],
               'protected_inputs':len(locks),'failed':[c['name'] for c in result['checks'] if not c['passed']],
               'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('examples.json',examples),('source-lock.json',locks)]:
            dump(HERE/name,value)
        files = [p for p in HERE.iterdir() if p.suffix in ['.py','.md']]
        files += [ROOT/'scripts/method_requirements_v1.py',ROOT/'tests/test_method_requirements_v1.py']
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':summary['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; Fraction; retained jsonschema validators',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1; no numerical framework imported',
            'random_seeds':'N/A: deterministic conformance','data_version':'Retained exact source locks',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
            'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in
                       ['checks.json','examples.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text()),'result replay mismatch'
        assert examples==json.loads((HERE/'examples.json').read_text()),'example replay mismatch'
        assert locks==json.loads((HERE/'source-lock.json').read_text()),'lock replay mismatch'
    print(json.dumps(summary))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
