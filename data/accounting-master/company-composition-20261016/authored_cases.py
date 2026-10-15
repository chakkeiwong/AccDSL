"""Hand-authored inputs and expected effects; never import the financial oracle."""
from copy import deepcopy
from fractions import Fraction as F

OPENING={'date':'2025-01-01','currency':'USD','basis':'historical_EU_IFRS_conditional',
 'entities':['P','S'],'parent':'P','subsidiary':'S','parent_fraction':'4/5',
 'control_start':'2024-01-01','control_end_exclusive':'2026-01-01',
 'same_policies':True,'same_calendar':True,'noninvestment_entity':True,
 'separate_investment_policy':'cost','tax_rate':'1/4','tax_recovery_supported':True,
 'outside_basis_timing_control':True,'outside_basis_no_foreseeable_reversal':True,
 'books':{'P':{'cash':'500','inventory':'60','ppe':'100','recovery_asset':'16','investment':'80','dta':'10',
  'dtl':'-4','refund_liability':'-40','debt':'-100','original_equity':'-10','capital':'-600','retained':'-12'},
  'S':{'cash':'100','capital':'-100'}},
 'returns':{'sold_units':'10','expected_units':'2','unit_refund':'20','unit_cost':'12',
  'estimated_handling':'3','estimated_deterioration':'1','recovery':'16','refund':'40','inventory':'0','settled':False},
 'compound':{'phase':'matured','debt':'100','debt_cash_basis':'90','original_equity':'10','due_date':'2025-01-01','prior_interest_expensed':'10'},
 'lot':{'lot_id':'lot-1','invoice_id':'invoice-1','original_cost':'60','internal_price':'0',
  'sold_fraction':'0','transferred':False,'settled':False},'return_inventory':'0',
 'ownership_purchase':None,'tax_closes':[]}

EVENTS=[]
def add(key,method,date,p,j,cash=None,changes=None):
 EVENTS.append({'id':key,'event':{'method':method,'date':date,'currency':'USD','parameters':p},
  'journals':j,'cash':cash or [],'changes':changes or {}})
def flow(entity,activity,amount,origin):return {'entity':entity,'activity':activity,'amount':str(amount),'origin':origin}
add('redeem','compound.redeem','2025-01-02',{'amount':'100','original_rights_unchanged':True},
 {'P':{'debt':'100','cash':'-100'}},[flow('P','operating',-10,'interest'),flow('P','financing',-90,'principal')],
 {'compound':{**OPENING['compound'],'phase':'ended','debt':'0'}})
add('returns','returns.settle','2025-02-01',{'actual_units':'2','unit_handling':'4','unit_deterioration':'2',
 'refund_cash':'40','handling_cash':'8','inventory_nrv':'20','all_rights_closed':True,'handling_is_selling_cost':True},
 {'P':{'refund_liability':'40','recovery_asset':'-16','inventory':'20','cash':'-48','cogs':'-4','selling_expense':'8'}},
 [flow('P','operating',-40,'refund'),flow('P','operating',-8,'handling')],
 {'returns':{**OPENING['returns'],'refund':'0','recovery':'0','inventory':'20','settled':True},'return_inventory':'20'})
add('wages','payroll.pay','2025-03-01',{'amount':'10','service_received':True,'tax_deductible':True},
 {'P':{'wages':'10','cash':'-10'}},[flow('P','operating',-10,'wages')])
add('depreciate-h1','ppe.depreciate','2025-06-01',{'amount':'10','systematic_basis':True,'tax_matches_book':True},
 {'P':{'depreciation':'10','ppe':'-10'}})
lot={**OPENING['lot'],'internal_price':'140','transferred':True}
add('internal-sale','inventory.transfer','2025-06-02',{'seller':'P','buyer':'S','lot_id':'lot-1','invoice_id':'invoice-1',
 'seller_amount':'140','buyer_amount':'140','cost':'60','counterparty_confirmed':True},
 {'P':{'receivable':'140','revenue':'-140','cogs':'60','inventory':'-60'},'S':{'inventory':'140','payable':'-140'}},changes={'lot':lot})
lot1={**lot,'sold_fraction':'2/5'}
add('external-h1','inventory.sell','2025-06-03',{'entity':'S','lot_id':'lot-1','fraction':'2/5','proceeds':'84','performance_complete':True},
 {'S':{'cash':'84','revenue':'-84','cogs':'56','inventory':'-56'}},[flow('S','operating',84,'external_sale')],{'lot':lot1})
add('internal-settle','intercompany.pay','2025-06-04',{'payer':'S','payee':'P','invoice_id':'invoice-1','payer_amount':'140','payee_amount':'140'},
 {'P':{'cash':'140','receivable':'-140'},'S':{'payable':'140','cash':'-140'}},
 [flow('P','operating',140,'internal'),flow('S','operating',-140,'internal')],{'lot':{**lot1,'settled':True}})
tax_facts={'rate':'1/4','rate_enacted':True,'recovery_supported':True,'temporary_difference_inventory_complete':True,
 'return_tax_timing':'refund_and_recovered_stock_on_settlement','outside_basis_timing_control':True,'outside_basis_no_foreseeable_reversal':True}
