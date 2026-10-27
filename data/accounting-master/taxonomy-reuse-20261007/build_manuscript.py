#!/usr/bin/env python3
"""Build the separate candidate with an explicitly writable, local TeX cache."""
import json
import argparse
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
env = os.environ.copy()
parser = argparse.ArgumentParser()
parser.add_argument('--trusted', action='store_true')
args = parser.parse_args()
cache = Path('/tmp/accdsl-taxonomy-20261008-texcache')
cache.mkdir(exist_ok=True)
if not args.trusted:
    env['TEXMFVAR'] = str(cache/'texmf-var')
    env['TEXMFCACHE'] = str(cache)
cwd = ROOT/'docs/design/proposal/manuscript-taxonomy-20261008'
command = ['latexmk','-lualatex','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
start = time.monotonic()
with (OUT/'build.stdout.log').open('w') as log:
    run = subprocess.run(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
receipt={'command':command,'cwd':str(cwd.relative_to(ROOT)),'exit_code':run.returncode,
         'wall_seconds':time.monotonic()-start,'finished_at':datetime.now(timezone.utc).isoformat(),
         'environment_overrides':{x:env[x] for x in ['TEXMFVAR','TEXMFCACHE'] if x in env},
         'permission_context':'trusted after sandbox cache failure' if args.trusted else 'sandbox; TeX caches explicitly placed in writable /tmp',
         'log':str((OUT/'build.stdout.log').relative_to(ROOT))}
(OUT/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
raise SystemExit(run.returncode)
