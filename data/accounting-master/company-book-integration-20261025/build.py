import hashlib,json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
TARGET=ROOT/'docs/design/proposal/manuscript-company-book-20261025'
assert not (HERE/'build.json').exists(),'build already recorded; preserve before repair'
command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
environment={'TEXMFVAR':'/tmp/accdsl-company-book-20261025-tex-cache','TEXMFCACHE':'/tmp/accdsl-company-book-20261025-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
Path(environment['TEXMFVAR']).mkdir(parents=True,exist_ok=True)
start=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
with (HERE/'build.log').open('w') as stream:
    r=subprocess.run(command,cwd=TARGET,env={**os.environ,**environment},stdout=stream,stderr=subprocess.STDOUT,timeout=180)
pdf=TARGET/'accounting-product-proposal.pdf'
result={'started_utc':started,'wall_seconds':time.perf_counter()-start,'command':command,'cwd':str(TARGET.relative_to(ROOT)),'environment':environment,'returncode':r.returncode,'log':str((HERE/'build.log').relative_to(ROOT)),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else None}
(HERE/'build.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result))
raise SystemExit(r.returncode)
