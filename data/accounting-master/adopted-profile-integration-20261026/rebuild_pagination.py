"""Drop a stale page-enlargement override after citation boxing failed."""
import json
import os
import shutil
import subprocess
import time
import integrate as m
previous=json.loads((m.HERE/'build.json').read_text())
assert previous['returncode']==12 and previous['attempt']==3
backup=m.HERE/'failed-build-03';backup.mkdir()
for name in ('build.json','build.log'):shutil.copy2(m.HERE/name,backup/name)
shutil.copy2(m.TARGET/'sections/selected-reuse.tex',backup/'selected-reuse.tex')
(m.TARGET/'sections/selected-reuse.tex').write_bytes((m.SOURCE/'sections/selected-reuse.tex').read_bytes())
name='sections/adapter-methods.tex'
assert (m.TARGET/name).read_bytes()==(m.SOURCE/name).read_bytes()
(m.TARGET/name).write_text(m.expected(name,(m.SOURCE/name).read_text()))
aux=backup/'auxiliary';aux.mkdir()
for suffix in ('.aux','.toc','.bbl','.blg','.fdb_latexmk','.fls','.log','.out'):
 path=m.TARGET/('accounting-product-proposal'+suffix)
 if path.exists():path.rename(aux/path.name)
m.dump('layout-repair.json',dict(source=name,before_sha256=m.sha(m.SOURCE/name),after_sha256=m.sha(m.TARGET/name),
 reason='Remove the inherited one-line page-enlargement override after shifted pagination triggered a hyperlink nesting error. Citation boxing did not repair it and was reverted exactly.',
 expected_delta='Delete one enlargethispage baselineskip command; all prose and citations unchanged',prior_failures=['failed-build-01','failed-build-02','failed-build-03']))
command=previous['command'];env=previous['environment'];start=time.monotonic()
with (m.HERE/'build.log').open('w') as log:
 result=subprocess.run(command,cwd=m.TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
pdf=m.TARGET/'accounting-product-proposal.pdf'
m.dump('build.json',dict(command=command,cwd=str(m.TARGET),environment=env,returncode=result.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=m.sha(pdf) if pdf.exists() else None,attempt=4,prior_attempts=['failed-build-01','failed-build-02','failed-build-03']))
print(json.dumps({'returncode':result.returncode}),flush=True)
raise SystemExit(result.returncode)
