"""Finite proposal calculation for the version correction; no runtime validator."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import platform
import sys
import time

started = time.monotonic()
root = Path(__file__).resolve().parents[4]
base = root / 'docs/design/proposal/architecture'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda n: json.loads((base / n).read_text())
old = read('accounting-integration-fixtures-v1.json')
new = read('accounting-integration-fixtures-v2.json')
legacy = read('accounting-records-fixtures-v1.json')
maps = read('accounting-integration-typing-map-v1.json')
examples = read('accounting-integration-typing-cases-v1.json')
inputs = read('accounting-integration-typing-inputs-v1.json')
checks = []
used = set()

def check(label, passed):
    checks.append({'id': label, 'passed': bool(passed)})

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False)

def digest(kind, content):
    return hashlib.sha256(('accdsl.accounting.integration.v1/' + kind + '\0'
                           + canon(content)).encode('ascii')).hexdigest()

def nonnegative_integer(value):
    return type(value) is int and value >= 0

def source(ref):
    p = root / ref['file']['path']
    used.add(p)
    check('source hash ' + str(p.relative_to(root)), sha(p) == ref['file']['sha256'])
    return next(c for c in json.loads(p.read_text())['cases'] if c['id'] == ref['case_id'])

def resolves(ref):
    packet = source(ref['case'])['complete_inputs'][ref['condition_id']]
    return (type(ref.get('value_version')) is str and bool(ref['value_version'])
            and type(packet['version']) is str
            and ref['value_version'] == packet['version'])

forward = {r['old']: r['new'] for r in maps['records']}
inverse = {v: k for k, v in forward.items()}
check('map exact coverage and injectivity', len(forward) == len(inverse) == len(old['records'])
      and set(forward) == set(old['records']) and set(inverse) == set(new['records']))
check('case order retained', [x['id'] for x in old['cases']] == [x['id'] for x in new['cases']])

def undo(value):
    if isinstance(value, str):
        return inverse.get(value, value)
    if isinstance(value, list):
        return [undo(v) for v in value]
    if isinstance(value, dict):
        return {k: canon(undo(json.loads(v))) if k == 'raw_text' else undo(v)
                for k, v in value.items()}
    return value

required_versions = {'branch': 'version', 'chart': 'version', 'event': 'version',
                     'evidence': 'version', 'assumptions': 'version', 'authority': 'version',
                     'method': 'version', 'context': 'schema_version', 'state': 'sequence',
                     'eligibility_input': 'schema_version', 'request': 'schema_version',
                     'assessment': 'schema_version'}
baseline_failures = []
for key, row in old['records'].items():
    field = required_versions.get(row['kind'])
    if field and not nonnegative_integer(row['content'].get(field)):
        baseline_failures.append({'record': key, 'kind': row['kind'], 'field': field,
                                  'value': row['content'].get(field)})
check('baseline has exactly seventeen evidence-version failures',
      len(baseline_failures) == 17 and all(x['kind'] == 'evidence' for x in baseline_failures))
expected_version_rows = []
for entry in maps['records']:
    k, n = entry['old'], entry['new']
    previous, current = old['records'][k], new['records'][n]
    check('map kind ' + k, previous['kind'] == current['kind'] == entry['kind'])
    restored = undo(current)
    if current['kind'] == 'evidence':
        v = previous['content']['version']
        check('declared numeric mapping ' + k,
              v in [f'integration-E{i:02}' for i in range(1, 18)]
              and type(current['content']['version']) is int
              and current['content']['version'] == int(v[-2:]))
        expected_version_rows.append({'old': v, 'new': current['content']['version'],
                                      'old_ref': k, 'new_ref': n})
        restored['content']['version'] = v
    check('all semantic fields preserved ' + k, restored == previous)
    check('canonical digest ' + n, digest(current['kind'], current['content']) == n)
    check('original canonical digest ' + k, digest(previous['kind'], previous['content']) == k)
    field = required_versions.get(current['kind'])
    if field:
        check('required numeric field ' + n, nonnegative_integer(current['content'].get(field)))
    for name in ['version', 'schema_version', 'sequence']:
        if name in current['content']:
            check('numeric field ' + name + n, nonnegative_integer(current['content'][name]))
check('version map exact', maps['evidence_versions'] == expected_version_rows)
check('all nonrecord content preserved',
      undo({k: v for k, v in new.items() if k != 'records'}) ==
      {k: v for k, v in old.items() if k != 'records'})

for ex in examples['record_versions']:
    actual = nonnegative_integer(ex['record'].get('version'))
    check('record type example ' + ex['id'], actual == ex['expected_valid'])
for ex in examples['condition_versions']:
    check('source version example ' + ex['id'], resolves(ex['condition']) == ex['expected_resolves'])

records = dict(legacy['records'], **new['records'])
def get(ref, kind):
    check('reference closure ' + str(ref), ref in records)
    row = records[ref]
    check('reference kind ' + ref, row['kind'] == kind)
    return row['content']

# All record reference fields used by this finite integration schema. FileRefs
# and CaseRefs are checked separately; arbitrary hex strings are not references.
links = {
    'branch': {'context':'context'}, 'chart': {'context':'context'},
    'state': {'context':'context','branch':'branch','chart':'chart'},
    'event': {'context':'context','branch':'branch','time':'time'},
    'admission': {'evidence':'evidence','time':'time'},
    'request': {'event':'event','opening':'state','context':'context','branch':'branch',
                'time':'time','chart':'chart','authority':'authority','method':'method',
                'evidence':'evidence','admissions':'admission','assumptions':'assumptions',
                'eligibility':'eligibility_input'},
    'assessment': {'request':'request','authority':'authority','method':'method',
                   'eligibility':'eligibility_input'},
    'response': {'submission':'submission','request':'request','assessment':'assessment',
                 'diagnostic_journal':'journal','diagnostic_delta':'delta','receipt':'receipt',
                 'observed_state':'state'},
}
for ref, row in new['records'].items():
    for field, kind in links.get(row['kind'], {}).items():
        value = row['content'][field]
        for target in value if isinstance(value, list) else [value]:
            if target is not None:
                get(target, kind)
    if row['kind'] == 'eligibility_input':
        for field, value in row['content']['bindings'].items():
            for target in value if isinstance(value, list) else [value]:
                get(target, links['request'][field])

def file_refs(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            p = root / value['path']; used.add(p)
            check('pinned file ' + value['path'], p.is_file() and sha(p) == value['sha256'])
        if 'file' in value and 'case_id' in value:
            source(value)
        for v in value.values(): file_refs(v)
    elif isinstance(value, list):
        for v in value: file_refs(v)
file_refs(new)

order = [f'C{i:02}' for i in range(1, 11)]
precedence = ['ineligible', 'outside_scope', 'unresolved', 'eligible']
pairs = set()
old_requests = {x['request'] for x in old['cases']}
committed_requests = {v['content']['request'] for v in legacy['records'].values()
                      if v['kind'] == 'receipt'}
for ex in new['cases']:
    ident = ex['id']; request = get(ex['request'], 'request')
    assessment = get(ex['assessment'], 'assessment')
    eligibility = get(request['eligibility'], 'eligibility_input')
    src = source(ex['source_case'])
    check(ident + ' same source', source(eligibility['source_case']) == src)
    check(ident + ' ordered conditions', [c['condition_id'] for c in eligibility['conditions']] == order)
    for condition in eligibility['conditions']:
        check(ident + ' exact source-version ' + condition['condition_id'], resolves(condition))
    for field, value in eligibility['bindings'].items():
        check(ident + ' eligibility binding ' + field, request[field] == value)
    v = {k: p['value'] for k, p in src['complete_inputs'].items()}
    statuses = dict.fromkeys(order, 'satisfied_conditionally')
    if not ('2023-01-01' <= v['C01']['annual_period_start'] < '2026-07-01'): statuses['C01'] = 'outside_scope'
    if v['C03']['party_to_contract'] is False: statuses['C03'] = 'ineligible'
    if not v['C05']['rationale_available']: statuses['C05'] = 'unresolved'
    if v['C07']['incremental'] is None: statuses['C07'] = 'unresolved'
    q, o = [v['C09'][k] for k in ['identical_instrument_active_market_quote', 'technique_only_observable_market_data']]
    if Decimal(v['C06']['price']) == Decimal(v['C06']['fair_value']):
        valuation = 'not_applicable'; statuses['C09'] = 'not_applicable'; method = 'conditional'
    else:
        pairs.add((q, o))
        valuation = 'B5.1.2A(a)' if q is True or o is True else 'B5.1.2A(b)' if q is False and o is False else 'unknown'
        statuses['C09'] = 'unresolved' if valuation == 'unknown' else 'satisfied_conditionally'
        statuses['C10'] = 'unresolved' if valuation == 'unknown' else 'outside_scope'
        method = 'unresolved' if valuation == 'unknown' else 'unavailable'
    summary = next((s for s in precedence if s in statuses.values()), 'eligible')
    check(ident + ' derived statuses', {f['condition']:f['status'] for f in assessment['findings']} == statuses)
    check(ident + ' derived outcome', [assessment['status'], assessment['valuation_branch'], assessment['method_applicability']] == [summary, valuation, method])
    check(ident + ' findings preserved', assessment['findings'] == src['condition_findings'])
    check(ident + ' no receipt alias', ex['request'] not in old_requests | committed_requests)
    check(ident + ' schema and no posting', request['schema_version'] == 2 and request['operation'] == 'assess_only' and assessment['posting_permitted'] is False)
    check(ident + ' raw request', json.loads(get(ex['submission'], 'submission')['raw_text']) == request)
    response = get(ex['response'], 'response')
    check(ident + ' response links', response['request'] == ex['request'] and response['assessment'] == ex['assessment'] and response['submission'] == ex['submission'])
    check(ident + ' committed domains unchanged', ex['before'] == ex['after'] and set(ex['before']) == {'identity_index','committed_journals','selected_state','committed_receipts'})
    check(ident + ' no new commitment', response['receipt'] is None and response['commit_status'] == 'not_committed' and response['additional_commit'] is False)
check('all nine valuation pairs', pairs == {(a,b) for a in [True,False,None] for b in [True,False,None]})
repeat = new['repeat_assessment']; first = next(x for x in new['cases'] if x['id'] == repeat['first_case'])
check('repeat assessment retained without receipt', repeat['same_request'] == first['request'] and repeat['same_assessment'] == first['assessment'] and repeat['receipt'] is None and repeat['status'] == 'assessed')
check('exact R01-R06 references retained', new['predecessor_exchanges'] == old['predecessor_exchanges'] and len(new['predecessor_exchanges']) == 6)
replay = source(new['committed_replay']['case'])
last = get(replay['responses'][-1], 'response'); receipt = get(last['receipt'], 'receipt')
check('original committed replay remains exact', new['committed_replay'] == old['committed_replay'] and last['commit_status'] == 'committed' and last['additional_commit'] is False and receipt['request'] == last['request'])
for p, h in inputs['predecessor_files'].items():
    check('preserved ' + p, sha(root / p) == h)
used.update(base / n for n in ['accounting-integration-fixtures-v1.json', 'accounting-integration-fixtures-v2.json', 'accounting-records-fixtures-v1.json', 'accounting-integration-typing-map-v1.json', 'accounting-integration-typing-cases-v1.json', 'accounting-integration-typing-inputs-v1.json', 'accounting-integration-typing-contract-v1.md'])
used.add(Path(__file__).resolve())
report = {
    'schema_version': 'accdsl.accounting.integration.typing.verification.v1',
    'passed': all(c['passed'] for c in checks), 'total': len(checks),
    'passed_count': sum(c['passed'] for c in checks), 'checks': checks,
    'baseline_expected_failures': baseline_failures,
    'input_hashes': {str(p.relative_to(root)):sha(p) for p in sorted(used)},
    'manifest': {'command': ['python3', *sys.argv], 'environment': {'python':sys.version, 'executable':sys.executable, 'platform':platform.platform(), 'packages':'standard library only'},
                 'git_commit':'N/A: unusable repository marker; input hashes retained',
                 'device_status':'CPU only; no GPU detection or framework imports',
                 'data_version':'pinned synthetic fixtures v1 and v2', 'seeds':'N/A: deterministic',
                 'wall_seconds':time.monotonic()-started,
                 'plan_file':'data/accounting-master/runs/20261005T150545-71a70996/P16/replan-2/plan-0.response.json',
                 'result_file':'data/accounting-master/deliverables/P16/result.md', 'output_file':sys.argv[1]},
    'limits':'Finite type and preservation checks; not complete added-field validation, rejection exchanges, runtime enforcement, accounting validity, forecast validity or human acceptance.'}
with Path(sys.argv[1]).open('x') as stream:
    json.dump(report, stream, indent=2); stream.write('\n')
print(json.dumps({'passed':report['passed'], 'total':report['total'], 'baseline_expected_failures':len(baseline_failures), 'failures':[c for c in checks if not c['passed']]}))
sys.exit(0 if report['passed'] else 1)
