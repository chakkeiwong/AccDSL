"""Copy the declared bank dependencies without executing any frozen writer."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('data/accounting-master')
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument('--preparation', required=True)
args = parser.parse_args()
files = {}

def add(path, reason, expected=None):
    path = Path(path)
    assert not path.is_absolute() and '..' not in path.parts, str(path)
    source = ROOT / path
    actual = digest(source)
    if expected is not None:
        assert actual == expected, str(path)
    row = files.setdefault(str(path), dict(sha256=actual, bytes=source.stat().st_size, reasons=[]))
    assert row['sha256'] == actual
    if reason not in row['reasons']:
        row['reasons'].append(reason)

units = []
for key, profile, attempt in [('bank', 'BankComponents/1', 'attempt-03'),
                              ('bank-v2', 'BankComponents/2', 'attempt-02'),
                              ('bank-assessment', 'BankAssessment/1', 'attempt-03')]:
    folder = BASE / 'extended-method-exchanges-20261015' / key
    packet_path = folder / attempt / 'portable-exchanges.json'
    packet = read(ROOT / packet_path)
    units.append(dict(id=key, profile=profile, folder=str(folder), attempt=attempt,
                      exchanges=len(packet['exchanges']), records=len(packet['record_registry'])))
    add(packet_path, key + ': retained complete request/response/world expectations')
    add(folder / attempt / 'record-schemas.json', key + ': frozen schema')
    for h, row in packet['blobs'].items():
        add(row['path'], key + ': declared blob', h)
    for name, row in packet['input_snapshots'].items():
        add(row['path'], key + ': frozen input', row['sha256'])
        add(folder / attempt / 'inputs' / name, key + ': frozen input snapshot', row['sha256'])
    for name in ['result.md', 'run-manifest.json', 'predecessor-lock.json',
                 'verify_exchanges.py', 'financial_checks.py', 'source_policy.py', 'semantic-contract.md']:
        add(folder / name, key + ': provenance or executable dependency')
    for pattern in ['validation-*.json', 'verification-*.json']:
        for p in sorted((ROOT / folder / attempt).glob(pattern)):
            add(p.relative_to(ROOT), key + ': original validation result')

exact = BASE / 'exact-bank-profile-adoption-20261026'
for name in ['successor.py', 'adapted_methods.py', 'record-schemas.json', 'semantic-contract.md',
             'result.md', 'run-manifest.json', 'checks.json', 'source-lock.json',
             'ordinary-comparisons.json', 'timing-comparisons.json', 'controls.json']:
    add(exact / name, 'exact time: implementation and preserved evidence')
for p in sorted((ROOT / exact / 'examples').glob('*.json')):
    add(p.relative_to(ROOT), 'exact time: retained full exchange')
    packet = read(p)
    add(packet['base_packet'], 'exact time: unchanged predecessor packet', packet['base_packet_sha256'])
    for h, row in packet['blobs'].items():
        add(row['path'], 'exact time: declared blob', h)

execute = [BASE / 'exact-native-timing-20261026/checker.py',
           BASE / 'exact-information-time-20261026/projection.py',
           exact / 'successor.py', exact / 'adapted_methods.py']
for unit in units:
    execute += [Path(unit['folder']) / name for name in ['verify_exchanges.py', 'financial_checks.py', 'source_policy.py']]
# The exact wrapper imports the frozen assessment verifier and its local modules.
execute += [BASE / 'extended-method-exchanges-20261015/bank-assessment/attempt-03/inputs' / name
            for name in ['verify_exchanges.py', 'financial_checks.py', 'source_policy.py']]
inspected = set()
while execute:
    p = execute.pop()
    if str(p) in inspected:
        continue
    inspected.add(str(p))
    add(p, 'declared executable import')
    tree = ast.parse((ROOT / p).read_text())
    for node in ast.walk(tree):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
        for name in names:
            candidate = Path('scripts') / (name.split('.')[0] + '.py')
            if (ROOT / candidate).is_file():
                execute.append(candidate)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if value.startswith(('data/', 'scripts/')) and value.endswith('.py') and (ROOT / value).is_file():
                execute.append(Path(value))
for name in ['README.md', 'prepare.py', 'replay.py', 'execution-audit.md', 'compatibility-map.md']:
    add(HERE.relative_to(ROOT) / name, 'current reproduction contract')
add(Path('docs/plans/accounting-bank-consolidation-20261027.md'), 'reviewed plan')
record = HERE / args.preparation
record.mkdir(exist_ok=False)
stage = Path(tempfile.mkdtemp(prefix='accdsl-bank-replay-', dir='/tmp'))
for name, row in files.items():
    target = stage / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
    assert digest(target) == row['sha256'], name
manifest = dict(profile='AccDSLBankInterfaceReplay/1', units=units, entries=files,
                exact_folder=str(exact), executable_modules=sorted(inspected),
                historical_git_preservation='not rerun; retained historical result only',
                accounting_profiles_merged=False, full_release_closure=False, rights='internal only')
for p in [record / 'bundle-manifest.json', stage / 'bank-manifest.json']:
    with p.open('x') as f:
        json.dump(manifest, f, indent=2); f.write(chr(10))
summary = dict(stage=str(stage), inputs=len(files), bytes=sum(r['bytes'] for r in files.values()),
               manifest_sha256=digest(stage / 'bank-manifest.json'))
with (record / 'stage.json').open('x') as f:
    json.dump(summary, f, indent=2); f.write(chr(10))
print(json.dumps(summary))
