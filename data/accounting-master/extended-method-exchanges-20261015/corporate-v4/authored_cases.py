"""Explicit illustrative inputs and authored expectations, independently checked elsewhere."""
from copy import deepcopy
from asset_cases import populate_assets

CASES = []

def case(key, tag, component, balances, tax='uncomputed'):
    value = {'id': key, 'tag': tag, 'opening_component': component, 'opening_balances': balances,
             'tax_status': tax, 'steps': []}
    CASES.append(value)
    return value

def step(c, method, parameters, changes, lines, cash=None):
    before = c['steps'][-1]['after'] if c['steps'] else c['opening_component']
    after = {**deepcopy(before), **changes}
    c['steps'].append({'method': method, 'parameters': parameters, 'after': after,
                      'journal': lines, 'cash_change': cash or {}})

for policy, cost, remaining in [('fifo', '1300', '260'), ('weighted_average', '11680/9', '2360/9')]:
    c = case('production-' + policy, 'production', {
        'stage_id': 'factory-stage-1', 'policy': policy, 'opening_units': '10', 'opening_material': '100',
        'opening_conversion': '50', 'opening_fraction': '1/2', 'started': '0', 'current_material': '0',
        'current_conversion': '0', 'completed': '0', 'closing_units': '10', 'closing_fraction': '1/2',
        'wip_cost': '150', 'finished_cost': '0', 'phase': 'opening'},
        {'cash': '2000', 'wip': '150', 'capital': '-2150'})
    step(c, 'production.accumulate', {'started': '90', 'material_cost': '900', 'conversion_cost': '510'},
         {'started': '90', 'current_material': '900', 'current_conversion': '510', 'wip_cost': '1560',
          'closing_units': None, 'closing_fraction': None, 'phase': 'accumulated'},
         {'wip': '1410', 'payable': '-1410'})
    step(c, 'production.complete', {'completed': '80', 'closing_units': '20', 'closing_fraction': '1/2', 'rounding': 'exact'},
         {'completed': '80', 'closing_units': '20', 'closing_fraction': '1/2', 'wip_cost': remaining,
          'finished_cost': cost, 'phase': 'completed'}, {'wip': '-' + cost, 'finished_goods': cost})

c = case('abnormal-loss', 'lossbatch', {'batch_id': 'batch-1', 'input_units': '100', 'normal_output': '95',
    'good_output': None, 'cost_pool': '1000', 'finished_cost': '0', 'abnormal_cost': '0',
    'full_effort': True, 'no_salvage': True, 'no_fixed_overhead': True, 'phase': 'unallocated'},
    {'cash': '100', 'wip': '1000', 'capital': '-1100'})
step(c, 'production.loss', {'good_output': '90', 'normal_output_admitted_before_observation': True},
    {'good_output': '90', 'finished_cost': '18000/19', 'abnormal_cost': '1000/19', 'phase': 'allocated'},
    {'wip': '-1000', 'finished_goods': '18000/19', 'expense': '1000/19'})

c = case('inspection', 'inspection', {'asset_id': 'machine-1', 'inspection_id': 'inspection-old',
    'physical_carrying': '80', 'inspection_carrying': '10', 'physical_life': '8', 'inspection_life': '2',
    'zero_residual': True}, {'cash': '100', 'ppe': '90', 'capital': '-190'})
step(c, 'inspection.replace', {'new_inspection_id': 'inspection-new', 'new_cost': '24', 'new_life': '4',
    'qualifies': True, 'old_allocation_known': True, 'old_carrying_current': True},
    {'inspection_id': 'inspection-new', 'inspection_carrying': '24', 'inspection_life': '4'},
    {'expense': '10', 'ppe': '14', 'cash': '-24'}, {'investing': '-24'})
step(c, 'inspection.consume', {'years': '1'}, {'physical_carrying': '70', 'inspection_carrying': '18',
    'physical_life': '7', 'inspection_life': '3'}, {'expense': '16', 'ppe': '-16'})

