"""Record four exact period summaries once; replay their complete outputs read only."""
from hashlib import sha256
from pathlib import Path
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
import group_period_report_v1 as composition

def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+chr(10))

def run():
    start=time.monotonic();record='--record' in sys.argv
    if record and (HERE/'evidence.json').exists():raise SystemExit('Evidence already exists; replay without --record')
    locks={};tests=[]
    def lock(path,expected=None):
        path=path if isinstance(path,Path) else ROOT/path;actual=sha(path)
        if expected is not None:assert actual==expected,str(path)
        locks[str(path.relative_to(ROOT))]=actual
    for folder in ['compatible-book-composition-20261025']:
        path=ROOT/'data/accounting-master'/folder/'source-lock.json';lock(path)
        for name,expected in json.loads(path.read_text()).items():lock(name,expected)
    for pattern in ['test_group_period_report_v1.py','test_compatible_book_composition_v1.py','test_company_book_reports_v1.py']:
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
    cases=examples.cases()
    for row in cases.values():
        assert all(row['result'][key] is False for key in composition.FLAGS)
    evidence={'tests':tests,'cases':cases,'expected':{'cash_opening':'200/1','cash_closing':'220/1','profit':'20/1','external_receipts':'20/1'},
              'scope':'Four constructed period summaries; no general consolidation, source or accounting admission'}
    for path in ['scripts/group_period_report_v1.py','tests/test_group_period_report_v1.py',
                 'docs/plans/accounting-group-period-report-20261025.md',
                 str((HERE/'examples.py').relative_to(ROOT)),str((HERE/'audit.md').relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]:lock(path)
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json')
        for row in tests:lock(HERE/(row['pattern']+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/group-period-report-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU exact rational/file checks; no GPU framework imported',
            'seeds':'N/A: deterministic','data_version':'Two charts, two activity classifications; exact cash and equity expectations',
            'wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-group-period-report-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']},
            'provenance':'Git identifies base; source locks identify executed uncommitted bytes'})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text()),'complete evidence replay'
        saved=json.loads((HERE/'source-lock.json').read_text())
        for name,expected in saved.items():assert sha(ROOT/name)==expected,name
        for name,expected in locks.items():assert saved[name]==expected,name
        manifest=json.loads((HERE/'run-manifest.json').read_text())
        for name,expected in manifest['artifacts'].items():assert sha(ROOT/name)==expected,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','focused':tests[0]['count'],
        'regressions':sum(r['count'] for r in tests[1:]),'cases':len(cases),'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}))

if __name__=='__main__':run()
