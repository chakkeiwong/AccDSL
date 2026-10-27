"""Bounded consistency diagnostic for four specified requests, not a product validator."""
import argparse
import hashlib
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = 'docs/design/proposal/architecture/'
started = time.monotonic()
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
checks, hashes, observations = [], {}, []

def check(label, value):
    checks.append({'id': label, 'passed': bool(value)})

def content_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()

def digest(path):
    value = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    hashes[path] = value
    return value

def load(path):
    digest(path)
    return json.loads((ROOT / path).read_text())

def pointer(value, ptr):
    for part in ptr.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def resolve(ref):
    check('pin ' + ref['path'], digest(ref['path']) == ref['sha256'])
    check('locator ' + ref['path'], bool(ref['locator']))
    if 'json_pointer' in ref:
        return pointer(json.loads((ROOT / ref['path']).read_text()), ref['json_pointer'])

def refs_in(record):
    out = set()
    for key in ('family_ref', 'view_ref', 'model_ref', 'source_joint_model_ref', 'semantic_model_ref', 'mapping_ref', 'time_ref', 'admission_ref', 'justification', 'predecessor'):
        if record.get(key):
            out.add(record[key])
    out.update(record.get('provenance', []))
    if isinstance(record.get('coordinates'), list):
        out.update(record['coordinates'])
    out.update(record.get('coordinate_order', []))
    out.update(record.get('coordinate_map', {}).values())
    return out

def closure(roots, records, declarations, label):
    pending, seen = list(roots), set()
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        check(label + ' resolves ' + key, key in records)
        if key in records:
            pending.extend(refs_in(records[key]) - seen)
    check(label + ' declared closure', seen <= set(declarations))
    check(label + ' every declaration available', set(declarations) <= set(records))
    return sorted(seen)

def identity(key, value):
    check('immutable identity ' + key, key == value['id'] + '@' + str(value['version']))

fixture_path = BASE + 'uncertainty-malformed-fixtures-v1.json'
d = load(fixture_path)
check('exactly two paired cases', [p['id'] for p in d['pairs']] == ['MF01_array_control', 'MF02_scalar_rejected'])
control, rejected = d['pairs']
# Derive field-type findings before traversing any request references.
derived = {}
for arm in ('family_linked', 'self_contained'):
    for pair in (control, rejected):
        q = pair[arm]['input']
        envelope_valid = isinstance(q['request_id'], str) and q['request_id'].startswith('request:') and q['version'] == 1 and q['operation'] == 'evaluate_event'
        check(pair['id'] + arm + ' usable envelope', envelope_valid)
        field = q['event_refs']
        finding = [] if isinstance(field, list) else [{'reason_code': 'REQUEST_FIELD_TYPE_INVALID', 'field_path': '/event_refs', 'expected_type': 'array', 'actual_type': 'string' if isinstance(field, str) else type(field).__name__}]
        derived[(pair['id'], arm)] = finding
        check(pair['id'] + arm + ' field type derived', bool(finding) == (pair is rejected))
        if not finding:
            check(arm + ' exact reference elements', all(isinstance(x, str) and x.rpartition('@')[2].isdigit() for x in field))
for ref in [d['specification']] + d['source_evidence']:
    resolve(ref)
original = resolve(control['baseline'])
reg = {key: resolve(ref) for key, ref in d['external_registry'].items()}
for key, record in reg.items():
    identity(key, record)
linked, owned = control['family_linked']['input'], control['self_contained']['input']
local = owned['records']
coords = {}
for key, value in local.items():
    identity(key, value)
    if value['kind'] == 'self_contained_finite_joint_model':
        for cid, cv in value['coordinates'].items():
            identity(cid, cv)
            check('nested coordinate consistency ' + cid, cid not in coords or coords[cid] == cv)
            coords[cid] = cv
