"""Pin inspected sources and preserve the preceding evidence; no execution claim."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import ast, json, os, platform, subprocess, sys, time
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = 'docs/plans/accounting-monetary-effects-audit-20261024.md'
NEXT = 'docs/plans/accounting-typed-monetary-effects-20261024.md'
PREFIX = 'data/accounting-master/company-return-execution-20261024/'
SOURCES = {
    PREFIX+'native_returns.py': ['transition', 'propose', 'apply', 'invariant', 'run_prefix'],
    PREFIX+'native_reports.py': ['report', 'carry'],
    'scripts/company_execution_v1.py': ['Engine'],
    'scripts/demo_debt_execution_v1.py': ['EventBook', 'execute'],
    'scripts/core0_ir_v1.py': ['evaluate_expression'],
    'scripts/method_requirements_v2.py': ['typed', 'product_type', 'compile_manifest', 'numeric'],
}
OBLIGATIONS = {
    'settlement_measurement': (PREFIX+'native_returns.py', 'refund=n*q'),
    'settlement_postings': (PREFIX+'native_returns.py', "for k,x in [('refund_liability'"),
    'settlement_memory': (PREFIX+'native_returns.py', "c.update(refund='0/1'"),
    'sale_measurement': (PREFIX+'native_returns.py', "v=q(event['proceeds'])"),
    'sale_postings': (PREFIX+'native_returns.py', "cash(v,'external_sale')"),
    'sale_memory': (PREFIX+'native_returns.py', "lot.update(units='0/1'"),
    'journal_cash_checks': (PREFIX+'native_returns.py', "need(sum(j.values())==0"),
    'final_state_check': (PREFIX+'native_returns.py', "z['seen'].append"),
    'semantic_replay': (PREFIX+'native_returns.py', 'expected=propose'),
    'portable_method_contract': ('docs/design/proposal/manuscript-collection-state-20261024/chapters/17-portable-reference.tex', 'preconditions, algorithm, account_roles'),
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
    previous = HERE.parent/'native-state-structure-20261024/manifest.json'
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
