"""Record and replay eight group bridges with explicit snapshot adapters."""
from pathlib import Path
from hashlib import sha256
import io
import json
import platform
import subprocess
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(HERE))
import examples

def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v, ensure_ascii=False, separators=(',',':')) + '\n')

def main():
    record = '--record' in sys.argv; started = time.monotonic()
    if record: assert not (HERE / 'evidence.json').exists()
    patterns = ['test_group_indirect_cash_v1.py', 'test_group_period_report_v1.py',
        'test_compatible_book_composition_v1.py', 'test_company_book_reports_v1.py',
        'test_declared_indirect_cash_v2.py']
    tests = []
    for pattern in patterns:
        stream = io.StringIO()
        suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern=pattern)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun, stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record: (HERE / (pattern + '.log')).write_text(stream.getvalue())
        print(json.dumps({'tests':pattern,'passed':result.testsRun}), flush=True)
    folder = HERE / 'cases'; folder.mkdir(exist_ok=True)
    cases = []
    for chart in ['named','numbered']:
        for variant in examples.VARIANTS:
            name = chart + '.' + variant; p = folder / (name + '.json')
            row = examples.checked_case(chart,variant)
            if record:
                assert not p.exists(); dump(p,row)
            else: assert row == json.loads(p.read_text()), 'complete_case:' + name
            cases.append({'name':name,'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
            examples._cache.clear()
            print(json.dumps({'case':name,'passed':True}), flush=True)
    locks = {}
    def lock(p,expected=None):
        p = p if isinstance(p,Path) else ROOT/p
        actual = sha(p)
        if expected is not None: assert actual == expected, str(p)
        locks[str(p.relative_to(ROOT))] = actual
    for module in list(sys.modules.values()):
        name = getattr(module,'__file__',None)
        if name and Path(name).resolve().parent == ROOT/'scripts' and Path(name).suffix == '.py':
            lock(Path(name).resolve())
    for p in [Path(__file__),HERE/'examples.py',HERE/'audit.md',
              ROOT/'docs/plans/accounting-group-indirect-cash-20261025.md',
              ROOT/'data/accounting-master/group-period-report-20261025/examples.py',
              ROOT/'data/accounting-master/compatible-book-composition-20261025/examples.py',
              ROOT/'data/accounting-master/declared-indirect-profit-components-20261025/examples.py',
              ROOT/'data/accounting-master/declared-indirect-cash-20261025/examples.py',
              ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py',
              ROOT/'data/accounting-master/declared-operating-cycle-20261025/examples.py']:
        lock(p)
    for pattern in patterns: lock(ROOT/'tests'/pattern)
    for folder in ['group-period-report-20261025','declared-indirect-profit-components-20261025']:
        base = ROOT/'data/accounting-master'/folder
        for name in ['evidence.json','source-lock.json','run-manifest.json','result.md']: lock(base/name)
        for name,expected in json.loads((base/'run-manifest.json').read_text())['artifacts'].items(): lock(name,expected)
    evidence = {'tests':tests,'cases':cases,'case_count':len(cases),
        'original_comparator_cases':4,'asymmetric_category_cases':4,
        'scope':'Conditional two-book trace binding and internal-flow correction; no accounting or completeness admission'}
    if record:
        dump(HERE/'evidence.json',evidence); lock(HERE/'evidence.json')
        for pattern in patterns: lock(HERE/(pattern+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/group-indirect-cash-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),
            'cpu_gpu':'CPU exact rational accounting; no GPU frameworks imported','seeds':'N/A deterministic',
            'data_version':'Two charts, four supplied cash classifications, explicit snapshot identity/schema adapters',
            'wall_seconds':time.monotonic()-started,'plan':'docs/plans/accounting-group-indirect-cash-20261025.md',
            'result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']},
            'provenance':'Git identifies base; exact executed local sources bound by hashes'})
    else:
        assert evidence == json.loads((HERE/'evidence.json').read_text())
        saved = json.loads((HERE/'source-lock.json').read_text())
        for name,expected in saved.items(): assert sha(ROOT/name) == expected,name
        for name,expected in locks.items(): assert saved[name] == expected,name
        for name,expected in json.loads((HERE/'run-manifest.json').read_text())['artifacts'].items():
            assert sha(ROOT/name) == expected,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
        'focused':tests[0]['count'],'regressions':sum(r['count'] for r in tests[1:]),
        'cases':len(cases),'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}),flush=True)

if __name__ == '__main__': main()
