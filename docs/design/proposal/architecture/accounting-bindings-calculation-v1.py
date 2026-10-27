"""Build and verify six fixed document examples; no accounting runtime API.
Run once from repository root. All new evidence uses exclusive creation.
"""
import copy
import hashlib
import json
import platform
import sys
import time
from datetime import date
from pathlib import Path

START = time.monotonic()
OUT = Path('docs/design/proposal/architecture')
PREDECESSOR = OUT / 'accounting-records-fixtures-v1.json'
CONTRACT = OUT / 'accounting-bindings-contract-v1.md'
SCRIPT = OUT / 'accounting-bindings-calculation-v1.py'
FIXTURE = OUT / 'accounting-bindings-fixtures-v1.json'
VERIFY = OUT / 'accounting-bindings-verification-v1.json'
INPUTS = OUT / 'accounting-bindings-inputs-v1.json'

def enc(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')

def digest(kind, content):
    return hashlib.sha256(('accdsl.accounting.records.v1/' + kind).encode('ascii') + b'\0' + enc(content)).hexdigest()

def fref(p):
    return {'path': str(p), 'sha256': hashlib.sha256(Path(p).read_bytes()).hexdigest()}

def save(p, obj):
    with p.open('x') as f:
        json.dump(obj, f, indent=2, ensure_ascii=True, allow_nan=False)
        f.write('\n')

def file_refs(obj):
    if isinstance(obj, dict):
        if 'path' in obj and 'sha256' in obj:
            yield {'path': obj['path'], 'sha256': obj['sha256']}
        for v in obj.values():
            yield from file_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from file_refs(v)

old = json.loads(PREDECESSOR.read_text())
arch = json.loads(Path('data/accounting-master/deliverables/P16/architecture.json').read_text())
preserved = list(file_refs(arch))
for r in preserved:
    assert fref(r['path']) == r, r['path']
# Snapshot all existing architecture-directory files; no predecessor is rewritten.
snapshot = [fref(p) for p in sorted(OUT.iterdir()) if p.is_file() and not p.name.startswith('accounting-bindings-')]
save(INPUTS, {'schema_version': 'accdsl.accounting.bindings.inputs.v1',
              'architecture_references': preserved, 'predecessor_files': snapshot})
records = copy.deepcopy(old['records'])
new_records = {}

def get(ref):
    return records[ref]['content']

def add(kind, c):
    ref = digest(kind, c)
    row = {'kind': kind, 'content': c}
    assert ref not in records or records[ref] == row
    records[ref] = row
    if ref not in old['records']:
        new_records[ref] = row
    return ref

LINKS = {
 'context': {}, 'branch': {'context':'context'}, 'time': {}, 'authority': {},
 'method': {'authority':'authority'}, 'assumptions': {}, 'evidence': {},
 'admission': {'evidence':'evidence','time':'time'}, 'chart': {'context':'context'},
 'state': {'context':'context','branch':'branch','chart':'chart'},
 'event': {'context':'context','branch':'branch','time':'time'},
 'request': {'event':'event','opening':'state','context':'context','branch':'branch',
             'time':'time','chart':'chart','authority':'authority','method':'method',
             'evidence':'evidence','admissions':'admission','assumptions':'assumptions'},
 'assessment': {'request':'request','authority':'authority','method':'method'},
 'journal': {'request':'request','assessment':'assessment','context':'context','branch':'branch','chart':'chart'},
 'delta': {'request':'request','context':'context','branch':'branch','chart':'chart'},
 'receipt': {'request':'request','assessment':'assessment','journal':'journal','delta':'delta','opening':'state','closing':'state'},
 'submission': {},
 'response': {'submission':'submission','request':'request','assessment':'assessment',
              'diagnostic_journal':'journal','diagnostic_delta':'delta','receipt':'receipt','observed_state':'state'}}

def refs(kind, c):
    for field, target in LINKS[kind].items():
        v = c[field]
        for ref in v if isinstance(v, list) else [v]:
            if ref is not None:
                assert ref in records and records[ref]['kind'] == target, (kind, field, ref)
                yield ref

def closure(q):
    reached = set()
    def visit(ref, ancestors):
        assert ref not in ancestors, 'cyclic dependency'
        if ref in reached:
            return
        row = records[ref]
        assert digest(row['kind'], row['content']) == ref
        reached.add(ref)
        for child in refs(row['kind'], row['content']):
            visit(child, ancestors | {ref})
    for ref in refs('request', q):
        visit(ref, set())
    return sorted(reached)

base = old['cases'][0]
assert base['id'] == 'R01_success'
q0 = json.loads(get(base['input_submission'])['raw_text'])
response0 = get(base['responses'][0])
branch2 = add('branch', {**get(q0['branch']), 'version':2})
time2 = add('time', {**get(q0['time']), 'economic_date':'2024-01-03'})
chart2 = add('chart', {**get(q0['chart']), 'version':2})
authority2 = add('authority', {**get(q0['authority']), 'version':2})
# Explicit fixed example mutations; expectations below are specified separately.
mutations = [('event','branch',branch2), ('opening','branch',branch2),
             ('event','time',time2), ('opening','chart',chart2),
             ('method','authority',authority2)]
codes = ['EVENT_BRANCH_MISMATCH','OPENING_BRANCH_MISMATCH','EVENT_TIME_MISMATCH',
         'OPENING_CHART_MISMATCH','METHOD_AUTHORITY_MISMATCH']
null_fields = ['request','assessment','diagnostic_journal','diagnostic_delta','receipt','observed_state']
invalid_status = {**response0['statuses'], 'structural_validity':'invalid',
                  'mathematical_status':'unresolved', 'computation_status':'not_computed'}
cases = [{'id':'B00_control', 'predecessor_case':{'file':fref(PREDECESSOR),'case_id':'R01_success'},
          'input_submission':base['input_submission'], 'submitted_dependencies':closure(q0),
          'validated_request':response0['request'], 'expected_mismatches':[],
          'response':base['responses'][0], 'before':base['before'], 'after':base['after'],
          'downstream':'Exact retained R01 exchange; eligibility stipulated, not reassessed'}]
for i, (owner, field, alternate) in enumerate(mutations, 1):
    q = copy.deepcopy(q0)
    original = q[owner]
    q[owner] = add(records[original]['kind'], {**get(original), field:alternate})
    sub = add('submission', {'wire_format':'ASCII_JSON','raw_text':enc(q).decode('ascii')})
    c = {**copy.deepcopy(response0), **dict.fromkeys(null_fields),
         'submission':sub, 'status':'rejected', 'reason_codes':[codes[i-1]],
         'commit_status':'not_committed','additional_commit':False,'statuses':invalid_status,
         'metadata':{'response_id':'binding-B%02d' % i,'operation':'submit'}}
    res = add('response', c)
    cases.append({'id':'B%02d' % i, 'input_submission':sub,
                  'submitted_dependencies':closure(q), 'validated_request':None,
                  'diagnostic_content_digest':{'value':digest('request',q),'role':'unvalidated_candidate'},
                  'synthetic_change':{'owner':owner,'field':field,'original_record':original,'replacement_record':q[owner]},
                  'expected_mismatches':[{'rule':'B%d' % i,'reason_code':codes[i-1],
                                          'left':alternate,'right':q[field]}],
                  'response':res,'before':copy.deepcopy(base['before']),'after':copy.deepcopy(base['before']),
                  'evaluation':{'identity_lookup':'not_evaluated','freshness':'not_evaluated','eligibility':'not_evaluated'}})
fixture = {'schema_version':'accdsl.accounting.bindings.fixtures.v1',
           'scope':'Six fixed design examples; no runtime, authority finding or full-phase acceptance',
           'imports':[{'file':fref(PREDECESSOR),'selector':'records and cases[id=R01_success]'}],
           'specification':fref(CONTRACT), 'records':new_records, 'cases':cases,
           'limits':['A01 and branch eligibility stipulated; A03 remains unresolved in predecessor.',
                     'Alternative branch/chart/authority versions are synthetic, not source amendments.',
                     'Invalid candidates have diagnostic digests only, never validated request references.']}
save(FIXTURE, fixture)
# Reload actual saved bytes; validate reference closure and relational consequences.
fixture = json.loads(FIXTURE.read_text())
checks = []
def check(name, value):
    checks.append({'id':name, 'passed':bool(value)})

for ref, row in records.items():
    check('digest:' + ref, digest(row['kind'], row['content']) == ref)
    list(refs(row['kind'], row['content']))
for r in file_refs(fixture):
    check('file:' + r['path'], fref(r['path']) == r)
comparisons = []
for n, case in enumerate(fixture['cases']):
    q = json.loads(get(case['input_submission'])['raw_text'])
    e, o, m = get(q['event']), get(q['opening']), get(q['method'])
    check(case['id']+':dependency_bundle', closure(q) == case['submitted_dependencies'])
    # Independent explicit equations, not the construction mutation table.
    actual = [e['branch'] != q['branch'], o['branch'] != q['branch'],
              e['time'] != q['time'], o['chart'] != q['chart'], m['authority'] != q['authority']]
    check(case['id']+':single_intended_mismatch', actual == [n == j for j in range(1,6)])
    expected = [codes[j] for j,bad in enumerate(actual) if bad]
    check(case['id']+':specified_reasons', [r['reason_code'] for r in case['expected_mismatches']] == expected)
    check(case['id']+':context', all(get(q[k])['context'] == q['context'] for k in ['event','opening','branch','chart']))
    check(case['id']+':nested_context', get(o['branch'])['context'] == q['context'] == get(o['chart'])['context'] == get(e['branch'])['context'])
    ctx = get(q['context'])
    check(case['id']+':identity', q['identity'] == {'entity_id':ctx['entity_id'],'book_id':ctx['book_id'],
          'branch_id':get(q['branch'])['branch_id'],'business_event_id':e['business_event_id']})
    check(case['id']+':admission', len(q['evidence']) == len(q['admissions']) and all(
          get(ad)['evidence'] == ev and get(ad)['time'] == q['time'] for ev,ad in zip(q['evidence'],q['admissions'])))
    check(case['id']+':chart_accounts', set(o['balances']) == {a['account_id'] for a in get(o['chart'])['accounts']} == {a['account_id'] for a in get(q['chart'])['accounts']})
    check(case['id']+':time_ranges', all(date.fromisoformat(get(t)['reporting_start']) <= date.fromisoformat(get(t)['economic_date']) <= date.fromisoformat(get(t)['reporting_end']) for t in [q['time'],e['time']]))
    res = get(case['response'])
    check(case['id']+':response_fields', set(res) == set(response0))
    check(case['id']+':domain_fields', set(case['before']) == set(base['before']) == set(case['after']))
    if n:
        change = case['synthetic_change']
        original, replacement = get(change['original_record']), get(change['replacement_record'])
        check(case['id']+':single_record_edge', {k for k in original if original[k] != replacement[k]} == {change['field']} and set(original) == set(replacement))
        check(case['id']+':other_request_fields', {k for k in q if q[k] != q0[k]} == {change['owner']})
        check(case['id']+':raw_content_digest', case['diagnostic_content_digest'] == {'value':digest('request',q),'role':'unvalidated_candidate'})
        check(case['id']+':no_validated_candidate', case['validated_request'] is None and digest('request',q) not in records)
        check(case['id']+':unequal_references', case['expected_mismatches'][0]['left'] == replacement[change['field']] != case['expected_mismatches'][0]['right'] == q[change['field']])
        check(case['id']+':rejection', res['status'] == 'rejected' and res['reason_codes'] == expected and all(res[k] is None for k in null_fields))
        check(case['id']+':statuses', res['statuses'] == invalid_status and res['commit_status'] == 'not_committed' and res['additional_commit'] is False)
        check(case['id']+':preserved_submission', res['submission'] == case['input_submission'] and get(res['submission'])['raw_text'] == enc(q).decode('ascii'))
        check(case['id']+':no_downstream_evaluation', set(case['evaluation'].values()) == {'not_evaluated'})
        check(case['id']+':four_parts_unchanged', enc(case['before']) == enc(case['after']) == enc(base['before']))
    else:
        check('B00:exact_retained_control', q == q0 and res == response0 and case['before'] == base['before'] and case['after'] == base['after'])
    comparisons.append({'case':case['id'],'digest_kind_closure':'pass','binding_failures':expected,
                        'binding_result':'reject' if expected else 'pass'})
for r in preserved + snapshot:
    check('preserved:' + r['path'], fref(r['path']) == r)
manifest = {'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/accounting-bindings-calculation-v1.py',
            'python':sys.version.split()[0], 'platform':platform.platform(),
            'environment':'Existing standard-library Python; no dependencies installed',
            'git_commit':'N/A: repository marker unusable; exact input hashes retained',
            'cpu_gpu':'CPU-only file/JSON/hash calculations; no GPU framework imported',
            'data_version':fref(PREDECESSOR),'seeds':'N/A: deterministic fixed examples',
            'wall_seconds':round(time.monotonic()-START,6),
            'plan':'data/accounting-master/runs/20261005T133743-c8a796f3/P16/approved-plan.json',
            'result':'data/accounting-master/deliverables/P16/result.md',
            'inputs':[fref(p) for p in [PREDECESSOR,CONTRACT,SCRIPT,INPUTS]],
            'outputs':[str(FIXTURE),str(VERIFY)]}
result = {'schema_version':'accdsl.accounting.bindings.verification.v1',
          'passed':all(c['passed'] for c in checks), 'tests':len(checks), 'checks':checks,
          'fixture':fref(FIXTURE),'comparisons':comparisons,'manifest':manifest,
          'limits':'Finite specified outcomes; no execution of an accounting endpoint, runtime transaction, authority assessment or general schema validator.'}
save(VERIFY, result)
print(json.dumps({'passed':result['passed'],'checks':len(checks),'cases':len(cases),'new_records':len(new_records),'failures':[c for c in checks if not c['passed']]}))
raise SystemExit(0 if result['passed'] else 1)
