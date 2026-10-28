"""Authored finite economic claims; not accounting or legal admission."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json

def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def exact(x):
    if isinstance(x,(bool,float)):raise ValueError('exact_rational_required')
    try:return Q(x)
    except (ValueError,TypeError,ZeroDivisionError):raise ValueError('exact_rational_required')

def funding(proceeds,need,mode):
    required=exact(need)
    if required<0:raise ValueError('negative_need')
    if proceeds is None:return dict(status='unresolved_offer',required=str(required),paid=None,shortfall=None)
    cash=exact(proceeds)
    if cash<0:raise ValueError('negative_proceeds')
    if mode not in ['require_full','partial_payment']:raise ValueError('explicit_payment_policy_required')
    if mode=='require_full' and cash<required:
        return dict(status='refused_insufficient_offer',available=str(cash),required=str(required),paid='0',closing_cash=str(cash),unpaid=str(required),funding_gap=str(required-cash))
    paid=min(cash,required)
    return dict(status='conditional_full_payment' if paid==required else 'conditional_partial_payment',available=str(cash),required=str(required),paid=str(paid),closing_cash=str(cash-paid),unpaid=str(required-paid))

def waterfall(estate,claims,priority):
    pool=exact(estate);amounts={k:exact(v) for k,v in claims.items()}
    if pool<0 or any(v<0 for v in amounts.values()):raise ValueError('negative_claim_or_estate')
    if len(priority)!=len(set(priority)) or set(priority)!=set(claims):raise ValueError('priority_claim_population')
    remaining=pool;paid={}
    for ident in priority:
        amount=min(remaining,amounts[ident]);paid[ident]=str(amount);remaining-=amount
    return dict(status='conditional_priority_allocation',payments=paid,equity_residual=str(remaining),estate=str(pool),legal_priority_verified=False)

def opening():
    return dict(id='supplied-conversion-state',estate='100',senior_claim='60',junior_claim='50',junior_active=True,
                old_equity_fraction='1',converted_fraction='0',events=[],source_admission=False)

def convert(state,event):
    if set(event)!={'id','fraction','approved'}:raise ValueError('conversion_fields')
    if not event['id'] or event['id'] in state['events']:raise ValueError('duplicate_conversion')
    if event['approved'] is None:return dict(status='unresolved',reason='conversion_authority_unknown',current=deepcopy(state))
    if event['approved'] is not True:return dict(status='unsupported',reason='conversion_not_approved',current=deepcopy(state))
    if state['junior_active'] is not True:raise ValueError('junior_already_extinguished')
    fraction=exact(event['fraction'])
    if not 0<=fraction<=1:raise ValueError('ownership_fraction')
    result=deepcopy(state);result.update(junior_claim='0',junior_active=False,converted_fraction=str(fraction),old_equity_fraction=str(1-fraction))
    result['events'].append(event['id'])
    return dict(status='conditional_conversion',before_sha256=digest(state),current=result,estate_change='0',cash_flow='0',accounting_admission=False)

def settle_converted(state):
    if state['junior_active'] or exact(state['junior_claim'])!=0:raise ValueError('converted_claim_still_active')
    new,old=exact(state['converted_fraction']),exact(state['old_equity_fraction'])
    if new<0 or old<0 or new+old!=1:raise ValueError('ownership_partition')
    if not state['events']:raise ValueError('conversion_event_required')
    w=waterfall(state['estate'],{'senior':state['senior_claim']},['senior']);residual=Q(w['equity_residual'])
    return dict(status='conditional_converted_distribution',estate=state['estate'],senior=w['payments']['senior'],junior_debt='0',converted_equity=str(new*residual),old_equity=str(old*residual),source_admission=False)
