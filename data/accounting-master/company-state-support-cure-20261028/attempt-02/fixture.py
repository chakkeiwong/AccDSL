"""Explicit support/priority examples and separate timestamp assessment."""
from copy import deepcopy
from datetime import datetime
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('support_location_fixture',ROOT/'data/accounting-master/company-state-location-timing-20261028/fixture.py')
location=importlib.util.module_from_spec(spec);spec.loader.exec_module(location)
ex,f,program=location.ex,location.f,location.program
fmt=f.fmt


def parent(owner='alpha',later=True):
    body,m=location.base(owner,'SupportParent','USD',dict(cash=5,debt=-4))
    entry=deepcopy(body['registry']['entries']['supplier_pay']);method=entry['method']
    # A supplied recoverable advance replaces a trade-liability settlement.
    method['account_map']['payables']=m['receivables'];entry['account_classes']['payables']='asset'
    pre=method['preconditions'];pre['manifest']['inputs'].pop('payables');pre['bindings'].pop('payables')
    pre['manifest']['requirements']=[r for r in pre['manifest']['requirements'] if 'payables' not in r['requires']]
    post=method['postconditions'];post['manifest']['inputs'].pop('payables');post['bindings'].pop('payables')
    post['manifest']['requirements']=[r for r in post['manifest']['requirements'] if 'payables' not in r['requires']]
    method['monetary']['definition']['flows'][0].update(activity='investing',origin='supplied_recoverable_support')
    method['residual_prerequisites'].append('Explicit recoverable intercompany advance; not a general guarantee recognition rule')
    entry['method_sha256']=program.digest(method);body['registry']['entries']['support']=entry
    body['commands']=[ex.event(body,'support','support2','2027-01-01',dict(amount='2/1'))]
    if later:body['commands'].append(ex.event(body,'debt_redeem','parent4','2027-01-01',dict(amount='4/1')))
    body['commands'].append(location.report())
    return body,m


def subsidiary(owner='alpha',support=True):
    body,m=location.base(owner,'SupportedSub','USD',dict(cash=4,receivables=80,debt=-70))
    entry=deepcopy(body['registry']['entries']['debt_issue']);method=entry['method']
    method['account_map']['debt']=m['payables']
    for side in ['preconditions','postconditions']:
        manifest=method[side]['manifest'];manifest['inputs'].pop('tracked_debt');method[side]['bindings'].pop('tracked_debt')
        manifest['requirements']=[r for r in manifest['requirements'] if 'tracked_debt' not in r['requires']]
    monetary=method['monetary'];monetary['definition']['inputs'].pop('principal_signed');monetary['bindings'].pop('principal_signed');monetary['definition']['calculations']=[]
    monetary['definition']['flows'][0]['origin']='supplied_support_receipt'
    empty=f.record({});h=program.digest(empty);entry['schemas'][h]=empty;body['schemas'][h]=empty
    method['memory']['definition'].update(input_schema=h,operations=[]);method['memory']['input_bindings']={}
    method['residual_prerequisites'].append('Explicit intercompany payable support; external facility debt memory remains70')
    entry['method_sha256']=program.digest(method);body['registry']['entries']['support_receipt']=entry
    body['commands']=[]
    if support:body['commands'].append(ex.event(body,'support_receipt','receive2','2027-01-01',dict(amount='2/1')))
    body['commands'] += [ex.event(body,'debt_redeem','deficiency6','2027-01-01',dict(amount='6/1')),location.report()]
    return body,m


def allocation(owner='alpha',order='fee_first',amount=Q(6)):
    body,m=location.base(owner,'Arrears','USD',dict(cash=amount,debt=-100,interest_payable=-5,payables=-2))
    entry=deepcopy(body['registry']['entries']['supplier_pay'])
    entry['method']['monetary']['definition']['flows'][0]['origin']='supplied_fee_arrears'
    entry['method']['residual_prerequisites'].append('Payables role explicitly contains fee arrears2 in this fixture')
    entry['method_sha256']=program.digest(entry['method']);body['registry']['entries']['fee_pay']=entry
    remaining=Q(amount);rows=[]
    sequence=[('fee_pay',2),('interest_pay',5),('debt_redeem',100)] if order=='fee_first' else [('debt_redeem',100),('interest_pay',5),('fee_pay',2)]
    for key,owed in sequence:
        paid=min(remaining,Q(owed));remaining-=paid
        if paid:rows.append(ex.event(body,key,key,'2027-01-01',dict(amount=fmt(paid))))
    body['commands']=rows+[location.report()];return body,m


def cure(receipt,payment,paid,arrears_remaining,known=True):
    """Separate conditional assessment; native books do not execute intraday."""
    result=dict(native_intraday_execution=False,contract_admission=False,required='7/1',paid=fmt(Q(paid)),
                arrears_remaining=None if arrears_remaining is None else fmt(Q(arrears_remaining)))
    if not known:return {**result,'status':'unresolved','reason':'Required cure terms or settlement facts unavailable'}
    if arrears_remaining is None:return {**result,'status':'unresolved','reason':'Payment allocation or remaining arrears unavailable'}
    received,settled=map(datetime.fromisoformat,[receipt,payment]);deadline=datetime.fromisoformat('2027-01-05T00:00:00+00:00')
    if received.tzinfo is None or settled.tzinfo is None:return {**result,'status':'invalid','reason':'timezone_required'}
    if settled<received:return {**result,'status':'invalid','reason':'payment_before_receipt'}
    if Q(paid)<0:return {**result,'status':'invalid','reason':'negative_payment'}
    if Q(arrears_remaining)<0 or Q(arrears_remaining)>7:return {**result,'status':'invalid','reason':'arrears_outside_supplied_scope'}
    if Q(paid)+Q(arrears_remaining)<7:return {**result,'status':'invalid','reason':'unexplained_arrears_reduction'}
    return {**result,'status':'conditional_cured' if Q(arrears_remaining)==0 and settled<deadline else 'conditional_not_cured',
            'receipt':receipt,'payment':payment,'deadline_exclusive':deadline.isoformat()}
