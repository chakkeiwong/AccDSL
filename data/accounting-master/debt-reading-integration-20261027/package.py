"""Construct the declared successor package without changing retained evidence."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import integrate as base

H, R, S, T = base.H, base.R, base.S, base.T
read, sha, dump = base.read, base.sha, base.dump

assert not (H / 'package-record.json').exists()
v = read(H / 'verification-03/verification.json')
assert v['passed'] and all(c['passed'] for c in v['checks'])
for d in v['documents']:
    assert sha(T / (d['document'] + '.pdf')) == d['sha256']
p = T / 'README.md'
before = p.read_text()
assert before == base.transform('README.md', (S / 'README.md').read_text())
after = base.once(before, 'protected 5.52 directory', 'protected predecessor directory')
after = base.once(after, 'Source relocation was checked page by page against the included PDFs.',
                 'The predecessor has retained source-relocation evidence; this successor\nrequires its own relocation comparison in the external execution record.')
(H / 'README-before-package.md').write_text(before)
p.write_text(after)
dump(H / 'package-source-delta.json', dict(file='README.md', before_sha256=sha(H / 'README-before-package.md'),
     after_sha256=sha(p), reason='Do not silently transfer the R1 relocation finding to new PDFs; correct the predecessor reference.'))
manifest = read(S / 'package-manifest.json')
manifest.update(candidate='5.53;not_ready',
    manifest_self_hash='Stored outside this package in debt-reading-integration-20261027/package-record.json')
for row in manifest['files']:
    f = T / row['path']
    assert f.is_file() and not f.is_symlink()
    row.update(sha256=sha(f), bytes=f.stat().st_size)
assert len(manifest['files']) == 409
dump(T / 'package-manifest.json', manifest)
p = subprocess.run(['python3', '-I', '-B', 'verify_package.py'], cwd=T, capture_output=True, text=True, timeout=30)
assert p.returncode == 0, p.stdout + p.stderr
result = json.loads(p.stdout)
assert result['pass'] and result['checked_files'] == 409
dump(H / 'package-record.json', dict(candidate='5.53;not_ready', manifest_path=str((T / 'package-manifest.json').relative_to(R)),
     manifest_sha256=sha(T / 'package-manifest.json'), predecessor_manifest_sha256=sha(S / 'package-manifest.json'),
     files=409, package_verification=result, source_delta=sha(H / 'package-source-delta.json'),
     manuscript_verification=sha(H / 'verification-03/verification.json'),
     timestamp_utc=datetime.now(timezone.utc).isoformat(), full_evidence_closure=False,
     rights='Internal review only; existing per-file rights preserved; no redistribution approval'))
print(json.dumps(dict(passed=True, files=409, manifest_sha256=sha(T / 'package-manifest.json'))))
