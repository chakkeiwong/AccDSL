"""Finite hazard correspondence; recording is one-time and replay read-only."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import platform
import subprocess
import time
from model import *
sys.path.insert(0, str(OUT))
from prepare import construct_packet, FACT_IDS, CONTEXT_IDS, VALUE_REASON, INVENTORY

def validate(packet, records, adjunct, material):
    checks = []
    def check(label, condition):
        require(condition, label); checks.append(label)
    check('EXACT_CLOSED_PACKET', packet == construct_packet())
    declared = profile()
    check('RECORD_COUNT', len(records) == 39)
    by_key, by_ref = {}, {}
    for record in records:
        key, kind = record['key'], record['kind']
        check('ENVELOPE:' + key, set(record) == set(declared['envelope_fields']))
        check('KEY:' + key, key not in by_key)
        check('SCHEMA:' + key, record['schema'] == declared['records'][kind]['schema'])
        check('REVISION:' + key, type(record['revision']) is int and record['revision'] == 0)
        typed(record['body'], declared['records'][kind]['body_type'], declared)
        check('TYPED:' + key, True)
        check('DEPENDENCIES:' + key, record['dependencies'] == ref_set(refs(record['body'])))
        by_key[key], by_ref[canonical(record_ref(record))] = record, record
    def body(key): return by_key[key]['body']
    def ref(key): return record_ref(by_key[key])
    for record in records:
        for dependency in record['dependencies']:
            check('CLOSED:' + record['key'] + ':' + dependency['digest'][:8], canonical(dependency) in by_ref)
    raw, root, xml_ids, ns, locate = material
    check('SOURCE_BLOB', body('source')['original_bytes_ref'] == blob(ROOT / packet['source']['path']))
    check('PACKET_BLOB', body('import')['original_bytes_ref'] == blob(PACKET) and body('import')['original_bytes_ref'] != body('source')['original_bytes_ref'])
    owners = {'source': ''}
    for i, entry in enumerate(packet['contexts']):
        key, owner = entry['id'], '/contexts/' + str(i)
        owners['occ-' + key] = owners['source-' + key] = owner
        check('CONTEXT_LOCATOR:' + key, body('occ-' + key)['locator'] == locator(entry))
        evidence = body('source-' + key)
        check('CONTEXT_REFERENCE:' + key, evidence['occurrence_ref'] == ref('occ-' + key))
        check('PERIOD:' + key, evidence['period'] == period(entry))
        check('DIMENSIONS:' + key, evidence['dimensions'] == dimensions(entry, packet))
        for j, dimension in enumerate(evidence['dimensions']):
            span = dimension['source_span']
            chunk = raw[span['byte_start']:span['byte_end']]
            check('DIMENSION_CONTAINMENT:' + key, entry['span']['byte_start'] <= span['byte_start'] < span['byte_end'] <= entry['span']['byte_end'])
            if dimension['form'] == 'typed':
                check('TYPED_NOT_QNAME:' + key, dimension['member_token'] is None and dimension['member_qname']['tag'] == 'Unknown')
                wrapper = '<root ' + ' '.join(('xmlns' + (':' + n['prefix'] if n['prefix'] else '') + '="' + n['namespace_uri'] + '"') for n in packet['namespace_bindings']) + '>'
                import xml.etree.ElementTree as ET
                parsed = ET.fromstring(wrapper.encode() + chunk + b'</root>')[0]
                check('TYPED_SUBTREE:' + key, reader_module().tree_reading(parsed) == entry['dimensions_and_qualifiers'][j]['reading'])
    for i, entry in enumerate(packet['facts']):
        key, owner = entry['id'], '/facts/' + str(i)
        for prefix in ['occ-', 'ctx-', 'fact-']: owners[prefix + key] = owner
        assertion, context = body('fact-' + key), body('ctx-' + key)
        element = xml_ids[key]
        check('TOKEN:' + key, assertion['reported_text'] == element.text)
        check('UNKNOWN_VALUE:' + key, assertion['value'] == unknown(VALUE_REASON))
        check('SOURCE_JOINS:' + key, context['source_context_ref'] == ref('source-' + element.get('contextRef')) and context['source_unit_ref']['tag'] == 'Unknown')
        check('FACT_JOINS:' + key, assertion['occurrence_refs'] == [ref('occ-' + key)] and assertion['context_ref'] == ref('ctx-' + key))
        check('FACT_SPAN:' + key, body('occ-' + key)['locator'] == locator(entry))
        check('FINANCIAL_UNKNOWNS:' + key, all(context[k]['tag'] == 'Unknown' for k in ['legal_entity', 'book', 'perimeter', 'basis', 'currency_or_unit', 'time', 'calendar', 'dimensions']))
        check('ATTRIBUTES:' + key, assertion['source_attributes'] == [{'name': k, 'value': v} for k,v in sorted(element.attrib.items())])
    owners['occ-link-1'] = '/source_links/0'
    link = body('occ-link-1')
    check('SOURCE_LINK_NULL_ID', link['locator']['element_id'] is None)
    check('SOURCE_LINK_LOCATOR', link['locator'] == locator(packet['source_links'][0]) and link['source_ref'] == ref('source'))
    check('SOURCE_LINK_ADJUNCT', adjunct == link_adjunct(packet, records))
    check('SOURCE_LINK_FIELDS', set(adjunct) == {'schema', 'status', 'occurrence_ref', 'expanded_name', 'source_attributes', 'resolution_status'})
    check('SOURCE_LINK_TYPING', adjunct['resolution_status'] == 'not_run' and adjunct['status'] == 'proposed')
    mapping = body('mapping')
    check('OUTPUT_MEMBERSHIP', mapping['outputs'] == ref_set([ref(k) for k in owners]))
    coverage = set()
    for item in mapping['field_mappings']:
        target = by_ref[canonical(item['target_ref'])]
        key, path = target['key'], item['target_path']
        check('FIELD:' + key + ':' + path, key in owners and path.startswith('/body/') and path.count('/') == 2 and path[6:] in target['body'])
        check('UNIQUE_MAPPING:' + key + ':' + path, (key, path) not in coverage)
        coverage.add((key, path)); owner = owners[key]
        check('OWNER:' + key + ':' + path, item['source_path'] == owner or item['source_path'].startswith(owner + '/'))
        original = pointer(packet, item['source_path'])
        if item['relation'] == 'equal_decoded_value':
            check('EQUAL:' + key + ':' + path, original == pointer(target, path))
        else:
            check('CONVERSION:' + key + ':' + path, item['source_path'] == owner and item['conversion_method_ref'] == ref('method-general'))
    check('COMPLETE_MAPPINGS', coverage == {(k, '/body/' + field) for k in owners for field in body(k)})
    for expected in construct(packet):
        check('SPECIFICATION_RECORD:' + expected['key'], by_key[expected['key']] == expected)
    return checks

def mutate(records, key, edit):
    changed, replacements = [], {}
    def replace(value):
        if isinstance(value, dict):
            if set(value) == {'kind', 'schema', 'digest'}: return replacements.get(canonical(value), value)
            return {k: replace(v) for k,v in value.items()}
        return [replace(v) for v in value] if isinstance(value, list) else value
    for original in records:
        row = deepcopy(original)
        if row['key'] == key: edit(row)
        row['body'] = replace(row['body'])
        if row['key'] == 'mapping': row['body']['outputs'] = ref_set(row['body']['outputs'])
        if row['key'] == 'comparison':
            mapping = next(r['body'] for r in changed if r['key'] == 'mapping')
            row['body']['output_digests'] = sorted(r['digest'] for r in mapping['outputs'])
            row['body']['field_mapping_count'] = len(mapping['field_mappings'])
        row['dependencies'] = ref_set(refs(row['body']))
        replacements[canonical(record_ref(original))] = record_ref(row)
        changed.append(row)
    return changed

def negatives(packet, records, adjunct, material):
    cases = []
    tests = [
        ('digits-promoted-to-number', 'fact-f-59', lambda r: r['body'].__setitem__('value', {'tag': 'Decimal', 'rational': {'n': '320193', 'd': '1'}}), 'UNKNOWN_VALUE:f-59'),
        ('leading-zeros-lost', 'fact-f-59', lambda r: r['body'].__setitem__('reported_text', '320193'), 'TOKEN:f-59'),
        ('invented-source-id', 'occ-link-1', lambda r: r['body']['locator'].__setitem__('element_id', 'schema-1'), 'SOURCE_LINK_NULL_ID'),
        ('typed-domain-as-member-qname', 'source-c-58', lambda r: r['body']['dimensions'][0].__setitem__('member_qname', {'namespace_uri': 'urn:invented', 'local_name': '2024'}), 'DIMENSIONS:c-58'),
        ('typed-domain-flattened', 'source-c-58', lambda r: r['body']['dimensions'][0].__setitem__('member_token', '2024-09-29'), 'DIMENSIONS:c-58'),
        ('typed-domain-span-shift', 'source-c-59', lambda r: r['body']['dimensions'][0]['source_span'].__setitem__('byte_start', r['body']['dimensions'][0]['source_span']['byte_start'] + 1), 'DIMENSIONS:c-59'),
        ('financial-time-inferred', 'ctx-f-934', lambda r: r['body'].__setitem__('time', {'tag': 'Instant', 'date': '2024-09-28'}), 'FINANCIAL_UNKNOWNS:f-934'),
        ('field-provenance-omitted', 'mapping', lambda r: r['body']['field_mappings'].pop(), 'COMPLETE_MAPPINGS'),
        ('packet-as-source', 'source', lambda r: r['body'].__setitem__('original_bytes_ref', blob(PACKET)), 'SOURCE_BLOB')]
    for name, key, edit, expected in tests:
        changed = mutate(records, key, edit)
        try: validate(packet, changed, link_adjunct(packet, changed), material)
        except ValueError as error:
            require(str(error) == expected, 'WRONG_NEGATIVE:' + name + ':' + str(error))
            cases.append({'case': name, 'rejected': str(error), 'dependent_refs_rebuilt': True})
        else: raise ValueError('ACCEPTED:' + name)
    for name, field, value in [('source-link-marked-resolved', 'resolution_status', 'resolved'), ('link-attributes-lost', 'source_attributes', [])]:
        altered = deepcopy(adjunct); altered[field] = value
        try: validate(packet, records, altered, material)
        except ValueError as error:
            require(str(error) == 'SOURCE_LINK_ADJUNCT', 'WRONG_ADJUNCT_NEGATIVE')
            cases.append({'case': name, 'rejected': str(error)})
        else: raise ValueError('ACCEPTED:' + name)
    altered = deepcopy(packet)
    next(c for c in altered['contexts'] if c['id'] == 'c-58')['dimensions_and_qualifiers'][0]['reading']['children'] = []
    try: validate(altered, records, adjunct, material)
    except ValueError as error:
        require(str(error) == 'EXACT_CLOSED_PACKET', 'WRONG_PACKET_NEGATIVE')
        cases.append({'case': 'typed-subtree-lost', 'rejected': str(error)})
    else: raise ValueError('ACCEPTED:typed-subtree-lost')
    return cases

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--record', action='store_true'); mode.add_argument('--check-only', action='store_true')
    args = parser.parse_args(); tick = time.monotonic()
    packet = read(PACKET)
    material = reader_module().source_material()
    records = construct(packet) if args.record or args.check_only else read(OUT / 'portable-records.json')
    adjunct = link_adjunct(packet, records) if args.record or args.check_only else read(OUT / 'source-link-adjunct.json')
    checks = validate(packet, records, adjunct, material)
    corruptions = negatives(packet, records, adjunct, material)
    counts = {'facts': 7, 'contexts': 6, 'typed_dimensions': 4, 'source_links': 1, 'records': len(records),
        'mappings': len(next(r for r in records if r['key'] == 'mapping')['body']['field_mappings']),
        'checks': len(checks), 'rejected_corruptions': len(corruptions)}
    findings = {'counts': counts, 'checks': checks, 'negative_cases': corruptions, 'upstream_executed': False, 'profile_registered': False}
    if args.record:
        for name in ['portable-records.json', 'source-link-adjunct.json', 'checks.json', 'run-manifest.json']:
            require(not (OUT / name).exists(), 'ALREADY_RECORDED:' + name)
        write_once(OUT / 'portable-records.json', records)
        write_once(OUT / 'source-link-adjunct.json', adjunct)
        write_once(OUT / 'checks.json', findings)
        predecessor = ROOT / 'data/accounting-master/native-shape-inventory-20261018'
        inherited = json.loads((predecessor / 'run-manifest.json').read_bytes())['protected_inputs']
        protected = inherited + [binding(p) for p in [PLAN, SPEC, INVENTORY, predecessor / 'checks.json', predecessor / 'completion.json', predecessor / 'run-manifest.json']]
        manifest = {'recorded_utc': datetime.now(timezone.utc).isoformat(),
            'command': 'python3 data/accounting-master/native-hazard-portable-20261018/check.py --record',
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'environment': {'executable': sys.executable, 'python': platform.python_version(), 'conda_env': 'tfgpu', 'cpu_gpu': 'CPU standard-library source checks only; no numerical framework/GPU'},
            'data_version': binding(INVENTORY), 'random_seeds': 'N/A: deterministic', 'wall_seconds': time.monotonic() - tick,
            'plan_file': str(PLAN.relative_to(ROOT)), 'result_file': str((OUT / 'result.md').relative_to(ROOT)),
            'protected_inputs': protected, 'artifacts': [binding(OUT / n) for n in ['model.py', 'prepare.py', 'check.py', 'native-packet.json', 'portable-records.json', 'source-link-adjunct.json', 'checks.json']]}
        write_once(OUT / 'run-manifest.json', manifest)
    elif not args.check_only:
        require(findings == read(OUT / 'checks.json'), 'REPLAY_CHECKS_CHANGED')
        manifest = json.loads((OUT / 'run-manifest.json').read_bytes())
        for row in manifest['protected_inputs'] + manifest['artifacts']:
            require(binding(ROOT / row['path']) == row, 'PROTECTED:' + row['path'])
    print(json.dumps({'mode': 'check_only' if args.check_only else 'record' if args.record else 'read_only_replay', **counts, 'status': 'pass'}))

if __name__ == '__main__': main()
