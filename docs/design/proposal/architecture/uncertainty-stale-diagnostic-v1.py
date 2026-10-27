"""Bounded document diagnostic for four specified requests; not a product evaluator."""
import copy
import hashlib
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'docs/design/proposal/architecture'
started = time.monotonic()
checks = []
hashes = {}
observations = []

def check(label, condition):
    checks.append({'id': label, 'passed': bool(condition)})

def digest(path):
    p = ROOT / path
    value = hashlib.sha256(p.read_bytes()).hexdigest()
    hashes[path] = value
    return value

def pointer(data, ptr):
    for token in ptr.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        data = data[int(token)] if isinstance(data, list) else data[token]
    return data

def resolve(ref):
    check('hash ' + ref['path'], digest(ref['path']) == ref['sha256'])
    check('locator ' + ref['path'], bool(ref['locator']))
    if 'json_pointer' in ref:
        return pointer(json.loads((ROOT / ref['path']).read_text()), ref['json_pointer'])

def refs_in(record):
    """Dependencies carried by the explicitly typed fields used in these examples."""
    out = set()
    fields = ('family_ref', 'view_ref', 'model_ref', 'source_joint_model_ref',
              'semantic_model_ref', 'mapping_ref', 'time_ref', 'admission_ref',
              'justification', 'predecessor')
    for key in fields:
        if record.get(key):
            out.add(record[key])
    out.update(record.get('provenance', []))
    coords = record.get('coordinates', [])
    if isinstance(coords, list):
        out.update(coords)
    out.update(record.get('coordinate_order', []))
    out.update(record.get('coordinate_map', {}).values())
    return out

def identity(key, record):
    check('immutable identity ' + key, key == record['id'] + '@' + str(record['version']))

def closure(roots, records, declarations, label):
    pending = list(roots)
    seen = set()
    while pending:
        key = pending.pop()
        if key in seen:
            continue
        seen.add(key)
        check(label + ' resolves ' + key, key in records)
        if key in records:
            pending.extend(refs_in(records[key]) - seen)
    check(label + ' declared closure', seen <= set(declarations))
    return sorted(seen)

def without_version(record):
    return {k: v for k, v in record.items() if k != 'version'}

fixture_path = 'docs/design/proposal/architecture/uncertainty-stale-fixtures-v1.json'
digest(fixture_path)
d = json.loads((ROOT / fixture_path).read_text())
for ref in [d['specification']] + d['source_evidence']:
    resolve(ref)
reg = {key: resolve(ref) for key, ref in d['external_registry'].items()}
for key, record in reg.items():
    identity(key, record)
check('two semantic models differ only in version',
      without_version(reg['model:tri@1']) == without_version(reg['model:tri@2']))
