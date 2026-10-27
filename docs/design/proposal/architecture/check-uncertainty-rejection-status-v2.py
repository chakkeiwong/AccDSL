"""Bounded specification diagnostic; no product execution or arithmetic reassessment."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = Path('docs/design/proposal/architecture')
OLD = BASE / 'uncertainty-chaining-fixtures-v1.json'
NEW = BASE / 'uncertainty-chaining-fixtures-v2.json'
CONTRACT = BASE / 'uncertainty-rejection-status-contract-v1.md'
GOVERNING = BASE / 'uncertainty-contract-v1.md'
REVIEW = Path('data/accounting-master/runs/20261005T120206-bdb3a74d/P16/execution-0/review_result-0.response.json')
OUTPUT = BASE / 'uncertainty-rejection-status-check-v2.json'


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield key
            if key != 'perimeter':  # Frozen scope label, not a registry reference.
                yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def record_refs(value):
    return {s for s in strings(value) if re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*@[1-9][0-9]*', s)}


def file_refs(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            yield value
        for child in value.values():
            yield from file_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from file_refs(child)


def main():
    old = json.loads((ROOT / OLD).read_text())
    new = json.loads((ROOT / NEW).read_text())
    records = new['records']
    checks = []

    def check(name, ok, detail=None):
        row = {'id': name, 'passed': bool(ok)}
        if detail is not None:
            row['detail'] = detail
        checks.append(row)

    names = {'candidate_only', 'duplicate_D', 'stale_law', 'stale_attachment', 'correction_on_posterior'}
    corrections = new['rejection_status_corrections']
    check('exactly five named correction mappings', len(corrections) == 5 and {r['case_id'] for r in corrections} == names)
    original_refs = set(old['records'])
    expected_new = {'CH.rejection.' + name + '@2' for name in names}
    check('only five appended registry records', set(records) == original_refs | expected_new)
    unchanged = [key for key, rec in old['records'].items() if canonical(records.get(key)) == canonical(rec)]
    check('all original records canonically unchanged', len(unchanged) == len(old['records']), {'preserved': len(unchanged), 'total': len(old['records'])})
    allowed_top = {'schema_version', 'scope', 'source_evidence', 'registry_convention', 'records', 'cases'}
    check('all other original top-level values unchanged', all(new.get(k) == v for k, v in old.items() if k not in allowed_top))
    check('only declared top-level additions', set(new) - set(old) == {'rejection_status_corrections', 'active_rejection_receipts', 'historical_rejection_receipts'})
    old_cases = {r['id']: r for r in old['cases']}
    cases = {r['id']: r for r in new['cases']}
    check('same ten unique cases', len(cases) == len(new['cases']) == len(old_cases) == 10 and set(cases) == set(old_cases))
    check('all successful cases unchanged', all(cases[k] == v for k, v in old_cases.items() if v['kind'] != 'reject'))
    historical = new['historical_rejection_receipts']
    check('exact historical exclusion set', len(historical) == 5 and {r['receipt_ref'] for r in historical} == {'CH.rejection.' + n + '@1' for n in names})
    check('no historical receipt selected actively', not ({r['receipt_ref'] for r in historical} & {r['expected_ref'] for r in new['cases']}))
    expected_status = dict(structural_validity='invalid', mathematical_status='unresolved', computation_status='not_computed', empirical_justification='not_established', capability_status='specified_only_no_runtime', accounting_validity='not_assessed', human_acceptance='pending')
    vocab = {'structural_validity': {'valid', 'invalid'}, 'mathematical_status': {'satisfied', 'failed', 'undefined', 'unresolved'}, 'computation_status': {'specified_exact', 'specified_partial', 'symbolic', 'not_computed'}, 'empirical_justification': {'stipulated', 'not_established', 'supported_for_named_scope'}, 'capability_status': {'specified_only_no_runtime', 'unsupported'}}
    permitted_changes = {'version', 'predecessor', 'mathematical_status', 'dependencies', 'provenance', 'structural_validity', 'computation_status', 'empirical_justification', 'accounting_validity'}
    for mapping in corrections:
        name, previous, current = mapping['case_id'], mapping['predecessor_ref'], mapping['corrected_ref']
        before, after = old['records'][previous], records[current]
        check(name + ': identity, version, predecessor', current == before['id'] + '@2' and previous == before['id'] + '@1' and after['id'] == before['id'] and after['version'] == 2 and after['predecessor'] == previous)
        check(name + ': status envelope and vocabulary', all(after.get(k) == v for k, v in expected_status.items()) and all(after[k] in v for k, v in vocab.items()))
        changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
        check(name + ': only allowed field changes', changed <= permitted_changes, sorted(changed))
        check(name + ': preserved request and decisive rejection', after['request_ref'] == before['request_ref'] and after['disposition'] == before['disposition'] == 'REQUEST_INVALID' and after['reason_codes'] == before['reason_codes'])
        check(name + ': preserved states and no domain effects', after['state_before'] == after['state_after'] == before['state_before'] == before['state_after'] and after['domain_writes'] == before['domain_writes'] == [] and after['audit_writes'] == before['audit_writes'] == ['submitted_bytes', 'rejection_receipt'] and after['proposed_view_ref'] is None and after['model_ref'] is None and after['preserved_parent_hashes'] == before['preserved_parent_hashes'])
        check(name + ': dependencies add only predecessor', after['dependencies'] == sorted(set(before['dependencies']) | {previous}))
        direct = record_refs({k: v for k, v in after.items() if k != 'dependencies'})
        closure, todo = set(), list(direct)
        while todo:
            key = todo.pop()
            if key in closure:
                continue
            closure.add(key)
            if key in records:
                todo.extend(record_refs(records[key]) - closure)
        check(name + ': dependency and reference closure', closure <= set(records) and closure <= set(after['dependencies']), {'missing_records': sorted(closure - set(records)), 'missing_dependencies': sorted(closure - set(after['dependencies']))})
        expected_case = dict(old_cases[name], expected_ref=current)
        check(name + ': active case and map agree', cases[name] == expected_case and new['active_rejection_receipts'].get(name) == current and set(new['active_rejection_receipts']) == names)
        check(name + ': predecessor historical only', any(r['receipt_ref'] == previous and r['superseded_by'] == current and r['eligible_as_active_expected_output'] is False for r in historical))
        check(name + ': specification correction, no runtime replay', mapping['correction_kind'] == 'specification_only' and mapping['runtime_replay'] is False and after['provenance']['kind'] == 'specification_correction_not_runtime_replay' and after['provenance']['source_fixture']['sha256'] == digest(OLD))
    missing_refs = record_refs(records) - set(records)
    check('entire registry reference resolution', not missing_refs, sorted(missing_refs))
    bad_pins = [r['path'] for r in file_refs(new) if not (ROOT / r['path']).is_file() or digest(r['path']) != r['sha256']]
    check('all fixture file references match current bytes', not bad_pins, bad_pins)
    inputs = {str(p): digest(p) for p in [OLD, NEW, CONTRACT, GOVERNING, REVIEW, Path(__file__).relative_to(ROOT)]}
    report = {'schema_version': 'accdsl.proposal.uncertainty.rejection-status.check.v2', 'scope': 'Five specified rejection-status corrections; preservation and reference checks only', 'command': ['python3', str(Path(__file__).relative_to(ROOT))], 'environment': {'python_version': sys.version.split()[0], 'packages': 'standard library only', 'gpu': 'N/A; no framework import or device detection', 'git_commit': 'N/A; repository marker unusable, no Git changes'}, 'input_hashes': inputs, 'passed': all(r['passed'] for r in checks), 'checks': checks, 'original_records_preserved': len(unchanged), 'correction_count': len(corrections), 'arithmetic_recomputed': False, 'product_implemented': False, 'human_acceptance': 'pending', 'independent_acceptance_recorded': False}
    with (ROOT / OUTPUT).open('x') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'output': str(OUTPUT), 'passed': report['passed'], 'checks': len(checks), 'failures': [r for r in checks if not r['passed']]}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
