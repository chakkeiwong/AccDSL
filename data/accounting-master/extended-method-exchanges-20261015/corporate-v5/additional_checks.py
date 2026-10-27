"""Independent customer/production/payable calculations, with no author imports."""
from copy import deepcopy
from fractions import Fraction as F

def calculate(original, method, p, require):
    c = deepcopy(original); j = {}; cash = {}
    def line(a, v): j[a] = j.get(a, F(0)) + v
    def operating(v): line('cash', v); cash['operating'] = cash.get('operating', F(0)) + v
    family, op = method.split('.')
    if family == 'returns':
        require(c['control_passed'] and c['estimate_admitted'], 'return_admission_unresolved', 'partial')
        require(c['no_recovery_costs'], 'recovery_measurement_required', 'partial')
        if op == 'sell':
            require(c['phase'] == 'opening', 'return_event_order')
            require(0 <= c['expected_remaining'] <= c['units'] and p['cash_received'] == c['units'] * c['price'], 'return_amount_mismatch')
            liability = c['expected_remaining'] * c['price']; asset = c['expected_remaining'] * c['cost']
            operating(p['cash_received']); line('income', -(p['cash_received'] - liability)); line('refund_liability', -liability)
            line('inventory', -c['units'] * c['cost']); line('return_recovery', asset); line('expense', c['units'] * c['cost'] - asset)
            c.update(refund=liability, recovery=asset, inventory_units=F(0), phase='sold')
        elif op == 'remeasure':
            require(c['phase'] in ['sold', 'remeasured'], 'return_event_order')
            require(p['new_evidence_admitted'], 'return_measurement_unresolved', 'partial')
            require(0 <= p['expected_remaining'] <= c['units'] - c['returned'], 'return_units_invalid')
            liability = p['expected_remaining'] * c['price']; asset = p['expected_remaining'] * c['cost']
            line('refund_liability', c['refund'] - liability); line('income', liability - c['refund'])
            line('return_recovery', asset - c['recovery']); line('expense', c['recovery'] - asset)
            c.update(expected_remaining=p['expected_remaining'], refund=liability, recovery=asset, phase='remeasured')
        else:
            require(c['phase'] == 'remeasured' and p['return_rights_expired'] and p['no_unresolved_claims'], 'return_expiry_unresolved', 'partial')
            require(p['units_returned'] == c['expected_remaining'], 'remeasure_before_settlement')
            line('refund_liability', c['refund']); operating(-c['refund'])
            line('inventory', c['recovery']); line('return_recovery', -c['recovery'])
            c.update(returned=c['returned'] + p['units_returned'], inventory_units=c['inventory_units'] + p['units_returned'],
                     expected_remaining=F(0), refund=F(0), recovery=F(0), phase='settled')
    elif family == 'assurance':
        require(c['classification'] == 'assurance', 'assurance_classification_unresolved', 'partial')
        require(c['population_obligation_admitted'], 'population_obligation_unresolved', 'partial')
        require(c['reimbursement_virtually_certain'], 'reimbursement_measurement_unresolved', 'partial')
        require(0 <= c['reimbursement_fraction'] <= 1, 'reimbursement_fraction_invalid')
        if op == 'recognize':
            require(c['phase'] == 'opening', 'assurance_event_order')
            require(all(x['probability'] >= 0 and x['cost'] >= 0 for x in c['outcomes']) and sum(x['probability'] for x in c['outcomes']) == 1, 'claim_law_invalid')
            cost = c['units'] * sum(x['probability'] * x['cost'] for x in c['outcomes']); recovery = cost * c['reimbursement_fraction']
            require(p['cash_sales'] == c['units'] * c['sale_price'], 'sale_amount_mismatch')
            operating(p['cash_sales']); line('product_revenue', -p['cash_sales']);line('reimbursement_income',-recovery)
            line('inventory', -c['inventory_cost']);line('cost_of_sales',c['inventory_cost'])
            line('assurance_expense', cost); line('provision', -cost); line('reimbursement', recovery)
            c.update(inventory_cost=F(0), provision=cost, reimbursement=recovery, phase='recognized')
        elif op == 'pay':
            require(c['phase'] in ['recognized', 'paid', 'remeasured'], 'assurance_event_order')
            require(0 <= p['claims_paid'] <= c['provision'] and 0 <= p['reimbursement_received'] <= c['reimbursement'], 'claims_settlement_mismatch')
            line('provision', p['claims_paid']); line('reimbursement', -p['reimbursement_received'])
            operating(p['reimbursement_received'] - p['claims_paid'])
            c['provision'] -= p['claims_paid']; c['reimbursement'] -= p['reimbursement_received']
            c['paid_claims'] += p['claims_paid']; c['received_reimbursement'] += p['reimbursement_received']
            c['phase'] = 'settled' if c['provision'] == c['reimbursement'] == 0 else 'paid'
        else:
            require(p['new_evidence_admitted'] and p['remaining_claims'] >= 0, 'claims_measurement_unresolved', 'partial')
            new = p['remaining_claims']; recovery = new * c['reimbursement_fraction']
            change = new - c['provision']; rc = recovery - c['reimbursement']
            line('provision', -change); line('assurance_expense' if change >= 0 else 'provision_gain', change)
            line('reimbursement', rc); line('reimbursement_income' if rc >= 0 else 'assurance_expense', -rc)
            c.update(provision=new, reimbursement=recovery, phase='remeasured')
    elif family == 'service':
        require(c['distinct_service'], 'requires_assurance_or_combined_method', 'unsupported')
        if op == 'receive':
            require(c['cash_received'] == 0 and p['cash'] == c['price'], 'prepayment_scope')
            require(c['product_ssp'] > 0 and c['service_ssp'] > 0, 'standalone_prices_unresolved', 'partial')
            product = c['price'] * c['product_ssp'] / (c['product_ssp'] + c['service_ssp'])
            c.update(cash_received=p['cash'], product_allocation=product, service_allocation=c['price'] - product)
            operating(p['cash']); line('contract_liability', -p['cash'])
        elif op == 'deliver':
            require(not c['product_delivered'] and c['cash_received'] == c['price'] and p['control_transferred'], 'delivery_admission_failed')
            line('contract_liability', c['product_allocation']); line('income', -c['product_allocation'])
            line('expense', c['product_cost']); line('inventory', -c['product_cost'])
            c.update(product_delivered=True, revenue=c['revenue'] + c['product_allocation'])
        else:
            require(p['faithful_measure_admitted'] and c['faithful_uniform_progress'], 'progress_measurement_unresolved', 'partial')
            require(c['product_delivered'] and c['progress'] <= p['progress'] <= 1 and p['cash_cost'] >= 0, 'service_progress_invalid')
            require(c['total_service_months'] > 0 and c['completed_service_months'] <= p['completed_service_months'] <= c['total_service_months']
                and p['progress'] == F(p['completed_service_months'], c['total_service_months']), 'service_month_progress_mismatch')
            revenue = c['service_allocation'] * (p['progress'] - c['progress'])
            line('contract_liability', revenue); line('income', -revenue); line('expense', p['cash_cost']); operating(-p['cash_cost'])
            c.update(progress=p['progress'], completed_service_months=p['completed_service_months'],
                revenue=c['revenue'] + revenue, service_cost_paid=c['service_cost_paid'] + p['cash_cost'])
    elif family == 'distinct':
        if op == 'receive':
            require(c['received'] == 0 and p['cash'] == c['total_price'], 'prepayment_scope')
            c['received'] = p['cash']; operating(p['cash']); line('contract_liability', -p['cash'])
        elif op == 'deliver':
            require(0 < p['units'] <= min(c['stock_units'], c['total_units'] - c['delivered']), 'delivery_units_invalid')
            revenue = p['units'] * c['remaining_price_per_unit']; cost = p['units'] * c['unit_cost']
            require(revenue <= c['received'] - c['recognized'], 'prepayment_scope')
            c['delivered'] += p['units']; c['stock_units'] -= p['units']; c['recognized'] += revenue
            line('contract_liability', revenue); line('income', -revenue); line('inventory', -cost); line('expense', cost)
        else:
            require(p['enforceable'], 'modification_enforceability_unresolved', 'partial')
            require(p['remaining_distinct'] and not p['separate_contract_test'], 'different_modification_method', 'unsupported')
            require(not c['modified'] and p['added_units'] > 0 and p['cash'] == p['added_price'], 'modification_scope')
            remaining = c['total_units'] - c['delivered'] + p['added_units']
            require(c['stock_units'] >= remaining, 'stock_not_created_by_amendment')
            c['remaining_price_per_unit'] = (c['total_price'] - c['recognized'] + p['added_price']) / remaining
            c['total_units'] += p['added_units']; c['total_price'] += p['added_price']; c['received'] += p['cash']; c['modified'] = True
            operating(p['cash']); line('contract_liability', -p['cash'])
    elif family == 'integrated':
        require(c['customer_controls_wip'], 'over_time_admission_unresolved', 'partial')
        if op == 'receive':
            require(c['received'] == 0 and p['cash'] == c['price'], 'prepayment_scope')
            c['received'] = p['cash']; operating(p['cash']); line('contract_liability', -p['cash'])
        elif op == 'perform':
            require(p['faithful_measure_admitted'], 'progress_measurement_unresolved', 'partial')
            require(c['progress'] <= p['cumulative_progress'] <= 1 and p['cash_cost'] >= 0, 'service_progress_invalid')
            target = c['price'] * p['cumulative_progress']; revenue = target - c['revenue']
            require(target <= c['received'], 'prepayment_scope')
            c.update(progress=p['cumulative_progress'], revenue=target, cost_paid=c['cost_paid'] + p['cash_cost'])
            line('contract_liability', revenue); line('income', -revenue); line('expense', p['cash_cost']); operating(-p['cash_cost'])
        else:
            require(p['enforceable'], 'modification_enforceability_unresolved', 'partial')
            require(p['remaining_not_distinct'] and not c['modified'], 'different_modification_method', 'unsupported')
            require(p['faithful_measure_admitted'] and 0 <= p['new_progress'] <= 1, 'progress_measurement_unresolved', 'partial')
            require(p['cash'] == p['new_price'] - c['price'], 'prepayment_scope')
            target = p['new_price'] * p['new_progress']; catchup = target - c['revenue']
            operating(p['cash']); line('contract_liability', catchup - p['cash']); line('income', -catchup)
            c.update(price=p['new_price'], received=c['received'] + p['cash'], progress=p['new_progress'], revenue=target, modified=True)
    elif family == 'mixed':
        require(c['allocation_admitted'] and c['faithful_cost_progress'], 'mixed_allocation_unresolved', 'partial')
        if op == 'receive':
            require(c['received'] == 0 and p['cash'] == c['construction_price'] + c['visits_total'] * c['visit_price'], 'prepayment_scope')
            c['received'] = p['cash']; operating(p['cash']); line('contract_liability', -p['cash'])
        elif op == 'perform':
            require(p['construction_cash_cost'] >= 0 and c['cost_incurred'] + p['construction_cash_cost'] <= c['expected_cost'], 'construction_cost_invalid')
            require(p['visits'] >= 0 and p['visits'] + c['visits_done'] <= c['visits_total'] and p['visit_cash_cost'] >= 0, 'visit_count_invalid')
            incurred = c['cost_incurred'] + p['construction_cash_cost']
            target = c['construction_price'] * incurred / c['expected_cost']; visits = p['visits'] * c['visit_price']
            revenue = target - c['construction_revenue'] + visits; cost = p['construction_cash_cost'] + p['visit_cash_cost']
            c.update(cost_incurred=incurred, construction_revenue=target, visits_done=c['visits_done'] + p['visits'],
                visit_revenue=c['visit_revenue'] + visits, visit_cost_paid=c['visit_cost_paid'] + p['visit_cash_cost'])
            line('contract_liability', revenue); line('income', -revenue); line('expense', cost); operating(-cost)
        else:
            require(p['enforceable'] and p['allocations_admitted'], 'mixed_allocation_unresolved', 'partial')
            require(not c['modified'] and p['new_expected_cost'] >= c['cost_incurred'] and p['new_expected_cost'] > 0 and p['new_visits_total'] >= c['visits_done'], 'mixed_modification_scope')
            new_total = p['new_construction_price'] + p['new_visits_total'] * c['visit_price']
            require(p['cash'] == new_total - c['received'], 'prepayment_scope')
            target = p['new_construction_price'] * c['cost_incurred'] / p['new_expected_cost']; catchup = target - c['construction_revenue']
            operating(p['cash']); line('contract_liability', catchup - p['cash']); line('income', -catchup)
            c.update(construction_price=p['new_construction_price'], expected_cost=p['new_expected_cost'], construction_revenue=target,
                visits_total=p['new_visits_total'], received=new_total, modified=True)
    elif family == 'agency':
        require(c['role'] != 'unknown' and c['control_finding'] and c['cash_controlled'], 'control_classification_unresolved', 'partial')
        if op == 'acquire':
            require(c['role'] == 'principal' and c['phase'] == 'opening' and p['cost'] == c['supplier_price'], 'principal_acquisition_scope')
            c.update(inventory=p['cost'], payable=p['cost'], phase='acquired'); line('inventory', p['cost']); line('payable', -p['cost'])
        elif op == 'transfer':
            require(p['promise_satisfied'] and p['cash'] == c['customer_price'], 'performance_not_admitted')
            require(c['phase'] == ('acquired' if c['role'] == 'principal' else 'opening'), 'agency_event_order')
            operating(p['cash'])
            if c['role'] == 'principal': line('income', -p['cash']); line('inventory', -c['inventory']); line('expense', c['inventory'])
            else: line('income', -(p['cash'] - c['supplier_price'])); line('payable', -c['supplier_price'])
            c.update(inventory=F(0), payable=c['supplier_price'], phase='transferred')
        else:
            require(c['phase'] == 'transferred' and p['cash'] == c['payable'], 'remittance_mismatch')
            line('payable', p['cash']); operating(-p['cash']); c.update(payable=F(0), phase='settled')
    elif family == 'joint':
        require(c['relative_sales_admitted'], 'joint_allocation_unresolved', 'partial')
        if op == 'allocate':
            require(c['phase'] == 'opening' and p['cash_cost'] == c['joint_cost'], 'joint_cost_mismatch')
            a = c['units_a'] * c['split_price_a']; b = c['units_b'] * c['split_price_b']
            require(a > 0 and b > 0, 'joint_prices_unresolved', 'partial')
            ca = c['joint_cost'] * a / (a + b); c.update(cost_a=ca, cost_b=c['joint_cost'] - ca, phase='allocated')
            line('inventory', c['joint_cost']); operating(-c['joint_cost'])
        else:
            require(c['phase'] == 'allocated', 'joint_event_order')
            require(0 <= p['units_a'] <= c['units_a'] and 0 <= p['units_b'] <= c['units_b'], 'joint_units_invalid')
            require(p['cash'] == p['units_a'] * c['split_price_a'] + p['units_b'] * c['split_price_b'], 'joint_sale_mismatch')
            used_a, used_b = c['cost_a'] * p['units_a'] / c['units_a'], c['cost_b'] * p['units_b'] / c['units_b']
            c['cost_a'] -= used_a; c['cost_b'] -= used_b; c.update(sold_a=p['units_a'], sold_b=p['units_b'], phase='sold')
            operating(p['cash']); line('income', -p['cash']); line('inventory', -used_a - used_b); line('expense', used_a + used_b)
    elif family == 'byproduct':
        require(c['immaterial_admitted'] and 0 <= c['byproduct_nrv'] <= c['production_cost'], 'byproduct_measurement_unresolved', 'partial')
        if op == 'allocate':
            require(c['phase'] == 'opening' and p['cash_cost'] == c['production_cost'], 'byproduct_cost_mismatch')
            c.update(main_cost=c['production_cost'] - c['byproduct_nrv'], byproduct_cost=c['byproduct_nrv'], phase='allocated')
            line('inventory', c['production_cost']); operating(-c['production_cost'])
        else:
            require(c['phase'] == 'allocated' and p['cash'] == c['byproduct_nrv'], 'byproduct_sale_scope')
            operating(p['cash']); line('income', -p['cash']); line('inventory', -c['byproduct_cost']); line('expense', c['byproduct_cost'])
            c.update(byproduct_cost=F(0), phase='sold')
    elif family == 'supplier':
        require(c['ordinary_trade_supplier'] and c['not_qualifying_asset'], 'supplier_financing_scope', 'unsupported')
        require(c['final_payment'] == c['normal_price'] * (1 + c['rate']) ** 2, 'supplier_eir_mismatch')
        if op == 'purchase':
            require(c['phase'] == 'opening' and p['financing_assessment_admitted'], 'financing_measurement_unresolved', 'partial')
            c.update(carrying=c['normal_price'], inventory_cost=c['normal_price'], phase='purchased')
            line('inventory', c['normal_price']); line('payable', -c['normal_price'])
        elif op == 'accrue':
            require(c['phase'] in ['purchased', 'sold'] and c['years_accrued'] < 2 and p['full_year_elapsed'], 'supplier_accrual_order')
            interest = c['carrying'] * c['rate']; c['carrying'] += interest; c['years_accrued'] += 1
            line('finance_expense', interest); line('payable', -interest)
        elif op == 'sell':
            require(c['phase'] == 'purchased' and p['cash'] >= 0, 'supplier_sale_order')
            operating(p['cash']); line('income', -p['cash']); line('inventory', -c['inventory_cost']); line('expense', c['inventory_cost'])
            c.update(inventory_cost=F(0), phase='sold')
        else:
            require(c['phase'] == 'sold' and c['years_accrued'] == 2 and p['cash'] == c['carrying'] == c['final_payment'], 'supplier_payment_mismatch')
            line('payable', c['carrying']); operating(-p['cash']); c.update(carrying=F(0), phase='settled')
    else: raise AssertionError(method)
    income,expense='product_revenue','cost_of_sales'
    if family in ['integrated','mixed'] or method == 'service.progress':income,expense='service_revenue','service_expense'
    if family == 'agency' and c['role'] == 'agent':income='commission_revenue'
    if 'income' in j:j[income]=j.pop('income')
    if 'expense' in j:j[expense]=j.pop('expense')
    return c, {k: v for k, v in j.items() if v}, {k: cash.get(k, F(0)) for k in ['operating', 'investing', 'financing', 'unclassified']}

