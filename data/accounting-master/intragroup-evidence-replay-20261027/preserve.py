"""Preserve the accepted copied replay and validate its complete archive."""
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
stage_info = read(HERE / 'preparation-03/stage.json')
stage = Path(stage_info['stage'])
manifest = read(stage / 'intragroup-manifest.json')
assert digest(stage / 'intragroup-manifest.json') == stage_info['manifest_sha256']
assert (stage / 'intragroup-manifest.json').read_bytes() == (HERE / 'preparation-03/bundle-manifest.json').read_bytes()
for name, row in manifest['entries'].items():
    assert digest(ROOT / name) == digest(stage / name) == row['sha256'], name
checks = read(stage / 'attempt-02/checks.json')
audit = read(stage / 'attempt-02/access-audit.json')
run = read(stage / 'attempt-02/run-manifest.json')
assert checks['passed'] and not checks['smoke_only'] and checks['normalization'] == 'none'
assert checks['exchanges'] == 351 and checks['checks'] == 3500 and checks['independent_assertions'] == 8432
assert run['passed'] and not audit['violations']
assert run['data_version'] == stage_info['manifest_sha256']
for unit in manifest['units']:
    rows = read(stage / 'attempt-02' / (unit['id'] + '-exchanges.json'))
    assert len(rows) == unit['cases'] + unit['controls']
    for population, expected_count in [('cases', unit['cases']), ('controls', unit['controls'])]:
        observed = [dict(id=r['id'], request=r['request'], result=r['result']) for r in rows if r['population'] == population]
        expected = read(ROOT / 'data/accounting-master' / unit['unit'] / 'attempt-01' / (population + '.json'))
        assert len(observed) == expected_count and observed == expected

attempt = HERE / 'attempt-02'
assert not attempt.exists() and not (HERE / 'preservation.json').exists()
shutil.copytree(stage / 'attempt-02', attempt)
shutil.copyfile(stage / 'attempt-02.log', attempt / 'launcher.log')
outputs = {}
for copied in sorted(attempt.rglob('*')):
    if not copied.is_file(): continue
    name = str(copied.relative_to(attempt))
    source = stage / 'attempt-02.log' if name == 'launcher.log' else stage / 'attempt-02' / name
    assert copied.read_bytes() == source.read_bytes()
    outputs[name] = dict(sha256=digest(copied), bytes=copied.stat().st_size)
archive = HERE / 'intragroup-replay-bundle.tar.gz'
with tarfile.open(archive, 'x:gz') as stream:
    for name in sorted(manifest['entries']): stream.add(stage / name, arcname=name, recursive=False)
    stream.add(stage / 'intragroup-manifest.json', arcname='intragroup-manifest.json', recursive=False)
with tarfile.open(archive, 'r:gz') as stream:
    members = stream.getmembers()
    assert len(members) == len(manifest['entries']) + 1
    assert {m.name for m in members} == set(manifest['entries']) | {'intragroup-manifest.json'}
    for member in members:
        assert member.isfile()
        expected = stage_info['manifest_sha256'] if member.name == 'intragroup-manifest.json' else manifest['entries'][member.name]['sha256']
        assert sha256(stream.extractfile(member).read()).hexdigest() == expected, member.name
record = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), passed=True,
    manifest_sha256=stage_info['manifest_sha256'], inputs=len(manifest['entries']), executable_modules=len(manifest['executable_modules']),
    exchanges=351, checks=3500, independent_assertions=8432, complete_saved_results_rechecked=True,
    original_and_staged_inputs_verified=True, copied_outputs_verified=True, archive_members_verified=True,
    archive=dict(path=archive.name, sha256=digest(archive), bytes=archive.stat().st_size, members=len(members)),
    outputs=outputs, command=run['command'], wall_seconds=run['wall_seconds'],
    normalization='none', original_source_admission=False, full_release_closure=False)
with (HERE / 'preservation.json').open('x') as stream:
    json.dump(record, stream, indent=2); stream.write('\n')
print(json.dumps({k: record[k] for k in ['passed','inputs','exchanges','checks','independent_assertions','archive']}))