all_records = {**reg, **local, **coords}
check('no local/external collisions', not (set(local) & set(reg)))
external = [r['ref'] for r in owned['external_dependencies']]
check('same external availability', set(external) == set(linked['dependencies']))
check('complete owned declarations', set(owned['local_dependencies']) == set(local))
check('both available versions retained', {'model:tri@1', 'model:tri@2'} <= set(linked['dependencies']))
check('old models selected', linked['model_ref'] == 'model:tri@1' and owned['joint_model_ref'] == 'joint-model:stale-owned@1' and owned['mapping_ref'] == 'mapping:stale-owned-to-family@1')
linked_closure = closure([linked['model_ref'], linked['family_ref'], linked['view_ref'], linked['attachment_ref']] + linked['event_refs'] + list(d['validation_context'].values()), reg, linked['dependencies'], 'linked control')
owned_closure = closure([owned['joint_model_ref'], owned['mapping_ref'], owned['attachment_ref']] + owned['event_refs'] + list(d['validation_context'].values()), all_records, external + owned['local_dependencies'] + list(coords), 'owned control')
for version in (1, 2):
    mp = local['mapping:stale-owned-to-family@' + str(version)]
    model, semantic, family = local[mp['source_joint_model_ref']], reg[mp['semantic_model_ref']], reg[mp['family_ref']]
    cm, om = mp['coordinate_map'], mp['outcome_map']
    check('map version ' + str(version), model['version'] == semantic['version'] == version)
    check('coordinate bijection ' + str(version), set(cm) == set(model['coordinate_order']) and len(set(cm.values())) == len(cm) and [cm[x] for x in model['coordinate_order']] == semantic['coordinates'])
    check('outcome bijection ' + str(version), set(om) == set(model['sample_space']['outcomes']) and len(set(om.values())) == len(om) and set(om.values()) == set(family['sample_space']['outcomes']))
    for key, target in cm.items():
        check('coordinate meaning ' + key, {k:v for k,v in model['coordinates'][key].items() if k != 'id'} == {k:v for k,v in reg[target].items() if k != 'id'})
    for key, target in om.items():
        check('assignments ' + key, {reg[cm[c]]['concept']: v for c,v in model['assignments'][key].items()} == family['assignments'][target])
    check('mapped masses ' + str(version), {om[k]:v for k,v in model['mass_or_density']['masses'].items()} == semantic['mass_or_density']['masses'])
    for key in ('measure_kind', 'purpose', 'dependence', 'provenance', 'justification', 'information_cutoff', 'evidence_cutoff', 'evaluator'):
        check('model context ' + str(version) + key, model[key] == semantic[key])
    check('request support context ' + str(version), model['support_restrictions'] == linked['support_restrictions'] and model['event_representation'] == linked['event_representation'])
mp = local[owned['mapping_ref']]
levent, oevent = reg[linked['event_refs'][0]], local[owned['event_refs'][0]]
check('event correspondence', {mp['outcome_map'][x] for x in oevent['selector']} == set(levent['selector']) and owned['event_correspondence'][owned['event_refs'][0]] == linked['event_refs'][0])
for key in ('version', 'kind', 'family_ref', 'view_ref', 'selector_kind', 'projection', 'provenance'):
    check('event context ' + key, levent[key] == oevent[key])
