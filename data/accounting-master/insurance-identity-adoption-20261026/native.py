"""Load the frozen documentary auditor and the isolated identity repair."""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = HERE.parent / 'extended-method-exchanges-20261015/insurance'
ATT = OLD / 'attempt-01'
sys.path.insert(0, str(OLD))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

n = load('insurance_native_auditor', OLD / 'verify_exchanges.py')
idx = load('insurance_pair_index', HERE.parent / 'component-identity-repair-20261026/identity_index.py')
