"""Retained source declarations matched against explicit expected records."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_family_text_v1 as authoring
from test_conditional_family_text_v1 import inputs,equivalent_result
from test_typed_affine_history_v1 import stock_fixture
from test_conditional_history_family_v1 import BUDGET
HERE=Path(__file__).resolve().parent


def requests():
    result=[(name,d,b) for name,(d,b) in zip(
        ['joint','temporal','monetary','typed_stock','attachment'],inputs())]
    result.append(('stock_shortage',stock_fixture(True),BUDGET))
    missing=stock_fixture();missing['state_constraints'][0]['domain']['premise']=None
    result.extend([('missing_premise',missing,BUDGET),
                   ('zero_budget',stock_fixture(),{**BUDGET,'max_cells':0})])
    return result


def cases():
    rows=[]
    for name,d,b in requests():
        path=HERE/'examples'/(name+'.accdsl')
        expected=authoring.exchange(d,b)
        source=path.read_bytes();parsed=authoring.lower(source)
        assert parsed==expected,name
        result=authoring.assess_exchange(parsed)
        rows.append({'case':name,'source_path':str(path.relative_to(ROOT)),
            'source_sha256':__import__('hashlib').sha256(source).hexdigest(),
            'expected_exchange':expected,'exchange':parsed,'result':result})
    return rows
