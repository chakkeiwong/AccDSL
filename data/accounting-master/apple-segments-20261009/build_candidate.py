"""Bounded LuaLaTeX build; keep every attempt in its own directory."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT/'docs/design/proposal/manuscript-segments-20261009'
if (OUT/'completion.json').exists():
    raise SystemExit('Unit is frozen')
attempt = 1
while (OUT/f'build-{attempt:02}').exists():
    attempt += 1
if attempt > 3:
    raise SystemExit('Three-build budget exhausted; diagnose before revising the plan')
run = OUT/f'build-{attempt:02}';run.mkdir()
cache = Path('/tmp/accdsl-segments-tex-cache-20261009');cache.mkdir(exist_ok=True)
environment = dict(CUDA_VISIBLE_DEVICES='-1',TEXMFVAR=str(cache),TEXMFCACHE=str(cache))
cmd = ['latexmk','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
start = datetime.now(timezone.utc);timer=time.monotonic()
with (run/'build.log').open('w') as log:
    try:
        result=subprocess.run(cmd,cwd=NEW,env={**os.environ,**environment},stdout=log,stderr=subprocess.STDOUT,timeout=240)
        code=result.returncode
    except subprocess.TimeoutExpired:
        code=124
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pdf=NEW/'accounting-product-proposal.pdf'
receipt=dict(command=cmd,cwd=str(NEW),environment=environment,started_at=start.isoformat(),
             finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-timer,
             exit_code=code,log_sha256=sha(run/'build.log'),pdf_sha256=sha(pdf) if pdf.exists() else None,
             script_sha256=sha(Path(__file__)),attempt=attempt)
(run/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(code)
