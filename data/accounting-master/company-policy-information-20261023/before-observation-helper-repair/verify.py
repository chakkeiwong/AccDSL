"""Deterministic dependency-timing checks; default execution is read-only."""
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
import argparse
import json
import os
import platform
import subprocess
import time

from policy_information import HERE, ROOT, query, schema, digest
from policy_context import context, file_hash, PARENT_NAME, POLICY, INFORMATION, EXCHANGE
from synthetic import make, change_observation


def protected_files():
    saved = HERE / 'baseline.json'
    if saved.exists():
        locked = json.loads(saved.read_text())
    else:
        locked = json.loads((HERE.parent / 'company-text-20261023/baseline.json').read_text())
        for directory in [POLICY, INFORMATION, EXCHANGE, HERE.parent / 'company-text-20261023']:
            for p in directory.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:
                    name = str(p.relative_to(ROOT))
                    if name in locked and locked[name] != file_hash(p):
                        raise AssertionError('Predecessor changed: ' + name)
                    locked[name] = file_hash(p)
        manuscript = ROOT / 'docs/design/proposal/manuscript-company-authoring-20261023'
        for p in manuscript.rglob('*'):
            if p.is_file() and p.suffix in ['.tex', '.bib', '.pdf']:
                locked[str(p.relative_to(ROOT))] = file_hash(p)
        for p in [HERE.parent / 'company-authoring-integration-20261023/coverage-delta.json',
                  HERE.parent / 'company-path-admission-20261023/reference-locks.json']:
            locked[str(p.relative_to(ROOT))] = file_hash(p)
    changed = [name for name, h in locked.items()
               if not (ROOT / name).is_file() or file_hash(ROOT / name) != h]
    if changed:
        raise AssertionError('Protected baseline mismatch: ' + repr(changed[:5]))
    return locked


