"""Complete retained native sale domain through declared company effects."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import company_method_clock_v1 as binder
import native_return_state_structure_v1 as structure

engine=binder.transition
core=engine.core
native=structure.native
PROFILE='NativeCompanySale/1'
PINS={'company_method_clock_v1.py':'39d9499cf9a36fa14eb3ec0d4d68f23e7a47c137e0494a4d83c2101e317b2f8d',
      'native_return_state_structure_v1.py':'9dacde63db6f39472154c518f14d48f06d4ccb37771d0d019a4c13bafe0da685'}
digest=core.digest
FLAGS=engine.FLAGS


def protected():
    folder=Path(__file__).resolve().parent
    for name,h in PINS.items():core.need(sha256((folder/name).read_bytes()).hexdigest()==h,'dependency_hash:'+name)
    for name,h in structure.PINNED.items():core.need(sha256((structure.ROOT/name).read_bytes()).hexdigest()==h,'native_dependency_hash:'+name)
    binder.protected()


def record(fields):return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}
def scalar(kind):return {'type':'boolean'} if kind=='boolean' else {'type':'string','minLength':1,'maxLength':4096,'x-exact-kind':kind}
def ref(key):return {'op':'ref','id':key}
def binary(op,left,right):return {'op':op,'left':left,'right':right}
def constant(typ,value):return {'op':'const','type':deepcopy(typ),'value':value}
def declared(typ,name,role='state'):return {'type':deepcopy(typ),'role':role,'source_ref':'explicit-native-projection:'+name}
def pointer(parts):return ''.join('/'+k.replace('~','~0').replace('/','~1') for k in parts)


def validate_native(state,event):
    protected();engine.memory.bounded(state);engine.memory.bounded(event)
    structure.validate(state,structure.schema());native.invariant(state)
    core.closed(event,['id','kind','method','date','source_pointer','lot_id','fraction','proceeds','performance_complete'],'native_sale_event')
    native.need(event['kind']=='sell','selected_sale_kind','unsupported')
    core.text(event['id'],'event_id');native.need(event['id'] not in state['seen'],'duplicate event')
    day=core.scalar(event['date'],'date')
    native.need(core.scalar(state['period']['start'],'date')<=day<core.scalar(state['period']['end_exclusive'],'date'),'event outside period')
    native.need(day>=core.scalar(state['date'],'date') and day>=core.scalar(state['tax_closed_until'],'date'),'event precedes close or state')
    native.need(event['method']=='inventory.sell','sale method')
    native.yes(event['performance_complete'],'sale performance')
    native.need(native.q(event['fraction'])==1,'whole lot method only','unsupported')
    native.need(event['lot_id'] in state['lots'],'unknown lot')
    native.need(not state['lots'][event['lot_id']]['disposed'],'lot already disposed')
    native.need(native.q(event['proceeds'])>=0,'negative sale proceeds')


def import_book(state):
    context={'entity':state['context']['entity'],'book':state['context']['book_role'],
             'currency':state['context']['currency'],'case_id':state['context']['case_id'],'mode':'synthetic'}
    classes={**{k:'asset' for k in native.ASSETS},**{k:'liability' for k in native.LIABILITIES},
             **{k:'equity' for k in native.EQUITY},**{k:'income' if k=='revenue' else 'expense' for k in native.INCOME}}
    book={'profile':engine.BOOK,'context':context,'period':deepcopy(state['period']),'date':state['date'],
          'accounts':{k:{'classification':classes[k]} for k in state['balances']},'balances':deepcopy(state['balances']),
          'cash_account':'cash','seen':deepcopy(state['seen'])}
    money=engine.money_type(book);units={**deepcopy(money),'dimensions':{'goods:unit':1}}
    types={'id':{'kind':'text','context':{}},'component_id':{'kind':'text','context':{}},'units':units,
           'carrying':money,'tax_base':money,'acquired':{'kind':'date','context':{}},'disposed':core.BOOL}
    lot_shape=record({k:scalar(t['kind']) for k,t in types.items()})
    shape=record({'lots':record({key:deepcopy(lot_shape) for key in state['lots']}),
                  'other_inventory':scalar('rational'),'tax_closed_until':scalar('date')})
    book.update(memory_schema=digest(shape),memory={'lots':deepcopy(state['lots']),
                'other_inventory':state['other_inventory'],'tax_closed_until':state['tax_closed_until']},
                memory_types={**{pointer(['lots',key,k]):deepcopy(t) for key in state['lots'] for k,t in types.items()},
                              '/other_inventory':money,'/tax_closed_until':{'kind':'date','context':{}}})
    book['flows']=[{**deepcopy(row),'id':digest(['native-prefix',i,row]),'book':context['book'],'currency':context['currency']}
                   for i,row in enumerate(state['flows'])]
    return book,shape


def requirement(method_id,types,rows):
    return {'profile':engine.requirements.PROFILE,'method_id':method_id,'version':'1',
            'inputs':{k:declared(t,k) for k,t in types.items()},
            'requirements':[{'id':name,'guard':constant(core.BOOL,True),'guard_requires':[],
                             'predicate':predicate,'requires':deps,'admission_refs':[],
                             'on_false':status,'on_unknown':'unresolved'} for name,predicate,deps,status in rows],
            'required_known':[],'capabilities':[],
            'residual_prerequisites':['Retained native domain checked separately; no source or posting admission.']}


def method_for(book,event,shape):
    identity='native.complete_lot_sale';money=engine.money_type(book);day={'kind':'date','context':{}}
    zero=constant(money,'0/1');negative=lambda x:binary('sub',deepcopy(zero),x)
    stock_types={'inventory':money,'other':money};stock_bindings={'inventory':{'kind':'account','role':'inventory'},
                                                               'other':{'kind':'memory','pointer':'/other_inventory'}}
    total=ref('other');dependencies=['inventory','other']
    for index,key in enumerate(book['memory']['lots']):
        name='lot.'+str(index);stock_types[name]=money;stock_bindings[name]={'kind':'memory','pointer':pointer(['lots',key,'carrying'])}
        total=binary('add',total,ref(name));dependencies.append(name)
    stock=('inventory_allocation',binary('eq',ref('inventory'),total),dependencies,'invalid')
    types={**stock_types,'proceeds':money,'disposed':core.BOOL,'complete':core.BOOL,'closed_until':day,'actual_date':day}
    pre=requirement(identity,types,[stock,
        ('proceeds',binary('le',deepcopy(zero),ref('proceeds')),['proceeds'],'invalid'),
        ('live',{'op':'not','arg':ref('disposed')},['disposed'],'invalid'),
        ('performance',ref('complete'),['complete'],'unsupported'),
        ('clock',binary('le',ref('closed_until'),ref('actual_date')),['closed_until','actual_date'],'invalid')])
    post=requirement(identity,stock_types,[deepcopy(stock)])
    bindings={**stock_bindings,'proceeds':{'kind':'event','name':'proceeds'},'complete':{'kind':'event','name':'complete'},
              'disposed':{'kind':'memory','pointer':pointer(['lots',event['lot_id'],'disposed'])},
              'closed_until':{'kind':'memory','pointer':'/tax_closed_until'},'actual_date':{'kind':'event','name':'actual_date'}}
    postings=[('cash',ref('proceeds'),'proceeds'),('revenue',negative(ref('proceeds')),'proceeds'),
              ('inventory',negative(ref('cost')),'cost'),('cogs',ref('cost'),'cost')]
    amounts={'profile':engine.monetary.PROFILE,'method_id':identity,'version':'1',
             'inputs':{'cost':declared(money,'cost'),'proceeds':declared(money,'proceeds','reported_measurement')},
             'calculations':[],'accounts':{k:deepcopy(money) for k in ['cash','inventory','revenue','cogs']},'cash_account':'cash',
             'postings':[{'id':k,'account':k,'expression':x,'requires':[dep]} for k,x,dep in postings],
             'flows':[{'id':'sale','activity':'operating','origin':'external_sale','expression':ref('proceeds'),'requires':['proceeds']}]}
    empty=record({});empty_hash=digest(empty)
    operations=[{'id':key,'op':'replace','path':['lots',event['lot_id'],key],
                 'value':{'kind':'literal','value':True if key=='disposed' else '0/1'}} for key in ['units','carrying','tax_base','disposed']]
    method={'profile':engine.METHOD,'id':identity,'version':'1','context':deepcopy(book['context']),
            'account_map':{k:k for k in amounts['accounts']},'preconditions':{'manifest':pre,'bindings':bindings},
            'postconditions':{'manifest':post,'bindings':stock_bindings},
            'monetary':{'definition':amounts,'bindings':{'proceeds':bindings['proceeds'],
                        'cost':{'kind':'memory','pointer':pointer(['lots',event['lot_id'],'carrying'])}}},
            'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],
                                   'input_schema':empty_hash,'operations':operations},'input_bindings':{}},
            'residual_prerequisites':['Native whole-lot import/export validated; no source/accounting admission.']}
    entry={'method_sha256':digest(method),'method':method,'schemas':{book['memory_schema']:shape,empty_hash:empty},
           'account_classes':{k:book['accounts'][k]['classification'] for k in method['account_map']},
           'event_inputs':{'proceeds':money,'complete':deepcopy(core.BOOL)},'metadata_bindings':{'actual_date':'date'},
           'clock':{'kind':'direct_event_date'}}
    registry={'profile':binder.REGISTRY,'context':deepcopy(book['context']),'entries':{'sell':entry}}
    call={'profile':binder.PROFILE,'expected_state_sha256':digest(book),'expected_registry_sha256':digest(registry),
          'registry':registry,'method_key':'sell','event':{'id':event['id'],'date':event['date'],'inputs':{
              'proceeds':{'type':deepcopy(money),'value':engine.known(event['proceeds']),'provenance':'Retained native sale event:proceeds'},
              'complete':{'type':deepcopy(core.BOOL),'value':engine.known(event['performance_complete']),'provenance':'Retained native sale event:performance_complete'}}}}
    return call


def export_book(before,after):
    result=deepcopy(before)
    for key in ['balances','date','seen']:result[key]=deepcopy(after[key])
    result['lots']=deepcopy(after['memory']['lots'])
    result['flows']=[{k:v for k,v in row.items() if k not in ['id','book','currency']} for row in after['flows']]
    structure.validate(result,structure.schema());native.invariant(result)
    return result


def request(state,event):
    return {'profile':PROFILE,'expected_state_sha256':digest(state),'expected_event_sha256':digest(event),'event':deepcopy(event)}


def failure(exc):
    status=exc.status if isinstance(exc,native.Rejected) else 'invalid'
    return {'profile':PROFILE,**FLAGS,'status':status,'reason':str(exc)[:300] or type(exc).__name__}


def propose(state,body):
    try:
        engine.memory.bounded(body);engine.closed(body,['profile','expected_state_sha256','expected_event_sha256','event'])
        core.need(body['profile']==PROFILE,'request_profile');core.need(body['expected_state_sha256']==digest(state),'stale_state')
        event=body['event'];core.need(body['expected_event_sha256']==digest(event),'event_digest')
        validate_native(state,event);book,shape=import_book(state);call=method_for(book,event,shape)
        result=binder.propose(book,call)
        output={'profile':PROFILE,**FLAGS,'status':result['status'],'before_sha256':digest(state),'request_sha256':digest(body),
                'imported_book':book,'method_call':call,'generic_result':result,
                'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_sha256':deepcopy(PINS)}
        if result['status']!='proposed':return output
        proposed=result['transition'];after=export_book(state,proposed['after'])
        flows=after['flows'][len(state['flows']):]
        return {**output,'after':after,'after_sha256':digest(after),'journal':proposed['journal'],'flows':flows}
    except Exception as exc:return failure(exc)


def apply(state,body,proposal):
    try:
        engine.memory.bounded(proposal);expected=propose(state,body)
        core.need(core.canonical(expected)==core.canonical(proposal),'proposal_recomputation_mismatch')
        if expected['status']!='proposed':return expected
        return {**deepcopy(expected),'status':'applied_provisional'}
    except Exception as exc:return failure(exc)
