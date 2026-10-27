"""Fixed local caller context, independent of all packet contents."""
from pathlib import Path
import importlib.util
import sys
from assemble import FILES
from portable import decode

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context():
    for name in ['company-family-20261023', 'company-expressions-20261023', 'company-recovery-20261023']:
        sys.path.insert(0, str(HERE.parent / name))
    recovery_checks = load('portable_recovery_fixtures', HERE.parent/'company-recovery-20261023/verify.py')
    _, source, engine, _, method = recovery_checks.context()
    import family
    import recovery
    import adapter
    policy = load('portable_local_policy', HERE.parent/'company-policy-20261023/policy.py')
    raw = {role: (HERE.parent/path).read_bytes() for role, (path, _) in FILES.items()}
    return raw, source, {'family': family, 'engine': engine, 'method': method,
        'recovery': recovery, 'materialize': adapter.materialize, 'generate': policy.generate}
