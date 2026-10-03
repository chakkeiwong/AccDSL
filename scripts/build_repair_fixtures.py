#!/usr/bin/env python3
"""Author-entered design fixtures. Expected values are not calculated here.

This is not an importer, accounting engine or inference implementation.
The separate checker evaluates journals/constraints against these expectations.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/design/fixtures'

def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def event(id, date, period, postings, cash_class=None, **state):
    return dict(id=id, date=date, period=period,
                postings=[dict(account=a, signed_amount=str(v)) for a, v in postings],
                cash_class=cash_class, state_changes=state)

def main():
    accounts = {
        'cash':'asset', 'receivables':'asset', 'inventory':'asset', 'plant_cost':'asset',
        'accum_depreciation':'contra_asset', 'tax_prepaid':'asset', 'payables':'liability',
        'debt':'liability', 'capital':'equity', 'retained':'equity', 'revenue':'income',
        'cost_of_sales':'expense', 'payroll':'expense', 'depreciation':'expense',
        'interest':'expense', 'tax':'expense'}
    opening = dict(cash='60', receivables='20', inventory='30', plant_cost='100',
                   accum_depreciation='-20', tax_prepaid='0', payables='-20',
                   debt='-100', capital='-50', retained='-20')
    events=[]
    for period,date,rows in [
        ('2024H1','2024-06-30',[
            ('sale',[('receivables',110),('revenue',-110)],None),
            ('collect',[('cash',110),('receivables',-110)],'operating'),
            ('buy',[('inventory',70),('payables',-70)],None),
            ('supplier',[('payables',65),('cash',-65)],'operating'),
            ('deliver',[('cost_of_sales',75),('inventory',-75)],None),
            ('wages',[('payroll',20),('cash',-20)],'operating'),
            ('plant',[('plant_cost',10),('cash',-10)],'investing'),
            ('depreciate',[('depreciation',5),('accum_depreciation',-5)],None),
            ('interest',[('interest','2.5'),('cash','-2.5')],'operating'),
            ('tax',[('tax','1.5'),('tax_prepaid',2),('cash','-3.5')],'operating'),
            ('dividend',[('retained',4),('cash',-4)],'financing')]),
        ('2024H2','2024-12-31',[
            ('sale',[('receivables',150),('revenue',-150)],None),
            ('collect',[('cash',135),('receivables',-135)],'operating'),
            ('buy',[('inventory',85),('payables',-85)],None),
            ('supplier',[('payables',80),('cash',-80)],'operating'),
            ('deliver',[('cost_of_sales',90),('inventory',-90)],None),
            ('wages',[('payroll',22),('cash',-22)],'operating'),
            ('plant',[('plant_cost',12),('cash',-12)],'investing'),
            ('depreciate',[('depreciation',6),('accum_depreciation',-6)],None),
            ('interest',[('interest','2.5'),('cash','-2.5')],'operating'),
            ('tax',[('tax','5.9'),('tax_prepaid',-2),('cash','-3.9')],'operating'),
            ('dividend',[('retained',5),('cash',-5)],'financing')])]:
        for name,postings,cls in rows:events.append(event(period+'.'+name,date,period,postings,cls))
    write('northstar.json',dict(
        schema='accdsl-design-fixture/1', entity='Northstar Components (synthetic)',
        currency='USD', units='one currency unit', basis='DemoCorporate/1; not GAAP certification',
        disclosure_scope='Closed synthetic goods company; the listed source package is complete by construction',
        assumptions={
            'historical_resolution':'half-year aggregate flows; existence of intraperiod schedules required, not recovered invoices',
            'inventory':'one homogeneous good at cost 5; purchases before delivery; quantities equal costs/5',
            'sales':'delivery transfers control; no returns, services, variable consideration or foreign currency',
            'tax':'20% positive taxable profit, all expenses deductible, no deferred tax; excess payment is prepaid tax',
            'plant':'opening cost 100, annual depreciation 10; end-H1 addition 10 lives 5 years; end-H2 addition 12 lives 12 years; zero residuals',
            'debt':'100 throughout; fixed and floating both 5% in 2024; fixed 5%, floating resets to 7% in 2025; all maturities after forecast',
            'time':'half-year accrual fractions 1/2, annual 1; explicit teaching convention',
            'closing':'temporary accounts closed after each H1/H2; annual income uses movements excluding closing',
            'universe':'no omitted company, OCI, acquisition, tax or off-balance-sheet operations inside this synthetic package'},
        accounts=accounts, opening=opening, historical_events=events,
        expected={
            '2024H1':dict(cash='65',receivables='20',inventory='25',plant_net='85',tax_prepaid='2',assets='197',payables='25',debt='100',equity='72',revenue='110',profit='6',operating_cash='19',investing_cash='-10',financing_cash='-4'),
            '2024H2':dict(cash='74.6',receivables='35',inventory='20',plant_net='91',tax_prepaid='0',assets='220.6',payables='30',debt='100',equity='90.6',revenue='150',profit='23.6',operating_cash='26.6',investing_cash='-12',financing_cash='-5'),
            '2024FY':dict(revenue='260',profit='29.6',operating_cash='45.6',investing_cash='-22',financing_cash='-9',cash_change='14.6'),
            '2025_fixed':dict(cash='95.2',receivables='55',inventory='40',plant_net='98',tax_prepaid='0',assets='288.2',payables='40',debt='100',equity='148.2',revenue='300',profit='65.6',interest='5',tax='16.4',operating_cash='48.6',investing_cash='-20',financing_cash='-8'),
            '2025_floating':dict(cash='93.6',receivables='55',inventory='40',plant_net='98',tax_prepaid='0',assets='286.6',payables='40',debt='100',equity='146.6',revenue='300',profit='64',interest='7',tax='16',operating_cash='47',investing_cash='-20',financing_cash='-8')},
        forecast=dict(start='2025-01-01',end_exclusive='2026-01-01',
            demand_units='30',price='10',unit_cost='5',target_inventory_units='8',
            current_sales_collection_fraction='0.9',legacy_receivable_collections='10',
            old_payables_paid='30',new_purchases_paid='130',payroll='50',
            capex_at_period_end='20',dividend='8',tax_rate='0.2',funding_limit='0'),
        coverage_units=[
            dict(id='NS.opening',kind='statement',disposition='structured',content='Opening balance sheet and account balances'),
            dict(id='NS.h1.original',kind='statement',disposition='superseded_reading_preserved',content='Originally revenue 120, receivables 30, tax expense/payment 3.5, profit 14, equity 80'),
            dict(id='NS.h1.correction',kind='note',disposition='structured',content='Premature invoice 10: reverse revenue and receivable; reduce tax expense 2 into tax prepayment; corrected profit 6'),
            dict(id='NS.fy',kind='statement',disposition='structured',content='Annual and revised interim statements derived from listed events'),
            dict(id='NS.operations',kind='policy',disposition='structured',content='Goods, inventory, asset and working-capital assumptions above'),
            dict(id='NS.debt',kind='note',disposition='alternative_family',content='Principal 100, interest 5; fixed/floating composition undisclosed'),
            dict(id='NS.equity',kind='note',disposition='structured',content='Capital 50; original retained 20; dividends H1 4, H2 5'),
            dict(id='NS.reference',kind='cross_reference',disposition='resolved',target='NS.debt',content='Financing note applies to debt and interest in every statement')]))
    write('temporal.json',dict(
        availability_policy='date-only filing is available at next midnight in stated reporting timezone',
        assertions=[
            dict(id='h1-original',key='revenue:H1:USD:NS:Demo',value='120',available='2024-08-01T00:00:00Z',ingested='2024-08-03T00:00:00Z',vintage='v1',supersedes=[]),
            dict(id='h1-restated',key='revenue:H1:USD:NS:Demo',value='110',available='2025-03-02T00:00:00Z',ingested='2025-03-05T00:00:00Z',vintage='v2',supersedes=['h1-original']),
            dict(id='fy',key='revenue:FY:USD:NS:Demo',value='260',available='2025-03-02T00:00:00Z',ingested='2025-03-05T00:00:00Z',vintage='v2',supersedes=[])],
        queries=[
            dict(cutoff='2024-09-01T00:00:00Z',system_as_of=None,expect=['h1-original']),
            dict(cutoff='2025-03-03T00:00:00Z',system_as_of=None,expect=['h1-restated','fy']),
            dict(cutoff='2025-03-03T00:00:00Z',system_as_of='2025-03-04T00:00:00Z',expect=['h1-original']),
            dict(cutoff='2025-03-06T00:00:00Z',system_as_of=None,mode='original',expect=['h1-original','fy'])],
        expected_valid_h2='150', incompatible_vintage_h2='140 must be rejected'))
    write('sectors.json',dict(
        bank=dict(opening=dict(cash='30',gross_loans='100',allowance='0.8',deposits='110',equity='19.2'),
                  events=dict(origination='20',external_transfer='15',loan_interest_cash='6',deposit_interest_accrued='2',allowance_target='2.4'),
                  expected_before_runoff=dict(cash='21',gross_loans='120',allowance='2.4',deposits='117',equity='21.6'),
                  runoff='25',facility_limit='10',expected_draw='4',expected_cash='0',expected_deposits='92',
                  default_runoff='40',expected_unpaid='9',regulatory_deduction='2',risk_weight='0.75',expected_CET1='19.6',expected_RWA='90'),
        insurer=dict(opening_equity='20',premium='120',ceded_premium='24',service_fraction='0.5',gross_claim_estimate='40',gross_claim_paid='30',gross_risk_adjustment='2',recovery_fraction='0.5',recovery_paid='15',ceded_risk_adjustment='1',
                     expected=dict(cash='101',remaining_coverage_liability='60',incurred_claim_liability='12',reinsurance_coverage_asset='12',reinsurance_claim_asset='6',equity='47',profit='27',assets='119',liabilities='72')),
        consolidation=dict(parent_cash='60',investment='40',parent_equity='100',sub_cash='30',sub_plant='20',sub_equity='50',ownership='0.8',
                           expected=dict(cash='90',plant='20',owners_equity='100',NCI='10',assets='110'),
                           intercompany_loan='10',disposal_proceeds='44',expected_disposal_gain='4',expected_after_disposal_cash='104'),
        inventory=dict(purchases=[dict(quantity='10',unit_cost='5'),dict(quantity='10',unit_cost='7')],sold='12',
                       expected=dict(FIFO_cost='64',FIFO_stock='56',LIFO_cost='80',LIFO_stock='40',average_cost='72',average_stock='48'))))
    write('borrowings.json',dict(
        exact=dict(principal='100',historical_rate='0.05',historical_interest='5',fixed_rate='0.05',stress_rate='0.07',cash='95',equity='-5',
                   expected=dict(fixed_interest='5',floating_interest='7',fixed_cash='90',floating_cash='88',fixed_equity='-10',floating_equity='-12')),
        rounded=dict(debt=['99.5','100.5'],interest=['4.5','5.5'],interval='lower closed, upper open',
                     constraints=['F>=0','V>=0','99.5<=F+V<100.5','4.5<=0.05*(F+V)<5.5'],
                     expected_infimum='4.975',expected_infimum_attained=True,expected_supremum='7.035',expected_supremum_attained=False),
        mixture=dict(hypotheses=['fixed','floating'],prior=['0.6','0.4'],likelihood_new_evidence=['0.2','0.8'],
                     expected_posterior=['3/11','8/11'],expected_stress_mean='5.8',
                     partial_failure=dict(fixed='complete',floating='unsupported',successful_mass='0.6',unresolved_mass='0.4',unconditional_mean='unavailable'))))
    print('Wrote five authored fixture packages; use check_repair_conformance.py for independent calculations.')

if __name__ == '__main__':
    main()
