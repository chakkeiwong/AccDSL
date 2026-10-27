"""Bounded document build; preserve the previous attempt before another run."""
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import time

U=Path(__file__).resolve().parent
R=U.parents[2]
C=R/'docs/design/proposal/manuscript-reserve-risk-20261020'
prior=U/'attempt-01'
assert (prior/'build-manifest.json').exists()
lock=json.loads((U/'source-lock.json').read_text())
lock['added']['sha256']=sha256((C/lock['added']['path']).read_bytes()).hexdigest()
(U/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
env=os.environ.copy()
env.update(CUDA_VISIBLE_DEVICES='-1',TEXMFVAR='/tmp/accdsl-reserve-risk-tex-cache',TEXMFCACHE='/tmp/accdsl-reserve-risk-tex-cache')
cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
start=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
with (U/'build-stdout.log').open('wb') as f:
    result=subprocess.run(cmd,cwd=C,env=env,stdout=f,stderr=subprocess.STDOUT)
manifest=json.loads((prior/'build-manifest.json').read_text())
manifest.update(attempt=2,started_utc=start,wall_seconds=time.monotonic()-tick,exit_code=result.returncode,
                source_lock_sha256=sha256((U/'source-lock.json').read_bytes()).hexdigest(),
                prior_attempt='attempt-01/build-manifest.json',repair='Present-value wording; explicit probability-domain and left-CDF definitions')
(U/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'exit_code':result.returncode,'wall_seconds':manifest['wall_seconds']}))
raise SystemExit(result.returncode)
