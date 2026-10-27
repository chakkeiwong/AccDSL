"""Finite proposal-document diagnostic; no endpoint or accounting validator."""
import copy
import hashlib
import json
import platform
import sys
from pathlib import Path

B = Path('docs/design/proposal/architecture')
P = 'accounting-integration-source-reason-types'
SELECTED = {'F154': 'C01', 'F169': 'C02', 'F182': 'C03',
            'F194': 'C04', 'F229': 'C06', 'F261': 'C08'}


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False)


def json_type(value):
    if value is None:
        return 'null'
    return {str: 'string', bool: 'boolean', int: 'number', float: 'number',
            list: 'array', dict: 'object'}[type(value)]


checks = []


def check(name, passed):
    checks.append({'id': name, 'passed': bool(passed)})


m = load(B / (P + '-matrix-v1.json'))
f = load(B / (P + '-fixtures-v1.json'))
snapshot = load(B / (P + '-inputs-v1.json'))
old_matrix = load(B / 'accounting-integration-field-validation-matrix-v1.json')
integration = load(B / 'accounting-integration-fixtures-v2.json')
records = {**load(B / 'accounting-records-fixtures-v1.json')['records'],
           **integration['records']}
observed = {cid: set() for cid in SELECTED.values()}
observed_locators = {cid: set() for cid in SELECTED.values()}
paths = set()


def inventory(value, path):
    paths.add(path)
    if isinstance(value, dict):
        for key, child in value.items():
            inventory(child, path + '/' + key)
    elif isinstance(value, list):
        for child in value:
            inventory(child, path + '/*')


# Independently resolve the retained cases; do not trust old row type labels.
for case in integration['cases']:
    for key in ['request', 'assessment', 'response']:
        inventory(records[case[key]]['content'], key)
    request = records[case['request']]['content']
    eligibility = records[request['eligibility']]['content']
    inventory(eligibility, 'eligibility_input')
    for evidence in request['evidence']:
        inventory(records[evidence]['content']['observable_valuation'],
                  'observable_valuation')
    for condition in eligibility['conditions']:
        source = condition['case']['file']
        check('source pin ' + source['path'], sha(source['path']) == source['sha256'])
        matches = [x for x in load(source['path'])['cases']
                   if x['id'] == condition['case']['case_id']]
        check('unique source case ' + case['id'], len(matches) == 1)
        cid = condition['condition_id']
        packet = matches[0]['complete_inputs'][cid]
        inventory(packet, 'source/' + cid)
        if cid in observed:
            observed[cid].add(json_type(packet['unknown_reason']))
            observed_locators[cid].add(source['path'] + '#cases[id=' +
                                      matches[0]['id'] + '].complete_inputs.' + cid)

check('preserved 299-path inventory', len(paths) == 299 and
      paths == {r['path'] for r in old_matrix['rows']})
check('exactly six amended rows', len(m['rows']) == 6 and
      {r['id']: r['condition_id'] for r in m['rows']} == SELECTED and
      m['amended_row_ids'] == list(SELECTED))
whitespace = {cp for low, high in m['whitespace_codepoint_ranges']
              for cp in range(low, high + 1)}
check('explicit 25 whitespace codepoints', len(whitespace) == 25)


def derive(cid, packet):
    """Evaluate only the three scoped predicates, from actual candidate data."""
    present = 'unknown_reason' in packet
    observation = {'present': present, 'type': 'missing'}
    if not present:
        code = 'INVALID_CONDITION_PACKET'
    else:
        value = packet['unknown_reason']
        observation.update(type=json_type(value), value=value)
        if value is not None and type(value) is not str:
            code = 'INVALID_FIELD_TYPE'
        elif type(value) is str and not any(ord(ch) not in whitespace for ch in value):
            code = 'INVALID_UNKNOWN_REPRESENTATION'
        else:
            code = None
    findings = [] if code is None else [{
        'stage': 'shape', 'path': 'source/' + cid + '/unknown_reason',
        'code': code, 'expected': m['expected_field_rule'], 'observed': observation}]
    return observation, findings


results = []
variants = {'retained_null', 'contextual_string', 'absent', 'empty_string',
            'whitespace_string', 'boolean_true', 'boolean_false',
            'integer_zero', 'fractional_number', 'array', 'object'}
