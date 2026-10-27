"""Preserve truncated auxiliaries from the fatal run, then rebuild the candidate."""
import json
import os
import shutil
import subprocess
import time
import integrate as m

previous=json.loads((m.HERE/'build.json').read_text())
assert previous['returncode']==12 and previous['attempt']==2
backup=m.HERE/'failed-build-02';backup.mkdir()
for name in ('build.json','build.log'):
 shutil.copy2(m.HERE/name,backup/name)
auxiliary=backup/'auxiliary';auxiliary.mkdir()
for suffix in ('.aux','.toc','.bbl','.blg','.fdb_latexmk','.fls','.log','.out'):
 path=m.TARGET/('accounting-product-proposal'+suffix)
 if path.exists():path.rename(auxiliary/path.name)
command=previous['command'];env=previous['environment'];start=time.monotonic()
with (m.HERE/'build.log').open('w') as log:
 result=subprocess.run(command,cwd=m.TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
pdf=m.TARGET/'accounting-product-proposal.pdf'
m.dump('build.json',dict(command=command,cwd=str(m.TARGET),environment=env,returncode=result.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=m.sha(pdf) if pdf.exists() else None,attempt=3,prior_attempts=['failed-build-01','failed-build-02']))
print(json.dumps({'returncode':result.returncode}),flush=True)
raise SystemExit(result.returncode)
