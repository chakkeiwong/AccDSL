"""Independent exact insurance oracle. Does not import fixtures or the builder."""
from copy import deepcopy
from fractions import Fraction as F

class Refusal(Exception):
    def __init__(self, code): self.code=code; super().__init__(code)
def need(ok, code):
    if not ok: raise Refusal(code)
def num(v):
    if isinstance(v,F): return v
    need(isinstance(v,dict) and set(v)=={'n','d'},'invalid_rational')
    x=F(int(v['n']),int(v['d']))
    need(str(x.numerator)==v['n'] and str(x.denominator)==v['d'],'noncanonical_rational')
    return x
def unpack(v):
    if isinstance(v,dict):
        if set(v)=={'n','d'}: return num(v)
        return {k:unpack(x) for k,x in v.items()}
    if isinstance(v,list): return [unpack(x) for x in v]
    return v
def wire(v):
    if isinstance(v,F): return {'n':str(v.numerator),'d':str(v.denominator)}
    if isinstance(v,dict): return {k:wire(x) for k,x in v.items()}
    if isinstance(v,list): return [wire(x) for x in v]
    return v
def liability(s):
    return s['lrc']+s['lic'] if s['model']=='PAA' else s['fcf']+s['csm']
def invariant(s):
    i,j,h,a=(s[k] for k in ('issued','replacement','held','accounts'))
    for z in (i,j):
        need(all(v>=0 for k,v in z.items() if k not in ('model','allocated_oci')),'negative_component')
        need(z['ra']<=z['fcf'] and not (z['csm'] and z['loss']),'incompatible_components')
        need(z['acquisition_asset']<=z['acquisition_gross'],'acquisition_above_cost')
    need(0<=h['loss_recovery']<=h['fcf_asset']+h['cost_csm'],'invalid_loss_recovery')
    assets=a['cash']+a['underlying']+a['derivative']+i['acquisition_asset']+j['acquisition_asset']+h['fcf_asset']+h['cost_csm']
    need(assets==liability(i)+liability(j)+a['equity'],'unbalanced_owner_states')
def journal(old,new):
    d=lambda role,k:new[role][k]-old[role][k]
    entries={
        'cash':d('accounts','cash'),'underlying_asset':d('accounts','underlying'),
        'derivative_asset':d('accounts','derivative'),
        'issued_acquisition_asset':d('issued','acquisition_asset'),
        'replacement_acquisition_asset':d('replacement','acquisition_asset'),
        'issued_liability':liability(old['issued'])-liability(new['issued']),
        'replacement_liability':liability(old['replacement'])-liability(new['replacement']),
        'held_asset':sum(d('held',k) for k in ('fcf_asset','cost_csm')),
        'insurance_service_result':-d('accounts','profit')+d('accounts','finance')+d('accounts','held_result'),
        'insurance_finance_result':-d('accounts','finance'),
        'reinsurance_result':-d('accounts','held_result'),'oci':-d('accounts','oci')}
    need(sum(entries.values())==0,'unbalanced_journal')
    return [{'account':k,'signed_debit':v} for k,v in sorted(entries.items()) if v]
