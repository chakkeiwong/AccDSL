"""Closed legal-company world envelope; no consolidation or sector postings."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re

import method_requirements_v1 as core

PROFILE = 'CompanyWorld/1'
FLAGS = {'executed': False, 'committed': False, 'source_admission': False,
         'accounting_admission': False, 'posting_authorized': False,
         'world_complete': False, 'references_resolved': False,
         'control_assessed': False}
SECTORS = {'corporate': 'CompanyComposition/1', 'bank': 'BankAssessment/1',
           'insurance': 'InsuranceAssessment/1'}
STATUS = {'conditional', 'unresolved'}
DIGEST = re.compile(r'^[0-9a-f]{64}$')
CORE_SHA256 = '6d176e25dada74da4623a0628e265ff88c7e06cdcf995a064e7d9186cd10b53a'


def bounded(body):
    # Bound the traversal before encoding or copying, including cyclic input.
    stack = [(body, 0)]
    count = 0
    while stack:
        item, depth = stack.pop()
        count += 1
        core.need(count <= core.MAX_NODES and depth <= core.MAX_DEPTH, 'world_structure_limit')
        if type(item) in (dict, list):
            core.need(len(item) <= core.MAX_NODES, 'world_structure_limit')
            if type(item) is dict:
                for key in item: text(key, 'world_key')
                children = item.values()
            else:
                children = item
            stack.extend((child, depth + 1) for child in children)
        elif type(item) is str:
            text(item, 'world_scalar')
        else:
            raise core.Invalid('world_scalar_type')
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'world_size_limit')


def text(value, label):
    core.need(type(value) is str and bool(value.strip()), label)
    core.text(value, label)


def digest(value, label):
    text(value, label); core.need(DIGEST.fullmatch(value) is not None, label + '_sha256')


def rational(value, label):
    text(value, label)
    return core.scalar(value, 'rational')


def validate(body):
    core.need(sha256(Path(core.__file__).read_bytes()).hexdigest() == CORE_SHA256,
              'world_core_dependency_hash')
    bounded(body)
    core.need(type(body) is dict, 'world_record')
    core.closed(body, ['profile', 'context', 'books', 'control_edges', 'components', 'obligations'], 'world')
    core.need(body['profile'] == PROFILE, 'world_profile')
    core.closed(body['context'], ['world_id', 'currency', 'calendar', 'case_id', 'mode'], 'world_context')
    for key, value in body['context'].items(): text(value, 'context_' + key)
    core.need(re.fullmatch('[A-Z]{3}', body['context']['currency']) is not None, 'world_currency')
    core.need(body['context']['mode'] in ['synthetic', 'conditional'], 'world_mode')
    core.need(body['context']['calendar'] == 'gregorian', 'world_calendar')
    books = body['books']; core.need(type(books) is dict and 0 < len(books) <= 64, 'book_count')
    identities, entities = set(), set()
    for key, book in books.items():
        text(key, 'book_key')
        core.closed(book, ['entity', 'book', 'currency', 'sector', 'state_ref', 'source_ref', 'view_ref'], 'legal_book')
        for name in ['entity', 'book', 'currency', 'sector']: text(book[name], 'book_' + name)
        core.need(book['currency'] == body['context']['currency'], 'book_currency_context')
        core.need(book['sector'] in SECTORS, 'book_sector'); digest(book['state_ref'], 'book_state_ref')
        digest(book['source_ref'], 'book_source_ref'); digest(book['view_ref'], 'book_view_ref')
        identity = (book['entity'], book['book'])
        core.need(identity not in identities, 'duplicate_legal_book'); identities.add(identity)
        entities.add(book['entity'])
    edges = body['control_edges']; core.need(type(edges) is list and len(edges) <= 128, 'control_edge_limit')
    edge_ids, pairs = set(), set()
    for edge in edges:
        core.closed(edge, ['id', 'parent', 'child', 'ownership_fraction', 'start', 'end_exclusive', 'control_premise'], 'control_edge')
        text(edge['id'], 'control_id'); core.need(edge['id'] not in edge_ids, 'duplicate_control_id'); edge_ids.add(edge['id'])
        for key in ['parent', 'child']: text(edge[key], 'control_' + key)
        core.need(edge['parent'] in entities and edge['child'] in entities, 'control_unknown_entity')
        core.need(edge['parent'] != edge['child'], 'self_control'); pair = (edge['parent'], edge['child'])
        core.need(pair not in pairs, 'duplicate_control_pair'); pairs.add(pair)
        fraction = rational(edge['ownership_fraction'], 'ownership_fraction')
        core.need(0 <= fraction <= 1, 'ownership_fraction_range')
        for key in ['start', 'end_exclusive']: core.scalar(edge[key], 'date')
        core.need(edge['start'] < edge['end_exclusive'], 'control_date_order')
        text(edge['control_premise'], 'control_premise')
    components = body['components']; core.need(type(components) is dict and len(components) <= 128, 'component_limit')
    occupied = set()
    for key, component in components.items():
        text(key, 'component_key')
        core.closed(component, ['owner', 'sector', 'profile', 'state_ref', 'source_ref', 'view_ref', 'status', 'obligation_ids'], 'component_handle')
        for name in ['owner', 'sector', 'profile', 'status']: text(component[name], 'component_' + name)
        core.need(component['owner'] in books, 'component_unknown_owner'); core.need(component['sector'] in SECTORS, 'component_sector')
        core.need(component['profile'] == SECTORS[component['sector']], 'component_profile_sector')
        owner_book = books[component['owner']]
        core.need(component['sector'] == owner_book['sector'], 'component_owner_sector')
        core.need(component['status'] in STATUS, 'component_status')
        for name in ['state_ref', 'source_ref', 'view_ref']:
            digest(component[name], 'component_' + name)
            core.need(component[name] == owner_book[name], 'component_' + name + '_binding')
        identity = (component['owner'], component['sector']); core.need(identity not in occupied, 'duplicate_sector_owner'); occupied.add(identity)
        core.need(type(component['obligation_ids']) is list, 'component_obligations')
        core.identifiers(component['obligation_ids'], 'component_obligation_ids')
        core.need(component['status'] != 'unresolved' or bool(component['obligation_ids']),
                  'unresolved_component_obligation_required')
    obligations = body['obligations']; core.need(type(obligations) is list and len(obligations) <= 512, 'obligation_limit')
    obligation_ids = set()
    for obligation in obligations:
        core.closed(obligation, ['id', 'meaning', 'affects'], 'world_obligation')
        text(obligation['id'], 'obligation_id'); core.need(obligation['id'] not in obligation_ids, 'duplicate_obligation_id'); obligation_ids.add(obligation['id'])
        text(obligation['meaning'], 'obligation_meaning'); core.identifiers(obligation['affects'], 'obligation_affects', nonempty=True)
    for component in components.values():
        core.need(set(component['obligation_ids']) <= obligation_ids, 'unknown_component_obligation')
    return True


def propose(body):
    try:
        validate(body)
        result = {'profile': PROFILE, **FLAGS, 'status': 'proposed', 'world_sha256': core.digest(body),
                  'world': deepcopy(body), 'book_ids': sorted(body['books']), 'component_ids': sorted(body['components']),
                  'unresolved_obligations': deepcopy(body['obligations']),
                  'scope': 'Opaque legal-book and sector handles only; no reference resolution, control assessment, posting, consolidation or admission',
                  'core_sha256': CORE_SHA256,
                  'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
        return result
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}


def verify(body, result):
    try: return core.canonical(propose(body)) == core.canonical(result)
    except Exception: return False
