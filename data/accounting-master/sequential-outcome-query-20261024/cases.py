"""Retain complete query requests and exact outcome evidence."""
from pathlib import Path
from fractions import Fraction as Q
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from test_sequential_outcome_query_v1 import fixture,profit,observation,BUDGET,query
def cases():
    selected=fixture(1,threshold='65/1');selected['family']['observations']=[observation(selected['family'],1,'inventory','65/1')]
    empty=fixture();s=empty['family']['first_family']['state'];cash=Q(s['balances']['cash']);s['balances']['cash']='1/1'
    s['balances']['original_equity']=query.native.monetary.fmt(Q(s['balances']['original_equity'])+cash-1)
    openq=fixture(1,threshold='80/1');openq['family']['first_family']['event_domains']['inventory_nrv']['interval'].update(upper='20/1',upper_inclusive=False)
    obligation=fixture();obligation['family']['obligations']=[{'id':'actual','meaning':'actual continuity unknown','affects':['history']}]
    missing=fixture();missing['family']['premise']=None
    middle_profit=profit(1);middle_profit['threshold']='-4/1'
    rows=[]
    for name,d,b,status,conclusion in [
        ('terminal_inventory',fixture(),BUDGET,'conditional_outcome_query','necessary'),
        ('middle_inventory',fixture(1,threshold='65/1'),BUDGET,'conditional_outcome_query','contingent'),
        ('impossible_middle',fixture(1,threshold='64/1'),BUDGET,'conditional_outcome_query','impossible'),
        ('observed_middle',selected,BUDGET,'conditional_outcome_query','necessary'),
        ('terminal_profit',profit(),BUDGET,'conditional_outcome_query','necessary'),
        ('middle_profit',middle_profit,BUDGET,'conditional_outcome_query','contingent'),
        ('empty_family',empty,BUDGET,'conditional_outcome_query','empty_family'),
        ('strict_endpoint',openq,BUDGET,'conditional_outcome_query','impossible'),
        ('candidate_obligations',obligation,BUDGET,'candidate_outcome_query','necessary'),
        ('missing_premise',missing,BUDGET,'unresolved',None),
        ('one_cell',fixture(),{**BUDGET,'max_cells':1},'conditional_outcome_query','unknown'),
        ('early_counterexample',fixture(1,threshold='65/1'),{**BUDGET,'max_cells':3},'conditional_outcome_query','unknown'),
        ('zero_cells',fixture(),{**BUDGET,'max_cells':0},'conditional_outcome_query','unknown')]:
        rows.append({'case':name,'request':d,'budget':b,'expected_status':status,'expected_conclusion':conclusion,'result':query.assess(d,b)})
    d=fixture();r=query.assess(d,BUDGET);x=next(x for x in r['regions'] if x['status']=='feasible')
    x['witness']['nrv']='25/1';x['replay']=query.replay_witness(d,BUDGET,x['branch'],x['region'],x['witness'])
    rows.append({'case':'alternate_witness','request':d,'budget':BUDGET,'expected_status':'conditional_outcome_query','expected_conclusion':'necessary','result':r})
    return rows
