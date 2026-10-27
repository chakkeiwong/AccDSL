"""Bounded local LuaLaTeX build using an explicitly writable font cache."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
NEW=ROOT/'docs/design/proposal/manuscript-debt-20261009'
if (OUT/'completion.json').exists():raise SystemExit('Closed unit')
if (OUT/'build-receipt.json').exists():raise SystemExit('Preserve the prior build before rerunning')
cache=Path('/tmp/accdsl-debt-tex-cache-20261009');cache.mkdir(exist_ok=True)
environment=dict(CUDA_VISIBLE_DEVICES='-1',TEXMFVAR=str(cache),TEXMFCACHE=str(cache))
cmd=['latexmk','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
start=datetime.now(timezone.utc);timer=time.monotonic()
with (OUT/'build.log').open('w') as log:
    try:
        result=subprocess.run(cmd,cwd=NEW,env={**os.environ,**environment},stdout=log,stderr=subprocess.STDOUT,timeout=240)
        code=result.returncode
    except subprocess.TimeoutExpired:
        code=124
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pdf=NEW/'accounting-product-proposal.pdf'
receipt=dict(command=cmd,cwd=str(NEW),environment=environment,started_at=start.isoformat(),finished_at=datetime.now(timezone.utc).isoformat(),
             wall_seconds=time.monotonic()-timer,exit_code=code,log_sha256=sha(OUT/'build.log'),
             pdf_sha256=sha(pdf) if pdf.exists() else None,script_sha256=sha(Path(__file__)),sandbox='workspace with writable /tmp font cache')
(OUT/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(code)
