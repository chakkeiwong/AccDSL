"""Independent expected categories; witnesses are checked rather than byte-fixed."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import joint_measurement_constraints_v1 as joint
from test_joint_measurement_constraints_v1 import definition,equation,obs,BUDGET


def comparisons():
    x0=equation('x0',[('x','1/1')]);x1=equation('x1',[('x','1/1')],'1/1')
    cases=[('x0',definition(equations=[x0]),BUDGET,'conditionally_feasible'),
           ('x1',definition(equations=[x1]),BUDGET,'conditionally_feasible'),
           ('joint_conflict',definition(equations=[x0,x1]),BUDGET,'conditionally_infeasible'),
           ('strict_lower',definition({'x':obs(lower=False)},[x0]),BUDGET,'conditionally_infeasible'),
           ('strict_upper',definition({'x':obs(upper=False)},[x1]),BUDGET,'conditionally_infeasible'),
           ('fractional',definition({'x':obs(),'y':obs()},[equation('sum',[('x','1/1'),('y','1/1')],'1/1'),
              equation('ratio',[('x','2/1'),('y','-1/1')])]),BUDGET,'conditionally_feasible'),
           ('zero_budget',definition(),{**BUDGET,'solver_timeout_ms':0},'unknown')]
    missing=definition();missing['observations']['x']['interval_premise']=None
    cases.append(('missing_premise',missing,BUDGET,'unresolved'))
    rows=[]
    for name,spec,budget,expected in cases:
        original=deepcopy(spec);result=joint.assess(spec,budget)
        valid=joint.check_witness(spec,result['witness']) if 'witness' in result else True
        rows.append({'case':name,'definition':spec,'budget':budget,'expected':expected,'result':result,
                     'passed':result['status']==expected and valid and spec==original})
    return rows
