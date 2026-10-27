"""Verify current scoped evidence and both protected release packages."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_company_state_program import validate

errors, inspected = [], 0
def bound(path, expected):
    global inspected
    p = ROOT / path; inspected += 1
    if not p.is_file() or sha256(p.read_bytes()).hexdigest() != expected:
        errors.append(path)

packages = []
for name in ['manuscript-reference-v555r1-20261027', 'manuscript-state-v556d1-20261028']:
    folder = ROOT / 'docs/design/proposal' / name
    manifest = json.loads((folder / 'package-manifest.json').read_text())
    before = len(errors)
    for row in manifest['files']:
        bound(str((folder / row['path']).relative_to(ROOT)), row['sha256'])
    packages.append(dict(package=name, files=len(manifest['files']), mismatches=len(errors) - before))
for relative in [
    'data/accounting-master/company-state-owner-semantics-20261028/attempt-01/run-manifest.json',
    'data/accounting-master/company-state-common-request-20261028/attempt-01/run-manifest.json',
    'data/accounting-master/construction-continuation-20261028/t01-definition-source-lock.json']:
    manifest = json.loads((ROOT / relative).read_text())
    for path, expected in manifest['source_hashes'].items():
        bound(path, expected)
manifest = json.loads((ROOT / 'data/accounting-master/company-state-rea-commitment-reading-20261028/manifest.json').read_text())
for row in manifest['files']:
    bound(row['path'], row['sha256'])
program = validate(ROOT, ROOT / 'data/accounting-master/unified-program-20261028')
checks = json.loads((ROOT / 'data/accounting-master/company-state-common-request-20261028/attempt-01/verification.json').read_text())
result = dict(passed=not errors and program['valid'] and checks['status'] == 'pass',
              program=program, protected=packages, checked_hashes=inspected, mismatches=errors, caller=checks)
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
target = parser.parse_args().output
with target.open('x') as stream:
    json.dump(result, stream, indent=2); stream.write('\n')
print(json.dumps(dict(passed=result['passed'], hashes=inspected, mismatches=errors,
                     caller_checks=checks['checks'], protected=packages, program_valid=program['valid'])))
raise SystemExit(not result['passed'])
