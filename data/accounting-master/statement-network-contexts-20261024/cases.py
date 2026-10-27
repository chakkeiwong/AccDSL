"""Full supported and explicitly narrower statement-network requests."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import retained_statement_network_v1 as network
from test_joint_measurement_constraints_v1 import BUDGET


def cases():
    full=network.fixture(assume=True);report=network.source.statement.evaluate(full['statement_request'])
    ids=network.numeric_selection(full['statement_request'],report);numeric=network.fixture(ids,True)
    missing=deepcopy(numeric);missing['mapping_hypotheses'][ids[0]]=None
    definitions=[('display_only',network.fixture(),BUDGET,'unresolved'),
        ('full_supported_explicit',full,BUDGET,'unresolved'),
        ('explicit_numeric_subset',numeric,BUDGET,'conditionally_feasible'),
        ('annual_numeric_subset',network.fixture([k for k in ids if k.startswith('annual.')],True),BUDGET,'conditionally_feasible'),
        ('interim_numeric_subset',network.fixture([k for k in ids if k.startswith('interim.')],True),BUDGET,'conditionally_feasible'),
        ('missing_population',missing,BUDGET,'unresolved'),
        ('zero_cells',numeric,{**BUDGET,'max_cells':0},'unknown'),
        ('rejected_omission',network.fixture(['interim.capital'],True),BUDGET,'invalid')]
    return [{'case':name,'request':body,'budget':budget,'expected':expected,
             'result':network.assess(body,budget)} for name,body,budget,expected in definitions]
