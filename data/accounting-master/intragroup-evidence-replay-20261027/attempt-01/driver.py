"""Replay unchanged intragroup calls with full goldens and rational checks."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import importlib.metadata
import json
import os
from pathlib import Path
import re
import resource
import sys
import time
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--smoke', action='store_true')
args = parser.parse_args()
root, out = args.root.resolve(), args.output.resolve()
assert out.is_relative_to(root) and out != root
assert Path(__file__).resolve().is_relative_to(root)
out.mkdir(exist_ok=False)
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
started = time.monotonic()
environment = {Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()}
accesses, violations, libraries = set(), [], set()
manifest = None

def kind(path):
    if path.is_relative_to(out): return 'output'
    if path.is_relative_to(root): return 'bundle'
    if any(path.is_relative_to(p) for p in environment): return 'installed_environment'
    return 'undeclared'

def refuse(event, value):
    violations.append(dict(event=event, detail=str(value)))
    raise RuntimeError('undeclared access: ' + str(value))

def audit(event, values):
    if event == 'open':
        path, mode, flags = values
        if isinstance(path, int):
            if path not in (0, 1, 2): refuse(event, path)
            return
        path = Path(os.fsdecode(path)).resolve()
        write = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        category = kind(path)
        accesses.add((str(path), 'write' if write else 'read', category))
        if (write and category != 'output') or (not write and category == 'undeclared'):
            refuse(event, path)
        if not write and category == 'bundle' and manifest is not None:
            relative = str(path.relative_to(root))
            # Failed bytecode probes are recorded; successful undeclared reads
            # are checked below, and bytecode writing is disabled.
            if path.is_file() and relative not in manifest['entries'] and relative != 'intragroup-manifest.json':
                refuse(event, path)
    elif event == 'ctypes.dlopen':
        path = values[0]; libraries.add(str(path))
        if path is not None and (not os.path.isabs(path) or kind(Path(path).resolve()) == 'undeclared'):
            refuse(event, path)
    elif event in ['os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime']:
        if kind(Path(os.fsdecode(values[0])).resolve()) != 'output': refuse(event, values[0])
    elif event in ['os.rename', 'os.link', 'os.symlink']:
        if any(kind(Path(os.fsdecode(p)).resolve()) != 'output' for p in values[:2]): refuse(event, values[:2])
    elif event in ['socket.connect', 'socket.bind', 'subprocess.Popen', 'os.system', 'os.exec']:
        refuse(event, values)

sys.addaudithook(audit)
checks, independent, counts, outputs = [], [], [], []
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
frac = lambda n: str(F(n).numerator) + '/' + str(F(n).denominator)

def dump(name, value):
    with (out / name).open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')

def check(name, actual, expected=True):
    passed = actual == expected
    checks.append(dict(name=name, passed=passed))
    if not passed:
        dump('first-difference.json', dict(name=name, actual=actual, expected=expected))
        raise AssertionError(name)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def fixture_arguments(unit, identifier):
    if unit in ['downstream', 'realisation', 'upstream']:
        match = re.fullmatch(r'([^/]+)/(cash|equity|mixed)/(credit|settled)/(recognised|unrecognised|unresolved)(?:/(\d+/\d+))?', identifier)
        assert match, identifier
        election, mix, settled, tax, sold = match.groups()
        result = [election, mix, settled == 'settled', tax]
        if sold is not None: result.append(sold)
        return result
    if unit == 'downstream-carry':
        match = re.fullmatch(r'(\d+/\d+)/(credit|settled)/(\d+/\d+)/(known|unresolved)', identifier)
    else:
        match = re.fullmatch(r'(\d+/\d+)/(credit|settled)/(\d+/\d+)/(recognised|unrecognised|unresolved)/(known|unresolved)', identifier)
    assert match, identifier
    values = list(match.groups()); values[1] = values[1] == 'settled'
    return values

# This checker takes reported records only; no candidate or fixture calculators.
INCOME = {'revenue', 'merchandise_revenue', 'cost_of_sales', 'depreciation',
          'operating_expense', 'current_tax_expense', 'intragroup_deferred_tax_expense',
          'tax_expense', 'inventory_tax_reversal_expense'}

def rational_checks(result):
    count = 0
    def eq(actual, expected, message):
        nonlocal count
        count += 1
        assert actual == expected, message
    def values(mapping): return {k: F(v) for k, v in mapping.items()}
    def add(state, entries):
        for key, value in entries.items(): state[key] = state.get(key, F(0)) + F(value)
    def balance(mapping, label): eq(sum(values(mapping).values()), F(0), label)
    if result['status'] == 'invalid':
        eq('report' in result, False, 'invalid report')
        return count
    if 'original_books' in result:
        for entity, book in result['original_books'].items():
            for stage, snapshot in book['snapshots'].items(): balance(snapshot['balances'], entity + '/' + stage)
        if 'legal_journals' in result:
            for entity, book in result['original_books'].items():
                state = {key: F(0) for key in book['snapshots']['closing']['balances']}
                for entry in result['legal_journals']:
                    if entry['entity'] != entity: continue
                    balance(entry['entries'], entry['id']); add(state, entry['entries'])
                    eq(state['cash'] >= 0, True, 'negative cash prefix')
                eq(state, values(book['snapshots']['closing']['balances']), 'complete legal closing')
        for label in ['acquisition_worksheet', 'closing_worksheet']:
            worksheet = result[label]
            state = values(worksheet['raw']); balance(worksheet['raw'], label + '/raw')
            for entry in worksheet['journals']:
                balance(entry['entries'], label + '/' + entry['id']); add(state, entry['entries'])
            eq(state, values(worksheet['adjusted']), label + '/adjusted')
            balance(worksheet['balances'], label + '/aggregated')
        for origin in result.get('intragroup_cash_origins', []):
            eq(F(origin['amount']) + F(origin['elimination']), F(0), 'internal cash cancellation')
        for origin in result.get('external_cash_origins', []):
            eq(F(origin['elimination']), F(0), 'external cash must remain')
    if 'opening_legal' in result:
        balance(result['opening_legal'], 'legal opening'); balance(result['opening_group'], 'group opening')
        opening = values(result['opening_legal']); add(opening, result['opening_bridge'])
        eq(opening, values(result['opening_group']), 'complete opening bridge')
        state = values(result['opening_legal'])
        for entry in result['legal_journals']:
            balance(entry['entries'], entry['id']); add(state, entry['entries'])
        eq(state, values(result['closing_legal']), 'carried legal replay')
        for entry in result['group_journals']:
            balance(entry['entries'], entry['id']); add(state, entry['entries'])
        eq(state, values(result['closing_adjusted']), 'carried group replay')
        balance(result['closing_balances'], 'carried aggregate')
        eq(any(entry['id'] == 'acquisition' for entry in result['group_journals']), False, 'new acquisition')
        subsidiary_income = -sum(F(value) for name, value in result['closing_adjusted'].items()
            if name.split('.')[0] in {'S', 'group'} and name.split('.')[1] in INCOME)
        eq(subsidiary_income / 4, F(result['report']['nci_profit']), 'NCI from subsidiary earnings')
    if result['status'] == 'tax_method_required':
        eq('report' in result, False, 'unknown tax has no final report')
        return count
    report = result['report']
    eq(F(report['owners_profit']) + F(report['nci_profit']), F(report['profit']), 'profit allocation')
    if 'assets_closing' in report:
        eq(F(report['assets_closing']) - F(report['liabilities_closing']), F(report['equity_closing']), 'balance sheet')
        eq(F(report['owners_equity_closing']) + F(report['nci_closing']), F(report['equity_closing']), 'closing equity allocation')
        cash = sum(F(book['snapshots']['closing']['balances']['cash']) for book in result['original_books'].values())
        eq(cash, F(report['cash']['closing']), 'cash from legal books')
    else:
        eq(F(report['assets']) - F(report['liabilities']), F(report['equity']), 'carry balance sheet')
        eq(F(report['owners_equity']) + F(report['nci']), F(report['equity']), 'carry equity allocation')
        cash = sum(F(value) for name, value in result['closing_adjusted'].items() if name.endswith('.cash'))
        eq(cash, F(report['cash']), 'cash from adjusted accounts')
    return count

success = False
try:
    manifest = read(root / 'intragroup-manifest.json')
    check('isolated Python', sys.flags.isolated, 1)
    check('recorded Python version', sys.version.split()[0], '3.11.15')
    for name, row in manifest['entries'].items(): check('before/' + name, digest(root / name), row['sha256'])
    sys.path.insert(0, str(root / 'scripts'))
    retained_results = {}
    for unit in manifest['units']:
        unit_id = unit['id']; folder = root / 'data/accounting-master' / unit['unit']
        candidate = load(unit_id.replace('-', '_') + '_candidate', folder / 'reference.py')
        fixture = load(unit_id.replace('-', '_') + '_oracle', folder / 'fixtures.py')
        unit_outputs = []
        for population, count_field in [('cases', 'cases'), ('controls', 'controls')]:
            rows = read(folder / ('attempt-01/' + population + '.json'))
            check(unit_id + '/' + population + '/population', len(rows), unit[count_field])
            selected = rows[:1] if args.smoke else rows
            for old in selected:
                label = unit_id + '/' + population + '/' + old['id']
                body = deepcopy(old['request']); before = deepcopy(body)
                actual = candidate.report(body)
                unit_outputs.append(dict(id=old['id'], population=population, request=body, result=actual))
                check(label + '/complete_result', actual, old['result'])
                check(label + '/immutable_request', body, before)
                check(label + '/admissions', {k: actual[k] for k in ['source_admission', 'accounting_admission', 'posting_authorized', 'report_authorized', 'executed']},
                      {k: False for k in ['source_admission', 'accounting_admission', 'posting_authorized', 'report_authorized', 'executed']})
                if population == 'cases':
                    params = fixture_arguments(unit_id, old['id'])
                    check(label + '/authored_request', fixture.fixture(*params), old['request'])
                    if 'carry' not in unit_id:
                        expected = fixture.expected(*params)
                    elif actual['status'] == 'tax_method_required':
                        check(label + '/retained_request', actual['request'], body)
                        prior_params = params[:2] + ([params[3]] if unit_id == 'upstream-carry' else [])
                        check(label + '/retained_prior', actual['prior_result'], fixture.prior(*prior_params)['result'])
                        expected = {}
                    else:
                        expected = fixture.expected(*params[:-1])
                    for key, value in expected.items(): check(label + '/independent/' + key, actual[key], value)
                    retained_results[(unit_id, old['id'])] = actual
                independent.append(dict(case=label, assertions=rational_checks(actual), passed=True))
            counts.append(dict(unit=unit_id, population=population, exchanges=len(selected)))
        dump(unit_id + '-exchanges.json', unit_outputs)
        outputs.append(unit_id + '-exchanges.json')
    # Absolute manuscript anchors are independent of generated expectation code.
    if not args.smoke:
        anchors = [
            ('realisation', 'proportional/cash/credit/recognised/1/2', dict(profit='39/1', owners_profit='483/16', nci_profit='141/16', assets_closing='416/1', liabilities_closing='113/4', equity_closing='1551/4')),
            ('downstream-carry', '0/1/credit/1/1/known', dict(profit='-2/1', owners_profit='3/8', nci_profit='-19/8', cash='310/1', assets='1627/4', liabilities='57/2', equity='1513/4')),
            ('upstream-carry', '0/1/credit/1/1/recognised/known', dict(profit='-2/1', owners_profit='3/8', nci_profit='-19/8', cash='290/1', assets='1547/4', liabilities='57/2', equity='1433/4')),
            ('upstream-carry', '0/1/credit/1/1/unrecognised/known', dict(profit='1/2', owners_profit='9/4', nci_profit='-7/4', cash='290/1', assets='1547/4', liabilities='57/2', equity='1433/4'))]
        for unit_id, identifier, expected in anchors:
            for key, value in expected.items(): check('manuscript/' + unit_id + '/' + identifier + '/' + key, retained_results[(unit_id, identifier)]['report'][key], value)
        recognized = retained_results[('upstream-carry', '0/1/credit/1/1/recognised/known')]
        unrecognized = retained_results[('upstream-carry', '0/1/credit/1/1/unrecognised/known')]
        for key in ['assets', 'liabilities', 'equity', 'owners_equity', 'nci', 'cash']:
            check('same cumulative full-sale closing/' + key, recognized['report'][key], unrecognized['report'][key])
        for mutation in ['cash', 'balanced_nci_attribution']:
            changed = deepcopy(recognized)
            if mutation == 'cash': changed['report']['cash'] = frac(F(changed['report']['cash']) + 1)
            else:
                changed['report']['nci_profit'] = frac(F(changed['report']['nci_profit']) + 1)
                changed['report']['owners_profit'] = frac(F(changed['report']['owners_profit']) - 1)
            try: rational_checks(changed)
            except AssertionError as exc:
                check('independent checker rejects/' + mutation, True)
                independent.append(dict(mutation=mutation, rejected=True, reason=str(exc)))
            else: check('independent checker rejects/' + mutation, False)
    for name, row in manifest['entries'].items(): check('after/' + name, digest(root / name), row['sha256'])
    observed_project_reads = {str(Path(p).relative_to(root)) for p, mode, cat in accesses
                              if mode == 'read' and cat == 'bundle' and Path(p).is_file()}
    check('all observed project reads declared', observed_project_reads <= set(manifest['entries']) | {'intragroup-manifest.json'})
    check('no observed undeclared access', violations, [])
    success = True
except Exception:
    dump('failure.json', dict(error=traceback.format_exc(), checks_completed=len(checks)))
finally:
    dump('checks.json', dict(passed=success, checks=len(checks), rows=checks, populations=counts,
        normalization='none', smoke_only=args.smoke,
        independent_assertions=sum(r.get('assertions', 0) for r in independent),
        exchanges=sum(r['exchanges'] for r in counts)))
    dump('independent-checks.json', independent)
    distributions = {name: importlib.metadata.version(name) for name in
        ['jsonschema', 'attrs', 'referencing', 'rpds-py', 'jsonschema-specifications']}
    saved_accesses = sorted(accesses)
    dump('access-audit.json', dict(violations=violations, accesses=saved_accesses,
        dynamic_libraries=sorted(libraries), scope='Python-visible events after driver bootstrap, before project imports; startup and arbitrary native syscalls excluded'))
    installed = {p: digest(Path(p)) for p, mode, cat in saved_accesses
                 if mode == 'read' and cat == 'installed_environment' and Path(p).is_file()}
    dump('environment-lock.json', dict(python=sys.version, executable=sys.executable,
        prefixes=sorted(map(str, environment)), distributions=distributions,
        observed_installed_file_hashes=installed, clean_install=False))
    dump('run-manifest.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        passed=success, command=[sys.executable, '-I', '-B', *sys.argv],
        environment=sys.version, cpu_gpu='CPU only; GPUs intentionally hidden',
        git_commit='N/A for this copied tree; exact original per-file identities retained',
        data_version=digest(root / 'intragroup-manifest.json'), random_seeds='N/A: exact deterministic arithmetic',
        wall_seconds=time.monotonic() - started,
        plan='docs/plans/accounting-intragroup-evidence-replay-20261027.md',
        result='data/accounting-master/intragroup-evidence-replay-20261027/result.md',
        output=str(out), outputs=outputs, smoke_only=args.smoke))
print(json.dumps(dict(passed=success, checks=len(checks), exchanges=sum(r['exchanges'] for r in counts),
                     independent_assertions=sum(r.get('assertions', 0) for r in independent), smoke_only=args.smoke)))
if not success: raise SystemExit(1)
