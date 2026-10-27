"""Finite C03 proposal-document diagnostic; no runtime or accounting API.

Expected findings reside in the fixtures. This script independently derives them
from candidate values and verifies exact changes, dependencies and publication.
"""
import copy
import hashlib
import datetime
import re
import json
import platform
import sys
import time
from pathlib import Path

START = time.monotonic()
B = Path('docs/design/proposal/architecture')
P = 'accounting-integration-c03-conditions'
D = 'accdsl.accounting.integration.v1'
checks, results = [], []
used = {str(Path(__file__))}


def load(path):
    used.add(str(path))
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False)


def digest(domain, kind, value):
    return hashlib.sha256((domain + '/' + kind + '\0' + canonical(value)).encode('ascii')).hexdigest()


def check(label, value):
    checks.append({'id': label, 'passed': bool(value)})


def strict(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key: ' + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def typ(value):
    if value is None:
        return 'null'
    return {bool: 'boolean', str: 'string', int: 'number', float: 'number',
            list: 'array', dict: 'object'}[type(value)]


m = load(B / (P + '-matrix-v1.json'))
f = load(B / (P + '-fixtures-v1.json'))
snapshot = load(B / (P + '-inputs-v1.json'))
rows = {r['path']: r for r in m['rows']}
check('two exact amended rows', {r['id'] for r in m['rows']} == {'F185', 'F186'})
records = {}
for ref in f['imports']:
    check('import pin ' + ref['path'], sha(ref['path']) == ref['sha256'])
    imported = load(ref['path'])
    for h, row in imported['records'].items():
        domains = [d for d in ['accdsl.accounting.records.v1', 'accdsl.accounting.record.v1', D]
                   if digest(d, row['kind'], row['content']) == h]
        check('import identity ' + h, len(domains) == 1)
        if domains:
            records[h] = {**row, 'domain': domains[0]}
records.update(f['records'])
for h, row in f['records'].items():
    check('candidate identity ' + h, digest(row['domain'], row['kind'], row['content']) == h)
source = load(f['source_comparator']['path'])
E = {c['id']: c for c in source['cases']}
integration = load(B / 'accounting-integration-fixtures-v2.json')
I = {c['id']: c for c in integration['cases']}
for row in m['rows']:
    cid = 'C03'
    parts = row['path'].split('/')[2:]
    observed = set()
    for c in source['cases']:
        value = c['complete_inputs'][cid]
        for part in parts:
            value = value[part]
        observed.add(typ(value))
    check(row['id'] + ' observed versus allowed', row['observed_types'] == sorted(observed)
          and row['allowed_types'] == (['boolean'] if parts[-1] == 'party_to_contract' else ['null', 'string'])
          and row['required'] is True)


def derive(cid, packet):
    """Independent calendar/type predicates on submitted C03 values."""
    out, triggers = [], []
    def finding(parts, code, parent):
        key = parts[-1]
        present = type(parent) is dict and key in parent
        obs = {'present': present}
        if present:
            obs.update(type=typ(parent[key]), value=parent[key])
        path = 'source/C03/' + '/'.join(parts)
        rule = rows[path]['expected_rule'] if path in rows else 'required object; malformed parent suppresses descendant predicates'
        out.append({'stage': 'shape', 'path': path, 'code': code,
                    'expected': rule, 'observed': obs})
    if type(packet) is not dict:
        raise ValueError('Outer packet outside this finite slice')
    if 'value' not in packet:
        finding(['value'], 'INVALID_CONDITION_PACKET', packet)
    elif type(packet['value']) is not dict:
        finding(['value'], 'INVALID_FIELD_TYPE', packet)
    else:
        v = packet['value']
        if 'party_to_contract' not in v:
            finding(['value', 'party_to_contract'], 'INVALID_CONDITION_PACKET', v)
        elif type(v['party_to_contract']) is not bool:
            finding(['value', 'party_to_contract'], 'INVALID_FIELD_TYPE', v)
        if 'contractual_date' not in v:
            finding(['value', 'contractual_date'], 'INVALID_CONDITION_PACKET', v)
        else:
            date = v['contractual_date']
            if date is None:
                if type(v.get('party_to_contract')) is bool and v['party_to_contract'] is True:
                    triggers.append('source/C03/value/contractual_date')
                    finding(['value', 'contractual_date'], 'INVALID_UNKNOWN_REPRESENTATION', v)
            elif type(date) is not str:
                finding(['value', 'contractual_date'], 'INVALID_FIELD_TYPE', v)
            else:
                valid = re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date) is not None
                if valid:
                    try:
                        datetime.date(*map(int, date.split('-')))
                    except ValueError:
                        valid = False
                if not valid:
                    finding(['value', 'contractual_date'], 'INVALID_CONDITION_PACKET', v)
    return sorted(out, key=lambda d: (d['path'], d['code'])), triggers


