"""Build the new prose candidate once with a complete bounded manifest."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from check_candidate import check

U=Path(__file__).resolve().parent
R=U.parents[2]
C=R/'docs/design/proposal/manuscript-readability-20261021'
assert not (U/'build-manifest.json').exists()
checks=check(source_only=True)
with (U/'source-checks.json').open('x') as f:
    json.dump(checks,f,indent=2);f.write(chr(10))
env=os.environ.copy()
settings={'CUDA_VISIBLE_DEVICES':'-1','TEXMFVAR':'/tmp/accdsl-readability-20261021-tex-cache','TEXMFCACHE':'/tmp/accdsl-readability-20261021-tex-cache'}
env.update(settings)
cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
start=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
with (U/'build-stdout.log').open('xb') as f:
    result=subprocess.run(cmd,cwd=C,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
manifest={'command':cmd,'cwd':str(C.relative_to(R)),'started_utc':start,'wall_seconds':time.monotonic()-tick,
    'exit_code':result.returncode,'environment':settings,'python':sys.executable,
    'git_commit':json.loads((U/'protection.json').read_text())['head'],
    'plan':'docs/plans/accounting-readability-repair-20261021.md',
    'result':'data/accounting-master/readability-repair-20261021/result.md',
    'source_lock_sha256':hashlib.sha256((U/'source-lock.json').read_bytes()).hexdigest(),
    'data_version':'Protected3.45; exact bounded prose replacements; no financial data change',
    'seeds':'N/A deterministic document build','cpu_gpu':'CPU only; GPU devices intentionally hidden','attempt':1}
with (U/'build-manifest.json').open('x') as f:
    json.dump(manifest,f,indent=2);f.write(chr(10))
print(json.dumps({'exit_code':result.returncode,'wall_seconds':manifest['wall_seconds']}))
raise SystemExit(result.returncode)
