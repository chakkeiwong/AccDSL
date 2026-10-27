"""Freeze the two-chart term lifecycle and check exact read-only replay."""
from pathlib import Path
from hashlib import sha256
import io
import json
import platform
import subprocess
import sys
import time
import unittest
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import examples
import receivable_term_history_v1 as terms
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def run():
    start=time.monotonic();record='--record' in sys.argv
    if record:assert not (HERE/'evidence.json').exists(),'record already exists'
    locks={};tests=[]
    def lock(p,expected=None):
        p=p if isinstance(p,Path) else ROOT/p;actual=sha(p)
        if expected is not None:assert actual==expected,str(p)
        locks[str(p.relative_to(ROOT))]=actual
    for folder in ['declared-collection-state-growth-20261025','amendment-semantics-audit-20261025']:
        p=ROOT/'data/accounting-master'/folder/'source-lock.json';lock(p)
        for path,expected in json.loads(p.read_text()).items():lock(path,expected)
    for pattern in ['test_receivable_term_history_v1.py','test_declared_receivable_lifecycle_v1.py',
                    'test_company_book_transition_v2.py','test_company_book_carry_v1.py']:
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
    cases=examples.cases()
    for case in cases.values():
        for step in case['steps']:assert all(step['result'][flag] is False for flag in terms.FLAGS)
        assert all(case['carry'][flag] is False for flag in terms.FLAGS)
    evidence={'tests':tests,'cases':cases,'scope':'Constructed prospective date-only terms; no actual modification accounting or complete term history'}
    for path in ['scripts/receivable_term_history_v1.py','tests/test_receivable_term_history_v1.py',
                 'docs/plans/accounting-receivable-term-history-20261025.md',
                 str((HERE/'examples.py').relative_to(ROOT)),str((HERE/'audit.md').relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]:lock(path)
    for name,h in terms.PINS.items():lock(ROOT/'scripts'/name,h)
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json')
        for row in tests:lock(HERE/(row['pattern']+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/receivable-term-history-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact state/schema checks; no GPU framework imported',
            'seeds':'N/A: deterministic','data_version':'Two retained synthetic charts, supplied term amendments and expected assessments',
            'wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-receivable-term-history-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'provenance':'Uncommitted code identified by source locks',
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text()),'exact evidence replay'
        saved=json.loads((HERE/'source-lock.json').read_text())
        for name,h in saved.items():assert sha(ROOT/name)==h,name
        for name,h in locks.items():assert saved[name]==h,name
        for name,h in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():assert sha(ROOT/name)==h,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','focused':tests[0]['count'],
        'regressions':sum(r['count'] for r in tests[1:]),'cases':len(cases),'steps_per_case':[len(c['steps']) for c in cases.values()],
        'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}))
if __name__=='__main__':run()