def apply_changes(value, changes):
    result = copy.deepcopy(value)
    for change in changes:
        cursor = result
        for part in change['path'][:-1]:
            cursor = cursor[part]
        if change['operation'] == 'remove':
            del cursor[change['path'][-1]]
        else:
            cursor[change['path'][-1]] = copy.deepcopy(change['value'])
    return result


for case in f['local_controls']:
    label, cid, candidate = case['id'], case['condition_id'], case['candidate']
    comparator = E[case['comparator']['case_id']]['complete_inputs'][cid]
    check(label + ' exact declared mutation only', apply_changes(comparator, case['mutations']) == candidate)
    actual, triggers = derive(cid, candidate)
    check(label + ' candidate-derived diagnostic', actual == case['expected_diagnostics'])
    check(label + ' representation scope', case['representation_valid'] == (not actual)
          and case['accounting_outcome'] == 'not_assessed_representation_only')
    check(label + ' unknown_reason untouched', candidate['unknown_reason'] == comparator['unknown_reason'])
    results.append({'id': label, 'diagnostics': actual, 'conditional_triggers': triggers})
variants = {c['variant']: c for c in f['local_controls']}
for name in ['true_date','false_null','false_date','true_null','bad_party_null_date',
             'combined_independent_defects','missing_both','false_invalid_date',
             'valid_date_2000-02-29','valid_date_2024-02-29','valid_date_0001-01-01','valid_date_9999-12-31']:
    check('required control ' + name, name in variants)
for value in [None,0,1,'true','false',[],{}]:
    check('non-Boolean control ' + canonical(value), 'party_type_' + canonical(value) in variants)
for value in [False,True,0,1,[],{}]:
    check('wrong date type control ' + canonical(value), 'date_type_' + canonical(value) in variants)


def verify_refs(value, label):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            p = Path(value['path'])
            used.add(str(p))
            check(label + ' file pin ' + str(p), p.is_file() and sha(p) == value['sha256'])
        if 'file' in value and 'case_id' in value:
            data = load(value['file']['path'])
            check(label + ' unique CaseRef', sum(c['id'] == value['case_id'] for c in data['cases']) == 1)
        for child in value.values():
            verify_refs(child, label)
    elif isinstance(value, list):
        for child in value:
            verify_refs(child, label)


