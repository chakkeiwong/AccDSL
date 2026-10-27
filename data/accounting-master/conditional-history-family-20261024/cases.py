"""Finite authored history cases, never retained issuer openings."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_history_family_v1 as history
from test_conditional_history_family_v1 import fixture,domain,witness,BUDGET


def cases():
    base=fixture();fixed=deepcopy(base)
    fixed['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
    fixed['events'][0]['amount']=domain('2/1');fixed['events'][1]['amount']=domain('3/1')
    obligations=deepcopy(base);obligations['obligations']=[{'id':'unadmitted_opening',
        'meaning':'Source opening is not admitted','affects':['target_history_membership','execution']}]
    missing=deepcopy(base);missing['templates']['sale']['premise']=None
    conflict=deepcopy(base);conflict['accounts']={'Cash':domain('10/1'),'Equity':domain('-9/1')}
    strict=deepcopy(base);strict['accounts']={'Cash':domain('10/1','11/1',False,True),'Equity':domain('-10/1')}
    chronology=deepcopy(base);chronology['dates'].reverse()
    definitions=[('symbolic_opening',base,BUDGET,'conditional_family_witness'),
        ('fixed_comparator',fixed,BUDGET,'conditional_family_witness'),
        ('unresolved_target',obligations,BUDGET,'candidate_witness_with_unresolved_obligations'),
        ('missing_premise',missing,BUDGET,'unresolved'),
        ('unbalanced_opening',conflict,BUDGET,'conditionally_infeasible'),
        ('strict_opening_conflict',strict,BUDGET,'conditionally_infeasible'),
        ('reversed_chronology',chronology,BUDGET,'invalid'),
        ('zero_slots',base,{**BUDGET,'max_slots':0},'unknown'),
        ('zero_cells',base,{**BUDGET,'max_cells':0},'unknown')]
    rows=[{'case':name,'request':d,'budget':b,'expected':expected,'result':history.assess(d,b)}
          for name,d,b,expected in definitions]
    alternative=history.assess(base,BUDGET);alternative['witness']=witness(8,3,4)
    alternative['replay']=history.replay_witness(base,BUDGET,alternative['witness'])
    rows.append({'case':'different_valid_history','request':base,'budget':BUDGET,
                 'expected':'conditional_family_witness','result':alternative})
    return rows
