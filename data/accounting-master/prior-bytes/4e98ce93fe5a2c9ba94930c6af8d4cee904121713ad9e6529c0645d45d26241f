#!/usr/bin/env python3
"""Execute catalogued P03 obligations with durable protection provenance."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import re
import shlex
import sys
import time
import unittest
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]
CHANGED = ['scripts/core0_frontends_v1.py', 'scripts/core0_ir_v1.py',
           'scripts/check_accounting_p03.py', 'tests/test_accounting_p03.py',
           'docs/design/spec/core0-lowering-profile-v1.md',
           'docs/design/fixtures/p03-lowering-cases-v1.json']
OUTPUTS = ['data/accounting-master/deliverables/P03/' + name
           for name in ('conformance.json', 'result.md', 'progress.md')]
PHASE_FILES = CHANGED + OUTPUTS
PHASE_INVENTORY = 'data/accounting-master/runs/20261002T181809-4cb566e0/P03/phase-entry-inventory.json'
EXECUTION_INVENTORY = 'data/accounting-master/runs/20261002T221346-d54a6552/P03/execution-0/pre-edit-files.json'
APPROVED_PLAN = 'data/accounting-master/runs/20261002T221346-d54a6552/P03/approved-plan.json'


def digest(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate inventory key: ' + key)
        result[key] = value
    return result


def _inventory(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != relative:
        raise ValueError('inventory path must be repository-relative')
    data = json.loads((root / path).read_text(), object_pairs_hook=_unique_object)
    if not isinstance(data, dict) or not data:
        raise ValueError('inventory must be a nonempty path-to-SHA256 object')
    for name, value in data.items():
        p = Path(name)
        if (p.is_absolute() or '..' in p.parts or p.as_posix() != name
                or not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value)):
            raise ValueError('invalid inventory entry: ' + name)
    return data


def capture_protection(root, historical_path, execution_path, writable=PHASE_FILES,
                       required_paths=()):
    """Keep historical differences separate; never replace the execution baseline."""
    errors = []
    inventories = []
    for name in (historical_path, execution_path):
        try:
            inventories.append(_inventory(root, name))
        except (OSError, ValueError) as exc:
            errors.append(f'{name}: {exc}')
            inventories.append({})
    historical, execution = inventories
    protected = sorted((set(historical) | set(execution) | set(required_paths)) - set(writable))
    absent = sorted(set(protected) - set(execution))
    if absent:
        errors.append('execution inventory omits protected paths: ' + ', '.join(absent))
    before = {p: digest(root / p) for p in protected}
    return {
        'historical_inventory': historical_path,
        'execution_inventory': execution_path,
        'inventory_hashes': {p: digest(root / p) for p in (historical_path, execution_path)},
        'excluded_phase_files': list(writable),
        'errors': errors,
        'execution_baseline': {p: execution.get(p) for p in protected},
        'before': before,
        'missing_before_check': [p for p, h in before.items() if h is None],
        'changed_since_execution_entry': [p for p in protected if before[p] != execution.get(p)],
        'historical_differences': [
            {'path': p, 'phase_entry_sha256': historical[p], 'execution_entry_sha256': execution[p],
             'attribution': 'Predates this execution, as recorded by the supervisor pre-edit inventory.'}
            for p in sorted(set(historical) & set(execution) - set(writable))
            if historical[p] != execution[p]],
    }


def finish_protection(root, report):
    report['after'] = {p: digest(root / p) for p in report['before']}
    report['changed_during_check'] = [p for p in report['before'] if report['before'][p] != report['after'][p]]
    report['changed_inventory_records'] = [p for p, h in report['inventory_hashes'].items()
                                           if h is None or digest(root / p) != h]
    report['passed'] = not any(report[k] for k in (
        'errors', 'missing_before_check', 'changed_since_execution_entry',
        'changed_during_check', 'changed_inventory_records'))
    return report


def obligation_status(catalog, observations):
    required_counts = Counter(c['id'] for c in catalog['obligations'])
    observed_counts = Counter(c['id'] for c in observations)
    required, observed = set(required_counts), set(observed_counts)
    return {
        'obligations_required': len(required), 'obligations_run': len(observed),
        'missing': sorted(required - observed), 'uncatalogued': sorted(observed - required),
        'duplicate_ids': sorted(k for k in required | observed
                                if required_counts[k] > 1 or observed_counts[k] > 1),
        'failed_observations': [c['id'] for c in observations if c.get('passed') is not True],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--execution-inventory', default=EXECUTION_INVENTORY)
    args = parser.parse_args(argv)
    out = Path(args.output_dir).resolve()
    if out != ROOT / 'data/accounting-master/deliverables/P03':
        parser.error('output-dir must be the declared P03 output directory')
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    protection = capture_protection(ROOT, PHASE_INVENTORY, args.execution_inventory,
                                    required_paths=('docs/design/spec/core-0.lark',
                                                    'docs/design/spec/core-ir.schema.json',
                                                    'docs/design/fixtures/borrowing.acc',
                                                    'docs/design/fixtures/demo-debt-package.json'))
    code_before = {p: digest(ROOT / p) for p in CHANGED}
    plan_hash = digest(ROOT / APPROVED_PLAN)
    if plan_hash is None:
        protection['errors'].append('approved plan is missing or unreadable')
    else:
        approved = json.loads((ROOT / APPROVED_PLAN).read_text())
        if approved.get('review', {}).get('verdict') != 'AGREE' or approved['review'].get('issues') != []:
            protection['errors'].append('approved plan lacks an issue-free AGREE review')
    # Lazy import keeps checker helpers usable by the required regression suite.
    sys.path.insert(0, str(ROOT / 'tests'))
    import test_accounting_p03 as cases
    cases.OBSERVATIONS.clear()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(cases)
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    catalog = json.loads((ROOT / 'docs/design/fixtures/p03-lowering-cases-v1.json').read_text())
    status = obligation_status(catalog, cases.OBSERVATIONS)
    finish_protection(ROOT, protection)
    code_after = {p: digest(ROOT / p) for p in CHANGED}
    changed_code = [p for p in CHANGED if code_before[p] is None or code_before[p] != code_after[p]]
    if digest(ROOT / APPROVED_PLAN) != plan_hash:
        protection['errors'].append('approved plan changed during check')
        protection['passed'] = False
    passed = (result.wasSuccessful() and result.testsRun > 0 and not result.skipped
              and bool(status['obligations_required']) and not changed_code and protection['passed']
              and not any(status[k] for k in ('missing', 'uncatalogued', 'duplicate_ids', 'failed_observations')))
    command_args = sys.argv[1:] if argv is None else argv
    payload = {
        'schema_version': 'accdsl.p03.conformance.v1', 'passed': bool(passed), 'profile': catalog['profile'],
        'manifest': {
            'git_commit': 'unavailable: existing marker is not a usable repository',
            'command': shlex.join(['python3', '-B', 'scripts/check_accounting_p03.py'] + command_args),
            'working_directory': str(ROOT), 'executable': sys.executable,
            'environment': {'python': platform.python_version(), 'lark': version('lark'), 'jsonschema': version('jsonschema')},
            'hardware': 'CPU only; no accelerator framework imported', 'random_seeds': 'N/A: deterministic checks',
            'data_version': 'synthetic P03 bindings and digest-locked DemoDebt@1',
            'started_utc': started_utc, 'utc': datetime.now(timezone.utc).isoformat(),
            'wall_seconds': round(time.monotonic() - started, 3),
            'plan': APPROVED_PLAN, 'plan_sha256': plan_hash,
            'execution_inventory': args.execution_inventory,
            'result': OUTPUTS[1], 'outputs': OUTPUTS[:2], 'changed_files': PHASE_FILES,
            'changed_this_execution': [p for p in CHANGED
                if code_after[p] != _inventory(ROOT, args.execution_inventory).get(p)]
                if not protection['errors'] else 'unavailable: protection evidence failed'},
        'tests': dict(status, methods_run=result.testsRun, skipped=result.skipped,
                      failures=[{'test': str(t), 'detail': d} for t, d in result.failures + result.errors],
                      runner_output=stream.getvalue()),
        'observations': cases.OBSERVATIONS, 'hashes': code_after,
        'checked_input_integrity': {'before': code_before, 'after': code_after, 'changed': changed_code},
        'protected_files': protection,
        'requirement_coverage': {
            'MC02': 'bounded context and numeric/source provenance',
            'MC04': 'separate evidence, assumptions, alternatives and global constraints',
            'MC10': 'explicit factual admission and scenario assumptions; broader uncertainty unsupported',
            'MC20': 'DemoDebt package digest/applicability and report policies; cross-company mappings unsupported',
            'MC23': 'independently authored matched typed/text programs; no authoring superiority claim',
            'MC24': 'bounded parsing, binding, typing and independent IR rejection'},
        'unsupported': catalog['unsupported'],
        'acceptance': {'engineering': bool(passed), 'accounting_validity': 'not established',
                       'forecast_validity': 'not established', 'human_acceptance': 'pending', 'whole_gap_closure': False},
    }
    decision = 'PASS' if passed else 'FAIL'
    positive = [c for c in cases.OBSERVATIONS if 'observed_interest' in c]
    examples = '\n'.join(f"| {c['id']} | {', '.join(c['expected_interest'])} | {', '.join(c['observed_interest'])} |"
                         for c in positive)
    historical_count = len(protection['historical_differences'])
    result_text = f'''# P03 bounded source lowering result

{decision}: {result.testsRun} unittest methods executed {status['obligations_run']} of
{status['obligations_required']} catalogued obligations. This is deterministic
Core0.1 engineering evidence; G2, G12 and G15 remain open beyond this profile.

Source programs pass through parsing, name binding, package/type/context checks
and shared IR construction. Independently authored typed declarations enter the
same semantic stages. The independent validator checks the resulting IR. Both
entrypoints preserve package locks, source context, assumptions and alternatives.
The executed checks cover renamed programs, changed principal and stress rates,
let arithmetic, formatting, unsupported operations and schema-valid corruptions.
The compiler does not read authored expected IR to produce its results.

The generated expressions give the following exact one-year interest amounts in
USD at fixed-fraction endpoints 1 and 0. These arithmetic diagnostics are separate
from accounting execution and empirical forecasting.

| Input | Expected interest | Observed interest |
| --- | --- | --- |
{examples}

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| {decision} for bounded engineering conformance | frontend agreement, input sensitivity and semantic rejection jointly tested | missing={len(status['missing'])}; uncatalogued={len(status['uncatalogued'])}; duplicate={len(status['duplicate_ids'])}; failed observations={len(status['failed_observations'])}; test failures/errors={len(result.failures)+len(result.errors)}; skips={len(result.skipped)}; protected inputs passed={protection['passed']}; changed check inputs={len(changed_code)} | language breadth and shared-implementation bugs | independent result review if PASS; focused repair if FAIL | full G2/G12/G15 closure, accounting validity, forecast validity or human acceptance |

Protection uses the durable historical inventory `{PHASE_INVENTORY}` and current
supervisor execution inventory `{args.execution_inventory}`. There are
{historical_count} historical differences predating this execution, attributed by
those two records rather than ignored or treated as new worker edits. Missing
inventory evidence, absent protected paths, changes since execution entry or
changes during the check prevent a pass. No temporary snapshot is required.
Conformance JSON preserves the inventory hashes, per-file baselines, actual IR,
bindings, source maps, input hashes, diagnostics and the complete unittest output.

Specification is recorded in the versioned profile. The two versioned modules
implement the declared slice; the catalog enumerates tested invariants. Accounting
validity and empirical forecast validity are not established; human acceptance is
pending. History families remain Unknown/PartialSearch, with zero completed cells,
one unsearched cell and no invented witnesses or solver results. MC02/MC04/MC10/
MC20/MC23/MC24 receive bounded evidence, while all MC01–MC35 and G1–G18 retain wider
obligations.

The strongest alternative explanation for frontend agreement is a shared compiler
bug. Independent arithmetic, comparison with corresponding authored IR fields and
schema-valid corruptions constrain that explanation without proving the general
language. An in-profile counterexample would overturn this engineering result.
No stochastic ranking, performance comparison or authoring superiority is claimed.

Actual command: `{payload['manifest']['command']}`. Approved plan:
`{APPROVED_PLAN}`. Environment: Python {platform.python_version()}, Lark
{version('lark')}, jsonschema {version('jsonschema')}; CPU only, no accelerator
framework imported. Check wall time: {payload['manifest']['wall_seconds']} seconds.
Git commit unavailable; content hashes provide file provenance. Changed phase
files and this execution's source changes are enumerated in the manifest. The
standalone unittest outcome and final integrity inspection are in progress.md.

Residuals: {', '.join(catalog['unsupported'])}. General language support, arbitrary
and cross-company mappings, broader uncertainty, reconstruction, accounting
execution and human acceptance require separate evidence.
'''
    out.mkdir(parents=True, exist_ok=True)
    (out / 'conformance.json').write_text(json.dumps(payload, indent=2, ensure_ascii=True) + '\n')
    (out / 'result.md').write_text(result_text)
    print(json.dumps({'passed': bool(passed), 'methods': result.testsRun,
                      'obligations': status['obligations_run'], 'missing': status['missing'],
                      'failures': len(result.failures) + len(result.errors),
                      'protected_inputs_passed': protection['passed'],
                      'protection_errors': protection['errors'],
                      'changed_since_execution_entry': protection['changed_since_execution_entry'],
                      'changed_during_check': protection['changed_during_check'],
                      'historical_differences': historical_count}))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
