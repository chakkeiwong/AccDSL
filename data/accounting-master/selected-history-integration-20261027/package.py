"""Declare the checked document package; no retained writer is invoked."""
from datetime import datetime, timezone
import json
import subprocess
import integrate as base

H, R, S, T = base.H, base.R, base.S, base.T
read, sha, dump = base.read, base.sha, base.dump
assert not (H / 'package-record.json').exists()
v = read(H / 'verification.json')
assert v['passed'] and all(c['passed'] for c in v['checks'])
for document in v['documents']:
    assert sha(T / (document['document'] + '.pdf')) == document['sha256']
lock = read(H / 'source-lock.json')
for name, expected in lock['sources'].items():
    assert sha(S / name) == expected
    if (S / name).suffix in ['.tex', '.md']:
        assert (T / name).read_text() == base.transform(name, (S / name).read_text())
    else:
        assert sha(T / name) == expected
assert (T / 'spec/source-opening-compatibility-v1.md').read_bytes() == (H / 'source-opening-compatibility-v1.md').read_bytes()
manifest = read(S / 'package-manifest.json')
manifest.update(candidate='5.54;not_ready',
    manifest_self_hash='Stored outside this package in selected-history-integration-20261027/package-record.json')
manifest['files'].append(dict(path='spec/source-opening-compatibility-v1.md',
    role='package_reference', redistribution='unreviewed_internal_only'))
manifest['files'].sort(key=lambda row: row['path'])
for row in manifest['files']:
    file = T / row['path']
    assert file.is_file() and not file.is_symlink()
    row.update(sha256=sha(file), bytes=file.stat().st_size)
assert len(manifest['files']) == 411
dump(T / 'package-manifest.json', manifest)
p = subprocess.run(['python3', '-I', '-B', 'verify_package.py'], cwd=T,
    capture_output=True, text=True, timeout=30)
assert p.returncode == 0, p.stdout + p.stderr
verification = json.loads(p.stdout)
assert verification['pass'] and verification['checked_files'] == 411
dump(H / 'package-record.json', dict(candidate='5.54;not_ready', files=411,
    manifest_path=str((T / 'package-manifest.json').relative_to(R)),
    manifest_sha256=sha(T / 'package-manifest.json'),
    predecessor_manifest_sha256=sha(S / 'package-manifest.json'),
    verification=verification, manuscript_verification=sha(H / 'verification.json'),
    timestamp_utc=datetime.now(timezone.utc).isoformat(), full_evidence_closure=False,
    rights='Internal review only; previous rights preserved; no redistribution approval'))
print(json.dumps(dict(passed=True, files=411, manifest_sha256=sha(T / 'package-manifest.json'))))
