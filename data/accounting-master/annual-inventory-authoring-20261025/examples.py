from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import importlib.util, sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_inventory_authoring_v1 as m

def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(s);s.loader.exec_module(module);return module
inventory=load('inventory_authoring_runtime_examples','data/accounting-master/annual-inventory-composition-20261025/examples.py')
old=load('inventory_authoring_old_examples','data/accounting-master/annual-program-authoring-20261025/examples.py')

@lru_cache(maxsize=1)
def fixtures():
    rows=[]
    def add(name,request,status='complete_provisional',stop=None,legacy=None):
        program=m.from_request(request,'inventory_book')
        rows.append({'case':name,'request':request,'program':program,'source':m.render(program),
                     'imports':{request['root_sha256']:deepcopy(request['root_request'])},
                     'expected_status':status,'expected_stop':stop,'legacy':legacy})
    for row in inventory.cases():
        if row['case']=='wrong_profile':continue
        add('inventory_'+row['case'],row['request'],row['expected_status'],row['expected_stop'])
    q=m.runtime.request(inventory.root(),[inventory.sale('first'),inventory.sale('second')])
    add('split_sale',q)
    q=m.runtime.request(inventory.root(),[inventory.sale('售出一件')])
    q['operations'][0]['event']['findings']['homogeneous_units']['provenance']='明确假设; unicode preserved'
    add('unicode_identity_provenance',q)
    for row in old.fixtures():
        request=deepcopy(row['request']);request['profile']=m.runtime.PROFILE
        add('legacy_'+row['case'],request,row['expected_status'],row['expected_stop'],row)
    return rows