for row in m['rows']:
    fid, cid = row['id'], row['condition_id']
    check(fid + ' recovered observations', row['observed_types'] == sorted(observed[cid]))
    check(fid + ' required null|string', row['required'] is True and
          row['allowed_types'] == ['null', 'string'])
    check(fid + ' original constraint', 'string|null' in next(
        r for r in old_matrix['rows'] if r['id'] == fid)['constraint'])
    check(fid + ' dispositions', set(row['predicate_dispositions']) == {
        'required_member', 'allowed_json_type', 'nonblank_string',
        'fact_reason_conditional_consistency'})
    check(fid + ' conditional deferral', row['predicate_dispositions'][
        'fact_reason_conditional_consistency']['status'] == 'deferred')
    subset = [x for x in f['cases'] if x['field_id'] == fid]
    check(fid + ' eleven matched candidates', len(subset) == 11 and
          {x['variant'] for x in subset} == variants)
    source = load(row['source_control']['path'])
    control = next(x for x in source['cases'] if x['id'] == 'E01')['complete_inputs'][cid]
    check(fid + ' retained null', control['unknown_reason'] is None)
    for case in subset:
        label = case['id']
        candidate = case['candidate_packet']
        check(label + ' exact control', canonical(control) == canonical(case['control_packet']))
        restored = copy.deepcopy(candidate)
        restored['unknown_reason'] = control['unknown_reason']
        check(label + ' isolated mutation', canonical(restored) == canonical(control))
        observation, findings = derive(cid, candidate)
        check(label + ' declared mutation value', canonical(observation) ==
              canonical(case['mutation']['after']))
        operation = ('remove' if not observation['present'] else
                     'retain' if canonical(candidate) == canonical(control) else 'replace')
        check(label + ' declared operation', case['mutation']['operation'] == operation and
              case['mutation']['path'] == 'source/' + cid + '/unknown_reason' and
              case['mutation']['before'] == {'present': True, 'type': 'null', 'value': None})
        expected = case['expected']
        check(label + ' input-derived findings', canonical(findings) == canonical(expected['findings']))
        check(label + ' local status', expected['local_status'] ==
              ('scoped_predicate_failed' if findings else 'scoped_predicates_satisfied'))
        check(label + ' no admission claim', expected['packet_admission'] ==
              expected['conditional_admissibility'] == 'not_assessed' and
              expected['local_stage'] == 'shape')
        check(label + ' positive/negative disposition', bool(findings) ==
              (case['variant'] not in {'retained_null', 'contextual_string'}))
        results.append({'id': label, 'observation': observation, 'derived_findings': findings})
check('exactly 66 distinct cases', len(f['cases']) == len({c['id'] for c in f['cases']}) == 66)
aggregate_results = []
for aggregate in f['aggregate_cases']:
    findings = []
    for cid, packet in aggregate['candidate_packets'].items():
        findings.extend(derive(cid, packet)[1])
    findings.sort(key=lambda d: (d['path'], d['code']))
    check('all independently decidable findings retained and sorted', len(findings) == 5 and
          canonical(findings) == canonical(aggregate['expected_findings']))
    for case_id in aggregate['component_case_ids']:
        case = next(c for c in f['cases'] if c['id'] == case_id)
        check('aggregate exact component ' + case_id, canonical(case['candidate_packet']) ==
              canonical(aggregate['candidate_packets'][case['condition_id']]))
    aggregate_results.append({'id': aggregate['id'], 'derived_findings': findings})
for path, digest in snapshot['protected_sha256'].items():
    check('preserved ' + path, sha(path) == digest)


def pins(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and 'sha256' in value:
            check('current reference ' + value['path'], sha(value['path']) == value['sha256'])
        for child in value.values():
            pins(child)
    elif isinstance(value, list):
        for child in value:
            pins(child)


for document in [m, f, load('data/accounting-master/deliverables/P16/architecture.json')]:
    pins(document)
report = {
    'schema_version': 'accdsl.proposal.source-reason-types.verification.v1',
    'passed': all(c['passed'] for c in checks), 'checks': len(checks),
    'failures': [c for c in checks if not c['passed']],
    'counts': {'amended_rows': 6, 'inventory_paths': len(paths),
               'local_cases': len(results), 'aggregate_cases': len(aggregate_results),
               'protected_predecessors': len(snapshot['protected_sha256'])},
    'observed_types_recovered': {k: sorted(v) for k, v in observed.items()},
    'observed_source_locators': {k: sorted(v) for k, v in observed_locators.items()},
    'derived_cases': results, 'derived_aggregate_cases': aggregate_results,
    'input_sha256': {str(p): sha(p) for p in [B / (P + suffix) for suffix in
        ['-v1.md', '-matrix-v1.json', '-fixtures-v1.json', '-inputs-v1.json', '-diagnostic-v1.py']]},
    'command': 'PYTHONDONTWRITEBYTECODE=1 python3 ' + ' '.join(sys.argv),
    'environment': platform.python_version() + ' standard library; no framework imported or GPU used',
    'scope': 'Finite local reason predicates, observed inventory, mutation and preservation checks only. '
             'Conditional admissibility, full exchange execution and accounting validity are not assessed.'}
with open(sys.argv[1], 'x') as output:
    json.dump(report, output, indent=2, ensure_ascii=False)
    output.write('\n')
print(json.dumps({k: report[k] for k in ['passed', 'checks', 'failures', 'counts']}))
sys.exit(0 if report['passed'] else 1)