check('event coordinate correspondence', [mp['coordinate_map'][x] for x in oevent['coordinates']] == levent['coordinates'])
for arm, records, modelkey in [('family_linked', reg, 'model_ref'), ('self_contained', all_records, 'joint_model_ref')]:
    c, b = control[arm], rejected[arm]
    q, bad, expected = c['input'], b['input'], b['expected']
    check(arm + ' control exact SC01 input', {k:v for k,v in q.items() if k != 'request_id'} == {k:v for k,v in original[arm]['input'].items() if k != 'request_id'})
    check(arm + ' unchanged roles', c['dependency_roles'] == b['dependency_roles'] == original[arm]['dependency_roles'])
    delta = sorted(k for k in q if q[k] != bad[k])
    check(arm + ' only type and identity change', set(q) == set(bad) and delta == ['event_refs', 'request_id'])
    check(arm + ' precise semantic delta', b['semantic_delta'] == [{'op':'replace','path':'/event_refs','before':q['event_refs'],'after':bad['event_refs']}] and bad['event_refs'] == q['event_refs'][0])
    check(arm + ' mechanical delta', b['mechanical_identity_changes'] == ['/request_id'])
    model, event, attachment = records[q[modelkey]], records[q['event_refs'][0]], records[q['attachment_ref']]
    check(arm + ' compatible bindings', event['model_ref'] == attachment['model_ref'] == q[modelkey] and event['family_ref'] == attachment['family_ref'] == 'family:tri@1' and event['view_ref'] == attachment['view_ref'] == 'view:tri@1')
    masses = {k:Fraction(v) for k,v in model['mass_or_density']['masses'].items()}
    space = model['sample_space']['outcomes']
    check(arm + ' finite law coverage', len(space) == len(set(space)) and set(masses) == set(space))
    check(arm + ' nonnegative unit law', all(v >= 0 for v in masses.values()) and sum(masses.values()) == 1)
    check(arm + ' selector subset', set(event['selector']) <= set(space) and len(event['selector']) == len(set(event['selector'])))
    probability = sum((masses[x] for x in event['selector']), Fraction())
    check(arm + ' independent control probability', str(probability) == c['expected']['probability'] == '5/6')
    for key, value in {'disposition':'EVALUATED','structural_validity':'valid','mathematical_status':'satisfied','attachment_status':'attached_assumption','computation_status':'evaluated'}.items():
        check(arm + ' control receipt ' + key, c['expected'][key] == value)
    check(arm + ' pre-state attachment retained', attachment['status'] == 'attached_assumption')
    for key, value in {'disposition':'REQUEST_INVALID','reason_codes':['REQUEST_FIELD_TYPE_INVALID'],'structural_validity':'invalid','mathematical_status':'unresolved','attachment_status':'unchanged_not_revalidated','computation_status':'not_computed','probability':None,'empirical_justification':'not_established','capability_status':'specified_only_no_runtime','family_effect':'unchanged','old_view':'view:tri@1','proposed_view':'view:tri@1','validated_dependency_refs':[],'reference_retention_status':'retained_not_validated_by_rejected_operation','next_permissible_operations':['submit_corrected_request'],'future_dependencies':['model_migration']}.items():
        check(arm + ' rejection receipt ' + key, expected[key] == value)
    check(arm + ' actual type finding', expected['field_errors'] == derived[(rejected['id'], arm)])
    trace = expected['validation_trace']
    check(arm + ' stopped before reference traversal', trace == {'1_envelope':'passed','1_operation_fields':'failed','1_registry_identities':'not_checked','2_semantic_resolution':'not_checked','3_dependency_resolution':'not_checked','4_bindings':'not_checked','5_finite_law':'not_checked','6_event_selector':'not_checked','event_evaluation':'not_checked'})
    sub = expected['submission']
    check(arm + ' exact submission preserved', sub['request_ref'] == expected['request_ref'] == bad['request_id']+'@1' and sub['content_sha256'] == content_hash(bad) and sub['submitted_value'] == bad['event_refs'] and sub['submitted_value_sha256'] == content_hash(bad['event_refs']) and pointer(d, sub['complete_request_locator']) == bad)
    supplied = {**reg, **q.get('records', {})}
    state = expected['state_preservation']
    wanted = {k:content_hash(supplied[k]) for k in ('family:tri@1','view:tri@1',q['attachment_ref'])}
    check(arm + ' state unchanged', state['pre'] == state['post'] == wanted)
    check(arm + ' all supplied records retained', state['supplied_record_hashes'] == {k:content_hash(v) for k,v in supplied.items()})
    check(arm + ' complete preserved refs', set(expected['preserved_records']) == set(supplied) | {bad['request_id']+'@1'})
    check(arm + ' retained support refs', expected['support_references'] == c['expected']['support_references'])
    check(arm + ' no pre-state invalidation', expected['pre_state_assessment']['attachment_status'] == attachment['status'] and expected['pre_state_assessment']['mathematical_status'] == 'satisfied')
    correction = expected['correction']
    check(arm + ' explicit correction only', correction == {'new_request_id_required':True,'operation':'evaluate_event','field_path':'/event_refs','corrected_value':q['event_refs'],'requires_full_validation':True,'automatic_repair':False,'performed':False,'preserve_rejected_request':True})
    for pair in (control, rejected):
        req, exp = pair[arm]['input'], pair[arm]['expected']
        check(pair['id'] + arm + ' identity linkage', exp['request_ref'] == req['request_id']+'@1' and exp['result_id'] == req['request_id'].replace('request:', 'result:') and exp['attachment_ref'] == req['attachment_ref'])
    observations.append({'encoding':arm,'control_probability':str(probability),'control_total_mass':str(sum(masses.values())),'rejection_derived_from_actual_type':derived[(rejected['id'],arm)],'rejected_probability':None,'rejected_operation_validated_dependencies':[],'control_dependency_closure':linked_closure if arm=='family_linked' else owned_closure,'runtime_executed':False})
