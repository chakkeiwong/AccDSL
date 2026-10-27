"""Create the finite documentary packet once; no upstream execution."""
from copy import deepcopy
from model import *

INVENTORY = ROOT / 'data/accounting-master/native-shape-inventory-20261018/inventory.json'
VALUE_REASON = 'Lexical digits alone do not establish taxonomy type; preserve original token'

def construct_packet():
    inventory = read(INVENTORY)
    by_id = {r['id']: r for r in inventory['entries'] if r['id']}
    raw = (ROOT / inventory['source']['path']).read_bytes()
    reader = reader_module()
    material = reader.source_material()
    root, xml_by_id, locate = material[1], material[2], material[4]
    contexts, facts, units = [], [], []
    for key in [r['id'] for r in inventory['entries'] if r['category'] == 'context']:
        entry, element = by_id[key], xml_by_id[key]
        contexts.append({'id': key, 'span': locate(key)[0],
            'identifier': reader.tree_reading(element.find(reader.XI + 'entity/' + reader.XI + 'identifier')),
            'period': reader.tree_reading(element.find(reader.XI + 'period')),
            'dimensions_and_qualifiers': deepcopy(entry['qualifiers'])})
    for key in [r['id'] for r in inventory['entries'] if r['category'] == 'unit']:
        entry = by_id[key]
        units.append({'id': key, 'span': locate(key)[0],
            **{side: [{'token': m['token'], 'expanded_name': '{' + m['namespace_uri'] + '}' + m['local_name']} for m in entry[side]]
               for side in ['numerator', 'denominator']}})
    for key in [r['id'] for r in inventory['entries'] if r['category'] == 'fact']:
        entry, element = by_id[key], xml_by_id[key]
        require(len(element) == 0, 'UNSUPPORTED_FACT_CHILDREN')
        lexical_class = entry['lexical']['class']
        if lexical_class == 'nil':
            value = {'tag': 'Nil'}
        elif lexical_class == 'decimal_lexical_candidate':
            value = {'tag': 'Decimal', 'rational': entry['lexical']['rational_candidate']} if entry['unit_id'] else unknown(VALUE_REASON)
        else:
            require(lexical_class == 'text', 'UNSUPPORTED_LEXICAL_CLASS')
            value = {'tag': 'UnvalidatedText', 'text': element.text}
        facts.append({'id': key, 'span': locate(key)[0], 'expanded_concept': entry['name'],
            'source_attributes': dict(element.attrib), 'decoded_text': element.text,
            'candidate_value': value, 'source_context_id': element.get('contextRef'),
            'source_unit_id': element.get('unitRef'), 'explicit_language': None,
            'lexical_class': lexical_class, 'taxonomy_type': 'Unknown',
            'root_language_evidence': {'source_path': '/1', 'attribute': reader.XML + 'lang', 'value': root.get(reader.XML + 'lang')},
            'financial_context': {k: {'tag': 'Unknown', 'reason': 'No admitted mapping in this documentary unit'}
                for k in ['legal_entity', 'book', 'perimeter', 'basis', 'currency_or_unit', 'calendar', 'dimensions', 'financial_time']},
            'admission': 'candidate_only'})
    link = inventory['entries'][0]
    require(link['category'] == 'link' and link['id'] is None, 'SOURCE_LINK_SELECTION')
    span = deepcopy(link['span'])
    span.update(id=None, element_path=link['element_path'], raw_utf8=raw[span['byte_start']:span['byte_end']].decode())
    source_link = {'id': None, 'position': 1, 'span': span, 'expanded_name': qname(link['name']),
                   'source_attributes': link['attributes'], 'source_tree': link['source_tree']}
    return {'evidence_mode': 'retained_source_full_documentary_packet', 'upstream_executed': False,
        'source': inventory['source'], 'inventory_ref': blob(INVENTORY), 'namespace_bindings': inventory['namespace_bindings'],
        'contexts': contexts, 'units': units, 'facts': facts, 'source_links': [source_link],
        'publication_time': {'tag': 'Unknown', 'reason': 'Publication availability not established by this packet'},
        'taxonomy_validation': 'not_run'}

if __name__ == '__main__':
    write_once(PACKET, construct_packet())
    print('Prepared 1127 facts, 193 contexts, seven units and one ID-less source link.')
