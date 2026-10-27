"""Hypothetical information declarations; never assessed or admitted tax facts."""
from copy import deepcopy
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_tax_readiness_v1 as m

INTERVAL = {'start': '2024-01-01', 'end_exclusive': '2026-01-01',
            'activity_through': '2025-12-31'}


def originals():
    rows = json.loads((ROOT / 'data/accounting-master/shared-book-statements-20261024/cases.json').read_text())
    return {r['case']: r for r in rows}


def missing(name='mixed_lifecycle'):
    return m.request(originals()[name]['request'], INTERVAL, {})


def supplied(body=None):
    body = deepcopy(body if body is not None else missing())
    native = m.reports.calculate(body['report_request'])
    fields, _ = m.catalog(native, body['report_request'])
    # Deliberately hypothetical: zero declared tax bases/adjustments are only
    # structural controls, not deductions from the recorded carrying amounts.
    for key, kind in fields.items():
        value = (True if kind['kind'] == 'boolean' else '0/1' if kind['kind'] == 'rational'
                 else 'Hypothetical information-completeness control; substantive treatment unassessed')
        body['information'][key] = {'status': 'known', 'value': value,
            'provenance': {'kind': 'assumption', 'reference': 'Synthetic schema test; not actual tax facts'}}
    return body


def cases():
    out = []
    def add(name, body, status):
        out.append({'case': name, 'request': deepcopy(body), 'expected_status': status})
    add('all_information_missing', missing(), 'unresolved')
    complete = supplied(); add('hypothetical_information_supplied', complete, 'information_supplied')
    x = deepcopy(complete); del x['information']['lease/lease1/B/closing_asset_tax_base']
    add('removed_right_tax_base_missing', x, 'unresolved')
    x = deepcopy(complete); x['information']['loss_route'] = {'status': 'unknown', 'reason': 'Loss treatment not supplied'}
    add('loss_route_unknown', x, 'unresolved')
    x = deepcopy(complete); x['information']['interval_coverage']['value'] = False
    add('coverage_finding_false', x, 'unsupported')
    x = deepcopy(complete); x['information']['recognition_support'] = {'status': 'unknown', 'reason': 'Recognition support unassessed'}
    add('recognition_unknown', x, 'unresolved')
    add('stopped_prefix_with_all_declarations', supplied(missing('shared_cash_competition')), 'unresolved')
    add('unknown_lease_membership', missing('unknown_lease_membership'), 'unresolved')
    add('unbalanced_opening', missing('empty_invalid_prefix'), 'invalid')
    x = deepcopy(complete); x['report_request_sha256'] = '0' * 64
    add('forged_request_identity', x, 'invalid')
    x = deepcopy(complete); x['information']['invented_field'] = deepcopy(x['information']['rate'])
    add('undeclared_information', x, 'invalid')
    x = deepcopy(complete); x['information']['rate']['value'] = 0
    add('wrong_rational_type', x, 'invalid')
    x = deepcopy(complete); x['information']['rate']['value'] = '-1/4'
    add('negative_rate', x, 'invalid')
    x = deepcopy(complete); x['information']['rate']['value'] = '5/4'
    add('no_invented_rate_cap', x, 'information_supplied')
    x = deepcopy(complete); x['information']['interval_coverage']['value'] = 1
    add('integer_not_boolean', x, 'invalid')
    x = deepcopy(complete); del x['information']['regime']['provenance']
    add('missing_provenance', x, 'invalid')
    x = deepcopy(complete); x['information']['regime']['provenance'] = {
        'kind': 'source_reference', 'reference': 'unverified:local-fixture-reference'}
    add('reference_retained_not_admitted', x, 'information_supplied')
    x = deepcopy(complete); x['information']['regime']['value'] = 'unknown'
    add('unknown_not_known_text', x, 'invalid')
    x = deepcopy(complete); x['interval']['activity_through'] = x['interval']['end_exclusive']
    add('exclusive_endpoint_not_last_day', x, 'invalid')
    x = deepcopy(complete); x['interval']['start'] = '2025-01-01'
    add('missing_interval_opening', x, 'invalid')
    x = deepcopy(complete); x['interval'].update(end_exclusive='2025-01-01', activity_through='2024-12-31')
    add('event_on_exclusive_endpoint', x, 'invalid')
    x = deepcopy(complete); x['interval'].update(end_exclusive='2027-01-01', activity_through='2026-12-31')
    add('interval_exceeds_execution_window', x, 'invalid')
    x = missing(); x['report_request'] = m.reports.request(x['report_request']['opening'], x['report_request']['events'][:3])
    x['report_request_sha256'] = m.book.digest(x['report_request'])
    x['interval'].update(end_exclusive='2025-01-01', activity_through='2024-12-31')
    add('explicit_first_year_interval', supplied(x), 'information_supplied')
    return out
