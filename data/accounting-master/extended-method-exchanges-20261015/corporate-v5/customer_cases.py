"""Finite customer examples and explicit expected states; not the verifier."""
from copy import deepcopy

def populate_customer(case,step,cases):
    for order in ['performance-first','invoice-first']:
        c=case('customer-cycle-'+order,'customer_cycle',{'contract_id':'sale-100','price':'100','revenue':'0',
            'advances':[],'invoices':[],'settlement_ids':[],'cash_received':'0','receivable':'0',
            'contract_asset':'0','contract_liability':'0'}, {})
        advance=[{'advance_id':'deposit-30','amount':'30'}]
        invoice={'invoice_id':'bill-80','gross':'80','credits':[{'advance_id':'deposit-30','amount':'30'}],'collected':'0'}
        step(c,'cycle.advance',{'contract_id':'sale-100','advance_id':'deposit-30','cash':'30'},
            {'advances':advance,'cash_received':'30','contract_liability':'30'},
            {'cash':'30','contract_liability':'-30'},{'operating':'30'})
        perform={'contract_id':'sale-100','cumulative_revenue':'60','recognition_admitted':True}
        bill={'contract_id':'sale-100','invoice_id':'bill-80','gross':'80','credits':invoice['credits'],'unconditional_right_admitted':True}
        if order=='performance-first':
            step(c,'cycle.perform',perform,{'revenue':'60','contract_liability':'0','contract_asset':'30'},
                {'contract_liability':'30','contract_asset':'30','product_revenue':'-60'})
            step(c,'cycle.invoice',bill,{'invoices':[deepcopy(invoice)],'receivable':'50','contract_asset':'0','contract_liability':'20'},
                {'receivable':'50','contract_asset':'-30','contract_liability':'-20'})
        else:
            step(c,'cycle.invoice',bill,{'invoices':[deepcopy(invoice)],'receivable':'50','contract_liability':'80'},
                {'receivable':'50','contract_liability':'-50'})
            step(c,'cycle.perform',perform,{'revenue':'60','contract_liability':'20'},
                {'contract_liability':'60','product_revenue':'-60'})
        invoice['collected']='20'
        step(c,'cycle.collect',{'contract_id':'sale-100','invoice_id':'bill-80','settlement_id':'cash-20','cash':'20'},
            {'invoices':[deepcopy(invoice)],'settlement_ids':['cash-20'],'cash_received':'50','receivable':'30'},
            {'cash':'20','receivable':'-20'},{'operating':'20'})
        step(c,'cycle.perform',{'contract_id':'sale-100','cumulative_revenue':'100','recognition_admitted':True},
            {'revenue':'100','contract_asset':'20','contract_liability':'0'},
            {'contract_liability':'20','contract_asset':'20','product_revenue':'-40'})
        final={'invoice_id':'bill-20','gross':'20','credits':[],'collected':'0'}
        step(c,'cycle.invoice',{'contract_id':'sale-100','invoice_id':'bill-20','gross':'20','credits':[],'unconditional_right_admitted':True},
            {'invoices':[deepcopy(invoice),deepcopy(final)],'contract_asset':'0','receivable':'50'},
            {'receivable':'20','contract_asset':'-20'})
        invoice['collected']='50'
        step(c,'cycle.collect',{'contract_id':'sale-100','invoice_id':'bill-80','settlement_id':'cash-30','cash':'30'},
            {'invoices':[deepcopy(invoice),deepcopy(final)],'settlement_ids':['cash-20','cash-30'],'cash_received':'80','receivable':'20'},
            {'cash':'30','receivable':'-30'},{'operating':'30'})
        final['collected']='20'
        step(c,'cycle.collect',{'contract_id':'sale-100','invoice_id':'bill-20','settlement_id':'cash-final-20','cash':'20'},
            {'invoices':[deepcopy(invoice),deepcopy(final)],'settlement_ids':['cash-20','cash-30','cash-final-20'],
                'cash_received':'100','receivable':'0'}, {'cash':'20','receivable':'-20'},{'operating':'20'})

    c=case('customer-cycle-full-prepayment','customer_cycle',{'contract_id':'sale-prepaid','price':'100','revenue':'0',
        'advances':[],'invoices':[],'settlement_ids':[],'cash_received':'0','receivable':'0','contract_asset':'0','contract_liability':'0'}, {})
    step(c,'cycle.advance',{'contract_id':'sale-prepaid','advance_id':'deposit-100','cash':'100'},
        {'advances':[{'advance_id':'deposit-100','amount':'100'}],'cash_received':'100','contract_liability':'100'},
        {'cash':'100','contract_liability':'-100'},{'operating':'100'})
    credits=[{'advance_id':'deposit-100','amount':'100'}]
    step(c,'cycle.invoice',{'contract_id':'sale-prepaid','invoice_id':'prepaid-bill','gross':'100','credits':credits,'unconditional_right_admitted':True},
        {'invoices':[{'invoice_id':'prepaid-bill','gross':'100','credits':credits,'collected':'0'}]}, {})
    step(c,'cycle.perform',{'contract_id':'sale-prepaid','cumulative_revenue':'100','recognition_admitted':True},
        {'revenue':'100','contract_liability':'0'},{'contract_liability':'100','product_revenue':'-100'})

    contracts=[{'contract_id':'original-10','allocation_id':'original-ssp','units':'10','delivered':'0','price':'100','received':'0','revenue':'0'}]
    c=case('separate-contract-addition','separate_addition',{'contracts':deepcopy(contracts),'stock_units':'16','unit_cost':'6',
        'distinct_original_goods_admitted':True},{'cash':'200','inventory':'96','capital':'-296'})
    contracts[0]['received']='100'
    step(c,'separate.receive',{'contract_id':'original-10','cash':'100'},{'contracts':deepcopy(contracts)},
        {'cash':'100','contract_liability':'-100'},{'operating':'100'})
    contracts[0].update(delivered='4',revenue='40')
    step(c,'separate.deliver',{'contract_id':'original-10','units':'4','control_passed':True},
        {'contracts':deepcopy(contracts),'stock_units':'12'},
        {'contract_liability':'40','product_revenue':'-40','inventory':'-24','cost_of_sales':'24'})
    contracts.append({'contract_id':'new-6','allocation_id':'new-ssp','units':'6','delivered':'0','price':'60','received':'0','revenue':'0'})
    step(c,'separate.add',{'new_contract_id':'new-6','allocation_id':'new-ssp','units':'6','price':'60','enforceable':True,
        'distinct_goods':True,'standalone_price_finding':True},{'contracts':deepcopy(contracts)}, {})
    contracts[1]['received']='60'
    step(c,'separate.receive',{'contract_id':'new-6','cash':'60'},{'contracts':deepcopy(contracts)},
        {'cash':'60','contract_liability':'-60'},{'operating':'60'})
    for index,stock in [(0,'6'),(1,'0')]:
        contracts[index].update(delivered=contracts[index]['units'],revenue=contracts[index]['price'])
        step(c,'separate.deliver',{'contract_id':contracts[index]['contract_id'],'units':'6','control_passed':True},
            {'contracts':deepcopy(contracts),'stock_units':stock},
            {'contract_liability':'60','product_revenue':'-60','inventory':'-36','cost_of_sales':'36'})

    c=case('return-recovery-nonzero-costs','return_costs',{'cohort_id':'return-100','units':'100','price':'10','cost':'6',
        'expected_returns':'12','recovery_cost_per_unit':'1','deterioration_per_unit':'1/2','recovery':'0','refund':'0',
        'control_and_scope_admitted':True,'constraint_and_estimate_admitted':True,'measurement_current':True,
        'actual_processing_cost':None,'actual_settlement_cash':None,'phase':'opening'},
        {'cash':'100','inventory':'600','capital':'-700'})
    step(c,'rcost.sell',{'cash':'1000'},{'recovery':'54','refund':'120','phase':'measured'},
        {'cash':'1000','product_revenue':'-880','refund_liability':'-120','inventory':'-600','return_recovery':'54','cost_of_sales':'546'},
        {'operating':'1000'})

    for variant in ['constrained','admitted','modified']:
        stock='16' if variant=='modified' else '10'
        obligations=[{'obligation_id':'original-'+str(i),'original':True,'delivered':False} for i in range(1,11)]
        c=case('variable-distinct-'+variant,'variable_distinct',{'contract_id':'variable-sale',
            'original_allocation_id':'original-equal-ssp','modified_allocation_id':None,'original_delivered_at_modification':[],
            'bonus_promise_id':'original-binary-bonus','obligations':deepcopy(obligations),
            'original_fixed_price':'100','total_fixed_price':'100','promised_bonus':'10','bonus_estimate':'0','bonus_admitted':'0',
            'received':'0','revenue':'0','unit_cost':'6','stock_units':stock,'remaining_fixed_per_unit':'0',
            'equal_original_ssp_admitted':True,'binary_bonus_admitted':True,'constraint_status':'not_assessed','modified':False},
            {'cash':'200','inventory':'96' if variant=='modified' else '60','capital':'-296' if variant=='modified' else '-260'})
        step(c,'variableD.receive',{'cash':'100'},{'received':'100'},
            {'cash':'100','contract_liability':'-100'},{'operating':'100'})
        assessment={'bonus_promise_id':'original-binary-bonus','allocation_id':'original-equal-ssp','estimate':'10',
            'constraint_finding':'constrained','most_likely_measure_admitted':True}
        step(c,'variableD.assess',assessment,{'bonus_estimate':'10','constraint_status':'constrained'}, {})
        for o in obligations[:4]:o['delivered']=True
        step(c,'variableD.deliver',{'obligation_ids':['original-'+str(i) for i in range(1,5)],'control_passed':True},
            {'obligations':deepcopy(obligations),'revenue':'40','stock_units':'12' if variant=='modified' else '6'},
            {'contract_liability':'40','product_revenue':'-40','inventory':'-24','cost_of_sales':'24'})
        if variant=='modified':
            added=['added-'+str(i) for i in range(1,7)]
            obligations += [{'obligation_id':key,'original':False,'delivered':False} for key in added]
            step(c,'variableD.modify',{'added_obligation_ids':added,'added_price':'48','cash':'48',
                'modified_allocation_id':'remaining-fixed-pool','enforceable':True,'remaining_distinct':True,'separate_contract_test':False},
                {'obligations':deepcopy(obligations),'original_delivered_at_modification':['original-'+str(i) for i in range(1,5)],
                    'total_fixed_price':'148','remaining_fixed_per_unit':'9','modified':True,
                    'modified_allocation_id':'remaining-fixed-pool','received':'148'},
                {'cash':'48','contract_liability':'-48'},{'operating':'48'})
        if variant!='constrained':
            step(c,'variableD.receive',{'cash':'10'},{'received':'158' if variant=='modified' else '110'},
                {'cash':'10','contract_liability':'-10'},{'operating':'10'})
            step(c,'variableD.assess',{**assessment,'constraint_finding':'admitted'},
                {'bonus_admitted':'10','constraint_status':'admitted','revenue':'44'},
                {'contract_liability':'4','product_revenue':'-4'})
        for o in obligations[4:10]:o['delivered']=True
        increment={'constrained':'60','admitted':'66','modified':'60'}[variant]
        final_revenue={'constrained':'100','admitted':'110','modified':'104'}[variant]
        step(c,'variableD.deliver',{'obligation_ids':['original-'+str(i) for i in range(5,11)],'control_passed':True},
            {'obligations':deepcopy(obligations),'revenue':final_revenue,'stock_units':'6' if variant=='modified' else '0'},
            {'contract_liability':increment,'product_revenue':'-'+increment,'inventory':'-36','cost_of_sales':'36'})
        if variant=='modified':
            for o in obligations[10:]:o['delivered']=True
            step(c,'variableD.deliver',{'obligation_ids':added,'control_passed':True},
                {'obligations':deepcopy(obligations),'revenue':'158','stock_units':'0'},
                {'contract_liability':'54','product_revenue':'-54','inventory':'-36','cost_of_sales':'36'})

    c=case('variable-integrated-modified','variable_integrated',{'contract_id':'integrated-variable',
        'original_promise_id':'original-construction','modified_promise_id':None,'original_allocation_id':'original-ssp',
        'modified_allocation_id':None,'bonus_promise_id':'construction-bonus','fixed_price':'100','promised_bonus':'10',
        'bonus_estimate':'0','bonus_admitted':'0','received':'0','progress':'0','revenue':'0','cost_paid':'0',
        'binary_bonus_admitted':True,'customer_controls_wip':True,'constraint_status':'not_assessed','modified':False},
        {'cash':'200','capital':'-200'})
    step(c,'variableI.receive',{'cash':'100'},{'received':'100'},
        {'cash':'100','contract_liability':'-100'},{'operating':'100'})
    assessment={'bonus_promise_id':'construction-bonus','allocation_id':'original-ssp','promise_id':'original-construction',
        'estimate':'10','constraint_finding':'constrained','most_likely_measure_admitted':True}
    step(c,'variableI.assess',assessment,{'bonus_estimate':'10','constraint_status':'constrained'}, {})
    step(c,'variableI.perform',{'cumulative_progress':'2/5','cash_cost':'30','faithful_measure_admitted':True},
        {'progress':'2/5','revenue':'40','cost_paid':'30'},
        {'cash':'-30','service_expense':'30','contract_liability':'40','service_revenue':'-40'},{'operating':'-30'})
    step(c,'variableI.modify',{'new_fixed_price':'130','new_progress':'3/10','cash':'30',
        'modified_promise_id':'modified-construction','modified_allocation_id':'modified-ssp',
        'enforceable':True,'remaining_not_distinct':True,'faithful_measure_admitted':True},
        {'fixed_price':'130','progress':'3/10','received':'130','revenue':'39','modified':True,
            'modified_promise_id':'modified-construction','modified_allocation_id':'modified-ssp'},
        {'cash':'30','contract_liability':'-31','service_revenue':'1'},{'operating':'30'})
    step(c,'variableI.receive',{'cash':'10'},{'received':'140'},
        {'cash':'10','contract_liability':'-10'},{'operating':'10'})
    step(c,'variableI.assess',{**assessment,'allocation_id':'modified-ssp','promise_id':'modified-construction','constraint_finding':'admitted'},
        {'bonus_admitted':'10','constraint_status':'admitted','revenue':'42'},
        {'contract_liability':'3','service_revenue':'-3'})
    step(c,'variableI.perform',{'cumulative_progress':'1','cash_cost':'50','faithful_measure_admitted':True},
        {'progress':'1','revenue':'140','cost_paid':'80'},
        {'cash':'-50','service_expense':'50','contract_liability':'98','service_revenue':'-98'},{'operating':'-50'})

    c=case('unmeasurable-progress-recovery','progress_recovery',{'contract_id':'service-recovery','promise_id':'service-over-time',
        'price':'100','received':'0','revenue':'0','cost_paid':'0','progress':None,
        'over_time_admitted':True,'costs_expensed_admitted':True,'measurement_status':'opening'},
        {'cash':'100','capital':'-100'})
    step(c,'recovery.receive',{'cash':'100'},{'received':'100'},
        {'cash':'100','contract_liability':'-100'},{'operating':'100'})
    step(c,'recovery.perform',{'measurement_available':False,'cumulative_progress':None,'cash_cost':'30',
        'costs_recoverable':True,'faithful_measure_admitted':None},
        {'cost_paid':'30','revenue':'30','measurement_status':'cost_recovery'},
        {'cash':'-30','service_expense':'30','contract_liability':'30','service_revenue':'-30'},{'operating':'-30'})
    step(c,'recovery.perform',{'measurement_available':True,'cumulative_progress':'2/5','cash_cost':'0',
        'costs_recoverable':None,'faithful_measure_admitted':True},
        {'progress':'2/5','revenue':'40','measurement_status':'measured'},
        {'contract_liability':'10','service_revenue':'-10'})
    step(c,'recovery.perform',{'measurement_available':True,'cumulative_progress':'1','cash_cost':'40',
        'costs_recoverable':None,'faithful_measure_admitted':True},
        {'progress':'1','revenue':'100','cost_paid':'70'},
        {'cash':'-40','service_expense':'40','contract_liability':'60','service_revenue':'-60'},{'operating':'-40'})

    # Exact synthetic dates exercise the retained historical AU source interval.
    for c in cases:
        if c['tag'] not in {'customer_cycle','separate_addition','return_costs','variable_distinct','variable_integrated','progress_recovery'}:continue
        c['source_family']='AU_AASB'
        for i,s in enumerate(c['steps'],1):s['event_date']='2024-06-'+str(i).zfill(2)