for x in f['exchanges']:
    label = x['id']
    comparator = I[x['control']['case_id']]
    q = strict(x['raw_request'])
    check(label + ' canonical raw request and identity', canonical(q) == x['raw_request']
          and digest(D, 'request', q) == x['candidate_request_digest'])
    sub = records[x['submission']]['content']
    check(label + ' exact submitted bytes', sub['raw_text'] == x['raw_request'] and sub['wire_format'] == 'ASCII_JSON')
    dependencies = {r['claimed_digest']: r for r in x['dependencies']}
    check(label + ' unique dependency assertions', len(dependencies) == len(x['dependencies']))
    reached = set()
    def walk(value):
        if isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value):
            check(label + ' dependency supplied ' + value, value in dependencies)
            if value not in dependencies or value in reached:
                return
            reached.add(value)
            row = dependencies[value]
            content = strict(row['content_text'])
            check(label + ' dependency digest ' + value, digest(row['domain'], row['kind'], content) == value)
            check(label + ' exact resolved dependency ' + value, records[value] == {
                'domain': row['domain'], 'kind': row['kind'], 'content': content})
            walk(content)
        elif isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                verify_refs(value, label)
                return
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(q)
    check(label + ' complete exact dependency closure', reached == set(dependencies))
    verify_refs(x['source_case'], label)
    data = load(x['source_case']['file']['path'])
    candidate = next(c for c in data['cases'] if c['id'] == x['source_case']['case_id'])['complete_inputs']
    expected_source = copy.deepcopy(E[comparator['source_case']['case_id']]['complete_inputs'])
    for change in x['mutations']:
        cid = change['condition_id']
        expected_source[cid] = apply_changes(expected_source[cid], [change])
    check(label + ' source mutation isolation', expected_source == candidate)
    eligibility = records[q['eligibility']]['content']
    check(label + ' source case binding', eligibility['source_case'] == x['source_case'])
    check(label + ' C01-C10 exact order', [r['condition_id'] for r in eligibility['conditions']] == ['C%02d'%i for i in range(1, 11)])
    for condition in eligibility['conditions']:
        check(label + ' ConditionRef and opaque version ' + condition['condition_id'],
              condition['case'] == x['source_case'] and
              condition['value_version'] == candidate[condition['condition_id']]['version'])
    check(label + ' bindings preserved', all(q[k] == val for k, val in eligibility['bindings'].items()))
    findings, triggers = [], {}
    for cid in ['C03']:
        found, triggers[cid] = derive(cid, candidate[cid])
        findings.extend(found)
    findings.sort(key=lambda d: (d['path'], d['code']))
    check(label + ' derived stage and diagnostics', findings == x['expected_diagnostics'])
    check(label + ' derived null triggers', triggers == x['stage_derivation']['conditional_triggers'])
    check(label + ' reached shape', x['stage_derivation']['shape'] == ('rejected' if findings else 'passed for this scoped amendment'))
    response = records[x['response']]['content']
    original_q = records[comparator['request']]['content']
    expected_q = copy.deepcopy(original_q)
    expected_q['eligibility'] = q['eligibility']
    check(label + ' exact request except refreshed eligibility', q == expected_q)
    expected_el = copy.deepcopy(records[original_q['eligibility']]['content'])
    expected_el['source_case'] = x['source_case']
    for condition in expected_el['conditions']:
        condition['case'] = x['source_case']
    check(label + ' exact refreshed eligibility', eligibility == expected_el and
          records[q['eligibility']]['kind'] == 'eligibility_input')
    if not x['mutations']:
        check(label + ' exact original exchange identities',
              x['candidate_request_digest'] == comparator['request'] and
              all(x[k] == comparator[k] for k in ['submission','assessment','response']))
    v = candidate['C03'].get('value', {})
    check(label + ' conditional guard derived', x['stage_derivation']['conditional_guard_evaluable'] ==
          (type(v.get('party_to_contract')) is bool))
    check(label + ' stage stop enforced',
          x['stage_derivation']['source_versions'] == ('not reached' if findings else 'passed: opaque versions match all condition packets') and
          x['stage_derivation']['bindings'] == ('not reached' if findings else 'passed: complete eligibility bindings match request'))
    verify_refs(x['source_files'], label)
    check(label + ' response submission', response['submission'] == x['submission'])
    check(label + ' unchanged committed domains', x['before'] == x['after'] == comparator['before'])
    check(label + ' no commit or posting', response['commit_status'] == 'not_committed' and response['additional_commit'] is False
          and response['receipt'] is None and response['observed_state'] is None)
    if findings:
        check(label + ' rejection before lookup/assessment', not x['receipt_lookup_performed']
              and not x['freshness_checked'] and not x['accounting_assessed'] and x['assessment'] is None)
        check(label + ' null publication', all(response[key] is None for key in ['request','assessment','diagnostic_journal','diagnostic_delta','receipt','observed_state']))
        check(label + ' rejected codes in diagnostic order', response['status'] == 'rejected' and
              response['reason_codes'] == list(dict.fromkeys(d['code'] for d in findings)))
        wanted = dict(structural_validity='invalid', mathematical_status='unresolved', computation_status='not_computed',
                      empirical_justification='not_established', capability_status='specified_only_no_runtime',
                      accounting_validity='not_assessed', human_acceptance='pending')
        check(label + ' seven rejection statuses', response['statuses'] == wanted)
    else:
        a = records[x['assessment']]['content']
        old = records[comparator['assessment']]['content']
        # Compare all source facts except the one explicitly permitted contextual date.
        beforefacts = copy.deepcopy(E[comparator['source_case']['case_id']]['complete_inputs'])
        afterfacts = copy.deepcopy(candidate)
        beforefacts['C03']['value'].pop('contractual_date')
        afterfacts['C03']['value'].pop('contractual_date')
        check(label + ' exact remaining semantic facts', beforefacts == afterfacts)
        party = candidate['C03']['value']['party_to_contract']
        finding = next(r for r in a['findings'] if r['condition'] == 'C03')
        check(label + ' Boolean-derived C03 consequence', finding['status'] ==
              ('satisfied_conditionally' if party else 'ineligible'))
        if party is False:
            check(label + ' false date cannot establish participation',
                  finding['reason'] == 'not party to contract at recognition' and
                  a['reason_codes'] == ['C03:ineligible'] and a['status'] == 'ineligible' and
                  response['reason_codes'] == ['C03:ineligible'] and
                  response['diagnostic_journal'] is None and response['diagnostic_delta'] is None)
        expected_assessment = copy.deepcopy(old)
        expected_assessment.update(request=x['candidate_request_digest'], eligibility=q['eligibility'], source_assessment=x['source_case'])
        check(label + ' full refreshed assessment', a == expected_assessment)
        expected_response = copy.deepcopy(records[comparator['response']]['content'])
        expected_response.update(submission=x['submission'],request=x['candidate_request_digest'],assessment=x['assessment'])
        check(label + ' full response and evidence statuses', response == expected_response)
        check(label + ' retained assessment consequences', all(a[k] == old[k] for k in ['status','reason_codes','preconditions','findings','method_applicability','posting_permitted','evidence_level']))
        check(label + ' refreshed assessment bindings', a['request'] == x['candidate_request_digest'] and a['eligibility'] == q['eligibility'] and a['source_assessment'] == x['source_case'])
        check(label + ' positive response', response['status'] == 'assessed' and response['request'] == x['candidate_request_digest']
              and response['assessment'] == x['assessment'] and a['status'] == x['expected_assessment_status'])
        check(label + ' positive assessment reached', x['receipt_lookup_performed'] and not x['before']['identity_index'] and x['accounting_assessed'] and x['freshness_checked'] and a['posting_permitted'] is False)
        verify_refs(a, label)
    results.append({'id': label, 'diagnostics': findings, 'conditional_triggers': triggers,
                    'dependency_count': len(reached), 'assessment_status': x['expected_assessment_status']})
