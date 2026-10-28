"""Conditional legal-book cash/transfer examples; no atomic group settlement."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('location_finance_examples', ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
program, f = ex.program, ex.financing
engine, core = f.engine, f.core
fmt = f.fmt


def recontext(value, old, new):
    if isinstance(value, dict):
        return {(('currency:'+new['currency']) if k=='currency:'+old['currency'] else k):
                recontext(v, old, new) for k,v in value.items()}
    if isinstance(value, list): return [recontext(v, old, new) for v in value]
    if isinstance(value, str):
        for k in ['entity','book','currency','case_id']:
            if value==old[k]: return new[k]
    return value


def base(owner, entity, currency, balances):
    body,_,_,m = ex.fixture(owner)
    old = deepcopy(body['opening']['context'])
    new = {**old, 'entity':entity, 'book':'legal-'+entity, 'currency':currency,
           'case_id':'location-timing-'+owner}
    body = recontext(body, old, new)
    book = body['opening']
    book['balances'] = {key:'0/1' for key in book['balances']}
    book['balances'].update({m[k]:fmt(Q(v)) for k,v in balances.items()})
    book['balances'][m['capital']] = fmt(-sum(Q(v) for v in book['balances'].values()))
    book['memory']['finance']['debt'] = book['balances'][m['debt']]
    schemas = {book['memory_schema']:deepcopy(body['schemas'][book['memory_schema']])}
    policy = {**deepcopy(ex.POLICY), 'annual_rate':'0/1',
        'provenance':'Explicit zero-interest synthetic debt isolates cash availability and timing'}
    registry = f.build(book, schemas, {k:m[k] for k in f.CLASSES}, '/finance/cursor', '/finance/debt',
                       policy, [dict(start='2027-01-01',end_exclusive='2027-01-02')])
    operations = ex.op.operations.build(book, schemas, {k:m[k] for k in ex.op.operations.CLASSES}, '/stock/unit_cost')
    registry['entries'].update(operations['entries'])
    for entry in registry['entries'].values(): schemas.update(deepcopy(entry['schemas']))
    body.update(schemas=schemas,registry=registry,name='location-'+entity,commands=[])
    return body,m


def report(ident='report'):
    return dict(kind='report',id=ident,cutoff='2027-01-03',equity_movements=[],notes=[
        dict(id='conditional',label='Conditional legal-book cash',status='unresolved',
             reason='Synthetic opening, claim and settlement premises; no actual cross-book atomicity or authority admission')])


def cap_method(body):
    entry=body['registry']['entries']['collect']; method=entry['method']
    money=engine.money_type(body['opening'])
    pre=method['preconditions']; pre['manifest']['inputs']['cap']=f.declaration(money,'cap')
    pre['bindings']['cap']=f.event('cap');entry['event_inputs']['cap']=deepcopy(money)
    # Opening intercompany claim30 less current claim is the cumulative transfer.
    used=f.binary('sub',f.constant(money,'30/1'),f.ref('receivables'))
    predicate=f.binary('le',f.binary('add',used,f.ref('amount')),f.ref('cap'))
    pre['manifest']['requirements'].append(dict(id='cumulative_transfer_cap',guard=f.constant(core.BOOL,True),guard_requires=[],
        predicate=predicate,requires=['receivables','amount','cap'],admission_refs=[],on_false='unsupported',on_unknown='unresolved'))
    method['residual_prerequisites'].append('Cap applies cumulatively to collections against this explicitly supplied opening intercompany claim30')
    entry['method_sha256']=program.digest(method)


def parent(owner='alpha', cap='10/1', amounts=('10/1',), pay=True):
    body,m=base(owner,'Parent','USD',dict(cash=5,receivables=30,debt=-20))
    cap_method(body)
    for i,amount in enumerate(amounts):
        body['commands'].append(ex.event(body,'collect','transfer.'+str(i),'2027-01-01',dict(amount=amount,cap=cap)))
    if pay:body['commands'].append(ex.event(body,'debt_redeem','maturity','2027-01-01',dict(amount='20/1')))
    body['commands'].append(report())
    return body,m


def subsidiary(owner='alpha', amount='10/1'):
    body,m=base(owner,'Subsidiary','USD',dict(cash=30,payables=-30))
    body['commands']=[ex.event(body,'supplier_pay','matched.transfer','2027-01-01',dict(amount=amount)),report()]
    return body,m


def foreign(owner='alpha', receipt='2027-01-03', order='chronological', opening='0/1'):
    body,m=base(owner,'Foreign','EUR',dict(cash=opening,receivables=20,debt=-20))
    accrue=ex.event(body,'interest_accrue.1','zero.interest','2027-01-01',{})
    collect=ex.event(body,'collect','foreign.receipt',receipt,dict(amount='20/1'))
    pay=ex.event(body,'debt_redeem','foreign.maturity','2027-01-02',dict(amount='20/1'))
    if order=='receipt_first' or receipt<'2027-01-02': events=[collect,pay]
    else: events=[pay,collect]
    body['commands']=[accrue,*events,report()]
    return body,m
