from pathlib import Path
from hashlib import sha256
import importlib.util
import io
import json
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
names = ['test_shared_tax_state_v1', 'test_conditional_tax_losses_v1', 'test_shared_book_statements_v1']
suite = unittest.TestSuite(); counts = {}
for name in names:
    path = ROOT / 'tests' / (name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    tests = unittest.defaultTestLoader.loadTestsFromModule(module)
    counts[name] = tests.countTestCases(); suite.addTests(tests)
stream = io.StringIO(); start = time.monotonic()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
files = [ROOT / 'scripts/shared_tax_state_v1.py'] + [ROOT / 'tests' / (n + '.py') for n in names]
observation = {'exit_code': 0 if result.wasSuccessful() else 1, 'test_methods': counts[names[0]],
    'regression_methods': sum(counts[n] for n in names[1:]), 'counts': counts,
    'wall_seconds': time.monotonic() - start,
    'command': 'python3 -B data/accounting-master/shared-tax-state-20261024/check_tests.py',
    'files': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files}}
assert not (HERE / 'manifest.json').exists(), 'evidence already frozen'
(HERE / 'test-output.txt').write_text(stream.getvalue())
(HERE / 'test-observation.json').write_text(json.dumps(observation, indent=2) + '\n')
print(json.dumps(observation))
if not result.wasSuccessful(): print(stream.getvalue())
raise SystemExit(observation['exit_code'])
