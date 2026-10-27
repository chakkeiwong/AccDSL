"""Bounded portable/source checks; --record once, otherwise read-only replay."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import json
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from model import *

def validate(packet, records, material):
    checks = []
    def check(label, condition):
        require(condition, label)
        checks.append(label)
    declared = profile()
    raw, root, xml_by_id, ns, locate = material
    by_key, by_ref = {}, {}
    check('RECORD_COUNT', len(records) == 54)
    for record in records:
        key, kind = record['key'], record['kind']
        check('ENVELOPE:' + key, set(record) == set(declared['envelope_fields']))
        check('UNIQUE_KEY:' + key, key not in by_key)
        check('SCHEMA:' + key, kind in declared['records'] and record['schema'] == declared['records'][kind]['schema'])
        check('REVISION:' + key, type(record['revision']) is int and record['revision'] == 0)
        typed(record['body'], declared['records'][kind]['body_type'], declared)
        check('TYPED:' + key, True)
        check('DEPENDENCIES:' + key, record['dependencies'] == ref_set(refs(record['body'])))
        by_key[key] = record
        by_ref[canonical(record_ref(record))] = record
    check('UNIQUE_REFS', len(by_ref) == len(records))
    for record in records:
        for ref in record['dependencies']:
            check('REF_CLOSED:' + record['key'] + ':' + ref['digest'][:8], canonical(ref) in by_ref)
    def body(key):
        return by_key[key]['body']
    def ref(key):
        return record_ref(by_key[key])
    source = body('source')
    check('SOURCE_BLOB', source['original_bytes_ref'] == blob(ROOT / packet['source']['path']))
    check('SOURCE_NAMESPACES', source['namespace_bindings'] == packet['namespace_bindings'])
    check('SOURCE_IDENTITY', source['document_identity'] == packet['source']['path'] and source['origin'] == 'retained-file:' + packet['source']['path'])
    check('SOURCE_UNKNOWNS', all(source[k]['tag'] == 'Unknown' for k in ['acquisition', 'issuer', 'publication_evidence', 'vintage_evidence']))
    owner_by_key = {'source': ''}
    for group in ['contexts', 'units', 'facts']:
        for i, entry in enumerate(packet[group]):
            key, owner = entry['id'], '/' + group + '/' + str(i)
            occurrence = body('occ-' + key)
            owner_by_key['occ-' + key] = owner
            check('OCC_SOURCE:' + key, occurrence['source_ref'] == ref('source'))
            check('OCC_LOCATOR:' + key, occurrence['locator'] == locator(entry))
            loc = occurrence['locator']
            check('EXACT_SLICE:' + key, sha(raw[loc['byte_start']:loc['byte_end']]) == entry['span']['slice_sha256'])
            check('OCC_METADATA:' + key, occurrence['package_root_key'] == packet['source']['path'] and occurrence['parent_key'] == 'xml-root' and occurrence['disposition'] == 'retained')
            if group != 'facts':
                owner_by_key['source-' + key] = owner
                evidence = body('source-' + key)
                check('EVIDENCE_ID:' + key, evidence['xml_id'] == key and evidence['occurrence_ref'] == ref('occ-' + key))
                if group == 'contexts':
                    element = xml_by_id[key]
                    identifier = element.find('{http://www.xbrl.org/2003/instance}entity/{http://www.xbrl.org/2003/instance}identifier')
                    check('IDENTIFIER:' + key, evidence['identifier'] == {'scheme': identifier.get('scheme'), 'text': identifier.text})
                    check('SOURCE_PERIOD:' + key, evidence['period'] == period(entry))
                    check('DIMENSIONS:' + key, evidence['dimensions'] == dimensions(entry, packet) and evidence['non_dimension_spans'] == [])
                    for dim in evidence['dimensions']:
                        span = dim['source_span']
                        check('DIMENSION_NESTED:' + key, loc['byte_start'] <= span['byte_start'] < span['byte_end'] <= loc['byte_end'])
                        chunk = raw[span['byte_start']:span['byte_end']].decode()
                        check('DIMENSION_TOKENS:' + key, dim['axis_token'] in chunk and dim['member_token'] in chunk and dim['container'] == 'segment')
                else:
                    for side in ['numerator', 'denominator']:
                        check('UNIT_' + side.upper() + ':' + key, evidence[side] == [{'token': m['token'], 'qname': qname(m['expanded_name'])} for m in entry[side]])
                continue
            owner_by_key['ctx-' + key] = owner
            owner_by_key['fact-' + key] = owner
            context, fact, element = body('ctx-' + key), body('fact-' + key), xml_by_id[key]
            check('CONTEXT_JOIN:' + key, context['source_context_ref'] == ref('source-' + element.get('contextRef')))
            expected_unit = ref('source-' + element.get('unitRef')) if element.get('unitRef') else unknown('No unitRef; applicability/type not established')
            check('UNIT_JOIN:' + key, context['source_unit_ref'] == expected_unit)
            for name, value in entry['financial_context'].items():
                target = 'time' if name == 'financial_time' else name
                check('FINANCIAL_UNKNOWN:' + key + ':' + target, context[target] == unknown(value['reason']))
            check('FACT_JOINS:' + key, fact['occurrence_refs'] == [ref('occ-' + key)] and fact['context_ref'] == ref('ctx-' + key))
            check('CANDIDATE_ONLY:' + key, context['interpretation_status'] == fact['interpretation_status'] == 'candidate')
            check('CONCEPT:' + key, fact['concept'] == qname(element.tag))
            check('CHARACTERS:' + key, fact['reported_text'] == (element.text or ''))
            check('ATTRIBUTES:' + key, fact['source_attributes'] == [{'name': n, 'value': v} for n, v in sorted(element.attrib.items())])
            for target, name in [('context_id_token', 'contextRef'), ('unit_id_token', 'unitRef'), ('decimals', 'decimals'), ('precision', 'precision'), ('explicit_language', '{http://www.w3.org/XML/1998/namespace}lang')]:
                check('RAW_FIELD:' + key + ':' + target, fact[target] == raw_field(element.attrib, name))
            check('LANGUAGE_UNKNOWN:' + key, fact['effective_language']['tag'] == 'Unknown')
            candidate = entry['candidate_value']
            if candidate['tag'] == 'Decimal':
                number = Fraction(element.text)
                expected = {'tag': 'Decimal', 'rational': {'n': str(number.numerator), 'd': str(number.denominator)}}
            elif candidate['tag'] == 'Nil':
                expected = {'tag': 'Nil'}
            else:
                expected = {'tag': 'Text', 'text': element.text}
            check('EXACT_VALUE:' + key, fact['value'] == expected)
    check('REPEATS_DISTINCT', body('fact-f-207')['value'] == body('fact-f-256')['value'] and ref('fact-f-207') != ref('fact-f-256') and body('occ-f-207')['locator'] != body('occ-f-256')['locator'])
    mapping = body('mapping')
    check('OUTPUT_MEMBERSHIP', mapping['outputs'] == ref_set([ref(key) for key in owner_by_key]))
    coverage = {}
    for item in mapping['field_mappings']:
        target = by_ref[canonical(item['target_ref'])]
        key, path = target['key'], item['target_path']
        check('MAPPING_TARGET:' + key + ':' + path, key in owner_by_key and path.startswith('/body/') and path.count('/') == 2 and path[6:] in target['body'])
        pair = (key, path)
        check('MAPPING_UNIQUE:' + key + ':' + path, pair not in coverage)
        coverage[pair] = item
        owner = owner_by_key[key]
        check('MAPPING_OWNER:' + key + ':' + path, item['source_path'] == owner or item['source_path'].startswith(owner + '/'))
        value = pointer(packet, item['source_path'])
        if item['relation'] == 'equal_decoded_value':
            check('MAPPING_EQUAL:' + key + ':' + path, value == pointer(target, path))
        else:
            method = 'method-markup' if key == 'fact-f-356' and path == '/body/value' else 'method-general'
            check('MAPPING_CONVERSION:' + key + ':' + path, item['source_path'] == owner and item['conversion_method_ref'] == ref(method))
    check('TOTAL_FIELD_COVERAGE', set(coverage) == {(key, '/body/' + field) for key in owner_by_key for field in body(key)})
    markup = coverage[('fact-f-356', '/body/value')]
    check('MARKUP_CONVERSION_EXPLICIT', markup.get('conversion_method_ref') == ref('method-markup'))
    comparison = body('comparison')
    check('COMPARISON', comparison['mapping_ref'] == ref('mapping') and comparison['output_digests'] == sorted(r['digest'] for r in mapping['outputs']) and comparison['field_mapping_count'] == len(coverage))
    imported = body('import')
    check('PACKET_BLOB', imported['original_bytes_ref'] == blob(PACKET) and imported['original_bytes_ref'] != source['original_bytes_ref'])
    check('IMPORT_BINDING', imported['decoder_ref'] == ref('method-general') and imported['portable_ref'] == ref('mapping') and imported['comparison_ref'] == ref('comparison') and imported['original_id'] == str(PACKET.relative_to(ROOT)) and imported['format'] == 'retained_native_documentary_readings.proposed.v1')
    for key in ['method-general', 'method-markup']:
        check('METHOD_SPEC:' + key, body(key)['specification_ref'] == blob(SPEC) and body(key)['evidence_mode'] == 'specification_example')
    # Independent XML checks above establish correspondence. This additional
    # exact-profile check covers metadata wording, constant policy and all fields
    # outside those semantic checks without pretending to be another oracle.
    expected_records = construct(packet)
    check('DECLARED_KEYS', set(by_key) == {r['key'] for r in expected_records})
    for expected in expected_records:
        check('SPECIFICATION_RECORD:' + expected['key'], by_key[expected['key']] == expected)
    return checks

def mutate(records, key, edit):
    """Rebind the ordered DAG after an edit so semantic cases reach their check."""
    changed, replacements = [], {}
    def replace(value):
        if isinstance(value, dict):
            if set(value) == {'kind', 'schema', 'digest'}:
                return replacements.get(canonical(value), value)
            return {k: replace(v) for k, v in value.items()}
        return [replace(v) for v in value] if isinstance(value, list) else value
    for original in records:
        row = deepcopy(original)
        if row['key'] == key:
            edit(row)
        row['body'] = replace(row['body'])
        if row['key'] == 'mapping':
            row['body']['outputs'] = ref_set(row['body']['outputs'])
        if row['key'] == 'comparison':
            mapping = next(r for r in changed if r['key'] == 'mapping')['body']
            row['body']['output_digests'] = sorted(r['digest'] for r in mapping['outputs'])
            row['body']['field_mapping_count'] = len(mapping['field_mappings'])
        row['dependencies'] = ref_set(refs(row['body']))
        replacements[canonical(record_ref(original))] = record_ref(row)
        changed.append(row)
    return changed

def negative_cases(packet, records, material):
    cases = []
    def field(name, key, target, value, error):
        cases.append((name, key, lambda row: row['body'].__setitem__(target, value), error))
    lookup = {r['key']: r for r in records}
    field('packet-as-source', 'source', 'original_bytes_ref', blob(PACKET), 'SOURCE_BLOB')
    field('source-as-packet', 'import', 'original_bytes_ref', lookup['source']['body']['original_bytes_ref'], 'PACKET_BLOB')
    field('drop-per-share-denominator', 'source-usdPerShare', 'denominator', [], 'UNIT_DENOMINATOR:usdPerShare')
    field('drop-dimension', 'source-c-13', 'dimensions', [], 'DIMENSIONS:c-13')
    field('nil-becomes-zero', 'fact-f-191', 'value', {'tag': 'Decimal', 'rational': {'n': '0', 'd': '1'}}, 'EXACT_VALUE:f-191')
    field('zero-becomes-nil', 'fact-f-325', 'value', {'tag': 'Nil'}, 'EXACT_VALUE:f-325')
    field('lost-sign', 'fact-f-94', 'value', {'tag': 'Decimal', 'rational': {'n': '565000000', 'd': '1'}}, 'EXACT_VALUE:f-94')
    field('eps-scaled', 'fact-f-105', 'value', {'tag': 'Decimal', 'rational': {'n': '611', 'd': '1'}}, 'EXACT_VALUE:f-105')
    field('decoded-markup-lost', 'fact-f-356', 'value', {'tag': 'Text', 'text': 'Inventory policy'}, 'EXACT_VALUE:f-356')
    field('entity-left-escaped', 'fact-f-1106', 'reported_text', 'Ernst &amp; Young LLP', 'CHARACTERS:f-1106')
    field('inferred-financial-time', 'ctx-f-147', 'time', {'tag': 'Instant', 'date': '2024-09-28'}, 'FINANCIAL_UNKNOWN:f-147:time')
    field('wrong-context-join', 'ctx-f-60', 'source_context_ref', record_ref(lookup['source-c-1']), 'CONTEXT_JOIN:f-60')
    field('wrong-unit-join', 'ctx-f-105', 'source_unit_ref', record_ref(lookup['source-usd']), 'UNIT_JOIN:f-105')
    field('missing-unit-promoted', 'ctx-f-7', 'source_unit_ref', {'tag': 'NotApplicable', 'reason': 'Assumed text'}, 'UNIT_JOIN:f-7')
    field('root-language-as-explicit', 'fact-f-7', 'explicit_language', {'tag': 'Present', 'token': 'en-US'}, 'RAW_FIELD:f-7:explicit_language')
    field('repeat-merged', 'fact-f-256', 'occurrence_refs', [record_ref(lookup['occ-f-207'])], 'FACT_JOINS:f-256')
    shifted = deepcopy(lookup['occ-f-147']['body']['locator']); shifted['byte_start'] += 1
    field('shifted-original-span', 'occ-f-147', 'locator', shifted, 'OCC_LOCATOR:f-147')
    field('concrete-admission', 'fact-f-102', 'interpretation_status', 'admitted', 'LITERAL')
    def remove_mapping(row):
        row['body']['field_mappings'].pop()
    cases.append(('missing-field-map', 'mapping', remove_mapping, 'TOTAL_FIELD_COVERAGE'))
    def wrong_owner(row):
        item = next(m for m in row['body']['field_mappings'] if m['target_ref'] == record_ref(lookup['fact-f-256']) and m['target_path'] == '/body/value')
        item['source_path'] = '/facts/10/candidate_value'
    cases.append(('equal-value-wrong-owner', 'mapping', wrong_owner, 'MAPPING_OWNER:fact-f-256:/body/value'))
    def silent_markup(row):
        item = next(m for m in row['body']['field_mappings'] if m['target_ref'] == record_ref(lookup['fact-f-356']) and m['target_path'] == '/body/value')
        item['conversion_method_ref'] = record_ref(lookup['method-general'])
    cases.append(('markup-caveat-lost', 'mapping', silent_markup, 'MAPPING_CONVERSION:fact-f-356:/body/value'))
    field('method-caveat-replaced', 'method-markup', 'algorithm', 'Taxonomy-validated plain text', 'SPECIFICATION_RECORD:method-markup')
    field('wrong-source-media', 'source', 'media_type', 'text/html', 'SPECIFICATION_RECORD:source')
    results = []
    for name, key, edit, expected in cases:
        altered = mutate(records, key, edit)
        try:
            validate(packet, altered, material)
        except ValueError as error:
            require(str(error) == expected, 'WRONG_NEGATIVE_DIAGNOSTIC:' + name + ':' + str(error))
            results.append({'case': name, 'rejected': str(error), 'dependent_refs_rebuilt': True})
        else:
            raise ValueError('CORRUPTION_ACCEPTED:' + name)
    return results

def protected_paths():
    paths = [PACKET, READINGS / 'check.py', READINGS / 'checks.json', READINGS / 'completion.json',
             BASE / 'common.py', BASE / 'profile_definitions.py', BASE / 'profile.json', BASE / 'completion-validation.json',
             ROOT / read(PACKET)['source']['path'], PLAN, SPEC, PDF,
             INTEGRATION / 'assessment-successor.json', INTEGRATION / 'integration-bindings.json', INTEGRATION / 'operation-successor.json',
             INTEGRATION / 'native-occurrence-bytes-supplement.json']
    return paths

def run_git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--record', action='store_true')
    mode.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    tick = time.monotonic()
    packet = read(PACKET)
    reader = reader_module()
    source_checks = reader.validate(packet)
    material = reader.source_material()
    records = construct(packet) if args.record or args.check_only else read(OUT / 'portable-records.json')
    checks = validate(packet, records, material)
    negatives = negative_cases(packet, records, material)
    findings = {'scope': 'selected_retained_source_specification_examples', 'upstream_executed': False, 'profile_registered': False,
        'counts': {'facts': 12, 'source_contexts': 4, 'source_units': 2, 'source_slices': 18, 'records': len(records),
                   'field_mappings': len(next(r for r in records if r['key'] == 'mapping')['body']['field_mappings']),
                   'source_checks': len(source_checks), 'portable_checks': len(checks), 'rejected_corruptions': len(negatives)},
        'source_checks': source_checks, 'portable_checks': checks, 'negative_cases': negatives}
    if args.check_only:
        print(json.dumps({'mode': 'check_only', **findings['counts']})); return
    if args.record:
        for name in ['portable-records.json', 'checks.json', 'protected-inputs.json', 'run-manifest.json']:
            require(not (OUT / name).exists(), 'ALREADY_RECORDED:' + name)
        require(run_git('rev-parse', 'HEAD') == '03fea070f089821f4759e49a4466a3399b7fc078', 'HEAD_CHANGED')
        require(sha((ROOT / '.git/index').read_bytes()) == '54c1f8bfd32b2a3e30fe8bea70befdd1b2106ca5b9955b6ea9b526ed12604db4', 'INDEX_CHANGED')
        require(run_git('diff', '--cached', '--name-only') == '', 'STAGED_WORK')
        dirty = run_git('diff', '--name-only').splitlines()
        require(len(dirty) == 36, 'TRACKED_DIRTY_COUNT')
        protected = [binding(p) for p in protected_paths()]
        protected += [binding(ROOT / name) for name in dirty if name not in CONTROLS]
        write_once(OUT / 'protected-inputs.json', protected)
        write_once(OUT / 'portable-records.json', records)
        write_once(OUT / 'checks.json', findings)
        manifest = {'recorded_utc': datetime.now(timezone.utc).isoformat(), 'git_commit': run_git('rev-parse', 'HEAD'),
            'command': 'python3 data/accounting-master/native-selected-portable-20261018/check.py --record',
            'environment': {'executable': sys.executable, 'python': platform.python_version(), 'conda_env': 'tfgpu',
                            'cpu_gpu': 'CPU standard-library file/XML checks only; no numerical framework or GPU initialized'},
            'data_version': binding(PACKET), 'random_seeds': 'N/A: deterministic correspondence',
            'wall_seconds': time.monotonic() - tick, 'plan_file': str(PLAN.relative_to(ROOT)),
            'result_file': str((OUT / 'result.md').relative_to(ROOT)), 'tracked_dirty_paths': dirty,
            'index_sha256': sha((ROOT / '.git/index').read_bytes()),
            'artifacts': [binding(OUT / name) for name in ['model.py', 'check.py', 'portable-records.json', 'checks.json', 'protected-inputs.json']]}
        write_once(OUT / 'run-manifest.json', manifest)
    else:
        require(findings == read(OUT / 'checks.json'), 'REPLAY_CHECKS_CHANGED')
        require(records == construct(packet), 'REPLAY_CONSTRUCTION_CHANGED')
        manifest = json.loads((OUT / 'run-manifest.json').read_bytes())
        for item in read(OUT / 'protected-inputs.json') + manifest['artifacts']:
            require(binding(ROOT / item['path']) == item, 'PROTECTED_CHANGED:' + item['path'])
        require(run_git('rev-parse', 'HEAD') == manifest['git_commit'], 'HEAD_CHANGED')
        require(sha((ROOT / '.git/index').read_bytes()) == manifest['index_sha256'], 'INDEX_CHANGED')
        require(run_git('diff', '--name-only').splitlines() == manifest['tracked_dirty_paths'], 'DIRTY_SET_CHANGED')
    print(json.dumps({'mode': 'record' if args.record else 'read_only_replay', **findings['counts'], 'status': 'pass'}))

if __name__ == '__main__':
    main()
