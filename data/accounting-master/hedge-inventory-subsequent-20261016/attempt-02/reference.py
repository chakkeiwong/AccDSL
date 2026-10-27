"""Source-bound single-batch cost, allowance and earnings reference calculation."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import re
from types import ModuleType

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
LOCK = json.loads((OUT / 'input-lock.json').read_text())['files']
HEDGE = 'data/accounting-master/repeated-rebalancing-20261016/reference.py'
FINDINGS = {'all_designated_units_received', 'inventory_recognition_satisfied',
    'acquisition_costs_complete', 'nrv_supports_adjusted_cost',
    'hedge_settlement_complete', 'settlement_at_carrying_no_fees',
    'early_settlement_permitted', 'no_further_valuation_movement',
    'no_other_cash_or_earnings', 'pretax_scope', 'interchangeable_uniform_batch',
    'no_other_inventory_or_purchases', 'same_nature_and_use'}
ACCOUNTS = ('cash', 'inventory_gross', 'inventory_allowance', 'derivative',
            'cf_reserve', 'gains', 'capital', 'revenue', 'cogs', 'nrv_expense')


class Refusal(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason


def need(ok, reason, status='rejected'):
    if not ok:
        raise Refusal(status, reason)


def rational(value):
    need(isinstance(value, str) and re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?', value), 'rational_encoding')
    q = Q(value)
    need(str(q) == value, 'rational_encoding')
    return q


def day(value):
    need(isinstance(value, str), 'date_encoding')
    try:
        d = date.fromisoformat(value)
    except ValueError:
        raise Refusal('rejected', 'date_encoding')
    need(d.isoformat() == value, 'date_encoding')
    return d


def finding(value, name):
    need(value is not None, 'missing_' + name, 'unresolved')
    need(type(value) is bool, 'finding_type')
    need(value, 'finding_' + name, 'unsupported')


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [encode(v) for v in value]
    return value


def calculate(request, resolve_bytes=None):
    result = dict(wire='HedgeInventorySubsequent/1', status='rejected', reason=None,
                  hedge=None, report=None, stages=[], journals=[], flows=[], mutations=[])
    try:
        fields = {'wire', 'operation', 'hedge', 'context', 'opening_cash',
                  'purchase', 'settlement', 'findings', 'cost_formula', 'events'}
        need(isinstance(request, dict) and set(request) == fields, 'request_shape')
        need(request['wire'] == 'HedgeInventorySubsequent/1' and request['operation'] == 'report', 'operation')
        need(request['cost_formula'] == 'weighted_average', 'cost_formula_method', 'unsupported')
        f = request['findings']
        need(isinstance(f, dict) and set(f) == FINDINGS, 'findings_shape')
        for key in sorted(FINDINGS):
            finding(f[key], key)
        reader = resolve_bytes or (lambda p: p.read_bytes())
        payloads = {}
        for item in LOCK:
            try:
                payload = reader(ROOT / item['path'])
            except OSError:
                raise Refusal('unresolved', 'input_bytes_missing')
            need(isinstance(payload, bytes), 'input_bytes_type')
            need(hashlib.sha256(payload).hexdigest() == item['sha256'], 'input_bytes_changed')
            payloads[item['path']] = payload
        # Execute the exact module bytes that passed the resolver hash checks.
        module = ModuleType('pinned_repeated_hedge')
        module.__file__ = str(ROOT / HEDGE)
        exec(compile(payloads[HEDGE], module.__file__, 'exec'), module.__dict__)
        hedge = module.calculate(request['hedge'])
        need(hedge['status'] == 'conditional_complete', 'hedge_' + str(hedge['reason']), hedge['status'])
        state = hedge['state']
        need(state['context'] == request['context'], 'context_mismatch')
        need(state['last_operation'] == 'measure', 'terminal_measurement_required')
        p, s = request['purchase'], request['settlement']
        need(isinstance(p, dict) and set(p) == {'date','quantity','unit_price','supplier_cash'}, 'purchase_shape')
        need(isinstance(s, dict) and set(s) == {'date','cash'}, 'settlement_shape')
        need(p['date'] == s['date'] == state['date'], 'terminal_date_mismatch')
        purchase_day = day(p['date'])
        quantity = sum(Q(layer['quantity']) for layer in state['layers'])
        need(rational(p['quantity']) == quantity, 'purchase_population')
        price = rational(p['unit_price'])
        need(price == Q(state['price']), 'purchase_price')
        C = rational(p['supplier_cash'])
        need(C == quantity * price and C >= 0, 'supplier_cost')
        D, R, I = (Q(state[k]) for k in ('D','reserve','profit'))
        need(rational(s['cash']) == D, 'settlement_carrying_value')
        opening = rational(request['opening_cash'])
        need(opening >= 0, 'negative_cash_input')
        K = C - R
        need(K >= 0, 'negative_inventory_method', 'unsupported')
        unit_cost = K / quantity
        books = {k: Q(0) for k in ACCOUNTS}
        books.update(cash=opening, capital=-opening, derivative=D, cf_reserve=-R, gains=-I)
        stages, journals, flows = [], [], []
        held = Q(0)

        def post(id, kind, when, entries, flow=None):
            need(sum(entries.values()) == 0, 'journal_balance')
            for account, value in entries.items():
                books[account] += value
            need(sum(books.values()) == 0, 'book_balance')
            need(books['cash'] >= 0, 'funding_required', 'unsupported')
            inventory = books['inventory_gross'] + books['inventory_allowance']
            profit = -(books['gains'] + books['revenue'] + books['cogs'] + books['nrv_expense'])
            equity = opening - books['cf_reserve'] + profit
            need(books['cash'] + inventory + books['derivative'] == equity, 'equity_bridge')
            journals.append(dict(id=id, operation=kind, date=when, entries=entries))
            if flow is not None:
                flows.append(dict(id=id, origin=flow[0], activity='operating', date=when, amount=flow[1]))
            stages.append(dict(id=id, operation=kind, date=when, quantity=held,
                gross_cost=books['inventory_gross'], allowance=-books['inventory_allowance'],
                inventory=inventory, cash=books['cash'], cumulative_pretax_profit=profit,
                pretax_equity=equity, cost_of_sales=books['cogs'], net_nrv_expense=books['nrv_expense'],
                reserve=-books['cf_reserve'], derivative=books['derivative'], books=deepcopy(books)))

        held = quantity
        post('purchase','purchase',p['date'],dict(inventory_gross=C,cash=-C),('supplier',-C))
        post('settlement','settlement',s['date'],dict(cash=D,derivative=-D),('hedge_settlement',D))
        post('basis','basis',p['date'],dict(cf_reserve=R,inventory_gross=-R))
        events = request['events']
        need(isinstance(events, list), 'events_shape')
        last = purchase_day
        ids = {'purchase','settlement','basis'}
        for event in events:
            need(isinstance(event, dict), 'event_shape')
            kind = event.get('kind')
            need(kind in ('sale','nrv'), 'event_method', 'unsupported')
            fields = ({'id','kind','date','quantity','cash','recognition_satisfied'} if kind == 'sale'
                      else {'id','kind','date','per_unit','valuation_satisfied','uniform_unit_nrv','recovery_conditions_met'})
            need(set(event) == fields, 'event_shape')
            id = event['id']
            need(isinstance(id, str) and bool(id) and id not in ids, 'event_id')
            ids.add(id)
            when = day(event['date'])
            need(when > purchase_day and when >= last, 'event_chronology')
            last = when
            need(held > 0, 'inventory_exhausted', 'unsupported')
            allowance = -books['inventory_allowance']
            if kind == 'sale':
                finding(event['recognition_satisfied'], 'sale_recognition_satisfied')
                sold, cash = rational(event['quantity']), rational(event['cash'])
                need(sold > 0 and sold <= held, 'sale_quantity')
                need(cash >= 0, 'negative_cash_input')
                gross_removed, allowance_removed = sold * unit_cost, sold * allowance / held
                held -= sold
                post(id,kind,event['date'],dict(cash=cash,revenue=-cash,cogs=gross_removed-allowance_removed,
                     inventory_gross=-gross_removed,inventory_allowance=allowance_removed),('inventory_sale',cash))
            else:
                finding(event['valuation_satisfied'], 'nrv_valuation_satisfied')
                finding(event['uniform_unit_nrv'], 'uniform_unit_nrv')
                v = rational(event['per_unit'])
                need(v >= 0, 'negative_nrv_method', 'unsupported')
                target = held * max(Q(0), unit_cost - v)
                change = target - allowance
                recovery = event['recovery_conditions_met']
                need(recovery is None or type(recovery) is bool, 'finding_type')
                if change < 0:
                    finding(recovery, 'recovery_conditions_met')
                post(id,kind,event['date'],dict(nrv_expense=change,inventory_allowance=-change))
            need(books['inventory_gross'] == held * unit_cost, 'remaining_gross_cost')
            need(0 <= -books['inventory_allowance'] <= books['inventory_gross'], 'allowance_bounds')
            need(books['cf_reserve'] == books['derivative'] == 0, 'cleared_hedge')
        receipts = sum(max(Q(0), f['amount']) for f in flows)
        payments = -sum(min(Q(0), f['amount']) for f in flows)
        need(books['cash'] - opening == receipts - payments, 'gross_cash_bridge')
        report = dict(initial_quantity=quantity, initial_adjusted_cost=K, unit_cost=unit_cost,
            original_reserve=R, original_ineffectiveness=I, closing=deepcopy(stages[-1]),
            revenue=-books['revenue'], total_inventory_expense=books['cogs']+books['nrv_expense'],
            operating_receipts=receipts, operating_payments=payments, net_cash=receipts-payments,
            tax='not_calculated', scope='cumulative_pretax_single_batch', oci_reclassification=Q(0))
        result.update(status='conditional_complete', hedge=hedge, report=encode(report),
                      stages=encode(stages), journals=encode(journals), flows=encode(flows))
    except Refusal as exc:
        result.update(status=exc.status, reason=exc.reason)
    return result
