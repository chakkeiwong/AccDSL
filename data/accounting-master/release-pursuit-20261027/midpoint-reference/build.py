from pathlib import Path
from datetime import datetime, timezone
import json
import os
import platform
import subprocess
import sys
import time

D = Path(__file__).resolve().parent
R = D.parents[3]
name = sys.argv[1]
assert name in ['accounting-product-proposal', 'simulation-foundations']
relocated = len(sys.argv) > 2 and sys.argv[2] == 'relocated'
T = Path(json.loads((D / 'relocation/location.json').read_text())['target']) if relocated else R / json.loads((D / 'candidate.json').read_text())['candidate']
out = D / ('relocation' if relocated else 'build')
out.mkdir(exist_ok=True)
log, record = out / (name + '.stdout'), out / (name + '.json')
assert not log.exists() and not record.exists()
cache = T / '.tex-cache'
cache.mkdir(exist_ok=True)
env = dict(os.environ, TEXMFVAR=str(cache), TEXMFCACHE=str(cache), CUDA_VISIBLE_DEVICES='-1')
cmd = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape', name + '.tex']
t = time.monotonic()
with log.open('w') as f:
    run = subprocess.run(cmd, cwd=T, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=300)
data = {'command': cmd, 'cwd': str(T), 'exit_code': run.returncode,
        'wall_seconds': time.monotonic()-t, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version, 'platform': platform.platform(),
        'environment': {k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},
        'seed': 'N/A: deterministic document build', 'git_commit': 'unavailable; unusable marker',
        'plan': 'docs/plans/accounting-midpoint-reference-20261027.md'}
record.write_text(json.dumps(data, indent=2)+'\n')
print(json.dumps(data))
raise SystemExit(run.returncode)