def evaluate(raw,opening):
    e=unpack(raw); old=unpack(opening); s=deepcopy(old); invariant(old)
    for k,v in e.items():
        if isinstance(v,F):
            if k in ('current_rate','incurrence_rate','allocation_rate'): need(v>-1,'invalid_discount_rate')
            elif k!='fcf_change': need(v>=0,'negative_event_quantity')
    m=e['method_id']; i=s['issued']; j=s['replacement']; h=s['held']; a=s['accounts']
    d={}; codes=[]
    def gain(p,finance=F(0),held=F(0),oci=F(0)):
        a['profit']+=p; a['finance']+=finance; a['held_result']+=held
        a['oci']+=oci; a['equity']+=p+oci
    if m=='grouping.assess@1':
        if e['membership']=='unknown': codes=['membership_unresolved']
        else:
            need(len({x['contract_id'] for x in e['contracts']})==len(e['contracts']),'duplicate_contract')
            for x in e['contracts']:
                need(all(x[k]==e[k] for k in ('portfolio_id','cohort','profitability','contract_role')),'incompatible_membership')
            d={'group_id':e['group_id'],'member_count':F(len(e['contracts'])),'contract_role':e['contract_role']}
    elif m=='acquisition.allocate@1':
        need(sum(x['amount'] for x in e['allocations'])==e['paid'],'allocation_not_conserved')
        need(len({x['allocation_id'] for x in e['allocations']})==len(e['allocations']),'duplicate_allocation')
        x=sum(x['amount'] for x in e['allocations'] if x['group_id']==e['target_group'])
        need(x==e['paid'] and x>=0,'unsupported_cross_group_allocation')
        i['acquisition_asset']+=x; i['acquisition_gross']+=x; a['cash']-=x
        d={'allocated':x,'unallocated':F(0)}
    elif m=='acquisition.recoverability@1':
        need(0<=e['recoverable'],'negative_recoverable')
        x=min(e['recoverable'],i['acquisition_gross']); change=x-i['acquisition_asset']
        i['acquisition_asset']=x; gain(change)
        d={'asset':x,'impairment_expense':-change}
    elif m=='gmm.recognize@1':
        need(i['fcf']==i['csm']==i['loss']==0,'already_recognized')
        x=e['claims']+e['ra']; transferred=i['acquisition_asset']
        margin=e['premium']-x-transferred
        i.update(model='GMM',fcf=x,ra=e['ra'],csm=max(margin,F(0)),loss=max(-margin,F(0)),acquisition_asset=F(0),acquisition_gross=F(0),remaining_units=e['units'])
        a['cash']+=e['premium']; gain(-i['loss'])
        d={'transferred_acquisition':transferred,'initial_loss':i['loss'],'csm':i['csm']}
    elif m=='gmm.future@1':
        need(i['model']=='GMM','wrong_model'); delta=e['fcf_change']; prior_loss=i['loss']
        if delta>=0:
            use=min(i['csm'],delta); i['csm']-=use; extra=delta-use; i['loss']+=extra; p=-extra
        else:
            reversal=min(i['loss'],-delta); i['loss']-=reversal; i['csm']+=-delta-reversal; p=reversal
        i['fcf']+=delta; gain(p)
        d={'loss_change':i['loss']-prior_loss,'profit_change':p,'csm':i['csm']}
    elif m=='gmm.service@1':
        i=s[e['owner']]
        need(i['model']=='GMM' and i['loss']==0,'unsupported_loss_service_allocation')
        need(0<e['units']<=i['remaining_units'],'invalid_service_units')
        release=i['csm']*e['units']/i['remaining_units']; rev=e['expected_claims']+e['ra_release']+release
        i['fcf']-=e['expected_claims']+e['ra_release']; i['ra']-=e['ra_release']; i['csm']-=release; i['remaining_units']-=e['units']
        a['cash']-=e['actual_claims']; a['revenue']+=rev; a['service_expense']+=e['actual_claims']; gain(rev-e['actual_claims'])
        d={'revenue':rev,'csm_release':release,'claims_expense':e['actual_claims']}
    elif m=='reinsurance.recognize@1':
        need(i['loss']>0 and h['fcf_asset']==h['cost_csm']==0,'invalid_treaty_opening')
        need(e['recognition_date']>=e['entry_date'] and e['recognition_date']>=e['coverage_start'],'invalid_treaty_recognition')
        need(0<=e['share']<=1 and 0<=e['covered_loss']<=i['loss'],'invalid_covered_allocation')
        need(e['covered_group']==e['issued_group'] and e['coverage_mapping']=='admitted','wrong_coverage_join')
        parts=e['allocations']; covered=[p for p in parts if p['covered']]
        need(len({p['contract_id'] for p in parts})==len(parts),'duplicate_contract')
        need(all(p[k]>=0 for p in parts for k in ('premium','claims','ra')),'negative_allocation')
        need(sum(p['claims']+p['ra'] for p in parts)==i['fcf'] and sum(p['ra'] for p in parts)==i['ra'] and sum(p['premium'] for p in parts)==i['fcf']-i['loss'],'allocation_not_conserved')
        need(e['covered_claims']==sum(p['claims'] for p in covered) and e['covered_loss']==sum(max(p['claims']+p['ra']-p['premium'],F(0)) for p in covered),'wrong_covered_loss')
        recovery=e['covered_claims']*e['share']; lr=e['covered_loss']*e['share'] if e['entry_date']<=e['underlying_recognition'] else F(0)
        f=recovery+e['transferred_ra']; base=e['premium']-f
        need(base>=0,'unsupported_net_gain_held')
        h.update(fcf_asset=f,cost_csm=base+lr,loss_recovery=lr); a['cash']-=e['premium']; gain(lr,held=lr)
        d={'expected_recovery':recovery,'initial_loss_recovery':lr,'held_asset':f+base+lr}
    elif m=='reinsurance.change@1':
        need(e['cause']=='covered_claim_estimate' and e['issued_csm_treatment']=='loss_reversal','wrong_change_cause')
        delta=e['new_covered_claims']-e['old_covered_claims']; need(delta<=0,'unsupported_adverse_treaty_change')
        need(-delta<=i['loss'] and 0<=e['new_covered_loss']<=i['loss']+delta,'invalid_covered_allocation')
        recovery_change=delta*e['share']; cap=e['new_covered_loss']*e['share']
        need(h['loss_recovery']+recovery_change==cap,'unaccounted_recovery_component_change')
        i['fcf']+=delta; i['loss']+=delta; h['fcf_asset']+=recovery_change; h['loss_recovery']=cap
        gain(-delta+recovery_change,held=recovery_change)
        d={'issued_loss_reversal':-delta,'held_expense':-recovery_change,'recovery_cap':cap}
    elif m=='reinsurance.nonperformance@1':
        need(0<=e['loss']<=h['fcf_asset'],'invalid_collectability_loss')
        h['fcf_asset']-=e['loss']; gain(-e['loss'],held=-e['loss'])
        d={'collectability_expense':e['loss'],'csm_change':F(0)}
    elif m=='reinsurance.settle@1':
        need(e['claims']==i['fcf']-i['ra'] and e['recovery']==h['fcf_asset']-e['transferred_ra'],'settlement_estimate_mismatch')
        issued_p=liability(i)-e['claims']; held_p=e['recovery']-h['fcf_asset']-h['cost_csm']
        revenue=liability(i)-i['loss']; a['revenue']+=revenue; a['service_expense']+=e['claims']-i['loss']
        a['cash']+=e['recovery']-e['claims']; gain(issued_p+held_p,held=held_p)
        for k in ('fcf','ra','csm','loss','remaining_units'): i[k]=F(0)
        h.update(fcf_asset=F(0),cost_csm=F(0),loss_recovery=F(0))
        d={'issued_profit':issued_p,'held_result':held_p,'issued_revenue':revenue}
    elif m in ('modification.replace@1','contract.transfer@1'):
        need(i['model']=='GMM' and i['loss']==0,'unsupported_modification_opening')
        if m=='modification.replace@1':
            if e['equivalent_premium'] is None: codes=['equivalent_premium_unresolved']
            need(e['modification_test']=='derecognize' and e['existing_right']==False,'modification_not_admitted')
            premium=e['equivalent_premium']; transfer=F(0) if premium is None else premium-e['actual_extra']
        else: transfer=e['third_party_premium']
        if not codes:
            need(0<=e['removed_fcf']<=i['fcf'] and 0<=e['removed_ra']<=i['ra'] and transfer>=0,'invalid_derecognition_allocation')
            csm=i['csm']+e['removed_fcf']-transfer; loss=max(-csm,F(0)); i['csm']=max(csm,F(0)); i['loss']=loss
            i['fcf']-=e['removed_fcf']; i['ra']-=e['removed_ra']; i['remaining_units']-=e['removed_units']; gain(-loss)
            if m=='modification.replace@1':
                need(j['model']=='none' and e['new_fcf']<=premium,'unsupported_new_onerous_group')
                j.update(model='GMM',fcf=e['new_fcf'],ra=e['new_ra'],csm=premium-e['new_fcf'],remaining_units=e['new_units']); a['cash']+=e['actual_extra']
            else: a['cash']-=transfer
            d={'deemed_or_transfer':transfer,'actual_cash_change':e['actual_extra'] if m=='modification.replace@1' else -transfer,'old_csm':i['csm'],'loss':loss}
    else:
        return evaluate_models(e,old,s)
    if codes: s=deepcopy(old); d={}
    invariant(s)
    return wire({'status':'unresolved' if codes else 'resolved','diagnostics':codes,'closing':s,'detail':d,'journal':journal(old,s)})

