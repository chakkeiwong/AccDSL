"""Create the finite documentary packet once; no upstream execution."""
from copy import deepcopy
from model import *

INVENTORY = ROOT / 'data/accounting-master/native-shape-inventory-20261018/inventory.json'
FACT_IDS = ['f-57', 'f-59', 'f-13', 'f-14', 'f-934', 'f-935', 'f-1127']
CONTEXT_IDS = ['c-1', 'c-58', 'c-59', 'c-60', 'c-61', 'c-128']
VALUE_REASON = 'Lexical digits alone do not establish taxonomy type; preserve original token'

def construct_packet():
    inventory = read(INVENTORY)
    by_id = {r['id']: r for r in inventory['entries'] if r['id']}
    raw = (ROOT / inventory['source']['path']).read_bytes()
    reader = reader_module()
    material = reader.source_material()
    root, xml_by_id, locate = material[1], material[2], material[4]
    contexts, facts = [], []
    for key in CONTEXT_IDS:
        entry, element = by_id[key], xml_by_id[key]
        contexts.append({'id': key, 'span': locate(key)[0],
            'identifier': reader.tree_reading(element.find(reader.XI + 'entity/' + reader.XI + 'identifier')),
            'period': reader.tree_reading(element.find(reader.XI + 'period')),
            'dimensions_and_qualifiers': deepcopy(entry['qualifiers'])})
    for key in FACT_IDS:
        entry, element = by_id[key], xml_by_id[key]
        require(entry['unit_id'] is None and len(element) == 0, 'SELECTION_UNIT_OR_CHILD')
        facts.append({'id': key, 'span': locate(key)[0], 'expanded_concept': entry['name'],
            'source_attributes': dict(element.attrib), 'decoded_text': element.text,
            'candidate_value': unknown(VALUE_REASON), 'source_context_id': element.get('contextRef'),
            'source_unit_id': None, 'explicit_language': None,
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
    return {'evidence_mode': 'retained_source_hazard_documentary_packet', 'upstream_executed': False,
        'source': inventory['source'], 'inventory_ref': blob(INVENTORY), 'namespace_bindings': inventory['namespace_bindings'],
        'contexts': contexts, 'units': [], 'facts': facts, 'source_links': [source_link],
        'publication_time': {'tag': 'Unknown', 'reason': 'Publication availability not established by this packet'},
        'taxonomy_validation': 'not_run'}

if __name__ == '__main__':
    write_once(PACKET, construct_packet())
    print('Prepared seven unitless facts, six contexts including four typed dimensions, and one ID-less source link.')