base = json.loads((BASE / 'uncertainty-measure-attachment-fixtures-v2.json').read_text())['groups'][4]['cases'][2]
check('baseline old-model declaration omission retained', 'model:tri@1' not in base['input']['dependencies'])
check('baseline migration omission retained', base['expected']['future_dependencies'] == [])
check('amendments explicitly recorded', len(d['baseline_amendments']) == 2)
for pair in d['pairs']:
    label = pair['id']
    linked = pair['family_linked']['input']
    owned = pair['self_contained']['input']
    le, oe = pair['family_linked']['expected'], pair['self_contained']['expected']
    local = owned['records']
    for key, record in local.items():
        identity(key, record)
    check(label + ' immutable owned versions', without_version(local['joint-model:stale-owned@1']) == without_version(local['joint-model:stale-owned@2']))
    selected = linked['model_ref']
    lm = reg[selected]
    om = local[owned['joint_model_ref']]
    mapping = local[owned['mapping_ref']]
    check(label + ' requested versions correspond', mapping['semantic_model_ref'] == selected and mapping['source_joint_model_ref'] == owned['joint_model_ref'])
    check(label + ' declarations no duplicates', len(linked['dependencies']) == len(set(linked['dependencies'])))
    check(label + ' both semantic versions declared', {'model:tri@1', 'model:tri@2'} <= set(linked['dependencies']))
    for key in ('family_ref', 'view_ref', 'coordinates', 'sample_space', 'measure_kind', 'purpose', 'mass_or_density', 'dependence', 'provenance', 'justification', 'information_cutoff', 'evidence_cutoff'):
        check(label + ' linked assertion ' + key, linked[key] == lm[key])
    check(label + ' unchanged restrictions', linked['support_restrictions'] == [])
    linked_closure = closure([selected, linked['family_ref'], linked['view_ref'], linked['attachment_ref']] + linked['event_refs'] + ['time:fixture@1','admission:fixture@1'], reg, linked['dependencies'], label + ' linked')
    local_coords = {}
    for record in local.values():
        if record.get('kind') == 'self_contained_finite_joint_model':
            for key, value in record['coordinates'].items():
                check(label + ' local coordinate copies consistent ' + key, key not in local_coords or local_coords[key] == value)
                local_coords[key] = value
    all_records = {**reg, **local, **local_coords}
    external = [x['ref'] for x in owned['external_dependencies']]
    check(label + ' same external availability', set(external) == set(linked['dependencies']))
    check(label + ' complete owned declarations', set(owned['local_dependencies']) == set(local))
    owned_closure = closure([owned['joint_model_ref'],owned['mapping_ref'],owned['attachment_ref']] + owned['event_refs'] + ['time:fixture@1','admission:fixture@1'], all_records, external + owned['local_dependencies'] + list(local_coords), label + ' owned')
    for version in (1, 2):
        mp = local['mapping:stale-owned-to-family@' + str(version)]
        model = local[mp['source_joint_model_ref']]
        semantic = reg[mp['semantic_model_ref']]
        family = reg[mp['family_ref']]
        cm, outcomes = mp['coordinate_map'], mp['outcome_map']
        check(label + ' map source version ' + str(version), model['version'] == semantic['version'] == version)
        check(label + ' map unchanged family/view ' + str(version), mp['family_ref'] == linked['family_ref'] and mp['view_ref'] == linked['view_ref'])
        check(label + ' coordinate bijection ' + str(version), set(cm) == set(model['coordinate_order']) and len(set(cm.values())) == len(cm) and list(cm[x] for x in model['coordinate_order']) == semantic['coordinates'])
        check(label + ' outcome bijection ' + str(version), set(outcomes) == set(model['sample_space']['outcomes']) and len(set(outcomes.values())) == len(outcomes) and set(outcomes.values()) == set(family['sample_space']['outcomes']))
        for coord, target in cm.items():
            check(label + ' coordinate meaning ' + coord, {k:v for k,v in model['coordinates'][coord].items() if k!='id'} == {k:v for k,v in reg[target].items() if k!='id'})
        for outcome, target in outcomes.items():
            translated = {reg[cm[c]]['concept']: value for c,value in model['assignments'][outcome].items()}
            check(label + ' assignments ' + outcome, translated == family['assignments'][target])
        mapped_masses = {outcomes[k]: v for k,v in model['mass_or_density']['masses'].items()}
        check(label + ' mapped law ' + str(version), mapped_masses == semantic['mass_or_density']['masses'])
        for key in ('measure_kind','purpose','dependence','provenance','justification','information_cutoff','evidence_cutoff','evaluator'):
            check(label + ' owned admission ' + str(version) + ' ' + key, model[key] == semantic[key])
        check(label + ' owned support/event algebra ' + str(version), model['support_restrictions'] == linked['support_restrictions'] and model['event_representation'] == linked['event_representation'] and model['sample_space']['measurable_sets'] == semantic['sample_space']['measurable_sets'])
    lat = reg[linked['attachment_ref']]
    lev = reg[linked['event_refs'][0]]
    oat = local[owned['attachment_ref']]
    oev = local[owned['event_refs'][0]]
    old_map = local[oat['mapping_ref']]
    check(label + ' attachment internal consistency', old_map['source_joint_model_ref'] == oat['model_ref'] == oev['model_ref'] and old_map['semantic_model_ref'] == lat['model_ref'] == lev['model_ref'])
    check(label + ' preserved attachment meaning', {**oat, 'model_ref':old_map['semantic_model_ref'], 'id':lat['id']} == {**lat, 'mapping_ref':oat['mapping_ref']})
    check(label + ' old event correspondence', {old_map['outcome_map'][x] for x in oev['selector']} == set(lev['selector']) and owned['event_correspondence'][owned['event_refs'][0]] == linked['event_refs'][0])
    for key in ('version','kind','family_ref','view_ref','selector_kind','projection','provenance'):
        check(label + ' event meaning ' + key, oev[key] == lev[key])
    check(label + ' event coordinates', [old_map['coordinate_map'][k] for k in oev['coordinates']] == lev['coordinates'])
    lmismatch = [name for name, target in [('attachment.model_ref',lat['model_ref']),('event.model_ref',lev['model_ref'])] if selected != target]
    omismatch = [name for name, target in [('attachment.model_ref',oat['model_ref']),('event.model_ref',oev['model_ref'])] if owned['joint_model_ref'] != target]
    if owned['mapping_ref'] != oat['mapping_ref']:
        omismatch.append('attachment.mapping_ref')
    check(label + ' derived linked mismatches', lmismatch == pair['expected_binding_mismatches']['family_linked'])
    check(label + ' derived owned mismatches', omismatch == pair['expected_binding_mismatches']['self_contained'])
    check(label + ' both bindings have same decision', bool(lmismatch) == bool(omismatch))
    stale = bool(lmismatch)
    probabilities = []
    for arm, req, model, ev, expected in [('linked', linked, lm, lev, le), ('owned', owned, om, oev, oe)]:
        masses = {k: Fraction(v) for k,v in model['mass_or_density']['masses'].items()}
        check(label + arm + ' full finite support', set(masses) == set(model['sample_space']['outcomes']) and len(masses)==len(model['sample_space']['outcomes']))
        check(label + arm + ' normalized nonnegative law', all(v>=0 for v in masses.values()) and sum(masses.values())==1)
        check(label + arm + ' selector valid in its old law', set(ev['selector']) <= set(masses))
        probability = None if stale else sum((masses[x] for x in ev['selector']), Fraction())
        probabilities.append(None if probability is None else str(probability))
        expected_status = {'disposition':'RETAINED_ONLY' if stale else 'EVALUATED','structural_validity':'invalid' if stale else 'valid','mathematical_status':'unresolved' if stale else 'satisfied','attachment_status':'attached_assumption','empirical_justification':'not_established','capability_status':'specified_only_no_runtime','computation_status':'not_computed' if stale else 'evaluated','probability':None if stale else str(probability),'reason_codes':['MODEL_VERSION_STALE'] if stale else [],'old_view':'view:tri@1','proposed_view':'view:tri@1','family_effect':'old_view_preserved' if stale else 'unchanged','future_dependencies':['model_migration'],'next_permissible_operations':['revise_request','attach_measure'] if stale else ['evaluate_event'],'observations':{}}
        for key, value in expected_status.items():
            check(label + arm + ' receipt ' + key, expected[key] == value)
        check(label + arm + ' request identity', expected['request_ref'] == req['request_id']+'@1')
        check(label + arm + ' old attachment retained', expected['attachment_ref'] == req['attachment_ref'])
        needed = set(linked['dependencies']) | ({*local} if arm=='owned' else set()) | {req['request_id']+'@1'}
        check(label + arm + ' preservation', set(expected['preserved_records']) == needed)
        check(label + arm + ' separate empirical limitation', all(op not in expected['next_permissible_operations'] for op in d['deferred_operations']))
    check(label + ' independent probabilities agree', probabilities[0] == probabilities[1] == (None if stale else '5/6'))
    corr = pair['receipt_correspondence']
    check(label + ' receipt field coverage', set(le) == set(corr['direct_equal_fields']+corr['encoding_fields']+corr['dependency_fields']) and set(oe)-set(le) == set(corr['owned_only_fields']))
    for key in corr['direct_equal_fields']:
        check(label + ' receipt correspondence ' + key, le[key] == oe[key])
    translation = pair['self_contained']['encoding_to_baseline']
    maps = {'mapping:stale-owned-to-family@1','mapping:stale-owned-to-family@2'}
    for key in corr['dependency_fields']:
        translated = {translation.get(x,x).replace('-owned@','-linked@') for x in oe[key] if x not in maps}
        check(label + ' receipt dependency translation ' + key, translated == set(le[key]))
    check(label + ' owned selected refs', oe['joint_model_ref'] == owned['joint_model_ref'] and oe['mapping_ref'] == owned['mapping_ref'])
    check(label + ' attachment encoding', translation[oe['attachment_ref']] == le['attachment_ref'])
    check(label + ' result encoding', oe['result_id'].replace('-owned','-linked') == le['result_id'])
    check(label + ' unchanged audit support', set(oe['audit_references']) == {'model:tri@1','model:tri@2','event:A@1','attachment:tri@1'})
    observations.append({'pair':label,'linked_binding_mismatches':lmismatch,'owned_binding_mismatches':omismatch,'specified_probabilities':probabilities,'linked_closure':linked_closure,'owned_closure':owned_closure,'old_law_unit_mass':True,'runtime_executed':False})
