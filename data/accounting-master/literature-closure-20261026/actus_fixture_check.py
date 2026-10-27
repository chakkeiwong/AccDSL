"""Independent arithmetic on two retained official PAM fixtures; no ACTUS runtime."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime
import json,hashlib,time,sys
p=Path(__file__).resolve().parent;start=time.monotonic()
source=p/'sources/actus-tests-tests_actus-tests-pam.json'
fixtures=json.loads(source.read_text()); rows=[]
# Tolerance is solely for decimal serialization in the official expected file.
# It does not license contract errors. 1e-10 currency units exceeds the observed
# 14-digit expected payoff rounding while remaining far below a cent.
tol=F(1,10**10)
for name,den,step in [('pam01',365,1),('pam02',360,2)]:
 f=fixtures[name];t=f['terms'];face=F(t['notionalPrincipal']);rate=F(t['nominalInterestRate']);discount=F(t['premiumDiscountAtIED'].strip());
 assert t['contractRole']=='RPA' and t['currency']=='USD'
 expected=[('2013-01-01T00:00','IED',-(face+discount))]
 prev=datetime(2013,1,1)
 for m in list(range(1,13,step))+[13]:
  now=datetime(2013,m,1) if m<=12 else datetime(2014,1,1)
  expected.append((now.isoformat(timespec='minutes'),'IP',face*rate*F((now-prev).days,den)));prev=now
 expected.append(('2014-01-01T00:00','MD',face))
 assert len(expected)==len(f['results'])
 for (date,event,value),actual in zip(expected,f['results']):
  err=abs(F(str(actual['payoff']))-value)
  ok=date==actual['eventDate'] and event==actual['eventType'] and err<=tol
  rows.append(dict(fixture=name,event=event,date=date,expected_exact=str(value),published=actual['payoff'],error_exact=str(err),passed=ok));assert ok
result=dict(status='PASS',checks=len(rows),cases=['pam01','pam02'],tolerance=str(tol),scope='Independent dated A365/A360 arithmetic, initial discount, same-day order and principal maturity against retained fixture. Not runtime conformance.',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),records=rows)
(p/'actus-fixture-results.json').write_text(json.dumps(result,indent=2)+'\n')
(p/'actus-fixture-manifest.json').write_text(json.dumps(dict(command='python3 data/accounting-master/literature-closure-20261026/actus_fixture_check.py',python=sys.version,wall_seconds=time.monotonic()-start,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),random_seeds='N/A: deterministic arithmetic',cpu_gpu='CPU only; no device detection',git='Unusable repository marker; hashes preserved',plan='docs/plans/accounting-literature-closure-20261026.md'),indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'}))
