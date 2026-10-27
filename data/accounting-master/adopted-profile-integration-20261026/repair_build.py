"""Retry only the failed build after preserving its exact diagnostic evidence."""
import json
import os
import subprocess
import time
import integrate as m

failed=json.loads((m.HERE/'failed-build-01/build.json').read_text())
assert failed['returncode']==12
assert (m.HERE/'build.json').read_bytes()==(m.HERE/'failed-build-01/build.json').read_bytes()
name='sections/selected-reuse.tex'
before=(m.TARGET/name).read_text()
assert before==(m.SOURCE/name).read_text()
after=m.expected(name,before)
(m.TARGET/name).write_text(after)
m.dump('layout-repair.json',dict(source=name,before_sha256=m.sha(m.SOURCE/name),after_sha256=m.sha(m.TARGET/name),
 reason='Prevent the existing linked author-year citation from splitting at the changed page boundary; content and citation key unchanged',
 failed_attempt='failed-build-01',expected_delta='Wrap the one existing citep in mbox'))
command=failed['command'];env=failed['environment'];start=time.monotonic()
with (m.HERE/'build.log').open('w') as log:
 result=subprocess.run(command,cwd=m.TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
pdf=m.TARGET/'accounting-product-proposal.pdf'
m.dump('build.json',dict(command=command,cwd=str(m.TARGET),environment=env,returncode=result.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=m.sha(pdf) if pdf.exists() else None,attempt=2,prior_attempt='failed-build-01'))
print(json.dumps({'returncode':result.returncode}),flush=True)
raise SystemExit(result.returncode)
