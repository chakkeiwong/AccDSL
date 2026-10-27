"""Independent economic derivations. Never import cases or packet construction."""
from copy import deepcopy
from fractions import Fraction as F

def check_component(tag,c,b):
    assert b['derivative_asset']==b['derivative_liability']==0
    assert b['transferred_asset']==c['asset']
    assert b['transfer_liability']==-c.get('liability',0)
    assert b['loss_allowance']==-c.get('allowance',0)
    assert b['fair_value_reserve']==-c.get('reserve',0)
    assert c['asset']>=0 and c.get('liability',0)>=0
    assert 0<=c.get('allowance',0)<=c['asset']
    assert b['cash']>=0
    if tag=='guarantee':
        assert 0<=c['service_fraction']<=1
        if c['phase']=='active':
            assert c['asset']==min(c['initial_asset'],c['cap'])
            assert c['liability']==c['asset']+c['initial_fee']*(1-c['service_fraction'])
        if c['phase']=='expired':assert c['asset']==c['liability']==c['allowance']==0
    if tag=='asset':
        assert c['ecl']>=0
        if c['classification']=='AC':assert c['allowance']==c['ecl']
        elif c['classification']=='debt_FVOCI':assert c['allowance']==0
        else:assert c['allowance']==c['ecl']==0
        if c['phase']=='disposed':assert c['asset']==c['allowance']==c['ecl']==0

