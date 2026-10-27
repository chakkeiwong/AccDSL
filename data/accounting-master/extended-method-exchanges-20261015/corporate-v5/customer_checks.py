"""Independent derivations from event facts; imports no author/builder modules."""
from copy import deepcopy
from fractions import Fraction as F
FAMILIES={'cycle','separate','rcost','variableD','variableI','recovery'}
TAGS={'customer_cycle','separate_addition','return_costs','variable_distinct','variable_integrated','progress_recovery'}

def cycle_values(c):
    advances={a['advance_id']:a['amount'] for a in c['advances']}
    assert len(advances)==len(c['advances']) and all(v>0 for v in advances.values())
    used={k:F(0) for k in advances};g=k=collected=F(0);ids=set()
    for invoice in c['invoices']:
        assert invoice['invoice_id'] not in ids;ids.add(invoice['invoice_id'])
        g+=invoice['gross'];subtotal=F(0);seen=set()
        for credit in invoice['credits']:
            key=credit['advance_id'];assert key in advances and key not in seen and credit['amount']>0
            seen.add(key);used[key]+=credit['amount'];subtotal+=credit['amount']
        assert invoice['gross']>0 and 0<=invoice['collected']<=invoice['gross']-subtotal
        k+=subtotal;collected+=invoice['collected']
    assert all(used[key]<=v for key,v in advances.items())
    a=sum(advances.values(),F(0));t=g+a-k;r=c['revenue']
    assert 0<=r<=c['price'] and 0<=t<=c['price'] and len(set(c['settlement_ids']))==len(c['settlement_ids'])
    return {'cash_received':a+collected,'receivable':g-k-collected,
        'contract_asset':max(r-t,F(0)),'contract_liability':max(t-r,F(0))},used

def distinct_revenue(c):
    originals=[o for o in c['obligations'] if o['original']]
    original_rate=c['original_fixed_price']/len(originals)
    prior=set(c['original_delivered_at_modification'])
    fixed=sum((original_rate if not c['modified'] or o['obligation_id'] in prior else c['remaining_fixed_per_unit'])
        for o in c['obligations'] if o['delivered'])
    return fixed+c['bonus_admitted']*sum(o['delivered'] for o in originals)/len(originals)

