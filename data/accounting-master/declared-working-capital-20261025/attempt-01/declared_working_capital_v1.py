"""Reconciled supported movements from a fully verified declared-program trace."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import declared_company_program_v1 as program
import declared_operating_methods_v1 as operations

PROFILE = 'DeclaredWorkingCapital/1'
FLAGS = program.FLAGS
PINS = {'declared_company_program_v1.py': '3c3a020fcc0bf6422d967725a3a4de53f8ebd89195575124b2db32156ed9e430',
        'declared_operating_methods_v1.py': '0201b1d8934e9ec40aeee301609090cc6f5d40829eb9d3dd603757f2a61a7590'}
SCOPED = ('receivables', 'inventory', 'payables', 'payroll_payable')
MOVEMENTS = {'purchase': {'inventory': 'purchases', 'payables': 'credit_purchases'},
             'deliver': {'receivables': 'credit_sales', 'inventory': 'cost_released'},
             'collect': {'receivables': 'collections'}, 'supplier_pay': {'payables': 'payments'},
             'payroll_accrue': {'payroll_payable': 'accruals'}, 'payroll_pay': {'payroll_payable': 'payments'}}
core = program.core
number = program.reports.number
fmt = program.reports.fmt
total = program.reports.total


class Unsupported(ValueError):pass


def protected():
    folder = Path(__file__).resolve().parent
    for name, expected in PINS.items():
        core.need(sha256((folder / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)
    program.protected()


def request(body, result, report_id, roles, unit_cost_pointer):
    return {'profile': PROFILE, 'program': deepcopy(body), 'result': deepcopy(result),
            'program_sha256': program.digest(body), 'result_sha256': program.digest(result),
            'report_id': report_id, 'roles': deepcopy(roles), 'unit_cost_pointer': unit_cost_pointer}


def report(body):
    try:
        protected()
        program.engine.closed(body, ['profile', 'program', 'result', 'program_sha256', 'result_sha256',
                                     'report_id', 'roles', 'unit_cost_pointer'])
        core.need(body['profile'] == PROFILE, 'schedule_profile')
        source, execution = body['program'], body['result']
        core.need(body['program_sha256'] == program.digest(source) and body['result_sha256'] == program.digest(execution), 'stale_input')
        core.need(program.verify(source, execution), 'unverified_program_result')
        core.need(execution['status'] in ['complete_provisional', 'stopped_provisional'], 'successful_prefix_required')
        program.engine.text(body['report_id'], 'report_id')
        trace = execution['trace']
        matches = [i for i, row in enumerate(trace) if row['command']['kind'] in ['report', 'carry'] and row['command']['id'] == body['report_id']]
        core.need(len(matches) == 1, 'successful_report_required')
        selected = matches[0]; row = trace[selected]
        selected_request = row['request'] if row['command']['kind'] == 'report' else row['request']['report_request']
        financial = row['result'] if row['command']['kind'] == 'report' else row['result']['report']
        opening, closing = selected_request['opening'], selected_request['closing']
        registry = operations.build(opening, source['schemas'], body['roles'], body['unit_cost_pointer'])
        by_hash = {entry['method_sha256']: kind for kind, entry in registry['entries'].items()}
        roles = body['roles']; pointer = body['unit_cost_pointer']
        _, unit_price = program.engine.binding.located(opening['memory'], pointer)
        prior_carries = [i for i in range(selected) if trace[i]['command']['kind'] == 'carry']
        start = prior_carries[-1] + 1 if prior_carries else 0
        expected_opening = trace[start - 1]['result']['next_opening'] if start else source['opening']
        core.need(core.canonical(expected_opening) == core.canonical(opening), 'period_opening_lineage')
        signs = {key: -1 if operations.CLASSES[key] == 'liability' else 1 for key in SCOPED}
        schedules = {key: {'account': roles[key], 'classification': operations.CLASSES[key],
                          'opening': fmt(signs[key] * number(opening['balances'][roles[key]])),
                          'movements': []} for key in SCOPED}
        cursor = deepcopy(opening); out_of_scope = []; event_count = 0
        for i in range(start, selected + 1):
            step = trace[i]; command = step['command']
            core.need(program.digest(cursor) == step['before_sha256'], 'trace_state_discontinuity')
            if command['kind'] == 'event':
                transition = step['result']['transition']; after = transition['after']
                key = step['result']['method_key']; entry = step['request']['registry']['entries'][key]
                method_hash = entry['method_sha256']; kind = by_hash.get(method_hash)
                found, price_after = program.engine.binding.located(after['memory'], pointer)
                if not found or price_after != unit_price:
                    raise Unsupported('unit_cost_changed:' + command['event']['id'])
                if kind is None:
                    if any(number(transition['journal'][roles[k]]) != 0 for k in SCOPED):
                        raise Unsupported('unclassified_scoped_movement:' + command['event']['id'])
                    out_of_scope.append({'event_id': command['event']['id'], 'method_sha256': method_hash,
                                         'result_sha256': program.digest(step['result']), 'scope': 'No scoped account movement or unit-price change'})
                else:
                    event_count += 1
                    for key in SCOPED:
                        signed = number(transition['journal'][roles[key]])
                        core.need(number(after['balances'][roles[key]]) - number(cursor['balances'][roles[key]]) == signed, 'scoped_journal_balance')
                        if key not in MOVEMENTS[kind]:
                            core.need(signed == 0, 'unexpected_supported_footprint'); continue
                        movement = {'category': MOVEMENTS[kind][key], 'event_id': command['event']['id'], 'date': command['event']['date'],
                                    'method_sha256': method_hash, 'debit_change': fmt(signed), 'change': fmt(signs[key] * signed),
                                    'inputs': deepcopy(command['event']['inputs']), 'request_sha256': program.digest(step['request']),
                                    'result_sha256': program.digest(step['result']), 'trace_index': i}
                        if kind in ['purchase', 'deliver']:
                            movement.update(units=deepcopy(command['event']['inputs']['units']),
                                            unit_cost={'value': unit_price, 'type': deepcopy(opening['memory_types'][pointer]),
                                                       'pointer': pointer, 'opening_sha256': program.digest(opening)})
                        schedules[key]['movements'].append(movement)
                cursor = after
            elif command['kind'] == 'report':
                cursor = step['request']['closing']
            else:
                core.need(i == selected, 'unaccounted_carry')
                cursor = step['request']['report_request']['closing']
        core.need(core.canonical(cursor) == core.canonical(closing), 'selected_closing_lineage')
        deltas = {}
        for key, schedule in schedules.items():
            values = [number(x['change']) for x in schedule['movements']]
            increase = total(v for v in values if v >= 0); decrease = -total(v for v in values if v < 0)
            closing_value = signs[key] * number(closing['balances'][roles[key]])
            delta = total(values); deltas[key] = delta
            reconciliation = total([number(schedule['opening']), delta, -closing_value])
            core.need(reconciliation == 0, 'schedule_reconciliation:' + key)
            categories = {}
            for movement in schedule['movements']:
                name = movement['category']; categories[name] = fmt(total([number(categories.get(name, '0/1')), number(movement['change'])]))
            schedule.update(increases=fmt(increase), decreases=fmt(decrease), net_change=fmt(delta), closing=fmt(closing_value),
                            categories=categories, reconciliation=fmt(reconciliation))
        contribution = total([-deltas['receivables'], -deltas['inventory'], deltas['payables'], deltas['payroll_payable']])
        profit = number(financial['income']['profit']); ocf = number(financial['cash_flows']['activities']['operating']['net'])
        return {'profile': PROFILE, **FLAGS, 'status': 'reported', 'scope': 'Selected recorded working-capital movements',
                'request_sha256': program.digest(body), 'program_sha256': body['program_sha256'], 'result_sha256': body['result_sha256'],
                'report_id': body['report_id'], 'report_sha256': program.digest(financial), 'report_trace_index': selected,
                'period': deepcopy(opening['period']), 'as_of': closing['date'], 'opening_sha256': program.digest(opening),
                'closing_sha256': program.digest(closing), 'context': deepcopy(opening['context']), 'schedules': schedules,
                'supported_events': event_count, 'out_of_scope_events': out_of_scope,
                'cash_diagnostic': {'working_capital_contribution': fmt(contribution), 'profit': fmt(profit), 'direct_operating_cash': fmt(ocf),
                                    'unexplained_by_four_account_bridge': fmt(ocf - profit - contribution),
                                    'role': 'Explanatory partial reconciliation; not a general indirect cash-flow statement'},
                'unresolved': ['Receivable ageing and impairment', 'Inventory valuation and quantity coverage', 'Payable maturity and terms',
                               'Related-party disclosures', 'Tax and source-population completeness', 'Full financial-statement note package'],
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(), 'dependency_sha256': deepcopy(PINS)}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'unsupported' if isinstance(exc, Unsupported) else 'invalid',
                'reason': str(exc)[:300] or type(exc).__name__}


def verify(body, result):
    try:
        return core.canonical(report(body)) == core.canonical(result)
    except Exception:
        return False
