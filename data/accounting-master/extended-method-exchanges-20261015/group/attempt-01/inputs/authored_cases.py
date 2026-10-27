"""Hand-authored facts and expected accounting; financial checker is separate."""
from copy import deepcopy
CASES=[]
def case(key, method, facts, values, journal=None, diagnostics=(), prior=None):
    facts=deepcopy(facts)
    if method=='reciprocal.join@1':facts.update(economic_event_id='internal-event-17',invoice_id='invoice-17',lot_id='lot-17')
    if method=='inventory.eliminate@1':facts.update(internal_date='2026-06-01',external_date='2026-09-30')
    if method=='inventory.release@1':facts.update(external_date='2027-06-30')
    CASES.append(dict(id=key,input=dict(method_id=method,**facts),expected=dict(
        status='unresolved' if diagnostics else 'resolved',diagnostics=list(diagnostics),
        values=values,adjustment_journal=journal or {},
        posting_effect='none' if diagnostics or not journal else 'group_only'),prior=prior))

JOIN=dict(left_amount='100',right_amount='100',allocations=[dict(allocation_id='part-40',invoice_id='invoice-17',amount='40'),dict(allocation_id='part-60',invoice_id='invoice-17',amount='60')],transaction_date='2026-06-01',cutoff='2026-12-31',control_start='2026-03-01',control_end_exclusive='2027-01-01',monetary_fx_difference='3')
JV=dict(matched='100',unmatched='0',balance_elimination='100',performance_eligible=True,fx_difference_retained='3')
case('join-split','reciprocal.join@1',JOIN,JV)
case('join-precontrol','reciprocal.join@1',{**deepcopy(JOIN),'transaction_date':'2026-02-01'},dict(JV,performance_eligible=False))
case('join-unmatched','reciprocal.join@1',{**deepcopy(JOIN),'right_amount':'90','allocations':[dict(allocation_id='part-90',invoice_id='invoice-17',amount='90')]},dict(JV,matched='90',unmatched='10',balance_elimination='90'),diagnostics=['unmatched_reciprocal_amount'])

INV=dict(original_cost='60',internal_price='100',sold_fraction='2/5',external_proceeds='60',parent_cash='90',subsidiary_opening_cash='50',parent_opening_equity='200',investment='50',lot_id='lot-17',internal_event_id='internal-sale-17',external_sale_id='external-sale-40percent')
case('inventory-first','inventory.eliminate@1',INV,dict(cash='200',inventory='36',unrealized_profit='24',group_cogs='24',period_profit='36',cumulative_profit='36',equity='236'),dict(subsidiary_capital='50',investment='-50',payable='100',receivable='-100',revenue='100',cogs='-76',inventory='-24'))
case('inventory-release','inventory.release@1',dict(external_proceeds='80',lot_id='lot-17',external_sale_id='external-sale-remainder',prior_external_sale_id='external-sale-40percent'),dict(cash='280',inventory='0',unrealized_profit='0',group_cogs='36',period_profit='44',cumulative_profit='80',equity='280'),dict(opening_retained='24',cogs='-24'),prior='inventory-first')

INF=dict(cash='100',inventory='60',debt='80',capital='80',indices=[dict(date='2026-01-01',index='100'),dict(date='2026-12-31',index='150')],cash_income=[],nrv=None,closing_rate='1/5',prior_rate='1/4',prior_presentation_date='2025-12-31',rate_date='2026-12-31',rate_from='LC',rate_to='USD',rate_purpose='foreign_operation_presentation',hyperinflation_finding='supplied_admitted',index_basis='general_price_index_supplied',comparative_policy='prior_nonhyperinflationary_presentation_retained')
IV=dict(cash='100',inventory='90',debt='80',capital='120',monetary_loss='10',real_income='0',write_down='0',equity='110',cash_purchasing_power_loss='50',restated_opening_cash='150',restated_cash_flow='0',nominal_cash_flow='0',prior_presentation_cash='25',translated=dict(cash='20',inventory='18',debt='16',capital='24',monetary_loss='2',real_income='0',write_down='0',equity='22'))
case('inflation-static','inflation.restate@1',INF,IV,dict(inventory='30',monetary_loss='10',capital='-40'))
case('inflation-nrv','inflation.restate@1',dict(INF,nrv='84'),dict(IV,inventory='84',write_down='6',equity='104',translated=dict(IV['translated'],inventory='84/5',write_down='6/5',equity='104/5')),dict(inventory='24',monetary_loss='10',capital='-40',write_down='6'))
TIM=deepcopy(INF);TIM['indices'].insert(1,dict(date='2026-06-30',index='125'));TIM['cash_income']=[dict(date='2026-06-30',amount='30',event_id='external-income-30')]
case('inflation-timed','inflation.restate@1',TIM,dict(IV,cash='130',monetary_loss='16',real_income='36',equity='140',cash_purchasing_power_loss='56',restated_cash_flow='36',nominal_cash_flow='30',translated=dict(IV['translated'],cash='26',monetary_loss='16/5',real_income='36/5',equity='28')),dict(inventory='30',monetary_loss='16',capital='-40',revenue='-6'))
case('first-application-tax','inflation.opening_tax@1',dict(cost='40',tax_base='40',tax_rate='1/5',acquisition_index='80',opening_index='100',closing_index='150',acquisition_date='2025-06-01',opening_date='2026-01-01',closing_date='2026-12-31',tax_origin='profit_no_exception_supplied',tax_base_policy='fixed_supplied'),dict(opening_asset='50',opening_dtl='2',restated_opening_dtl='3',closing_asset='75',closing_dtl='7',period_tax_expense='4',closing_equity='68'),dict(inventory='35',tax_expense='4',dtl='-7',capital='-32'))

