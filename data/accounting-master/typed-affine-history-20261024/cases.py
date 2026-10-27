"""Authored deterministic typed-state and prefix-constraint examples."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import typed_affine_history_v1 as history
from test_typed_affine_history_v1 import stock_fixture,monetary_embedding
from test_conditional_history_family_v1 import BUDGET,witness,domain


def cases():
    missing=stock_fixture();missing['state_constraints'][0]['domain']['premise']=None
    partial=stock_fixture();partial['obligations']=[{
        'id':'contracts','meaning':'Contract facts unavailable','affects':['target_membership']}]
    mismatch=stock_fixture();mismatch['templates']['sale']['postings']['Cash']['type']['scale']='1000/1'
    opening=stock_fixture();opening['memory']['units']['domain']=domain('-1/1')
    opening['measurements'][1]['domain']=domain('0/1')
    rows=[]
    for name,d,b,expected in [
        ('monetary_embedding',monetary_embedding(),BUDGET,'conditional_family_witness'),
        ('typed_stock_path',stock_fixture(),BUDGET,'conditional_family_witness'),
        ('same_day_sale_before_stock',stock_fixture(True),BUDGET,'conditionally_infeasible'),
        ('constraint_omitted_stays_unchecked',stock_fixture(True,False),BUDGET,'conditional_family_witness'),
        ('opening_constraint_violation',opening,BUDGET,'conditionally_infeasible'),
        ('missing_state_premise',missing,BUDGET,'unresolved'),
        ('missing_contract_facts',partial,BUDGET,'candidate_witness_with_unresolved_obligations'),
        ('scale_mismatch',mismatch,BUDGET,'invalid'),
        ('zero_slots',stock_fixture(),{**BUDGET,'max_slots':0},'unknown'),
        ('zero_cells',stock_fixture(),{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':history.assess(d,b)})
    d=monetary_embedding();r=history.assess(d,BUDGET)
    r['witness']=witness(8,3,4);r['replay']=history.replay_witness(d,BUDGET,r['witness'])
    rows.append({'case':'alternate_valid_typed_history','request':d,'budget':BUDGET,
                 'expected':'conditional_family_witness','result':r})
    return rows
