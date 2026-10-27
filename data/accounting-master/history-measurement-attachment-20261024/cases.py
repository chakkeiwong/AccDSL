"""Complete parent-formula attachment and discriminating conditional examples."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import history_measurement_attachment_v1 as attachment
from test_history_measurement_attachment_v1 import fixture,joined_witness
from test_conditional_history_family_v1 import domain,BUDGET


def cases():
    base=fixture();fixed=deepcopy(base);fixed['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
    conflict=deepcopy(fixed);conflict['measurements']['observations']['opening']['interval']=domain('8/1')['interval']
    missing=deepcopy(base);missing['bindings']['flow']['premise']=None
    partial=deepcopy(base);partial['bindings'].pop('opening')
    obligations=deepcopy(base);obligations['obligations']=[{'id':'authority','meaning':'No admitted accounting map','affects':['history','execution']}]
    invalid=deepcopy(base);invalid['bindings']['flow']['kind']='snapshot'
    rows=[]
    for name,d,b,expected in [
        ('whole_formula_join',base,BUDGET,'conditional_attachment_witness'),
        ('different_parent_witness_needed',fixed,BUDGET,'conditional_attachment_witness'),
        ('separately_feasible_joint_conflict',conflict,BUDGET,'conditionally_infeasible'),
        ('missing_mapping_premise',missing,BUDGET,'unresolved'),
        ('unmapped_observation',partial,BUDGET,'candidate_attachment_with_unresolved_obligations'),
        ('unresolved_authority',obligations,BUDGET,'candidate_attachment_with_unresolved_obligations'),
        ('wrong_flow_role',invalid,BUDGET,'invalid'),
        ('zero_slots',base,{**BUDGET,'max_slots':0},'unknown'),
        ('zero_cells',base,{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':attachment.assess(d,b)})
    alternative=attachment.assess(base,BUDGET);alternative['witness']=joined_witness(8,3,4)
    alternative['replay']=attachment.replay_witness(base,BUDGET,alternative['witness'])
    rows.append({'case':'alternative_joint_history','request':base,'budget':BUDGET,
                 'expected':'conditional_attachment_witness','result':alternative})
    return rows