add('tax-h1','tax.close','2025-06-30',{'period_start':'2025-01-01','period_end_exclusive':'2025-07-01',**tax_facts},
 {'P':{'current_tax':'8','deferred_tax':'6','cash':'-8','dta':'-10','dtl':'4'},'S':{'current_tax':'7','cash':'-7'}},
 [flow('P','operating',-8,'income_tax'),flow('S','operating',-7,'income_tax')],{'tax_closes':['2025-07-01']})
purchase={'date':'2025-07-01','old_fraction':'4/5','new_fraction':'9/10','consideration':'20','nci_before':'121/5',
 'carrying_reduction':'121/10','parent_equity_debit':'79/10','subsidiary_profit_before':'21'}
add('nci-purchase','ownership.purchase','2025-07-01',{'new_parent_fraction':'9/10','consideration':'20','control_retained':True,'same_rights_per_share':True},
 {'P':{'investment':'20','cash':'-20'}},[flow('P','investing',-20,'nci_purchase')],
 {'parent_fraction':'9/10','ownership_purchase':purchase})
add('external-h2','inventory.sell','2025-08-01',{'entity':'S','lot_id':'lot-1','fraction':'3/5','proceeds':'126','performance_complete':True},
 {'S':{'cash':'126','revenue':'-126','cogs':'84','inventory':'-84'}},[flow('S','operating',126,'external_sale')],
 {'lot':{**lot1,'settled':True,'sold_fraction':'1'}})
add('recovered-sale','inventory.sell','2025-09-01',{'entity':'P','lot_id':'recovered','fraction':'1','proceeds':'40','performance_complete':True},
 {'P':{'cash':'40','revenue':'-40','cogs':'20','inventory':'-20'}},[flow('P','operating',40,'external_sale')],{'return_inventory':'0'})
add('depreciate-h2','ppe.depreciate','2025-12-01',{'amount':'10','systematic_basis':True,'tax_matches_book':True},
 {'P':{'depreciation':'10','ppe':'-10'}})
add('tax-h2','tax.close','2025-12-31',{'period_start':'2025-07-01','period_end_exclusive':'2026-01-01',**tax_facts},
 {'P':{'current_tax':'5/2','cash':'-5/2'},'S':{'current_tax':'21/2','cash':'-21/2'}},
 [flow('P','operating','-5/2','income_tax'),flow('S','operating','-21/2','income_tax')],{'tax_closes':['2025-07-01','2026-01-01']})

EXPECTED_REPORTS={
 'h1':{'start':'2025-01-01','end':'2025-07-01','through':8,
  'group':{'cash':'511','inventory':'56','ppe':'90','dta':'12','dtl':'0','assets':'669','liabilities':'0','equity':'669',
   'revenue':'84','cogs':'20','selling_expense':'8','wages':'10','depreciation':'10','finance_expense':'0','current_tax':'15','deferred_tax':'-6','pretax':'36','profit':'27','nci_profit':'21/5','parent_profit':'114/5','nci_equity':'121/5','parent_equity':'3224/5',
   'operating_receipts':'84','operating_payments':'83','investing_receipts':'0','investing_payments':'0','financing_receipts':'0','financing_payments':'90','interest_paid':'10','tax_paid':'15','net_cash':'-89'},
  'legal':{'P':{'cash':'474','profit':'42','equity':'664','taxable_income':'32'},'S':{'cash':'37','profit':'21','equity':'121','taxable_income':'28'}}},
 'h2':{'start':'2025-07-01','end':'2026-01-01','through':13,
  'group':{'cash':'644','inventory':'0','ppe':'80','dta':'0','dtl':'0','assets':'724','liabilities':'0','equity':'724',
   'revenue':'166','cogs':'56','selling_expense':'0','wages':'0','depreciation':'10','finance_expense':'0','current_tax':'13','deferred_tax':'12','pretax':'100','profit':'75','nci_profit':'63/20','parent_profit':'1437/20','nci_equity':'61/4','parent_equity':'2835/4',
   'operating_receipts':'166','operating_payments':'13','investing_receipts':'0','investing_payments':'0','financing_receipts':'0','financing_payments':'20','interest_paid':'0','tax_paid':'13','net_cash':'133'},
  'legal':{'P':{'cash':'983/2','profit':'15/2','equity':'1343/2','taxable_income':'10'},'S':{'cash':'305/2','profit':'63/2','equity':'305/2','taxable_income':'42'}}},
 'annual':{'start':'2025-01-01','end':'2026-01-01','through':13,
  'group':{'cash':'644','inventory':'0','ppe':'80','dta':'0','dtl':'0','assets':'724','liabilities':'0','equity':'724',
   'revenue':'250','cogs':'76','selling_expense':'8','wages':'10','depreciation':'20','finance_expense':'0','current_tax':'28','deferred_tax':'6','pretax':'136','profit':'102','nci_profit':'147/20','parent_profit':'1893/20','nci_equity':'61/4','parent_equity':'2835/4',
   'operating_receipts':'250','operating_payments':'96','investing_receipts':'0','investing_payments':'0','financing_receipts':'0','financing_payments':'110','interest_paid':'10','tax_paid':'28','net_cash':'44'},
  'legal':{'P':{'cash':'983/2','profit':'99/2','equity':'1343/2','taxable_income':'42'},'S':{'cash':'305/2','profit':'105/2','equity':'305/2','taxable_income':'70'}}}}
