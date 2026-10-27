"""Explicit temporal reference cases, including absent hypotheses and budgets."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import retained_temporal_source_binding_v1 as source
import temporal_measurement_constraints_v1 as temporal
from test_joint_measurement_constraints_v1 import BUDGET
from test_temporal_measurement_constraints_v1 import fixture as constructed


def cases():
    assumed=source.fixture(assume=True)
    missing=deepcopy(assumed);missing['mapping_hypotheses'][source.SUPPORTED[0]]=None
    no_identity=deepcopy(assumed);no_identity['identity_hypotheses'][source.SUPPORTED[0]]=None
    no_rounding=deepcopy(assumed);no_rounding['rounding_hypothesis']=None
    definitions=[('source_display_only',source.fixture(),BUDGET,'unresolved'),
        ('source_explicit',assumed,BUDGET,'conditionally_feasible'),
        ('source_annual',source.fixture([source.SUPPORTED[0]],True),BUDGET,'conditionally_feasible'),
        ('source_interim',source.fixture([source.SUPPORTED[1]],True),BUDGET,'conditionally_feasible'),
        ('source_missing_population',missing,BUDGET,'unresolved'),
        ('source_missing_identity',no_identity,BUDGET,'unresolved'),
        ('source_missing_rounding',no_rounding,BUDGET,'unresolved'),
        ('source_zero_cells',assumed,{**BUDGET,'max_cells':0},'unknown')]
    rows=[{'case':name,'kind':'source','request':request,'budget':budget,'expected':expected,
           'result':source.assess(request,budget)} for name,request,budget,expected in definitions]
    conflict=constructed();conflict['observations']['closing']['interval'].update(lower='8/1',upper='8/1')
    invalid=constructed();invalid['observations']['opening']['type']['time']['at']='2024-01-01'
    for name,d,expected in [('constructed_valid',constructed(),'conditionally_feasible'),
                            ('constructed_conflict',conflict,'conditionally_infeasible'),
                            ('constructed_wrong_time',invalid,'invalid')]:
        rows.append({'case':name,'kind':'constructed','request':d,'budget':BUDGET,'expected':expected,
                     'result':temporal.assess(d,BUDGET)})
    return rows
