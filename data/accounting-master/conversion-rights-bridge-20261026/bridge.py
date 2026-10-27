"""Selected synthetic conversion over unchanged declared-book engines."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import declared_company_program_v2 as runtime
import declared_financing_methods_v1 as h

spec = importlib.util.spec_from_file_location('two_date_control_for_conversion_bridge', HERE.parent/'two-date-financing-control-20261026/financing_control.py')
decision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decision)
DATE, TEXT, BOOL = {'kind':'date','context':{}}, {'kind':'text','context':{}}, runtime.core.BOOL
SCOPE = 'Explicit synthetic carrying-value transfer; no source, legal, valuation or accounting admission.'


def make(chart='alpha', carrying='80', branch='conversion'):
    roles = ('cash','project','senior','convertible','capital','issued_equity')
    mapping = {role:role if chart=='alpha' else f'B{90-i*11}' for i,role in enumerate(roles)}
    classes = dict(cash='asset', project='asset', senior='liability', convertible='liability', capital='equity', issued_equity='equity')
    context = dict(entity='Conversion-'+chart,book='legal-'+chart,currency='USD',case_id='synthetic-conversion-'+chart,mode='synthetic')
    book = dict(profile=runtime.engine.BOOK,context=context,period=dict(start='2028-01-01',end_exclusive='2029-01-01'),
                date='2028-01-01',accounts={mapping[r]:dict(classification=classes[r]) for r in roles},
                balances={mapping[r]:h.fmt(v) for r,v in dict(cash=0,project=100,senior=-40,convertible=-F(carrying),capital=F(carrying)-60,issued_equity=0).items()},
                cash_account=mapping['cash'],seen=[],flows=[])
    money=runtime.engine.money_type(book)
    share={**deepcopy(money),'dimensions':{'equity:share':1}}
    types=dict(face=money,old_shares=share,new_shares=share,conversion_shares=share,decision_date=DATE,observed=BOOL,converted=BOOL,signal=TEXT)
    fields={k:({'type':'boolean'} if t['kind']=='boolean' else h.scalar(t['kind'])) for k,t in types.items()}
    shape=h.record({'financing':h.record(fields),'unrelated':h.record({'tag':h.scalar('text')})})
    schema_hash=runtime.digest(shape)
    book.update(memory_schema=schema_hash, memory_types={**{'/financing/'+k:t for k,t in types.items()},'/unrelated/tag':TEXT},
                memory={'financing':dict(face='80/1',old_shares='40/1',new_shares='0/1',conversion_shares='120/1',decision_date='2028-01-01',observed=False,converted=False,signal='unobserved'),
                        'unrelated':{'tag':'preserve-conversion-complement'}})
    schemas={schema_hash:shape}
    entries={}
    for selected in ('debt','conversion'):
        identity='synthetic.selected-conversion.'+selected
        event_inputs=dict(approved=BOOL,signal_input=TEXT)
        bindings={**{k:(t,h.memory('/financing/'+k)) for k,t in types.items()},
                  'liability':(money,h.account('convertible')),'event_date':(DATE,h.event('event_date')),
                  **{k:(t,h.event(k)) for k,t in event_inputs.items()}}
        eq=lambda name,value,typ:h.binary('eq',h.ref(name),h.constant(typ,value))
        pre=[('approved',h.ref('approved'),['approved'],'unsupported'),
             ('on_decision_date',h.binary('eq',h.ref('event_date'),h.ref('decision_date')),['event_date','decision_date'],'invalid'),
             ('signal_matches',eq('signal_input',selected,TEXT),['signal_input'],'invalid'),
             ('unobserved',eq('observed',False,BOOL),['observed'],'invalid'),
             ('unconverted',eq('converted',False,BOOL),['converted'],'invalid'),
             ('new_face80',eq('face','80/1',money),['face'],'invalid'),
             ('old_shares40',eq('old_shares','40/1',share),['old_shares'],'invalid'),
             ('no_new_shares',eq('new_shares','0/1',share),['new_shares'],'invalid'),
             ('conversion_shares120',eq('conversion_shares','120/1',share),['conversion_shares'],'invalid'),
             ('liability_credit',h.binary('le',h.ref('liability'),h.constant(money,'0/1')),['liability'],'invalid')]
        post=[('observed',eq('observed',True,BOOL),['observed'],'invalid'),
              ('signal_retained',eq('signal',selected,TEXT),['signal'],'invalid'),
              ('old_shares_retained',eq('old_shares','40/1',share),['old_shares'],'invalid'),
              ('face',eq('face','0/1' if selected=='conversion' else '80/1',money),['face'],'invalid'),
              ('shares',eq('new_shares','120/1' if selected=='conversion' else '0/1',share),['new_shares'],'invalid'),
              ('converted',eq('converted',selected=='conversion',BOOL),['converted'],'invalid')]
        if selected=='conversion':
            post.append(('carrying_extinguished',eq('liability','0/1',money),['liability'],'invalid'))
        pre_keys={key for _,_,deps,_ in pre for key in deps}
        post_keys={key for _,_,deps,_ in post for key in deps}
        changes={'observed':True,'signal':selected}
        if selected=='conversion':
            changes.update(face='0/1',new_shares='120/1',converted=True)
        input_shape=h.record({})
        local_schemas={schema_hash:shape,runtime.digest(input_shape):input_shape}
        numeric=['liability'] if selected=='conversion' else []
        postings=[] if selected=='debt' else [
            dict(id='remove_liability',account='convertible',expression=h.binary('sub',h.constant(money,'0/1'),h.ref('liability')),requires=['liability']),
            dict(id='issue_equity',account='issued_equity',expression=h.ref('liability'),requires=['liability'])]
        method=dict(profile=runtime.engine.METHOD,id=identity,version='1',context=deepcopy(context),account_map=deepcopy(mapping),
            preconditions=dict(manifest=h.conditions(identity,{k:bindings[k][0] for k in sorted(pre_keys)},pre),bindings={k:bindings[k][1] for k in sorted(pre_keys)}),
            postconditions=dict(manifest=h.conditions(identity,{k:bindings[k][0] for k in sorted(post_keys)},post),bindings={k:bindings[k][1] for k in sorted(post_keys)}),
            monetary=dict(definition=dict(profile=runtime.engine.monetary.PROFILE,method_id=identity,version='1',
                inputs={k:h.declaration(bindings[k][0],k) for k in numeric},calculations=[],accounts={r:money for r in roles},cash_account='cash',postings=postings,flows=[]),
                bindings={k:bindings[k][1] for k in numeric}),
            memory=dict(definition=dict(profile=runtime.engine.memory.PROFILE,state_schema=schema_hash,input_schema=runtime.digest(input_shape),
                operations=[dict(id='write.'+k,op='replace',path=['financing',k],value=dict(kind='literal',value=v)) for k,v in changes.items()]),input_bindings={}),
            residual_prerequisites=[SCOPE])
        entries[selected]=dict(method_sha256=runtime.digest(method),method=method,schemas=local_schemas,account_classes=classes,
                               event_inputs=event_inputs,metadata_bindings={'event_date':'date'},clock={'kind':'direct_event_date'})
        schemas.update(local_schemas)
    statement_map=dict(profile=runtime.reports.MAP,context=deepcopy(context),lines=[dict(id=r,label=r,classification=classes[r],accounts=[mapping[r]]) for r in roles])
    event=dict(id='signal.'+branch,date='2028-01-01',inputs={k:dict(type=deepcopy(entries[branch]['event_inputs'][k]),value=runtime.engine.known(v),provenance=SCOPE) for k,v in dict(approved=True,signal_input=branch).items()})
    movements=[] if branch=='debt' else [dict(id='conversion',event_id=event['id'],date=event['date'],account=mapping['issued_equity'],amount=h.fmt(carrying),description='Supplied noncash carrying-value transfer to issued equity')]
    body=dict(profile=runtime.PROFILE,name='selected-conversion-'+chart,opening=book,schemas=schemas,
              registry=dict(profile=runtime.methods.REGISTRY,context=deepcopy(context),entries=entries),mapping=statement_map,
              commands=[dict(kind='event',method_key=branch,event=event),dict(kind='report',id='after_signal',cutoff=event['date'],equity_movements=movements,notes=[dict(id='scope',label='Supplied conversion treatment',status='unresolved',reason=SCOPE)])])
    return body,mapping


def project_rights(book,mapping):
    state=book['memory']['financing']
    if not state['observed'] or state['signal'] not in ('debt','conversion'):
        raise ValueError('signal_unobserved')
    converts=state['signal']=='conversion'
    if state['converted'] != converts or F(state['old_shares'])!=40 or F(state['new_shares'])!=(120 if converts else 0) or F(state['face'])!=(0 if converts else 80):
        raise ValueError('inconsistent_conversion_rights')
    if converts and F(book['balances'][mapping['convertible']]) != 0:
        raise ValueError('converted_carrying_remaining')
    old,new=F(state['old_shares']),F(state['new_shares'])
    if F(book['balances'][mapping['senior']]) != -40:
        raise ValueError('senior_premise_changed')
    return dict(date=state['decision_date'],senior_face=F(40),new_debt=F(state['face']),old_shares=old,new_shares=new,
                old_cash_fraction=old/(old+new),new_cash_fraction=new/(old+new),old_vote_fraction=old/(old+new),new_vote_fraction=new/(old+new),
                controller='new' if new>old else 'old' if old>new else None,
                conversion=dict(date=state['decision_date'],debt_extinguished=F(80),shares_issued=new) if converts else None)