verify_refs(f, 'fixture references')
for name in [P + '-v1.md', 'accounting-integration-contract-v1.md',
             'accounting-integration-rejections-contract-v1.md',
             'accounting-integration-source-reason-types-v1.md']:
    used.add(str(B / name))
for path, h in snapshot['protected_sha256'].items():
    check('predecessor unchanged ' + path, sha(path) == h)

out = Path(sys.argv[1])
if out.exists():
    raise SystemExit('Refusing to overwrite a prior verification artifact')
failures = [r for r in checks if not r['passed']]
report = {'schema_version':'accdsl.proposal.c03.verification.v1','passed':not failures,
          'checks':checks,'failures':failures,'derived_results':results,
          'input_hashes':{p:sha(p) for p in sorted(used)},
          'manifest':{'command':'PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__))+' '+str(out),
                      'python':platform.python_version(),'environment':'existing standard-library Python; no ML framework import',
                      'cpu_gpu':'CPU document checks only; no GPU use','git_commit':'N/A: existing marker is not a usable repository',
                      'random_seeds':'N/A deterministic document check','wall_seconds':round(time.monotonic()-START,4),
                      'plan_hash':snapshot['approved_plan_hash'],'result':str(out)},
          'limits':'Finite specified exchanges only; no runtime, accounting validity, forecast validity or P16 acceptance.'}
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':not failures,'checks':len(checks),'failures':failures,'output':str(out)}))
raise SystemExit(bool(failures))
