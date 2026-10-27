"""Complete typed-history and temporal-observation intersections."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import typed_history_measurement_attachment_v1 as attachment
from test_typed_history_measurement_attachment_v1 import fixture,monetary_fixture,joined_witness,domain
from test_conditional_history_family_v1 import BUDGET

def cases():
    missing=fixture();missing['bindings']['units_flow']['premise']=None
    partial=fixture();partial['bindings'].pop('units_closing')
    unknown=fixture()
    for e in unknown['history']['events']:e['amount']=domain('0/1','10/1')
    mismatch=fixture();mismatch['bindings']['units_closing']['terms'][0]['coefficient']['type']['scale']='1000/1'
    incompatible=monetary_fixture();incompatible['history']['accounts']={'Cash':domain('10/1'),'Equity':domain('-10/1')}
    incompatible['measurements']['observations']['opening']['interval']=domain('8/1')['interval']
    rows=[]
    for name,d,b,expected in [
        ('cash_and_units',fixture(),BUDGET,'conditional_attachment_witness'),
        ('intermediate_shortage',fixture(True),BUDGET,'conditionally_infeasible'),
        ('shortage_condition_omitted',fixture(True,False),BUDGET,'conditional_attachment_witness'),
        ('unknown_event_sizes',unknown,BUDGET,'conditional_attachment_witness'),
        ('monetary_embedding',monetary_fixture(),BUDGET,'conditional_attachment_witness'),
        ('incompatible_parents',incompatible,BUDGET,'conditionally_infeasible'),
        ('missing_mapping_premise',missing,BUDGET,'unresolved'),
        ('partial_mapping',partial,BUDGET,'candidate_attachment_with_unresolved_obligations'),
        ('wrong_coefficient_scale',mismatch,BUDGET,'invalid'),
        ('zero_budget',fixture(),{**BUDGET,'max_cells':0},'unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected':expected,'result':attachment.assess(d,b)})
    d=monetary_fixture();r=attachment.assess(d,BUDGET)
    r['witness']=joined_witness(8,3,4);r['replay']=attachment.replay_witness(d,BUDGET,r['witness'])
    rows.append({'case':'alternate_valid_witness','request':d,'budget':BUDGET,'expected':'conditional_attachment_witness','result':r})
    return rows
