from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import importlib.util, sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import annual_inventory_family_v1 as m

def load(name,path):
    s=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(s);s.loader.exec_module(module);return module
inventory=load('inventory_family_runtime_examples','data/accounting-master/annual-inventory-composition-20261025/examples.py')
legacy=load('inventory_family_legacy_examples','data/accounting-master/annual-scenario-family-20261025/examples.py')

@lru_cache(maxsize=1)
def fixture():
    first=inventory.residual_carry()
    periods=[{'start':'2027-01-01','end_exclusive':'2028-01-01'}]+[deepcopy(o['event']['next_period']) for o in first['operations'] if o['kind']=='provisional_carry']
    members=[]
    def add(name,operations,statement):
        members.append({'id':name,'assumptions':[{'id':'premise','statement':statement,'provenance':'Explicit synthetic inventory case; no issuer fact'}],'operations':deepcopy(operations)})
    add('residual_carry',first['operations'],'Sell one unit, carry one unit and sell it next period')
    add('refreshed_carry',inventory.refreshed_carry()['operations'],'Sales after assessment require replacement assessment and fresh measurement')
    for name,field,value in [('unknown_units','homogeneous_units',{'status':'unknown','reason':'Not supplied'}),('false_divisibility','divisible_units',m.runtime.partial.known(False))]:
        q=deepcopy(first);q['operations'][0]['event']['findings'][field]=value
        add(name,q['operations'],'Retain an unresolved or rejected finding')
    q=deepcopy(first);q['operations'][0]['event']['sold_units']='3/1';add('oversale',q['operations'],'Quantity exceeds the remaining lot')
    q=deepcopy(first);q['operations'][0]['event']['method']='unimplemented_method';add('unsupported_method',q['operations'],'Unimplemented method is explicit data')
    q=deepcopy(first);q['operations'][4]['event']['sold_units']='2/1';add('later_oversale',q['operations'],'The second-period sale exceeds residual stock')
    same=deepcopy(members[0]);same['id']='同額別案';same['assumptions'][0]['statement']='Separately named identical path';members.append(same)
    return m.request(first['root_request'],periods,members,len(members))

def variant(budget=None,empty=False):
    body=deepcopy(fixture())
    if budget is not None:body['budget']['max_members']=budget
    if empty:body['members']=[]
    return body

def simple():
    operations=[[inventory.sale()], [inventory.sale('full','2/1','30/1')]]
    members=[{'id':name,'assumptions':[],'operations':ops} for name,ops in zip(['partial','full'],operations)]
    return m.request(inventory.root(),[{'start':'2027-01-01','end_exclusive':'2028-01-01'}],members,2)

def legacy_pair():
    old=deepcopy(legacy.fixture());new=deepcopy(old);new['profile']=m.PROFILE
    return old,new

RESULT_METADATA={'profile','optional_inventory_reference','request_sha256','source_bundle_sha256','implementation_sha256'}
def financial_result(result):
    return {k:v for k,v in result.items() if k not in RESULT_METADATA}