c = case('lease', 'lease', {'right_id': 'space-1', 'rou': '80', 'liability': '100', 'remaining_payment': '110',
    'rate': '1/10', 'usage_due': '0', 'periods_remaining': 1, 'homogeneous': True},
    {'cash': '120', 'rou': '80', 'lease_liability': '-100', 'capital': '-100'})
step(c, 'lease.reduce', {'surrendered_fraction': '1/4', 'new_payment': '352/5', 'new_rate': '1/10',
    'same_remaining_term': True, 'no_termination_fee': True}, {'rou': '49', 'liability': '64', 'remaining_payment': '352/5'},
    {'lease_liability': '36', 'rou': '-31', 'income': '-5'})
step(c, 'lease.usage', {'units': '3', 'unit_fee': '2', 'non_index_variable': True, 'capitalization_required': False},
    {'usage_due': '6'}, {'expense': '6', 'payable': '-6'})
step(c, 'lease.mature', {'cash_payment': '352/5', 'one_period_elapsed': True},
    {'rou': '0', 'liability': '0', 'remaining_payment': '0', 'periods_remaining': 0},
    {'expense': '49', 'rou': '-49', 'finance_expense': '32/5', 'lease_liability': '64', 'cash': '-352/5'},
    {'financing': '-64', 'operating': '-32/5'})

c = case('benefits', 'benefit', {'plan_id': 'pension-1', 'dbo': '1000', 'plan_assets': '900',
    'no_ceiling_required': True, 'phase': 'opening'}, {'cash': '500', 'pension_liability': '-100', 'capital': '-400'})
step(c, 'benefit.remeasure', {'dbo': '1100', 'plan_assets': '920'},
    {'dbo': '1100', 'plan_assets': '920', 'phase': 'remeasured'}, {'oci_pension': '80', 'pension_liability': '-80'})
step(c, 'benefit.curtail', {'dbo_reduction': '150', 'no_earlier_trigger': True},
    {'dbo': '950', 'phase': 'curtailed'}, {'pension_liability': '150', 'income': '-150'})
step(c, 'benefit.settle', {'dbo_discharged': '200', 'plan_assets_paid': '170', 'company_cash_paid': '20', 'legal_discharge': True},
    {'dbo': '750', 'plan_assets': '750', 'phase': 'settled'}, {'pension_liability': '30', 'cash': '-20', 'income': '-10'},
    {'operating': '-20'})
step(c, 'benefit.service', {'service_cost': '30', 'annual_rate': '1/20', 'year_fraction': '1/2', 'simple_accrual': True},
    {'dbo': '3195/4', 'plan_assets': '3075/4', 'phase': 'service'}, {'expense': '30', 'pension_liability': '-30'})

c = case('past-funding', 'funding', {'plan_id': 'pension-2', 'dbo': '100', 'plan_assets': '120',
    'unavailable_surplus': True, 'required_funding': '0', 'recognized_obligation': '0', 'paid': '0'},
    {'cash': '100', 'capital': '-100'})
step(c, 'funding.recognize', {'required_amount': '10', 'past_service': True, 'wholly_unavailable_after_payment': True},
    {'required_funding': '10', 'recognized_obligation': '10'}, {'oci_pension': '10', 'pension_liability': '-10'})
step(c, 'funding.pay', {'cash_paid': '10'}, {'plan_assets': '130', 'recognized_obligation': '0', 'paid': '10'},
    {'pension_liability': '10', 'cash': '-10'}, {'operating': '-10'})