def calculate_customer(original,method,p,require):
    c=deepcopy(original);j={};cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    def line(a,v):j[a]=j.get(a,F(0))+v
    family,action=method.split('.')
    if family=='cycle':
        require(p['contract_id']==c['contract_id'],'customer_contract_mismatch')
        old,_=cycle_values(c)
        if action=='advance':
            require(c['revenue']==0 and not c['invoices'],'advance_timing_unsupported','unsupported')
            require(p['advance_id'] not in {a['advance_id'] for a in c['advances']},'advance_identity_reused')
            require(p['cash']>0 and old['cash_received']+p['cash']<=c['price'],'advance_amount_invalid')
            c['advances'].append({'advance_id':p['advance_id'],'amount':p['cash']})
        elif action=='perform':
            require(p['recognition_admitted'],'performance_finding_unresolved','partial')
            require(c['revenue']<p['cumulative_revenue']<=c['price'],'performance_amount_invalid')
            c['revenue']=p['cumulative_revenue']
        elif action=='invoice':
            require(p['unconditional_right_admitted'],'unconditional_right_unresolved','partial')
            require(p['invoice_id'] not in {i['invoice_id'] for i in c['invoices']},'invoice_identity_reused')
            av={a['advance_id']:a['amount'] for a in c['advances']};_,used=cycle_values(c);seen=set();credits=F(0)
            for item in p['credits']:
                key=item['advance_id']
                require(key in av,'advance_contract_mismatch')
                require(key not in seen and 0<item['amount']<=av[key]-used[key],'advance_credit_reused')
                seen.add(key);credits+=item['amount']
            require(p['gross']>0 and credits<=p['gross'],'invoice_amount_invalid')
            prior_t=old['cash_received']+old['receivable']
            require(prior_t+p['gross']-credits<=c['price'],'contract_entitlement_exceeded')
            c['invoices'].append({'invoice_id':p['invoice_id'],'gross':p['gross'],'credits':deepcopy(p['credits']),'collected':F(0)})
        elif action=='collect':
            found=[i for i in c['invoices'] if i['invoice_id']==p['invoice_id']]
            require(len(found)==1,'invoice_contract_mismatch')
            require(p['settlement_id'] not in c['settlement_ids'],'settlement_identity_reused')
            i=found[0];due=i['gross']-sum(x['amount'] for x in i['credits'])-i['collected']
            require(0<p['cash']<=due,'collection_exceeds_right')
            i['collected']+=p['cash'];c['settlement_ids'].append(p['settlement_id'])
        values,_=cycle_values(c);c.update(values)
        for account,key,sign in [('cash','cash_received',1),('receivable','receivable',1),
            ('contract_asset','contract_asset',1),('contract_liability','contract_liability',-1)]:
            line(account,sign*(values[key]-old[key]))
        line('product_revenue',original['revenue']-c['revenue']);cash['operating']=values['cash_received']-old['cash_received']
    elif family=='separate':
        require(c['distinct_original_goods_admitted'],'distinct_goods_unresolved','partial')
        if action=='add':
            require(p['enforceable'] and p['distinct_goods'],'separate_addition_conditions_failed')
            require(p['standalone_price_finding'] is not None,'standalone_price_unresolved','partial')
            require(p['standalone_price_finding'],'separate_contract_test_failed')
            require(p['new_contract_id'] not in {x['contract_id'] for x in c['contracts']},'separate_contract_identity_reused')
            require(p['allocation_id'] not in {x['allocation_id'] for x in c['contracts']},'allocation_identity_reused')
            require(p['units']>0 and p['price']>0 and p['units'].denominator==1,'separate_addition_amount')
            committed=sum(x['units']-x['delivered'] for x in c['contracts'])
            require(committed+p['units']<=c['stock_units'],'unfunded_stock_allocation')
            c['contracts'].append({'contract_id':p['new_contract_id'],'allocation_id':p['allocation_id'],
                'units':p['units'],'delivered':F(0),'price':p['price'],'received':F(0),'revenue':F(0)})
        else:
            found=[x for x in c['contracts'] if x['contract_id']==p['contract_id']]
            require(len(found)==1,'separate_contract_identity_unknown');x=found[0]
            if action=='receive':
                require(0<p['cash']<=x['price']-x['received'],'separate_receipt_amount')
                x['received']+=p['cash'];line('cash',p['cash']);line('contract_liability',-p['cash']);cash['operating']=p['cash']
            else:
                require(p['control_passed'],'performance_finding_unresolved','partial')
                require(0<p['units']<=x['units']-x['delivered'] and p['units'].denominator==1,'separate_delivery_amount')
                revenue=p['units']*x['price']/x['units'];cost=p['units']*c['unit_cost']
                require(x['received']-x['revenue']>=revenue,'cross_contract_funding_forbidden')
                x['delivered']+=p['units'];x['revenue']+=revenue;c['stock_units']-=p['units']
                line('contract_liability',revenue);line('product_revenue',-revenue);line('inventory',-cost);line('cost_of_sales',cost)
    elif family=='rcost':
        if action=='settle':
            require(p['actual_processing_cost'] is not None and p['actual_settlement_cash'] is not None,
                'actual_return_settlement_unresolved','partial')
            require(False,'nonzero_cost_settlement_method_not_specified','unsupported')
        require(c['phase']=='opening','return_measurement_already_posted')
        require(c['control_and_scope_admitted'] and c['constraint_and_estimate_admitted'] and c['measurement_current'],
            'return_measurement_unresolved','partial')
        net=c['cost']-c['recovery_cost_per_unit']-c['deterioration_per_unit']
        require(0<=c['expected_returns']<=c['units'] and min(c['recovery_cost_per_unit'],c['deterioration_per_unit'],net)>=0,'return_cost_measurement_invalid')
        require(p['cash']==c['units']*c['price'],'return_cash_mismatch')
        c['recovery']=c['expected_returns']*net;c['refund']=c['expected_returns']*c['price'];c['phase']='measured'
        line('cash',p['cash']);line('product_revenue',-(p['cash']-c['refund']));line('refund_liability',-c['refund'])
        line('inventory',-c['units']*c['cost']);line('return_recovery',c['recovery'])
        line('cost_of_sales',c['units']*c['cost']-c['recovery']);cash['operating']=p['cash']
    elif family=='variableD':
        require(c['equal_original_ssp_admitted'] and c['binary_bonus_admitted'],'variable_allocation_premises_unresolved','partial')
        if action=='receive':
            require(0<p['cash']<=c['total_fixed_price']+c['promised_bonus']-c['received'],'variable_receipt_amount')
            c['received']+=p['cash'];line('cash',p['cash']);line('contract_liability',-p['cash']);cash['operating']=p['cash']
        elif action=='deliver':
            require(p['control_passed'],'performance_finding_unresolved','partial')
            ids=p['obligation_ids'];mapping={o['obligation_id']:o for o in c['obligations']}
            require(len(set(ids))==len(ids) and all(k in mapping and not mapping[k]['delivered'] for k in ids),'variable_delivery_identity')
            require(len(ids)<=c['stock_units'],'variable_stock_shortage')
            for key in ids:mapping[key]['delivered']=True
            c['stock_units']-=len(ids)
            cost=len(ids)*c['unit_cost'];line('inventory',-cost);line('cost_of_sales',cost)
        elif action=='modify':
            require(not c['modified'] and p['enforceable'] and p['remaining_distinct'],'variable_modification_conditions')
            require(not p['separate_contract_test'],'variable_separate_contract_requires_paragraph20','unsupported')
            ids=p['added_obligation_ids'];existing={o['obligation_id'] for o in c['obligations']}
            require(len(set(ids))==len(ids) and not (set(ids)&existing),'variable_added_identity')
            require(p['modified_allocation_id']!=c['original_allocation_id'],'allocation_identity_reused')
            require(p['added_price']>=0 and 0<=p['cash']<=p['added_price'],'variable_modification_amount')
            prior=[o['obligation_id'] for o in c['obligations'] if o['delivered']]
            require(len(existing)-len(prior)+len(ids)<=c['stock_units'],'variable_stock_shortage')
            unearned_fixed=c['original_fixed_price']*(len(existing)-len(prior))/len(existing)
            c['original_delivered_at_modification']=prior
            c['remaining_fixed_per_unit']=(unearned_fixed+p['added_price'])/(len(existing)-len(prior)+len(ids))
            c['obligations'] += [{'obligation_id':key,'original':False,'delivered':False} for key in ids]
            c['total_fixed_price']+=p['added_price'];c['received']+=p['cash'];c['modified']=True
            c['modified_allocation_id']=p['modified_allocation_id']
            line('cash',p['cash']);line('contract_liability',-p['cash']);cash['operating']=p['cash']
        elif action=='assess':
            require(p['bonus_promise_id']==c['bonus_promise_id'],'bonus_promise_mismatch')
            require(p['allocation_id']==c['original_allocation_id'],'original_bonus_allocation_required')
            require(p['constraint_finding']!='unknown','variable_constraint_unresolved','partial')
            require(p['most_likely_measure_admitted'],'variable_estimation_unresolved','partial')
            require(p['estimate'] in [0,c['promised_bonus']],'binary_bonus_estimate_invalid')
            c['bonus_estimate']=p['estimate'];c['constraint_status']=p['constraint_finding']
            c['bonus_admitted']=p['estimate'] if p['constraint_finding']=='admitted' else F(0)
        target=distinct_revenue(c);delta=target-c['revenue']
        require(c['received']>=target,'variable_prepayment_scope','unsupported')
        c['revenue']=target;line('contract_liability',delta);line('product_revenue',-delta)
    elif family=='variableI':
        require(c['binary_bonus_admitted'] and c['customer_controls_wip'],'integrated_variable_scope_unresolved','partial')
        paid=F(0);cost=F(0)
        if action=='receive':
            require(0<p['cash']<=c['fixed_price']+c['promised_bonus']-c['received'],'variable_receipt_amount')
            paid=p['cash']
        elif action=='perform':
            require(p['faithful_measure_admitted'],'faithful_progress_unresolved','partial')
            require(c['progress']<=p['cumulative_progress']<=1 and p['cash_cost']>=0,'integrated_progress_invalid')
            c['progress']=p['cumulative_progress'];cost=p['cash_cost']
        elif action=='modify':
            require(not c['modified'] and p['enforceable'] and p['remaining_not_distinct'],'integrated_modification_conditions')
            require(p['faithful_measure_admitted'],'faithful_progress_unresolved','partial')
            require(p['modified_promise_id']!=c['original_promise_id'] and p['modified_allocation_id']!=c['original_allocation_id'],
                'modified_identity_required')
            require(p['new_fixed_price']>0 and 0<=p['new_progress']<=1 and 0<=p['cash']<=p['new_fixed_price']-c['fixed_price'],
                'integrated_modification_amount')
            c.update(fixed_price=p['new_fixed_price'],progress=p['new_progress'],modified=True,
                modified_promise_id=p['modified_promise_id'],modified_allocation_id=p['modified_allocation_id'])
            paid=p['cash']
        elif action=='assess':
            require(p['bonus_promise_id']==c['bonus_promise_id'],'bonus_promise_mismatch')
            expected_allocation=c['modified_allocation_id'] if c['modified'] else c['original_allocation_id']
            expected_promise=c['modified_promise_id'] if c['modified'] else c['original_promise_id']
            require(p['allocation_id']==expected_allocation and p['promise_id']==expected_promise,'modified_bonus_allocation_required')
            require(p['constraint_finding']!='unknown','variable_constraint_unresolved','partial')
            require(p['most_likely_measure_admitted'],'variable_estimation_unresolved','partial')
            require(p['estimate'] in [0,c['promised_bonus']],'binary_bonus_estimate_invalid')
            c.update(bonus_estimate=p['estimate'],constraint_status=p['constraint_finding'],
                bonus_admitted=p['estimate'] if p['constraint_finding']=='admitted' else F(0))
        c['received']+=paid;c['cost_paid']+=cost;target=(c['fixed_price']+c['bonus_admitted'])*c['progress']
        require(c['received']>=target,'variable_prepayment_scope','unsupported')
        delta=target-c['revenue'];c['revenue']=target
        line('cash',paid-cost);line('contract_liability',delta-paid);line('service_revenue',-delta);line('service_expense',cost)
        cash['operating']=paid-cost
    elif family=='recovery':
        require(c['over_time_admitted'],'over_time_condition_unresolved','partial')
        require(c['costs_expensed_admitted'],'cost_capitalization_method_required','unsupported')
        if action=='receive':
            require(0<p['cash']<=c['price']-c['received'],'recovery_receipt_invalid')
            c['received']+=p['cash'];line('cash',p['cash']);line('contract_liability',-p['cash']);cash['operating']=p['cash']
        else:
            require(p['cash_cost']>=0,'recovery_cost_invalid')
            c['cost_paid']+=p['cash_cost']
            if p['measurement_available']:
                require(p['cumulative_progress'] is not None and p['faithful_measure_admitted'] is True,
                    'faithful_progress_unresolved','partial')
                require(0<=p['cumulative_progress']<=1,'recovery_progress_invalid')
                if c['progress'] is not None:require(p['cumulative_progress']>=c['progress'],'recovery_progress_invalid')
                c['progress']=p['cumulative_progress'];c['measurement_status']='measured';target=c['price']*c['progress']
            else:
                require(c['measurement_status']!='measured','progress_measurement_loss_requires_new_method','unsupported')
                require(p['cumulative_progress'] is None,'unmeasurable_progress_is_not_zero')
                require(p['costs_recoverable'] is True,'recoverability_unresolved','partial')
                require(c['cost_paid']<=c['price'],'cost_recovery_scope','unsupported')
                c['progress']=None;c['measurement_status']='cost_recovery';target=c['cost_paid']
            require(target<=c['received'],'recovery_prepayment_scope','unsupported')
            delta=target-c['revenue'];c['revenue']=target
            line('cash',-p['cash_cost']);line('service_expense',p['cash_cost'])
            line('contract_liability',delta);line('service_revenue',-delta);cash['operating']=-p['cash_cost']
    else:raise AssertionError(method)
    return c,{k:v for k,v in j.items() if v},cash

