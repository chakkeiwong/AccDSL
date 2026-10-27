"""One-period par-redemption tax schedule under explicit synthetic fiscal facts."""
from fractions import Fraction as Q
import re

NUMBERS = {'proceeds','liability','coupon','period_rate','tax_rate'}
FISCAL_NUMBERS = {'initial_base','accrued_base','after_coupon_base','deduction','settlement_taxable_income'}
FINDINGS = {'coupon_deductible_at_accrual','discount_not_separately_deductible',
            'fiscal_proceeds_are_debt','settlement_no_additional_tax','sufficient_taxable_income',
            'no_other_counterfactual_earnings_tax','complete_consequences'}


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value, list):
        return [encode(v) for v in value]
    return value


def calculate(request):
    result = dict(wire='CompoundTaxRollforward/1', status='rejected', reason=None,
                  amounts=None, stages=[], journals=[], mutations=[])
    def refuse(status, reason):
        result.update(status=status, reason=reason)
        return result
    if not isinstance(request,dict) or set(request) != NUMBERS | {'fiscal'}:
        return refuse('rejected','request_shape')
    fiscal = request['fiscal']
    if not isinstance(fiscal,dict) or set(fiscal) != FISCAL_NUMBERS | FINDINGS:
        return refuse('rejected','fiscal_shape')
    for key in NUMBERS:
        if request[key] is None:
            return refuse('unresolved','missing_'+key)
    for key,value in fiscal.items():
        if value is None:
            return refuse('unresolved','missing_'+key)
    for key in FINDINGS:
        if type(fiscal[key]) is not bool:
            return refuse('rejected','finding_type')
        if not fiscal[key]:
            return refuse('unresolved' if key == 'complete_consequences' else 'unsupported','finding_'+key)
    parsed = {}
    for key in NUMBERS | FISCAL_NUMBERS:
        value = request[key] if key in NUMBERS else fiscal[key]
        if not isinstance(value,str) or re.fullmatch(r'(0|-?[1-9][0-9]*)(/[1-9][0-9]*)?',value) is None:
            return refuse('rejected','rational_encoding')
        q = Q(value)
        if str(q) != value:
            return refuse('rejected','rational_encoding')
        parsed[key] = q
    p,l,c,r,t = (parsed[k] for k in ('proceeds','liability','coupon','period_rate','tax_rate'))
    if p <= 0 or l <= 0 or min(c,r,t) < 0 or l > p:
        return refuse('rejected','invalid_amount')
    if t > 1:
        return refuse('unsupported','tax_rate_profile')
    if l*(1+r) != p+c:
        return refuse('rejected','contract_present_value')
    if any(parsed[k] != v for k,v in dict(initial_base=p,accrued_base=p+c,
            after_coupon_base=p,deduction=c,settlement_taxable_income=Q(0)).items()):
        return refuse('unsupported','fiscal_schedule')
    e, interest = p-l,l*r
    stages = []
    for stage,book,tax in [('issue',l,parsed['initial_base']),
                           ('accrued',l+interest,parsed['accrued_base']),
                           ('coupon_paid',l+interest-c,parsed['after_coupon_base']),
                           ('settled',Q(0),Q(0))]:
        stages.append(dict(stage=stage,carrying=book,tax_base=tax,temporary_difference=tax-book,dtl=t*(tax-book)))
    dtl0 = stages[0]['dtl']
    deferred = stages[1]['dtl']-dtl0
    current = -t*parsed['deduction']
    amounts = dict(gross_equity=e,finance_expense=interest,initial_dtl=dtl0,
        net_issue_equity=e-dtl0,current_tax_expense_delta=current,
        deferred_tax_expense_delta=deferred,after_tax_cost=interest+current+deferred)
    journals = [
        dict(id='issue',entries=dict(cash=p,new_debt=-l,new_conversion_equity=-e)),
        dict(id='issue_tax',entries=dict(new_conversion_equity=dtl0,compound_dtl=-dtl0)),
        dict(id='accrue',entries=dict(finance_expense=interest,new_debt=-interest)),
        dict(id='accrue_tax',entries=dict(compound_dtl=-deferred,deferred_tax=deferred)),
        dict(id='current_tax_delta',entries=dict(current_tax=current,current_tax_payable=-current)),
        dict(id='coupon',entries=dict(new_debt=c,cash=-c))]
    result.update(status='conditional_complete',amounts=encode(amounts),stages=encode(stages),journals=encode(journals))
    return result
