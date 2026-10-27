"""Exact source/native checks with independent printed-quantity expectations."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import debt_measurement as adapter

ROOT = adapter.ROOT
HERE = 'data/accounting-master/company-state-debt-measurement-20261028'
PLAN = 'docs/plans/company-state-debt-measurement-20261028.md'
BUDGET = dict(max_slots=0, max_formula_nodes=10000, max_integer_assignments=1,
              max_cells=1, elapsed_ms=5000, solver_timeout_ms=1000, solver_rlimit=1000000)
FILES = dict(
    debt='data/accounting-master/company-state-debt-source-20261028/attempt-01/source-to-state.json',
    timing='data/accounting-master/company-state-source-timing-20261028/attempt-01/source-time-card.json',
    issuance='data/accounting-master/company-state-source-card-20261028/attempt-01/source-to-state.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    cards = {k: json.loads((ROOT / p).read_text()) for k, p in FILES.items()}
    identities = {k: adapter.identity(v) for k, v in cards.items()}
    checks, controls = [], []
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    def construct(values=None, hashes=None, cutoff=None):
        v = cards if values is None else values
        h = identities if hashes is None else hashes
        return adapter.construct(v['debt'], v['timing'], v['issuance'], h, cutoff=cutoff)
    before = deepcopy(cards)
    result = construct()
    definition = result['definition']
    native = adapter.temporal.assess(definition, BUDGET)
    check('native feasibility', native['status'], 'conditionally_feasible')
    expected = dict(principal='97341/1', unamortized_deduction='321/1', hedge_deduction='358/1',
        carrying='96662/1', current_carrying='10912/1', noncurrent_carrying='85750/1',
        principal_bucket_2025='10930/1', principal_bucket_2026='12342/1',
        principal_bucket_2027='9936/1', principal_bucket_2028='7800/1',
        principal_bucket_2029='5153/1', principal_bucket_thereafter='51180/1')
    check('complete expected reported quantities', set(definition['observations']), set(expected))
    for key, amount in expected.items():
        observation = definition['observations'][key]
        check('independent displayed value ' + key, observation['interval'], adapter.point(amount))
        check('instant preserved ' + key, observation['type']['time'], dict(kind='instant', at='2024-09-28'))
        check('USD million scale ' + key, observation['type']['value_type']['scale'], '1000000/1')
    check('native independent witness', adapter.temporal.check_witness(definition, BUDGET, expected), True)
    check('solver agrees with complete independent values', native.get('joint_assessment', {}).get('witness'), expected)
    check('principal occurrences share quantity', [r['id'] for r in result['source_mapping']['principal']], ['f-942', 'f-961'])
    check('all source occurrences retained', sum(len(r) for r in result['source_mapping'].values()), 13)
    check('no duplicated principal variable', len(definition['observations']), 12)
    check('all printed relations', [r['id'] for r in definition['relations']],
          ['principal_to_carrying', 'current_noncurrent', 'principal_allocation'])
    check('principal independent identity', Q(expected['principal']) - Q(expected['unamortized_deduction']) - Q(expected['hedge_deduction']), Q(expected['carrying']))
    check('carrying independent identity', Q(expected['current_carrying']) + Q(expected['noncurrent_carrying']), Q(expected['carrying']))
    check('maturity independent identity', sum(Q(v) for k, v in expected.items() if k.startswith('principal_bucket_')), Q(expected['principal']))
    check('next bucket differs from carrying', Q(expected['principal_bucket_2025']) - Q(expected['current_carrying']), Q(18))
    check('issuance exact economic zero withheld', result['exact_economic_zero'], False)
    check('issuance period', result['independent_issuance']['type']['time'],
          dict(kind='period', start='2023-10-01', end_exclusive='2024-09-29'))
    check('no invented debt bridge', result['independent_issuance_relation'], None)
    check('all original source cards retained', result['source_cards'], cards)
    check('inputs immutable', cards, before)
    for flag in ['source_admission', 'accounting_admission', 'actual_actor_knowledge', 'forecast_admission']:
        check('no promotion ' + flag, result[flag], False)
    for key in ['executable_opening', 'probability_model', 'policy_input']:
        check('no invented ' + key, result[key], None)

    # Recompute proposed identities for semantic mutations; validation must not
    # rely solely on the caller's hash approval to justify the financial meaning.
    mutations = [
        ('missing fact', lambda x: x['debt']['facts'].pop()),
        ('duplicate fact', lambda x: x['debt']['facts'].append(deepcopy(x['debt']['facts'][0]))),
        ('concept substitution', lambda x: x['debt']['facts'][0].update(concept='{http://fasb.org/us-gaap/2024}LongTermDebt')),
        ('issuer extension silently standardized', lambda x: x['debt']['facts'][2].update(concept='{http://fasb.org/us-gaap/2024}HedgeAccountingAdjustmentsRelatedToLongTermDebt')),
        ('wrong caption', lambda x: x['debt']['facts'][0].update(pdf_caption='Total carrying debt')),
        ('wrong source sign', lambda x: x['debt']['facts'][1].update(pdf_reconciliation_sign=1)),
        ('wrong fact scale', lambda x: x['debt']['facts'][0].update(reported_usd='97341')),
        ('wrong precision', lambda x: x['debt']['facts'][0].update(decimals='0')),
        ('wrong fact context', lambda x: x['debt']['facts'][0].update(context='c-1')),
        ('wrong issuer', lambda x: x['debt'].update(issuer='Other')),
        ('wrong instant', lambda x: x['debt'].update(as_of='2024-09-29')),
        ('wrong units', lambda x: x['debt'].update(unit='USD')),
        ('archive mismatch', lambda x: x['timing']['xbrl_binding'].update(sha256='0' * 64)),
        ('instance mismatch', lambda x: x['debt'].update(instance_sha256='0' * 64)),
        ('unreviewed admission', lambda x: x['debt'].update(source_admission=True)),
        ('false exact principal duplicate', lambda x: x['debt']['facts'][-1].update(reported_usd='97342000000', reported_usd_million=97342)),
    ]
    for name, mutate in mutations:
        values = deepcopy(cards)
        mutate(values)
        try:
            construct(values, {k: adapter.identity(v) for k, v in values.items()})
            reason = None
        except ValueError as exc:
            reason = str(exc)
        check('refuse ' + name, reason is not None, True)
        controls.append(dict(case=name, status='invalid' if reason else 'accepted', reason=reason))
    altered = deepcopy(cards)
    altered['debt']['distinctions'].append('modified bytes')
    try:
        construct(altered)
        changed_refused = False
    except ValueError as exc:
        changed_refused = str(exc) == 'input_identity:debt'
    check('external content identity binds all metadata', changed_refused, True)

    # Well-typed financial mistakes must fail the actual printed equations.
    numeric_controls = [
        ('principal substituted for carrying', lambda d: d['observations']['carrying'].update(interval=adapter.point('97341/1'))),
        ('next bucket substituted for current carrying', lambda d: d['observations']['current_carrying'].update(interval=adapter.point('10930/1'))),
        ('adjustment added instead of subtracted', lambda d: d['relations'][0]['terms'][1].update(coefficient='1/1')),
    ]
    for name, mutate in numeric_controls:
        d = deepcopy(definition)
        mutate(d)
        a = adapter.temporal.assess(d, BUDGET)
        check(name, a['status'], 'conditionally_infeasible')
        check(name + ':rechecked contradiction', all(c['rechecked'] == 'unsat' for c in a.get('joint_assessment', {}).get('conflicts', [])), True)
        controls.append(dict(case=name, result=a))
    for name, where, value in [
        ('future payment mistaken for observation', 'time', dict(kind='instant', at='2025-09-28')),
        ('wrong scale', 'scale', '1/1'), ('wrong currency', 'dimensions', {'currency:EUR': 1}),
        ('wrong perimeter', 'context', dict(issuer_cik='0000320193', perimeter='single_legal_entity'))]:
        d = deepcopy(definition)
        typ = d['observations']['principal_bucket_2025']['type']
        (typ if where == 'time' else typ['value_type'])[where] = value
        a = adapter.temporal.assess(d, BUDGET)
        check(name, a['status'], 'invalid')
        controls.append(dict(case=name, result=a))
    unused = deepcopy(definition)
    unused['observations']['issuance'] = deepcopy(result['independent_issuance'])
    check('independent observation cannot be silently attached', adapter.temporal.assess(unused, BUDGET)['status'], 'invalid')
    missing = deepcopy(definition)
    missing['relations'][0]['identity_premise'] = None
    check('missing interpretation remains unresolved', adapter.temporal.assess(missing, BUDGET)['status'], 'unresolved')
    check('resource exhaustion not infeasible', adapter.temporal.assess(definition, dict(BUDGET, max_cells=0))['status'], 'unknown')
    for cutoff in ('2024-10-31', '2024-11-01', '2026-10-28'):
        query = construct(cutoff=cutoff)
        check('no inferred historical access ' + cutoff, query['status'], 'historical_information_unresolved')
        check('audit definition retained ' + cutoff, query['definition'], definition)
        check('no actor input ' + cutoff, query['policy_input'], None)

    # Preserve the full outstanding issuer population, not only its count.
    deps_path = 'data/accounting-master/company-cases-current-20261028/attempt-01/current-decisions.json'
    targets_path = 'data/accounting-master/selected-reading-history-20261027/attempt-01/result.json'
    deps = json.loads((ROOT / deps_path).read_text())
    targets = json.loads((ROOT / targets_path).read_text())
    obligations = {k: deepcopy(v['target_obligations']) for k, v in targets['attachments'].items()}
    result['issuer_dependency_rows'] = deepcopy(deps['rows'])
    result['target_obligations'] = obligations
    check('all15 dependency rows', len(result['issuer_dependency_rows']), 15)
    check('all180 obligations', sum(map(len, obligations.values())), 180)
    check('no issuer target admitted', all(r['original_target_ready'] is False for r in deps['rows']), True)

    source_hashes = {}
    for manifest_path, key in [
        ('data/accounting-master/company-state-debt-source-20261028/attempt-01/run-manifest.json', 'inputs'),
        ('data/accounting-master/company-state-source-timing-20261028/attempt-01/run-manifest.json', 'source_hashes')]:
        manifest = json.loads((ROOT / manifest_path).read_text())
        source_hashes[manifest_path] = sha256((ROOT / manifest_path).read_bytes()).hexdigest()
        for path, expected_hash in manifest[key].items():
            actual = sha256((ROOT / path).read_bytes()).hexdigest()
            check('parent input preserved ' + path, actual, expected_hash)
            source_hashes[path] = actual
    modules = [adapter, adapter.temporal, adapter.temporal.joint, adapter.temporal.core,
               adapter.temporal.joint.types, adapter.temporal.joint.solver]
    files = [Path(__file__), ROOT / PLAN, *(ROOT / p for p in FILES.values()),
             ROOT / deps_path, ROOT / targets_path, *(Path(m.__file__) for m in modules)]
    source_hashes.update({str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files})
    failed = [c for c in checks if not c['passed']]
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), failed=failed,
                        reported_quantities=12, source_occurrences=13, independent_period_observations=1)
    manifest = dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], environment=sys.version, z3=adapter.temporal.joint.z3.get_version_string(),
        cpu_gpu='CPU-only exact source and native measurement validation; no accelerator imports',
        random_seeds='N/A deterministic', data_version='Retained Apple2024 Note9 plus separate selected issuance reading',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-start,
        plan_file=PLAN, result_file=HERE+'/result.md', source_hashes=source_hashes)
    def safe(x):
        if isinstance(x, set): return sorted(x)
        if isinstance(x, Q): return adapter.rational(x)
        raise TypeError(type(x).__name__)
    for name, value in [('construction.json', result), ('native-result.json', native),
                        ('independent-witness.json', expected), ('controls.json', controls),
                        ('checks.json', checks), ('verification.json', verification), ('run-manifest.json', manifest)]:
        (out / name).write_text(json.dumps(value, indent=2, default=safe) + '\n')
    print(json.dumps(verification, default=safe))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
