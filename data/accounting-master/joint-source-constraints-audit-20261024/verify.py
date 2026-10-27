"""Pin inspected sources and preserve the preceding evidence; no execution claim."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import ast, json, os, platform, subprocess, sys, time
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-joint-source-constraints-audit-20261024.md'
NEXT = 'docs/plans/accounting-joint-measurement-constraints-20261024.md'
PREFIX = 'data/accounting-master/company-return-execution-20261024/'
SOURCES = {
    'scripts/rational_solver_v1.py':['Problem','Budget','affine','solve','domain_formula','disclosure_domain'],
    'scripts/reconstruction_v1.py':['construct','expression'],
    'data/accounting-master/source-relations-20261024/relations.py':['normalized','interval_sum','evaluate'],
    'data/accounting-master/source-constrained-state-20261024/partial_state.py':['rounding_interval','evaluate'],
}
OBLIGATIONS = {
    'rounding_convention':('scripts/rational_solver_v1.py',"if convention == 'half_even':"),
    'unknown_product_rejection':('scripts/rational_solver_v1.py',"unknown-by-unknown product:"),
    'core_recheck':('scripts/rational_solver_v1.py',"verified, _ = check([e for _, e in core], 'core-recheck')"),
    'incomplete_coverage':('scripts/rational_solver_v1.py',"cov['complete'] = cov['unresolved'] == 0"),
}

def sha(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else '--check'
    assert mode in ['--check', '--record', '--replay']
    assert mode != '--record' or not (HERE/'manifest.json').exists()
    start = time.monotonic()
    if mode == '--replay':
        saved = json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs', 'implementation', 'outputs']:
            for name, h in saved[group].items():
                assert sha(ROOT/name) == h, name
    previous = HERE.parent/'transition-coverage-refresh-20261024/manifest.json'
    old = json.loads(previous.read_text())
    locks = {}
    for group in ['inputs', 'implementation', 'outputs']:
        locks.update(old[group])
    checks, anchors = [], []
    for name in sorted(set(SOURCES) | {p for p, _ in OBLIGATIONS.values()} | {PLAN, NEXT, str(previous.relative_to(ROOT))}):
        h = sha(ROOT/name)
        assert name not in locks or locks[name] == h, name
        locks[name] = h
    for name, h in locks.items():
        checks.append({'name': 'protected:'+name, 'passed': sha(ROOT/name) == h})
    for name, functions in SOURCES.items():
        tree = ast.parse((ROOT/name).read_text())
        found = {n.name:n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for function in functions:
            assert function in found, (name, function)
            node = found[function]
            anchors.append({'file':name, 'symbol':function, 'start':node.lineno, 'end':node.end_lineno, 'sha256':locks[name]})
    for obligation, (name, text) in OBLIGATIONS.items():
        hits = [i for i, line in enumerate((ROOT/name).read_text().splitlines(), 1) if text in line]
        assert len(hits) == 1, obligation
        anchors.append({'file':name, 'obligation':obligation, 'line':hits[0], 'sha256':locks[name]})
        checks.append({'name':obligation, 'passed':True})
    result = {'passed':all(x['passed'] for x in checks), 'checks':checks, 'anchors':anchors,
              'scope':'source inventory and protected identities; no new method execution'}
    assert result['passed']
    observation = {'passed':True, 'checks':len(checks), 'anchors':len(anchors),
                   'protected_inputs':len(locks), 'wall_seconds':time.monotonic()-start}
    if mode == '--record':
        dump(HERE/'checks.json', result)
        dump(HERE/'source-lock.json', locks)
        dump(HERE/'manifest.json', {
            'started_utc':datetime.now(timezone.utc).isoformat(), 'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version(), 'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic source audit', 'data_version':'source-lock.json',
            'plan':PLAN, 'result':str(HERE.relative_to(ROOT)/'result.md'), 'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','source-lock.json']}})
    elif mode == '--replay':
        assert result == json.loads((HERE/'checks.json').read_text())
    print(json.dumps(observation))

if __name__ == '__main__':
    main()
