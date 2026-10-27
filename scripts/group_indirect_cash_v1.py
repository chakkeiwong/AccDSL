"""Conditional group bridge from exact legal traces and explicit paired flows."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import declared_indirect_cash_v2 as indirect
import group_period_report_v1 as group

PROFILE = 'GroupIndirectCash/1'
FLAGS = {**group.FLAGS, 'classification_admission': False}
PINS = {
    'declared_indirect_cash_v2.py': '5b8a9c2d74a834a7d5cc7abaa82c80a61da9459cc8fcb349ba04645017aef3e9',
    'group_period_report_v1.py': '13cef76b375c0e8ba44ef22db8950606dcbd9ba8b492a44fb9fb6c4377ab1566',
}
core = group.core
number, fmt, total = group.number, group.fmt, group.total
MAX_BYTES = 48 * 1024 * 1024
ITEMS = ('profit', 'working_capital', 'noncash_profit', 'nonoperating_profit_adjustment')


def protected():
    for name, expected in PINS.items():
        core.need(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == expected,
                  'dependency_hash:' + name)


def request(group_request, group_result, legal):
    return {'profile': PROFILE, 'group_request': deepcopy(group_request),
            'group_result': deepcopy(group_result),
            'group_request_sha256': core.digest(group_request),
            'group_result_sha256': core.digest(group_result), 'legal': deepcopy(legal)}


def report(body):
    try:
        protected()
        core.closed(body, ['profile', 'group_request', 'group_result',
                           'group_request_sha256', 'group_result_sha256', 'legal'], 'group_indirect_request')
        core.need(body['profile'] == PROFILE, 'group_indirect_profile')
        core.need(len(core.canonical(body)) <= MAX_BYTES, 'group_indirect_size_limit')
        source, result = body['group_request'], body['group_result']
        core.need(body['group_request_sha256'] == core.digest(source) and
                  body['group_result_sha256'] == core.digest(result), 'stale_group_input')
        core.need(group.verify(source, result) and result['status'] == 'period_reported',
                  'unverified_group_report')
        owners = set(source['legal_reports'])
        legal = body['legal']
        core.need(type(legal) is dict and set(legal) == owners, 'exact_legal_bridge_population')
        checked = {}
        for owner in sorted(owners):
            row = legal[owner]
            core.closed(row, ['request', 'result'], 'legal_bridge_record')
            req, res = row['request'], row['result']
            core.need(indirect.verify(req, res) and res['status'] == 'explained_provisional',
                      'unverified_legal_bridge:' + owner)
            opening = source['opening']['books'][owner]
            closing = source['closing']['books'][owner]
            core.need(res['opening_sha256'] == core.digest(opening) and
                      res['closing_sha256'] == core.digest(closing), 'legal_book_binding:' + owner)
            core.need(res['period'] == opening['period'] and res['as_of'] == closing['date'],
                      'legal_time_binding:' + owner)
            core.need(core.canonical(res['financial_report']) == core.canonical(result['legal_reports'][owner]),
                      'legal_report_binding:' + owner)
            _, _, report_request, _ = indirect.period(req['result'], req['report_id'])
            core.need(core.canonical(report_request) == core.canonical(source['legal_reports'][owner]),
                      'legal_report_request_binding:' + owner)
            checked[owner] = deepcopy(row)
        items = {k: total(number(row['result']['items'][k]) for row in checked.values()) for k in ITEMS}
        raw = total(number(row['result']['direct_operating_cash']) for row in checked.values())
        core.need(total(items.values()) == raw, 'raw_legal_bridge_reconciliation')
        core.need(raw == number(result['raw_cash_flows']['activities']['operating']['net']),
                  'raw_group_cash_binding')
        corrections = []
        for pair in result['internal_cash_pairs']:
            removed = total(number(pair[side + '_flow']['amount']) for side in ['payer', 'payee']
                            if pair[side + '_flow']['activity'] == 'operating')
            corrections.append({'pair_id': pair['id'], 'pair': deepcopy(pair),
                                'removed_operating_cash': fmt(removed), 'adjustment': fmt(-removed)})
        adjustment = total(number(row['adjustment']) for row in corrections)
        operating = total([raw, adjustment])
        direct = number(result['cash_flows']['activities']['operating']['net'])
        core.need(operating == direct, 'group_indirect_reconciliation')
        core.need(items['profit'] == number(result['equity']['profit']) and
                  items['profit'] == number(result['closing_worksheet']['adjusted_totals']['profit']),
                  'unchanged_group_profit_required')
        return {'profile': PROFILE, **FLAGS, 'status': 'group_explained_provisional',
                'request_sha256': core.digest(body),
                'group_request_sha256': body['group_request_sha256'],
                'group_result_sha256': body['group_result_sha256'],
                'group_report': deepcopy(result), 'legal': checked,
                'items': {**{k: fmt(v) for k, v in items.items()},
                          'internal_operating_cash_adjustment': fmt(adjustment),
                          'indirect_operating_cash': fmt(operating)},
                'raw_legal_operating_cash': fmt(raw), 'direct_group_operating_cash': fmt(direct),
                'internal_cash_adjustments': corrections,
                'reconciliations': {'raw_legal_bridge': '0/1', 'group_operating_cash': '0/1', 'profit': '0/1'},
                'scope': 'Two compatible legal traces; supplied full ownership and paired internal cash; no profit eliminations',
                'unresolved': ['Truth and completeness of internal-flow pairs and classifications',
                               'Actual source, accounting and control admission',
                               'NCI, goodwill, FX, tax and intragroup profit methods',
                               'Complete event population and consolidated notes'],
                'dependency_sha256': deepcopy(PINS),
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid',
                'reason': str(exc)[:350] or type(exc).__name__}


def verify(body, result):
    try:
        core.need(len(core.canonical(result)) <= MAX_BYTES, 'group_indirect_result_size_limit')
        return core.canonical(report(body)) == core.canonical(result)
    except Exception:
        return False
