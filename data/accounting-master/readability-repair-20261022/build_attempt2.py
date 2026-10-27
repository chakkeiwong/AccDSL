"""Build the amended candidate once, retaining all first-attempt evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_candidate import check

U = Path(__file__).resolve().parent
R = U.parents[2]
C = R / 'docs/design/proposal/manuscript-readability-20261022'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (U / 'build-attempt-2.json').exists()
for name, digest in json.loads((U / 'attempts/1/preservation.json').read_text())['bindings'].items():
    assert sha(R / name) == digest, name
checks = check(source_only=True)
with (U / 'source-checks-attempt-2.json').open('x') as f:
    json.dump(checks, f, indent=2); f.write('\n')
env = os.environ.copy()
settings = {'CUDA_VISIBLE_DEVICES': '-1', 'TEXMFVAR': '/tmp/accdsl-readability-20261022-tex-cache',
            'TEXMFCACHE': '/tmp/accdsl-readability-20261022-tex-cache'}
env.update(settings)
cmd = ['latexmk', '-lualatex', '-silent', '-g', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
start = datetime.now(timezone.utc).isoformat(); tick = time.monotonic()
with (U / 'build-attempt-2-stdout.log').open('xb') as f:
    result = subprocess.run(cmd, cwd=C, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=180)
manifest = dict(command=cmd, cwd=str(C.relative_to(R)), started_utc=start,
    wall_seconds=time.monotonic()-tick, exit_code=result.returncode, environment=settings,
    python=sys.executable, git_commit=json.loads((U / 'protection.json').read_text())['head'],
    plan='docs/plans/accounting-readability-repair-20261022.md',
    amendment='docs/plans/accounting-readability-repair-20261022-amendment.md',
    result='data/accounting-master/readability-repair-20261022/result.md',
    source_lock_sha256=sha(U / 'source-lock.json'),
    data_version='Protected3.46; bounded prose/navigation and grammar replacements; no financial data change',
    seeds='N/A deterministic document build', cpu_gpu='CPU only; GPU devices intentionally hidden',
    stdout='data/accounting-master/readability-repair-20261022/build-attempt-2-stdout.log', attempt=2)
with (U / 'build-attempt-2.json').open('x') as f:
    json.dump(manifest, f, indent=2); f.write('\n')
if result.returncode == 0:
    checks = check()
    with (U / 'candidate-checks.json').open('x') as f:
        json.dump(checks, f, indent=2); f.write('\n')
    (U / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(exit_code=0, wall_seconds=manifest['wall_seconds'],
        pages=checks['pages'], pdf_sha256=checks['pdf_sha256'])))
else:
    print(json.dumps(dict(exit_code=result.returncode, wall_seconds=manifest['wall_seconds'])))
raise SystemExit(result.returncode)
