"""Explicit equity approval/receipt premises over unchanged native execution."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
p = ROOT/'data/accounting-master/company-state-gross-equity-history-20261028/fixture.py'
s = importlib.util.spec_from_file_location('retained_gross_equity_fixture',p)
base = importlib.util.module_from_spec(s);s.loader.exec_module(base)
program,h=base.program,base.h
fmt,ref,binary,constant=base.fmt,base.ref,base.binary,base.constant
RULES=['share_authorization_cap','approval_exists','offer_accepted','subscription_settled','offer_price_matches','receipt_matches']

def make(owner='alpha',shares=15,price=10,guarded=True):
    body,mapping=base.make('issue_only',owner)
    body['registry']['entries']={'equity_issue':body['registry']['entries']['equity_issue']}
    entry=body['registry']['entries']['equity_issue'];method=entry['method']
    pre=method['preconditions'];money=program.engine.money_type(body['opening'])
    share_type=entry['event_inputs']['shares'];price_type=entry['event_inputs']['price']
    if guarded:
        types={'approved':program.core.BOOL,'offer_accepted':program.core.BOOL,
               'settled':program.core.BOOL,'cash_received':money,'offer_price':price_type}
        for name,typ in types.items():
            entry['event_inputs'][name]=deepcopy(typ)
            pre['manifest']['inputs'][name]=h.declaration(typ,name)
            pre['bindings'][name]={'kind':'event','name':name}
        rows=[('share_authorization_cap',binary('le',ref('shares'),constant(share_type,'15/1')),['shares']),
              ('approval_exists',ref('approved'),['approved']),
              ('offer_accepted',ref('offer_accepted'),['offer_accepted']),
              ('subscription_settled',ref('settled'),['settled']),
              ('offer_price_matches',binary('eq',ref('offer_price'),ref('price')),['offer_price','price']),
              ('receipt_matches',binary('eq',ref('cash_received'),binary('mul',ref('shares'),ref('price'))),['cash_received','shares','price'])]
        for name,predicate,requires in rows:
            pre['manifest']['requirements'].append(dict(id=name,guard=constant(program.core.BOOL,True),guard_requires=[],
                predicate=predicate,requires=requires,admission_refs=[],on_false='invalid',on_unknown='unresolved'))
        method['residual_prerequisites'].append('Supplied one-raise authorization15, accepted offer and receipt premises; no actual authority, bank access or legal/accounting admission.')
        entry['method_sha256']=program.digest(method)
    values={'shares':fmt(shares),'price':fmt(price)}
    if guarded:values.update(approved=True,offer_accepted=True,settled=True,cash_received=fmt(Q(shares)*Q(price)),offer_price=fmt(price))
    event=body['commands'][0]['event']
    event['inputs']={k:dict(type=deepcopy(entry['event_inputs'][k]),value=program.engine.known(v),
        provenance='Authored synthetic authorization/offer/receipt premise') for k,v in values.items()}
    body['commands'][-1]['equity_movements'][0]['amount']=fmt(Q(shares)*Q(price))
    body['commands'][-1]['notes']=[dict(id='equity_terms',label='Conditional equity issue',status='unresolved',
        reason='Authorization, offer, receipt and valuation are explicit synthetic premises; real admission absent')]
    body['name']='equity-authority-'+owner
    return body,mapping

def supplied(body,name,value,unknown=False):
    body['commands'][0]['event']['inputs'][name]['value']=dict(status='unknown',reason='Required synthetic premise withheld') if unknown else program.engine.known(value)

def valuation(old_shares,new_shares,economic_assets,issue_price):
    old,new,assets,price=map(Q,[old_shares,new_shares,economic_assets,issue_price])
    if old<=0 or new<0 or assets<0 or price<0:raise ValueError('explicit nonnegative illustrative inputs')
    cash=new*price;total=assets+cash;fraction=old/(old+new)
    return {k:fmt(v) for k,v in dict(old_ownership=fraction,new_ownership=1-fraction,
        new_cash=cash,total_value=total,old_value=fraction*total,new_value=(1-fraction)*total,
        old_value_change=fraction*total-assets,new_value_less_contribution=(1-fraction)*total-cash).items()}
