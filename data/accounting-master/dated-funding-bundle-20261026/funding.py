"""Finite joint funding proposals over unchanged typed-book methods; no durable commit."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import declared_company_program_v2 as runtime
import declared_financing_methods_v1 as h
spec=importlib.util.spec_from_file_location('two_date_decision_for_funding',HERE.parent/'two-date-financing-control-20261026/financing_control.py')
decision=importlib.util.module_from_spec(spec);spec.loader.exec_module(decision)
MODEL=json.loads((HERE.parent/'two-date-financing-control-20261026/model.json').read_text())
BOOL=runtime.core.BOOL
SCOPE='Synthetic joint funding and cost-basis transfers; no source, accounting or durable transaction admission.'
ROLES=('cash','project','senior','convertible','capital','issued_equity','investment')
CLASSES=dict(cash='asset',project='asset',senior='liability',convertible='liability',capital='equity',issued_equity='equity',investment='asset')
PARTIES=('company','owner','new_holder','seller')


def transfers(quote):
    return [dict(id='new_issue',payer='new_holder',payee='company',date='2027-01-01',amount=h.fmt(quote)),
            dict(id='owner_contribution',payer='owner',payee='company',date='2027-01-01',amount=h.fmt(60-F(quote))),
            dict(id='investment_purchase',payer='company',payee='seller',date='2027-01-01',amount='60/1')]


def fixture(chart='alpha',owner_cash='22',new_cash='40'):
    mapping={r:r if chart=='alpha' else f'C{300-i*13}' for i,r in enumerate(ROLES)}
    books={};schemas={}
    for actor in PARTIES:
        context=dict(entity='Funding-'+actor,book=actor+'-'+chart,currency='USD',case_id='synthetic-funding-'+chart,mode='synthetic')
        amounts={r:F(0) for r in ROLES}
        if actor=='company':amounts.update(project=F(40),senior=F(-40))
        elif actor=='seller':amounts.update(project=F(60),capital=F(-60))
        else:
            cash=F(owner_cash if actor=='owner' else new_cash);amounts.update(cash=cash,capital=-cash)
        book=dict(profile=runtime.engine.BOOK,context=context,period=dict(start='2027-01-01',end_exclusive='2028-01-01'),date='2027-01-01',
                  accounts={mapping[r]:dict(classification=CLASSES[r]) for r in ROLES},balances={mapping[r]:h.fmt(v) for r,v in amounts.items()},
                  cash_account=mapping['cash'],seen=[],flows=[])
        types=dict(settled=BOOL);memory=dict(settled=False)
        if actor=='company':
            money=runtime.engine.money_type(book);share={**deepcopy(money),'dimensions':{'equity:share':1}}
            types.update(face=money,old_shares=share,new_shares=share);memory.update(face='0/1',old_shares='40/1',new_shares='0/1')
        shape=h.record({k:({'type':'boolean'} if t['kind']=='boolean' else h.scalar(t['kind'])) for k,t in types.items()})
        book.update(memory=memory,memory_types={'/'+k:t for k,t in types.items()},memory_schema=runtime.digest(shape))
        schemas[runtime.digest(shape)]=shape;books[actor]=book
    quote=F(17000,441)
    return dict(profile='SelectedDatedFunding/1',date='2027-01-01',strategy=dict(debt='risky',conversion='safe'),quote=h.fmt(quote),
                transfers=transfers(quote),books=books,schemas=schemas,mapping=mapping)


def effects(actor,quote):
    quote=F(quote);contribution=60-quote
    if actor=='company':return dict(cash=F(0),project=F(60),convertible=-quote,capital=-contribution),[('new_issue','financing',quote),('owner_contribution','financing',contribution),('investment_purchase','investing',F(-60))]
    amount=contribution if actor=='owner' else quote
    if actor in ('owner','new_holder'):return dict(cash=-amount,investment=amount),[('owner_contribution' if actor=='owner' else 'new_issue','investing',-amount)]
    return dict(cash=F(60),project=F(-60)),[('investment_purchase','investing',F(60))]


def program(book,schemas,mapping,actor,quote):
    money=runtime.engine.money_type(book);identity='selected.funding.'+actor;zero=h.constant(money,'0/1')
    postings,flows=effects(actor,quote)
    bindings={'cash':(money,h.account('cash')),'settled':(BOOL,h.memory('/settled'))}
    pre=[('not_settled',h.binary('eq',h.ref('settled'),h.constant(BOOL,False)),['settled'],'invalid'),
         ('cash_sufficient',h.binary('le',h.constant(money,h.fmt(max(0,-postings.get('cash',F(0))))),h.ref('cash')),['cash'],'invalid')]
    post=[('settled',h.ref('settled'),['settled'],'invalid'),('cash_nonnegative',h.binary('le',zero,h.ref('cash')),['cash'],'invalid')]
    changes=dict(settled=True)
    if actor=='company':
        for field,old,new in [('face','0/1','80/1'),('old_shares','40/1','40/1'),('new_shares','0/1','0/1')]:
            typ=book['memory_types']['/'+field];bindings[field]=(typ,h.memory('/'+field))
            pre.append((field,h.binary('eq',h.ref(field),h.constant(typ,old)),[field],'invalid'))
            post.append((field,h.binary('eq',h.ref(field),h.constant(typ,new)),[field],'invalid'))
        changes['face']='80/1'
    pre_keys={k for _,_,deps,_ in pre for k in deps};post_keys={k for _,_,deps,_ in post for k in deps}
    input_shape=h.record({});local_schemas={**schemas,runtime.digest(input_shape):input_shape}
    method=dict(profile=runtime.engine.METHOD,id=identity,version='1',context=deepcopy(book['context']),account_map=deepcopy(mapping),
        preconditions=dict(manifest=h.conditions(identity,{k:bindings[k][0] for k in sorted(pre_keys)},pre),bindings={k:bindings[k][1] for k in sorted(pre_keys)}),
        postconditions=dict(manifest=h.conditions(identity,{k:bindings[k][0] for k in sorted(post_keys)},post),bindings={k:bindings[k][1] for k in sorted(post_keys)}),
        monetary=dict(definition=dict(profile=runtime.engine.monetary.PROFILE,method_id=identity,version='1',inputs={},calculations=[],accounts={r:money for r in ROLES},cash_account='cash',
            postings=[dict(id=r,account=r,expression=h.constant(money,h.fmt(v)),requires=[]) for r,v in postings.items()],
            flows=[dict(id=ident,activity=activity,origin=ident,expression=h.constant(money,h.fmt(v)),requires=[]) for ident,activity,v in flows]),bindings={}),
        memory=dict(definition=dict(profile=runtime.engine.memory.PROFILE,state_schema=book['memory_schema'],input_schema=runtime.digest(input_shape),
            operations=[dict(id='write.'+k,op='replace',path=[k],value=dict(kind='literal',value=v)) for k,v in changes.items()]),input_bindings={}),residual_prerequisites=[SCOPE])
    entry=dict(method_sha256=runtime.digest(method),method=method,schemas=local_schemas,account_classes=CLASSES,event_inputs={},metadata_bindings={},clock=dict(kind='direct_event_date'))
    event=dict(id='funding.'+actor,date='2027-01-01',inputs={})
    movements=[] if actor!='company' else [dict(id='owner_contribution',event_id=event['id'],date=event['date'],account=mapping['capital'],amount=h.fmt(60-F(quote)),description='Supplied owner capital contribution')]
    statement_map=dict(profile=runtime.reports.MAP,context=deepcopy(book['context']),lines=[dict(id=r,label=r,classification=CLASSES[r],accounts=[mapping[r]]) for r in ROLES])
    return dict(profile=runtime.PROFILE,name=identity,opening=deepcopy(book),schemas=local_schemas,registry=dict(profile=runtime.methods.REGISTRY,context=deepcopy(book['context']),entries={'settle':entry}),mapping=statement_map,
                commands=[dict(kind='event',method_key='settle',event=event),dict(kind='report',id='settlement_report',cutoff=event['date'],equity_movements=movements,notes=[dict(id='scope',label='Synthetic funding',status='unresolved',reason=SCOPE)])])


def cash_schedule(request):
    cash={actor:F(book['balances'][request['mapping']['cash']]) for actor,book in request['books'].items()}
    runtime.core.need(all(value>=0 for value in cash.values()),'negative_initial_cash')
    trace=[]
    for transfer in request['transfers']:
        amount=F(transfer['amount']);payer=transfer['payer'];payee=transfer['payee']
        runtime.core.need(amount>0 and payer!=payee,'positive_external_transfer')
        runtime.core.need(cash[payer]>=amount,'cash_shortfall:'+payer)
        before=deepcopy(cash);cash[payer]-=amount;cash[payee]+=amount
        trace.append(dict(transfer=deepcopy(transfer),before={k:h.fmt(v) for k,v in before.items()},after={k:h.fmt(v) for k,v in cash.items()}))
    return trace


def propose(request):
    original=deepcopy(request['books']);diagnostics={};programs={}
    try:
        runtime.core.need(request['profile']=='SelectedDatedFunding/1','profile')
        runtime.core.need(request['date']=='2027-01-01','funding_date')
        runtime.core.need(set(original)==set(PARTIES),'party_population')
        mapping=request['mapping'];runtime.core.need(set(mapping)==set(ROLES),'account_roles')
        expected_transfers={t['id']:t for t in transfers(request['quote'])}
        runtime.core.need(len(request['transfers'])==3 and {t['id']:t for t in request['transfers']}==expected_transfers,'transfer_contract')
        runtime.core.need(len({(book['context']['entity'],book['context']['book']) for book in original.values()})==len(PARTIES),'distinct_party_books')
        for actor,book in original.items():
            runtime.core.need(book['date']==request['date']==book['period']['start'],'party_date')
            runtime.core.need(book['cash_account']==mapping['cash'],'cash_mapping')
            amounts={role:F(book['balances'][mapping[role]]) for role in ROLES}
            expected={role:F(0) for role in ROLES}
            if actor=='company':expected.update(project=F(40),senior=F(-40))
            elif actor=='seller':expected.update(project=F(60),capital=F(-60))
            else:expected.update(cash=amounts['cash'],capital=-amounts['cash'])
            runtime.core.need(amounts==expected,'opening_premise:'+actor)
        offered=decision.offer(MODEL,request['strategy'],request['quote'],original['owner']['balances'][mapping['cash']])
        runtime.core.need(offered['status']=='accepted','offer:'+','.join(offered['reasons']))
        schedule=cash_schedule(request)
        for actor in PARTIES:
            programs[actor]=program(original[actor],request['schemas'],mapping,actor,request['quote'])
            diagnostics[actor]=runtime.run(programs[actor])
            runtime.core.need(diagnostics[actor]['status']=='complete_provisional','party_refusal:'+actor)
        after={actor:diagnostics[actor]['current'] for actor in PARTIES}
        runtime.core.need(sum(F(book['balances'][mapping['cash']]) for book in after.values())==sum(F(book['balances'][mapping['cash']]) for book in original.values()),'joint_cash')
        for transfer in request['transfers']:
            found=[]
            for actor in (transfer['payer'],transfer['payee']):
                rows=[f for f in after[actor]['flows'] if f['origin']==transfer['id']]
                runtime.core.need(len(rows)==1,'transfer_population');found.append(F(rows[0]['amount']))
                runtime.core.need(rows[0]['date']==transfer['date'],'transfer_date')
            runtime.core.need(found==[-F(transfer['amount']),F(transfer['amount'])],'reciprocal_cash')
        runtime.core.need(schedule[-1]['after']=={actor:book['balances'][mapping['cash']] for actor,book in after.items()},'schedule_book_agreement')
        return dict(status='proposed_joint_funding',current=after,programs=programs,diagnostics=diagnostics,offer=offered,cash_schedule=schedule,committed=False,durable=False)
    except (ValueError,KeyError,TypeError) as exc:
        return dict(status='refused',reason=str(exc),current=original,programs=programs,diagnostics=diagnostics,committed=False,durable=False)
