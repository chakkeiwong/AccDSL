"""Build the candidate with bounded log output and an exact command record."""
import json
import os
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
CAND = ROOT / 'docs/design/proposal/manuscript-visible-text-20261012'
COMMAND = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
env = os.environ.copy()
env.update(TEXMFVAR='/tmp/accdsl-texmfvar', TEXMFCACHE='/tmp/accdsl-texmfvar', CUDA_VISIBLE_DEVICES='-1')
start = time.monotonic()
with (OUT / 'build-stdout.log').open('w') as log:
    result = subprocess.run(COMMAND, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
record = {'command': COMMAND, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': {k: env[k] for k in ['TEXMFVAR', 'TEXMFCACHE', 'CUDA_VISIBLE_DEVICES']}, 'wall_seconds': time.monotonic()-start, 'exit_code': result.returncode}
(OUT / 'build-run.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
raise SystemExit(result.returncode)
