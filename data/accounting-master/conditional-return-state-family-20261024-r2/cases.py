"""Retained conditional next-state families and exact native comparators."""
from pathlib import Path
from fractions import Fraction as Q
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_return_state_family_v2 as family
from test_conditional_return_state_family_v2 import fixture,refresh_sources
from test_piecewise_method_family_v1 import BUDGET

def cases():
    low=fixture();s=low['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=family.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
    zero=fixture(variable=False);zero['event'].update(actual_units='0/1',refund_cash='0/1',handling_cash='0/1')
    missing=fixture();missing['premise']=None
    unknown=fixture();unknown['event']['all_rights_closed']='unknown';refresh_sources(unknown)
    false=fixture();false['event']['all_rights_closed']=False;refresh_sources(false)
    partial=fixture();partial['obligations']=[{'id':'actual','meaning':'Actual opening not admitted','affects':['history']}]
    rows=[]
    for name,d,b,expected in [
        ('fixed_settlement',fixture(variable=False),BUDGET,'conditional_state_family_witness'),
        ('fixed_sale',fixture('sell',False),BUDGET,'conditional_state_family_witness'),
        ('uncertain_settlement_two_states',fixture(),BUDGET,'conditional_state_family_witness'),
        ('uncertain_sale',fixture('sell'),BUDGET,'conditional_state_family_witness'),
        ('insufficient_opening_cash',low,BUDGET,'conditionally_infeasible'),
        ('zero_quantity_excluded',zero,BUDGET,'conditionally_infeasible'),
        ('missing_premise',missing,BUDGET,'unresolved'),
        ('unknown_rights',unknown,BUDGET,'unresolved'),
        ('false_rights',false,BUDGET,'unsupported'),
        ('actual_state_obligation',partial,BUDGET,'candidate_state_with_unresolved_obligations'),
        ('one_global_cell',fixture(),{**BUDGET,'max_cells':1},'conditional_state_family_witness'),
        ('zero_budget',fixture(),{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':family.assess(d,b)})
    d=fixture();r=family.assess(d,BUDGET);b=r['branches'][0];b['witness']['nrv']='25/1'
    b['replay']=family.replay_witness(d,BUDGET,0,b['witness'])
    rows.append({'case':'alternate_valid_native_state','request':d,'budget':BUDGET,'expected':'conditional_state_family_witness','result':r})
    return rows
