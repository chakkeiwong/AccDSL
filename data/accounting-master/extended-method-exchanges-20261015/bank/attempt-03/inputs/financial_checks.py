"""Independent exact derivations. Never imports expected cases or the builder.

Debits are positive. Discounting is confined to an explicitly dated integer
annual/half-year grid; values and judgments are synthetic supplied premises.
"""
from copy import deepcopy
from datetime import date
from fractions import Fraction as F

def derive(tag,original,method,p,event_date,require):
    c=deepcopy(original);j={};cash={k:F(0) for k in ['operating','investing','financing','unclassified']}
    oci={'fair_value':F(0)};equity={'issue':F(0)}
    def line(k,v):j[k]=j.get(k,F(0))+v
    def flow(v,kind='operating'):line('cash',v);cash[kind]+=v
    def evidence(v):require(v is not None,'cash_evidence_unresolved','partial')
    def amount(v):require(v>=0,'negative_amount')
    def history():
        require(p['measurement_available'],'measurement_unresolved','partial')
        require(p['horizon_supported'] and p['horizon_evidence'] is not None,'exposure_horizon_unresolved','partial')
        for k in ['current_risk_id','information_id','law_id','measurement_vintage']:c[k]=p[k]
    def losses(a,u):
        amount(a);amount(u);require(a<=c['gross'],'allowance_exceeds_gross')
        da,du=a-c['allowance'],u-c['provision']
        line('allowance',-da);line('commitment_provision',-du);line('impairment_expense',da+du)
        c.update(allowance=a,provision=u)
    def allocation(total):
        if p['interest_component'] is not None:
            require(0<=p['interest_component']<=total,'cash_allocation_mismatch')

    if tag=='loan':
        require(c['measurement_basis']=='amortised_cost_non_POCI','loan_measurement_method_required','unsupported')
        if method=='loan.originate':
            require(not c['originated'],'loan_already_originated')
            require(event_date==c['grid'][0],'origination_date_mismatch')
            require(p['classification_admitted'],'classification_unresolved','partial')
            require(p['amount']==c['principal']>0,'principal_mismatch')
            require(c['principal']==c['terminal']/c['factor']**c['due_index'],'original_rate_contract_mismatch')
            if p['mode']=='external':evidence(p['cash_evidence']);flow(-p['amount'])
            else:
                line('deposits',-p['amount']);c['deposits']+=p['amount'];c['pending_transfer']+=p['amount']
            c['gross']=p['amount'];line('gross_loan',p['amount']);c['legal_unpaid']=c['terminal'];c['originated']=True
        elif method=='loan.external_transfer':
            evidence(p['cash_evidence']);require(0<p['amount']<=c['pending_transfer'],'pending_transfer_mismatch')
            line('deposits',p['amount']);flow(-p['amount']);c['deposits']-=p['amount'];c['pending_transfer']-=p['amount']
        elif method=='loan.deposit':
            evidence(p['cash_evidence']);amount(p['amount']);flow(p['amount']);line('deposits',-p['amount']);c['deposits']+=p['amount']
        elif method=='loan.deposit_interest':
            require(p['contractual_accrual_supported'],'deposit_interest_terms_unresolved','partial');amount(p['amount'])
            line('deposit_interest_expense',p['amount']);line('deposits',-p['amount']);c['deposits']+=p['amount']
        elif method=='loan.accrue':
            require(c['originated'] and c['gross']>0,'no_live_loan')
            n=p['index'];require(n==c['clock']+1 and n<len(c['grid']),'discount_clock_mismatch')
            require(event_date==c['grid'][n],'discount_date_mismatch')
            # No new contractual interest after maturity. Net interest on a
            # delayed expected recovery still unwinds the loss allowance.
            gd=c['gross']*(c['factor']-1) if n<=c['due_index'] else F(0)
            impaired=c['credit_impaired'] and n>=c['net_from_index']
            interest=(c['gross']-c['allowance'])*(c['factor']-1) if impaired else gd
            da=gd-interest
            require(c['allowance']+da>=0,'negative_allowance')
            line('gross_loan',gd);line('interest_income',-interest);line('allowance',-da)
            c.update(gross=c['gross']+gd,allowance=c['allowance']+da,clock=n)
        elif method=='loan.measure':
            require(c['originated'] and c['gross']>0,'no_live_loan');history()
            require(event_date==c['grid'][c['clock']],'discount_date_mismatch')
            require(p['credit_finding_supported'],'credit_assessment_unresolved','partial')
            require(p['credit_impaired'] or not c['credit_impaired'],'separate_cure_required')
            require(p['law_kind']=='disjoint_scenarios' and p['mutually_exclusive_exhaustive'],'probability_law_unresolved','partial')
            ss=p['scenarios'];require(sum(s['weight'] for s in ss)==1 and all(s['weight']>=0 for s in ss),'probability_law_invalid')
            require(len({s['scenario_id'] for s in ss})==len(ss),'scenario_identity_duplicate')
            now=c['clock'];lifetime=p['sicr'] or p['credit_impaired'];ecl=F(0)
            reporting=date.fromisoformat(event_date);cutoff=reporting.replace(year=reporting.year+1)
            contractual=c['terminal']/c['factor']**max(0,c['due_index']-now)
            require(contractual==c['gross'],'gross_contractual_pv_mismatch')
            for s in ss:
                default=s['default_index']
                require(default is None or (0<=default<len(c['grid']) and (default>now or p['credit_impaired'])),'default_date_scope')
                pv=F(0)
                for f in s['receipts']:
                    require(now<=f['index']<len(c['grid']) and 0<=f['cost']<=f['gross'],'recovery_cashflow_invalid')
                    pv+=(f['gross']-f['cost'])/c['factor']**(f['index']-now)
                require(0<=pv<=contractual,'negative_credit_shortfall')
                if default is None:require(pv==contractual,'no_default_cashflow_mismatch')
                if lifetime or (default is not None and date.fromisoformat(c['grid'][default])<=cutoff):ecl+=s['weight']*(contractual-pv)
            delta=ecl-c['allowance'];line('impairment_expense',delta);line('allowance',-delta)
            if p['credit_impaired'] and not c['credit_impaired']:c['net_from_index']=now+1
            c.update(allowance=ecl,sicr=p['sicr'],credit_impaired=p['credit_impaired'])
        elif method=='loan.modify':
            require(c['originated'],'no_live_loan')
            require(p['non_derecognition_supported'],'derecognition_assessment_unresolved','partial')
            require(p['fees']==p['costs']==0,'modification_fee_method_required','unsupported')
            require(event_date==c['grid'][c['clock']],'discount_date_mismatch')
            n=p['new_due_index'];require(c['clock']<n<len(c['grid']),'modified_maturity_scope');amount(p['new_terminal'])
            target=p['new_terminal']/c['factor']**(n-c['clock']);delta=target-c['gross']
            line('gross_loan',delta);line('modification_expense',-delta)
            c.update(gross=target,terminal=p['new_terminal'],legal_unpaid=p['new_terminal'],due_index=n,modified=True)
        elif method=='loan.cure':
            require(c['credit_impaired'],'not_credit_impaired')
            require(p['objective_improvement'] and p['subsequent_event'] and p['evidence'] is not None,'objective_cure_unresolved','partial')
            require(p['sicr_remains'],'sicr_cure_method_required','unsupported')
            c.update(credit_impaired=False,cure_evidence=p['evidence'],sicr=True)
        elif method=='loan.collect':
            require(event_date>=c['grid'][c['due_index']],'early_collection_method_required','unsupported')
            evidence(p['cash_evidence']);allocation(p['amount']);require(0<p['amount']<=c['gross'],'collection_amount_mismatch')
            flow(p['amount']);line('gross_loan',-p['amount']);c['gross']-=p['amount'];c['legal_unpaid']-=p['amount']
            if p['full_contractual_settlement']:
                require(c['gross']==c['legal_unpaid']==0,'incomplete_contractual_settlement')
                line('allowance',c['allowance']);line('impairment_expense',-c['allowance']);c['allowance']=F(0)
            require(c['gross']>=c['allowance'],'collection_requires_loss_remeasurement')
            c['last_cash_evidence']=p['cash_evidence']
        elif method=='loan.writeoff':
            require(p['no_reasonable_recovery'] and p['finding_evidence'] is not None,'writeoff_finding_unresolved','partial')
            require(not p['legal_waiver'],'legal_waiver_method_required','unsupported')
            require(0<p['amount']<=min(c['gross'],c['allowance']),'writeoff_amount_mismatch')
            line('gross_loan',-p['amount']);line('allowance',p['amount'])
            c['gross']-=p['amount'];c['allowance']-=p['amount'];c['written_off']+=p['amount']
        elif method=='loan.recovery':
            evidence(p['cash_evidence']);require(c['written_off']>0 and 0<p['amount']<=min(c['legal_unpaid'],c['written_off']-c['recovered']),'recovery_amount_mismatch')
            flow(p['amount']);line('recovery_income',-p['amount']);c['legal_unpaid']-=p['amount'];c['recovered']+=p['amount'];c['last_cash_evidence']=p['cash_evidence']
        else:require(False,'unknown_method','unsupported')
    elif tag=='commitment':
        require(not c['lapsed'],'facility_lapsed')
        if method=='commitment.reserve_full':
            require(not c['revolving'] and c['gross']==0 and not c['fully_drawn'],'full_commitment_scope');history()
            require(event_date==c['measurement_date'],'commitment_date_scope','unsupported')
            require(p['sicr_supported'],'credit_assessment_unresolved','partial')
            require(0<=p['draw_probability']<=1 and p['default_first']>=0 and p['default_later']>=0 and p['default_first']+p['default_later']<=1,'probability_law_invalid')
            pd=p['default_first']+(p['default_later'] if p['lifetime'] else 0)
            ecl=p['draw_probability']*pd*(c['terminal']-c['recovery'])/c['factor']**2
            losses(F(0),ecl)
            c.update(draw_probability=p['draw_probability'],default_first=p['default_first'],default_later=p['default_later'],lifetime=p['lifetime'],horizon_evidence=p['horizon_evidence'])
        elif method=='commitment.draw_full':
            require(event_date==c['measurement_date'],'commitment_date_scope','unsupported')
            require(not c['revolving'] and not c['fully_drawn'] and p['amount']==c['capacity']==c['limit'],'full_draw_amount_mismatch')
            require(p['classification_admitted'],'classification_unresolved','partial')
            if p['mode']=='external':evidence(p['cash_evidence']);flow(-p['amount'])
            else:line('deposits',-p['amount']);c['deposits']+=p['amount'];c['pending_transfer']+=p['amount']
            line('gross_loan',p['amount']);c.update(gross=p['amount'],capacity=F(0),fully_drawn=True,draw_probability=F(1))
            # Drawing is observed: its probability is one in this conditional law.
            pd=c['default_first']+(c['default_later'] if c['lifetime'] else 0)
            losses(pd*(c['terminal']-c['recovery'])/c['factor']**2,F(0))
        elif method=='commitment.external_transfer':
            evidence(p['cash_evidence']);require(0<p['amount']<=c['pending_transfer'],'pending_transfer_mismatch')
            flow(-p['amount']);line('deposits',p['amount']);c['deposits']-=p['amount'];c['pending_transfer']-=p['amount']
        elif method=='commitment.lapse':
            require(c['gross']==0 and p['rights_expired'] and p['evidence'] is not None,'expiry_unresolved','partial')
            losses(F(0),F(0));c.update(capacity=F(0),lapsed=True)
        elif method in ['commitment.revolving_draw','commitment.revolving_repay']:
            require(c['revolving'] and not c['inseparable'],'revolving_scope');history();evidence(p['cash_evidence'])
            require(p['funded_ecl'] is not None and p['undrawn_ecl'] is not None,'measurement_unresolved','partial')
            n=p['amount'];require(n>0,'negative_amount')
            if method.endswith('_draw'):
                require(n<=c['capacity'],'facility_limit_exceeded');flow(-n);line('gross_loan',n);c['gross']+=n;c['capacity']-=n
            else:
                require(p['replenishment_supported'],'replenishment_unresolved','partial');require(n<=c['gross'],'repayment_amount_mismatch')
                flow(n);line('gross_loan',-n);c['gross']-=n;c['capacity']+=n
            losses(p['funded_ecl'],p['undrawn_ecl']);c['horizon_evidence']=p['horizon_evidence']
        elif method=='commitment.combined':
            history();require(p['cannot_separate_supported'],'inseparability_unresolved','partial')
            require(p['combined_ecl'] is not None,'measurement_unresolved','partial');amount(p['combined_ecl'])
            a=min(c['gross'],p['combined_ecl']);losses(a,p['combined_ecl']-a);c.update(inseparable=True,horizon_evidence=p['horizon_evidence'])
        else:require(False,'unknown_method','unsupported')
    elif tag=='fee':
        if method=='fee.receive':
            require(not c['received'],'fee_already_received');require(p['purpose_supported'],'fee_purpose_unresolved','partial')
            evidence(p['cash_evidence']);require(p['amount']==c['fee'],'fee_amount_mismatch')
            flow(p['amount']);line('fee_liability',-p['amount']);c.update(received=True,liability=p['amount'])
        elif method=='fee.originate':
            require(c['purpose']=='probable_specific_loan' and c['received'] and not c['originated'] and not c['expired'],'fee_origination_scope')
            require(p['specific_loan_probable'] and p['classification_admitted'],'fee_origination_facts_unresolved','partial')
            require(c['zero_ecl_isolation_supported'],'fee_credit_measurement_unresolved','partial')
            a,z=date.fromisoformat(c['origination_date']),date.fromisoformat(c['maturity_date'])
            require((z.year-a.year,z.month-a.month,z.day-a.day)==(1,0,0),'fee_rate_period_scope','unsupported')
            evidence(p['cash_evidence']);require(p['amount']==c['principal'] and event_date==c['origination_date'],'fee_principal_date_mismatch')
            carrying=p['amount']-c['liability'];require(carrying*c['factor']==c['terminal'],'fee_rate_mismatch')
            flow(-p['amount']);line('fee_liability',c['liability']);line('gross_loan',carrying);c.update(gross=carrying,liability=F(0),originated=True)
        elif method=='fee.accrue':
            require(c['originated'] and not c['settled'] and c['interest_recognised']==0,'fee_accrual_scope')
            require(event_date==c['maturity_date'],'fee_accrual_date_mismatch')
            require(p['zero_ecl_isolation_supported'] and c['zero_ecl_isolation_supported'],'fee_credit_measurement_unresolved','partial')
            interest=c['gross']*(c['factor']-1);line('gross_loan',interest);line('interest_income',-interest);c['gross']+=interest;c['interest_recognised']=interest
        elif method=='fee.collect':
            require(event_date>=c['maturity_date'],'early_collection_method_required','unsupported')
            evidence(p['cash_evidence']);allocation(p['amount']);require(c['originated'] and not c['settled'] and p['amount']==c['gross']==c['terminal'],'fee_collection_mismatch')
            flow(p['amount']);line('gross_loan',-p['amount']);c.update(gross=F(0),settled=True)
        elif method=='fee.expire':
            require(c['purpose']=='probable_specific_loan' and c['received'] and not c['originated'] and not c['expired'],'fee_expiry_scope')
            require(p['rights_expired'] and p['evidence'] is not None,'expiry_unresolved','partial')
            line('fee_liability',c['liability']);line('fee_income',-c['liability']);c.update(liability=F(0),expired=True)
        elif method=='fee.service':
            require(c['purpose']=='equal_stand_ready' and c['received'],'fee_service_scope')
            n=p['elapsed'];require(n==c['service_elapsed']+1 and n<=len(c['service_dates']),'service_clock_mismatch')
            require(event_date>=c['service_dates'][n-1],'future_service_not_performed')
            require(p['equal_service_performed'] and p['revenue_method_admitted'],'service_pattern_unresolved','partial')
            revenue=c['fee']/len(c['service_dates']);line('fee_liability',revenue);line('fee_income',-revenue);c['liability']-=revenue;c['service_elapsed']=n
        else:require(False,'unknown_method','unsupported')
    elif tag=='liquidity':
        if method=='liquidity.capacity':
            require(p['eligibility_supported'] and p['haircut_supported'],'capacity_terms_unresolved','partial')
            c['capacity']=min(c['limit'],c['eligible_lot']*(1-c['haircut']))
        elif method=='liquidity.request':
            require(c['request_status']=='none','funding_request_exists')
            require(p['request_evidence'] is not None,'request_evidence_unresolved','partial')
            require(0<p['amount']<=c['capacity'],'request_exceeds_capacity')
            c.update(requested=p['amount'],request_status='pending')
        elif method=='liquidity.settle':
            require(p['evidence_kind']!='timeout' and p['amount'] is not None and p['cash_evidence'] is not None,'funding_receipt_unresolved','partial')
            require(p['settlement_id'] not in c['settlement_ids'],'settlement_evidence_duplicate')
            n=p['amount'];amount(n)
            require((p['evidence_kind']=='verified_no_receipt')==(n==0),'receipt_evidence_mismatch')
            breach=c['request_status']!='pending' or n>c['requested'] or n>c['capacity']
            # Confirmed money is recognised even when the request breached a control.
            flow(n,'financing');line('funding',-n);c['cash']+=n;c['funding']+=n;c['actual_received']+=n
            c.update(request_status='settled',receipt_status='verified_zero' if n==0 else 'confirmed' if n==c['requested'] else 'partial',
                control_breach=c['control_breach'] or breach,receipt_evidence=p['cash_evidence'])
            c['settlement_ids'].append(p['settlement_id'])
        elif method=='liquidity.withdraw':
            evidence(p['actual_payment_evidence']);require(p['withdrawal_id'] not in c['withdrawal_ids'],'withdrawal_evidence_duplicate')
            require(c['unpaid_deposits']==0,'existing_unpaid_withdrawal_method_required','unsupported')
            n=p['requested'];require(0<n<=c['deposits'],'withdrawal_amount_mismatch')
            paid=min(n,c['cash']);flow(-paid);line('deposits',paid);c['cash']-=paid;c['deposits']-=paid;c['unpaid_deposits']=n-paid;c['withdrawal_ids'].append(p['withdrawal_id'])
        else:require(False,'unknown_method','unsupported')
    else:require(False,'unknown_component','unsupported')
    j={k:v for k,v in j.items() if v}
    require(sum(j.values())==0,'derived_journal_unbalanced')
    return c,j,cash,oci,equity

