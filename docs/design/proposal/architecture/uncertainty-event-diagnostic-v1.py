"""One-off authored-fixture diagnostic; not an AccDSL runtime or test suite."""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
checks, inputs, observations = [], {}, {}

def check(label, ok):
    checks.append({'id': label, 'passed': bool(ok)})

def read(path):
    p = ROOT / path
    data = p.read_bytes()
    inputs[str(p.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return json.loads(data)

def pointer(data, value):
    for key in value.strip('/').split('/') if value else []:
        key = key.replace('~1', '/').replace('~0', '~')
        data = data[int(key)] if isinstance(data, list) else data[key]
    return data

def pins(value):
    if isinstance(value, dict):
        if 'path' in value and 'sha256' in value:
            p = ROOT / value['path']
            digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
            check('pin '+value['path'], digest == value['sha256'])
            if digest:
                inputs[value['path']] = digest
                if 'json_pointer' in value:
                    check('locator '+value['json_pointer'], pointer(json.loads(p.read_bytes()), value['json_pointer']) is not None)
        for item in value.values():
            pins(item)
    elif isinstance(value, list):
        for item in value:
            pins(item)

def rid(record):
    return record['id']+'@'+str(record['version'])

def translate(value, mapping):
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return [translate(x, mapping) for x in value]
    if isinstance(value, dict):
        return {mapping.get(k,k):translate(v,mapping) for k,v in value.items()}
    return value

fixture = read('docs/design/proposal/architecture/uncertainty-event-fixtures-v1.json')
pins(fixture)
registry = {ref:pointer(read(loc['path']),loc['json_pointer']) for ref,loc in fixture['external_registry'].items()}
for ref,record in registry.items():
    check('available identity '+ref, rid(record)==ref)
# Retained prerequisite results are checked for freshness, not rerun.
for name in ['uncertainty-representation-verification-v1.json','uncertainty-measure-failures-consistency-v1.json']:
    prior = read(str((HERE/name).relative_to(ROOT)))
    for path,digest in prior['input_hashes'].items():
        check('retained input '+path, hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)

for pair in fixture['pairs']:
    label=pair['id']; b=pointer(read(pair['baseline']['path']),pair['baseline']['json_pointer'])
    bi,be=b['input'],b['expected']; linked=pair['family_linked']; owned=pair['self_contained']
    li,le=linked['input'],linked['expected']; oi,oe=owned['input'],owned['expected']
    model=oi['joint_model']; mapping=oi['family_mapping']; om=mapping['outcome_map']; cm=mapping['coordinate_map']; em=mapping['event_map']
    family=registry[bi['family_ref']]; law=registry[bi['model_ref']]
    check(label+' linked inputs fixed', {k:v for k,v in li.items() if k!='request_id'}=={k:v for k,v in bi.items() if k!='request_id'})
    check(label+' dependency closure', set(li['dependencies'])==set(x['ref'] for x in oi['external_dependencies']) and set(li['dependencies'])<=set(registry))
    check(label+' mapping target', all(mapping[k]==bi[k] for k in ['family_ref','view_ref']) and mapping['semantic_model_ref']==bi['model_ref'] and mapping['source_joint_model_ref']==rid(model))
    check(label+' view binding',registry[bi['view_ref']]['family_ref']==bi['family_ref'])
    check(label+' model binding',all(law[k]==bi[k] for k in ['family_ref','view_ref','coordinates','sample_space','mass_or_density']))
    check(label+' coordinate bijection',set(cm)==set(model['coordinate_order']) and len(set(cm.values()))==len(cm) and list(cm.values())==bi['coordinates'])
    for local,semantic in cm.items():
        definition=model['coordinates'][local]
        check(label+' coordinate '+local, rid(definition)==local and {k:v for k,v in definition.items() if k!='id'}=={k:v for k,v in registry[semantic].items() if k!='id'})
    check(label+' outcome bijection',set(om)==set(model['sample_space']['outcomes']) and len(set(om.values()))==len(om) and set(om.values())==set(family['sample_space']['outcomes']))
    check(label+' full assignment coverage',set(model['assignments'])==set(om))
    for local,semantic in om.items():
        check(label+' assignment '+local, {registry[cm[k]]['concept']:v for k,v in model['assignments'][local].items()}==family['assignments'][semantic])
    for k in ['measure_kind','purpose','dependence','provenance','justification','information_cutoff','evidence_cutoff','support_restrictions','event_representation']:
        check(label+' common '+k,model[k]==bi[k])
    check(label+' evaluator',model['evaluator']==law['evaluator'])
    check(label+' mass mapping',translate(model['mass_or_density'],om)==li['mass_or_density'])
    check(label+' event coverage',set(em)==set(oi['events'])==set(oi['event_refs']) and set(em.values())==set(li['event_refs']) and len(em)==len(set(em.values())))
    for local,semantic in em.items():
        event=oi['events'][local]; target=registry[semantic]
        check(label+' event ownership '+local, rid(event)==local and event['model_ref']==rid(model) and event['family_ref']==bi['family_ref'] and event['view_ref']==bi['view_ref'])
        check(label+' event selector '+local,translate(event['selector'],om)==target['selector'])
        check(label+' event metadata '+local,translate(event['coordinates'],cm)==target['coordinates'] and event['selector_kind']==target['selector_kind'] and event['provenance']==target['provenance'])
    att=oi['attachment']; original=registry[bi['attachment_ref']]
    check(label+' owned attachment binding',oi['attachment_ref']==rid(att)==oe['attachment_ref'] and att['mapping_ref']==rid(mapping) and att['model_ref']==rid(model))
    for k in ['family_ref','view_ref','purpose','status','provenance','justification','empirical_justification']:
        check(label+' attachment '+k,att[k]==original[k])
    outcomes={}
    for arm in ['family_linked','self_contained']:
        is_owned=arm=='self_contained'; request=pair[arm]['input']; receipt=pair[arm]['expected']
        current=model if is_owned else request
        masses={k:Fraction(v) for k,v in current['mass_or_density']['masses'].items()}
        space=current['sample_space']['outcomes']
        check(label+' '+arm+' finite law',len(space)==len(set(space)) and set(masses)==set(space) and all(v>=0 for v in masses.values()) and sum(masses.values())==1 and current['sample_space']['measurable_sets']=='all_subsets')
        events=[oi['events'][x] for x in oi['event_refs']] if is_owned else [registry[x] for x in li['event_refs']]
        check(label+' '+arm+' selectors inside space',all(set(ev['selector'])<=set(space) for ev in events))
        if request['query']=='overlap':
            a,c=[set(ev['selector']) for ev in events]
            sets=[a,c,a&c,a|c]; names=['event_a_probability','event_b_probability','intersection_probability','union_probability']
            result={k:str(sum((masses[s] for s in selected),Fraction())) for k,selected in zip(names,sets)}
            check(label+' '+arm+' overlap retained',bool(a&c) and a|c==set(space))
            detail={'intersection':sorted(a&c),'union':sorted(a|c),'naive_probability_sum':str(sum(masses[s] for s in a)+sum(masses[s] for s in c))}
        else:
            event=events[0]; projection=event['projection']; values={}; preimages={}
            for outcome in space:
                assignment=model['assignments'][outcome] if is_owned else family['assignments'][outcome]
                rate_key=next(k for k,v in cm.items() if registry[v]['concept']=='rate') if is_owned else 'rate'
                value=assignment[rate_key]; preimages.setdefault(value,[]).append(outcome)
                check(label+' '+arm+' projection value '+outcome,projection['mapping'][outcome]=={rate_key:value})
                values['rate='+value]=values.get('rate='+value,Fraction())+masses[outcome]
            expected_coords=list(cm) if is_owned else bi['coordinates']
            check(label+' '+arm+' projection coordinates',projection['source_coordinates']==expected_coords and projection['target_coordinates']==[expected_coords[1]] and projection['lost_coordinates']==[expected_coords[0]])
            check(label+' '+arm+' complete preimage',set(projection['mapping'])==set(space)==set(event['selector']) and len(preimages['1'])==2)
            result={'projected_probabilities':{k:str(v) for k,v in values.items()},'elementary_outcomes_preserved':space}
            detail={'preimages':preimages,'lost_coordinates':projection['lost_coordinates']}
        check(label+' '+arm+' independently calculated observations',result==receipt['observations'])
        outcomes[arm]={'calculated':result,**detail}
        enc=pair[arm]['encoding_to_baseline']
        for k in pair['receipt_correspondence']['direct_equal_fields']:
            check(label+' '+arm+' receipt '+k,receipt[k]==be[k])
        check(label+' '+arm+' request identity',receipt['request_ref']==request['request_id']+'@1' and enc[receipt['request_ref']]==be['request_ref'])
        check(label+' '+arm+' result identity',enc[receipt['result_id']+'@1']==be['result_id']+'@1')
        check(label+' '+arm+' attachment identity',enc.get(receipt['attachment_ref'],receipt['attachment_ref'])==be['attachment_ref'])
        for field in ['support_references','preserved_records']:
            mapped={enc.get(x,x) for x in receipt[field] if x!=rid(mapping)}
            check(label+' '+arm+' '+field,mapped==set(be[field]))
        extras={'joint_model_ref','mapping_ref','audit_references'} if is_owned else set()
        check(label+' '+arm+' receipt field coverage',set(receipt)==set(be)|extras)
    check(label+' cross representation results',translate(outcomes['self_contained']['calculated'],om)==outcomes['family_linked']['calculated'])
    check(label+' audit support roles',set(oe['audit_references'])=={x['ref'] for x in oi['external_dependencies'] if x['roles']==['equivalence_audit']})
    check(label+' owned extra receipt refs',oe['joint_model_ref']==rid(model) and oe['mapping_ref']==rid(mapping))
    observations[label]=outcomes

self_path=Path(__file__).resolve(); inputs[str(self_path.relative_to(ROOT))]=hashlib.sha256(self_path.read_bytes()).hexdigest()
failures=[c['id'] for c in checks if not c['passed']]
report={'schema_version':'accdsl.proposal.event_verification.v1','passed':not failures,'total':len(checks),'checks':checks,'failures':failures,'observations':observations,'input_hashes':inputs,'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/uncertainty-event-diagnostic-v1.py '+sys.argv[1],'environment':'Python standard library; exact fractions; no scientific-framework imports or GPU use','scope':'Authored-fixture arithmetic and correspondence only; expected receipts are not runtime execution. Prior input hashes checked, prior diagnostics not rerun.','limitations':fixture['nonclaims']}
with (ROOT/sys.argv[1]).open('x') as handle:
    json.dump(report,handle,indent=2);handle.write('\n')
print(json.dumps({'passed':report['passed'],'total':len(checks),'failures':failures,'observations':observations}))
sys.exit(bool(failures))
