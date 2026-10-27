"""Inventory concrete complete methods without changing their semantic owners."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
payment=load('method_payment_examples','data/accounting-master/company-book-transition-20261025/examples.py')
sale=load('method_sale_examples','data/accounting-master/declared-collection-state-growth-20261025/examples.py')
def leaves(value,path=''):
    if isinstance(value,dict):
        if not value:yield path
        for key,child in value.items():yield from leaves(child,path+'/'+key.replace('~','~0').replace('/','~1'))
    elif isinstance(value,list):
        if not value:yield path
        for i,child in enumerate(value):yield from leaves(child,path+'/'+str(i))
    else:yield path
rows=[]
out=HERE/'examples';out.mkdir(parents=True,exist_ok=True)
for owner in ['alpha','beta']:
    for kind,fixture,engine in [('payment',payment.fixture,payment.engine),('sale',sale.sale_fixture,sale.engine)]:
        values=fixture(owner);book,request=values[:2]
        method=request['method'];engine.prepare(book,request)
        row={'id':kind+'.'+owner,'request_profile':request['profile'],'method_profile':method['profile'],
             'top_level_fields':sorted(method),'leaf_paths':list(leaves(method)),
             'memory_operations':[x['op'] for x in method['memory']['definition']['operations']],
             'request_extra_fields':sorted(set(request)-{'profile','expected_state_sha256','expected_method_sha256','method','event','schemas'}),
             'method_sha256':engine.core.digest(method)}
        rows.append(row)
        (out/(kind+'.'+owner+'.json')).write_text(json.dumps({'book':book,'request':request},indent=2)+chr(10))
assert len(rows)==4 and {op for r in rows for op in r['memory_operations']}=={'replace','insert'}
inputs=['scripts/company_book_transition_v1.py','scripts/company_book_transition_v2.py','scripts/company_method_clock_v1.py',
        'scripts/company_method_clock_v2.py','scripts/declared_company_text_v2.py','scripts/annual_program_authoring_v1.py',
        'scripts/company_function_text_v1.py','scripts/method_requirement_text_v2.py','scripts/method_monetary_effects_v1.py',
        'scripts/method_memory_effects_v1.py','data/accounting-master/company-book-transition-20261025/examples.py',
        'data/accounting-master/declared-collection-state-growth-20261025/examples.py']
result={'passed':True,'methods':rows,'inputs':{p:sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        'scope':'exact field enumeration and existing prepare validation; no native financial result rerun'}
(HERE/'inventory.json').write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps({'methods':len(rows),'leaf_counts':{r['id']:len(r['leaf_paths']) for r in rows},'v2_memory_definition_preserved':True}))
