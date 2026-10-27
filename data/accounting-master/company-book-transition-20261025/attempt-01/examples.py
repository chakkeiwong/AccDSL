"""Authored synthetic fixtures; no reported company or accounting authority."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import company_book_transition_v1 as engine
core=engine.core


def record(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}


def scalar(kind):
    if kind=='boolean':return {'type':'boolean'}
    return {'type':'string','minLength':1,'maxLength':4096,'x-exact-kind':kind}


def ref(name):return {'op':'ref','id':name}
def binary(op,left,right):return {'op':op,'left':left,'right':right}
def const(typ,value):return {'op':'const','type':deepcopy(typ),'value':value}
def decl(typ,name,role='state'):
    return {'type':deepcopy(typ),'role':role,'source_ref':'constructed:'+name}
def account(role):return {'kind':'account','role':role}
def mem(pointer):return {'kind':'memory','pointer':pointer}
def event(name):return {'kind':'event','name':name}


def conditions(method_id,types,rows):
    return {'profile':engine.requirements.PROFILE,'method_id':method_id,'version':'1',
            'inputs':{k:decl(t,k) for k,t in types.items()},
            'requirements':[{'id':name,'guard':const(core.BOOL,True),'guard_requires':[],
                             'predicate':node,'requires':deps,'admission_refs':[],
                             'on_false':status,'on_unknown':'unresolved'}
                            for name,node,deps,status in rows],
            'required_known':[],'capabilities':[],
            'residual_prerequisites':['Synthetic applicability only; actual source and accounting admission remain separate.']}


def fixture(owner='alpha',amount='7/2'):
    if owner=='alpha':
        ids={'cash':'bank.alpha','liability':'note.alpha','other':'machine.alpha','equity':'capital.alpha'}
        path=['loan']
    elif owner=='beta':
        ids={'cash':'101','liability':'230','other':'150','equity':'310'}
        path=['contracts','obligation']
    else:raise ValueError('fixture_owner')
    context={'entity':owner,'book':'legal-'+owner,'currency':'USD','case_id':'constructed-'+owner,'mode':'synthetic'}
    book={'profile':engine.BOOK,'context':context,'period':{'start':'2027-01-01','end_exclusive':'2028-01-01'},
          'date':'2027-01-01','accounts':{ids[k]:{'classification':v} for k,v in
          [('cash','asset'),('liability','liability'),('other','asset'),('equity','equity')]},
          'balances':{ids['cash']:'100/1',ids['liability']:'-30/1',ids['other']:'10/1',ids['equity']:'-80/1'},
          'cash_account':ids['cash'],'seen':[],'flows':[]}
    money=engine.money_type(book)
    quantity={**deepcopy(money),'dimensions':{'goods:unit':1}}
    leaf={'outstanding':'30/1','paid':'0/1','last_date':'2027-01-01','last_event':'opening'}
    leaf_shape=record({k:scalar('rational' if k in ['outstanding','paid'] else 'date' if k=='last_date' else 'text') for k in leaf})
    memory,shape=leaf,leaf_shape
    for key in reversed(path):memory,shape={key:memory},record({key:shape})
    memory['untouched']={'tag':'preserve','quantity':'7/1'}
    shape['properties']['untouched']=record({'tag':scalar('text'),'quantity':scalar('rational')})
    shape['required'].append('untouched')
    prefix='/'+'/'.join(path)
    types={prefix+'/'+k:deepcopy(money) if k in ['outstanding','paid'] else {'kind':'date' if k=='last_date' else 'text','context':{}} for k in leaf}
    types.update({'/untouched/tag':{'kind':'text','context':{}},'/untouched/quantity':quantity})
    book.update(memory_schema=core.digest(shape),memory_types=types,memory=memory)
    identity='synthetic.liability.payment';zero=const(money,'0/1')
    negative=lambda node:binary('sub',deepcopy(zero),node)
    pre_types={'cash':money,'liability':money,'outstanding':money,'amount':money,'approved':core.BOOL}
    pre=conditions(identity,pre_types,[
        ('positive',binary('gt',ref('amount'),deepcopy(zero)),['amount'],'invalid'),
        ('cash',binary('ge',ref('cash'),ref('amount')),['cash','amount'],'invalid'),
        ('outstanding',binary('ge',ref('outstanding'),ref('amount')),['outstanding','amount'],'invalid'),
        ('control',binary('eq',binary('add',ref('liability'),ref('outstanding')),deepcopy(zero)),['liability','outstanding'],'invalid'),
        ('applicable',ref('approved'),['approved'],'unsupported')])
    post=conditions(identity,{'liability':money,'outstanding':money},[
        ('control',binary('eq',binary('add',ref('liability'),ref('outstanding')),deepcopy(zero)),['liability','outstanding'],'invalid')])
    amounts={'profile':engine.monetary.PROFILE,'method_id':identity,'version':'1',
             'inputs':{k:decl(money,k,'reported_measurement' if k=='amount' else 'state') for k in ['amount','outstanding','paid']},
             'calculations':[{'id':'outstanding_after','expression':binary('sub',ref('outstanding'),ref('amount')),'requires':['outstanding','amount'],'type':deepcopy(money)},
                             {'id':'paid_after','expression':binary('add',ref('paid'),ref('amount')),'requires':['paid','amount'],'type':deepcopy(money)}],
             'accounts':{k:deepcopy(money) for k in ['cash','liability']},'cash_account':'cash',
             'postings':[{'id':'cash','account':'cash','expression':negative(ref('amount')),'requires':['amount']},
                         {'id':'liability','account':'liability','expression':ref('amount'),'requires':['amount']}],
             'flows':[{'id':'payment','activity':'financing','origin':'principal_payment','expression':negative(ref('amount')),'requires':['amount']}]}
    input_shape=record({'remaining':scalar('rational'),'paid':scalar('rational'),'date':scalar('date'),'event_id':scalar('text')})
    operations=[{'id':'write.'+key,'op':'replace','path':path+[key],
                 'value':{'kind':'read','source':'inputs','pointer':'/'+source}}
                for key,source in [('outstanding','remaining'),('paid','paid'),('last_date','date'),('last_event','event_id')]]
    method={'profile':engine.METHOD,'id':identity,'version':'1','context':deepcopy(context),
            'account_map':{k:ids[k] for k in ['cash','liability']},
            'preconditions':{'manifest':pre,'bindings':{'cash':account('cash'),'liability':account('liability'),
                           'outstanding':mem(prefix+'/outstanding'),'amount':event('amount'),'approved':event('approved')}},
            'postconditions':{'manifest':post,'bindings':{'liability':account('liability'),'outstanding':mem(prefix+'/outstanding')}},
            'monetary':{'definition':amounts,'bindings':{'amount':event('amount'),'outstanding':mem(prefix+'/outstanding'),'paid':mem(prefix+'/paid')}},
            'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],
                       'input_schema':core.digest(input_shape),'operations':operations},
                      'input_bindings':{'remaining':{'kind':'calculation','name':'outstanding_after'},
                                        'paid':{'kind':'calculation','name':'paid_after'},
                                        'date':{'kind':'event','name':'date'},'event_id':{'kind':'event','name':'id'}}},
            'residual_prerequisites':['Constructed payment contract; no inference of source authority or accounting compliance.']}
    request={'profile':engine.PROFILE,'expected_state_sha256':core.digest(book),'expected_method_sha256':core.digest(method),
             'method':method,'event':{'id':'payment.1','date':'2027-01-02','inputs':{
                 'amount':{'type':deepcopy(money),'value':engine.known(amount),'provenance':'Authored payment for exact arithmetic comparison'},
                 'approved':{'type':deepcopy(core.BOOL),'value':engine.known(True),'provenance':'Hypothetical applicability finding, not posting authorization'}}},
             'schemas':{book['memory_schema']:shape,core.digest(input_shape):input_shape}}
    return book,request


def rehash(book,request):
    request['expected_state_sha256']=core.digest(book)
    request['expected_method_sha256']=core.digest(request['method'])


if __name__=='__main__':
    import json
    for owner in ['alpha','beta']:
        book,request=fixture(owner);result=engine.propose(book,request)
        print(json.dumps({'owner':owner,'status':result['status'],'reason':result.get('reason'),'journal':result.get('journal')}))
