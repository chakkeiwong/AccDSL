"""Input-driven documentary semantics; no persistent or production commits."""
from copy import deepcopy
from fractions import Fraction as Q
from verify import validate, q


def execute(body, validator, source):
    validated=validate(body,validator,source)
    if validated['status']!='validated':
        return {**validated,'committed':False}
    projection=source['record_registry'][body['projection']['digest']]['body']
    opening=source['record_registry'][projection['opening_ref']['digest']]['body']
    balances={k:q(v) for k,v in opening['balances'].items()}
    opening_balances=deepcopy(balances); share=q(body['share'])
    originals={j['event_kind']:{l['account']:q(l['signed_amount']['constant'])+share*q(l['signed_amount']['coefficient_x']) for l in j['lines']} for j in projection['proposed_journals']}
    cash_classes={e['event_kind']:e['cash_class'] for e in projection['event_plan']}
    cash_classes.update(facility_draw='financing',facility_repayment='financing',facility_interest=body['loan']['interest_cash_class'])
    claims={c['id']:{'ledger':c['ledger'],'recognised':q(c['recognised']),'settled':Q(0),'outstanding':q(c['recognised'])} for c in body['claims'] if c['origin']=='opening'}
    facility_drawn=q(body['facility']['drawn']); new_principal=Q(0)
    principal=validated['principal']; interest=validated['facility_interest']; tax_rate=q(body['tax']['rate'])
    flows={k:Q(0) for k in ['operating','investing','financing']}; schedule=[]; income=None; minimum=balances['cash']
    temporary=['revenue','cost_of_sales','payroll','depreciation','interest','tax']
    for event in body['events']:
        kind=event['kind']; next_claims=deepcopy(claims); next_facility=facility_drawn; next_new=new_principal
        if kind in ['purchase','delivery']:
            for c in body['claims']:
                if c['origin']==kind:
                    next_claims[c['id']]={'ledger':c['ledger'],'recognised':q(c['recognised']),'settled':Q(0),'outstanding':q(c['recognised'])}
        if kind in ['collection','supplier_payment']:
            ledger='receivable' if kind=='collection' else 'payable'
            for c in body['claims']:
                if c['ledger']==ledger and q(c['settlement']):
                    if c['id'] not in next_claims or q(c['settlement'])>next_claims[c['id']]['outstanding']:
                        return {'status':'invalid','reason':'settlement_before_claim_or_excess','event':kind,'committed':False}
                    next_claims[c['id']]['settled']+=q(c['settlement']); next_claims[c['id']]['outstanding']-=q(c['settlement'])
        if kind=='facility_draw':
            lines={'cash':principal,'debt':-principal}; next_facility+=principal; next_new+=principal
        elif kind=='facility_interest': lines={'interest':interest,'cash':-interest}
        elif kind=='facility_repayment':
            if new_principal!=principal: return {'status':'invalid','reason':'principal_state','committed':False}
            lines={'debt':principal,'cash':-principal}; next_facility-=principal; next_new-=principal
        elif kind=='tax':
            before_tax=-balances['revenue']-sum(balances[k] for k in ['cost_of_sales','payroll','depreciation','interest'])
            if before_tax<0: return {'status':'unsupported','reason':'loss_tax_method','committed':False}
            lines={'tax':before_tax*tax_rate,'cash':-before_tax*tax_rate}
        elif kind=='close':
            income={k:(-balances[k] if k=='revenue' else balances[k]) for k in temporary}
            lines={k:-balances[k] for k in temporary}; lines['retained']=sum(balances[k] for k in temporary)
        else: lines=deepcopy(originals[kind])
        if sum(lines.values(),Q(0))!=0: return {'status':'invalid','reason':'unbalanced_journal','committed':False}
        cash_delta=lines.get('cash',Q(0))
        if balances['cash']+cash_delta<0:
            return {'status':'funding_failure','event':kind,'shortfall':-(balances['cash']+cash_delta),
                    'balances':balances,'claims':claims,'facility_drawn':facility_drawn,'flows':flows,
                    'applied':schedule,'committed':False,'conditional_state':True}
        for account,delta in lines.items(): balances[account]+=delta
        claims=next_claims; facility_drawn=next_facility; new_principal=next_new
        if cash_delta: flows[cash_classes[kind]]+=cash_delta
        minimum=min(minimum,balances['cash'])
        for ledger,account,sign in [('receivable','receivables',1),('payable','payables',-1)]:
            assert sum((c['outstanding'] for c in claims.values() if c['ledger']==ledger),Q(0))==sign*balances[account]
        schedule.append({'event':kind,'date':event['at'][:10],'at':event['at'],'journal':lines,'cash_class':cash_classes[kind],
                         'cash_after':balances['cash'],'facility_principal_after':new_principal})
    profit=income['revenue']-sum(income[k] for k in temporary if k!='revenue')
    assets=sum(balances[k] for k in ['cash','receivables','inventory','plant_cost','accum_depreciation','tax_prepaid'])
    liabilities=-(balances['payables']+balances['debt']); equity=-(balances['capital']+balances['retained'])
    assert assets==liabilities+equity
    assert opening_balances['cash']+sum(flows.values(),Q(0))==balances['cash']
    assert all(balances[k]==0 for k in temporary)
    return {'status':'complete_conditional','committed':False,'conditional_state':True,
            'closing_balances':balances,'claims':claims,'journals':schedule,'minimum_cash':minimum,
            'statements':{'assets':assets,'liabilities':liabilities,'equity':equity,'profit':profit,
                          'cash':balances['cash'],'cash_flows':flows},'income':income,'facility_drawn':facility_drawn}
