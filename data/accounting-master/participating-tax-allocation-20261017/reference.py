"""Documentary three-step IAS 33 participating-tax allocation; no postings."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTEXT={'entity','book','currency','ordinary_class','participating_class','start',
    'end_exclusive','information_date','facts_available_on','rule'}
AMOUNTS={'profit_before_benefit','opening_base_balance','participating_ratio','tax_rate',
    'weighted_average_ordinary','participating_dividend','ordinary_base_dividend',
    'ordinary_tax_dividend','actual_tax_benefit','reported_profit'}
FINDINGS={'equity_classification','fixed_proportional_rights','ordinary_only_tax_benefit',
    'tax_deduction_supported','actual_benefit_recognition_supported','full_actual_benefit_distributed',
    'complete_dividends','no_other_entitlements','denominator_complete','base_balance_supported',
    'same_rights_on_residual_allocation'}


class Refusal(Exception):
    def __init__(self,status,reason):
        self.status,self.reason=status,reason


def require(ok, reason, status='rejected'):
    if not ok:
        raise Refusal(status,reason)


def fields(value, expected, reason):
    require(type(value) is dict and set(value)==expected,reason)


def evaluate(request, *, source_root=ROOT):
    """source_root is an internal fixture hook, never a wire field."""
    empty=dict(result=None,trace=[],journals=[],mutations=[],diluted=None,
               selected=None,selection_status='not_evaluated')
    try:
        for item in json.loads((OUT/'input-lock.json').read_text())['files']:
            p=Path(source_root)/item['path']
            require(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],
                    'source_or_input_changed')
        fields(request,{'wire','operation','context','amounts','benefit_location','findings'},'request_fields')
        require(request['wire']=='ParticipatingTaxEPS/1','wire')
        require(request['operation']=='basic','operation_not_supported','unsupported')
        c=request['context'];fields(c,CONTEXT,'context_fields')
        for value in c.values():
            require(type(value) is str and bool(value.strip()),'context_value')
        require(c['rule']=='IFRS-IC-2017-IAS33-participating-tax','source_profile')
        require(c['ordinary_class']!=c['participating_class'],'class_collision')
        dates={}
        for key in ('start','end_exclusive','information_date','facts_available_on'):
            try:
                d=date.fromisoformat(c[key])
            except (ValueError,TypeError):
                raise Refusal('rejected','date')
            require(d.isoformat()==c[key],'date')
            dates[key]=d
        require(dates['start']<dates['end_exclusive']<=dates['information_date'],'report_period')
        require(dates['facts_available_on']<=dates['information_date'],'future_information')
        fields(request['findings'],FINDINGS,'finding_fields')
        for key,value in request['findings'].items():
            require(value is not None,'missing_finding/'+key,'unresolved')
            require(type(value) is bool,'finding_type')
            require(value,'unsupported_finding/'+key,'unsupported')
        fields(request['amounts'],AMOUNTS,'amount_fields')
        a={}
        for key,value in request['amounts'].items():
            require(value is not None,'missing_amount/'+key,'unresolved')
            require(type(value) is str,'rational_type')
            try:
                q=Q(value)
            except (ValueError,ZeroDivisionError):
                raise Refusal('rejected','rational_value')
            require(str(q)==value,'noncanonical_rational')
            a[key]=q
        p=a['profit_before_benefit'];t=a['tax_rate'];r=a['participating_ratio']
        require(p>=0,'loss_tax_not_specified','unsupported')
        require(all(v>=0 for v in a.values()),'negative_amount')
        require(a['weighted_average_ordinary']>0,'ordinary_denominator')
        require(t<1,'tax_rate')
        location=request['benefit_location']
        require(location in ('profit','equity'),'benefit_location','unsupported')
        dp=a['participating_dividend'];do=a['ordinary_base_dividend']
        h=a['actual_tax_benefit'];dt=a['ordinary_tax_dividend']
        require(dp==r*do,'dividend_rights_mismatch')
        require(h==t*dp,'actual_tax_mismatch')
        require(dt==h,'tax_benefit_payout_mismatch')
        require(a['reported_profit']==p+(h if location=='profit' else 0),'reported_profit_mismatch')
        closing=a['opening_base_balance']+p-dp-do
        require(closing>=0,'unfunded_base_dividend')

        # Source Step 1: normalize actual recognition location, then subtract payouts.
        adjusted=a['reported_profit']+(h if location=='equity' else 0)
        ordinary_declared=do+dt
        residual=adjusted-dp-ordinary_declared
        # Source Step 2: signed residual sharing and its hypothetical benefit.
        participating_residual=residual*r/(1+r)
        ordinary_residual=residual/(1+r)
        residual_tax=t*participating_residual
        # Source Step 3: rejoin declared and residual class allocations.
        ordinary=ordinary_declared+ordinary_residual+residual_tax
        participating=dp+participating_residual
        total=ordinary+participating
        require(total==adjusted+residual_tax,'allocation_invariant')
        require(residual==p-dp-do,'residual_invariant')
        values=dict(adjusted_profit=adjusted,residual_base=residual,
            residual_participating=participating_residual,residual_ordinary=ordinary_residual,
            residual_tax=residual_tax,declared_ordinary=ordinary_declared,
            ordinary_earnings=ordinary,participating_earnings=participating,
            total_eps_earnings=total,closing_base_balance=closing,
            basic_eps=ordinary/a['weighted_average_ordinary'])
        empty.update(status='conditional_complete',reason=None,
            result=dict(context=deepcopy(c),**{k:str(v) for k,v in values.items()}),
            trace=[dict(step='adjust_and_subtract',adjusted_profit=str(adjusted),residual=str(residual)),
                   dict(step='allocate_signed_residual',participating=str(participating_residual),
                        ordinary=str(ordinary_residual),tax=str(residual_tax)),
                   dict(step='add_declared_allocations',ordinary=str(ordinary),participating=str(participating))])
    except Refusal as e:
        empty.update(status=e.status,reason=e.reason)
    return empty
