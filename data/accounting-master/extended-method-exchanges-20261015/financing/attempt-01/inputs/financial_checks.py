"""Independent derivations from opening components and economic event facts.

Does not import authored cases, proposed journals, builders or closing states.
Signed journals use debits positive; reserve/component quantities use their
economic sign (a credit reserve is positive). Values remain exact fractions.
"""
from copy import deepcopy
from fractions import Fraction as F

def derive(tag, original, method, p, event_date, require):
    c=deepcopy(original); j={}; cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    oci={k:F(0) for k in ['cash_flow','intrinsic','cost']}
    equity={k:F(0) for k in ['issue','award','basis_transfer']}
    def line(a,v): j[a]=j.get(a,F(0))+v
    def flow(v,kind='operating'): line('cash',v); cash[kind]+=v
    def reserve(account,component,delta):
        line(account,-delta); c[component]+=delta
    def effective(d,h):
        require(d==0 or h==0 or d*h<0,'offsetting_measurement_scope','unsupported')
        return (1 if d>=0 else -1)*min(abs(d),abs(h))

    if tag=='amendment':
        if method=='amendment.announce':
            require(not c['announced'] and not c['bound'],'announcement_already_consumed')
            require(event_date==c['announcement_date'],'announcement_date_mismatch')
            require(not p['rights_changed'],'binding_terms_method_required','unsupported')
            c['announced']=True
        elif method=='amendment.bind':
            require(not c['bound'],'amendment_already_consumed')
            require(event_date==c['binding_date']==p['quote_date'],'amendment_date_mismatch')
            require(p['conditions_resolved'],'amendment_conditions_unresolved','partial')
            require(p['legal_discharge'],'debt_not_discharged')
            require(p['equity_qualified'] and not p['cash_alternative'],'equity_classification_failed')
            require(p['quote'] is not None,'amendment_quote_unresolved','partial')
            require(p['quote']>=0 and c['new_shares']>=c['old_shares'],'negative_consideration')
            loss=(c['new_shares']-c['old_shares'])*p['quote'] if c['consideration']=='shares' else c['bonus']
            pending=c['debt']+loss-(c['bonus'] if c['consideration']=='cash_bonus' else 0)
            line('debt',c['debt']); line('inducement_expense',loss); line('equity_pending',-pending)
            if c['consideration']=='cash_bonus': line('bonus_payable',-c['bonus']); c['bonus_due']=c['bonus']
            c.update(debt=F(0),equity_pending=pending,bound=True); equity['issue']=pending
        elif method=='amendment.deliver':
            require(c['bound'] and not c['delivered'],'delivery_already_consumed_or_not_bound')
            require(event_date==c['delivery_date'] and p['shares']==c['new_shares'],'delivery_terms_mismatch')
            line('equity_pending',c['equity_pending']); line('capital',-c['equity_pending'])
            c.update(issued=c['issued']+c['equity_pending'],equity_pending=F(0),delivered=True)
        elif method=='amendment.pay_bonus':
            require(c['bound'] and not c['bonus_paid'] and c['bonus_due']>0,'bonus_already_consumed')
            require(event_date>=c['binding_date'],'bonus_before_binding')
            require(p['amount']==c['bonus_due'],'bonus_amount_mismatch')
            line('bonus_payable',p['amount']); flow(-p['amount'],'financing')
            c.update(bonus_due=F(0),bonus_paid=True)
        else: require(False,'unknown_method','unsupported')
    elif tag=='award':
        require(c['all_original_vest'],'original_vesting_assessment_required','partial')
        if method=='award.service':
            require(c['settlement']=='equity','cash_remeasurement_method_required','unsupported')
            elapsed=p['elapsed']
            require(elapsed==c['elapsed']+1 and elapsed<=c['total_years'],'service_clock_mismatch')
            require(event_date>=c['service_dates'][elapsed-1],'future_service_not_performed')
            target=c['quantity']*c['grant_fv']*F(elapsed,c['total_years'])
            inc=F(0)
            if c['modification_elapsed'] is not None and c['incremental_total']:
                duration=c['incremental_end']-c['modification_elapsed']
                require(duration>0,'incremental_clock_invalid')
                inc=c['incremental_total']*min(F(1),F(elapsed-c['modification_elapsed'],duration))
            cost=target-c['original_cost']+inc-c['incremental_cost']
            line('award_expense',cost); line('award_equity',-cost); equity['award']=cost
            c.update(elapsed=elapsed,original_cost=target,incremental_cost=inc,award_equity=c['award_equity']+cost)
        elif method=='award.modify':
            require(c['settlement']=='equity' and not c['modified'],'award_modification_order')
            require(0<c['elapsed']<c['total_years'],'modification_service_scope','unsupported')
            require(event_date>=c['service_dates'][c['elapsed']-1] and event_date<c['service_dates'][c['elapsed']],
                'modification_service_date_mismatch')
            require(p['original_conditions_unchanged'],'modified_conditions_method_required','unsupported')
            require(p['before_fv'] is not None and p['after_fv'] is not None,'modification_value_unresolved','partial')
            require(p['before_fv']>=0 and p['after_fv']>=0 and p['added_quantity']>=0,'negative_award_value')
            require(c['elapsed']<p['incremental_end']<=c['total_years'],'incremental_clock_invalid')
            if p['kind']=='repricing':
                require(p['added_quantity']==0,'award_modification_kind_mismatch')
                total=c['quantity']*max(F(0),p['after_fv']-p['before_fv'])
            else: total=p['added_quantity']*p['after_fv']
            c.update(modified=True,incremental_total=total,modification_elapsed=c['elapsed'],incremental_end=p['incremental_end'])
        elif method=='award.cash_to_equity':
            require(c['settlement']=='cash' and not c['modified'],'award_modification_order')
            require(c['quantity']>0 and 0<c['elapsed']<c['total_years'],'modification_service_scope','unsupported')
            require(c['service_dates'][c['elapsed']-1]<=event_date<c['service_dates'][c['elapsed']],
                'modification_service_date_mismatch')
            require(p['replacement_identified'],'replacement_identification_unresolved','partial')
            require(p['remeasured_liability'] is not None and p['replacement_fv'] is not None,'modification_value_unresolved','partial')
            require(p['remeasured_liability']==c['liability'],'cash_award_remeasurement_required','partial')
            require(p['replacement_fv']>=0 and p['modified_total_years']>c['elapsed'],'modified_service_clock_invalid')
            require(p['modified_total_years']==c['total_years'],'modified_service_calendar_required','unsupported')
            target=p['replacement_fv']*F(c['elapsed'],p['modified_total_years']); difference=target-c['liability']
            line('award_liability',c['liability']); line('award_expense',difference); line('award_equity',-target)
            equity['award']=target
            c.update(liability=F(0),settlement='equity',modified=True,original_cost=target,
                grant_fv=p['replacement_fv']/c['quantity'],award_equity=target)
        else: require(False,'unknown_method','unsupported')
    elif tag=='cashflow':
        if method=='cashflow.measure':
            require(c['active'],'designation_discontinued')
            require(not c['basis_done'] and not c['interest_paid'],'post_transaction_measurement_method_required','unsupported')
            require(p['eligibility_known'],'hedge_eligibility_unresolved','partial')
            require(p['D'] is not None and p['H'] is not None,'hedge_value_unresolved','partial')
            e=effective(p['D'],p['H']); i=p['D']-e
            line('derivative',p['D']-c['D']); reserve('cf_reserve','reserve',e-c['E'])
            line('other_gains',-(i-c['I'])); oci['cash_flow']=e-c['E']
            c.update(D=p['D'],E=e,I=i,derivative=p['D']-c['settled_total'])
        elif method=='cashflow.settle':
            require(c['derivative']!=0,'derivative_already_settled')
            require(p['amount']==c['derivative'],'settlement_amount_mismatch')
            line('derivative',-p['amount']); flow(p['amount'])
            c.update(derivative=F(0),settled_total=c['settled_total']+p['amount'])
        elif method=='cashflow.purchase':
            require(c['purpose']=='inventory' and not c['bought'] and p['amount']>0,'purchase_order')
            line('inventory',p['amount']); flow(-p['amount']); c.update(inventory=p['amount'],bought=True)
        elif method=='cashflow.basis_transfer':
            require(p['reserve_origin']==c['designation_id'],'reserve_origin_mismatch')
            require(c['bought'] and not c['basis_done'],'basis_transfer_already_consumed_or_no_asset')
            amount=c['reserve']; require(c['inventory']>=amount,'negative_inventory_basis')
            line('cf_reserve',amount); line('inventory',-amount); equity['basis_transfer']=-amount
            c.update(reserve=F(0),inventory=c['inventory']-amount,basis_done=True)
        elif method=='cashflow.sell':
            require(c['basis_done'] and not c['sold'],'inventory_sale_order')
            require(p['proceeds']>=0,'negative_sale_proceeds')
            flow(p['proceeds']); line('revenue',-p['proceeds']); line('inventory',-c['inventory']); line('cost_of_sales',c['inventory'])
            c.update(inventory=F(0),sold=True)
        elif method=='cashflow.pay_interest':
            require(c['purpose']=='interest' and c['interest_paid']==0 and p['amount']>0,'interest_payment_order')
            line('finance_expense',p['amount']); flow(-p['amount']); c['interest_paid']=p['amount']
        elif method=='cashflow.discontinue':
            require(c['active'],'designation_already_discontinued'); c.update(active=False,expected=p['still_expected'])
        elif method=='cashflow.release':
            require(p['reserve_origin']==c['designation_id'],'reserve_origin_mismatch')
            require(c['reserve']!=0,'reserve_already_released')
            if p['reason']=='interest_earned': require(c['purpose']=='interest' and c['interest_paid']>0,'interest_not_earned')
            else: require(not c['active'] and not c['expected'],'forecast_still_expected')
            amount=c['reserve']; line('cf_reserve',amount); line('hedge_expense',-amount)
            oci['cash_flow']=-amount; c['reserve']=F(0)
        else: require(False,'unknown_method','unsupported')
    elif tag=='option':
        if method=='option.buy':
            require(not c['bought'] and p['premium']==c['initial_actual'],'option_purchase_order')
            require(p['premium']>=0 and c['initial_aligned']>=0,'negative_premium_scope','unsupported')
            line('derivative',p['premium']); flow(-p['premium'])
            c.update(bought=True,time_value=p['premium'],aligned_time_value=c['initial_aligned'],derivative=p['premium'])
        elif method=='option.measure':
            require(c['bought'] and c['active'] and not c['settled'],'option_measurement_order')
            require(not c['basis_done'],'post_transaction_measurement_method_required','unsupported')
            require(all(p[k] is not None for k in ['intrinsic','time_value','aligned_time_value','H']),'option_component_value_unresolved','partial')
            require(p['intrinsic']>=0,'purchased_intrinsic_scope','unsupported')
            require(p['time_value']>=0 and p['aligned_time_value']>=0,'signed_option_component_method_required','unsupported')
            e=effective(p['intrinsic'],p['H']); actual=p['time_value']-c['initial_actual']
            aligned=p['aligned_time_value']-c['initial_aligned']
            if c['initial_actual']==c['initial_aligned']:
                require(p['time_value']==p['aligned_time_value'],'aligned_component_scope','unsupported'); related=actual
            elif c['initial_actual']>c['initial_aligned']: related=aligned
            else:
                require(0<=p['time_value']<=c['initial_actual'] and 0<=p['aligned_time_value']<=c['initial_aligned'],
                    'declining_positive_alignment_scope','unsupported')
                related=-min(-actual,-aligned)
            mismatch=actual-related
            value=p['intrinsic']+p['time_value']; line('derivative',value-c['derivative'])
            reserve('intrinsic_reserve','intrinsic_reserve',e-c['effective_intrinsic'])
            reserve('cost_reserve','cost_reserve',related-c['related_cost'])
            line('other_gains',-((p['intrinsic']-e)-(c['intrinsic']-c['effective_intrinsic'])))
            line('hedge_expense',-(mismatch-c['mismatch_profit']))
            oci.update(intrinsic=e-c['effective_intrinsic'],cost=related-c['related_cost'])
            c.update(intrinsic=p['intrinsic'],time_value=p['time_value'],aligned_time_value=p['aligned_time_value'],
                derivative=value,effective_intrinsic=e,related_cost=related,mismatch_profit=mismatch)
        elif method=='option.settle':
            require(c['bought'] and not c['settled'] and p['amount']==c['derivative'],'option_settlement_order')
            require(c['time_value']==0,'pre_expiry_settlement_method_required','unsupported')
            line('derivative',-p['amount']); flow(p['amount']); c.update(derivative=F(0),settled=True)
        elif method=='option.purchase':
            require(c['route']=='transaction' and not c['inventory_bought'] and p['amount']>0,'option_inventory_order')
            line('inventory',p['amount']); flow(-p['amount']); c.update(inventory_bought=True,inventory=p['amount'])
        elif method=='option.basis_transfer':
            require(p['intrinsic_origin']==c['designation_id']+'/intrinsic' and p['cost_origin']==c['designation_id']+'/cost','reserve_origin_mismatch')
            require(c['inventory_bought'] and not c['basis_done'],'option_basis_already_consumed_or_no_asset')
            amount=c['intrinsic_reserve']+c['cost_reserve']; require(c['inventory']>=amount,'negative_inventory_basis')
            line('intrinsic_reserve',c['intrinsic_reserve']); line('cost_reserve',c['cost_reserve']); line('inventory',-amount)
            equity['basis_transfer']=-amount
            c.update(intrinsic_reserve=F(0),cost_reserve=F(0),inventory=c['inventory']-amount,basis_done=True)
        elif method=='option.sell':
            require(c['basis_done'] and not c['sold'],'option_inventory_sale_order')
            require(p['proceeds']>=0,'negative_sale_proceeds')
            flow(p['proceeds']); line('revenue',-p['proceeds']); line('inventory',-c['inventory']); line('cost_of_sales',c['inventory'])
            c.update(inventory=F(0),sold=True)
        elif method=='option.amortize':
            require(c['bought'] and c['active'] and c['route']=='time_period' and c['periods']>0,'amortization_route_mismatch')
            require(p['rational_even_allocation_admitted'],'amortization_policy_unresolved','partial')
            require(p['elapsed']==c['elapsed']+1 and p['elapsed']<=c['periods'],'protection_clock_mismatch')
            require(event_date>=c['protection_dates'][p['elapsed']-1],'future_protection_not_performed')
            target=min(c['initial_actual'],c['initial_aligned'])*F(p['elapsed'],c['periods']); amount=target-c['amortized']
            line('cost_reserve',-amount); line('hedge_expense',amount); oci['cost']=amount
            c.update(elapsed=p['elapsed'],amortized=target,cost_reserve=c['cost_reserve']+amount)
        elif method=='option.discontinue':
            require(c['bought'] and c['active'] and c['route']=='time_period' and p['relationship_ended'],'option_discontinuation_order')
            amount=c['cost_reserve']; line('cost_reserve',amount); line('hedge_expense',-amount); oci['cost']=-amount
            c.update(cost_reserve=F(0),active=False)
        else: require(False,'unknown_method','unsupported')
    elif tag=='rebalancing':
        if method=='rebalancing.measure':
            require(c['revision']==0,'pre_rebalance_measurement_required')
            e=effective(p['D'],p['H']); i=p['D']-e
            line('derivative',p['D']-c['D']); reserve('cf_reserve','reserve',e-c['E']); line('other_gains',-(i-c['I']))
            oci['cash_flow']=e-c['E']; c.update(D=p['D'],E=e,I=i,derivative=p['D'],last_measurement_date=event_date)
        elif method=='rebalancing.change':
            require(c['revision']==0,'rebalancing_revision_scope','unsupported')
            require(c['last_measurement_date']==event_date,'measure_before_rebalance')
            require(p['objective_unchanged'],'objective_changed_discontinue_required','unsupported')
            require(p['documentation_updated'],'rebalancing_documentation_unresolved','partial')
            require(0<p['retained_fraction']<=1,'rebalancing_fraction_invalid')
            layer=p['added_layer']
            if layer is not None:
                require(layer['designation_date']==event_date and layer['quantity']>0 and
                    layer['layer_id'] not in [v['layer_id'] for v in c['layers']],'new_layer_origin_mismatch')
                c['layers'].append(layer)
            c.update(revision=1,retained_fraction=p['retained_fraction'])
        elif method=='rebalancing.layers':
            require(p['zero_discount_admitted'],'discount_method_required','partial')
            require(all(layer['designation_date']<=event_date for layer in c['layers']),'future_layer')
            c['layer_gain']=sum(layer['quantity']*(p['current_price']-layer['reference_price']) for layer in c['layers'])
        elif method=='rebalancing.prospective_measure':
            require(c['revision']==1,'rebalancing_required')
            require(not c['prospective_measured'],'further_rebalance_measurement_method_required','unsupported')
            gain=p['total_D']-c['D']; e=effective(gain*c['retained_fraction'],p['item_change_since_rebalance'])
            line('derivative',gain); reserve('cf_reserve','reserve',e); line('other_gains',-(gain-e)); oci['cash_flow']=e
            c.update(D=p['total_D'],E=c['E']+e,I=c['I']+gain-e,derivative=p['total_D'],last_measurement_date=event_date,
                prospective_measured=True)
        else: require(False,'unknown_method','unsupported')
    elif tag=='nethedge':
        if method=='nethedge.designate':
            require(not c['designated'],'designation_already_consumed')
            require(c['external_items'] and all(p.values()),'net_hedge_eligibility_unresolved','partial')
            if c['sales_usd']==c['service_usd']:
                require(all(c[k] for k in ['rolling_strategy','changing_net_size','normal_instrument_use','inconsistent_recognition']),
                    'nil_net_conditions_unresolved','partial')
            c['designated']=True
        elif method=='nethedge.measure':
            require(c['designated'] and not c['measured'],'net_measurement_order')
            require(p['zero_discount_forward_credit_effects'],'net_valuation_method_required','unsupported')
            require(p['spot']==c['execution_spot'],'net_spot_mismatch')
            d=-(c['sales_usd']-c['service_usd'])*(p['spot']-c['initial_spot'])
            line('derivative',d); reserve('cf_reserve','reserve',d); oci['cash_flow']=d
            c.update(derivative=d,measured=True)
        elif method in ['nethedge.sale','nethedge.service']:
            require(c['measured'],'net_measurement_required')
            require(p['spot']==c['execution_spot'],'new_rate_measurement_required','unsupported')
            sale=method=='nethedge.sale'; period=c['sales_period'] if sale else c['service_period']
            require(p['recognition_period']==period==int(event_date[:4]),'gross_earning_period_mismatch')
            require(not c['sales_done' if sale else 'service_done'],'gross_transaction_already_consumed')
            require(sale or c['sales_done'],'net_service_before_sale_scope','unsupported')
            quantity=c['sales_usd'] if sale else c['service_usd']; gross=quantity*p['spot']
            offset=quantity*(p['spot']-c['initial_spot'])*(1 if sale else -1)
            flow(gross if sale else -gross); line('revenue' if sale else 'service_expense',-gross if sale else gross)
            line('hedge_expense',offset); reserve('cf_reserve','reserve',offset); oci['cash_flow']=offset
            c['sales_done' if sale else 'service_done']=True
            c['gross_revenue' if sale else 'gross_service']+=gross; c['hedge_expense']+=offset
        elif method=='nethedge.settle':
            require(c['measured'] and c['service_done'] and not c['settled'],'net_settlement_order')
            require(p['amount']==c['derivative'],'net_settlement_amount_mismatch')
            flow(p['amount']); line('derivative',-p['amount']); c.update(derivative=F(0),settled=True)
        else: require(False,'unknown_method','unsupported')
    else: require(False,'unsupported_component','unsupported')
    j={k:v for k,v in j.items() if v}
    require(sum(j.values())==0,'derived_journal_unbalanced')
    return c,j,cash,oci,equity