def evaluate_models(e,old,s):
    m=e['method_id']; i=s['issued']; a=s['accounts']; d={}
    def gain(p,finance=F(0),oci=F(0)):
        a['profit']+=p; a['finance']+=finance; a['oci']+=oci; a['equity']+=p+oci
    if m=='paa.recognize@1':
        need(e['eligibility']=='admitted' and e['coverage_years']<=1,'paa_not_admitted')
        need(i['model']=='none','already_recognized')
        cost=e['acquisition_paid']; p=e['premium']; expense=cost if e['expense_election'] else F(0)
        i.update(model='PAA',lrc=p-(cost-expense),paa_cost_remaining=cost-expense,unearned_premium=p,remaining_units=e['units'])
        a['cash']+=p-cost; gain(-expense)
        d={'lrc':i['lrc'],'acquisition_expense':expense,'cash_change':p-cost}
    elif m=='paa.service@1':
        need(i['model']=='PAA' and i['loss']==0,'unsupported_paa_loss_allocation')
        need(0<e['units']<=i['remaining_units'],'invalid_service_units')
        fraction=e['units']/i['remaining_units']; rev=i['unearned_premium']*fraction; cost=i['paa_cost_remaining']*fraction
        i['lrc']-=rev-cost; i['unearned_premium']-=rev; i['paa_cost_remaining']-=cost; i['remaining_units']-=e['units']
        a['revenue']+=rev; a['service_expense']+=cost; gain(rev-cost)
        d={'revenue':rev,'acquisition_expense':cost,'lrc':i['lrc']}
    elif m=='paa.onerous@1':
        need(i['model']=='PAA' and e['facts_indicate_onerous'],'paa_onerous_not_admitted')
        loss=max(e['remaining_fcf']-i['lrc'],F(0)); i['lrc']+=loss; i['loss']+=loss; gain(-loss)
        d={'additional_loss':loss,'lrc':i['lrc']}
    elif m=='paa.claim@1':
        need(i['model']=='PAA' and i['lrc']==0 and i['lic']==0,'unsupported_claim_opening')
        need(e['rate_origin']=='claim_incurrence' and e['rate_date']==e['claim_date'],'wrong_rate_origin')
        years=e['years']; need(years.denominator==1 and 0<years<=10,'invalid_horizon')
        pv=e['payment']/(1+e['incurrence_rate'])**int(years)
        i.update(lic=pv+e['ra'],ra=e['ra'],fcf=e['ra'],allocation_carrying=pv)
        a['service_expense']+=i['lic']; gain(-i['lic'])
        d={'claim_pv':pv,'lic':i['lic'],'incurrence_rate':e['incurrence_rate']}
    elif m=='paa.finance@1':
        need(i['model']=='PAA' and e['rate_origin']=='claim_incurrence' and e['rate_date']==e['claim_date'],'wrong_rate_origin')
        years=e['remaining_years']; need(years.denominator==1 and 0<=years<=10,'invalid_horizon')
        current=e['payment']/(1+e['current_rate'])**int(years)
        previous=i['lic']-i['ra']; pl=i['allocation_carrying']*e['incurrence_rate']; total=current-previous
        need(0<=e['ra_release']<=i['ra'],'invalid_ra_release')
        i['ra']-=e['ra_release']; i['fcf']=i['ra']; i['allocation_carrying']+=pl; i['lic']=current+i['ra']
        a['revenue']+=e['ra_release']; gain(-pl+e['ra_release'],finance=-pl,oci=pl-total)
        d={'profit_finance_expense':pl,'oci_income':pl-total,'current_finance_expense':total,'ra_release':e['ra_release'],'lic':i['lic']}
    elif m=='paa.settle@1':
        need(i['model']=='PAA' and i['lic']==e['payment'] and i['ra']==0,'unsettled_claim_components')
        a['cash']-=e['payment']; i['lic']=F(0); i['allocation_carrying']=F(0)
        d={'cash_paid':e['payment'],'revenue':F(0)}
    elif m=='vfa.recognize@1':
        need(e['participation']=='admitted' and e['insurance']=='admitted' and e['role']=='issued','vfa_not_admitted')
        need(0<=e['policyholder_share']<=1 and i['model']=='none','invalid_vfa_opening')
        investment=e['pool']*e['policyholder_share']; fcf=investment+e['claims']+e['ra']; csm=e['premium']-fcf
        need(csm>=0,'unsupported_initial_vfa_loss')
        i.update(model='VFA',fcf=fcf,ra=e['ra'],csm=csm,investment=investment,remaining_units=e['units'])
        a['cash']+=e['premium']-e['pool']; a['underlying']+=e['pool']
        d={'investment_component':investment,'fcf':fcf,'csm':csm}
    elif m=='vfa.pool@1':
        need(i['model']=='VFA' and e['holding']=='held' and e['finance_policy']=='all_profit','unsupported_vfa_policy')
        delta=e['new_pool']-a['underlying']; policy=delta*e['policyholder_share']; fee=delta-policy
        need(i['csm']+fee>=0,'unsupported_negative_fee_change')
        a['underlying']=e['new_pool']; i['investment']+=policy; i['fcf']+=policy; i['csm']+=fee
        d={'asset_gain':delta,'liability_finance_expense':delta,'fee_to_csm':fee,'investment_component':i['investment']}
    elif m=='vfa.service@1':
        need(i['model']=='VFA' and i['loss']==0,'unsupported_vfa_loss_service')
        need(0<e['units']<=i['remaining_units'],'invalid_service_units')
        release=i['csm']*e['units']/i['remaining_units']; rev=e['claims']+e['ra_release']+release
        i['fcf']-=e['claims']+e['ra_release']; i['ra']-=e['ra_release']; i['csm']-=release; i['remaining_units']-=e['units']
        a['cash']-=e['claims']; a['revenue']+=rev; a['service_expense']+=e['claims']; gain(rev-e['claims'])
        d={'service_revenue':rev,'csm_release':release,'profit':rev-e['claims'],'investment_revenue':F(0)}
    elif m=='vfa.guarantee@1':
        need(i['model']=='VFA' and i['loss']==0,'unsupported_vfa_change_opening')
        if e['mitigation']:
            need(e['change_kind']=='financial_guarantee' and e['strategy']=='prior_documented' and e['economic_offset']=='admitted' and e['credit_not_dominant']=='admitted','mitigation_not_admitted')
        i['fcf']+=e['change']; a['derivative']+=e['derivative_gain']
        if e['mitigation']:
            p=e['derivative_gain']-e['change']; loss=F(0)
        else:
            loss=max(e['change']-i['csm'],F(0)); i['csm']=max(i['csm']-e['change'],F(0)); i['loss']+=loss; p=e['derivative_gain']-loss
        finance=e['derivative_gain']-(e['change'] if e['mitigation'] else F(0)); gain(p,finance=finance)
        d={'csm':i['csm'],'loss':loss,'derivative_gain':e['derivative_gain'],'profit_change':p}
    elif m=='vfa.settle@1':
        need(i['model']=='VFA' and i['remaining_units']==i['ra']==i['csm']==0 and i['fcf']==i['investment'],'unsettled_vfa_service')
        need(e['investment_payment']==i['investment'],'wrong_investment_payment')
        a['cash']+=a['underlying']-e['investment_payment']; a['underlying']=F(0); i['fcf']=F(0); i['investment']=F(0)
        d={'investment_paid':e['investment_payment'],'investment_revenue':F(0),'investment_expense':F(0)}
    elif m=='finance.variable@1':
        need(i['model']=='GMM' and i['csm']==i['ra']==0,'unsupported_variable_finance_opening')
        years=e['remaining_years']; elapsed=e['elapsed_years']; need(years.denominator==elapsed.denominator==1 and 0<=elapsed<=years<=10,'invalid_horizon')
        need(i['allocation_carrying']*(1+e['allocation_rate'])**int(years)==e['payment'],'wrong_prospective_allocation_rate')
        pl=i['allocation_carrying']*((1+e['allocation_rate'])**int(elapsed)-1)
        new=e['payment']/(1+e['current_rate'])**int(years-elapsed); total=new-i['fcf']
        i['allocation_carrying']+=pl; i['fcf']=new; gain(-pl,finance=-pl,oci=pl-total)
        d={'profit_finance_expense':pl,'oci_income':pl-total,'current_liability':new,'allocation_carrying':i['allocation_carrying']}
    else: raise Refusal('unsupported_method')
    invariant(s)
    return wire({'status':'resolved','diagnostics':[],'closing':s,'detail':d,'journal':journal(old,s)})
