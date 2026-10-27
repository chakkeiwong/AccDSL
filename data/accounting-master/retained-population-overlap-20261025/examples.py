from copy import deepcopy
from pathlib import Path
from fractions import Fraction as Q
import json
import compose

ROOT=Path(__file__).resolve().parents[3]
BUDGET={'max_slots':0,'max_formula_nodes':20000,'max_integer_assignments':1,'max_cells':1,
        'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}
PATH=ROOT/'data/accounting-master/retained-network-history-20261025/exchanges'

def premise(key,text):return {'id':key,'status':'proposed','meaning':text}
def interval(lo,hi=None):return {'lower':f'{lo}/1','upper':f'{lo if hi is None else hi}/1',
    'lower_inclusive':True,'upper_inclusive':True}

def fixture(mode='both',base='opening-unmapped'):
    old=json.loads((PATH/(base+'.json')).read_text())
    request=deepcopy(old['request']['source_request']);source=old['result']['source_result']
    ids={a:k for k,v in source['source_mapping'].items() for a in v['aliases']}
    groups={}
    for name,b,f in [('opening','annual.opening.cash','annual.cash_flow.opening'),
                     ('closing','annual.balance.cash','annual.cash_flow.closing')]:
        if mode not in [name,'both']:continue
        groups[name]={'observations':{'B':ids[b],'F':ids[f]},
            'regions':{k:{'interval':interval(0,40000),
                'bound_premise':premise('region_bound.'+name+'.'+k,
                    'Authored bounded aggregate; not an account or identified member.')}
                for k in ['01','10','11']},
            'valuation_premise':premise('common_valuation.'+name,
                'Assume common nonnegative additive valuation at the exact retained instant; no set membership admission.'),
            'projection_premises':{n:premise('projection.'+name+'.'+n,
                'Conditional population interpretation of retained cash caption '+alias+'; no actual account mapping.')
                for n,alias in [('B',b),('F',f)]}}
    return request,groups

def cases():
    request,groups=fixture();equal=deepcopy(groups)
    for k in ['01','10']:equal['opening']['regions'][k]['interval']=interval(0)
    missing=deepcopy(groups);missing['opening']['projection_premises']['B']=None
    cross=deepcopy(groups);cross['opening']['observations']['F']=groups['closing']['observations']['F']
    full,fg=fixture(base='full-unmapped')
    return {'both_instants':(request,groups,BUDGET,'conditionally_feasible'),
        'opening_only':(*fixture('opening'),BUDGET,'conditionally_feasible'),
        'closing_only':(*fixture('closing'),BUDGET,'conditionally_feasible'),
        'false_opening_equality':(request,equal,BUDGET,'conditionally_infeasible'),
        'missing_projection':(request,missing,BUDGET,'unresolved'),
        'cross_date':(request,cross,BUDGET,'invalid'),
        'full_source_dash':(full,fg,BUDGET,'unresolved'),
        'zero_budget':(request,groups,{**BUDGET,'max_cells':0},'unknown')}

def alternative_witness(result,extra):
    witness=deepcopy(result['assessment']['joint_assessment']['witness'])
    for row in result['groups'].values():
        b,f=(Q(witness[row['source_ids'][k]]) for k in ['B','F'])
        b_only=max(Q(0),b-f)+extra
        values={'region:10':b_only,'region:01':f-b+b_only,'region:11':b-b_only}
        for k,v in values.items():witness[row['rename'][k]]=f'{v.numerator}/{v.denominator}'
    return witness