def check_component(tag, c, b):
    if tag == 'returns':
        assert b['inventory'] == c['inventory_units'] * c['cost'] and b['return_recovery'] == c['recovery'] and -b['refund_liability'] == c['refund']
    elif tag == 'assurance':
        assert b['inventory'] == c['inventory_cost'] and -b['provision'] == c['provision'] and b['reimbursement'] == c['reimbursement']
    elif tag == 'service_contract':
        assert -b['contract_liability'] == c['cash_received'] - c['revenue']
        assert b['inventory'] == (0 if c['product_delivered'] else c['product_cost'])
    elif tag == 'distinct_contract':
        assert -b['contract_liability'] == c['received'] - c['recognized'] and b['inventory'] == c['stock_units'] * c['unit_cost']
    elif tag == 'integrated_contract': assert -b['contract_liability'] == c['received'] - c['revenue']
    elif tag == 'mixed_contract': assert -b['contract_liability'] == c['received'] - c['construction_revenue'] - c['visit_revenue']
    elif tag == 'agency': assert b['inventory'] == c['inventory'] and -b['payable'] == c['payable']
    elif tag == 'joint_products': assert b['inventory'] == c['cost_a'] + c['cost_b']
    elif tag == 'byproduct': assert b['inventory'] == c['main_cost'] + c['byproduct_cost']
    elif tag == 'supplier_finance': assert b['inventory'] == c['inventory_cost'] and -b['payable'] == c['carrying']
    else: raise AssertionError(tag)