for pair in (control, rejected):
    le, oe, corr = pair['family_linked']['expected'], pair['self_contained']['expected'], pair['receipt_correspondence']
    check(pair['id'] + ' complete receipt correspondence', set(le) == set(corr['direct_equal_fields']+corr['encoding_fields']+corr['dependency_fields']) and set(oe)-set(le) == set(corr['owned_only_fields']))
    for key in corr['direct_equal_fields']:
        check(pair['id'] + ' corresponding ' + key, le[key] == oe[key])
    translation = pair['self_contained']['encoding_to_baseline']
    for key in corr['dependency_fields']:
        converted = {translation.get(x,x).replace('-owned@','-linked@') for x in oe[key] if not x.startswith('mapping:')}
        check(pair['id'] + ' dependency correspondence ' + key, converted == set(le[key]))
    check(pair['id'] + ' attachment translation', translation[oe['attachment_ref']] == le['attachment_ref'])
    check(pair['id'] + ' immutable audit roles', oe['audit_references'] == original['self_contained']['expected']['audit_references'])
for path in ('uncertainty-malformed-diagnostic-v1.py', 'uncertainty-malformed-prior-result-v1.md'):
    digest(BASE + path)
failures = [c['id'] for c in checks if not c['passed']]
report = {'schema_version':'accdsl.proposal.malformed_verification.v1','passed':not failures,'checks':checks,'failures':failures,'input_hashes':hashes,'observations':observations,'command':'PYTHONDONTWRITEBYTECODE=1 python3 '+BASE+'uncertainty-malformed-diagnostic-v1.py --output '+args.output,'environment':{'python':platform.python_version(),'packages':'standard library only','cpu_gpu':'CPU-only JSON/Fraction diagnostic; no framework or device detection','git_commit':'unavailable: unusable .git marker; source hashes recorded','data_version':'pinned SC01 and local fixture v1','seeds':'N/A: deterministic'},'wall_seconds':time.monotonic()-started,'plan':BASE+'uncertainty-malformed-comparison-v1.md','result':'data/accounting-master/deliverables/P16/result.md','output':args.output,'author_diagnostic_repair':'Initial run stopped before report creation: support_restrictions belongs to linked request, not semantic model. Corrected comparison to the declared request fields and reran.', 'limits':['Specified receipts are not executed product responses.','No general equivalence, architecture preference or performance comparison.','No storage, accounting, empirical forecast or human acceptance claim.','Author checks do not replace independent substantive review.']}
with (ROOT / args.output).open('x') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps({'passed':not failures,'checks':len(checks),'failures':failures,'output':args.output}))
sys.exit(bool(failures))
