"""Independent, bounded reads of authored native records; no old tool imports."""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
BASE = R / 'data/accounting-master'
load = lambda p: json.loads(p.read_text())
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def reference(record):
    return {'kind': record['kind'], 'schema': record['schema'],
            'digest': sha(('accdsl.portable.v1/' + record['schema']).encode()
                          + b'\0' + canonical(record))}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def inspect(packet, records, raw):
    """Check only occurrence ownership, source joins and candidate boundaries."""
    by = {row['key']: row for row in records}
    require(len(by) == len(records), 'record-key-uniqueness')
    refs = {key: reference(row) for key, row in by.items()}
    root = ET.fromstring(raw)
    paths = {}

    def walk(node, path):
        paths[path] = node
        for i, child in enumerate(node, 1):
            walk(child, path + '/' + str(i))

    walk(root, '/1')
    source = by['source']['body']['original_bytes_ref']
    require(source == {'kind': 'blob', 'algorithm': 'sha256',
                       'digest': sha(raw), 'byte_length': len(raw)}, 'source-blob')
    expected = {'occ-' + e['id'] for group in ('facts', 'contexts', 'units')
                for e in packet[group]}
    expected |= {'occ-link-' + str(i + 1) for i in range(len(packet.get('source_links', [])))}
    require({k for k, v in by.items() if v['kind'] == 'UnitOccurrence'} == expected,
            'occurrence-membership')
    for group in ('facts', 'contexts', 'units'):
        for entry in packet[group]:
            ident, span = entry['id'], entry['span']
            occ = by['occ-' + ident]['body']
            require(occ['source_ref'] == refs['source'], 'source-ref:' + ident)
            require(occ['locator'] == {k: span[k] for k in
                    ('byte_start', 'byte_end', 'element_path')} | {'element_id': ident},
                    'locator:' + ident)
            piece = raw[span['byte_start']:span['byte_end']]
            require(sha(piece) == span['slice_sha256'] and
                    piece.decode('utf-8') == span['raw_utf8'], 'source-bytes:' + ident)
            element = paths[span['element_path']]
            require(element.get('id') == ident, 'source-path:' + ident)
            if group != 'facts':
                require(by['source-' + ident]['body']['occurrence_ref'] == refs['occ-' + ident],
                        'evidence-join:' + ident)
                continue
            assertion, context = by['fact-' + ident]['body'], by['ctx-' + ident]['body']
            require(assertion['occurrence_refs'] == [refs['occ-' + ident]], 'fact-occurrence:' + ident)
            require(assertion['context_ref'] == refs['ctx-' + ident], 'fact-context:' + ident)
            require(context['source_context_ref'] == refs['source-' + element.get('contextRef')],
                    'context-source:' + ident)
            if element.get('unitRef'):
                require(context['source_unit_ref'] == refs['source-' + element.get('unitRef')],
                        'unit-source:' + ident)
            require(assertion['reported_text'] == (element.text or ''), 'literal:' + ident)
            if entry['decoded_text'] is None:
                require(element.text is None and entry['candidate_value']['tag'] == 'Nil'
                        and assertion['value']['tag'] == 'Nil', 'nil-empty-conversion:' + ident)
            else:
                require(assertion['reported_text'] == entry['decoded_text'], 'packet-literal:' + ident)
            require(assertion['source_attributes'] ==
                    [{'name': k, 'value': v} for k, v in sorted(element.attrib.items())],
                    'attributes:' + ident)
            require(assertion['interpretation_status'] == context['interpretation_status'] == 'candidate',
                    'candidate:' + ident)
            require(all(context[k]['tag'] == 'Unknown' for k in
                    ('legal_entity', 'book', 'perimeter', 'basis', 'currency_or_unit',
                     'time', 'calendar', 'dimensions')), 'financial-unknown:' + ident)
    # Mapping ownership is checked independently of equality of the value.
    fact_by_ref = {canonical(refs['fact-' + e['id']]): (e['id'], '/facts/' + str(i))
                   for i, e in enumerate(packet['facts'])}
    mapping_rows = 0
    for item in by['mapping']['body']['field_mappings']:
        target = fact_by_ref.get(canonical(item['target_ref']))
        if target:
            ident, owner = target
            require(item['source_path'] == owner or item['source_path'].startswith(owner + '/'),
                    'mapping-owner:' + ident)
            mapping_rows += 1
    signatures = defaultdict(list)
    for e in packet['facts']:
        attrs = {k: v for k, v in e['source_attributes'].items() if k != 'id'}
        signatures[canonical([e['expanded_concept'], attrs, e['decoded_text']])].append(e['id'])
    repeated = sorted(sorted(v) for v in signatures.values() if len(v) > 1)
    a, b = (by['fact-' + ident]['body'] for ident in ('f-207', 'f-256'))
    require(a['reported_text'] == b['reported_text'] == '56950000000', 'equal-pair-value')
    require(a['value'] == b['value'] == {'tag': 'Decimal', 'rational': {'n': '56950000000', 'd': '1'}},
            'equal-pair-rational')
    require(a['occurrence_refs'] != b['occurrence_refs'] and a['context_ref'] != b['context_ref'],
            'equal-pair-distinct')
    return {'records': len(records), 'record_kinds': dict(sorted(Counter(v['kind'] for v in records).items())),
            'facts': len(packet['facts']), 'contexts': len(packet['contexts']), 'units': len(packet['units']),
            'source_links': len(packet.get('source_links', [])), 'fact_mapping_rows_checked': mapping_rows,
            'source_signature_definition': 'expanded concept + all source attributes except id + decoded text',
            'repeated_source_signature_groups': len(repeated),
            'repeated_group_members': sum(map(len, repeated)),
            'pair_occurrences': [by['occ-' + i]['body']['locator'] for i in ('f-207', 'f-256')]}


