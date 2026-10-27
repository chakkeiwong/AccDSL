"""Retained complete settlement-sale families, not selected middle witnesses."""
from pathlib import Path
from fractions import Fraction as Q
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import sequential_return_state_family_v1 as family
from test_sequential_return_state_family_v1 import fixture,observation
from test_piecewise_method_family_v1 import BUDGET

def cases():
    selected=fixture();selected['observations']=[observation(selected,1,'inventory','65/1')]
    terminal=fixture();terminal['observations']=[observation(terminal,2,'inventory','60/1')]
    low=fixture();s=low['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=family.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
    unknown=fixture();unknown['sale_event']['performance_complete']='unknown'
    false=fixture();false['sale_event']['performance_complete']=False
    missing=fixture();missing['premise']=None
    partial=fixture();partial['obligations']=[{'id':'actual','meaning':'No actual continuity admission','affects':['history']}]
    later=fixture();later['sale_event']['date']='2025-03-01'
    wrong=fixture();wrong['sale_event']['lot_id']='wrong'
    rows=[]
    for name,d,b,expected in [
        ('both_middle_paths',fixture(),BUDGET,'conditional_sequence_family_witness'),
        ('intermediate_observation',selected,BUDGET,'conditional_sequence_family_witness'),
        ('terminal_observation_retains_paths',terminal,BUDGET,'conditional_sequence_family_witness'),
        ('unknown_sale_proceeds',fixture(True),BUDGET,'conditional_sequence_family_witness'),
        ('later_sale_context',later,BUDGET,'conditional_sequence_family_witness'),
        ('unfunded_middle',low,BUDGET,'conditionally_infeasible'),
        ('unknown_performance',unknown,BUDGET,'unresolved'),
        ('false_performance',false,BUDGET,'unsupported'),
        ('missing_continuity_premise',missing,BUDGET,'unresolved'),
        ('actual_continuity_obligation',partial,BUDGET,'candidate_sequence_with_unresolved_obligations'),
        ('wrong_lot',wrong,BUDGET,'invalid'),
        ('unvisited_valid_second_arm',selected,{**BUDGET,'max_cells':1},'unknown'),
        ('zero_budget',fixture(),{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':family.assess(d,b)})
    d=fixture();r=family.assess(d,BUDGET);b=r['branches'][0];b['witness']['nrv']='25/1'
    b['replay']=family.replay_witness(d,BUDGET,0,b['witness'])
    rows.append({'case':'alternate_complete_trajectory','request':d,'budget':BUDGET,'expected':'conditional_sequence_family_witness','result':r})
    return rows
