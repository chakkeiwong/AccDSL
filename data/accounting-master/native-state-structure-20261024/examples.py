"""Concrete retained states and complete fixed-object shape coverage."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests'),str(HERE.parent/'company-return-schema-20261023')]
import native_return_state_structure_v1 as structure
from test_native_return_state_structure_v1 import states,fixed_objects
from retained_fixture import fixture
core=structure.core


def comparisons():
    saved=states();author,raw=fixture();packet=json.loads(raw)
    opening=packet['record_registry'][packet['aliases']['opening']['digest']]['body']
    initial=structure.native.initialize(author,opening['books']['P'],opening['compound']['prior_interest_expensed'])
    saved={'initialized':initial,**saved}
    pending=deepcopy(author);pending['tax']['rate_enacted']='unknown'
    saved['pending_tax_initialized']=structure.native.initialize(pending,opening['books']['P'],opening['compound']['prior_interest_expensed'])
    component=deepcopy(author);component['component']['expected_units']='unknown'
    saved['pending_expected_units_initialized']=structure.native.initialize(component,opening['books']['P'],opening['compound']['prior_interest_expensed'])
    rows=[];shape=structure.schema();key=core.digest(shape)
    for name,value in saved.items():
        encoded=core.canonical(value);h=sha256(encoded).hexdigest();result=structure.inspect(encoded,h,key)
        rows.append({'case':name,'raw_utf8':encoded.decode(),'result':result,
                     'passed':result['status']=='structure_valid' and result['value']==value,
                     'provenance':'canonical derived record from preserved native computation; not original filing'})
    return rows


def coverage():
    expected={}
    def walk(rule,path=()):
        if 'properties' in rule:
            expected[path]=sorted(rule['required'])
            for key,child in rule['properties'].items():walk(child,path+(key,))
        if type(rule.get('additionalProperties')) is dict:walk(rule['additionalProperties'],path+('*',))
        if 'items' in rule:walk(rule['items'],path+('*',))
    walk(structure.schema())
    observed=fixed_objects()
    assert set(expected)==set(observed),(set(expected)-set(observed),set(observed)-set(expected))
    rows=[]
    for path,fields in expected.items():
        name,actual,item,rule=observed[path]
        assert fields==sorted(rule['required'])
        rows.append({'schema_path':'/'+('/'.join(path)),'representative_case':name,
                     'actual_path':list(actual),'required_fields':fields,
                     'adverse_cases':len(fields)+1,'checks':'each required field omitted; one extra field added'})
    return rows