GW=dict(identifiable_assets='200',recognized_goodwill='40',notional_goodwill='50',recoverable='220',parent_fraction='4/5',notional_support='admitted',nci_measurement='proportionate_share',profit_allocation='same_as_parent_fraction',unit_scope='subsidiary_is_unit')
GV=dict(test_carrying='250',test_loss='30',recognized_loss='24',unrecognized_nci_loss='6',parent_loss='24',nci_loss='0',closing_goodwill='16',closing_assets='200',reported_assets='216',remaining_notional='4')
case('goodwill-partial','goodwill.impair@1',GW,GV,dict(goodwill='-24',impairment_expense='24'))
case('goodwill-severe','goodwill.impair@1',dict(GW,recoverable='180'),dict(test_carrying='250',test_loss='70',recognized_loss='60',unrecognized_nci_loss='10',parent_loss='56',nci_loss='4',closing_goodwill='0',closing_assets='180',reported_assets='180',remaining_notional='0'),dict(goodwill='-40',identifiable_assets='-20',impairment_expense='60'))
case('goodwill-unknown','goodwill.impair@1',dict(GW,notional_support='unknown'),{k:None for k in GV},diagnostics=['notional_goodwill_not_admitted'])
CORP=dict(assets=['40','40','60','60','40'],floors=['0']*5,unit_a_recoverable='70',unit_b_recoverable='130',group_recoverable='207',asset_order=['A1','A2','B1','B2','HQ'],hq_allocation='smallest_combined_group_only',unit_goodwill='none',recoverables='supplied_not_valued')
CV=dict(unit_stage=['35','35','60','60','40'],unit_loss='10',group_test_carrying='230',additional_loss='23',closing_assets=['63/2','63/2','54','54','36'],total_loss='33',closing_total='207')
case('corporate-postorder','corporate_asset.impair@1',CORP,CV,dict(asset_1='-17/2',asset_2='-17/2',asset_3='-6',asset_4='-6',asset_5='-4',impairment_expense='33'))
case('corporate-floor','corporate_asset.impair@1',dict(CORP,floors=['34','0','0','0','0']),dict(CV,closing_assets=['34','1211/39','692/13','692/13','1384/39']),dict(asset_1='-6',asset_2='-349/39',asset_3='-88/13',asset_4='-88/13',asset_5='-176/39',impairment_expense='33'))
case('acquisition-tax','acquisition.tax@1',dict(fair_value_assets='150',tax_base='100',tax_rate='1/4',consideration='150',business_finding='supplied_business',control_finding='supplied_control',tax_origin='acquisition',goodwill_dtl_exception='applies_to_initial_goodwill_only'),dict(identifiable_assets='150',dtl='25/2',net_identifiable_assets='275/2',goodwill='25/2',group_equity='150',legal_cash_posting='0'),dict(subsidiary_capital='150',investment='-150',goodwill='25/2',dtl='-25/2'))

