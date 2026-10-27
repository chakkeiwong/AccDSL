"""Independent financial reconstruction, without importing authored expectations."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as F

def check_component(tag,s,b):
    def same(k,v):assert b[k]==v,(k,b[k],v)
    if tag=='rcost':
        assert 0<=s['expected_units']<=s['sold_units']
        assert s['estimated_handling']+s['estimated_deterioration']<=s['unit_cost']
        same('refund_liability',-s['refund']);same('recovery_asset',s['recovery']);same('inventory',s['inventory'])
        if not s['settled']:
            assert s['refund']==s['expected_units']*s['unit_refund']
            assert s['recovery']==s['expected_units']*(s['unit_cost']-s['estimated_handling']-s['estimated_deterioration'])
    elif tag=='cgu':
        assert len({a['asset_id'] for a in s['assets']})==len(s['assets'])
        assert all(0<=a['carrying']<=a['no_impairment'] and a['recoverable_cap']>=0 for a in s['assets'])
        same('ppe',sum(a['carrying'] for a in s['assets']));same('goodwill',s['goodwill'])
    elif tag=='individual':
        assert 0<=s['carrying']<=s['no_impairment'];same('ppe',s['carrying'])
    elif tag=='lease':
        assert len({r['right_id'] for r in s['rights']})==len(s['rights'])
        assert all(r['rou']>=0 and r['liability']>=0 and r['rate']>=0 for r in s['rights'])
        same('rou',sum(r['rou'] for r in s['rights']));same('lease_liability',-sum(r['liability'] for r in s['rights']))
    elif tag=='cost':
        assert 0<=s['asset']<=s['no_impairment'] and s['remaining_units']>=0
        same('contract_cost',s['asset'])
    elif tag in ('distinct','integrated'):
        same('contract_asset',s['unbilled']);same('revenue',-s['revenue'])
        if tag=='distinct':assert s['remaining_units']>=0 and s['remaining_consideration']>=0
        else:assert 0<=s['progress']<=1 and s['revenue']==s['progress']*s['total_consideration']
    elif tag=='acqdta':
        assert s['goodwill']>=0 and s['dta']>=0
        same('goodwill',s['goodwill']);same('dta',s['dta'])
    elif tag=='taxlots':
        assert len({r['lot_id'] for r in s['lots']})==len(s['lots'])
        for r in s['lots']:
            assert 0<=r['rate']<=1 and 0<=r['fraction']<=1
            assert r['difference']>=0 or r['fraction']==1
            assert r['amount']==r['difference']*r['rate']*r['fraction']
        same('dta',sum(max(F(0),r['amount']) for r in s['lots']))
        same('dtl',sum(min(F(0),r['amount']) for r in s['lots']))
        if s['present_net']:assert len({(r['entity_id'],r['authority_id']) for r in s['lots']})==1
    else:raise AssertionError('Unknown component')

def derive(tag,opening,method,p,when,need):
    s=deepcopy(opening);j={};cash={k:F(0) for k in ('operating','investing','financing','unclassified')}
    oci={'tax':F(0)};equity={'tax':F(0)}
    def post(k,v):j[k]=j.get(k,F(0))+v
    def known(v,code):need(v is not None,code,'partial');return v
    def yes(v,code):known(v,code);need(v,code)
    def origin(delta,dest):
        post({'profit':'tax_expense','oci':'tax_oci','equity':'tax_equity'}[dest],-delta)
        if dest=='oci':oci['tax']+=delta
        if dest=='equity':equity['tax']+=delta
    if method=='rcost.settle':
        need(not s['settled'],'return_already_settled');need(p['all_rights_closed'],'return_rights_still_open','partial')
        handling=known(p['unit_handling'],'actual_handling_missing')
        yes(p['handling_is_selling_cost'],'handling_classification_unresolved')
        nr=known(p['inventory_nrv'],'returned_inventory_nrv_missing')
        r=p['actual_units'];d=p['unit_deterioration']
        need(0<=r<=s['sold_units'] and 0<=d<=s['unit_cost'] and handling>=0 and nr>=0,'return_quantity_or_cost_invalid')
        refund=r*s['unit_refund'];processing=r*handling
        need(known(p['refund_cash'],'refund_cash_missing')==refund and known(p['handling_cash'],'handling_cash_missing')==processing,'settlement_cash_mismatch')
        inventory=min(r*(s['unit_cost']-d),nr)
        post('refund_liability',s['refund']);post('recovery_asset',-s['recovery']);post('inventory',inventory)
        post('cash',-refund-processing);post('revenue',refund-s['refund'])
        post('cost_of_sales',s['recovery']-inventory);post('cost_expense',processing);cash['operating']=-refund-processing
        s.update(refund=F(0),recovery=F(0),inventory=s['inventory']+inventory,settled=True)
    elif method=='cgu.reverse':
        need(p['changed_estimates'] and not p['passage_only'],'reversal_estimate_change_required')
        need(p['recoverable']>=0,'recoverable_negative')
        assets=s['assets'];total=sum(a['carrying'] for a in assets)+s['goodwill']
        capacities={a['asset_id']:max(F(0),min(a['no_impairment'],a['recoverable_cap'])-a['carrying']) for a in assets}
        remaining=min(max(F(0),p['recoverable']-total),sum(capacities.values()))
        weights={a['asset_id']:a['carrying'] for a in assets}
        allocation={k:F(0) for k in weights}
        while remaining:
            eligible=[k for k in weights if capacities[k]>allocation[k]]
            denom=sum(weights[k] for k in eligible)
            need(denom>0,'zero_weight_allocation_unspecified','partial')
            offers={k:remaining*weights[k]/denom for k in eligible}
            used=F(0)
            for k in eligible:
                part=min(offers[k],capacities[k]-allocation[k]);allocation[k]+=part;used+=part
            need(used>0,'zero_weight_allocation_unspecified','partial');remaining-=used
        reversal=sum(allocation.values())
        for a in assets:a['carrying']+=allocation[a['asset_id']]
        post('ppe',reversal);post('other_gains',-reversal)
    elif method=='individual.reverse':
        need(p['cost_model'],'revaluation_route_unspecified','unsupported')
        need(p['changed_estimates'],'reversal_estimate_change_required');need(p['recoverable']>=0,'recoverable_negative')
        increase=max(F(0),min(p['recoverable'],s['no_impairment'])-s['carrying'])
        s['carrying']+=increase;post('ppe',increase);post('other_gains',-increase)
    elif method=='lease.reduce':
        need(p['allocation_basis']=='traced_right_amounts','lease_allocation_basis_missing','partial')
        yes(p['standalone_allocation_supported'],'standalone_allocation_missing')
        need(p['annual_end_payments'],'nonannual_lease_schedule_unspecified','unsupported')
        need({r['right_id'] for r in p['rights']}=={r['right_id'] for r in s['rights']} and len(p['rights'])==len(s['rights']),'lease_rights_mismatch')
        byid={r['right_id']:r for r in p['rights']}
        for right in s['rights']:
            x=byid[right['right_id']];rr=known(x['removed_rou'],'surrendered_rou_missing');rl=known(x['removed_liability'],'surrendered_liability_missing')
            rate=known(x['new_rate'],'revised_rate_missing')
            need(0<=rr<=right['rou'] and 0<=rl<=right['liability'] and rate>=0 and all(v>=0 for v in x['payments']),'lease_reduction_invalid')
            if x['full_termination']:need(rr==right['rou'] and rl==right['liability'] and not x['payments'],'full_right_termination_mismatch')
            else:need(bool(x['payments']),'remaining_lease_schedule_missing','partial')
            liability=sum((amount/(1+rate)**i for i,amount in enumerate(x['payments'],1)),F(0))
            adjustment=liability-(right['liability']-rl)
            need(right['rou']-rr+adjustment>=0,'negative_remaining_rou_unspecified','unsupported')
            post('rou',-rr+adjustment);post('lease_liability',rl-adjustment);post('other_gains',rr-rl)
            right.update(rou=right['rou']-rr+adjustment,liability=liability,rate=rate,last_measurement_date=when)
    elif method=='lease.pay':
        right=next((r for r in s['rights'] if r['right_id']==p['right_id']),None)
        need(right is not None,'lease_right_missing')
        need(p['one_year_elapsed'] and p['no_intervening_accrual_or_modification'],'lease_payment_interval_unresolved','partial')
        a=date.fromisoformat(right['last_measurement_date']);z=date.fromisoformat(when)
        need((z.year,z.month,z.day)==(a.year+1,a.month,a.day),'lease_payment_interval_mismatch')
        interest=right['liability']*right['rate'];principal=p['amount']-interest
        need(0<=principal<=right['liability'],'lease_payment_invalid')
        post('cash',-p['amount']);post('finance_expense',interest);post('lease_liability',principal)
        cash['operating']=-interest;cash['financing']=-principal
        right['liability']-=principal;right['last_measurement_date']=when
    elif method=='lease.depreciate':
        yes(p['systematic_allocation_supported'],'lease_depreciation_basis_missing')
        right=next((r for r in s['rights'] if r['right_id']==p['right_id']),None)
        need(right is not None,'lease_right_missing');need(0<=p['amount']<=right['rou'],'lease_depreciation_invalid')
        right['rou']-=p['amount'];post('rou',-p['amount']);post('depreciation',p['amount'])
    elif method=='cost.incur':
        need(p['kind']==s['kind'],'cost_lot_kind_mismatch');need(p['amount']>=0,'cost_negative')
        need(p['other_standard']=='none','cost_other_standard_required','unsupported')
        recoverable=known(p['recoverable'],'cost_recoverability_missing')
        if p['nature'] in ('waste','past_service','admin'):capitalise=False
        elif p['kind']=='acquisition':capitalise=known(p['incremental'],'incremental_cost_finding_missing') and recoverable
        else:capitalise=known(p['directly_related'],'direct_cost_finding_missing') and known(p['future_resources'],'future_resource_finding_missing') and recoverable
        if capitalise:
            need(s['asset']==s['no_impairment']==0 and s['remaining_units']>0,'cost_lot_already_recognized')
            s['asset']+=p['amount'];s['no_impairment']+=p['amount'];post('contract_cost',p['amount'])
        else:post('cost_expense',p['amount'])
        post('cash',-p['amount']);cash['operating']=-p['amount']
    elif method=='cost.amortize':
        yes(p['equal_unit_pattern_supported'],'cost_amortization_pattern_missing')
        n=p['delivered_units'];need(0<n<=s['remaining_units'],'cost_service_units_invalid')
        ratio=n/s['remaining_units'];amort=s['asset']*ratio
        s['asset']-=amort;s['no_impairment']*=1-ratio;s['remaining_units']-=n
        post('contract_cost',-amort);post('amortization',amort)
    elif method in ('cost.impair','cost.reverse'):
        yes(p['other_impairments_done'],'other_asset_impairment_incomplete')
        need(p['credit_adjusted_consideration']>=0 and p['remaining_direct_cost']>=0,'cost_recovery_inputs_invalid')
        limit=max(F(0),p['credit_adjusted_consideration']-p['remaining_direct_cost'])
        if method=='cost.impair':change=-max(F(0),s['asset']-limit)
        else:
            need(p['changed_circumstances'],'cost_reversal_change_required')
            change=max(F(0),min(limit,s['no_impairment'])-s['asset'])
        s['asset']+=change;s['cgu_review_pending']=True
        post('contract_cost',change);post('impairment_expense',-change)
    elif method=='distinct.modify':
        yes(p['remaining_distinct'],'remaining_distinctness_missing');yes(p['added_distinct'],'added_distinctness_missing')
        need(not p['priced_at_ssp'],'separate_contract_route_required','unsupported')
        need(p['added_units']>0 and p['added_consideration']>=0,'modification_scope_invalid')
        s['remaining_units']+=p['added_units'];s['remaining_consideration']+=p['added_consideration'];s['revision']+=1
    elif method=='distinct.perform':
        need(0<p['units']<=s['remaining_units'],'performance_units_invalid')
        earned=s['remaining_consideration']*p['units']/s['remaining_units']
        s['remaining_units']-=p['units'];s['remaining_consideration']-=earned
        s['revenue']+=earned;s['unbilled']+=earned;post('contract_asset',earned);post('revenue',-earned)
    elif method in ('integrated.modify','integrated.perform'):
        yes(p['progress_supported'],'contract_progress_finding_missing')
        if method=='integrated.modify':
            yes(p['integrated_obligation'],'integrated_obligation_finding_missing')
            need(p['new_total']>=0,'contract_total_negative');s['total_consideration']=p['new_total'];s['revision']+=1
        need(0<=p['new_progress']<=1,'contract_progress_invalid')
        if method=='integrated.perform':need(p['new_progress']>=s['progress'],'performance_progress_decreased')
        earned=s['total_consideration']*p['new_progress']-s['revenue']
        s['progress']=p['new_progress'];s['revenue']+=earned;s['unbilled']+=earned
        post('contract_asset',earned);post('revenue',-earned)
    elif method=='acqdta.recognize':
        yes(p['rate_enacted'],'tax_rate_authority_missing');rate=known(p['rate'],'tax_rate_missing');yes(p['recoverable'],'dta_recovery_finding_missing')
        need(0<=rate<=1 and p['additional_difference']>=0,'dta_amount_invalid')
        acq=date.fromisoformat(s['acquisition_date']);end=date.fromisoformat(s['measurement_end_inclusive']);now=date.fromisoformat(when)
        # Examples exclude leap-day acquisitions; no implicit calendar convention.
        need((acq.month,acq.day)!=(2,29),'leap_day_measurement_calendar_unspecified','unsupported')
        anniversary=acq.replace(year=acq.year+1)
        need(acq<=end<=anniversary and now>=acq,'measurement_period_invalid')
        need(not p['measurement_period_open'] or now<=end,'measurement_period_closed')
        benefit=p['additional_difference']*rate;s['dta']+=benefit;post('dta',benefit)
        within=p['benefit_owner']=='acquiree' and p['measurement_period_open'] and now<=end
        if within:within=known(p['new_acquisition_date_information'],'acquisition_date_information_missing')
        if within:
            reduction=min(s['goodwill'],benefit);s['goodwill']-=reduction;post('goodwill',-reduction)
            excess=benefit-reduction;origin(excess,'profit');s['retrospective_adjustment']+=benefit;s['profit_adjustment']+=excess
        else:
            dest=known(p['underlying_origin'],'tax_origin_missing')
            origin(benefit,dest);s[{'profit':'profit_adjustment','oci':'oci_adjustment','equity':'equity_adjustment'}[dest]]+=benefit
    elif method=='taxlots.remeasure':
        need(len(p['lots'])==len(s['lots']) and {r['lot_id'] for r in p['lots']}=={r['lot_id'] for r in s['lots']},'tax_lots_mismatch')
        inputs={r['lot_id']:r for r in p['lots']}
        old_assets=sum(max(F(0),r['amount']) for r in s['lots']);old_liabs=sum(min(F(0),r['amount']) for r in s['lots'])
        for r in s['lots']:
            x=inputs[r['lot_id']];yes(x['rate_enacted'],'tax_rate_authority_missing');yes(x['eligible_difference'],'tax_difference_eligibility_missing')
            rate=known(x['rate'],'tax_rate_missing');fraction=x['fraction'];difference=x['difference']
            need(0<=rate<=1 and 0<=fraction<=1 and (difference>=0 or fraction==1),'tax_rate_or_fraction_invalid')
            if difference>0 and fraction>0:yes(x['recognition_supported'],'dta_recovery_finding_missing')
            target=difference*rate*fraction;origin(target-r['amount'],r['origin'])
            r.update(difference=difference,rate=rate,fraction=fraction,amount=target)
        post('dta',sum(max(F(0),r['amount']) for r in s['lots'])-old_assets)
        post('dtl',sum(min(F(0),r['amount']) for r in s['lots'])-old_liabs)
    elif method=='taxlots.present':
        if p['request_offset']:
            yes(p['enforceable_current_setoff_right'],'tax_setoff_right_missing')
            need(len({(r['entity_id'],r['authority_id']) for r in s['lots']})==1,'tax_offset_scope_mismatch')
        s['present_net']=p['request_offset']
    else:raise AssertionError('Unknown method '+method)
    j={k:v for k,v in j.items() if v}
    need(sum(j.values())==0,'derived_journal_unbalanced')
    need(j.get('cash',0)==sum(cash.values()),'derived_cash_unbalanced')
    return s,j,cash,oci,equity
