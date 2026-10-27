"""Identify, copy and lock the five cited unchanged intragroup profiles."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--preparation', required=True)
args = parser.parse_args()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
units = [dict(id=key, unit='acquisition-intragroup' + suffix + '-20261027', cases=cases, controls=controls)
         for key, suffix, cases, controls in [
             ('downstream', '', 22, 33), ('realisation', '-realisation', 66, 24),
             ('downstream-carry', '-carry', 14, 27), ('upstream', '-upstream', 66, 36),
             ('upstream-carry', '-upstream-carry', 36, 27)]]
files = {}
def add(path, reason, expected=None):
    name = str(path)
    assert not path.is_absolute() and '..' not in path.parts
    actual = digest(ROOT / path)
    if expected is not None:
        assert actual == expected, name
    row = files.setdefault(name, dict(sha256=actual, bytes=(ROOT / path).stat().st_size, reasons=[]))
    assert row['sha256'] == actual, name
    if reason not in row['reasons']:
        row['reasons'].append(reason)

execute = set()
for unit in units:
    folder = Path('data/accounting-master') / unit['unit']
    previous = read(ROOT / folder / 'attempt-01/verification.json')
    assert previous['status'] == 'PASS' and previous['cases'] == unit['cases'] and previous['refusal_controls'] == unit['controls']
    for path, expected in read(ROOT / folder / 'attempt-01/source-lock.json').items():
        add(Path(path), unit['id'] + ': frozen original input', expected)
    for name in ['reference.py', 'fixtures.py', 'predecessor-lock.json', 'contract.md', 'result.md',
                 'attempt-01/cases.json', 'attempt-01/controls.json', 'attempt-01/source-lock.json',
                 'attempt-01/verification.json']:
        add(folder / name, unit['id'] + ': native/expected/provenance input')
    execute.update([str(folder / 'reference.py'), str(folder / 'fixtures.py')])

# Dynamic imports inspected before execution. Archival writer modules in source
# locks remain data-only dependencies and are never imported.
execute.update('data/accounting-master/' + name for name in [
    'acquisition-consideration-20261027/reference.py', 'acquisition-symbolic-20261027/reference.py',
    'control-group-boundary-20261027/scope.py', 'control-history-contract-20261026/history.py',
    'exact-information-time-20261026/projection.py', 'company-portable-authoring-20261023/portable.py',
    'company-path-admission-20261023/admission.py'])
pending = list(execute)
inspected = set()
while pending:
    name = pending.pop()
    if name in inspected:
        continue
    inspected.add(name)
    path = Path(name)
    add(path, 'inspected native or independent fixture import')
    tree = ast.parse((ROOT / path).read_text())
    for node in ast.walk(tree):
        imports = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
        for imported in imports:
            candidate = Path('scripts') / (imported.split('.')[0] + '.py')
            if (ROOT / candidate).is_file():
                pending.append(str(candidate))
    # Confirm any explicit project Python dependency is already part of the
    # inspected dynamic graph or included through the standard import scan.
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if value.startswith(('data/', 'scripts/')) and value.endswith('.py') and (ROOT / value).is_file():
                pending.append(value)

manuscript = Path('docs/design/proposal/manuscript-financing-v554r2p2-20261027')
for name in ['intragroup.tex', 'carry.tex', 'upstream.tex', 'upstream-carry.tex']:
    add(manuscript / 'simulation' / name, 'current manuscript claim and exact arithmetic anchor')
for name in ['replay.py', 'prepare.py', 'README.md', 'execution-audit.md']:
    add(HERE.relative_to(ROOT) / name, 'reproduction driver and declared scope')
add(Path('docs/plans/accounting-intragroup-evidence-replay-20261027.md'), 'reviewed evidence contract')
record = HERE / args.preparation
record.mkdir(exist_ok=False)
stage = Path(tempfile.mkdtemp(prefix='accdsl-intragroup-replay-', dir='/tmp'))
for name, row in files.items():
    target = stage / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
    assert digest(target) == row['sha256'], name
manifest = dict(profile='AccDSLIntragroupEvidenceReplay/1', units=units,
    entries=files, executable_modules=sorted(inspected),
    interpretation='Exact conditional reference profiles; original source/accounting admission remains false',
    normalization='none', rights='internal only; original-source redistribution not established')
for target in [stage / 'intragroup-manifest.json', record / 'bundle-manifest.json']:
    with target.open('x') as stream:
        json.dump(manifest, stream, indent=2); stream.write('\n')
summary = dict(stage=str(stage), inputs=len(files), executable_modules=len(inspected),
    bytes=sum(row['bytes'] for row in files.values()), manifest_sha256=digest(stage / 'intragroup-manifest.json'))
with (record / 'stage.json').open('x') as stream:
    json.dump(summary, stream, indent=2); stream.write('\n')
print(json.dumps(summary))
