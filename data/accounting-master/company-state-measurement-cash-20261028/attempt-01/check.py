"""Independent exact-state discrimination of original SIM-F037/038."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import fixture as f

ROOT, H = f.ROOT, Path(__file__).resolve().parent
PLAN = 'docs/plans/company-state-measurement-cash-20261028.md'


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    out = ap.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    checks, cases = [], []

    def ck(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))

    def run(name, body):
        before = f.program.digest(body)
        result = f.program.run(body)
        ck(name + '/input preserved', f.program.digest(body), before)
        ck(name + '/replay', f.program.verify(body, result), True)
        cases.append(dict(id=name, input=body, result=result))
        return result

    def valid(name, result):
        ck(name + '/status', result['status'], 'complete_provisional')
        return result['status'] == 'complete_provisional'

    def stopped(name, body, result, expected):
        ck(name + '/status', result['status'], 'stopped_provisional')
        ck(name + '/outcome', (result.get('stop') or {}).get('status'), expected)
        ck(name + '/atomic state', result.get('current'), body['opening'])

    original_apply = f.ex.native.Engine.apply
    f.ex.native.Engine.apply = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('legacy fallback forbidden'))
    try:
        for owner in ['alpha', 'beta']:
            for target in ['4/1', '0/1', '10/1', '1/3']:
                name = owner + '/target_' + target
                body, m = f.make(owner, target)
                result = run(name, body)
                if not valid(name, result):
                    continue
                expected = deepcopy(body['opening']['balances'])
                expected[m['dta']] = target
                expected[m['deferred_tax']] = f.fmt(10 - Q(target))
                ck(name + '/all balances', result['current']['balances'], expected)
                ck(name + '/all memory', result['current']['memory'], body['opening']['memory'])
                ck(name + '/no cash flow', result['current']['flows'], [])
                report = result['trace'][-1]['result']
                ck(name + '/profit', report['income']['profit'], f.fmt(Q(target) - 10))
                ck(name + '/cash change', report['cash_flows']['net_movement'], '0/1')
                ck(name + '/reconciliations', report['reconciliations'], dict(balance_sheet='0/1', cash='0/1', equity='0/1'))
                ck(name + '/no accounting admission', report['accounting_admission'], False)
            name = owner + '/carry'
            body, m = f.make(owner, carry=True)
            result = run(name, body)
            if valid(name, result):
                expected = deepcopy(body['opening']['balances'])
                expected.update({m['dta']: '4/1', m['retained']: '6/1'})
                ck(name + '/all carried balances', result['current']['balances'], expected)
                ck(name + '/all carried memory', result['current']['memory'], body['opening']['memory'])
                ck(name + '/opening profit', result['trace'][-1]['result']['income']['profit'], '0/1')
                ck(name + '/no cash flow', result['current']['flows'], [])
                ck(name + '/period starts', result['current']['period']['start'], '2028-01-01')
            for label, field, value, outcome in [
                ('false_approval', 'approved', False, 'unsupported'),
                ('negative_target', 'target', '-1/1', 'invalid'),
                ('increase_outside_scope', 'target', '11/1', 'unsupported'),
                ('stale_opening', 'expected', '9/1', 'invalid'),
                ('unknown_approval', 'approved', None, 'unresolved'),
                ('unknown_measurement', 'target', None, 'unresolved')]:
                name = owner + '/' + label
                body, m = f.make(owner)
                item = body['commands'][0]['event']['inputs'][field]
                item['value'] = dict(status='unknown', reason='Required synthetic premise is unavailable') if value is None else f.engine.known(value)
                result = run(name, body)
                stopped(name, body, result, outcome)
            name = owner + '/duplicate'
            body, m = f.make(owner)
            body['commands'].insert(1, deepcopy(body['commands'][0]))
            result = run(name, body)
            ck(name + '/stopped', result['status'], 'stopped_provisional')
            ck(name + '/one event', len(result.get('trace', [])), 1)
            if result.get('trace'):
                ck(name + '/no second posting', result['current'], result['trace'][0]['result']['transition']['after'])
            name = owner + '/cash_mutation'
            body, m = f.make(owner)
            f.false_cash(body)
            result = run(name, body)
            if valid(name, result):
                report = result['trace'][-1]['result']
                ck(name + '/generic reconciliations pass', report['reconciliations'], dict(balance_sheet='0/1', cash='0/1', equity='0/1'))
                ck(name + '/measurement target passes', result['current']['balances'][m['dta']], '4/1')
                ck(name + '/fictitious cash', result['current']['balances'][m['cash']], '26/1')
                ck(name + '/false operating receipt', report['cash_flows']['activities']['operating']['net'], '6/1')
                ck(name + '/independent oracle rejects', result['current']['balances'][m['cash']] == '20/1' and result['current']['flows'] == [], False)
            for weaken in [False, True]:
                name = owner + '/right_mutation_' + str(weaken)
                body, m = f.make(owner)
                f.false_right(body, weaken)
                result = run(name, body)
                if not weaken:
                    stopped(name, body, result, 'invalid')
                elif valid(name, result):
                    ck(name + '/balances unchanged by memory defect', result['current']['balances'][m['dta']], '4/1')
                    ck(name + '/generic reconciliations pass', result['trace'][-1]['result']['reconciliations'], dict(balance_sheet='0/1', cash='0/1', equity='0/1'))
                    ck(name + '/independent rights oracle rejects', result['current']['memory'] == body['opening']['memory'], False)
            for wrong in [False, True]:
                name = owner + '/cash_category_' + str(wrong)
                body, m = f.financing(owner, wrong)
                result = run(name, body)
                if not valid(name, result):
                    continue
                report = result['trace'][-1]['result']
                activities = report['cash_flows']['activities']
                expected = deepcopy(body['opening']['balances'])
                expected.update({m['cash']: '80/1', m['debt']: '-60/1'})
                ck(name + '/all balances', result['current']['balances'], expected)
                ck(name + '/profit', report['income']['profit'], '0/1')
                ck(name + '/generic reconciliations', report['reconciliations'], dict(balance_sheet='0/1', cash='0/1', equity='0/1'))
                ck(name + '/principal memory', result['current']['memory']['finance']['debt'], '-60/1')
                ck(name + '/reported operating', activities['operating']['net'], '60/1' if wrong else '0/1')
                ck(name + '/reported financing', activities['financing']['net'], '0/1' if wrong else '60/1')
                ck(name + '/category oracle', activities['operating']['net'] == '0/1' and activities['financing']['net'] == '60/1', not wrong)
                ck(name + '/economic cash including principal differs from OCF', Q('100/1') - Q('40/1') == Q('0/1'), False)
    finally:
        f.ex.native.Engine.apply = original_apply
    fm = ROOT / 'data/accounting-master/unified-program-20261028/failure-map.json'
    originals = [r['original_row'] for r in json.loads(fm.read_text())['rows'] if r['original_row']['id'] in ['SIM-F037', 'SIM-F038']]
    ck('original exact discriminators', {r['id']: r['discriminating_case'] for r in originals},
       {'SIM-F037': 'Deferred tax asset falls10 to4', 'SIM-F038': 'Import economic OCF including principal as reported OCF'})
    paths = {Path(__file__), H / 'fixture.py', H / 'setup-diagnostics.md', ROOT / PLAN, fm}
    paths.update(Path(mod.__file__).resolve() for mod in list(sys.modules.values()) if getattr(mod, '__file__', None) and Path(mod.__file__).resolve().is_relative_to(ROOT))
    hashes = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    failed = [r for r in checks if not r['passed']]
    verdict = dict(status='fail' if failed else 'pass', checks=len(checks), native_cases=len(cases), failed=failed,
                   original_rows=['SIM-F037', 'SIM-F038'], actual_company_admission=False, general_tax_model=False)
    manifest = dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], environment=platform.python_version(),
        cpu_gpu='CPU-only exact rational native execution; no GPU framework imports', random_seeds='N/A deterministic fixtures',
        data_version='Original SIM-F037/038 with supplied synthetic journal, measurement, rights and financing classification',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - start,
        plan_file=PLAN, result_file=str((H / 'result.md').relative_to(ROOT)), source_hashes=hashes)
    for name, obj in [('verification', verdict), ('checks', checks), ('original-rows', originals), ('run-manifest', manifest)]:
        dump(out / (name + '.json'), obj)
    with gzip.open(out / 'native-results.json.gz', 'wt') as fh:
        json.dump(cases, fh)
    for name in ['fixture.py', 'check.py']:
        (out / name).write_bytes((H / name).read_bytes())
    print(json.dumps(dict(status=verdict['status'], checks=len(checks), native_cases=len(cases), failed=[r['name'] for r in failed])))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