TAX=dict(difference='60',carrying='160',tax_base='100',tax_rate='1/5',controls_reversal='no',no_foreseeable_reversal='yes',probable_reversal='yes',probable_taxable_profit='yes',tax_origin='profit',tax_law='supplied_synthetic')
TV=dict(deferred_tax='12',recognition='recognized',tax_origin='profit')
case('outside-taxable','investment.taxable@1',TAX,TV,dict(tax_expense='12',dtl='-12'))
case('outside-exception','investment.taxable@1',dict(TAX,controls_reversal='yes'),dict(TV,deferred_tax='0',recognition='not_recognized'))
case('outside-tax-unknown','investment.taxable@1',dict(TAX,controls_reversal='unknown'),dict(TV,deferred_tax=None,recognition='unresolved'),diagnostics=['outside_basis_tax_findings_missing'])
case('outside-known-false','investment.taxable@1',dict(TAX,no_foreseeable_reversal='unknown'),TV,dict(tax_expense='12',dtl='-12'))
DTAX=dict(TAX,carrying='100',tax_base='160')
case('outside-deductible','investment.deductible@1',DTAX,TV,dict(dta='12',tax_expense='-12'))
case('outside-profit-absent','investment.deductible@1',dict(DTAX,probable_taxable_profit='no'),dict(TV,deferred_tax='0',recognition='not_recognized'))
case('outside-deductible-unknown','investment.deductible@1',dict(DTAX,probable_reversal='unknown'),dict(TV,deferred_tax=None,recognition='unresolved'),diagnostics=['outside_basis_tax_findings_missing'])
case('outside-no-reversal','investment.deductible@1',dict(DTAX,probable_reversal='no',probable_taxable_profit='unknown'),dict(TV,deferred_tax='0',recognition='not_recognized'))

FX=dict(amount_needed='1000',amount_obtainable='5',enforceable='yes',normal_delay='yes',permitted='yes',significance='insignificant',admitted_rate='2/25',rate_objective='met',foreign_amount='1000',measurement_date='2026-12-31',rate_date='2026-12-31',rate_from='LC',rate_to='USD',rate_purpose='dividends',admission_purpose='dividends',other_purpose_rate='1/10',subsequent_rate='9/100',subsequent_date='2027-01-31',management_intent='hold',ability_basis='supplied_findings_not_intent')
XV=dict(exchangeability='not_exchangeable',availability_ratio='1/200',admitted_rate='2/25',translated_amount='80',estimator='supplied_not_estimated')
case('exchange-limited','exchangeability.assess@1',FX,XV)
case('exchange-significant','exchangeability.assess@1',dict(FX,significance='significant'),dict(XV,exchangeability='exchangeable'))
case('exchange-intent','exchangeability.assess@1',dict(FX,management_intent='exchange'),XV)
case('exchange-rate-missing','exchangeability.assess@1',dict(FX,admitted_rate=None,rate_objective='unknown'),dict(XV,admitted_rate=None,translated_amount=None),diagnostics=['rate_objective_not_admitted'])
case('exchange-objective-failed','exchangeability.assess@1',dict(FX,rate_objective='not_met'),dict(XV,admitted_rate=None,translated_amount=None),diagnostics=['rate_objective_not_admitted'])
case('exchange-finding-unknown','exchangeability.assess@1',dict(FX,significance='unknown'),dict(XV,exchangeability='unresolved',admitted_rate=None,translated_amount=None),diagnostics=['exchangeability_findings_missing'])
case('exchange-inaccessible','exchangeability.assess@1',dict(FX,permitted='no',significance='unknown'),XV)

TRANS=dict(foreign_amount='100',old_rate='10',new_rate='12',transition_kind='monetary_payable',initial_date='2025-01-01',annual_period_start='2025-01-01',rate_date='2025-01-01',rate_from='USD',rate_to='LC',rate_purpose='liability_settlement',rate_admission='orderly_measurement_date_rate_supplied',comparative_restatement=False,transition_destination='opening_retained')
case('transition-payable','exchangeability.transition@1',TRANS,dict(old_carrying='1000',new_carrying='1200',equity_change='-200',destination='opening_retained',comparative_restatement=False,period_profit='0',period_oci='0'),dict(payable='-200',opening_retained='200'))
case('transition-operation','exchangeability.transition@1',dict(TRANS,foreign_amount='1000',old_rate='1/10',new_rate='2/25',transition_kind='foreign_operation',rate_from='LC',rate_to='USD',rate_purpose='foreign_operation_presentation',transition_destination='accumulated_translation'),dict(old_carrying='100',new_carrying='80',equity_change='-20',destination='accumulated_translation',comparative_restatement=False,period_profit='0',period_oci='0'),dict(net_assets='-20',accumulated_translation='20'))