def examples():
    pairs = list(itertools.product(('A1', 'A2'), ('B1', 'B2')))
    assert len(set(pairs)) == 4
    content = b'same source paragraph'
    occurrences = [{'id': 'o1', 'locator': 1, 'content_digest': sha(content)},
                   {'id': 'o2', 'locator': 2, 'content_digest': sha(content)}]
    alias = {'hypothesis': 'same contextual assertion and compatible lineage explicitly established',
             'assertion': 'a1', 'supporting_occurrence_ids': ['o1', 'o2']}
    assert len(occurrences) == len(set(alias['supporting_occurrence_ids'])) == 2
    seq_true = [[['A1', 'A2'], ['B1', 'B2']]]
    seq_false = [[[a], [b]] for a, b in pairs]
    finer, coarse = (Fraction(5450), Fraction(5550)), (Fraction(4500), Fraction(5500))
    intersection = (max(finer[0], coarse[0]), min(finer[1], coarse[1]))
    witness = Fraction(5525)
    assert finer[0] <= witness <= finer[1] and not intersection[0] <= witness <= intersection[1]
    return {'status': 'conditional authored examples; no XML/XPath/processor execution',
            'cases': [
                {'id': 'content-sharing', 'occurrences': occurrences, 'content_bodies': 1,
                 'retained_occurrences': 2, 'original_span_bytes_assumed_identical': True},
                {'id': 'assertion-alias', 'alias': alias, 'retained_occurrences': 2,
                 'not_applied_to_apple_pair': True},
                {'id': 'formula-bindings', 'hypotheses_from':
                 'data/accounting-master/r06-formula-binding-20261023/binding-example.json',
                 'singleton': [list(p) for p in pairs], 'sequence_matches_true': seq_true,
                 'sequence_matches_false': seq_false, 'possible_data_set_counts': [4, 1, 4],
                 'mandatory_processor_calls': 'not established'},
                {'id': 'sequence-cardinality', 'before_nodes': ['A1', 'A2'], 'after_nodes': ['A1'],
                 'test': 'length(A)=2', 'before': True, 'after': False,
                 'equal_numeric_values_do_not_establish_node_identity': True},
                {'id': 'calculation-interval', 'finer': [str(v) for v in finer],
                 'coarse': [str(v) for v in coarse], 'intersection': [str(v) for v in intersection],
                 'exact_witness': str(witness), 'finest_only_accepts': True, 'intersection_accepts': False,
                 'condition': 'Closed-interval arithmetic only; not a resolution of Calc1.1 5.1/5.4'},
                {'id': 'inline-required-id', 'input_ids': ['i1', 'i2'],
                 'shared_output_id_exists': False,
                 'reason': 'One output id cannot equal two distinct required non-absent IDs; necessary condition only'},
                {'id': 'admission', 'source_preparation': 'candidate', 'financial_admission': False,
                 'posting_authority': False, 'formula_enabled_in_selected_importer': False}]}


def run():
    full = load(BASE / 'native-full-portable-20261018/native-packet.json')
    raw = (R / full['source']['path']).read_bytes()
    assert sha(raw) == full['source']['sha256'] and len(raw) == full['source']['byte_length']
    results, negatives = {}, []
    for label, packet_path, record_path in (
        ('selected', 'native-occurrence-bytes-20261018/readings.json', 'native-selected-portable-20261018/portable-records.json'),
        ('full', 'native-full-portable-20261018/native-packet.json', 'native-full-portable-20261018/portable-records.json')):
        packet, records = load(BASE / packet_path), load(BASE / record_path)
        results[label] = inspect(packet, records, raw)
        by = {v['key']: v for v in records}
        cases = ('redirect-occurrence', 'remove-occurrence', 'equal-value-wrong-owner', 'admit-candidate')
        for case in cases:
            changed = deepcopy(records)
            new = {v['key']: v for v in changed}
            if case == 'redirect-occurrence':
                new['fact-f-256']['body']['occurrence_refs'] = [reference(by['occ-f-207'])]
                expected = 'fact-occurrence:f-256'
            elif case == 'remove-occurrence':
                changed.remove(new['occ-f-256'])
                expected = 'occurrence-membership'
            elif case == 'equal-value-wrong-owner':
                target = reference(by['fact-f-256'])
                item = next(i for i in new['mapping']['body']['field_mappings']
                            if i['target_ref'] == target and i['target_path'] == '/body/value')
                wrong_index = next(i for i, e in enumerate(packet['facts']) if e['id'] == 'f-207')
                item['source_path'] = '/facts/' + str(wrong_index) + '/candidate_value'
                expected = 'mapping-owner:f-256'
            else:
                new['fact-f-256']['body']['interpretation_status'] = 'admitted'
                expected = 'candidate:f-256'
            # The scoped projection recalculates Refs; no stale-ref failure is the oracle.
            try:
                inspect(packet, changed, raw)
            except ValueError as error:
                require(str(error) == expected, 'unexpected-negative:' + str(error))
                negatives.append({'packet': label, 'case': case, 'rejection': str(error)})
            else:
                raise AssertionError('negative accepted: ' + case)
    assert results['full']['facts'] == 1127 and results['full']['records'] == 3788
    assert (results['full']['repeated_source_signature_groups'], results['full']['repeated_group_members']) == (69, 151)
    assert results['selected']['facts'] == 12 and results['selected']['records'] == 54
    return {'projection': results, 'negative_controls': negatives, 'examples': examples()}
