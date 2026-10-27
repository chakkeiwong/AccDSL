"""Retained exact native-prerequisite and monetary-family intersections."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import prerequisite_method_family_v1 as joined
from test_prerequisite_method_family_v1 import fixture,redigest
from test_piecewise_method_family_v1 import BUDGET


def cases():
    false=fixture();false['bindings']['all_rights_closed']['binding']={'status':'known','value':False}
    unknown=fixture();unknown['bindings']['all_rights_closed']['binding']={'status':'unknown','reason':'not verified'}
    premise=fixture();premise['bindings']['n']['premise']=None
    partial=fixture();partial['obligations']=[{'id':'native_state','meaning':'Complete native state unavailable','affects':['execution']}]
    unmapped=fixture();unmapped['bindings'].pop('n')
    inactive=fixture(variable=False)
    for req in inactive['requirements']['requirements']:req['guard']['value']=False
    redigest(inactive)
    rows=[]
    for name,d,b,expected in [
        ('fixed_settlement',fixture(variable=False),BUDGET,'conditional_family_witness'),
        ('fixed_sale',fixture('sell',False),BUDGET,'conditional_family_witness'),
        ('quantity_narrowed_two_arms',fixture(),BUDGET,'conditional_family_witness'),
        ('over_quantity_empty_join',fixture(over=True),BUDGET,'conditionally_infeasible'),
        ('false_external_rights',false,BUDGET,'unsupported'),
        ('unknown_external_rights',unknown,BUDGET,'unresolved'),
        ('missing_mapping_premise',premise,BUDGET,'unresolved'),
        ('native_state_obligation',partial,BUDGET,'candidate_with_unresolved_obligations'),
        ('unmapped_input',unmapped,BUDGET,'invalid'),
        ('all_inactive_known_inputs',inactive,BUDGET,'conditional_family_witness'),
        ('one_global_cell',fixture(),{**BUDGET,'max_cells':1},'conditional_family_witness'),
        ('zero_cells',fixture(),{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':joined.assess(d,b)})
    d=fixture();r=joined.assess(d,BUDGET);r['branches'][0]['witness']['nrv']='25/1'
    r['branches'][0]['replay']=joined.replay_witness(d,BUDGET,0,r['branches'][0]['witness'])
    rows.append({'case':'alternate_valid_joined_witness','request':d,'budget':BUDGET,
                 'expected':'conditional_family_witness','result':r})
    return rows