for arm in ('family_linked','self_contained'):
    control = d['pairs'][0][arm]['input']; stale = d['pairs'][1][arm]['input']
    changed = sorted(k for k in set(control)|set(stale) if control.get(k)!=stale.get(k))
    allowed = ['model_ref','request_id'] if arm=='family_linked' else ['joint_model_ref','mapping_ref','request_id']
    check('control/stale only intended changes '+arm, changed == sorted(allowed))
for path in ['docs/design/proposal/architecture/uncertainty-stale-diagnostic-v1.py','docs/design/proposal/architecture/uncertainty-stale-prior-result-v1.md']:
    digest(path)
failed = [c['id'] for c in checks if not c['passed']]
report = {'schema_version':'accdsl.proposal.stale_verification.v1','passed':not failed,'checks':checks,'failures':failed,'input_hashes':hashes,'observations':observations,'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-stale-diagnostic-v1.py --output '+sys.argv[2], 'environment':{'python':platform.python_version(),'packages':'standard library only','gpu':'N/A: no numerical framework or device APIs','git_commit':'unavailable: project .git marker unusable; file hashes provide provenance','seeds':'N/A: deterministic rational document diagnostic'},'wall_seconds':time.monotonic()-started,'plan':'docs/design/proposal/architecture/uncertainty-stale-comparison-v1.md','result':'data/accounting-master/deliverables/P16/result.md','limits':['Expected receipts are specifications, not product responses.','No architecture selection or general equivalence.','No accounting or empirical validation.','Independent substantive review pending.']}
out = ROOT / sys.argv[2]
with out.open('x') as f:
    json.dump(report,f,indent=2); f.write('\n')
print(json.dumps({'passed':not failed,'checks':len(checks),'failures':failed,'output':str(out.relative_to(ROOT))}))
sys.exit(bool(failed))