def derive(tag,opening,method,p,date,require):
    c=deepcopy(opening);j={};cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    oci={'fair_value':F(0)}
    equity={k:F(0) for k in ['issue','reserve_transfer','retained_transfer']}
    def post(a,x):j[a]=j.get(a,F(0))+F(x)
    def money(x,kind):post('cash',x);cash[kind]+=x
    def finding():
        require(p['finding_supported'] is not None and p['finding_evidence'] is not None,'transfer_finding_required','partial')
        require(p['finding_supported'],'transfer_finding_failed')
        c['finding_evidence']=p['finding_evidence']
    def measured():
        require(p['measurement_available'] and p['measurement_evidence'] is not None,'measurement_required','partial')
    def paid():require(p['cash_evidence'] is not None,'cash_evidence_required','partial')
    def isolated():require(p['fees']==p['prior_oci']==0 and not p['servicing'],'unsupported_transfer_extras','unsupported')
    def gain(x,account='fair_value_gain'):
        if x>=0:post(account,-x)
        else:post('fair_value_expense',-x)
    def fv_values():
        measured()
        s,tc,tp=p['spot'],p['call_time'],p['put_time']
        require(s>=0 and tc>=0 and tp>=0,'invalid_option_value')
        k=c['kind'];kc,kp=c['call_strike'],c['put_strike']
        require((k!='call' or tp==0) and (k!='put' or tc==0),'unused_option_time_value')
        require((k=='call' and kc>0 and kp==0) or (k=='put' and kp>0 and kc==0) or
                (k=='collar' and 0<kp<kc),'invalid_option_strikes')
        a=min(s,kp) if k=='put' else s
        l=kp+tp if k=='put' else min(s,kc)-tc+(max(kp-s,0)+tp if k=='collar' else 0)
        require(l>=0,'invalid_option_liability')
        return a,l
    def update_option(a,l):
        da,dl=a-c['asset'],l-c['liability']
        post('transferred_asset',da);post('transfer_liability',-dl);gain(da-dl)
        c.update(asset=a,liability=l,spot=p['spot'],call_time=p['call_time'],put_time=p['put_time'])

    if method=='transfer.partial':
        require(c['phase']=='unassessed','transfer_already_assessed');finding();isolated();paid()
        require(p['eligible_part'] and p['derecognition_supported'],'partial_derecognition_not_supported')
        require(p['nontrading_investment'],'cash_classification_finding_required','partial')
        sold,ret=p['sold_fv'],p['retained_fv']
        require(sold>0 and ret>0 and p['proceeds']>=0,'invalid_relative_values')
        amount=F(c['asset'])*sold/(sold+ret)
        money(p['proceeds'],'investing');post('transferred_asset',-amount);post('disposal_gain',amount-p['proceeds'])
        c.update(asset=c['asset']-amount,sold_fv=sold,retained_fv=ret,phase='partial')
    elif method=='transfer.retain_risks':
        require(c['phase']=='unassessed','transfer_already_assessed');finding();isolated();paid()
        require(p['proceeds']>0,'invalid_funding_amount')
        money(p['proceeds'],'financing');post('transfer_liability',-p['proceeds'])
        c.update(liability=p['proceeds'],principal_funding=p['proceeds'],phase='funded')
    elif method=='transfer.asset_income':
        require(c['phase']=='funded' and not c['asset_accrued'],'asset_accrual_state')
        require(date==c['accrual_date'],'accrual_anniversary_mismatch')
        require(p['original_eir_supported'] and c['asset_rate']>=0,'asset_eir_not_supported')
        x=c['asset']*c['asset_rate'];post('transferred_asset',x);post('asset_interest_income',-x)
        c.update(asset=c['asset']+x,asset_accrued=True)
    elif method=='transfer.liability_expense':
        require(c['phase']=='funded' and not c['liability_accrued'],'liability_accrual_state')
        require(date==c['accrual_date'],'accrual_anniversary_mismatch')
        require(p['separate_eir_supported'] and c['liability_rate']>=0,'liability_eir_not_supported')
        x=c['liability']*c['liability_rate'];post('transfer_liability',-x);post('liability_interest_expense',x)
        c.update(liability=c['liability']+x,liability_accrued=True)
    elif method=='transfer.repay':
        require(c['phase']=='funded' and c['asset_accrued'] and c['liability_accrued'],'repayment_state')
        require(p['discharge_supported'],'discharge_not_supported');paid()
        require(p['amount']==c['liability'],'repayment_amount_mismatch')
        require(p['interest_component'] is not None and p['contractual_interest_allocation_supported'],
                'cash_interest_allocation_required','partial')
        interest=p['interest_component']
        require(interest==p['amount']-c['principal_funding']>=0,'cash_interest_allocation_mismatch')
        money(-c['principal_funding'],'financing');money(-interest,'operating')
        post('transfer_liability',c['liability']);c.update(liability=F(0),phase='settled')
    elif method=='guarantee.start':
        require(c['phase']=='unassessed','transfer_already_assessed');finding();isolated();measured();paid()
        require(p['continuing_involvement_supported'],'continuing_involvement_not_supported')
        require(p['cap']>0 and p['guarantee_fv']>=0,'invalid_guarantee_values')
        a=min(c['asset'],p['cap']);l=a+p['guarantee_fv']
        require(p['proceeds']==c['asset']+p['guarantee_fv'],'isolated_guarantee_proceeds_mismatch')
        money(p['proceeds'],'unclassified');post('transferred_asset',a-c['asset']);post('transfer_liability',-l)
        c.update(asset=a,liability=l,cap=p['cap'],initial_fee=p['guarantee_fv'],phase='active')
    elif method=='guarantee.service':
        require(c['phase']=='active' and date<c['expiry_date'],'guarantee_service_state')
        require(p['service_evidence'] is not None,'service_evidence_required','partial')
        require(p['equal_service_performed'] and p['revenue_method_admitted'],'service_pattern_not_supported')
        f=p['cumulative_fraction'];require(c['service_fraction']<f<=1,'service_fraction_order')
        x=c['initial_fee']*(f-c['service_fraction']);post('transfer_liability',x);post('guarantee_income',-x)
        c.update(liability=c['liability']-x,service_fraction=f)
    elif method=='guarantee.measure_loss':
        require(c['phase']=='active' and date<c['expiry_date'],'guarantee_measurement_state');measured()
        require(p['expected_loss'] is not None,'expected_loss_required','partial')
        x=p['expected_loss'];require(0<=x<=c['asset'],'invalid_expected_loss')
        d=x-c['allowance'];post('loss_allowance',-d);post('impairment_expense',d);c['allowance']=x
    elif method=='guarantee.expire':
        require(c['phase']=='active' and date==c['expiry_date'],'guarantee_expiry_date')
        require(p['expiry_evidence'] is not None,'expiry_evidence_required','partial')
        require(p['rights_expired'] and p['no_claim_supported'],'no_claim_expiry_not_supported')
        post('loss_allowance',c['allowance']);post('impairment_expense',-c['allowance'])
        post('transferred_asset',-c['asset']);post('transfer_liability',c['liability'])
        post('guarantee_income',c['asset']-c['liability'])
        c.update(asset=F(0),liability=F(0),allowance=F(0),phase='expired',service_fraction=F(1))
    elif method=='option.start':
        require(c['phase']=='unassessed' and date<c['expiry_date'],'option_start_state');finding();isolated();paid()
        require(p['continuing_involvement_supported'],'continuing_involvement_not_supported')
        require(p['zero_day_one_gain_supported'],'day_one_gain_not_in_scope','unsupported')
        a,l=fv_values()
        require(p['proceeds']==c['asset']-a+l,'isolated_option_proceeds_mismatch')
        money(p['proceeds'],'unclassified');post('transferred_asset',a-c['asset']);post('transfer_liability',-l)
        c.update(asset=a,liability=l,spot=p['spot'],call_time=p['call_time'],put_time=p['put_time'],phase='active')
    elif method in ['option.remeasure','option.expire']:
        require(c['phase']=='active','option_measurement_state')
        if method=='option.expire':
            require(date==c['expiry_date'],'option_expiry_date')
            require(p['expiry_evidence'] is not None,'expiry_evidence_required','partial')
            require(p['rights_expired'],'option_expiry_not_supported')
            require(p['call_time']==p['put_time']==0,'expiry_time_value_nonzero')
        else:require(date<c['expiry_date'],'option_measurement_after_expiry')
        a,l=fv_values();update_option(a,l)
        if method=='option.expire':c['phase']='expired'
    elif method=='option.exercise':
        require(c['phase']=='expired' and date==c['expiry_date'],'option_exercise_state')
        require(p['physical_settlement_supported'],'cash_settlement_not_in_scope','unsupported');paid()
        side=p['side'];require(c['kind'] in [side,'collar'],'option_exercise_side')
        strike=c[side+'_strike']
        require((side=='call' and c['spot']>=strike) or (side=='put' and c['spot']<=strike),'option_not_exercisable')
        require(p['amount']==strike==c['liability'],'exercise_amount_mismatch')
        money(-strike,'unclassified');post('transfer_liability',strike);c.update(liability=F(0),phase='exercised')
    elif method=='ac_option.start':
        require(c['phase']=='unassessed' and date<c['accrual_date'],'option_start_state');finding();isolated();paid()
        require(c['zero_allowance_isolation'] and p['zero_allowance_isolation_supported'],'zero_allowance_isolation_required','partial')
        require(p['proceeds']>0 and c['asset_rate']>=0 and c['liability_rate']>=0,'invalid_ac_option_values')
        require(c['asset']*(1+c['asset_rate'])==c['asset_terminal'],'asset_eir_terminal_mismatch')
        require(p['proceeds']*(1+c['liability_rate'])==c['liability_terminal']==c['asset_terminal'],'liability_eir_terminal_mismatch')
        money(p['proceeds'],'unclassified');post('transfer_liability',-p['proceeds'])
        c.update(liability=p['proceeds'],phase='active')
    elif method=='ac_option.accrue_asset':
        require(c['phase']=='active' and not c['asset_accrued'],'asset_accrual_state')
        require(date==c['accrual_date'],'accrual_anniversary_mismatch')
        require(c['zero_allowance_isolation'] and p['zero_allowance_isolation_supported'],'zero_allowance_isolation_required','partial')
        require(p['original_eir_supported'],'asset_eir_not_supported')
        x=c['asset']*c['asset_rate'];require(c['asset']+x==c['asset_terminal'],'asset_eir_terminal_mismatch')
        post('transferred_asset',x);post('asset_interest_income',-x);c.update(asset=c['asset']+x,asset_accrued=True)
    elif method=='ac_option.accrue_liability':
        require(c['phase']=='active' and not c['liability_accrued'],'liability_accrual_state')
        require(date==c['accrual_date'],'accrual_anniversary_mismatch')
        require(p['separate_eir_supported'],'liability_eir_not_supported')
        x=c['liability']*c['liability_rate'];require(c['liability']+x==c['liability_terminal'],'liability_eir_terminal_mismatch')
        post('transfer_liability',-x);post('liability_interest_expense',x);c.update(liability=c['liability']+x,liability_accrued=True)
    elif method=='ac_option.exercise':
        require(c['phase']=='active' and c['asset_accrued'] and c['liability_accrued'] and date==c['accrual_date'],'ac_option_exercise_state')
        require(p['physical_settlement_supported'],'cash_settlement_not_in_scope','unsupported');paid()
        require(p['amount']==c['strike'],'exercise_amount_mismatch')
        money(-p['amount'],'unclassified');post('transfer_liability',c['liability']);post('liability_interest_expense',p['amount']-c['liability'])
        c.update(liability=F(0),phase='exercised')
    elif method=='asset.classify':
        require(c['phase']=='unassessed','classification_is_irrevocable')
        require(p['assessment_evidence'] is not None,'classification_finding_required','partial')
        require(p['initial_recognition'],'initial_election_date_required')
        if c['instrument']=='debt':
            require(p['business_model']!='unknown' and p['sppi'] in ['pass','fail'],'classification_finding_required','partial')
            require(not p['equity_election'],'debt_equity_election_invalid')
            if p['fvtpl_designation']:
                require(p['mismatch_eligible'] is not None,'mismatch_finding_required','partial')
                require(p['mismatch_eligible'],'mismatch_designation_not_eligible')
            route='FVTPL' if p['fvtpl_designation'] or p['sppi']=='fail' or p['business_model']=='other' else ('AC' if p['business_model']=='collect' else 'debt_FVOCI')
        else:
            require(p['sppi']=='not_applicable' and not p['fvtpl_designation'],'equity_classification_inputs')
            require(not (p['held_for_trading'] and p['equity_election']),'trading_equity_election_invalid')
            route='equity_FVOCI' if p['equity_election'] else 'FVTPL'
        require(not p['held_for_trading'],'trading_cash_policy_not_in_scope','unsupported')
        c.update(classification=route,business_model=p['business_model'],sppi=p['sppi'],
                 fvtpl_designated=p['fvtpl_designation'],equity_elected=p['equity_election'],
                 assessment_evidence=p['assessment_evidence'],phase='classified')
    elif method=='asset.acquire':
        require(c['phase']=='classified','asset_purchase_state');paid()
        require(p['fees']==0,'investment_costs_not_in_scope','unsupported')
        require(p['nontrading_investment'],'cash_classification_finding_required','partial')
        require(p['cost']>0,'invalid_investment_cost')
        money(-p['cost'],'investing');post('transferred_asset',p['cost']);c.update(asset=p['cost'],phase='held')
    elif method=='asset.remeasure':
        require(c['phase']=='held','asset_measurement_state');measured()
        require(c['classification']!='AC','AC_does_not_remeasure_to_FV')
        require(p['fair_value']>=0,'invalid_fair_value');d=p['fair_value']-c['asset'];post('transferred_asset',d)
        if c['classification']=='FVTPL':gain(d)
        else:post('fair_value_reserve',-d);oci['fair_value']+=d;c['reserve']+=d
        c['asset']=p['fair_value']
    elif method=='asset.impair':
        require(c['phase']=='held','asset_measurement_state')
        require(c['classification'] in ['AC','debt_FVOCI'],'separate_ECL_not_applicable')
        measured();require(p['expected_loss'] is not None,'expected_loss_required','partial')
        x=p['expected_loss'];require(0<=x<=c['asset'],'invalid_expected_loss');d=x-c['ecl'];post('impairment_expense',d)
        if c['classification']=='AC':post('loss_allowance',-d);c['allowance']=x
        else:post('fair_value_reserve',-d);oci['fair_value']+=d;c['reserve']+=d
        c['ecl']=x
    elif method=='asset.dispose':
        require(c['phase']=='held','asset_disposal_state');paid()
        require(p['rights_transferred'],'asset_disposal_not_supported')
        require(p['proceeds']>=0,'invalid_sale_proceeds');route=c['classification']
        require(route=='AC' or p['proceeds']==c['asset'],'dispose_fv_current_required')
        money(p['proceeds'],'investing');post('transferred_asset',-c['asset']);post('loss_allowance',c['allowance'])
        post('disposal_gain',c['asset']-c['allowance']-p['proceeds'])
        if route=='debt_FVOCI':
            post('fair_value_reserve',c['reserve']);post('disposal_gain',-c['reserve']);oci['fair_value']-=c['reserve'];c['reserve']=F(0)
        c.update(asset=F(0),allowance=F(0),ecl=F(0),phase='disposed')
    elif method=='asset.transfer_reserve':
        require(c['phase']=='disposed' and c['classification']=='equity_FVOCI' and not c['reserve_transferred'],'within_equity_transfer_state')
        require(p['within_equity_elected'],'within_equity_transfer_not_elected')
        r=c['reserve'];post('fair_value_reserve',r);post('retained',-r)
        equity.update(reserve_transfer=-r,retained_transfer=r);c.update(reserve=F(0),reserve_transferred=True)
    elif method=='asset.time_value_probe':
        require(c['phase']=='unassessed' and c['instrument']=='debt' and c['probe_status']=='not_run','time_value_probe_state')
        require(p['scenario_evidence'] is not None and p['matched_benchmark_supported'],'benchmark_evidence_required','partial')
        require(p['principal']>0 and p['contract_rate']>=0 and p['benchmark_rate']>=0 and 1<=p['months']<=12,'invalid_probe_inputs')
        c.update(probe_contractual=p['principal']*(1+p['contract_rate']*F(p['months'],12)),
                 probe_benchmark=p['principal']*(1+p['benchmark_rate']*F(p['months'],12)),probe_status='explanatory_only')
    else:require(False,'unknown_financial_method','unsupported')
    j={k:v for k,v in j.items() if v}
    assert sum(j.values())==0,(method,j)
    assert j.get('cash',0)==sum(cash.values())
    return c,j,cash,oci,equity
