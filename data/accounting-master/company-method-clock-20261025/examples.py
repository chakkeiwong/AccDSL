from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import company_method_clock_v1 as binder
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
book_examples=load('clock_book_examples','data/accounting-master/company-book-transition-20261025/examples.py')
native_examples=load('clock_native_examples','data/accounting-master/company-book-transition-20261025/native_comparisons.py')


def bind_request(book,request,metadata=None,key='pay'):
    metadata={} if metadata is None else metadata
    method=deepcopy(request['method']);types=binder.event_declarations(method)
    entry={'method_sha256':binder.digest(method),'method':method,'schemas':deepcopy(request['schemas']),
           'account_classes':{role:book['accounts'][account]['classification'] for role,account in method['account_map'].items()},
           'event_inputs':{k:deepcopy(t) for k,t in types.items() if k not in metadata},
           'metadata_bindings':deepcopy(metadata),'clock':{'kind':'direct_event_date'}}
    registry={'profile':binder.REGISTRY,'context':deepcopy(book['context']),'entries':{key:entry}}
    event=deepcopy(request['event']);event['inputs']={k:v for k,v in event['inputs'].items() if k not in metadata}
    return {'profile':binder.PROFILE,'expected_state_sha256':binder.digest(book),
            'expected_registry_sha256':binder.digest(registry),'registry':registry,'method_key':key,'event':event}


def payment(owner='alpha'):
    book,request=book_examples.fixture(owner)
    return book,bind_request(book,request),request


def sale():
    name,state,event=next(x for x in native_examples.prior.selected_cases() if x[2]['kind']=='sell')
    book,request=native_examples.sale_projection(state,event)
    # Metadata provenance is authored explicitly in the independent comparator.
    request['event']['inputs']['event_date']['provenance']='Bound from actual event metadata:date'
    return book,bind_request(book,request,{'event_date':'date'},'sell'),request


def rehash(book,call):
    for entry in call['registry']['entries'].values():entry['method_sha256']=binder.digest(entry['method'])
    call['expected_state_sha256']=binder.digest(book)
    call['expected_registry_sha256']=binder.digest(call['registry'])


if __name__=='__main__':
    import json
    for name,make in [('payment',payment),('sale',sale)]:
        book,call,expected=make();result=binder.propose(book,call)
        print(json.dumps({'case':name,'status':result['status'],'reason':result.get('reason'),
                          'request_equal':result.get('materialized_request')==expected,
                          'apply_status':binder.apply(book,call,result)['status']}))
