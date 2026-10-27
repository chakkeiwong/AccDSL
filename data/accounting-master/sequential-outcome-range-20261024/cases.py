"""Full typed range requests and complete original endpoint evidence."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from test_sequential_outcome_range_v1 import ranges,fixture,profit,empty,variable_proceeds,observation,BUDGET
def cases():
    openq=fixture(1);openq['family']['first_family']['event_domains']['inventory_nrv']['interval'].update(upper='20/1',upper_inclusive=False,lower_inclusive=False)
    selected=fixture(1);selected['family']['observations']=[observation(selected['family'],1,'inventory','65/1')]
    obligation=fixture();obligation['family']['obligations']=[{'id':'actual','meaning':'actual source unknown','affects':['history']}]
    missing=fixture();missing['family']['premise']=None
    rows=[]
    for name,d,b,status,answer,expected in [
      ('middle_inventory',fixture(1),BUDGET,'conditional_outcome_range','finite_envelope',['65/1','80/1',True,True]),
      ('terminal_inventory',fixture(),BUDGET,'conditional_outcome_range','finite_envelope',['60/1','60/1',True,True]),
      ('middle_profit',profit(1),BUDGET,'conditional_outcome_range','finite_envelope',['-19/1','-4/1',True,True]),
      ('terminal_profit',profit(),BUDGET,'conditional_outcome_range','finite_envelope',['16/1','16/1',True,True]),
      ('open_middle',openq,BUDGET,'conditional_outcome_range','finite_envelope',['65/1','80/1',False,False]),
      ('selected_middle',selected,BUDGET,'conditional_outcome_range','finite_envelope',['65/1','65/1',True,True]),
      ('variable_proceeds',variable_proceeds(),BUDGET,'conditional_outcome_range','finite_envelope',['-24/1','76/1',True,True]),
      ('unfunded',empty(),BUDGET,'conditional_outcome_range','empty_family',None),
      ('first_branch_only',fixture(1),{**BUDGET,'max_cells':1},'conditional_outcome_range','unknown',None),
      ('zero_cells',fixture(),{**BUDGET,'max_cells':0},'conditional_outcome_range','unknown',None),
      ('candidate_obligations',obligation,BUDGET,'candidate_outcome_range','finite_envelope',['60/1','60/1',True,True]),
      ('missing_premise',missing,BUDGET,'unresolved',None,None)]:
        rows.append({'case':name,'request':d,'budget':b,'expected_status':status,'expected_conclusion':answer,'expected_bounds':expected,'result':ranges.assess(d,b)})
    d=fixture();r=ranges.assess(d,BUDGET);e=r['branches'][0]['bounds']['lower'];e['witness']['nrv']='25/1'
    e['replay']=ranges.replay_value(d,BUDGET,0,e['witness'])
    rows.append({'case':'alternative_endpoint','request':d,'budget':BUDGET,'expected_status':'conditional_outcome_range','expected_conclusion':'finite_envelope','expected_bounds':['60/1','60/1',True,True],'result':r})
    return rows
