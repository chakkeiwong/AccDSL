"""Bounded author diagnostic for five specified rejection receipts, not a runtime.
Run from repository root. --output must name a fresh JSON report.
"""
import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

BASE = Path('docs/design/proposal/architecture')
FIXTURE = BASE / 'uncertainty-measure-failures-fixtures-v1.json'
SPEC = BASE / 'uncertainty-measure-failures-contract-v1.md'
checks, observations = [], []
def check(label, condition, detail=None):
    checks.append({'id': label, 'passed': bool(condition), 'detail': detail})
def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def read(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
output = Path(args.output)
if output.exists():
    raise SystemExit('Refusing to overwrite existing evidence: ' + str(output))
fixture = read(FIXTURE)
for pin in fixture['baseline'] + [fixture['specification']]:
    check('Pinned baseline/specification ' + pin['path'], file_hash(pin['path']) == pin['sha256'])
baseline_path = next(p['path'] for p in fixture['baseline'] if p['path'].endswith('.json'))
baseline = read(baseline_path)
old_records = baseline['records']
check('Registry additions cannot replace baseline keys', not (old_records.keys() & fixture['records'].keys()))
records = old_records | fixture['records']
check('Exactly five rejection cases', [c['id'] for c in fixture['cases']] == ['MF01','MF02','MF03','MF04','MF05'])
check('Exactly two control records', len(fixture['controls']) == 2)
check('Exactly two candidate additions', len(fixture['records']) == 2)

SINGLE = {'family_ref','view_ref','model_ref','attachment_ref','justification','time_ref','admission_ref','left','right'}
MULTIPLE = {'coordinates','provenance','event_refs'}
def references(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in SINGLE and isinstance(item, str):
                yield item
            elif key in MULTIPLE and isinstance(item, list):
                yield from item
            else:
                yield from references(item)
    elif isinstance(value, list):
        for item in value:
            yield from references(item)

def closure(roots):
    seen, pending = set(), list(roots)
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        if key in records:
            pending.extend(references(records[key]))
    return seen

def law_status(model):
    space = model['sample_space']['outcomes']
    mass = {key: Fraction(value) for key, value in model['mass_or_density']['masses'].items()}
    valid = len(space) == len(set(space)) and set(space) == set(mass)
    valid = valid and all(value >= 0 for value in mass.values()) and sum(mass.values(), Fraction()) == 1
    return valid

for key, record in records.items():
    check('Immutable registry key ' + key, key == record['id'] + '@' + str(record['version']))
    check('Registry reference resolution ' + key, all(ref in records for ref in references(record)))

request_fields = set(baseline['groups'][1]['cases'][0]['input'])
result_fields = set(baseline['groups'][1]['cases'][0]['expected'])

def prerequisite(request, context):
    """Derive the first failure from the input only; no expected result is read."""
    direct = set(references(request)) | set(references(context))
    unknown_events = sorted(set(request.get('event_refs', [])) - records.keys())
    if unknown_events:
        return 'EVENT_REFERENCE_UNRESOLVED', {'unavailable_event_refs': unknown_events}, unknown_events
    check('Other direct semantic references resolve ' + request['request_id'], direct <= records.keys())
    if not direct <= records.keys():
        raise ValueError('Unexpected unresolved non-event semantic reference')
    unavailable = sorted(set(request['dependencies']) - records.keys())
    if unavailable:
        return 'DEPENDENCY_VERSION_UNAVAILABLE', {'unavailable_dependency_refs': unavailable}, unavailable
    required = closure(direct)
    check('Required closure is resolvable ' + request['request_id'], required <= records.keys())
    missing = sorted(required - set(request['dependencies']))
    if missing:
        return 'DEPENDENCY_NOT_DECLARED', {'undeclared_required_refs': missing}, []
    model = records[request['model_ref']]
    family = records[request['family_ref']]
    check('Request/model bindings ' + request['request_id'], all(request[k] == model[k] for k in ['family_ref','view_ref','coordinates','sample_space','measure_kind','purpose','mass_or_density','dependence','information_cutoff','evidence_cutoff']))
    check('Family/view binding ' + request['request_id'], records[request['view_ref']]['family_ref'] == request['family_ref'])
    check('Model/family domain ' + request['request_id'], model['sample_space'] == family['sample_space'] and model['coordinates'] == family['coordinates'])
    if 'attachment_ref' in request:
        attached = records[request['attachment_ref']]
        check('Attachment binding ' + request['request_id'], all(request[k] == attached[k] for k in ['model_ref','family_ref','view_ref','purpose']))
    space = model['sample_space']['outcomes']
    mass = {key: Fraction(value) for key, value in model['mass_or_density']['masses'].items()}
    check('Unique elementary IDs ' + request['request_id'], len(space) == len(set(space)))
    missing_mass, extra_mass = sorted(set(space) - mass.keys()), sorted(mass.keys() - set(space))
    if missing_mass or extra_mass:
        return 'FINITE_MASS_COVERAGE_INCOMPLETE', {'missing_mass_outcomes': missing_mass, 'extra_mass_outcomes': extra_mass, 'listed_mass_total': str(sum(mass.values(), Fraction()))}, []
    check('Complete candidate is a finite law ' + request['request_id'], law_status(model))
    outside = set()
    for event_ref in set(request.get('event_refs', [])):
        event = records[event_ref]
        check('Event binding ' + request['request_id'], all(event[k] == request[k] for k in ['model_ref','family_ref','view_ref','coordinates']))
        check('Scoped finite selector ' + request['request_id'], event['selector_kind'] == 'finite_ids')
        outside.update(set(event['selector']) - set(space))
    if outside:
        return 'EVENT_SELECTOR_OUTSIDE_SAMPLE_SPACE', {'outside_outcomes': sorted(outside)}, []
    return None, {}, []

controls = {c['id']: c for c in fixture['controls']}
baseline_cases = {c['id']: c for g in baseline['groups'] for c in g['cases']}
check('Existing control input preserved', controls['CONTROL-MA03c']['input'] == baseline_cases['MA03c']['input'])
check('Existing control expected preserved', controls['CONTROL-MA03c']['expected'] == baseline_cases['MA03c']['expected'])
for cid, control in controls.items():
    request, expected = control['input'], control['expected']
    check('Control required fields ' + cid, request_fields <= request.keys() and result_fields <= expected.keys())
    reason, detail, unresolved = prerequisite(request, control['validation_context'])
    check('Positive control passes prerequisites ' + cid, reason is None)
    model = records[request['model_ref']]
    if request['operation'] == 'evaluate_event':
        chosen = set(records[request['event_refs'][0]]['selector'])
        probability = str(sum((Fraction(model['mass_or_density']['masses'][x]) for x in chosen), Fraction()))
        check('Existing event control evaluates 5/6', probability == expected['probability'] == '5/6')
        check('Existing idempotent event control', len(set(request['event_refs'])) == 1 and expected['reason_codes'] == ['IDEMPOTENT_EVENT_REFERENCE'])
        disposition = 'EVALUATED'
    else:
        check('Diagonal control preserves two explicit zeros', sum(Fraction(x) == 0 for x in model['mass_or_density']['masses'].values()) == 2)
        check('Diagonal control valid attachment', expected['probability'] is None and expected['attachment_ref'] == 'attachment:diag@1')
        disposition = 'ATTACHED_ASSUMPTION'
    check('Control statuses ' + cid, expected['disposition'] == disposition and expected['structural_validity'] == 'valid' and expected['mathematical_status'] == 'satisfied')
    observations.append({'id': cid, 'derived_disposition': disposition, 'finite_law_valid': law_status(model)})

seen_requests, seen_results = set(), set()
for case in fixture['cases']:
    cid, request, expected = case['id'], case['input'], case['expected']
    request_ref = request['request_id'] + '@' + str(request['version'])
    result_ref = expected['result_id'] + '@' + str(expected['version'])
    check('Unique request/result identities ' + cid, request_ref not in seen_requests and result_ref not in seen_results)
    seen_requests.add(request_ref); seen_results.add(result_ref)
    check('Complete records ' + cid, request_fields <= request.keys() and result_fields <= expected.keys())
    check('Receipt request/operation identity ' + cid, expected['request_ref'] == request_ref and expected['operation'] == request['operation'])
    submitted = case['submission']['bytes']
    check('Submitted bytes preserved ' + cid, json.loads(submitted) == request and digest(submitted) == case['submission']['sha256'] == expected['submission_sha256'])
    pre_state = case['pre_state']
    check('State receipts unchanged ' + cid, expected['state_before'] == pre_state == expected['state_after'])
    check('Old and proposed view unchanged ' + cid, expected['old_view'] == expected['proposed_view'] == pre_state['view_ref'])
    for key, value in pre_state['record_sha256'].items():
        check('Preserved state hash ' + cid + '/' + key, key in old_records and digest(canonical(old_records[key])) == value)
    old_attachment = records[pre_state['attachment_ref']]
    old_model = records[old_attachment['model_ref']]
    check('Old attachment remains valid ' + cid, old_attachment['status'] == 'attached_assumption' and law_status(old_model))
    old_status = {'attachment_ref':pre_state['attachment_ref'], 'structural_validity':'valid', 'mathematical_status':'satisfied', 'empirical_justification':'not_established'}
    check('Separate old law status ' + cid, expected['existing_attachment_law_status'] == old_status)
    reason, detail, unresolved = prerequisite(request, case['validation_context'])
    check('Input-derived rejection reason ' + cid, expected['reason_codes'] == [reason] and reason is not None)
    check('Input-derived observations ' + cid, expected['observations'] == detail)
    check('Unresolved identifiers preserved ' + cid, expected['unresolved_references'] == unresolved)
    roots = set(references(request)) | set(request['dependencies']) | set(references(case['validation_context'])) | set(references(pre_state))
    existing = sorted(closure(roots) & records.keys())
    check('Only available support records ' + cid, expected['support_references'] == existing)
    check('Preserved submission and available records ' + cid, expected['preserved_records'] == [request_ref] + existing)
    check('Unavailable records never claimed preserved ' + cid, not (set(unresolved) & set(expected['preserved_records'] + expected['support_references'])))
    statuses = {'disposition':'REQUEST_INVALID','structural_validity':'invalid','mathematical_status':'unresolved','empirical_justification':'not_established','capability_status':'specified_only_no_runtime','computation_status':'not_computed','probability':None,'family_effect':'unchanged','next_permissible_operations':['revise_request']}
    statuses['attachment_status'] = 'not_attached' if request['operation'] == 'attach_measure' else 'attached_assumption'
    statuses['attachment_ref'] = None if request['operation'] == 'attach_measure' else pre_state['attachment_ref']
    check('Independent rejection status dimensions ' + cid, all(expected[k] == v for k, v in statuses.items()))
    check('Unresolved repair obligation retained ' + cid, expected['unresolved_obligations'] == expected['mathematical_obligations'] and bool(expected['unresolved_obligations']))
    observations.append({'id':cid,'derived_reason':reason,'derived_observations':detail,'unresolved_references':unresolved,'existing_law_valid':law_status(old_model),'state_unchanged':expected['state_before'] == expected['state_after']})

# Verify the deliberately narrow input changes independently of authored receipts.
for case in fixture['cases']:
    request = copy.deepcopy(case['input'])
    control = copy.deepcopy(controls[case['baseline_control']]['input'])
    check('Request lineage ' + case['id'], request['predecessor'] == control['request_id'] + '@1')
    for key in ['request_id','predecessor']:
        request.pop(key); control.pop(key)
    if case['id'] == 'MF01':
        model = copy.deepcopy(records[request['model_ref']]); original = copy.deepcopy(records[control['model_ref']])
        model.pop('id'); original.pop('id')
        model['mass_or_density']['masses']['bin:01@1'] = '0'
        check('Only one missing zero in candidate model', model == original)
        request['mass_or_density']['masses']['bin:01@1'] = '0'
        request['dependencies'] = [control['model_ref'] if x == request['model_ref'] else x for x in request['dependencies']]
        request['model_ref'] = control['model_ref']
    elif case['id'] in {'MF02','MF03'}:
        changed_event = request['event_refs'][0]
        if case['id'] == 'MF03':
            candidate = copy.deepcopy(records[changed_event]); original = copy.deepcopy(records['event:A@1'])
            candidate.pop('id'); original.pop('id'); candidate['selector'].remove('tri:outside@1')
            check('Only one outside selector member', candidate == original)
        request['event_refs'] = ['event:A@1'] * len(request['event_refs'])
        request['dependencies'] = ['event:A@1' if x == changed_event else x for x in request['dependencies']]
    elif case['id'] == 'MF04':
        check('Omitted direct dependency stays available', request['justification'] == 'justification:fixture@1' and request['justification'] in records)
        request['dependencies'].insert(control['dependencies'].index('justification:fixture@1'), 'justification:fixture@1')
    elif case['id'] == 'MF05':
        check('Unavailable exact version has available predecessor', 'evidence:synthetic@2' not in records and 'evidence:synthetic@1' in records)
        request['dependencies'].remove('evidence:synthetic@2')
    check('Single semantic difference restored ' + case['id'], request == control)

paths = [FIXTURE,SPEC,Path(__file__),Path(baseline_path)] + [Path(p['path']) for p in fixture['baseline']]
failures = [item for item in checks if not item['passed']]
report = {'schema_version':'accdsl.proposal.measure_failures.diagnostic.v1','recorded_at':datetime.now(timezone.utc).isoformat(),'passed':not failures,'checks':checks,'total':len(checks),'failures':failures,'observations':observations,'input_hashes':{str(p):file_hash(p) for p in paths},'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-measure-failures-diagnostic-v1.py --output ' + str(output),'environment':{'python':sys.version.split()[0],'packages':'standard library only','gpu':'not used; no numerical framework imported'},'scope':'Input-derived consistency of exactly five rejection examples and two controls; no runtime, accounting, empirical or human acceptance.'}
output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'total':len(checks),'failures':failures,'output':str(output)}))
raise SystemExit(0 if report['passed'] else 1)
