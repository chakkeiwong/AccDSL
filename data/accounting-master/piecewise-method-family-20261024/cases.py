"""Exact method-family outputs and complete/partial branch coverage examples."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import piecewise_method_family_v1 as family
from test_piecewise_method_family_v1 import fixture,measure,BUDGET
from test_conditional_history_family_v1 import domain


def cases():
    cap=fixture();measure(cap,'calculation','carrying','20/1')
    empty=fixture();measure(empty,'journal','inventory','21/1')
    product=fixture();product['domains']['n']=domain('1/1','3/1');product['domains']['p']=domain('10/1','20/1')
    missing=fixture();missing['domains']['nrv']['premise']=None
    obligation=fixture();obligation['obligations']=[{'id':'native_state','meaning':'Native requirements not checked',
                                                  'affects':['target_method_membership']}]
    limited=fixture();limited['branch_limit']=1
    rows=[]
    for name,d,b,expected in [
        ('known_method_comparator',fixture(False),BUDGET,'conditional_family_witness'),
        ('complete_two_arm_family',fixture(),BUDGET,'conditional_family_witness'),
        ('minimum_tie',cap,BUDGET,'conditional_family_witness'),
        ('all_arms_infeasible',empty,BUDGET,'conditionally_infeasible'),
        ('unknown_product',product,BUDGET,'unsupported'),
        ('missing_premise',missing,BUDGET,'unresolved'),
        ('native_state_unresolved',obligation,BUDGET,'candidate_with_unresolved_obligations'),
        ('one_cell_witness_partial',fixture(),{**BUDGET,'max_cells':1},'conditional_family_witness'),
        ('one_cell_no_witness_unknown',empty,{**BUDGET,'max_cells':1},'unknown'),
        ('zero_cells',fixture(),{**BUDGET,'max_cells':0},'unknown'),
        ('branch_cap',limited,BUDGET,'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':family.assess(d,b)})
    d=fixture();r=family.assess(d,BUDGET)
    r['branches'][0]['witness']['nrv']='22/1'
    r['branches'][0]['replay']=family.replay_witness(d,BUDGET,0,r['branches'][0]['witness'])
    rows.append({'case':'alternate_valid_witness','request':d,'budget':BUDGET,
                 'expected':'conditional_family_witness','result':r})
    return rows
