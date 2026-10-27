"""A finite return-state proposal boundary; no journal publication or I/O."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json

PROFILE = 'CompanyModuleInvocationDraft/1'
WORLD = 'CompanyModuleBooksDraft/1'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(value): return sha256(canonical(value)).hexdigest()


def same(left, right): return canonical(left) == canonical(right)


class Refusal(Exception):
    def __init__(self, reason, status='invalid'):
        self.reason, self.status = reason, status


def need(condition, reason, status='invalid'):
    if not condition:
        raise Refusal(reason, status)


def native_capabilities(path, required):
    """Explicit profile assessment, not execution or an accounting conclusion."""
    first = path['initial_year']
    kinds = {o['kind'] for o in first['operations']}
    missing = []
    if 'return_settlement' not in kinds: missing.append('return_settlement_operation')
    if 'return_components' not in first: missing.append('return_component_memory')
    if 'return_findings' not in first: missing.append('return_eligibility_findings')
    missing += ['refund_liability_and_recovery_asset_accounts', 'recovered_inventory_valuation',
                'return_tax_and_report_classification', 'return_memory_rollforward']
    return {'status': 'unsupported', 'profile': path['profile'],
        'context': deepcopy(first['context']), 'missing_capabilities': missing,
        'required_original_owner': deepcopy(required['owner']),
        'owner_conversion_authorized': False, 'invoked': False}


def request(world, key, trusted):
    original = trusted['migration']
    return {'profile': PROFILE, 'operation': 'propose_return_settlement',
        'world_sha256': digest(world), 'book_key': key,
        'method_sha256': digest(trusted['descriptor']),
        'source_state_ref': deepcopy(original['source_state_ref']),
        'context_ref': deepcopy(original['projected']['source_context_ref']),
        'view_ref': deepcopy(original['projected']['source_view_ref']),
        'event': deepcopy(original['event']),
        'account_map': deepcopy(trusted['account_map']),
        'findings': {'all_rights_closed': True, 'handling_is_selling_cost': True},
        'posts': False}


def propose(world, invocation, trusted):
    before = deepcopy(world)
    try:
        need(type(world) is dict and set(world) == {'profile', 'books'}, 'world_fields')
        need(world['profile'] == WORLD and type(world['books']) is dict, 'world_profile')
        owners = set()
        for book_key, book in world['books'].items():
            need(type(book_key) is str and book_key and type(book) is dict, 'book_shape')
            owner = book.get('owner')
            need(type(owner) is dict and set(owner) == {'entity_id','book_id','branch_key'}, 'owner_shape')
            need(all(type(x) is str and x for x in owner.values()), 'owner_identity')
            identity = canonical(owner)
            need(identity not in owners, 'duplicate_legal_book')
            owners.add(identity)
        need(type(invocation) is dict and set(invocation) == {
            'profile','operation','world_sha256','book_key','method_sha256','source_state_ref',
            'context_ref','view_ref','event','account_map','findings','posts'}, 'invocation_fields')
        need(invocation['profile'] == PROFILE and invocation['operation'] == 'propose_return_settlement', 'invocation_profile')
        need(invocation['posts'] is False, 'posting_not_authorized')
        need(invocation['world_sha256'] == digest(world), 'stale_world')
        key = invocation['book_key']; need(type(key) is str and key in world['books'], 'book_missing')
        findings = invocation['findings']
        need(type(findings) is dict and set(findings) == {'all_rights_closed','handling_is_selling_cost'}, 'finding_fields')
        for name, value in findings.items():
            if value is None: raise Refusal('missing_'+name, 'unresolved')
            need(type(value) is bool, 'finding_type')
            need(value, 'unsupported_'+name, 'unsupported')
        expected = request(world, key, trusted)
        for field in ['method_sha256','source_state_ref','context_ref','view_ref','account_map','event']:
            need(same(invocation[field], expected[field]), 'changed_'+field, 'unsupported')
        projected = trusted['project']()
        current = world['books'][key]
        need(same(current, projected), 'incompatible_shared_book_state', 'unsupported')
        need(invocation['event']['context_ref'] == current['source_context_ref'], 'event_context')
        after = trusted['step'](deepcopy(current), deepcopy(invocation['event']), need)
        need(same(after, trusted['expected_after']), 'method_result_mismatch')
        journal = {k: str(Fraction(after['balances'][k])-Fraction(v)) for k,v in current['balances'].items()}
        need(sum(Fraction(x) for x in journal.values()) == 0, 'unbalanced_module_journal')
        q = lambda x: Fraction(int(x['n']), int(x['d']))
        cash = {name: {k: str(q(v)-q(current['accumulators'][name][k])) for k,v in values.items()}
                for name, values in after['accumulators'].items() if name.startswith('cash_')}
        need(Fraction(journal['cash']) == sum(Fraction(v) for v in cash['cash_movements'].values()), 'cash_origin_mismatch')
        proposal = deepcopy(world); proposal['books'][key] = after
        return {'status': 'proposed', 'world': before, 'proposed_world': proposal,
            'journal': journal, 'cash_effects': cash, 'method_sha256': invocation['method_sha256'],
            'source_state_ref': invocation['source_state_ref'], 'committed': False,
            'physical_durability': False, 'historical_admission': False, 'forecast_admission': False}
    except Refusal as exc:
        return {'status': exc.status, 'reason': exc.reason, 'world': before,
                'proposed_world': None, 'journal': None, 'committed': False}
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return {'status': 'invalid', 'reason': 'malformed_boundary_input', 'detail': type(exc).__name__,
                'world': before, 'proposed_world': None, 'journal': None, 'committed': False}
