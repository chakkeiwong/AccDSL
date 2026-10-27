#!/usr/bin/env python3
"""Rebuild the canonical P08 JSON from retained specifications and executions.

Validate before a single atomic replace. The prior bytes are content-addressed
under the phase output directory. Narrative and historic check reports do not
grant acceptance; run the standalone checker after publication.
"""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys

from accounting_master_support import atomic_bytes, atomic_json, digest, local_path
from check_accounting_p08 import check_deliverable, independent_case
from corporate_financing_v1 import AuthorityBook, Contract, run_case, compare_same_facts
from corporate_authority_eu_v1 import EUAuthorityPreparation, REGISTER as EU_REGISTER
from corporate_authority_eu_recovery_v1 import validate_recovery, REGISTER as RECOVERY_REGISTER
from corporate_authority_eu_current import validate_disposition, REGISTER as DISPOSITION_REGISTER
from corporate_authority_eu_applicability_v1 import validate_applicability, REGISTER as APPLICABILITY_REGISTER

ROOT = Path(__file__).resolve().parents[1]
SPEC = 'docs/design/fixtures/p08-result-spec-v1.json'
DESTINATION = ROOT / 'data/accounting-master/deliverables/P08/authority-and-methods.json'


def build():
    spec = json.loads((ROOT / SPEC).read_text())
    payload = deepcopy(spec)
    inputs = set(payload.pop('source_inputs')) | {SPEC, 'scripts/build_accounting_p08.py'}
    authority = AuthorityBook()
    cases = []
    for facts in payload.pop('case_inputs'):
        contract = Contract(**facts['facts'])
        result = run_case(contract, facts['settlement'], facts['opening_cash'], authority)
        state = result['state'].copy()
        journal = state.pop('journal')
        oracle = independent_case(contract, facts['settlement'], facts['opening_cash'], authority)
        oracle['case_id'] = facts['case_id']
        cases.append({**facts, 'facts': result['contract'], 'opening_cash': result['opening_cash'],
                      'initial_liability': result['initial_liability'], 'journal': journal,
                      'final_state': state, 'notes': result['notes'], 'independent_oracle': oracle})
    for key in ('authorities', 'claims', 'research', 'method_queue'):
        payload[key] = authority.records[key]
    payload['authority_register_sha256'] = digest(ROOT / payload['authority_register_path'])
    payload['source_access'] = json.loads((ROOT / 'docs/design/research/p08-v1/access-records.json').read_text())
    payload['source_access'].append(json.loads((ROOT / 'docs/design/research/p08-v1/eu-access.json').read_text()))
    preparation = ROOT / 'docs/design/research/p08-v2/source-inspection.json'
    payload['authority_preparation'] = json.loads(preparation.read_text())
    payload['authority_preparation_sha256'] = digest(preparation)
    payload['source_access_recovery'] = json.loads((ROOT / payload['authority_preparation']['source_access']['path']).read_text())
    payload['eu_authority_preparation'] = EUAuthorityPreparation().records
    payload['eu_authority_preparation_sha256'] = digest(ROOT / EU_REGISTER)
    recovery = validate_recovery(ROOT)
    payload['eu_source_recovery'] = recovery
    payload['eu_source_recovery_sha256'] = digest(ROOT / RECOVERY_REGISTER)
    inputs.update(pin['path'] for pin in recovery['source_pins'])
    inputs.update({RECOVERY_REGISTER, 'scripts/corporate_authority_eu_recovery_v1.py'})
    disposition = validate_disposition(ROOT)
    payload['eu_source_disposition'] = disposition
    payload['eu_source_disposition_sha256'] = digest(ROOT / DISPOSITION_REGISTER)
    inputs.update(pin['path'] for pin in disposition['source_pins'])
    inputs.update({DISPOSITION_REGISTER, 'scripts/corporate_authority_eu_current.py'})
    applicability = validate_applicability(ROOT)
    payload['eu_applicability_disposition'] = applicability
    payload['eu_applicability_disposition_sha256'] = digest(ROOT / APPLICABILITY_REGISTER)
    inputs.update({APPLICABILITY_REGISTER, 'scripts/corporate_authority_eu_applicability_v1.py'})
    payload['cases'] = cases
    payload['comparisons'] = compare_same_facts(authority=authority)
    complete = payload['comparisons']['criterion_status'] == 'complete_bounded'
    payload['acceptance'] = {'engineering': 'validated by builder; standalone checks required',
        'phase_criteria_complete': complete,
        'criteria': {f'criterion_{i}': 'incomplete' if i == 3 and not complete else 'complete_bounded' for i in range(1, 5)},
        'accounting_validity': 'not established', 'forecast_validity': 'not established',
        'human_acceptance': 'pending', 'whole_gap_closure': False}
    payload['manifest'] = {'builder': 'python3 -B scripts/build_accounting_p08.py',
        'command': 'python3 -B scripts/check_accounting_p08.py --check',
        'environment': {'python': sys.version, 'python_executable': sys.executable,
                        'hardware': 'CPU only; no accelerator framework imported',
                        'seeds': 'N/A: deterministic exact arithmetic'},
        'source_hashes': {n: digest(local_path(ROOT, n)) for n in sorted(inputs)}}
    findings = check_deliverable(payload, authority)
    if findings:
        raise ValueError('Candidate validation failed: ' + '; '.join(findings))
    return payload


def publish(payload, destination=DESTINATION, history_dir=None):
    # Validation is repeated at publication so callers cannot bypass it.
    findings = check_deliverable(payload, AuthorityBook())
    if findings:
        raise ValueError('Publication refused: ' + '; '.join(findings))
    if destination.exists():
        old = destination.read_bytes()
        archive = Path(history_dir) if history_dir is not None else destination.parent / 'history'
        atomic_bytes(archive / (digest(destination) + '.json'), old)
    atomic_json(destination, payload)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--history-dir', type=Path, help='Archive prior bytes outside protected supervisor directories')
    args = parser.parse_args()
    candidate = build()
    publish(candidate, history_dir=args.history_dir)
    print(json.dumps({'result': str(DESTINATION.relative_to(ROOT)), 'sha256': digest(DESTINATION),
                      'phase_criteria_complete': candidate['acceptance']['phase_criteria_complete']}))
