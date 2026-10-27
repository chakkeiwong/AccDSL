"""Conditional profit-to-operating-cash explanation from verified event traces."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import declared_company_program_v2 as program

PROFILE = 'DeclaredIndirectCash/2'
POLICY = 'DeclaredIndirectCashPolicy/2'
PIN = 'aa69e8bfb4628ddff5867bb243996b32d43c56119bd61f2baf1b87b23d5d1633'
core = program.core
FLAGS = {**program.FLAGS, 'classification_admission': False}
number, fmt, total = program.reports.number, program.reports.fmt, program.reports.total
CATEGORIES = ('working_capital', 'noncash_profit', 'nonoperating', 'owner')


class Unsupported(ValueError):
    pass


def protected():
    core.need(sha256(Path(program.__file__).read_bytes()).hexdigest() == PIN, 'indirect_program_dependency')
    program.protected()


def request(body, result, report_id, policy):
    return {'profile': PROFILE, 'program': deepcopy(body), 'result': deepcopy(result),
            'program_sha256': core.digest(body), 'result_sha256': core.digest(result),
            'report_id': report_id, 'policy': deepcopy(policy)}


def period(execution, report_id):
    trace = execution['trace']
    matches = [i for i, row in enumerate(trace) if row['command']['kind'] in ['report', 'carry']
               and row['command']['id'] == report_id]
    core.need(len(matches) == 1, 'successful_report_required')
    selected = matches[0]
    row = trace[selected]
    request_ = row['request'] if row['command']['kind'] == 'report' else row['request']['report_request']
    financial = row['result'] if row['command']['kind'] == 'report' else row['result']['report']
    carries = [i for i in range(selected) if trace[i]['command']['kind'] == 'carry']
    start = carries[-1] + 1 if carries else 0
    return start, selected, request_, financial


def report(body):
    try:
        protected()
        core.closed(body, ['profile', 'program', 'result', 'program_sha256', 'result_sha256',
                           'report_id', 'policy'], 'indirect_request')
        core.need(body['profile'] == PROFILE, 'indirect_profile')
        source, execution, policy = body['program'], body['result'], body['policy']
        program.engine.memory.bounded(policy)
        core.need(len(core.canonical(source)) <= core.MAX_BYTES, 'program_size_limit')
        core.need(len(core.canonical(execution)) <= program.MAX_TRACE_BYTES + 2 * core.MAX_BYTES, 'result_size_limit')
        core.need(body['program_sha256'] == core.digest(source) and
                  body['result_sha256'] == core.digest(execution), 'stale_input')
        core.need(program.verify(source, execution), 'unverified_program_result')
        core.need(execution['status'] in ['complete_provisional', 'stopped_provisional'], 'successful_prefix_required')
        program.engine.text(body['report_id'], 'report_id')
        core.closed(policy, ['profile', 'context', 'methods'], 'indirect_policy')
        core.need(policy['profile'] == POLICY and policy['context'] == source['opening']['context'], 'indirect_policy_context')
        core.need(type(policy['methods']) is dict and len(policy['methods']) <= program.MAX_COMMANDS, 'policy_method_limit')
        start, selected, report_request, financial = period(execution, body['report_id'])
        opening, closing = report_request['opening'], report_request['closing']
        trace = execution['trace']
        expected_opening = trace[start - 1]['result']['next_opening'] if start else source['opening']
        core.need(core.canonical(opening) == core.canonical(expected_opening), 'period_opening_lineage')
        used = {row['request']['registry']['entries'][row['result']['method_key']]['method_sha256']
                for row in trace[start:selected + 1] if row['command']['kind'] == 'event'}
        core.need(set(policy['methods']) == used, 'exact_policy_methods')
        current = deepcopy(opening)
        rows = []
        for i in range(start, selected + 1):
            row = trace[i]
            core.need(core.digest(current) == row['before_sha256'], 'trace_state_discontinuity')
            if row['command']['kind'] != 'event':
                core.need(row['command']['kind'] == 'report' or i == selected, 'unaccounted_carry')
                current = row['request']['closing'] if row['command']['kind'] == 'report' else row['request']['report_request']['closing']
                continue
            transition = row['result']['transition']
            entry = row['request']['registry']['entries'][row['result']['method_key']]
            method_hash = entry['method_sha256']
            classification = policy['methods'][method_hash]
            core.closed(classification, ['accounts', 'profit_accounts', 'premise'], 'method_classification')
            program.engine.text(classification['premise'], 'classification_premise')
            account_map = classification['accounts']
            core.need(type(account_map) is dict, 'classification_accounts')
            gross = transition['monetary']['diagnostics']['postings']
            required = {entry['method']['account_map'][p['account']] for p in gross}
            required = {a for a in required if a != current['cash_account'] and
                        current['accounts'][a]['classification'] not in ['income', 'expense']}
            if set(account_map) != required:
                raise Unsupported('exact_gross_posting_classification:' + row['command']['event']['id'])
            profit_map = classification['profit_accounts']
            profit_required = {entry['method']['account_map'][p['account']] for p in gross
                               if current['accounts'][entry['method']['account_map'][p['account']]]['classification'] in ['income', 'expense']}
            core.need(type(profit_map) is dict and set(profit_map) == profit_required, 'exact_profit_posting_classification')
            core.need(all(v in ['operating', 'nonoperating'] for v in profit_map.values()), 'profit_category')
            for account, category in account_map.items():
                core.need(category in CATEGORIES, 'adjustment_category')
                is_equity = current['accounts'][account]['classification'] == 'equity'
                core.need((category == 'owner') == is_equity, 'owner_classification')
            sums = {k: number('0/1') for k in CATEGORIES}
            profit = number('0/1')
            removed_profit = number('0/1')
            contributions = []
            for posting in gross:
                account = entry['method']['account_map'][posting['account']]
                amount = number(posting['binding']['value'])
                kind = current['accounts'][account]['classification']
                if account == current['cash_account']:
                    category = 'cash'
                elif kind in ['income', 'expense']:
                    category = 'profit_' + profit_map[account]
                    profit = total([profit, -amount])
                    if profit_map[account] == 'nonoperating':
                        removed_profit = total([removed_profit, amount])
                else:
                    category = account_map[account]
                    sums[category] = total([sums[category], amount])
                contributions.append({'posting_id': posting['id'], 'account': account,
                                      'category': category, 'debit_change': fmt(amount)})
            activities = {k: total(number(f['amount']) for f in transition['flows'] if f['activity'] == k)
                          for k in ['operating', 'investing', 'financing']}
            excluded = total([sums['nonoperating'], sums['owner']])
            exclusion_check = total([excluded, removed_profit, activities['investing'], activities['financing']])
            if exclusion_check != 0:
                raise Unsupported('nonoperating_reconciliation:' + row['command']['event']['id'])
            working = -sums['working_capital']
            noncash = -sums['noncash_profit']
            indirect = total([profit, working, noncash, removed_profit])
            core.need(indirect == activities['operating'], 'event_indirect_reconciliation')
            rows.append({'event_id': row['command']['event']['id'], 'date': row['command']['event']['date'],
                         'method_sha256': method_hash, 'classification': deepcopy(classification),
                         'trace_index': i, 'before_sha256': row['before_sha256'],
                         'after_sha256': row['after_sha256'], 'request_sha256': core.digest(row['request']),
                         'result_sha256': core.digest(row['result']), 'gross_postings': contributions,
                         'profit': fmt(profit), 'working_capital': fmt(working), 'noncash_profit': fmt(noncash),
                         'nonoperating_profit_adjustment': fmt(removed_profit),
                         'excluded_balance_sheet_change': fmt(excluded),
                         'cash': {k: fmt(v) for k, v in activities.items()},
                         'nonoperating_reconciliation': fmt(exclusion_check),
                         'indirect_operating_cash': fmt(indirect)})
            current = transition['after']
        core.need(core.canonical(current) == core.canonical(closing), 'selected_closing_lineage')
        totals = {k: total(number(r[k]) for r in rows)
                  for k in ['profit', 'working_capital', 'noncash_profit', 'nonoperating_profit_adjustment', 'indirect_operating_cash']}
        direct = number(financial['cash_flows']['activities']['operating']['net'])
        core.need(totals['profit'] == number(financial['income']['profit']), 'period_profit_reconciliation')
        core.need(totals['indirect_operating_cash'] == direct, 'period_indirect_reconciliation')
        core.need(total([totals['profit'], totals['working_capital'], totals['noncash_profit'], totals['nonoperating_profit_adjustment']]) == direct,
                  'period_bridge_reconciliation')
        return {'profile': PROFILE, **FLAGS, 'status': 'explained_provisional',
                'request_sha256': core.digest(body), 'program_sha256': body['program_sha256'],
                'result_sha256': body['result_sha256'], 'policy_sha256': core.digest(policy),
                'report_id': body['report_id'], 'report_sha256': core.digest(financial),
                'opening_sha256': core.digest(opening), 'closing_sha256': core.digest(closing),
                'period': deepcopy(opening['period']), 'as_of': closing['date'],
                'items': {k: fmt(v) for k, v in totals.items()}, 'direct_operating_cash': fmt(direct),
                'events': rows, 'policy': deepcopy(policy), 'financial_report': deepcopy(financial),
                'reconciliations': {'profit': '0/1', 'indirect_cash': '0/1'},
                'scope': 'Selected verified recorded period under explicit method/account classification',
                'unresolved': ['Accounting validity and completeness of classifications', 'Actual-source admission',
                               'Event-population completeness', 'Full note package',
                               'Mixed classification within one account and method'],
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'program_dependency_sha256': PIN}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'unsupported' if isinstance(exc, Unsupported) else 'invalid',
                'reason': str(exc)[:350] or type(exc).__name__}


def verify(body, result):
    try:
        return core.canonical(report(body)) == core.canonical(result)
    except Exception:
        return False
