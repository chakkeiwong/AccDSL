"""Independent exact accounting calculations; no authored expectations imported."""
from fractions import Fraction as F
from datetime import date

class Refusal(Exception):
    def __init__(self, code): self.code=code; super().__init__(code)
def need(ok, code):
    if not ok: raise Refusal(code)
def num(v):
    if isinstance(v,F): return v
    if isinstance(v,int): return F(v)
    need(isinstance(v,dict) and set(v)=={'n','d'},'invalid_rational')
    x=F(int(v['n']),int(v['d']))
    need(str(x.numerator)==v['n'] and str(x.denominator)==v['d'],'noncanonical_rational')
    return x
def q(v):
    x=F(v); return dict(n=str(x.numerator),d=str(x.denominator))
def wire(v):
    if isinstance(v,F): return q(v)
    if isinstance(v,dict): return {k:wire(x) for k,x in v.items()}
    if isinstance(v,list): return [wire(x) for x in v]
    return v
def journal(**lines): return {k:v for k,v in sorted(lines.items()) if v}
def result(values, lines=None, diagnostics=()):
    return wire(dict(status='unresolved' if diagnostics else 'resolved',
                     diagnostics=list(diagnostics),values=values,
                     adjustment_journal=lines or {},
                     posting_effect='none' if diagnostics or not lines else 'group_only'))
def allocation(values, floors, loss):
    """Water filling at carrying-value weights, fixing binding floors first."""
    a=list(values); remaining=loss
    need(all(F(0)<=f<=v for v,f in zip(a,floors)),'invalid_asset_floor')
    while remaining:
        eligible=[i for i in range(len(a)) if a[i]>floors[i]]
        need(bool(eligible),'unallocated_impairment')
        total=sum(a[i] for i in eligible)
        proposed={i:remaining*a[i]/total for i in eligible}
        capped=[i for i in eligible if proposed[i]>a[i]-floors[i]]
        if not capped:
            for i in eligible:a[i]-=proposed[i]
            remaining=F(0)
        else:
            for i in capped:remaining-=a[i]-floors[i];a[i]=floors[i]
    return a

