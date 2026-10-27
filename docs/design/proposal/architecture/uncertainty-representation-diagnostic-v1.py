"""One-off document consistency check for RC01; not an AccDSL runtime or test suite."""
import copy
import hashlib
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DIR = ROOT / 'docs/design/proposal/architecture'
FIXTURE = DIR / 'uncertainty-representation-fixtures-v1.json'
checks = []
inputs = {}


def check(name, value):
    checks.append({'id': name, 'passed': bool(value)})


def read(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    inputs[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    return raw


def load(path):
    return json.loads(read(path))


def pointer(obj, path):
    for bit in path.split('/')[1:]:
        bit = bit.replace('~1', '/').replace('~0', '~')
        obj = obj[int(bit)] if isinstance(obj, list) else obj[bit]
    return obj


def pins(value):
    if isinstance(value, dict):
        if {'path', 'sha256'} <= value.keys():
            raw = read(value['path'])
            check('pin ' + value['path'], bool(raw) and hashlib.sha256(raw).hexdigest() == value['sha256'])
        for child in value.values():
            pins(child)
    elif isinstance(value, list):
        for child in value:
            pins(child)


def rid(record):
    return record['id'] + '@' + str(record['version'])


def dependencies(record):
    deps = []
    for field in ['family_ref', 'view_ref', 'time_ref', 'admission_ref', 'justification']:
        if record.get(field):
            deps.append(record[field])
    for field in ['coordinates', 'provenance']:
        deps.extend(record.get(field, []))
    return deps


def law(label, space, masses):
    ids = space['outcomes']
    values = {k: Fraction(v) for k, v in masses.items()}
    check(label + ' unique IDs', len(ids) == len(set(ids)))
    check(label + ' complete mass coverage', set(ids) == set(values))
    check(label + ' nonnegative', all(v >= 0 for v in values.values()))
    check(label + ' unit total', sum(values.values(), Fraction(0)) == 1)
    check(label + ' finite event algebra', space['kind'] == 'finite' and space['measurable_sets'] == 'all_subsets')
    return {'total': str(sum(values.values(), Fraction(0))), 'positive': [s for s in ids if values[s] > 0], 'zero': [s for s in ids if values[s] == 0]}


f = load(FIXTURE)
pins(f)
base = pointer(load(f['baseline']['path']), f['baseline']['json_pointer'])
check('baseline case', base['id'] == 'MA02a')
check('common request is baseline', f['common_semantics']['input'] == base['input'])
check('common expected receipt is baseline', f['common_semantics']['expected'] == base['expected'])
registry = {}
for name, loc in f['external_registry'].items():
    registry[name] = pointer(load(loc['path']), loc['json_pointer'])
    check('record identity ' + name, rid(registry[name]) == name)
for name, record in registry.items():
    for dep in dependencies(record):
        check('available dependency ' + name + ' -> ' + dep, dep in registry)
pair = f['pairs'][0]
fl = pair['family_linked']['input']
sc = pair['self_contained']['input']
j = sc['joint_model']
m = sc['family_mapping']
family = registry[fl['family_ref']]
model = registry[fl['model_ref']]
view = registry[fl['view_ref']]
check('external request closure', set(fl['dependencies']) == set(registry))
check('SC external closure', {d['ref'] for d in sc['external_dependencies']} == set(registry))
check('comparison model only an audit dependency', next(d['roles'] for d in sc['external_dependencies'] if d['ref'] == fl['model_ref']) == ['equivalence_audit'])
check('view resolves family', view['family_ref'] == fl['family_ref'])
check('mapping target binding', all(m[k] == fl[k] for k in ['family_ref', 'view_ref']) and m['semantic_model_ref'] == fl['model_ref'])
check('mapping owns exact source version', m['source_joint_model_ref'] == rid(j))
check('request encoding IDs differ', fl['request_id'] != sc['request_id'])
check('same request operation/version/predecessor', all(sc[k] == fl[k] for k in ['operation', 'version', 'predecessor']))
for k, v in base['input'].items():
    if k != 'request_id':
        check('linked input ' + k, fl[k] == v)
for k in ['family_ref', 'view_ref', 'coordinates', 'sample_space', 'measure_kind', 'purpose', 'mass_or_density', 'dependence', 'provenance', 'justification', 'information_cutoff', 'evidence_cutoff']:
    check('linked model field ' + k, fl[k] == model[k])
check('family coordinate order', family['coordinates'] == fl['coordinates'])
check('family space', family['sample_space'] == fl['sample_space'])
check('family assignments pin', f['common_semantics']['family_assignments'] == family['assignments'])
cm, om = m['coordinate_map'], m['outcome_map']
check('coordinate mapping total', set(cm) == set(j['coordinates']) == set(j['coordinate_order']))
check('coordinate mapping bijective', len(set(cm.values())) == len(cm) and set(cm.values()) == set(family['coordinates']))
check('coordinate order preserved', [cm[c] for c in j['coordinate_order']] == family['coordinates'])
for local, semantic in cm.items():
    check('embedded coordinate local identity ' + local, rid(j['coordinates'][local]) == local)
    a = {k: v for k, v in j['coordinates'][local].items() if k not in ['id', 'version']}
    b = {k: v for k, v in registry[semantic].items() if k not in ['id', 'version']}
    check('all coordinate meaning fields ' + local, a == b)
check('outcome mapping total', set(om) == set(j['sample_space']['outcomes']))
check('outcome mapping bijective', len(set(om.values())) == len(om) and set(om.values()) == set(family['sample_space']['outcomes']))
check('owned assignments complete', set(j['assignments']) == set(om))
for local, semantic in om.items():
    check('assignment coordinate coverage ' + local, set(j['assignments'][local]) == set(cm))
    mapped = {j['coordinates'][c]['concept']: v for c, v in j['assignments'][local].items()}
    check('assignment preservation ' + local, mapped == family['assignments'][semantic])
for k in ['measure_kind', 'purpose', 'dependence', 'provenance', 'justification', 'information_cutoff', 'evidence_cutoff', 'support_restrictions', 'event_representation']:
    check('owned model field ' + k, j[k] == fl[k])
check('evaluator designation', j['evaluator'] == model['evaluator'])
check('event algebra preserved', j['sample_space']['measurable_sets'] == fl['sample_space']['measurable_sets'])
check('all mapped masses equal', {om[o]: Fraction(v) for o, v in j['mass_or_density']['masses'].items()} == {o: Fraction(v) for o, v in fl['mass_or_density']['masses'].items()})
obs = {'family_linked': law('linked', fl['sample_space'], fl['mass_or_density']['masses']), 'self_contained': law('owned', j['sample_space'], j['mass_or_density']['masses'])}
for variant in ['family_linked', 'self_contained']:
    e = pair[variant]['expected']
    for k in pair['receipt_correspondence']['direct_equal_fields']:
        check(variant + ' receipt ' + k, e[k] == base['expected'][k])
    for k, v in {'disposition':'ATTACHED_ASSUMPTION', 'structural_validity':'valid', 'attachment_status':'attached_assumption', 'mathematical_status':'satisfied', 'empirical_justification':'not_established', 'capability_status':'specified_only_no_runtime', 'computation_status':'validated_attachment', 'probability':None, 'family_effect':'measure_record_appended_family_unchanged'}.items():
        check(variant + ' independent status boundary ' + k, e[k] == v)
    check(variant + ' expected total is calculated', e['observations']['probability_total'] == obs[variant]['total'])
    check(variant + ' expected positive support is calculated', e['observations']['positive_mass_support'] == obs[variant]['positive'])
    check(variant + ' expected zero support is calculated', e['observations']['zero_mass_outcomes'] == obs[variant]['zero'])
    check(variant + ' future operations separate', e['future_dependencies'] == ['conditioning', 'likelihood_update', 'conditional_outcomes'] and e['next_permissible_operations'] == ['evaluate_event'])
    translated = pair[variant]['encoding_to_baseline']
    for k in ['request_ref', 'attachment_ref']:
        check(variant + ' receipt identity map ' + k, translated[e[k]] == base['expected'][k])
    check(variant + ' result identity map', translated[e['result_id'] + '@' + str(e['version'])] == base['expected']['result_id'] + '@1')
    local_ids = {rid(j), rid(m)} if variant == 'self_contained' else set()
    available = set(registry) | local_ids | {e['request_ref']}
    check(variant + ' receipt support resolves', set(e['support_references']) <= available)
    check(variant + ' exact preservation closure', set(e['preserved_records']) == available)
check('linked support unchanged', pair['family_linked']['expected']['support_references'] == base['expected']['support_references'])
check('SC structural support explicit', set(pair['self_contained']['expected']['support_references']) == (set(registry) - {fl['model_ref']} | {rid(j), rid(m)}))
check('synthetic admission preserved', registry['admission:fixture@1']['disposition'] == 'selected_synthetic_assumption' and registry['admission:fixture@1']['empirical_justification'] == 'not_established')
check('time cutoffs match', all(registry['time:fixture@1'][k] == fl[k] for k in ['information_cutoff', 'evidence_cutoff']))
prior = load(DIR / 'uncertainty-measure-failures-consistency-v1.json')
for path, sha in prior['input_hashes'].items():
    check('prior supplement input unchanged ' + path, hashlib.sha256(read(path)).hexdigest() == sha)
check('prior saved report really has 266 passes', prior['total'] == 266 and len(prior['checks']) == 266 and all(c['passed'] for c in prior['checks']))
read(__file__)
failed = [c['id'] for c in checks if not c['passed']]
report = {'schema_version':'accdsl.proposal.representation_verification.v1', 'passed':not failed, 'total':len(checks), 'checks':checks, 'failures':failed, 'observations':obs, 'input_hashes':inputs, 'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-representation-diagnostic-v1.py ' + sys.argv[1], 'environment':{'python':platform.python_version(), 'packages':'standard library only', 'gpu':'not used; no numerical framework imported'}, 'scope':'Author consistency check of definitions and one synthetic MA02a pair; no proposed runtime executed.', 'limitations':['No architecture selection or general equivalence', 'Overlap, projection and rejection comparisons deferred', 'No accounting, empirical, performance, recovery or human acceptance']}
with (ROOT / sys.argv[1]).open('x') as handle:
    json.dump(report, handle, indent=2)
    handle.write('\n')
print(json.dumps({'passed':not failed, 'checks':len(checks), 'failures':failed, 'observations':obs, 'output':sys.argv[1]}))
sys.exit(bool(failed))
