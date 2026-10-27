"""Independent documentary arithmetic and protocol checks; no builder imports."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as F
from pathlib import Path
import hashlib
import importlib.metadata
import json
import math
import subprocess
import time
from jsonschema import Draft202012Validator, FormatChecker
from additional_checks import calculate, check_component

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
ASSETS = 'cash wip finished_goods ppe goodwill rou dta pension_asset receivable inventory return_recovery reimbursement'.split()
LIABS = 'payable lease_liability pension_liability provision dtl contract_liability refund_liability'.split()
PROFIT = 'income expense finance_expense tax_expense'.split()
PROFIT += ['product_revenue','service_revenue','commission_revenue','reimbursement_income',
    'provision_gain','cost_of_sales','service_expense','assurance_expense']
OCI = ['oci_revaluation', 'oci_pension']
CASH = ['operating', 'investing', 'financing', 'unclassified']

def encode(v): return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
def decode(v):
    if isinstance(v, dict):
        if set(v) == {'n', 'd'}:
            n, d = int(v['n']), int(v['d'])
            assert d > 0 and math.gcd(n, d) == 1
            return F(n, d)
        return {k: decode(x) for k, x in v.items()}
    if isinstance(v, list): return [decode(x) for x in v]
    assert not isinstance(v, float)
    return v
def refs(v):
    if isinstance(v, dict):
        if set(v) == {'kind', 'schema', 'digest'}: yield v
        else:
            for x in v.values(): yield from refs(x)
    elif isinstance(v, list):
        for x in v: yield from refs(x)
def blobs(v):
    if isinstance(v, dict):
        if v.get('kind') == 'blob': yield v
        else:
            for x in v.values(): yield from blobs(x)
    elif isinstance(v, list):
        for x in v: yield from blobs(x)

class Refusal(Exception):
    def __init__(self, code, disposition='rejected'):
        self.code, self.disposition = code, disposition

def require(ok, code, disposition='rejected'):
    if not ok: raise Refusal(code, disposition)

def derive(tag, original, method, p):
    """Compute from component/event facts only, never proposed lines/closing values."""
    if method.split('.')[0] in ['returns','assurance','service','distinct','integrated','mixed','agency','joint','byproduct','supplier']:
        return calculate(original, method, p, require)
    c = deepcopy(original); j = {}; cash = {}
    def line(account, amount): j[account] = j.get(account, F(0)) + amount
    if method == 'production.accumulate':
        require(c['phase'] == 'opening', 'production_order')
        require(p['started'] >= 0 and p['material_cost'] >= 0 and p['conversion_cost'] >= 0, 'negative_production_input')
        c['started'] += p['started']; c['current_material'] += p['material_cost']; c['current_conversion'] += p['conversion_cost']
        cost = p['material_cost'] + p['conversion_cost']; c['wip_cost'] += cost; c['phase'] = 'accumulated'
        c['closing_units'] = c['closing_fraction'] = None
        line('wip', cost); line('payable', -cost)
    elif method == 'production.complete':
        require(p['rounding'] == 'exact', 'rounding_profile_unsupported', 'unsupported')
        require(c['phase'] == 'accumulated', 'production_order')
        completed, ending, fraction = p['completed'], p['closing_units'], p['closing_fraction']
        require(completed >= 0 and ending >= 0 and 0 <= fraction <= 1 and 0 <= c['opening_fraction'] <= 1, 'production_fraction')
        require(c['opening_units'] + c['started'] == completed + ending, 'physical_units_mismatch')
        total = c['opening_material'] + c['opening_conversion'] + c['current_material'] + c['current_conversion']
        require(total == c['wip_cost'], 'production_cost_pool_mismatch')
        if c['policy'] == 'fifo':
            require(completed >= c['opening_units'] and c['started'] > 0, 'fifo_scope_unsupported', 'unsupported')
            effort = c['opening_units'] * (1 - c['opening_fraction']) + completed - c['opening_units'] + ending * fraction
            require(effort > 0, 'zero_conversion_effort', 'partial')
            material_rate = c['current_material'] / c['started']; conversion_rate = c['current_conversion'] / effort
            cost = c['opening_material'] + c['opening_conversion'] + c['opening_units'] * (1 - c['opening_fraction']) * conversion_rate
            cost += (completed - c['opening_units']) * (material_rate + conversion_rate)
        else:
            require(completed + ending > 0 and completed + ending * fraction > 0, 'zero_conversion_effort', 'partial')
            cost = completed * ((c['opening_material'] + c['current_material']) / (completed + ending)
                + (c['opening_conversion'] + c['current_conversion']) / (completed + ending * fraction))
        c.update(completed=completed, closing_units=ending, closing_fraction=fraction,
                 wip_cost=total - cost, finished_cost=c['finished_cost'] + cost, phase='completed')
        line('wip', -cost); line('finished_goods', cost)
    elif method == 'production.loss':
        require(c['phase'] == 'unallocated', 'production_order')
        require(c['full_effort'] and c['no_salvage'] and c['no_fixed_overhead'], 'loss_model_unsupported', 'unsupported')
        require(p['normal_output_admitted_before_observation'], 'normal_yield_unresolved', 'partial')
        require(0 <= p['good_output'] <= c['normal_output'] <= c['input_units'] and c['normal_output'] > 0, 'loss_scope_unsupported', 'unsupported')
        unit = c['cost_pool'] / c['normal_output']; good = p['good_output'] * unit
        abnormal = (c['normal_output'] - p['good_output']) * unit
        c.update(good_output=p['good_output'], finished_cost=good, abnormal_cost=abnormal, phase='allocated')
        line('wip', -c['cost_pool']); line('finished_goods', good); line('expense', abnormal)
    elif method == 'inspection.replace':
        require(p['old_allocation_known'] and p['old_carrying_current'], 'old_component_measurement_unresolved', 'partial')
        require(p['qualifies'], 'inspection_recognition_failed')
        require(p['new_cost'] >= 0 and p['new_life'] > 0, 'invalid_inspection_measurement')
        old = c['inspection_carrying']; c.update(inspection_id=p['new_inspection_id'], inspection_carrying=p['new_cost'], inspection_life=p['new_life'])
        line('expense', old); line('ppe', p['new_cost'] - old); line('cash', -p['new_cost']); cash['investing'] = -p['new_cost']
    elif method == 'inspection.consume':
        require(c['zero_residual'] and 0 < p['years'] <= min(c['physical_life'], c['inspection_life']), 'depreciation_scope_unsupported', 'unsupported')
        expense = F(0)
        for part in ['physical', 'inspection']:
            dep = c[part + '_carrying'] * p['years'] / c[part + '_life']
            c[part + '_carrying'] -= dep; c[part + '_life'] -= p['years']; expense += dep
        line('expense', expense); line('ppe', -expense)
    elif method == 'lease.reduce':
        require(c['homogeneous'] and p['same_remaining_term'] and p['no_termination_fee'], 'rights_allocation_unsupported', 'unsupported')
        q = p['surrendered_fraction']; require(0 < q < 1 and p['new_rate'] > -1 and p['new_payment'] >= 0, 'invalid_lease_parameters')
        require(c['periods_remaining'] == 1, 'lease_period_scope', 'unsupported')
        old_a, old_l = c['rou'], c['liability']; new_l = p['new_payment'] / (1 + p['new_rate'])
        new_a = old_a * (1 - q) + new_l - old_l * (1 - q)
        require(new_a >= 0, 'negative_rou_requires_separate_method', 'unsupported')
        c.update(rou=new_a, liability=new_l, remaining_payment=p['new_payment'], rate=p['new_rate'])
        line('lease_liability', old_l - new_l); line('rou', new_a - old_a); line('income', -q * (old_l - old_a))
    elif method == 'lease.usage':
        require(p['non_index_variable'] and not p['capitalization_required'], 'usage_method_unsupported', 'unsupported')
        require(p['units'] >= 0 and p['unit_fee'] >= 0, 'negative_usage')
        cost = p['units'] * p['unit_fee']; c['usage_due'] += cost
        line('expense', cost); line('payable', -cost)
    elif method == 'lease.mature':
        require(p['one_period_elapsed'] and c['periods_remaining'] == 1, 'lease_period_scope', 'unsupported')
        interest = c['liability'] * c['rate']
        require(p['cash_payment'] == c['remaining_payment'] == c['liability'] + interest, 'payment_measurement_mismatch')
        line('expense', c['rou']); line('rou', -c['rou']); line('finance_expense', interest)
        line('lease_liability', c['liability']); line('cash', -p['cash_payment'])
        cash.update(financing=-c['liability'], operating=-interest)
        c.update(rou=F(0), liability=F(0), remaining_payment=F(0), periods_remaining=0)
    elif method.startswith('benefit.'):
        require(c['no_ceiling_required'] and c['dbo'] >= c['plan_assets'], 'ceiling_method_required', 'unsupported')
        d, a = c['dbo'], c['plan_assets']
        if method == 'benefit.remeasure':
            require(p['dbo'] >= p['plan_assets'] >= 0, 'ceiling_method_required', 'unsupported')
            movement = (p['dbo'] - p['plan_assets']) - (d - a)
            c.update(dbo=p['dbo'], plan_assets=p['plan_assets'], phase='remeasured')
            line('oci_pension', movement); line('pension_liability', -movement)
        elif method == 'benefit.curtail':
            require(c['phase'] == 'remeasured' and p['no_earlier_trigger'], 'benefit_event_order')
            reduction = p['dbo_reduction']; require(0 <= reduction <= d and d - reduction >= a, 'ceiling_method_required', 'unsupported')
            c.update(dbo=d - reduction, phase='curtailed'); line('pension_liability', reduction); line('income', -reduction)
        elif method == 'benefit.settle':
            require(p['legal_discharge'], 'legal_discharge_failed')
            require(c['phase'] == 'curtailed', 'benefit_event_order')
            dd, pp, cc = p['dbo_discharged'], p['plan_assets_paid'], p['company_cash_paid']
            require(0 <= dd <= d and 0 <= pp <= a and cc >= 0 and d - dd >= a - pp, 'settlement_scope_unsupported', 'unsupported')
            c.update(dbo=d - dd, plan_assets=a - pp, phase='settled')
            line('pension_liability', dd - pp); line('cash', -cc); line('income', -(dd - pp - cc)); cash['operating'] = -cc
        elif method == 'benefit.service':
            require(c['phase'] == 'settled' and p['simple_accrual'], 'benefit_event_order')
            require(p['service_cost'] >= 0 and p['annual_rate'] >= 0 and 0 <= p['year_fraction'] <= 1, 'benefit_parameters')
            factor = p['annual_rate'] * p['year_fraction']; ni = (d - a) * factor
            c.update(dbo=d * (1 + factor) + p['service_cost'], plan_assets=a * (1 + factor), phase='service')
            line('expense', p['service_cost']); line('finance_expense', ni); line('pension_liability', -p['service_cost'] - ni)
    elif method == 'funding.recognize':
        require(c['unavailable_surplus'] and c['plan_assets'] >= c['dbo'] and p['past_service'] and p['wholly_unavailable_after_payment'], 'funding_scope_unsupported', 'unsupported')
        require(c['required_funding'] == 0 and c['paid'] == 0 and p['required_amount'] >= 0, 'funding_already_recognized')
        amount = p['required_amount']; c.update(required_funding=amount, recognized_obligation=amount)
        line('oci_pension', amount); line('pension_liability', -amount)
    elif method == 'funding.pay':
        amount = p['cash_paid']; require(0 < amount <= c['recognized_obligation'], 'funding_payment_mismatch')
        c['paid'] += amount; c['recognized_obligation'] -= amount; c['plan_assets'] += amount
        line('pension_liability', amount); line('cash', -amount); cash['operating'] = -amount
    elif method == 'restoration.change':
        require(c['original_cost_includes_liability'] and p['measurement_current'], 'restoration_admission_failed')
        require(p['new_liability'] >= 0, 'negative_liability')
        change = p['new_liability'] - c['liability']; line('provision', -change)
        if c['life'] == 0:
            require(c['ppe'] == 0, 'exhausted_asset_mismatch')
            line('expense', change)
        elif change < 0:
            asset_reduction = min(c['ppe'], -change); c['ppe'] -= asset_reduction
            line('ppe', -asset_reduction); line('income', change + asset_reduction)
        else:
            require(p['recoverable_amount'] is not None, 'measurement_unresolved', 'partial')
            new_asset = c['ppe'] + change
            impairment = max(new_asset - p['recoverable_amount'], F(0)); c['ppe'] = new_asset - impairment
            c['impairment_to_date'] += impairment; line('ppe', change - impairment); line('expense', impairment)
        c['liability'] = p['new_liability']
    elif method == 'restoration.pay':
        require(p['cash_paid'] == c['liability'] and p['cash_paid'] >= 0, 'payment_measurement_mismatch')
        require((p['classification'], p['classification_status']) in [
            ('operating', 'provisional_supplied_interpretation'), ('unresolved', 'unresolved')], 'cash_policy_mismatch')
        line('provision', c['liability']); line('cash', -p['cash_paid']); c['liability'] = F(0)
        cash['operating' if p['classification'] == 'operating' else 'unclassified'] = -p['cash_paid']
    elif method == 'impairment.allocate':
        require(not c['allocated'] and p['perimeter_consistent'], 'impairment_perimeter_failed')
        require(p['unit_recoverable'] is not None and all(a['floor'] is not None and a['valuation_status'] == 'known' for a in c['assets']), 'measurement_unresolved', 'partial')
        require(p['unit_recoverable'] >= 0, 'negative_recoverable')
        loss = max(c['goodwill'] + sum(a['carrying'] for a in c['assets']) - p['unit_recoverable'], F(0))
        g = min(loss, c['goodwill']); c['goodwill'] -= g; c['goodwill_loss'] += g
        remaining = loss - g
        capacities = [max(a['carrying'] - a['floor'], F(0)) for a in c['assets']]
        allocations = [F(0)] * len(capacities)
        active = {i for i, cap in enumerate(capacities) if cap > 0 and c['assets'][i]['carrying'] > 0}
        while remaining and active:
            total = sum(c['assets'][i]['carrying'] for i in active)
            proposed = {i: remaining * c['assets'][i]['carrying'] / total for i in active}
            saturated = {i for i in active if proposed[i] > capacities[i]}
            if not saturated:
                for i in active: allocations[i] = proposed[i]
                remaining = F(0)
            else:
                for i in saturated: allocations[i] = capacities[i]; remaining -= capacities[i]
                active -= saturated
        require(remaining == 0, 'unallocated_loss_requires_investigation', 'partial')
        for asset, amount in zip(c['assets'], allocations): asset['carrying'] -= amount; asset['loss_to_date'] += amount
        c.update(unit_recoverable=p['unit_recoverable'], allocated=True)
        line('expense', loss); line('goodwill', -g); line('ppe', -sum(allocations))
    elif method == 'tax.revalue_impair':
        require(p['no_time_or_base_change'] and c['rate_enacted'], 'tax_scope_unsupported', 'unsupported')
        require(0 <= p['recoverable'] <= c['carrying'] and c['dta'] == 0, 'tax_scope_unsupported', 'unsupported')
        require(c['dtl'] == max(c['carrying'] - c['tax_base'], 0) * c['rate'], 'tax_opening_mismatch')
        loss = c['carrying'] - p['recoverable']; oci_loss = min(loss, c['gross_surplus']); pnl_loss = loss - oci_loss
        new_dtl = max(p['recoverable'] - c['tax_base'], F(0)) * c['rate']
        deductible = max(c['tax_base'] - p['recoverable'], F(0))
        require(not deductible or c['recovery_probable'], 'tax_recovery_unresolved', 'partial')
        new_dta = deductible * c['rate']; dtl_release = c['dtl'] - new_dtl
        require(dtl_release == oci_loss * c['rate'], 'tax_origin_scope_unsupported', 'unsupported')
        line('ppe', -loss); line('oci_revaluation', oci_loss - dtl_release); line('expense', pnl_loss)
        line('dtl', dtl_release); line('dta', new_dta); line('tax_expense', -new_dta)
        c.update(carrying=p['recoverable'], dtl=new_dtl, dta=new_dta, gross_surplus=c['gross_surplus'] - oci_loss)
    elif method == 'advance.allocate':
        require(not c['bill_allocated'], 'advance_already_allocated')
        require(c['bill_id'] == p['bill_id'] and p['gross_bill'] == c['nominal_bill'] == c['unallocated_advance'], 'advance_right_mismatch')
        c.update(unallocated_advance=F(0), bill_allocated=True)
    else: raise Refusal('method_not_supported', 'unsupported')
    return c, {k: v for k, v in j.items() if v}, {k: cash.get(k, F(0)) for k in CASH}

class Check:
    def __init__(self):
        self.packet = json.loads((OUT / 'portable-exchanges.json').read_text())
        self.schemas = json.loads((OUT / 'record-schemas.json').read_text())
        self.reg = self.packet['record_registry']; self.alias = self.packet['aliases']; self.checks = []
        self.blob_cache = {}; self.derived = {}
    def body(self, r):
        if isinstance(r, str): r = self.alias[r]
        value = self.reg[r['digest']]
        assert (value['kind'], value['schema']) == (r['kind'], r['schema'])
        return value['body']
    def ck(self, name, action):
        try: action(); self.checks.append({'name': name, 'passed': True})
        except Exception as e: self.checks.append({'name': name, 'passed': False, 'detail': repr(e)[:600]})
    def raw(self, r):
        if r['digest'] not in self.blob_cache:
            p = ROOT / self.packet['blobs'][r['digest']]['path']; data = p.read_bytes()
            assert hashlib.sha256(data).hexdigest() == r['digest']
            self.blob_cache[r['digest']] = data
        data = self.blob_cache[r['digest']]; assert len(data) == r['byte_length']; return data
    def closure(self, roots):
        found, active = set(), set()
        def visit(r):
            assert r['digest'] not in active, 'cycle'
            if r['digest'] in found: return
            self.body(r); active.add(r['digest'])
            for child in self.reg[r['digest']]['dependencies']: visit(child)
            active.remove(r['digest']); found.add(r['digest'])
        for r in roots: visit(r)
        return sorted(found)
    def record(self, digest, r):
        assert set(r) == {'kind', 'schema', 'key', 'revision', 'body', 'dependencies'}
        assert r['schema'] == self.schemas['schema_ids'][r['kind']] and type(r['revision']) is int and r['revision'] >= 0
        Draft202012Validator(self.schemas['$defs'][r['kind']], format_checker=FormatChecker()).validate(r['body'])
        decode(r)
        assert hashlib.sha256(('accdsl.portable.v1/' + r['schema']).encode() + b'\0' + encode(r)).hexdigest() == digest
        dependencies = {encode(x): x for x in refs(r['body'])}
        assert r['dependencies'] == [dependencies[k] for k in sorted(dependencies)]
        for x in dependencies.values(): self.body(x)
        for x in blobs(r['body']): self.raw(x)
    def state(self, rr):
        s = decode(self.body(rr)); b = s['balances']; comp = decode(self.body(self.body(rr)['component_ref'])); c, tag = comp['value'], comp['tag']
        assert sum(b.values()) == 0 and b['cash'] >= 0
        assert all(b[a] >= 0 for a in ASSETS) and all(b[a] <= 0 for a in LIABS)
        if tag == 'production': assert b['wip'] == c['wip_cost'] and b['finished_goods'] == c['finished_cost']
        elif tag == 'lossbatch':
            assert b['wip'] == (c['cost_pool'] if c['phase'] == 'unallocated' else 0)
            assert b['finished_goods'] == c['finished_cost']
        elif tag == 'inspection': assert b['ppe'] == c['physical_carrying'] + c['inspection_carrying']
        elif tag == 'lease': assert b['rou'] == c['rou'] and -b['lease_liability'] == c['liability'] and -b['payable'] == c['usage_due']
        elif tag == 'benefit': assert -b['pension_liability'] == c['dbo'] - c['plan_assets']
        elif tag == 'funding': assert -b['pension_liability'] == c['recognized_obligation'] and b['pension_asset'] == 0
        elif tag == 'restoration': assert b['ppe'] == c['ppe'] and -b['provision'] == c['liability']
        elif tag == 'impairment': assert b['goodwill'] == c['goodwill'] and b['ppe'] == sum(a['carrying'] for a in c['assets'])
        elif tag == 'tax_origin':
            assert b['ppe'] == c['carrying'] and b['dta'] == c['dta'] and -b['dtl'] == c['dtl']
            assert -b['oci_revaluation'] == c['gross_surplus'] - c['dtl']
        elif tag == 'advance': assert -b['contract_liability'] == c['nominal_bill'] and b['cash'] == c['nominal_bill']
        else: check_component(tag, c, b)
    def finances(self, basis_ref, journal_ref, delta_ref):
        bb = self.body(basis_ref); opening = self.body(bb['opening_ref']); ev = self.body(bb['event_ref'])
        cb = decode(self.body(opening['component_ref'])); method = self.body(bb['method_ref'])
        require(method['method_id'] == ev['method_id'] and method['component_kind'] == cb['tag'], 'method_component_mismatch')
        after_component, lines, cash = derive(cb['tag'], cb['value'], ev['method_id'], decode(ev['parameters']))
        if ev['method_id'] == 'service.progress':
            c = cb['value']; start = date.fromisoformat(c['service_start']); end = date.fromisoformat(c['service_end_exclusive'])
            observed = date.fromisoformat(ev['event_date']) + timedelta(days=1)
            require(start.day == end.day == 1 and (end.year-start.year)*12+end.month-start.month == c['total_service_months'],
                'service_calendar_scope','unsupported')
            months = max(0, min(c['total_service_months'], (observed.year-start.year)*12+observed.month-start.month))
            require(ev['parameters']['completed_service_months'] <= months, 'future_service_not_performed')
        journal = self.body(journal_ref); delta = self.body(delta_ref); closing = self.body(delta['closing_ref'])
        actual = {}
        for item in journal['lines']: actual[item['account']] = actual.get(item['account'], F(0)) + decode(item['signed_amount'])
        actual = {k: v for k, v in actual.items() if v}
        require(actual == lines and sum(actual.values()) == 0, 'wrong_financial_transition')
        require((journal['mode'] == 'state_only') == (not lines) and (lines or not journal['lines']), 'wrong_journal_mode')
        require(decode(self.body(closing['component_ref'])) == {'tag': cb['tag'], 'value': after_component}, 'wrong_component_transition')
        require(delta['opening_ref'] == bb['opening_ref'] and delta['basis_ref'] == basis_ref and journal['basis_ref'] == basis_ref, 'basis_mismatch')
        require(closing['context_ref'] == opening['context_ref'] and closing['view_ref'] == bb['view_ref'], 'context_or_view_mismatch')
        require(closing['sequence'] == opening['sequence'] + 1 and closing['instant'] == ev['instant'], 'state_time_mismatch')
        require(closing['tax_status'] == opening['tax_status'], 'tax_status_changed')
        expected_cash_status = ev['parameters']['classification_status'] if ev['method_id'] == 'restoration.pay' else opening['cash_classification_status']
        require(closing['cash_classification_status'] == expected_cash_status, 'cash_policy_status_mismatch')
        b0, b1 = decode(opening['balances']), decode(closing['balances'])
        require(b1 == {a: b0[a] + lines.get(a, F(0)) for a in b0}, 'wrong_account_transition')
        require(decode(delta['cash_change']) == cash and sum(cash.values()) == lines.get('cash', 0), 'cash_classification_mismatch')
        require(decode(closing['cash_movements']) == {k: decode(opening['cash_movements'])[k] + cash[k] for k in CASH}, 'cash_history_mismatch')
        self.state(bb['opening_ref']); self.state(delta['closing_ref'])
        return after_component, lines, cash
    def bind(self, request):
        rq = self.body(request); args = rq['arguments']['value']
        require(rq['profile_ref'] == self.packet['profile_ref'], 'profile_mismatch', 'unsupported')
        require(rq['operation'] == rq['arguments']['tag'] == self.body(rq['signature_ref'])['operation'], 'operation_binding_mismatch')
        require(self.body(rq['signature_ref'])['profile_ref'] == rq['profile_ref'] and
                self.body(rq['profile_ref'])['schema_lock_ref'] == self.packet['schema_lock_ref'], 'signature_lock_mismatch')
        if 'basis_ref' not in args: return
        b = self.body(args['basis_ref']); ev = self.body(b['event_ref']); opening = self.body(b['opening_ref'])
        context = self.body(b['context_ref']); authority = self.body(b['authority_ref']); method = self.body(b['method_ref'])
        require(all(b['identity'][k] == context[k] for k in ['entity_id', 'book_id', 'branch_key']), 'owner_binding_mismatch')
        require(b['context_ref'] == ev['context_ref'] == opening['context_ref'] == authority['context_ref'], 'context_binding_mismatch')
        require(rq['view_ref'] == b['view_ref'] == opening['view_ref'], 'view_binding_mismatch')
        require(self.body(rq['view_ref'])['information_mode'] == 'archival_synthetic', 'information_mode_unsupported', 'unsupported')
        require(authority['source_ref'] == method['source_ref'] and method['source_ref'] in self.body(b['view_ref'])['source_refs'], 'source_method_mismatch')
        require(authority['supporting_source_refs'] == method['supporting_source_refs'], 'source_method_mismatch')
        source_refs = [method['source_ref'], *method['supporting_source_refs']]
        for sr in source_refs:
            source = self.body(sr)
            require(sr in self.body(b['view_ref'])['source_refs'], 'source_method_mismatch')
            required_basis = 'historical_AU_AASB_conditional' if source['family'] == 'AU_AASB' else 'historical_EU_IFRS_conditional'
            require(context['basis'] == required_basis and context['issuer_class'] == 'for_profit', 'source_jurisdiction_mismatch')
            if source['family'] == 'AU_AASB':
                start, end, date = ev['reporting_period_start'], ev['reporting_period_end_exclusive'], ev['event_date']
                require(start is not None and end is not None and date is not None, 'reporting_period_unresolved', 'partial')
                require(start <= date < end, 'event_outside_reporting_period')
                require(source['period_start_inclusive'] <= start and
                    (source['period_start_exclusive'] is None or start < source['period_start_exclusive']), 'source_period_mismatch')
        require(authority['start_inclusive'] <= ev['instant'] < authority['end_exclusive'], 'authority_interval_mismatch')
        require(ev['instant'] > opening['instant'], 'event_time_order')
        if 'authorization_ref' in args:
            auth = self.body(args['authorization_ref']); admission = self.body(auth['admission_ref'])
            require(auth['basis_ref'] == admission['basis_ref'] == args['basis_ref'] and auth['view_ref'] == b['view_ref'], 'authorization_binding_mismatch')
            require(auth['posting_permitted'] and admission['status'] == 'eligible', 'posting_not_authorized')
            require(admission['source_ref'] == method['source_ref'] and admission['context_ref'] == b['context_ref'] and admission['instant'] == ev['instant'], 'admission_binding_mismatch')
            require(all(x['status'] == 'satisfied' and x['support_ref'] == b['event_ref'] for x in admission['findings']), 'admission_evidence_mismatch')
    def report(self, report_ref):
        r = self.body(report_ref); s = self.body(r['state_ref']); initial = self.body(r['opening_ref'])
        assert s['context_ref'] == initial['context_ref'] and r['view_ref'] == s['view_ref']
        b, b0 = decode(s['balances']), decode(initial['balances']); values = decode(r['values'])
        expected = {'cash': b['cash'], 'assets': sum(b[k] for k in ASSETS), 'liabilities': -sum(b[k] for k in LIABS),
            'equity': -sum(b[k] for k in ['capital', 'retained', *PROFIT, *OCI]),
            'profit': -sum(b[k] - b0[k] for k in PROFIT), 'oci': -sum(b[k] - b0[k] for k in OCI),
            **{k:decode(s['cash_movements'])[k]-decode(initial['cash_movements'])[k] for k in CASH}}
        assert values == expected and values['assets'] == values['liabilities'] + values['equity']
        assert sum(values[k] for k in CASH) == b['cash'] - b0['cash']
        opening_equity = -sum(b0[k] for k in ['capital', 'retained', *PROFIT, *OCI])
        assert opening_equity + values['profit'] + values['oci'] == values['equity']
        assert r['tax_status'] == s['tax_status'] and not r['complete_company_after_tax']
        assert r['cash_classification_complete'] == (values['unclassified'] == 0)
        assert r['cash_classification_status'] == s['cash_classification_status']
        income=decode(r['income_statement'])
        for k in ['product_revenue','service_revenue','commission_revenue','reimbursement_income']:
            assert income[k] == -(b[k]-b0[k])
        for k in ['cost_of_sales','service_expense','assurance_expense','finance_expense','tax_expense']:
            assert income[k] == b[k]-b0[k]
        assert income['other_gains'] == -(b['income']+b['provision_gain']-b0['income']-b0['provision_gain'])
        assert income['other_expense'] == b['expense']-b0['expense']
        assert sum(income[k] for k in ['product_revenue','service_revenue','commission_revenue','reimbursement_income','other_gains']) - sum(
            income[k] for k in ['cost_of_sales','service_expense','assurance_expense','other_expense','finance_expense','tax_expense']) == values['profit']
    def exchange(self, e):
        rq = self.body(e['request_ref']); response = self.body(e['response_ref']); sub = self.body(e['submission_ref'])
        assert self.raw(sub['blob_ref']) == encode(self.reg[e['request_ref']['digest']])
        assert response['submission_ref'] == e['submission_ref'] and response['request_ref'] == e['request_ref']
        assert response['operation'] == rq['operation'] and response['input_view_ref'] == rq['view_ref']
        assert response['statuses']['capability_status'] == 'specified_only_no_runtime'
        before, after = e['world_before'], e['world_after']; expected = deepcopy(before)
        code, disposition, receipt = None, 'completed', None
        args = rq['arguments']['value']
        try:
            self.bind(e['request_ref'])
            if rq['operation'] == 'accounting.commit@1':
                self.finances(args['basis_ref'], args['journal_ref'], args['delta_ref'])
                b = self.body(args['basis_ref']); ident = encode([b['identity'][k] for k in ['entity_id', 'book_id', 'branch_key', 'business_event_id']]).decode()
                if ident in before['event_receipts']:
                    saved = before['event_receipts'][ident]
                    require(saved['request_ref'] == e['request_ref'], 'idempotency_conflict')
                    receipt = saved['receipt_ref']; disposition = 'replayed'
                else:
                    require(rq['view_ref'] == before['current_view_ref'], 'stale_dependency_view')
                    st = b['opening_ref']; sb = self.body(st); c = self.body(sb['context_ref'])
                    expected_head = {'owner_key': '/'.join(c[k] for k in ['entity_id', 'book_id', 'branch_key']), 'state_ref': st, 'generation': sb['sequence']}
                    require(rq['expected_head'] == before['head'] == expected_head, 'stale_head')
                    receipt = response['receipt_ref']; assert receipt is not None
                    rec = self.body(receipt); closing = self.body(args['delta_ref'])['closing_ref']
                    assert rec == {'request_ref': e['request_ref'], **args, 'opening_ref': st,
                        'closing_ref': closing, 'generation': self.body(closing)['sequence'], 'status': 'committed'}
                    expected['head'] = {**expected_head, 'state_ref': closing, 'generation': rec['generation']}
                    expected['event_receipts'][ident] = {'request_ref': e['request_ref'], 'receipt_ref': receipt}
                    for dst, rr in [('journals', args['journal_ref']), ('deltas', args['delta_ref']), ('receipts', receipt)]: expected[dst].append(rr)
                    expected['published_records'] = sorted(set(before['published_records']) | set(self.closure([receipt])))
            elif rq['operation'] == 'accounting.authorize@1':
                require(rq['view_ref'] == before['current_view_ref'], 'stale_dependency_view')
                out = response['payload']['result_refs']; assert len(out) == 1
                auth = self.body(out[0]); adm = self.body(auth['admission_ref']); b = self.body(args['basis_ref'])
                assert auth['basis_ref'] == args['basis_ref'] == adm['basis_ref'] and auth['posting_permitted']
                assert adm['source_ref'] == self.body(b['method_ref'])['source_ref']
                event = self.body(b['event_ref']); comp = decode(self.body(self.body(b['opening_ref'])['component_ref']))
                derive(comp['tag'], comp['value'], event['method_id'], decode(event['parameters']))
            elif rq['operation'] == 'accounting.propose@1':
                require(rq['view_ref'] == before['current_view_ref'], 'stale_dependency_view')
                jr, dr = response['payload']['result_refs']; self.finances(args['basis_ref'], jr, dr)
            else:
                require(not args['require_current'] or rq['view_ref'] == before['current_view_ref'], 'stale_dependency_view')
                assert rq['operation'] == 'report.build@1' and len(response['payload']['result_refs']) == 1
                rr = response['payload']['result_refs'][0]; assert self.body(rr)['state_ref'] == args['state_ref']
                assert self.body(rr)['opening_ref'] == args['opening_ref']
                self.report(rr)
        except Refusal as err: code, disposition = err.code, err.disposition
        assert response['disposition'] == disposition, (e['id'], response['disposition'], disposition, code)
        assert [x['code'] for x in response['diagnostics']] == ([code] if code else [])
        assert response['receipt_ref'] == receipt
        assert after == expected, 'store world differs from derived atomic outcome'
        assert response['payload']['additional_commit'] == (disposition == 'completed' and receipt is not None)
        assert response['commit_observation'] == ('committed' if receipt else 'not_committed')
        cov = response['coverage']; assert self.body(cov['domain_ref'])['request_ref'] == e['request_ref']
        bucket = 'unresolved' if disposition == 'partial' else 'unsupported' if disposition == 'unsupported' else 'completed'
        assert len(cov[bucket]) == 1 and sum(len(cov[k]) for k in ['completed', 'unresolved', 'unsupported', 'infeasible', 'cancelled']) == 1
        assert self.body(cov[bucket][0])['domain_ref'] == cov['domain_ref']
        assert bool(response['unresolved']) == (disposition == 'partial')
        for ref in response['unresolved']:
            assert self.body(ref)['code'] == code and self.body(ref)['basis_ref'] == args['basis_ref']
    def run(self):
        for digest, r in self.reg.items(): self.ck('record:' + r['key'], lambda digest=digest, r=r: self.record(digest, r))
        for kind, schema in self.schemas['$defs'].items(): self.ck('schema:' + kind, lambda schema=schema: Draft202012Validator.check_schema(schema))
        for rr in self.alias.values():
            if rr['kind'] == 'CompanyState': self.ck('state:' + self.reg[rr['digest']]['key'], lambda rr=rr: self.state(rr))
        for step in self.packet['financial_steps']:
            def compute(step=step):
                jr = self.body(step['journal_ref']); result = self.finances(jr['basis_ref'], step['journal_ref'], step['delta_ref'])
                self.derived[step['id']] = {'component': result[0], 'journal': result[1], 'cash_change': result[2]}
            self.ck('independent:' + step['id'], compute)
        for e in self.packet['exchanges']: self.ck('exchange:' + e['id'], lambda e=e: self.exchange(e))
        for e in self.packet['unbound_submissions']:
            def check_unbound(e=e):
                sub, response = self.body(e['submission_ref']), self.body(e['response_ref'])
                old = json.loads(self.raw(sub['blob_ref'])); source = json.loads(self.raw(e['source_bundle_blob']))
                assert old in source['record_registry'].values()
                assert old['body']['profile_ref']['schema'] in ['accdsl.corporate.profile.v1','accdsl.corporate-components.profile.v1']
                errors = list(Draft202012Validator(self.schemas['$defs']['OperationRequest']).iter_errors(old['body']))
                assert any(list(error.path)[:2] == ['profile_ref', 'schema'] for error in errors)
                assert response['request_ref'] is response['operation'] is response['payload'] is response['coverage'] is None
                assert response['receipt_ref'] is None and response['commit_observation'] == 'not_committed'
                assert response['statuses']['structural_validity'] == 'invalid' and response['disposition'] == 'rejected'
                assert [x['code'] for x in response['diagnostics']] == ['profile_mismatch']
                assert e['world_before'] == e['world_after']
            self.ck('unbound:' + e['id'], check_unbound)
        def global_checks():
            assert set(self.closure(list(self.alias.values()))) == set(self.reg)
            assert {x['method'] for x in self.packet['financial_steps']} == {
                r['body']['method_id'] for r in self.reg.values() if r['kind'] == 'MethodDefinition'}
            assert self.raw(self.body(self.packet['schema_lock_ref'])['schema_blob']) == (OUT / 'record-schemas.json').read_bytes()
            assert self.raw(self.body(self.packet['schema_lock_ref'])['semantic_contract_blob']) == (OUT / 'semantic-contract.md').read_bytes()
            loss = self.packet['lost_acknowledgement']; es = {e['id']: e for e in self.packet['exchanges']}
            first, retry = es[loss['retry_before_exchange']], es[loss['retry_after_exchange']]
            assert first['request_ref'] == retry['request_ref'] and first['submission_ref'] == retry['submission_ref']
            assert loss['before_publication'] == first['world_before'] and loss['after_publication'] == first['world_after'] == retry['world_before'] == retry['world_after']
            partial = self.packet['invalid_partial_publication']; assert partial not in [loss['before_publication'], loss['after_publication']]
            assert any(r['receipt_ref']['digest'] not in partial['published_records'] for r in partial['event_receipts'].values())
            baseline = json.loads((OUT.parent / 'protected-inputs.json').read_text())
            for pin in baseline['files']:
                assert hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], pin['path']
                assert hashlib.sha256((ROOT / pin['snapshot']).read_bytes()).hexdigest() == pin['sha256'], pin['snapshot']
            for pin in json.loads((OUT / 'predecessor.json').read_text())['files']:
                assert hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], pin['path']
            dates_by_context = {}
            for step in self.packet['financial_steps']:
                ev = self.body(step['event_ref']); key = ev['context_ref']['digest']
                if ev['event_date'] is not None:
                    assert dates_by_context.get(key, ev['event_date']) <= ev['event_date']
                    dates_by_context[key] = ev['event_date']
            idx = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
            assert hashlib.sha256(idx).hexdigest() == baseline['index_sha256']
            assert len(idx.splitlines()) == 100
            assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['git_commit']
        self.ck('global-closure-recovery-preservation', global_checks)

if __name__ == '__main__':
    started = time.monotonic(); check = Check(); check.run()
    result = {'passed': all(x['passed'] for x in check.checks), 'count': len(check.checks),
        'financial_steps': len(check.derived), 'exchanges': len(check.packet['exchanges']), 'checks': check.checks,
        'wall_seconds': time.monotonic() - started, 'jsonschema_version': importlib.metadata.version('jsonschema'),
        'evidence_role': 'Independent deterministic documentary check, not runtime or accounting admission'}
    (OUT / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    (OUT / 'independent-finances.json').write_text(json.dumps(check.derived, default=str, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'count', 'financial_steps', 'exchanges', 'wall_seconds']}))
    for failure in [x for x in check.checks if not x['passed']][:8]: print(json.dumps(failure))
    assert result['passed']
