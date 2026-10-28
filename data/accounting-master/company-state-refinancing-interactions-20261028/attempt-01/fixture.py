"""Supplied refinancing methods on one declared book; no tax-law admission."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
p = ROOT/'data/accounting-master/declared-financing-clock-20261025/examples.py'
s = importlib.util.spec_from_file_location('refinancing_examples', p)
ex = importlib.util.module_from_spec(s); s.loader.exec_module(ex)
program, h, fmt = ex.program, ex.financing, ex.fmt
ref, binary, constant = h.ref, h.binary, h.constant
TAX = dict(profile='SyntheticImmediateDeduction/1', rate='1/4', fee_deductible=True,
           interest_deductible=True, recognition=True, basis='SuppliedTeachingBasis/1',
           source='Authored premises; no actual law, source or accounting admission')


def make(owner='alpha'):
    body, _, _, roles = ex.fixture(owner)
    book = body['opening']; money = program.engine.money_type(book)
    shares = {**deepcopy(money), 'dimensions': {'equity:share': 1}}
    price = {**deepcopy(money), 'dimensions': {'currency:USD': 1, 'equity:share': -1}}
    for key, classification in [('new_debt','liability'), ('fee','expense'),
                                ('current_tax','expense'), ('tax_payable','liability')]:
        if key in roles:
            continue
        account = key if owner == 'alpha' else 'extra.'+key
        roles[key] = account
        book['accounts'][account] = dict(classification=classification)
        body['mapping']['lines'].append(dict(id=key,label=key,classification=classification,accounts=[account]))
    book['balances'] = {k:'0/1' for k in book['accounts']}
    book['balances'].update({roles[k]:fmt(v) for k,v in dict(cash=30,inventory=170,debt=-100,capital=-100).items()})
    shape = deepcopy(body['schemas'][book['memory_schema']])
    shape['properties']['finance'] = h.record({k:h.scalar('rational' if 'debt' in k else 'date')
                                              for k in ['old_cursor','new_cursor','old_debt','new_debt']})
    shape['properties']['ownership'] = h.record(dict(old=h.scalar('rational'),new=h.scalar('rational')))
    shape['required'].append('ownership')
    book['memory']['finance'] = dict(old_cursor=book['date'],new_cursor=book['date'],old_debt='-100/1',new_debt='0/1')
    book['memory']['ownership'] = dict(old='100/1',new='0/1')
    book['memory_types'] = {k:v for k,v in book['memory_types'].items() if not k.startswith('/finance/')}
    book['memory_types'].update({'/finance/'+k:deepcopy(money if 'debt' in k else h.DATE) for k in book['memory']['finance']})
    book['memory_types'].update({'/ownership/'+k:deepcopy(shares) for k in ['old','new']})
    book['memory_schema'] = program.digest(shape)
    schemas = {program.digest(shape):shape}; entries = {}
    for instrument, rate in [('old','0/1'),('new','73/248')]:
        mapped = {k:roles[k] for k in h.CLASSES}
        if instrument == 'new': mapped['debt'] = roles['new_debt']
        policy = dict(profile=h.POLICY,convention='actual_days/365_simple',annual_rate=rate,
                      interest_cash_activity='operating',provenance='Synthetic stated cost2; not market terms')
        reg = h.build(book,schemas,mapped,'/finance/'+instrument+'_cursor',
                      '/finance/'+instrument+'_debt',policy,[dict(start='2027-01-01',end_exclusive='2027-02-01')])
        wanted = ['debt_redeem'] if instrument == 'old' else ['debt_issue','interest_accrue.1','interest_pay']
        for key in wanted: entries[instrument+'.'+key] = reg['entries'][key]
        for e in entries.values(): schemas.update(deepcopy(e['schemas']))

    def method(key, inputs, postings, flows, changes=None, extra=None):
        changes = changes or {}; extra = extra or []
        identity = 'refinancing.teaching.'+key
        types = {k:v[0] for k,v in inputs.items()}; binds = {k:v[1] for k,v in inputs.items()}
        event_types = {k:t for k,(t,b) in inputs.items() if b['kind']=='event'}
        checks = [('cash_nonnegative',binary('le',constant(money,'0/1'),ref('cash_control')),['cash_control'],'invalid')]
        checks += [(k+'_nonnegative',binary('le',constant(t,'0/1'),ref(k)),[k],'invalid') for k,t in event_types.items()]
        checks += extra
        pre_types = {**types,'cash_control':money}; pre_binds={**binds,'cash_control':h.account('cash')}
        used = {k for _,_,deps,_ in checks for k in deps}
        pre_types={k:v for k,v in pre_types.items() if k in used}; pre_binds={k:v for k,v in pre_binds.items() if k in used}
        calculations=[]; fields={}; bindings={}; operations=[]
        for name,(typ,expression,deps,path) in changes.items():
            calculations.append(dict(id=name,type=typ,expression=expression,requires=deps))
            fields[name]=h.scalar('rational'); bindings[name]=dict(kind='calculation',name=name)
            operations.append(dict(id='write.'+name,op='replace',path=path,value=dict(kind='read',source='inputs',pointer='/'+name)))
        ishape=h.record(fields); local_schemas={**schemas,program.digest(ishape):ishape}
        used={k for _,_,d in postings+flows for k in d}|{k for row in calculations for k in row['requires']}
        monetary_types={k:v for k,v in types.items() if k in used}; monetary_binds={k:v for k,v in binds.items() if k in used}
        accounts={'cash'}|{a for a,_,_ in postings}|{b['role'] for b in binds.values() if b['kind']=='account'}
        post=[('cash_nonnegative',binary('le',constant(money,'0/1'),ref('cash_control')),['cash_control'],'invalid')]
        m=dict(profile=program.engine.METHOD,id=identity,version='1',context=deepcopy(book['context']),
            account_map={a:roles[a] for a in accounts},
            preconditions=dict(manifest=h.conditions(identity,pre_types,checks),bindings=pre_binds),
            postconditions=dict(manifest=h.conditions(identity,{'cash_control':money},post),bindings={'cash_control':h.account('cash')}),
            monetary=dict(definition=dict(profile=program.engine.monetary.PROFILE,method_id=identity,version='1',
                inputs={k:h.declaration(t,k) for k,t in monetary_types.items()},calculations=calculations,
                accounts={a:money for a in accounts},cash_account='cash',
                postings=[dict(id=a,account=a,expression=e,requires=d) for a,e,d in postings],
                flows=[dict(id=key,activity=a,origin=key,expression=e,requires=d) for a,e,d in flows]),bindings=monetary_binds),
            memory=dict(definition=dict(profile=program.engine.memory.PROFILE,state_schema=book['memory_schema'],
                input_schema=program.digest(ishape),operations=operations),input_bindings=bindings),
            residual_prerequisites=['Explicit synthetic revenue/fee/share/tax premises; no admission or general tax implementation.'])
        entries[key]=dict(method_sha256=program.digest(m),method=m,schemas=local_schemas,
                          account_classes={a:book['accounts'][roles[a]]['classification'] for a in accounts},
                          event_inputs=event_types,metadata_bindings={},clock=dict(kind='direct_event_date'))
        schemas.update(local_schemas)
    neg=lambda x:binary('sub',constant(money,'0/1'),x)
    amount={'amount':(money,h.event('amount'))}
    method('service_receipt',amount,[('cash',ref('amount'),['amount']),('revenue',neg(ref('amount')),['amount'])],[('operating',ref('amount'),['amount'])])
    method('refinancing_fee',amount,[('fee',ref('amount'),['amount']),('cash',neg(ref('amount')),['amount'])],[('operating',neg(ref('amount')),['amount'])])
    inputs=dict(shares=(shares,h.event('shares')),price=(price,h.event('price')),existing=(shares,h.memory('/ownership/new')))
    subscription=binary('mul',ref('shares'),ref('price'))
    method('equity_subscription',inputs,[('cash',subscription,['shares','price']),('capital',neg(subscription),['shares','price'])],
           [('financing',subscription,['shares','price'])],
           dict(next_shares=(shares,binary('add',ref('existing'),ref('shares')),['existing','shares'],['ownership','new'])))
    method('tax_accrue',amount,[('current_tax',ref('amount'),['amount']),('tax_payable',neg(ref('amount')),['amount'])],[])
    method('tax_pay',{**amount,'payable':(money,h.account('tax_payable'))},
           [('tax_payable',ref('amount'),['amount']),('cash',neg(ref('amount')),['amount'])],[('operating',neg(ref('amount')),['amount'])],
           extra=[('payable_available',binary('le',ref('amount'),neg(ref('payable'))),['amount','payable'],'invalid')])
    body.update(name='joined-refinancing-'+owner,schemas=schemas,registry=dict(profile=program.methods.REGISTRY,context=deepcopy(book['context']),entries=entries),commands=[])
    rows=[('service_receipt','2027-01-01',dict(amount='20/1')),
          ('new.debt_issue','2027-01-01',dict(amount='80/1')),
          ('equity_subscription','2027-01-01',dict(shares='10/1',price='2/1')),
          ('old.debt_redeem','2027-01-01',dict(amount='100/1')),
          ('refinancing_fee','2027-01-01',dict(amount='4/1')),
          ('new.interest_accrue.1','2027-01-31',{}),
          ('new.interest_pay','2027-01-31',dict(amount='2/1'))]
    for key,day,vals in rows:body['commands'].append(event(body,key,key,day,vals))
    return body,roles


def event(body,key,ident,day,values):
    types=body['registry']['entries'][key]['event_inputs']; vals=deepcopy(values)
    if 'approved' in types:vals['approved']=True
    return dict(kind='event',method_key=key,event=dict(id=ident,date=day,inputs={
        k:dict(type=deepcopy(types[k]),value=program.engine.known(v),provenance='Explicit synthetic interaction premise')
        for k,v in vals.items()}))


def finish(body,roles,tax):
    result=deepcopy(body)
    result['commands'] += [event(result,'tax_accrue','tax.accrue','2027-02-01',dict(amount=tax)),
                           event(result,'tax_pay','tax.pay','2027-02-01',dict(amount=tax)),
        dict(kind='report',id='closing',cutoff='2027-02-01',
             equity_movements=[dict(id='subscription',event_id='equity_subscription',date='2027-01-01',
                                    account=roles['capital'],amount='20/1',description='Supplied ordinary shares')],
             notes=[dict(id='scope',label='Supplied refinancing and tax treatment',status='unresolved',
                         reason='Actual contract, tax, authority and accounting admission absent')])]
    return result