def check_customer(tag,c,b):
    if tag=='customer_cycle':
        values,_=cycle_values(c)
        assert all(c[k]==v for k,v in values.items())
        assert b['cash']==c['cash_received'] and b['receivable']==c['receivable']
        assert b['contract_asset']==c['contract_asset'] and -b['contract_liability']==c['contract_liability']
        assert -b['product_revenue']==c['revenue']
        assert c['cash_received']+c['receivable']+c['contract_asset']-c['contract_liability']==c['revenue']
    elif tag=='separate_addition':
        contracts=c['contracts'];assert len({x['contract_id'] for x in contracts})==len(contracts)
        assert len({x['allocation_id'] for x in contracts})==len(contracts)
        assert all(0<=x['delivered']<=x['units'] and x['revenue']==x['price']*x['delivered']/x['units'] for x in contracts)
        assert all(x['revenue']<=x['received']<=x['price'] for x in contracts)
        assert b['inventory']==c['stock_units']*c['unit_cost']
        assert -b['contract_liability']==sum(x['received']-x['revenue'] for x in contracts)
        assert -b['product_revenue']==sum(x['revenue'] for x in contracts)
    elif tag=='return_costs':
        assert b['return_recovery']==c['recovery'] and -b['refund_liability']==c['refund']
        assert c['actual_processing_cost'] is None and c['actual_settlement_cash'] is None
        if c['phase']=='measured':
            assert c['recovery']==c['expected_returns']*(c['cost']-c['recovery_cost_per_unit']-c['deterioration_per_unit'])
            assert c['refund']==c['expected_returns']*c['price'] and b['inventory']==0
        else:assert b['inventory']==c['units']*c['cost']
    elif tag=='variable_distinct':
        obligations=c['obligations'];ids={x['obligation_id'] for x in obligations};assert len(ids)==len(obligations)
        prior=set(c['original_delivered_at_modification'])
        assert prior<={x['obligation_id'] for x in obligations if x['original'] and x['delivered']}
        assert (c['modified_allocation_id'] is not None)==c['modified']
        assert c['revenue']==distinct_revenue(c) and -b['product_revenue']==c['revenue']
        assert -b['contract_liability']==c['received']-c['revenue']
        assert sum(not x['delivered'] for x in obligations)<=c['stock_units']
        assert b['inventory']==c['stock_units']*c['unit_cost']
        assert c['bonus_admitted']==(c['bonus_estimate'] if c['constraint_status']=='admitted' else 0)
    elif tag=='variable_integrated':
        assert (c['modified_promise_id'] is not None)==c['modified']
        assert (c['modified_allocation_id'] is not None)==c['modified']
        assert c['revenue']==(c['fixed_price']+c['bonus_admitted'])*c['progress']
        assert -b['service_revenue']==c['revenue'] and b['service_expense']==c['cost_paid']
        assert -b['contract_liability']==c['received']-c['revenue']
        assert c['bonus_admitted']==(c['bonus_estimate'] if c['constraint_status']=='admitted' else 0)
    elif tag=='progress_recovery':
        assert -b['contract_liability']==c['received']-c['revenue']
        assert -b['service_revenue']==c['revenue'] and b['service_expense']==c['cost_paid']
        if c['measurement_status']=='cost_recovery':assert c['progress'] is None and c['revenue']==c['cost_paid']
        elif c['measurement_status']=='measured':assert c['revenue']==c['price']*c['progress']
        else:assert c['revenue']==0 and c['progress'] is None
