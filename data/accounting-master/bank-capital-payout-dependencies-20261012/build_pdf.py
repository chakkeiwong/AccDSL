"""Build only this new candidate, retaining complete logs."""
import json
import os
import subprocess
import time
from build_candidate import CAND, OUT, ROOT, save

assert not (OUT / 'completion.json').exists()
env = os.environ.copy()
overrides = {'TEXMFVAR': '/tmp/accdsl-texmfvar', 'TEXMFCACHE': '/tmp/accdsl-texmfvar', 'CUDA_VISIBLE_DEVICES': '-1'}
env.update(overrides)
command = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
start = time.monotonic()
with (OUT / 'build-stdout.log').open('w') as log:
    result = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
record = {'command': command, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': overrides,
          'wall_seconds': time.monotonic() - start, 'exit_code': result.returncode}
save('build-run.json', record)
print(json.dumps(record))
raise SystemExit(result.returncode)