def conformance():
    c = context()
    fixture = make(c['parent_fixture'], c['parent'], c['policy'],
                   c['trust'].materializer, c['materialization']['child_path_sha256'])
    checks, witnesses = [], {}

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})

    def evaluate(f=None, *, mode='investor_information', cutoff='2025-03-13T00:00:00Z',
                 trust=None, **changes):
        f = fixture if f is None else f
        t = c['trust'] if trust is None else trust
        t = replace(t, observation_hashes=frozenset(f['trusted_observation_hashes']))
        args = dict(trust=t, exchange=c['exchange'], raw=c['raw'], parent_name=PARENT_NAME,
                    parent_declaration=f['parent_declaration'], declaration=f['declaration'],
                    observations=f['observations'], policy=c['policy'],
                    materialization=c['materialization'], child_result=c['result'],
                    mode=mode, cutoff=cutoff)
        args.update(changes)
        return query(**args)

    def case(name, expected, f=None, **kwargs):
        value = evaluate(f, **kwargs)
        witnesses[name] = value
        check(name, value['status'] == expected)
        return value

    before = digest(fixture)
    schedules = [
        ('source_only', 'investor_information', '2025-03-03T00:00:00Z', 'ineligible'),
        ('parent_only', 'investor_information', '2025-03-08T00:00:00Z', 'ineligible'),
        ('policy_public_method_unavailable', 'investor_information', '2025-03-11T00:00:00Z', 'ineligible'),
        ('method_public_day_start', 'investor_information', '2025-03-12T00:00:00Z', 'unresolved'),
        ('method_public_day_last_second', 'investor_information', '2025-03-12T23:59:59Z', 'unresolved'),
        ('method_public_day_complete', 'investor_information', '2025-03-13T00:00:00Z', 'eligible_synthetic'),
        ('policy_internal_method_unavailable', 'system_as_of', '2025-03-09T11:00:00Z', 'ineligible'),
        ('method_before_authorship', 'system_as_of', '2025-03-11T08:59:59Z', 'ineligible'),
        ('method_before_ingestion', 'system_as_of', '2025-03-11T09:59:59Z', 'ineligible'),
        ('method_before_acceptance', 'system_as_of', '2025-03-11T10:59:59Z', 'ineligible'),
        ('method_acceptance_exact', 'system_as_of', '2025-03-11T11:00:00Z', 'eligible_synthetic')]
    for name, mode, cutoff, expected in schedules:
        case(name, expected, mode=mode, cutoff=cutoff)
    check('parent_pass_does_not_admit_policy',
          witnesses['parent_only']['parent_information']['status'] == 'eligible_synthetic')
    check('source_pass_does_not_admit_assumptions',
          witnesses['source_only']['parent_information']['source_timing']['status'] == 'eligible_synthetic')
    archival = case('archival', 'archival_synthetic', mode='archival_exploration', cutoff=None)
    check('archival_without_temporal_claim', not archival['temporal_admission'])
    check('selector_pure', before == digest(fixture))
    check('protected_generator_still_unadmitted', c['materialization']['information_admission'] ==
          {'status': 'unresolved', 'reason': 'policy_information_not_admitted'})

    for slot in ['policy', 'materializer']:
        for event in ['authored', 'published', 'ingested', 'accepted']:
            f = deepcopy(fixture)
            item = next(d for d in f['declaration']['declarations'] if d['slot'] == slot)
            item['events'][event] = {'status': 'unknown', 'reason': 'No timing evidence'}
            mode = 'system_as_of' if event in ['ingested', 'accepted'] else 'investor_information'
            case('missing_' + slot + '_' + event, 'unresolved', f, mode=mode)
    f = deepcopy(fixture)
    for d in f['declaration']['declarations']:
        for event in d['events']:
            d['events'][event] = {'status': 'unknown', 'reason': 'No timing evidence'}
    case('archival_retains_untimed_policy', 'archival_synthetic', f,
         mode='archival_exploration', cutoff=None)
    f = deepcopy(fixture)
    policy_refs = {r['observation_sha256'] for d in f['declaration']['declarations']
                   for r in d['events'].values()}
    f['trusted_observation_hashes'] = sorted(set(f['trusted_observation_hashes']) - policy_refs)
    case('parent_trust_does_not_authenticate_policy_or_method', 'unresolved', f)
    f = deepcopy(fixture)
    f['trusted_observation_hashes'] = []
    case('packet_cannot_self_authenticate', 'unresolved', f)
    f = deepcopy(fixture)
    change_observation(f, 'policy', 'published', audience='internal')
    case('private_policy_not_public', 'unresolved', f)
    case('private_policy_system_view', 'eligible_synthetic', f, mode='system_as_of')
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'published', audience='internal')
    case('private_method_not_public', 'unresolved', f)
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'published',
                       time='2025-03-12T15:00:00Z', precision='utc_instant')
    case('instant_publication_before', 'ineligible', f, cutoff='2025-03-12T14:59:59Z')
    case('instant_publication_equal', 'eligible_synthetic', f, cutoff='2025-03-12T15:00:00Z')
    f = deepcopy(fixture)
    change_observation(f, 'policy', 'published', time='2025-03-09T09:00:00Z', precision='utc_instant')
    change_observation(f, 'materializer', 'accepted', time='2025-03-11T10:00:00Z')
    case('equal_authored_publication', 'eligible_synthetic', f)
    case('equal_ingestion_acceptance', 'eligible_synthetic', f,
         mode='system_as_of', cutoff='2025-03-11T10:00:00Z')
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'published', time='2025-03-11', precision='calendar_day_utc')
    case('overlap_leaves_order_unresolved', 'unresolved', f)
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'authored', time='2025-03-11T00:00:00Z')
    change_observation(f, 'materializer', 'published', time='2025-03-10', precision='calendar_day_utc')
    case('publication_day_exclusive_end_before_authorship', 'invalid', f)
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'authored', time='2025-03-10', precision='calendar_day_utc')
    change_observation(f, 'materializer', 'published', time='2025-03-11T00:00:00Z', precision='utc_instant')
    case('authorship_day_precedes_exact_publication', 'eligible_synthetic', f)
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'accepted', time='2025-03-11T08:00:00Z')
    case('acceptance_before_ingestion', 'invalid', f, mode='system_as_of')
    f = deepcopy(fixture)
    change_observation(f, 'materializer', 'accepted', time='2025-03-11T08:00:00Z', trusted=False)
    case('untrusted_impossible_clock_not_fact', 'unresolved', f, mode='system_as_of')
    f = deepcopy(fixture)
    change_observation(f, 'policy', 'published', time='2025-03-10T00:00:00+08:00', precision='utc_instant')
    case('non_utc_clock_rejected', 'invalid', f)

    for field in ['exchange_sha256', 'parent_path_sha256', 'child_path_sha256',
                  'policy_sha256', 'materializer_sha256']:
        f = deepcopy(fixture)
        f['declaration'][field] = '0' * 64
        case('wrong_identity_' + field, 'invalid', f)
    f = deepcopy(fixture)
    f['declaration']['declarations'].pop()
    case('omitted_component', 'invalid', f)
    f = deepcopy(fixture)
    f['declaration']['declarations'][1] = deepcopy(f['declaration']['declarations'][0])
    case('duplicate_component', 'invalid', f)
    f = deepcopy(fixture)
    f['declaration']['trusted'] = True
    case('packet_trust_flag_rejected', 'invalid', f)
    f = deepcopy(fixture)
    change_observation(f, 'policy', 'published', component_sha256='0' * 64)
    case('rehashed_wrong_component_observation', 'invalid', f)
    f = deepcopy(fixture)
    change_observation(f, 'policy', 'published', event='accepted')
    case('rehashed_wrong_event_observation', 'invalid', f)
    f = deepcopy(fixture)
    ref = f['declaration']['declarations'][0]['events']['published']['observation_sha256']
    f['observations'][ref]['time'] = '2025-03-01'
    case('changed_observation_bytes', 'invalid', f)
    f = deepcopy(fixture)
    del f['observations'][ref]
    case('missing_claimed_observation_bytes', 'invalid', f)
    f = deepcopy(fixture)
    change_observation(f, 'year:0', 'published', parent=True,
                       time='2025-03-14', precision='calendar_day_utc')
    case('policy_cannot_mask_late_parent', 'ineligible', f)
    f = deepcopy(fixture)
    f['parent_declaration']['declarations'][1]['events']['published'] = {
        'status': 'unknown', 'reason': 'No parent publication evidence'}
    case('policy_cannot_mask_unknown_parent', 'unresolved', f)
    case('policy_cannot_mask_unknown_source', 'unresolved',
         trust=replace(c['trust'], source_view=lambda mode, cutoff: {'status': 'unresolved'}))
    case('policy_cannot_mask_invalid_source', 'invalid',
         trust=replace(c['trust'], source_view=lambda mode, cutoff: {'status': 'invalid'}))
    packet = deepcopy(c['exchange'])
    packet['trusted'] = True
    case('changed_exchange_lock_rejected', 'invalid', exchange=packet)
    case('binding_only_exchange_rejected', 'invalid',
         trust=replace(c['trust'], validate_exchange=lambda *args: {
             'status': 'validated_synthetic_exchange', 'verification_level': 'content_binding_only'}))

    changed_policy = deepcopy(c['policy'])
    changed_policy['fraction'] = '4/5'
    materialized = c['trust'].generate(c['parent'], changed_policy)
    child_run = c['trust'].execute(materialized['path'])
    changed_args = dict(policy=changed_policy, materialization=materialized, child_result=child_run)
    case('changed_policy_cannot_reuse_declaration', 'invalid', **changed_args)
    f = deepcopy(fixture)
    f['declaration']['policy_sha256'] = digest(changed_policy)
    f['declaration']['child_path_sha256'] = materialized['child_path_sha256']
    case('rebinding_envelope_does_not_retime_policy', 'invalid', f, **changed_args)
    f['declaration']['declarations'][0]['component_sha256'] = digest(changed_policy)
    case('rebinding_component_does_not_retime_observations', 'invalid', f, **changed_args)
    f = make(c['parent_fixture'], c['parent'], changed_policy, c['trust'].materializer,
             materialized['child_path_sha256'])
    case('changed_policy_needs_distinct_observations', 'eligible_synthetic', f, **changed_args)
    # A hypothetical caller-selected implementation descriptor tests rebinding;
    # this is not a claim that alternate code was installed or reviewed.
    changed_method = deepcopy(c['trust'].materializer)
    changed_method['source_sha256'] = '1' * 64
    changed_trust = replace(c['trust'], materializer=changed_method)
    case('changed_method_cannot_reuse_declaration', 'invalid', trust=changed_trust)
    f = deepcopy(fixture)
    f['declaration']['materializer_sha256'] = digest(changed_method)
    f['declaration']['declarations'][1]['component_sha256'] = digest(changed_method)
    case('changed_method_cannot_reuse_observations', 'invalid', f, trust=changed_trust)

    forged = deepcopy(c['materialization'])
    forged['path']['continuations'][0]['operations'][0]['id'] += '-altered'
    forged['child_path_sha256'] = digest(forged['path'])
    f = deepcopy(fixture)
    f['declaration']['child_path_sha256'] = forged['child_path_sha256']
    case('fully_rehashed_altered_materialization', 'invalid', f, materialization=forged)
    forged = deepcopy(c['materialization'])
    forged['allocation_trace'][0]['generated_amount'] = '0/1'
    case('altered_allocation_trace', 'invalid', materialization=forged)
    forged = deepcopy(c['materialization'])
    forged['execution_required'] = 1  # True == 1 under Python equality.
    check('numeric_type_mutation_would_pass_python_equality', forged == c['materialization'])
    case('materialization_json_type_must_match', 'invalid', materialization=forged)
    forged = deepcopy(c['result'])
    forged['years'][1]['report']['lines']['cash']['value'] = '0/1'
    forged['years'][1]['result_sha256'] = digest(forged['years'][1]['report'])
    case('rehashed_altered_accounting_report', 'invalid', child_result=forged)
    forged = deepcopy(c['result'])
    forged['committed'] = 0
    check('result_type_mutation_would_pass_python_equality', forged == c['result'])
    case('accounting_result_json_type_must_match', 'invalid', child_result=forged)
    unknown = deepcopy(c['policy'])
    unknown['fraction'] = 'unknown'
    case('unknown_policy_remains_unresolved', 'unresolved', policy=unknown)
    unsupported = deepcopy(c['policy'])
    unsupported['collection_operations'] = unsupported['collection_operations'][:1]
    unsupported['installment_shares'] = ['1/1']
    case('unselected_target_settlement_remains_unsupported', 'unsupported', policy=unsupported)
    invalid = deepcopy(c['policy'])
    invalid['fraction'] = '11/10'
    case('invalid_fraction_not_unresolved', 'invalid', policy=invalid)
    case('invalid_mode', 'invalid', mode='latest_everything')
    case('invalid_cutoff', 'invalid', cutoff='2025-03-13')
    case('archival_cutoff_invalid', 'invalid', mode='archival_exploration')

    accepted = witnesses['method_public_day_complete']
    check('derived_result_kind', accepted['result_kind'] == 'derived_synthetic_consequence')
    check('current_derivation_and_accounting_replayed',
          accepted['derivation_verified'] and accepted['accounting_execution_verified'])
    check('child_clock_not_inherited', accepted['child_clock_inherited'] is False
          and 'child_authored_at' not in accepted and 'child_published_at' not in accepted)
    check('both_exact_components', accepted['policy_information']['component_count'] == 2)
    check('result_identity_bound', accepted['child_result_sha256'] == digest(c['result']))
    year, fixed = c['result']['years'][1], c['fixed_result']['years'][1]
    delta = lambda name: Q(year['report']['lines'][name]['value']) - Q(fixed['report']['lines'][name]['value'])
    check('same_independent_cash_receivable_consequence', delta('cash') == -delta('receivables') == Q(144, 5))
    check('profit_unchanged', delta('profit') == 0)
    for name, value in witnesses.items():
        if any(value.get(k) is not False for k in ['real_world_admission', 'forecast_admission',
                                                  'historical_execution_established', 'real_behavior_evidence']):
            check('synthetic_flags:' + name, False)
    check('every_branch_keeps_synthetic_and_no_past_run_flags', all(
        all(v.get(k) is False for k in ['real_world_admission', 'forecast_admission',
                                       'historical_execution_established', 'real_behavior_evidence'])
        for v in witnesses.values()))
    check('temporal_admission_only_for_eligible_dependencies', all(
        v['temporal_admission'] == (v['status'] == 'eligible_synthetic') for v in witnesses.values()))
    return {'checks': checks, 'passed': all(x['passed'] for x in checks),
            'witnesses': witnesses}, fixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    target = HERE / 'checks.json'
    if args.record and target.exists():
        raise RuntimeError('Evidence exists; use read-only verification')
    if os.environ.get('CUDA_VISIBLE_DEVICES') != '-1':
        raise RuntimeError('Set CUDA_VISIBLE_DEVICES=-1 for the declared CPU-only run')
    baseline = protected_files()
    manifest_path = HERE / 'manifest.json'
    if not args.record and manifest_path.exists():
        for name, h in json.loads(manifest_path.read_text())['files'].items():
            if file_hash(ROOT / name) != h:
                raise AssertionError('Recorded file changed: ' + name)
    start = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    evidence, fixture = conformance()
    protected_files()
    failed = [x['name'] for x in evidence['checks'] if not x['passed']]
    if failed:
        failure = HERE / 'diagnostic-failure.json'
        if not failure.exists():
            failure.write_text(json.dumps({'evidence': evidence, 'baseline': baseline}, indent=2) + '\n')
    elif args.record:
        for name, value in [('checks.json', evidence), ('fixture.json', fixture),
                            ('schema.json', schema()), ('baseline.json', baseline)]:
            (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
        manifest = {
            'started_utc': start, 'wall_seconds': time.perf_counter() - clock,
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-policy-information-20261023/verify.py --record',
            'environment': 'system Python ' + platform.python_version() + '; jsonschema; trusted local replay',
            'cpu_gpu': 'CPU only; GPU intentionally hidden by CUDA_VISIBLE_DEVICES=-1',
            'data_version': baseline, 'random_seeds': 'N/A: deterministic',
            'plan': 'docs/plans/accounting-policy-information-20261023.md',
            'result': 'data/accounting-master/company-policy-information-20261023/result.md',
            'files': {str(p.relative_to(ROOT)): file_hash(p) for p in HERE.iterdir() if p.is_file()}}
        (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    elif target.exists():
        for name, actual in [('checks.json', evidence), ('fixture.json', fixture), ('schema.json', schema())]:
            if actual != json.loads((HERE / name).read_text()):
                raise AssertionError('Recorded replay mismatch: ' + name)
    print(json.dumps({'checks': len(evidence['checks']), 'passed': not failed,
                      'failed': failed, 'recorded': args.record, 'protected_files': len(baseline),
                      'wall_seconds': round(time.perf_counter() - clock, 3)}))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
