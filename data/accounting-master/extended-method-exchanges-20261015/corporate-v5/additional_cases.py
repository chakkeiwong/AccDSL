"""Existing P17/R03-E numbers in closed successor state/event variants."""
def populate(case, step):
    au = []
    c = case('customer-returns', 'returns', {'cohort_id': 'cohort-1', 'units': '100', 'price': '10', 'cost': '6',
        'expected_remaining': '10', 'returned': '0', 'refund': '0', 'recovery': '0', 'inventory_units': '100',
        'control_passed': True, 'estimate_admitted': True, 'no_recovery_costs': True, 'phase': 'opening'},
        {'inventory': '600', 'capital': '-600'}); au.append(c)
    step(c, 'returns.sell', {'cash_received': '1000'}, {'refund': '100', 'recovery': '60', 'inventory_units': '0', 'phase': 'sold'},
        {'cash': '1000', 'income': '-900', 'refund_liability': '-100', 'inventory': '-600', 'return_recovery': '60', 'expense': '540'}, {'operating': '1000'})
    step(c, 'returns.remeasure', {'expected_remaining': '12', 'new_evidence_admitted': True},
        {'expected_remaining': '12', 'refund': '120', 'recovery': '72', 'phase': 'remeasured'},
        {'income': '20', 'refund_liability': '-20', 'return_recovery': '12', 'expense': '-12'})
    step(c, 'returns.remeasure', {'expected_remaining': '8', 'new_evidence_admitted': True},
        {'expected_remaining': '8', 'refund': '80', 'recovery': '48'},
        {'income': '-40', 'refund_liability': '40', 'return_recovery': '-24', 'expense': '24'})
    c['steps'][-1]['year'] = 2025
    step(c, 'returns.settle', {'units_returned': '8', 'return_rights_expired': True, 'no_unresolved_claims': True},
        {'expected_remaining': '0', 'returned': '8', 'refund': '0', 'recovery': '0', 'inventory_units': '8', 'phase': 'settled'},
        {'refund_liability': '80', 'cash': '-80', 'inventory': '48', 'return_recovery': '-48'}, {'operating': '-80'})
    c['steps'][-1]['year'] = 2025

    c = case('assurance-population', 'assurance', {'population_id': 'sales-1', 'units': '100', 'sale_price': '20',
        'inventory_cost': '600', 'provision': '0', 'reimbursement': '0', 'reimbursement_fraction': '1/4',
        'paid_claims': '0', 'received_reimbursement': '0', 'outcomes': [{'cost': '0', 'probability': '3/4'},
        {'cost': '10', 'probability': '1/5'}, {'cost': '40', 'probability': '1/20'}], 'classification': 'assurance',
        'population_obligation_admitted': True, 'reimbursement_virtually_certain': True, 'phase': 'opening'},
        {'cash': '1000', 'inventory': '600', 'capital': '-1600'}); au.append(c)
    step(c, 'assurance.recognize', {'cash_sales': '2000'}, {'inventory_cost': '0', 'provision': '400',
        'reimbursement': '100', 'phase': 'recognized'}, {'cash': '2000', 'product_revenue': '-2000',
        'reimbursement_income':'-100','inventory': '-600','cost_of_sales':'600',
        'assurance_expense': '400', 'provision': '-400', 'reimbursement': '100'}, {'operating': '2000'})
    step(c, 'assurance.pay', {'claims_paid': '100', 'reimbursement_received': '25'},
        {'provision': '300', 'reimbursement': '75', 'paid_claims': '100', 'received_reimbursement': '25', 'phase': 'paid'},
        {'provision': '100', 'cash': '-75', 'reimbursement': '-25'}, {'operating': '-75'})
    step(c, 'assurance.remeasure', {'remaining_claims': '250', 'new_evidence_admitted': True},
        {'provision': '250', 'reimbursement': '125/2', 'phase': 'remeasured'},
        {'provision': '50', 'provision_gain': '-50', 'reimbursement': '-25/2', 'assurance_expense': '25/2'})
    step(c, 'assurance.pay', {'claims_paid': '250', 'reimbursement_received': '125/2'},
        {'provision': '0', 'reimbursement': '0', 'paid_claims': '350', 'received_reimbursement': '175/2', 'phase': 'settled'},
        {'provision': '250', 'cash': '-375/2', 'reimbursement': '-125/2'}, {'operating': '-375/2'})
    c['steps'][-1]['year'] = 2025

    c = case('service-warranty', 'service_contract', {'contract_id': 'service-1', 'price': '108', 'product_ssp': '100',
        'service_ssp': '20', 'product_cost': '60', 'cash_received': '0', 'product_allocation': '0', 'service_allocation': '0',
        'progress': '0', 'revenue': '0', 'service_cost_paid': '0', 'distinct_service': True,
        'faithful_uniform_progress': True, 'product_delivered': False,
        'service_start':'2024-07-01','service_end_exclusive':'2025-07-01','total_service_months':12,'completed_service_months':0},
        {'inventory': '60', 'capital': '-60'}); au.append(c)
    step(c, 'service.receive', {'cash': '108'}, {'cash_received': '108', 'product_allocation': '90', 'service_allocation': '18'},
        {'cash': '108', 'contract_liability': '-108'}, {'operating': '108'})
    step(c, 'service.deliver', {'control_transferred': True}, {'product_delivered': True, 'revenue': '90'},
        {'contract_liability': '90', 'income': '-90', 'expense': '60', 'inventory': '-60'})
    step(c, 'service.progress', {'progress': '1/2', 'completed_service_months':6, 'cash_cost': '3', 'faithful_measure_admitted': True},
        {'progress': '1/2', 'completed_service_months':6, 'revenue': '99', 'service_cost_paid': '3'},
        {'contract_liability': '9', 'income': '-9', 'expense': '3', 'cash': '-3'}, {'operating': '-3'})
    step(c, 'service.progress', {'progress': '1', 'completed_service_months':12, 'cash_cost': '3', 'faithful_measure_admitted': True},
        {'progress': '1', 'completed_service_months':12, 'revenue': '108', 'service_cost_paid': '6'},
        {'contract_liability': '9', 'income': '-9', 'expense': '3', 'cash': '-3'}, {'operating': '-3'})
    c['steps'][-1]['year'] = 2025

    c = case('distinct-amendment', 'distinct_contract', {'contract_id': 'distinct-1', 'total_units': '10',
        'delivered': '0', 'stock_units': '16', 'unit_cost': '6', 'total_price': '100', 'received': '0',
        'recognized': '0', 'remaining_price_per_unit': '10', 'modified': False},
        {'inventory': '96', 'capital': '-96'}); au.append(c)
    step(c, 'distinct.receive', {'cash': '100'}, {'received': '100'}, {'cash': '100', 'contract_liability': '-100'}, {'operating': '100'})
    step(c, 'distinct.deliver', {'units': '4'}, {'delivered': '4', 'stock_units': '12', 'recognized': '40'},
        {'contract_liability': '40', 'income': '-40', 'inventory': '-24', 'expense': '24'})
    step(c, 'distinct.modify', {'added_units': '6', 'added_price': '48', 'cash': '48', 'enforceable': True,
        'remaining_distinct': True, 'separate_contract_test': False},
        {'total_units': '16', 'total_price': '148', 'received': '148', 'remaining_price_per_unit': '9', 'modified': True},
        {'cash': '48', 'contract_liability': '-48'}, {'operating': '48'})
    for delivery, stock, rev in [('10', '6', '94'), ('16', '0', '148')]:
        step(c, 'distinct.deliver', {'units': '6'}, {'delivered': delivery, 'stock_units': stock, 'recognized': rev},
            {'contract_liability': '54', 'income': '-54', 'inventory': '-36', 'expense': '36'})
    c['steps'][-1]['year'] = 2025

    c = case('integrated-amendment', 'integrated_contract', {'contract_id': 'integrated-1', 'price': '100',
        'received': '0', 'progress': '0', 'revenue': '0', 'cost_paid': '0', 'customer_controls_wip': True, 'modified': False},
        {'cash': '50', 'capital': '-50'}); au.append(c)
    step(c, 'integrated.receive', {'cash': '100'}, {'received': '100'}, {'cash': '100', 'contract_liability': '-100'}, {'operating': '100'})
    step(c, 'integrated.perform', {'cumulative_progress': '2/5', 'cash_cost': '30', 'faithful_measure_admitted': True},
        {'progress': '2/5', 'revenue': '40', 'cost_paid': '30'},
        {'contract_liability': '40', 'income': '-40', 'expense': '30', 'cash': '-30'}, {'operating': '-30'})
    step(c, 'integrated.modify', {'new_price': '130', 'new_progress': '3/10', 'cash': '30', 'enforceable': True,
        'remaining_not_distinct': True, 'faithful_measure_admitted': True},
        {'price': '130', 'received': '130', 'progress': '3/10', 'revenue': '39', 'modified': True},
        {'cash': '30', 'contract_liability': '-31', 'income': '1'}, {'operating': '30'})
    step(c, 'integrated.perform', {'cumulative_progress': '1', 'cash_cost': '60', 'faithful_measure_admitted': True},
        {'progress': '1', 'revenue': '130', 'cost_paid': '90'},
        {'contract_liability': '91', 'income': '-91', 'expense': '60', 'cash': '-60'}, {'operating': '-60'})
    c['steps'][-1]['year'] = 2025

    c = case('mixed-amendment', 'mixed_contract', {'contract_id': 'mixed-1', 'construction_price': '100',
        'expected_cost': '80', 'cost_incurred': '0', 'construction_revenue': '0', 'visit_price': '5',
        'visits_total': '4', 'visits_done': '0', 'visit_revenue': '0', 'visit_cost_paid': '0', 'received': '0',
        'modified': False, 'allocation_admitted': True, 'faithful_cost_progress': True}, {'cash': '100', 'capital': '-100'}); au.append(c)
    step(c, 'mixed.receive', {'cash': '120'}, {'received': '120'}, {'cash': '120', 'contract_liability': '-120'}, {'operating': '120'})
    step(c, 'mixed.perform', {'construction_cash_cost': '40', 'visits': '1', 'visit_cash_cost': '2'},
        {'cost_incurred': '40', 'construction_revenue': '50', 'visits_done': '1', 'visit_revenue': '5', 'visit_cost_paid': '2'},
        {'contract_liability': '55', 'income': '-55', 'expense': '42', 'cash': '-42'}, {'operating': '-42'})
    step(c, 'mixed.modify', {'new_construction_price': '140', 'new_expected_cost': '100', 'new_visits_total': '6',
        'cash': '50', 'enforceable': True, 'allocations_admitted': True},
        {'construction_price': '140', 'expected_cost': '100', 'construction_revenue': '56',
         'visits_total': '6', 'received': '170', 'modified': True},
        {'cash': '50', 'contract_liability': '-44', 'income': '-6'}, {'operating': '50'})
    step(c, 'mixed.perform', {'construction_cash_cost': '0', 'visits': '2', 'visit_cash_cost': '4'},
        {'visits_done': '3', 'visit_revenue': '15', 'visit_cost_paid': '6'},
        {'contract_liability': '10', 'income': '-10', 'expense': '4', 'cash': '-4'}, {'operating': '-4'})
    step(c, 'mixed.perform', {'construction_cash_cost': '60', 'visits': '3', 'visit_cash_cost': '6'},
        {'cost_incurred': '100', 'construction_revenue': '140', 'visits_done': '6', 'visit_revenue': '30', 'visit_cost_paid': '12'},
        {'contract_liability': '99', 'income': '-99', 'expense': '66', 'cash': '-66'}, {'operating': '-66'})
    c['steps'][-1]['year'] = 2025

    for role in ['principal', 'agent']:
        c = case(role, 'agency', {'promise_id': 'promise-1', 'role': role, 'control_finding': True,
            'cash_controlled': True, 'supplier_price': '100', 'customer_price': '120', 'inventory': '0', 'payable': '0', 'phase': 'opening'}, {}); au.append(c)
        if role == 'principal':
            step(c, 'agency.acquire', {'cost': '100'}, {'inventory': '100', 'payable': '100', 'phase': 'acquired'},
                {'inventory': '100', 'payable': '-100'})
        step(c, 'agency.transfer', {'cash': '120', 'promise_satisfied': True}, {'inventory': '0', 'payable': '100', 'phase': 'transferred'},
            {'cash': '120', 'income': '-120', 'expense': '100', 'inventory': '-100'} if role == 'principal' else
            {'cash': '120', 'income': '-20', 'payable': '-100'}, {'operating': '120'})
        step(c, 'agency.remit', {'cash': '100'}, {'payable': '0', 'phase': 'settled'}, {'payable': '100', 'cash': '-100'}, {'operating': '-100'})

    c = case('joint-products', 'joint_products', {'batch_id': 'joint-1', 'joint_cost': '300', 'units_a': '60', 'units_b': '40',
        'split_price_a': '4', 'split_price_b': '9', 'cost_a': '0', 'cost_b': '0', 'sold_a': '0', 'sold_b': '0',
        'relative_sales_admitted': True, 'phase': 'opening'}, {'cash': '500', 'capital': '-500'})
    step(c, 'joint.allocate', {'cash_cost': '300'}, {'cost_a': '120', 'cost_b': '180', 'phase': 'allocated'},
        {'inventory': '300', 'cash': '-300'}, {'operating': '-300'})
    step(c, 'joint.sell', {'units_a': '30', 'units_b': '10', 'cash': '210'}, {'cost_a': '60', 'cost_b': '135',
        'sold_a': '30', 'sold_b': '10', 'phase': 'sold'}, {'cash': '210', 'income': '-210', 'inventory': '-105', 'expense': '105'}, {'operating': '210'})
    c = case('byproduct', 'byproduct', {'batch_id': 'byproduct-1', 'production_cost': '300', 'byproduct_nrv': '20',
        'main_cost': '0', 'byproduct_cost': '0', 'immaterial_admitted': True, 'phase': 'opening'}, {'cash': '500', 'capital': '-500'})
    step(c, 'byproduct.allocate', {'cash_cost': '300'}, {'main_cost': '280', 'byproduct_cost': '20', 'phase': 'allocated'},
        {'inventory': '300', 'cash': '-300'}, {'operating': '-300'})
    step(c, 'byproduct.sell', {'cash': '20'}, {'byproduct_cost': '0', 'phase': 'sold'},
        {'cash': '20', 'income': '-20', 'inventory': '-20', 'expense': '20'}, {'operating': '20'})
    c = case('supplier-finance', 'supplier_finance', {'creditor_id': 'supplier-1', 'normal_price': '100', 'final_payment': '121',
        'rate': '1/10', 'carrying': '0', 'inventory_cost': '0', 'years_accrued': 0, 'ordinary_trade_supplier': True,
        'not_qualifying_asset': True, 'phase': 'opening'}, {'cash': '100', 'capital': '-100'})
    step(c, 'supplier.purchase', {'financing_assessment_admitted': True}, {'carrying': '100', 'inventory_cost': '100', 'phase': 'purchased'},
        {'inventory': '100', 'payable': '-100'})
    step(c, 'supplier.accrue', {'full_year_elapsed': True}, {'carrying': '110', 'years_accrued': 1}, {'finance_expense': '10', 'payable': '-10'})
    step(c, 'supplier.sell', {'cash': '150'}, {'inventory_cost': '0', 'phase': 'sold'},
        {'cash': '150', 'income': '-150', 'inventory': '-100', 'expense': '100'}, {'operating': '150'})
    step(c, 'supplier.accrue', {'full_year_elapsed': True}, {'carrying': '121', 'years_accrued': 2}, {'finance_expense': '11', 'payable': '-11'})
    step(c, 'supplier.pay', {'cash': '121'}, {'carrying': '0', 'phase': 'settled'}, {'cash': '-121', 'payable': '121'}, {'operating': '-121'})
    dates = {
        'customer-returns': ['2024-07-01','2024-12-31','2025-06-30','2025-06-30'],
        'assurance-population': ['2024-07-01','2024-10-01','2024-12-31','2025-06-30'],
        'service-warranty': ['2024-07-01','2024-07-01','2024-12-31','2025-06-30'],
        'distinct-amendment': ['2024-01-15','2024-03-31','2024-06-30','2024-12-31','2025-06-30'],
        'integrated-amendment': ['2024-01-15','2024-06-30','2024-12-31','2025-06-30'],
        'mixed-amendment': ['2024-01-15','2024-06-30','2024-07-01','2024-12-31','2025-06-30'],
        'principal': ['2024-01-15','2024-01-16','2024-01-17'],
        'agent': ['2024-01-16','2024-01-17'],
    }
    for c in au:
        c['source_family'] = 'AU_AASB'
        for s, date in zip(c['steps'], dates[c['id']]): s['event_date'] = date
    # Assign economic income/expense roles explicitly; reimbursement is not sales revenue.
    for c in [*au]:
        for s in c['steps']:
            mid=s['method']; family=mid.split('.')[0]
            income = 'product_revenue'
            expense = 'cost_of_sales'
            if family in ['integrated','mixed']: income,expense='service_revenue','service_expense'
            if mid == 'service.progress': income,expense='service_revenue','service_expense'
            if family == 'agency' and c['id'] == 'agent': income='commission_revenue'
            if 'income' in s['journal']:s['journal'][income]=s['journal'].pop('income')
            if 'expense' in s['journal']:s['journal'][expense]=s['journal'].pop('expense')
