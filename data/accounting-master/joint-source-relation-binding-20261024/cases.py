"""Finite source cases; result files retain the complete statement report."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import joint_source_relation_binding_v1 as adapter
BUDGET = {'max_slots':0, 'max_formula_nodes':10000, 'max_integer_assignments':1,
          'max_cells':1, 'elapsed_ms':5000, 'solver_timeout_ms':1000, 'solver_rlimit':1000000}


def cases():
    assumed = adapter.fixture(assume=True)
    no_identity = deepcopy(assumed)
    no_identity['identity_hypotheses'][adapter.SUPPORTED[0]] = None
    no_rounding = deepcopy(assumed); no_rounding['rounding_hypothesis'] = None
    inputs = [
        ('display_only', adapter.fixture(), BUDGET, 'unresolved'),
        ('combined_explicit', assumed, BUDGET, 'conditionally_feasible'),
        ('annual_explicit', adapter.fixture(list(adapter.SUPPORTED[:9]), True), BUDGET, 'conditionally_feasible'),
        ('interim_explicit', adapter.fixture(list(adapter.SUPPORTED[9:]), True), BUDGET, 'conditionally_feasible'),
        ('missing_identity', no_identity, BUDGET, 'unresolved'),
        ('missing_rounding', no_rounding, BUDGET, 'unresolved'),
        ('empty_selection', adapter.fixture([]), BUDGET, 'no_asserted_system'),
        ('zero_cells', assumed, {**BUDGET, 'max_cells':0}, 'unknown')]
    return [{'case':name, 'request':request, 'budget':budget, 'expected':expected,
             'result':adapter.assess(request, budget)} for name,request,budget,expected in inputs]
