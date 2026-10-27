"""Preserve the completed companion once; verify inputs, copies and archive."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
summary = read(HERE / 'preparation-01/stage.json')
stage = Path(summary['stage'])
manifest_path = stage / 'companion-manifest.json'
manifest = read(manifest_path)
assert digest(manifest_path) == summary['manifest_sha256']
assert manifest_path.read_bytes() == (HERE / 'preparation-01/companion-manifest.json').read_bytes()
components = {c['id']: c for c in manifest['components']}
originals = {}
for name, row in manifest['files'].items():
    path = Path(name)
    assert not path.is_absolute() and '..' not in path.parts
    assert digest(stage / name) == row['sha256'], name
    assert (stage / name).stat().st_size == row['bytes'], name
    if path.parts[0] == 'component-notes':
        component = components[path.parts[1]]
        original = ROOT / 'data/accounting-master' / component['unit'] / path.name
    elif name in ('source-manifest.json', 'replay-manifest.json'):
        component = next(c for c in components.values() if c['manifest'] == name)
        original = ROOT / 'data/accounting-master' / component['unit'] / component['preparation'] / 'bundle-manifest.json'
    elif name in ('README.md', 'reproduce.py'):
        original = HERE / name
    else:
        original = ROOT / name
    assert digest(original) == row['sha256'], str(original)
    originals[name] = str(original.relative_to(ROOT))

result = read(stage / 'reproduction-01/result.json')
assert result['passed'] and result['all_inputs_preserved']
assert result['data_version'] == summary['manifest_sha256']
for child in result['components']:
    folder = stage / child['output']
    checks = read(folder / 'checks.json')
    audit = read(folder / 'access-audit.json')
    assert child['exit_code'] == 0 and checks['passed'] and not audit['violations']
    assert digest(folder / 'checks.json') == child['checks_sha256']
    assert digest(folder / 'access-audit.json') == child['audit_sha256']
    assert digest(stage / 'reproduction-01' / (child['id'] + '.log')) == child['log_sha256']
assert sum(c['checks'] for c in result['components']) == 2981

attempt = HERE / 'attempt-01'
archive = HERE / 'internal-evidence-bundle.tar.gz'
assert not attempt.exists() and not archive.exists() and not (HERE / 'preservation.json').exists()
shutil.copytree(stage / 'reproduction-01', attempt)
shutil.copyfile(stage / 'launcher.log', attempt / 'launcher.log')
outputs = {}
for copied in sorted(attempt.rglob('*')):
    if not copied.is_file():
        continue
    relative = copied.relative_to(attempt)
    source = stage / 'launcher.log' if str(relative) == 'launcher.log' else stage / 'reproduction-01' / relative
    assert copied.read_bytes() == source.read_bytes(), str(relative)
    outputs[str(relative)] = dict(sha256=digest(copied), bytes=copied.stat().st_size)

with tarfile.open(archive, 'x:gz') as packed:
    for name in sorted(manifest['files']):
        packed.add(stage / name, arcname=name, recursive=False)
    packed.add(manifest_path, arcname='companion-manifest.json', recursive=False)
with tarfile.open(archive, 'r:gz') as packed:
    members = packed.getmembers()
    expected = set(manifest['files']) | {'companion-manifest.json'}
    assert len(members) == len(expected) and {m.name for m in members} == expected
    for member in members:
        assert member.isfile()
        expected_hash = summary['manifest_sha256'] if member.name == 'companion-manifest.json' else manifest['files'][member.name]['sha256']
        assert sha256(packed.extractfile(member).read()).hexdigest() == expected_hash, member.name
record = dict(
    timestamp_utc=datetime.now(timezone.utc).isoformat(),
    inputs=len(manifest['files']), archive_members=len(members),
    shared_dependency_files=summary['shared_dependency_files'],
    original_and_staged_inputs_verified=True, copied_outputs_verified=True,
    archive_members_verified=True, child_runs_repeated=False,
    manifest_sha256=summary['manifest_sha256'],
    archive=dict(path=archive.name, sha256=digest(archive), bytes=archive.stat().st_size),
    output_directory='attempt-01', outputs=outputs, original_locations=originals,
    command=result['command'], component_checks={c['id']:c['checks'] for c in result['components']},
    checks=sum(c['checks'] for c in result['components']), wall_seconds=result['wall_seconds'],
    environment='Exact installed environment in both component-notes/*/environment-lock.json; no clean installation',
    rights='Internal use; no redistribution rights established', full_release_closure=False)
with (HERE / 'preservation.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({k: record[k] for k in ('inputs','archive_members','checks','archive','child_runs_repeated')}))