for key, ppe, liability, capital, new, recoverable, after_ppe, impairment, lines in [
    ('restoration-increase', '80', '20', '-160', '50', '90', '90', '20', {'ppe': '10', 'provision': '-30', 'expense': '20'}),
    ('restoration-decrease', '30', '80', '-50', '30', None, '0', '0', {'provision': '50', 'ppe': '-30', 'income': '-20'}),
    ('restoration-exhausted', '0', '20', '-80', '25', None, '0', '0', {'provision': '-5', 'expense': '5'}),
]:
    c = case(key, 'restoration', {'asset_id': 'plant-1', 'liability_id': 'restore-1', 'ppe': ppe,
        'liability': liability, 'life': '0' if key.endswith('exhausted') else '4', 'impairment_to_date': '0',
        'original_cost_includes_liability': True}, {'cash': '100', 'ppe': ppe, 'provision': '-' + liability, 'capital': capital})
    step(c, 'restoration.change', {'new_liability': new, 'recoverable_amount': recoverable, 'measurement_current': True},
         {'ppe': after_ppe, 'liability': new, 'impairment_to_date': impairment}, lines)
    if key.endswith('exhausted'):
        step(c, 'restoration.pay', {'cash_paid': '25', 'classification': 'operating',
             'classification_status': 'provisional_supplied_interpretation'}, {'liability': '0'},
             {'provision': '25', 'cash': '-25'}, {'operating': '-25'})

c = case('impairment-floor', 'impairment', {'cgu_id': 'cgu-1', 'goodwill': '20', 'goodwill_loss': '0',
    'assets': [{'asset_id': 'A', 'carrying': '60', 'floor': '55', 'valuation_status': 'known', 'loss_to_date': '0'},
               {'asset_id': 'B', 'carrying': '40', 'floor': '5', 'valuation_status': 'known', 'loss_to_date': '0'}],
    'unit_recoverable': None, 'allocated': False}, {'cash': '80', 'ppe': '100', 'goodwill': '20', 'capital': '-200'})
step(c, 'impairment.allocate', {'unit_recoverable': '70', 'perimeter_consistent': True},
    {'goodwill': '0', 'goodwill_loss': '20', 'assets': [
        {'asset_id': 'A', 'carrying': '55', 'floor': '55', 'valuation_status': 'known', 'loss_to_date': '5'},
        {'asset_id': 'B', 'carrying': '15', 'floor': '5', 'valuation_status': 'known', 'loss_to_date': '25'}],
     'unit_recoverable': '70', 'allocated': True}, {'expense': '50', 'goodwill': '-20', 'ppe': '-30'})

c = case('revalued-tax', 'tax_origin', {'asset_id': 'revalued-asset-1', 'carrying': '140', 'tax_base': '100',
    'rate': '1/4', 'dtl': '10', 'dta': '0', 'gross_surplus': '40', 'recovery_probable': True, 'rate_enacted': True},
    {'ppe': '140', 'dtl': '-10', 'capital': '-100', 'oci_revaluation': '-30'}, 'computed_origin_only')
step(c, 'tax.revalue_impair', {'recoverable': '90', 'no_time_or_base_change': True},
    {'carrying': '90', 'dtl': '0', 'dta': '5/2', 'gross_surplus': '0'},
    {'ppe': '-50', 'oci_revaluation': '30', 'expense': '10', 'dtl': '10', 'dta': '5/2', 'tax_expense': '-5/2'})

c = case('prepaid-bill', 'advance', {'contract_id': 'contract-1', 'bill_id': 'bill-1',
    'unallocated_advance': '100', 'nominal_bill': '100', 'bill_allocated': False},
    {'cash': '100', 'contract_liability': '-100'})
step(c, 'advance.allocate', {'bill_id': 'bill-1', 'gross_bill': '100'},
    {'unallocated_advance': '0', 'bill_allocated': True}, {})

from additional_cases import populate
populate(case, step)
for c in CASES:
    if c['tag'] in ['joint_products','byproduct','supplier_finance']:
        for s in c['steps']:
            if 'income' in s['journal']:s['journal']['product_revenue']=s['journal'].pop('income')
            if 'expense' in s['journal']:s['journal']['cost_of_sales']=s['journal'].pop('expense')

populate_assets(case, step)
from benefit_tax_cases import populate_benefit_tax
populate_benefit_tax(case, step)
