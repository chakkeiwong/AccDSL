"""One-time construction of documentary records, not an AccDSL implementation."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'


def closed(properties):
    return {'type': 'object', 'additionalProperties': False,
            'required': list(properties), 'properties': properties}


def ref(name):
    return {'$ref': '#/$defs/' + name}


def amount(value):
    value = Fraction(value)
    return {'n': str(value.numerator), 'd': str(value.denominator)}


def main():
    paths = [OUT / 'schema.json', OUT / 'cases.json']
    if any(p.exists() for p in paths):
        raise RuntimeError('One-time preparation refuses to overwrite evidence')
    text = {'type': 'string', 'minLength': 1}
    instant = {'type': 'string', 'format': 'date-time',
               'pattern': r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$'}
    context = closed({'entity': text, 'book': text, 'currency': text})
    rational = closed({'n': {'type': 'string', 'pattern': r'^(0|-?[1-9][0-9]*)$'},
                       'd': {'type': 'string', 'pattern': r'^[1-9][0-9]*$'}})
    unknown = closed({'tag': {'const': 'unknown'}, 'reason': text,
                      'obligations': {'type': 'array', 'minItems': 1, 'uniqueItems': True, 'items': text}})
    facility = closed({'tag': {'const': 'facility'}, 'id': text, 'context': ref('context'),
                       'limit': ref('amount'), 'drawn': ref('amount'), 'reserved': ref('amount'),
                       'available_from': instant, 'expires_exclusive': instant,
                       'eligibility': {'oneOf': [{'type': 'boolean'}, unknown]}, 'source_ref': text})
    funding = {'oneOf': [closed({'tag': {'const': 'known_none'}, 'source_ref': text}), unknown, facility]}
    decision = {'oneOf': [closed({'policy': {'const': 'cash_only'}}),
                            closed({'policy': {'const': 'explicit_draw'}, 'facility_id': text,
                                    'amount': ref('amount'), 'settles_at': instant,
                                    'draw_before_payment': {'type': 'boolean'}, 'authorisation_ref': text})]}
    evidence = {'type': 'object', 'minProperties': 1, 'additionalProperties': {'oneOf': [
        closed({'kind': {'const': 'retained_source'}, 'path': text, 'sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}}),
        closed({'kind': {'const': 'scenario_assumption'}, 'description': text})]}}
    schema = closed({'profile': {'const': 'SettlementDecisionDraft/1'},
                     'context': ref('context'), 'decision_at': instant, 'payment_at': instant,
                     'information_as_of': instant, 'evidence': evidence, 'assumption_ref': text,
                     'opening': closed({'snapshot_at': instant, 'cash': ref('amount'),
                                        'payables': ref('amount'), 'other_payables': ref('amount'),
                                        'debt': ref('amount'), 'source_ref': text}),
                     'claim': closed({'id': text, 'context': ref('context'), 'recognised': ref('amount'),
                                      'adjustments': ref('amount'), 'settled': ref('amount'),
                                      'outstanding': ref('amount'), 'due_at': instant, 'source_ref': text}),
                     'funding': funding, 'decision': decision})
    schema.update({'$schema': 'https://json-schema.org/draft/2020-12/schema',
                   'title': 'SettlementDecisionDraft/1 documentary input',
                   '$defs': {'amount': rational, 'context': context}})
    source = json.loads(SOURCE.read_text()); records = source['record_registry']
    projection = records[source['aliases']['projection.stress7']['digest']]['body']
    opening = records[projection['opening_ref']['digest']]['body']
    ctx = records[opening['context_ref']['digest']]['body']
    local_context = {k: ctx[k] for k in ('entity', 'book', 'currency')}
    scenario = 'Authored payable allocation and facility; no intervening movements except the proposed draw and payment. Not issuer facts.'
    base = {'profile': 'SettlementDecisionDraft/1', 'context': local_context,
            'decision_at': '2025-01-04T09:00:00Z', 'payment_at': '2025-01-04T12:00:00Z',
            'information_as_of': '2025-01-04T09:00:00Z',
            'evidence': {'retained': {'kind': 'retained_source', 'path': str(SOURCE.relative_to(ROOT)),
                                      'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()},
                         'scenario': {'kind': 'scenario_assumption', 'description': scenario}},
            'assumption_ref': 'scenario',
            'opening': {'snapshot_at': '2025-01-04T09:00:00Z', 'cash': opening['balances']['cash'],
                        'payables': amount(200), 'other_payables': amount(40), 'debt': amount(100),
                        'source_ref': 'retained'},
            'claim': {'id': 'supplier-claim-1', 'context': deepcopy(local_context),
                      'recognised': amount(160), 'adjustments': amount(0), 'settled': amount(0),
                      'outstanding': amount(160), 'due_at': '2025-01-04T12:00:00Z', 'source_ref': 'scenario'},
            'funding': {'tag': 'facility', 'id': 'facility-1', 'context': deepcopy(local_context),
                        'limit': amount(100), 'drawn': amount(0), 'reserved': amount(0),
                        'available_from': '2025-01-01T00:00:00Z', 'expires_exclusive': '2026-01-01T00:00:00Z',
                        'eligibility': True, 'source_ref': 'scenario'},
            'decision': {'policy': 'explicit_draw', 'facility_id': 'facility-1', 'amount': amount('85.4'),
                         'settles_at': '2025-01-04T11:00:00Z', 'draw_before_payment': True, 'authorisation_ref': 'scenario'}}
    cases = []

    def case(name, expected, changes=()):
        body = deepcopy(base)
        for path, value in changes:
            node = body
            keys = path.split('.')
            for k in keys[:-1]:
                node = node[k]
            node[keys[-1]] = value
        cases.append({'id': name, 'expected': expected, 'body': body})

    unknown_value = {'tag': 'unknown', 'reason': 'Commitment or conditions not supplied', 'obligations': ['obtain-terms']}
    case('funded_payment', 'proposed')
    case('cash_only_shortfall', 'infeasible_under_policy', [('decision', {'policy': 'cash_only'}), ('funding', {'tag': 'known_none', 'source_ref': 'scenario'})])
    case('cash_only_unknown_funding', 'unresolved_funding', [('decision', {'policy': 'cash_only'}), ('funding', unknown_value)])
    case('cash_only_sufficient_unknown_funding', 'proposed', [('decision', {'policy': 'cash_only'}), ('funding', unknown_value), ('opening.cash', amount(200))])
    case('explicit_draw_unknown_funding', 'unresolved_funding', [('funding', unknown_value)])
    case('unknown_eligibility', 'unresolved_funding', [('funding.eligibility', unknown_value)])
    case('known_ineligible', 'infeasible_under_policy', [('funding.eligibility', False)])
    case('reserved_capacity', 'infeasible_under_policy', [('funding.reserved', amount(20))])
    case('drawn_capacity', 'infeasible_under_policy', [('funding.drawn', amount(20))])
    case('late_draw', 'infeasible_under_policy', [('decision.settles_at', '2025-01-04T13:00:00Z')])
    case('expired_at_draw', 'infeasible_under_policy', [('funding.expires_exclusive', '2025-01-04T11:00:00Z')])
    case('draw_before_availability', 'infeasible_under_policy', [('funding.available_from', '2025-01-05T00:00:00Z')])
    case('same_instant_ordered', 'proposed', [('decision.settles_at', base['payment_at'])])
    case('same_instant_unordered', 'invalid_input', [('decision.settles_at', base['payment_at']), ('decision.draw_before_payment', False)])
    case('future_information', 'invalid_input', [('information_as_of', '2025-01-05T00:00:00Z')])
    case('claim_rollforward_mismatch', 'invalid_input', [('claim.settled', amount(1))])
    case('control_account_mismatch', 'invalid_input', [('opening.other_payables', amount(41))])
    case('wrong_currency', 'invalid_input', [('funding.context.currency', 'EUR')])
    case('unresolved_authorisation', 'invalid_input', [('decision.authorisation_ref', 'missing')])
    case('source_is_not_authorisation', 'invalid_input', [('decision.authorisation_ref', 'retained')])
    case('wrong_facility', 'invalid_input', [('decision.facility_id', 'another-facility')])
    case('noncanonical_rational', 'invalid_input', [('decision.amount', {'n': '854', 'd': '10'})])
    case('unsupported_policy_field', 'invalid_input', [('decision.automatic_draw', True)])
    case('stale_snapshot', 'invalid_input', [('opening.snapshot_at', '2025-01-03T09:00:00Z')])
    case('decision_after_payment', 'invalid_input', [('decision_at', '2025-01-05T09:00:00Z'), ('opening.snapshot_at', '2025-01-05T09:00:00Z')])
    case('draw_before_decision', 'invalid_input', [('decision.settles_at', '2025-01-04T08:00:00Z')])
    case('insufficient_chosen_draw', 'infeasible_under_policy', [('decision.amount', amount(80))])
    case('negative_headroom_input', 'invalid_input', [('funding.drawn', amount(110))])
    for p, data in zip(paths, [schema, {'scope': 'Synthetic documentary proposals; no committed runtime or real-company lending facts', 'source_context': ctx, 'cases': cases}]):
        p.write_text(json.dumps(data, indent=2) + chr(10))
    print(json.dumps({'schema': str(paths[0].relative_to(ROOT)), 'cases': len(cases)}))


if __name__ == '__main__':
    main()