def evaluate(c, prior=None):
    m=c['method_id']; n=lambda k:num(c[k]); zero=F(0)
    if m=='reciprocal.join@1':
        need(n('left_amount')>=0 and n('right_amount')>=0,'negative_invoice')
        parts=c['allocations']; ids=[p['allocation_id'] for p in parts]
        need(len(ids)==len(set(ids)),'duplicate_allocation')
        need(all(num(p['amount'])>0 for p in parts),'invalid_allocation')
        allocated=sum((num(p['amount']) for p in parts),zero)
        need(allocated<=min(n('left_amount'),n('right_amount')),'overallocated_invoice')
        unmatched=n('left_amount')+n('right_amount')-2*allocated
        eligible=c['control_start']<=c['transaction_date']<c['control_end_exclusive']
        need(c['control_start']<=c['cutoff']<c['control_end_exclusive'],'outside_reporting_perimeter')
        return result(dict(matched=allocated,unmatched=unmatched,
            balance_elimination=allocated,performance_eligible=eligible,
            fx_difference_retained=n('monetary_fx_difference')),
            diagnostics=['unmatched_reciprocal_amount'] if unmatched else [])
    if m=='inventory.eliminate@1':
        cost,transfer,sold,external=n('original_cost'),n('internal_price'),n('sold_fraction'),n('external_proceeds')
        need(cost>=0 and transfer>=cost and 0<=sold<=1 and external>=0,'invalid_inventory_facts')
        unreal=(transfer-cost)*(1-sold); closing=cost*(1-sold)
        profit=external-cost*sold; cash=n('parent_cash')+n('subsidiary_opening_cash')+external
        return result(dict(cash=cash,inventory=closing,unrealized_profit=unreal,
            group_cogs=cost*sold,period_profit=profit,cumulative_profit=profit,
            equity=n('parent_opening_equity')+profit),
            journal(subsidiary_capital=n('investment'),investment=-n('investment'),
                    payable=transfer,receivable=-transfer,revenue=transfer,
                    cogs=-(transfer-unreal),inventory=-unreal))
    if m=='inventory.release@1':
        need(prior is not None,'missing_prior_lot')
        p=prior['values']; carrying=num(p['inventory']); unreal=num(p['unrealized_profit'])
        proceeds=n('external_proceeds'); need(proceeds>=0,'negative_sale')
        profit=proceeds-carrying; cumulative=num(p['cumulative_profit'])+profit
        return result(dict(cash=num(p['cash'])+proceeds,inventory=zero,
            unrealized_profit=zero,group_cogs=carrying,period_profit=profit,
            cumulative_profit=cumulative,equity=num(p['equity'])+profit),
            journal(opening_retained=unreal,cogs=-unreal))
    if m=='inflation.restate@1':
        obs=c['indices']; dates=[x['date'] for x in obs]
        need(dates==sorted(set(dates)) and len(dates)>=2,'invalid_index_dates')
        indices={x['date']:num(x['index']) for x in obs}
        need(all(i>0 for i in indices.values()),'nonpositive_index')
        events=c['cash_income']; ed=[e['date'] for e in events]
        need(ed==sorted(set(ed)),'duplicate_or_unsorted_income')
        need(all(dates[0]<d<dates[-1] and d in indices for d in ed),'missing_event_index')
        income={e['date']:num(e['amount']) for e in events}
        need(all(x>=0 for x in income.values()),'negative_cash_income')
        opening,closing=indices[dates[0]],indices[dates[-1]]
        cash,debt=n('cash'),n('debt'); loss=cash_loss=real_income=zero
        for a,b in zip(dates,dates[1:]):
            factor=(indices[b]/indices[a]-1)*closing/indices[b]
            loss+=(cash-debt)*factor; cash_loss+=cash*factor
            if b in income:cash+=income[b];real_income+=income[b]*closing/indices[b]
        capital=n('capital')*closing/opening
        inventory=n('inventory')*closing/opening
        writedown=max(zero,inventory-num(c['nrv'])) if c['nrv'] is not None else zero
        inventory-=writedown; equity=cash+inventory-debt
        need(n('cash')+n('inventory')-debt==n('capital'),'unbalanced_inflation_opening')
        need(equity==capital+real_income-loss-writedown,'monetary_reconciliation')
        rate=n('closing_rate'); need(rate>0 and n('prior_rate')>0,'nonpositive_rate')
        local=dict(cash=cash,inventory=inventory,debt=debt,capital=capital,
            monetary_loss=loss,real_income=real_income,write_down=writedown,equity=equity)
        lines=journal(inventory=inventory-n('inventory'),monetary_loss=loss,
            capital=-(capital-n('capital')),revenue=-(real_income-sum(income.values(),zero)),write_down=writedown)
        return result(dict(**local,cash_purchasing_power_loss=cash_loss,
            restated_opening_cash=n('cash')*closing/opening,restated_cash_flow=real_income,
            nominal_cash_flow=sum(income.values(),zero),translated={k:v*rate for k,v in local.items()},
            prior_presentation_cash=n('cash')*n('prior_rate')),lines)
    if m=='inflation.opening_tax@1':
        cost,base,tax=n('cost'),n('tax_base'),n('tax_rate')
        acquisition,opening,closing=n('acquisition_index'),n('opening_index'),n('closing_index')
        need(all(v>0 for v in (acquisition,opening,closing)) and 0<=tax<=1,'invalid_tax_index')
        a=cost*opening/acquisition; z=cost*closing/acquisition
        need(a>=base,'deductible_case_outside_profile')
        dt=(a-base)*tax; restated=dt*closing/opening; final=(z-base)*tax
        expense=final-restated; equity=z-final
        return result(dict(opening_asset=a,opening_dtl=dt,restated_opening_dtl=restated,
            closing_asset=z,closing_dtl=final,period_tax_expense=expense,closing_equity=equity),
            journal(inventory=z-cost,tax_expense=expense,dtl=-final,capital=-((a-dt)*closing/opening-cost)))
    if m=='goodwill.impair@1':
        assets,gw,notional,recover,p=n('identifiable_assets'),n('recognized_goodwill'),n('notional_goodwill'),n('recoverable'),n('parent_fraction')
        need(0<p<=1 and assets>=0 and gw>=0 and notional>=gw and recover>=0,'invalid_goodwill_facts')
        if c['notional_support']!='admitted':
            return result(dict(test_carrying=None,test_loss=None,recognized_loss=None,
                unrecognized_nci_loss=None,parent_loss=None,nci_loss=None,
                closing_goodwill=None,closing_assets=None,reported_assets=None,
                remaining_notional=None),diagnostics=['notional_goodwill_not_admitted'])
        need(gw==p*notional,'not_proportional_goodwill')
        test=assets+notional; loss=max(zero,test-recover)
        gl=min(notional,loss); al=min(assets,max(zero,loss-notional))
        recognized_gw=gl*p; recognized=recognized_gw+al
        return result(dict(test_carrying=test,test_loss=loss,recognized_loss=recognized,
            unrecognized_nci_loss=gl*(1-p),parent_loss=recognized_gw+al*p,
            nci_loss=al*(1-p),closing_goodwill=gw-recognized_gw,
            closing_assets=assets-al,reported_assets=assets-al+gw-recognized_gw,
            remaining_notional=(notional-gl)*(1-p)),
            journal(goodwill=-recognized_gw,identifiable_assets=-al,impairment_expense=recognized))
    if m=='corporate_asset.impair@1':
        assets=[num(x) for x in c['assets']]; floors=[num(x) for x in c['floors']]
        need(len(assets)==len(floors)==5 and all(v>=0 for v in assets),'invalid_asset_vector')
        ra,rb,rg=n('unit_a_recoverable'),n('unit_b_recoverable'),n('group_recoverable')
        need(min(ra,rb,rg)>=0,'negative_recoverable')
        a=allocation(assets[:2],floors[:2],max(zero,sum(assets[:2])-ra))
        b=allocation(assets[2:4],floors[2:4],max(zero,sum(assets[2:4])-rb))
        stage=a+b+assets[4:]; stage_loss=sum(assets)-sum(stage)
        extra=max(zero,sum(stage)-rg); final=allocation(stage,floors,extra)
        loss=stage_loss+extra
        lines={f'asset_{i+1}':final[i]-assets[i] for i in range(5)}
        lines['impairment_expense']=loss
        return result(dict(unit_stage=stage,unit_loss=stage_loss,group_test_carrying=sum(stage),
            additional_loss=extra,closing_assets=final,total_loss=loss,closing_total=sum(final)),
            {k:v for k,v in sorted(lines.items()) if v})
    if m=='acquisition.tax@1':
        fv,base,rate,consideration=n('fair_value_assets'),n('tax_base'),n('tax_rate'),n('consideration')
        need(0<=rate<=1 and fv>=base and consideration>=fv-(fv-base)*rate,'outside_acquisition_tax_profile')
        dt=(fv-base)*rate; net=fv-dt; gw=consideration-net
        return result(dict(identifiable_assets=fv,dtl=dt,net_identifiable_assets=net,
            goodwill=gw,group_equity=consideration,legal_cash_posting=zero),
            journal(subsidiary_capital=fv,investment=-consideration,
                    goodwill=gw,dtl=-dt))
    if m in ('investment.taxable@1','investment.deductible@1'):
        difference,rate=n('difference'),n('tax_rate')
        need(difference>=0 and 0<=rate<=1,'invalid_investment_tax')
        actual=n('carrying')-n('tax_base') if m=='investment.taxable@1' else n('tax_base')-n('carrying')
        need(difference==actual,'outside_basis_difference_mismatch')
        flags=(c['controls_reversal'],c['no_foreseeable_reversal']) if m=='investment.taxable@1' else (c['probable_reversal'],c['probable_taxable_profit'])
        unknown='unknown' in flags and 'no' not in flags
        if unknown:
            return result(dict(deferred_tax=None,recognition='unresolved',tax_origin='profit'),diagnostics=['outside_basis_tax_findings_missing'])
        recognized=not all(x=='yes' for x in flags) if m=='investment.taxable@1' else all(x=='yes' for x in flags)
        amount=difference*rate if recognized else zero
        lines=journal(tax_expense=amount,dtl=-amount) if m=='investment.taxable@1' else journal(dta=amount,tax_expense=-amount)
        return result(dict(deferred_tax=amount,recognition='recognized' if recognized else 'not_recognized',tax_origin='profit'),lines)
    if m=='exchangeability.assess@1':
        needed,available=n('amount_needed'),n('amount_obtainable')
        need(needed>0 and available>=0 and n('foreign_amount')>=0,'invalid_exchange_amount')
        need(c['significance']!='significant' or available>0,'inconsistent_significance')
        flags=(c['enforceable'],c['normal_delay'],c['permitted'])
        uncertainty='unknown' in flags or c['significance']=='unknown'
        unavailable='no' in flags or c['significance']=='insignificant'
        if unavailable: finding='not_exchangeable'
        elif uncertainty:finding='unresolved'
        else:finding='exchangeable'
        admitted=c['rate_objective']=='met' and c['admitted_rate'] is not None
        if admitted:need(num(c['admitted_rate'])>0,'nonpositive_rate')
        diagnostics=[]
        if finding=='unresolved':diagnostics.append('exchangeability_findings_missing')
        if not admitted:diagnostics.append('rate_objective_not_admitted')
        rate=num(c['admitted_rate']) if admitted and finding!='unresolved' else None
        return result(dict(exchangeability=finding,availability_ratio=available/needed,
            admitted_rate=rate,translated_amount=None if rate is None else n('foreign_amount')*rate,
            estimator='supplied_not_estimated'),diagnostics=diagnostics)
    if m=='exchangeability.transition@1':
        amount,old,new=n('foreign_amount'),n('old_rate'),n('new_rate')
        need(amount>=0 and old>0 and new>0,'invalid_transition_rate')
        change=amount*(new-old)
        liability=c['transition_kind']=='monetary_payable'
        destination='opening_retained' if liability else 'accumulated_translation'
        return result(dict(old_carrying=amount*old,new_carrying=amount*new,
            equity_change=-change if liability else change,destination=destination,
            comparative_restatement=False,period_profit=zero,period_oci=zero),
            journal(**({'payable':-change,'opening_retained':change} if liability else
                       {'net_assets':change,'accumulated_translation':-change})))
    raise Refusal('unsupported_method')
