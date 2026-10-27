"""Verified financing movements with accrual coverage kept separate."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path

import declared_company_program_v2 as program
import declared_financing_methods_v1 as financing

PROFILE = 'DeclaredFinancingSchedules/1'
FLAGS = program.FLAGS
core = program.core
number, fmt, total = program.reports.number, program.reports.fmt, program.reports.total
PINS = {'declared_company_program_v2.py': 'aa69e8bfb4628ddff5867bb243996b32d43c56119bd61f2baf1b87b23d5d1633', 'declared_financing_methods_v1.py': 'c26efd02a2c3e63fe440af68db23d7c9f63185662dbd1dc07b570a07511f1842'}  # Reviewed exact dependencies.
SCOPED = ('debt', 'interest_payable', 'capital', 'retained', 'dividend_payable')
MOVEMENTS = {'debt_issue': {'debt': 'issued'}, 'debt_redeem': {'debt': 'repaid'},
             'interest_accrue': {'interest_payable': 'accrued'},
             'interest_pay': {'interest_payable': 'paid'},
             'equity_issue': {'capital': 'contributions'},
             'dividend_declare': {'retained': 'declared_dividends', 'dividend_payable': 'declared'},
             'dividend_pay': {'dividend_payable': 'paid'}}


class Unsupported(ValueError):
    pass


def protected():
    folder = Path(__file__).resolve().parent
    core.need(set(PINS) == {'declared_company_program_v2.py', 'declared_financing_methods_v1.py'},
              'dependency_population')
    for name, expected in PINS.items():
        core.need(sha256((folder / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)
    program.protected()


def request(body, result, report_id, roles, cursor_pointer, debt_pointer, policy, intervals):
    return {'profile': PROFILE, 'program': deepcopy(body), 'result': deepcopy(result),
            'program_sha256': program.digest(body), 'result_sha256': program.digest(result),
            'report_id': report_id, 'roles': deepcopy(roles), 'cursor_pointer': cursor_pointer,
            'debt_pointer': debt_pointer, 'policy': deepcopy(policy), 'intervals': deepcopy(intervals)}


def leaf(book, pointer):
    found, value = program.engine.binding.located(book['memory'], pointer)
    core.need(found, 'missing_financing_memory')
    return value


def report(body):
    try:
        protected()
        program.engine.closed(body, ['profile', 'program', 'result', 'program_sha256', 'result_sha256',
            'report_id', 'roles', 'cursor_pointer', 'debt_pointer', 'policy', 'intervals'])
        core.need(body['profile'] == PROFILE, 'schedule_profile')
        source, execution = body['program'], body['result']
        core.need(body['program_sha256'] == program.digest(source) and
                  body['result_sha256'] == program.digest(execution), 'stale_input')
        core.need(program.verify(source, execution), 'unverified_program_result')
        core.need(execution['status'] in ['complete_provisional', 'stopped_provisional'], 'successful_prefix_required')
        program.engine.text(body['report_id'], 'report_id')
        trace = execution['trace']
        matches = [i for i, row in enumerate(trace) if row['command']['kind'] in ['report', 'carry']
                   and row['command']['id'] == body['report_id']]
        core.need(len(matches) == 1, 'successful_report_required')
        selected = matches[0]
        row = trace[selected]
        selected_request = row['request'] if row['command']['kind'] == 'report' else row['request']['report_request']
        financial = row['result'] if row['command']['kind'] == 'report' else row['result']['report']
        opening, closing = selected_request['opening'], selected_request['closing']
        roles, cp, dp = body['roles'], body['cursor_pointer'], body['debt_pointer']
        registry = financing.build(source['opening'], source['schemas'], roles, cp, dp,
                                   body['policy'], body['intervals'])
        by_hash = {}
        for key, entry in registry['entries'].items():
            interval = None
            kind = key
            if key.startswith('interest_accrue.'):
                interval = body['intervals'][int(key.rsplit('.', 1)[1])-1]
                kind = 'interest_accrue'
            by_hash[entry['method_sha256']] = (kind, interval)
        prior_carries = [i for i in range(selected) if trace[i]['command']['kind'] == 'carry']
        start = prior_carries[-1] + 1 if prior_carries else 0
        expected_opening = trace[start-1]['result']['next_opening'] if start else source['opening']
        core.need(core.canonical(expected_opening) == core.canonical(opening), 'period_opening_lineage')
        core.need(leaf(opening, dp) == opening['balances'][roles['debt']], 'opening_principal_mismatch')
        opening_cursor = leaf(opening, cp)
        core.scalar(opening_cursor, 'date')
        cursor = deepcopy(opening)
        schedules = {k: {'account': roles[k], 'classification': financing.CLASSES[k],
                         'opening': fmt(-number(opening['balances'][roles[k]])), 'movements': []}
                     for k in SCOPED}
        intervals, cash, other_events = [], [], []
        interest_expense = number('0/1')
        for i in range(start, selected+1):
            step, command = trace[i], trace[i]['command']
            core.need(program.digest(cursor) == step['before_sha256'], 'trace_state_discontinuity')
            if command['kind'] != 'event':
                core.need(command['kind'] == 'report' or i == selected, 'unaccounted_carry')
                cursor = step['request']['closing'] if command['kind'] == 'report' else step['request']['report_request']['closing']
                continue
            transition = step['result']['transition']
            after = transition['after']
            entry = step['request']['registry']['entries'][step['result']['method_key']]
            method_hash = entry['method_sha256']
            meaning = by_hash.get(method_hash)
            scoped_accounts = {roles[k] for k in (*SCOPED, 'interest')}
            if meaning is None:
                gross = transition['monetary']['diagnostics']['postings']
                if any(entry['method']['account_map'][p['account']] in scoped_accounts and
                       number(p['binding']['value']) != 0 for p in gross):
                    raise Unsupported('unclassified_gross_financing_movement:' + command['event']['id'])
                if any(number(transition['journal'][a]) != 0 for a in scoped_accounts):
                    raise Unsupported('unclassified_financing_movement:' + command['event']['id'])
                if leaf(after, cp) != leaf(cursor, cp) or leaf(after, dp) != leaf(cursor, dp):
                    raise Unsupported('unclassified_financing_memory_change:' + command['event']['id'])
                other_events.append({'event_id': command['event']['id'], 'method_sha256': method_hash,
                                     'result_sha256': program.digest(step['result'])})
            else:
                kind, interval = meaning
                lineage = {'event_id': command['event']['id'], 'date': command['event']['date'],
                           'method_sha256': method_hash, 'inputs': deepcopy(command['event']['inputs']),
                           'request_sha256': program.digest(step['request']),
                           'result_sha256': program.digest(step['result']), 'trace_index': i}
                for key in SCOPED:
                    signed = number(transition['journal'][roles[key]])
                    core.need(number(after['balances'][roles[key]]) - number(cursor['balances'][roles[key]]) == signed,
                              'scoped_journal_balance')
                    if key not in MOVEMENTS[kind]:
                        core.need(signed == 0, 'unexpected_supported_footprint')
                        continue
                    schedules[key]['movements'].append({**deepcopy(lineage), 'category': MOVEMENTS[kind][key],
                                                       'debit_change': fmt(signed), 'change': fmt(-signed)})
                expense = number(transition['journal'][roles['interest']])
                interest_expense += expense
                if kind == 'interest_accrue':
                    a, b = (core.scalar(interval[k], 'date') for k in ['start', 'end_exclusive'])
                    core.need(leaf(cursor, cp) == interval['start'] and leaf(after, cp) == interval['end_exclusive'],
                              'interval_memory_lineage')
                    core.need(command['event']['date'] == (b-timedelta(days=1)).isoformat(), 'interval_event_date')
                    principal = -number(cursor['balances'][roles['debt']])
                    expected = principal * number(body['policy']['annual_rate']) * (b-a).days / 365
                    core.need(expense == expected, 'independent_interest_amount')
                    intervals.append({**deepcopy(lineage), **deepcopy(interval),
                                      'days': (b-a).days, 'principal': fmt(principal),
                                      'interest': fmt(expense)})
                else:
                    core.need(expense == 0 and leaf(after, cp) == leaf(cursor, cp), 'nonaccrual_clock_unchanged')
                cash.extend([{**deepcopy(lineage), **deepcopy(f)} for f in transition['flows']])
            core.need(leaf(after, dp) == after['balances'][roles['debt']], 'principal_memory_mismatch')
            cursor = after
        core.need(core.canonical(cursor) == core.canonical(closing), 'selected_closing_lineage')
        for key, schedule in schedules.items():
            values = [number(x['change']) for x in schedule['movements']]
            increase = total(v for v in values if v >= 0)
            decrease = -total(v for v in values if v < 0)
            end = -number(closing['balances'][roles[key]])
            residual = number(schedule['opening']) + increase - decrease - end
            core.need(residual == 0, 'schedule_reconciliation:' + key)
            categories = {}
            for row in schedule['movements']:
                category = row['category']
                categories[category] = fmt(number(categories.get(category, '0/1')) + number(row['change']))
            schedule.update(increases=fmt(increase), decreases=fmt(decrease), closing=fmt(end),
                            categories=categories, reconciliation=fmt(residual))
        expected_end = (core.scalar(closing['date'], 'date') + timedelta(days=1)).isoformat()
        actual_end = leaf(closing, cp)
        core.scalar(actual_end, 'date')
        continuity = opening_cursor
        for interval in intervals:
            core.need(interval['start'] == continuity, 'coverage_discontinuity')
            continuity = interval['end_exclusive']
        core.need(continuity == actual_end, 'coverage_cursor_mismatch')
        needs = []
        if opening_cursor != opening['period']['start']:
            needs.append({'kind': 'opening_coverage_mismatch', 'period_start': opening['period']['start'],
                          'opening_cursor': opening_cursor})
        if actual_end < expected_end:
            needs.append({'kind': 'unaccrued_interval', 'start': actual_end, 'end_exclusive': expected_end})
        elif actual_end > expected_end:
            needs.append({'kind': 'cursor_after_report', 'cursor': actual_end, 'expected_end': expected_end})
        coverage = {'opening_cursor': opening_cursor, 'closing_cursor': actual_end,
                    'expected_end_exclusive': expected_end, 'intervals': intervals,
                    'complete_for_selected_period': not needs, 'needs': needs,
                    'scope': 'Executed synthetic intervals only; not fiscal or source completeness'}
        return {'profile': PROFILE, **FLAGS, 'status': 'reported', 'report_id': body['report_id'],
                'request_sha256': program.digest(body), 'program_sha256': body['program_sha256'],
                'result_sha256': body['result_sha256'], 'report_sha256': program.digest(financial),
                'report_trace_index': selected, 'period': deepcopy(opening['period']), 'as_of': closing['date'],
                'opening_sha256': program.digest(opening), 'closing_sha256': program.digest(closing),
                'context': deepcopy(opening['context']), 'schedules': schedules,
                'interest_expense': fmt(interest_expense), 'interest_coverage': coverage,
                'financing_cash': {'movements': cash, 'by_activity': {
                    activity: fmt(total(number(f['amount']) for f in cash if f['activity'] == activity))
                    for activity in ['operating', 'investing', 'financing']}},
                'out_of_scope_events': other_events,
                'unresolved': ['Contract maturity and covenants', 'Fees and effective-interest valuation',
                               'Outstanding shares and lawful distributions', 'Tax and related parties',
                               'Source population and complete financial-statement notes'],
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'dependency_sha256': deepcopy(PINS)}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'unsupported' if isinstance(exc, Unsupported) else 'invalid',
                'reason': str(exc)[:300] or type(exc).__name__}


def verify(body, result):
    try:
        return core.canonical(report(body)) == core.canonical(result)
    except Exception:
        return False
