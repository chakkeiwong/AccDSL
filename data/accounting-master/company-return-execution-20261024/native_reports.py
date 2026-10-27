"""Finite legal-book reporting and conditional carry; no group consolidation."""
from copy import deepcopy
from datetime import date
from native_returns import invariant,need,q,fmt,profit,digest,ASSETS,LIABILITIES,EQUITY,INCOME

def report(opening,closing):
    invariant(opening);invariant(closing)
    need(opening['context']==closing['context'] and opening['period']==closing['period'],'report context')
    need(opening['source']==closing['source'],'report source identity')
    need(closing['tax_closed_until']==closing['period']['end_exclusive'],'annual tax incomplete','unresolved')
    need(opening['date']==opening['period']['start'] and not opening['flows'],'opening report basis')
    need(all(q(opening['balances'][k])==0 for k in INCOME),'opening income not closed')
    b0,b=opening['balances'],closing['balances'];p=profit(b)
    equity=-sum(q(b[k]) for k in EQUITY)+p
    assets={k:fmt(q(b[k])) for k in ASSETS};liabilities={k:fmt(-q(b[k])) for k in LIABILITIES}
    need(sum(q(x) for x in assets.values())-sum(q(x) for x in liabilities.values())==equity,'balance sheet equation')
    flows=closing['flows'];cf={}
    for activity in ['operating','investing','financing']:
        f=[q(x['amount']) for x in flows if x['activity']==activity]
        cf[activity]={'receipts':fmt(sum(x for x in f if x>=0)),
            'payments':fmt(-sum(x for x in f if x<0)),'net':fmt(sum(f))}
    need(q(b['cash'])-q(b0['cash'])==sum(q(x['net']) for x in cf.values()),'cash bridge')
    # Finite profile: all receivable/payable and return balances are operating;
    # capital and original equity do not change. Other capital methods need
    # their own equity bridge, not an inferred balancing movement.
    need(all(b[k]==b0[k] for k in EQUITY),'equity movement method required','unsupported')
    opening_equity=-sum(q(b0[k]) for k in EQUITY)
    need(opening_equity+p==equity,'equity bridge')
    bridge={'profit':p,'depreciation':q(b['depreciation']),
        'deferred_tax':q(b['deferred_tax']),
        **{'change_'+k:-(q(b[k])-q(b0[k])) for k in ['inventory','receivable','payable','recovery_asset','refund_liability']},
        'opening_interest_paid':-q(closing['opening_interest_paid'])}
    need(sum(bridge.values())==q(cf['operating']['net']),'indirect operating cash bridge')
    return {'profile':'ReturnLegalAnnualReport/1','context':deepcopy(closing['context']),
        'period':deepcopy(closing['period']),'conditional':True,
        'balance_sheet':{'assets':assets,'liabilities':liabilities,'equity':fmt(equity)},
        'income':{**{k:fmt(-q(b[k]) if k=='revenue' else q(b[k])) for k in INCOME},'profit':fmt(p)},
        'cash_flows':cf,'indirect_operating':{k:fmt(v) for k,v in bridge.items()},
        'opening_equity':fmt(opening_equity),'closing_cash':b['cash'],
        'remaining_lots':deepcopy(closing['lots']),'source':deepcopy(closing['source']),
        'annual_close_sha256':digest(closing)}

def carry(opening,closing,next_end):
    annual=report(opening,closing)
    try:parsed=date.fromisoformat(next_end)
    except (ValueError,TypeError):need(False,'malformed next period')
    need(parsed.isoformat()==next_end,'canonical next period')
    start=closing['period']['end_exclusive'];need(next_end>start,'next period')
    z=deepcopy(closing);p=profit(closing['balances'])
    z['balances']['retained']=fmt(q(z['balances']['retained'])-p)
    for k in INCOME:z['balances'][k]='0/1'
    z['period']={'start':start,'end_exclusive':next_end};z['date']=start
    z['flows']=[];z['opening_interest_paid']='0/1';z['tax_closed_until']=start
    # Prior-year adjustments remain for provenance but current tax filters by
    # the new period; lifetime ids and disposed lots continue to prevent reuse.
    z['tax_premises']['opening_dta']=z['balances']['dta']
    z['tax_premises']['opening_dtl']=fmt(-q(z['balances']['dtl']))
    z['prior_years'].append({'period':deepcopy(closing['period']),
        'closing_sha256':digest(closing),'report_sha256':digest(annual)})
    return invariant(z)
