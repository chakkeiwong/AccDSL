"""Finite documentary examples; no upstream importer or runtime registration."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / 'data/accounting-master/native-xbrl-translation-20261018'
READINGS = ROOT / 'data/accounting-master/native-occurrence-bytes-20261018'
PACKET = OUT / 'native-packet.json'
SPEC = ROOT / 'docs/design/proposal/architecture/native-full-portable-proposed-v1.md'
PLAN = ROOT / 'docs/plans/accounting-native-full-portable-20261018.md'
INTEGRATION = ROOT / 'data/accounting-master/early-conversion-integration-20261018'
PDF = ROOT / 'docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf'
CONTROLS = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
            'data/accounting-master/next-plan.md', 'docs/plans/accounting-mission-requirements.md']
sys.path.insert(0, str(BASE))
from common import blob, canonical, pointer, read, record_ref, refs, ref_set, require, sha, typed, unknown, write_once
from profile_definitions import profile

def reader_module():
    spec = importlib.util.spec_from_file_location('selected_source_reader', READINGS / 'check.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

def qname(expanded):
    require(expanded.startswith('{') and '}' in expanded, 'EXPANDED_QNAME')
    uri, local = expanded[1:].split('}', 1)
    return {'namespace_uri': uri, 'local_name': local}

def expand(token, packet):
    ns = {r['prefix']: r['namespace_uri'] for r in packet['namespace_bindings']}
    prefix, local = token.split(':', 1) if ':' in token else ('', token)
    return {'namespace_uri': ns[prefix], 'local_name': local}

def raw_field(attributes, name):
    return {'tag': 'Present', 'token': attributes[name]} if name in attributes else {'tag': 'Absent'}

def locator(entry):
    span = entry['span']
    return {k: span[k] for k in ['byte_start', 'byte_end', 'element_path']} | {'element_id': entry['id']}

def period(entry):
    children = {c['name'].split('}')[-1]: c['text'] for c in entry['period']['children']}
    if set(children) == {'startDate', 'endDate'}:
        return {'form': 'duration', 'start_token': children['startDate'], 'end_token': children['endDate'], 'instant_token': None}
    require(set(children) == {'instant'}, 'SELECTED_PERIOD_SHAPE')
    return {'form': 'instant', 'start_token': None, 'end_token': None, 'instant_token': children['instant']}

def dimensions(entry, packet):
    result = []
    raw = entry['span']['raw_utf8'].encode('utf-8')
    matches = list(re.finditer(br'<xbrldi:(explicitMember|typedMember)\b[^>]*>.*?</xbrldi:\1>', raw, re.S))
    require(len(matches) == len(entry['dimensions_and_qualifiers']), 'SELECTED_DIMENSION_SPANS')
    for item, match in zip(entry['dimensions_and_qualifiers'], matches):
        evidence = item['reading']
        axis = evidence['attributes']['dimension']
        is_typed = evidence['name'].endswith('}typedMember')
        member = None if is_typed else evidence['text']
        result.append({'container': item['container'], 'form': 'typed' if is_typed else 'explicit', 'axis_token': axis, 'axis_qname': expand(axis, packet),
                       'member_token': member, 'member_qname': unknown('Typed domain subtree is retained; no explicit member QName') if is_typed else expand(member, packet),
                       'source_span': {'byte_start': entry['span']['byte_start'] + match.start(),
                                       'byte_end': entry['span']['byte_start'] + match.end()}})
    return result

def construct(packet):
    declared = profile()
    records, outputs, mappings = [], [], []
    methods = {}
    def add(kind, key, body, owner=None, aliases=None):
        record = {'kind': kind, 'schema': declared['records'][kind]['schema'], 'key': key, 'revision': 0,
                  'body': body, 'dependencies': ref_set(refs(body))}
        ref = record_ref(record)
        records.append(record)
        if owner is not None:
            outputs.append(ref)
            for field, value in body.items():
                source_path = owner + '/' + (aliases or {}).get(field, field)
                try:
                    equal = canonical(pointer(packet, source_path)) == canonical(value)
                except (KeyError, IndexError, TypeError, ValueError):
                    equal = False
                mapping = {'source_path': source_path if equal else owner, 'target_ref': ref,
                           'target_path': '/body/' + field, 'relation': 'equal_decoded_value' if equal else 'explicit_conversion'}
                if not equal:
                    unvalidated = kind == 'ReportedAssertion' and field == 'value' and pointer(packet, owner).get('candidate_value', {}).get('tag') == 'UnvalidatedText'
                    mapping['conversion_method_ref'] = methods['text' if unvalidated else 'general']
                mappings.append(mapping)
        return ref
    for key, name, algorithm in [
        ('general', 'retained-native-full-readings', 'Preserve all source occurrences, exact lexical candidates, typed subtrees, unknown financial time, nil/zero and source-link adjunct; no taxonomy or financial admission'),
        ('text', 'decoded-unvalidated-text', 'Preserve decoded characters as portable Text, including markup; retain UnvalidatedText packet tag and Unknown taxonomy type; no execution or sanitization')]:
        methods[key] = add('ConversionMethod', 'method-' + key, {'name': name, 'algorithm': algorithm,
                           'specification_ref': blob(SPEC), 'evidence_mode': 'specification_example'})
    identity = packet['source']['path']
    source = add('SourceVersion', 'source', {'original_bytes_ref': blob(ROOT / identity), 'media_type': 'application/xml',
        'origin': 'retained-file:' + identity, 'acquisition': unknown('Acquisition receipt not established by this selected packet'),
        'issuer': unknown('Source registrant and CIK evidence not promoted to admitted issuer identity'), 'document_identity': identity,
        'publication_evidence': unknown(packet['publication_time']['reason']),
        'vintage_evidence': unknown('Historical byte availability not established'), 'namespace_bindings': packet['namespace_bindings']}, '',
        {'document_identity': 'source/path'})
    def occurrence(entry, owner):
        return add('UnitOccurrence', 'occ-' + entry['id'], {'source_ref': source, 'locator': locator(entry),
            'package_root_key': identity, 'parent_key': 'xml-root', 'disposition': 'retained'}, owner)
    contexts, units = {}, {}
    for i, entry in enumerate(packet['contexts']):
        owner = '/contexts/' + str(i)
        contexts[entry['id']] = add('XbrlContextEvidence', 'source-' + entry['id'], {
            'occurrence_ref': occurrence(entry, owner), 'xml_id': entry['id'],
            'identifier': {'scheme': entry['identifier']['attributes']['scheme'], 'text': entry['identifier']['text']},
            'period': period(entry), 'dimensions': dimensions(entry, packet), 'non_dimension_spans': []}, owner, {'xml_id': 'id'})
    for i, entry in enumerate(packet['units']):
        owner = '/units/' + str(i)
        units[entry['id']] = add('XbrlUnitEvidence', 'source-' + entry['id'], {
            'occurrence_ref': occurrence(entry, owner), 'xml_id': entry['id'],
            **{side: [{'token': m['token'], 'qname': qname(m['expanded_name'])} for m in entry[side]]
               for side in ['numerator', 'denominator']}}, owner, {'xml_id': 'id'})
    for i, entry in enumerate(packet['facts']):
        owner, key = '/facts/' + str(i), entry['id']
        occ = occurrence(entry, owner)
        financial = {('time' if name == 'financial_time' else name): unknown(value['reason'])
                     for name, value in entry['financial_context'].items()}
        context = add('Context', 'ctx-' + key, {'source_context_ref': contexts[entry['source_context_id']],
            'source_unit_ref': units.get(entry['source_unit_id'], unknown('No unitRef; applicability/type not established')),
            **financial, 'interpretation_status': 'candidate'}, owner)
        value = deepcopy(entry['candidate_value'])
        if value['tag'] == 'UnvalidatedText':
            value['tag'] = 'Text'
        attributes = entry['source_attributes']
        add('ReportedAssertion', 'fact-' + key, {'occurrence_refs': [occ], 'context_ref': context,
            'concept': qname(entry['expanded_concept']), 'context_id_token': raw_field(attributes, 'contextRef'),
            'unit_id_token': raw_field(attributes, 'unitRef'), 'reported_text': entry['decoded_text'] or '',
            'source_attributes': [{'name': name, 'value': value} for name, value in sorted(attributes.items())], 'value': value,
            'decimals': raw_field(attributes, 'decimals'), 'precision': raw_field(attributes, 'precision'),
            'explicit_language': raw_field(attributes, '{http://www.w3.org/XML/1998/namespace}lang'),
            'effective_language': unknown('Root language retained as evidence; effective-language rule not admitted'),
            'interpretation_status': 'candidate'}, owner, {'reported_text': 'decoded_text', 'value': 'candidate_value'})
    for i, entry in enumerate(packet['source_links']):
        add('UnitOccurrence', 'occ-link-' + str(entry['position']), {'source_ref': source, 'locator': locator(entry),
            'package_root_key': identity, 'parent_key': 'xml-root', 'disposition': 'retained'}, '/source_links/' + str(i))
    mapping = add('ImportMapping', 'mapping', {'outputs': ref_set(outputs), 'field_mappings': mappings})
    comparison = add('ImportComparison', 'comparison', {'mapping_ref': mapping,
        'output_digests': sorted(r['digest'] for r in outputs), 'field_mapping_count': len(mappings),
        'verdict': 'correspondence_checked', 'evidence_mode': 'specification_example'})
    add('LegacyImport', 'import', {'format': 'retained_native_documentary_readings.proposed.v1', 'original_bytes_ref': blob(PACKET),
        'original_id': str(PACKET.relative_to(ROOT)), 'decoder_ref': methods['general'], 'portable_ref': mapping, 'comparison_ref': comparison})
    return records

def link_adjunct(packet, records):
    occurrence = next(r for r in records if r['key'] == 'occ-link-1')
    entry = packet['source_links'][0]
    return {'schema': 'accdsl.native_source_link.documentary.proposed.v1', 'status': 'proposed',
            'occurrence_ref': record_ref(occurrence), 'expanded_name': entry['expanded_name'],
            'source_attributes': [{'name': k, 'value': v} for k, v in sorted(entry['source_attributes'].items())],
            'resolution_status': 'not_run'}