def check_component(tag,c,b):
    assert sum(b.values())==0
    assert b['cash']>=0 and b['gross_loan']>=0 and -b['allowance']>=0 and b['gross_loan']+b['allowance']>=0
    if tag in ['loan','commitment','liquidity']:
        assert b['gross_loan']==c['gross'] and b['allowance']==-c['allowance'] and b['deposits']==-c['deposits']
    if tag=='loan':
        assert c['factor']>0 and c['factor']>=1 and 0<=c['clock']<len(c['grid']) and c['due_index']<len(c['grid'])
        dates=[date.fromisoformat(d) for d in c['grid']];assert dates==sorted(set(dates))
        spacing={(z.year-a.year)*12+z.month-a.month for a,z in zip(dates,dates[1:])}
        assert len(spacing)==1 and spacing <= {6,12} and all(a.day==z.day for a,z in zip(dates,dates[1:]))
        assert c['original_risk_date']<=c['grid'][0] and c['legal_unpaid']>=0 and c['written_off']>=c['recovered']>=0
        assert c['pending_transfer']>=0 and c['pending_transfer']<=c['deposits']
    if tag=='commitment':
        assert b['commitment_provision']==-c['provision'] and c['capacity']>=0
        assert c['lapsed'] or c['capacity']+c['gross']==c['limit']
        assert not c['fully_drawn'] or c['draw_probability']==1
        assert c['horizon_kind'] in ['contractual','behavioural_exception']
        assert c['factor']>=1 and c['terminal']>=c['recovery']>=0
        if not c['revolving']:
            a,z=date.fromisoformat(c['measurement_date']),date.fromisoformat(c['maturity_date'])
            assert (z.year-a.year,z.month-a.month,z.day-a.day)==(2,0,0)
            assert c['limit']*c['factor']**2==c['terminal']
    if tag=='fee':
        assert b['gross_loan']==c['gross'] and b['fee_liability']==-c['liability'] and c['liability']>=0
        assert b['allowance']==0
    if tag=='liquidity':
        assert b['cash']==c['cash'] and b['securities']==c['securities'] and b['funding']==-c['funding']
        assert 0<=c['unpaid_deposits']<=c['deposits'] and 0<=c['haircut']<=1
