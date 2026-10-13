"""Record the scoped document build; numerical runtime stays held."""
import json,os,subprocess,time
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
C=R/'docs/design/proposal/manuscript-apple-award-versions-20261013'
cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
settings={'TEXMFVAR':'/tmp/accdsl-texmfvar','TEXMFCACHE':'/tmp/accdsl-texmfvar','CUDA_VISIBLE_DEVICES':'-1'}
env=os.environ.copy();env.update(settings);t=time.monotonic()
with (U/'build-stdout.log').open('w') as f:
    result=subprocess.run(cmd,cwd=C,env=env,stdout=f,stderr=subprocess.STDOUT)
x={'command':cmd,'cwd':str(C),'environment':settings,'exit_code':result.returncode,'wall_seconds':round(time.monotonic()-t,2)}
(U/'build-run.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps(x))
raise SystemExit(result.returncode)
