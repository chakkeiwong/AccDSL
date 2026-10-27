from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import shutil

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R/'docs/design/proposal/manuscript-sector-v555-20261027'
A = R/'docs/design/proposal/manuscript-reference-v554r3-20261027'
T = R/'docs/design/proposal/manuscript-reference-v555r1-20261027'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert (R/'docs/AccDSL-latest.pdf').resolve() == B/'accounting-product-proposal.pdf'
assert not T.exists()
original = R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027/simulation/18-computation-cases.tex'
assert (B/'simulation/18-computation-cases.tex').read_bytes() == original.read_bytes()
p = R/'docs/plans/accounting-midpoint-reference-20261027.md'
p.write_text(p.read_text()+'''
## Concurrent successor reconciliation

The live package advanced to5.55 during the independent5.54-R3 repair.
The sector integration adds dated PAA and bank interfaces and24 files.
Its simulation chapter18 is byte-identical to the original repair baseline.
Do not select the older branch. Preserve it and its completed checks, and
merge only the reviewed chapter18 repair and five companion files onto5.55
as protected5.55-R1. All sector methods, sources and replay evidence remain
unchanged. Rebuild and reproduce both merged documents. Reuse the exact
arithmetic evidence because its code, data and mathematical target do not
change; verify copied identities. The older branch's main-only relocated
build is partial reproduction and cannot substitute for merged reproduction.

Skeptical re-audit passes: exact source comparison excludes a chapter conflict,
and the new successor preserves all447 selected files except explicit cover,
readme, dependency and chapter changes plus rebuilt PDFs. Live-pointer drift
before integration requires reconciliation rather than an overwrite.
''')
m = json.loads((B/'package-manifest.json').read_text())
assert len(m['files']) == 447
T.mkdir()
for row in m['files']:
    source = B/row['path']
    assert sha(source) == row['sha256']
    q = T/row['path']
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(source.read_bytes())
(T/'simulation/18-computation-cases.tex').write_bytes((A/'simulation/18-computation-cases.tex').read_bytes())
C = T/'companions/reference-computations'
shutil.copytree(A/'companions/reference-computations', C)
for name in ['accounting-product-proposal','simulation-foundations']:
    p = T/(name+'.tex')
    s = p.read_text()
    assert s.count('Version 5.55 ') == 1
    p.write_text(s.replace('Version 5.55 ', 'Version 5.55-R1 '))
p = T/'README.md'
s = p.read_text().replace('# AccDSL 5.55 — sector interfaces', '# AccDSL 5.55-R1 — sector interfaces and numerical references',1)
s = s.replace('Six companions now','Seven companions now')
s = s.replace('| Dated PAA book |', '| Reference computations | 169 retained arithmetic checks and exact midpoint cases | companions/reference-computations/README.md |\n| Dated PAA book |',1)
s += '''
This successor clarifies midpoint-grid convergence in chapter18, adds the
exact threshold-error bound and preserves all six predecessor companions.
The current record is release-pursuit-20261027/midpoint-reference/merged/.
PACKAGE-REVISION.json is the unchanged historical sector-integration record;
package-manifest.json and the current external record bind this successor.
'''
p.write_text(s)
p = T/'DEPENDENCIES.md'
p.write_text('''# Additional numerical reference in5.55-R1

The seventh component, companions/reference-computations, reproduces the
retained169 teaching checks and6,552 exact rational threshold cases using
Python3.11+ standard library. The universal bound rests on the written floor
proof. Follow its README and choose a fresh output directory. It supplies no
stochastic validation or general solver. All six sector-predecessor components
are unchanged; their earlier reproduction evidence applies to their exact
bytes. Current document build/reproduction records are in
data/accounting-master/release-pursuit-20261027/midpoint-reference/merged/.

The following dependency record is retained from the5.55 predecessor.

'''+p.read_text())
M = D/'merged'
M.mkdir()
info = {'baseline':str(B.relative_to(R)),'candidate':str(T.relative_to(R)),
    'baseline_manifest_sha256':sha(B/'package-manifest.json'),'files':m['files'],
    'allowed_changes':['README.md','DEPENDENCIES.md','accounting-product-proposal.tex',
        'simulation-foundations.tex','simulation/18-computation-cases.tex',
        'accounting-product-proposal.pdf','simulation-foundations.pdf'],
    'added_files':[str(x.relative_to(T)) for x in sorted(C.iterdir())],
    'repair_source_sha256':sha(A/'simulation/18-computation-cases.tex'),
    'plan_sha256_after_concurrent_extension':sha(R/'docs/plans/accounting-midpoint-reference-20261027.md'),
    'timestamp_utc':datetime.now(timezone.utc).isoformat()}
(M/'baseline.json').write_text(json.dumps(info,indent=2)+'\n')
b = (D/'build.py').read_text()
b = b.replace("out = D / ('relocation' if relocated else 'build')", "out = D / 'merged' / ('relocation' if relocated else 'build')")
b = b.replace("(D / 'relocation/location.json')", "(D / 'merged/relocation/location.json')")
b = b.replace("(D / 'candidate.json')", "(D / 'merged/baseline.json')")
(D/'build_merged.py').write_text(b)
print(json.dumps({'staged':str(T),'predecessor_files':len(m['files']),'added':len(info['added_files'])}))