def check_component(tag,c,b):
    if tag=='amendment':
        assert -b['debt']==c['debt'] and -b['bonus_payable']==c['bonus_due']
        assert -b['equity_pending']==c['equity_pending'] and -b['capital']==c['issued']
    elif tag=='award':
        assert -b['award_equity']==c['award_equity'] and -b['award_liability']==c['liability']
        assert len(c['service_dates'])==c['total_years'] and c['elapsed']<=c['total_years']
        assert c['service_dates']==sorted(set(c['service_dates']))
    elif tag=='cashflow':
        assert b['derivative']==c['derivative']==c['D']-c['settled_total']
        assert -b['cf_reserve']==c['reserve'] and b['inventory']==c['inventory']
        assert c['D']==c['E']+c['I']
    elif tag=='option':
        assert b['derivative']==c['derivative'] and b['inventory']==c['inventory']
        assert -b['intrinsic_reserve']==c['intrinsic_reserve'] and -b['cost_reserve']==c['cost_reserve']
        assert c['elapsed']<=c['periods'] and c['amortized']>=0
        assert len(c['protection_dates'])==c['periods'] and c['protection_dates']==sorted(set(c['protection_dates']))
    elif tag=='rebalancing':
        assert b['derivative']==c['derivative']==c['D'] and c['D']==c['E']+c['I']
        assert -b['cf_reserve']==c['reserve'] and 0<c['retained_fraction']<=1
        assert len({v['layer_id'] for v in c['layers']})==len(c['layers'])
    elif tag=='nethedge':
        assert b['derivative']==c['derivative'] and -b['cf_reserve']==c['reserve']
        assert -b['revenue']==c['gross_revenue'] and b['service_expense']==c['gross_service']
        assert b['hedge_expense']==c['hedge_expense']
    else: raise AssertionError(tag)
