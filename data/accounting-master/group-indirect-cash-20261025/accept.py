"""Preserve accepted group replay without altering the executed baseline."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert not (HERE/'replay-observation.json').exists()
log=Path('/tmp/accdsl-group-indirect-replay.log')
last=json.loads(log.read_text().splitlines()[-1])
assert last=={'passed':True,'mode':'read_only_replay','focused':14,'regressions':56,'cases':8,'locked_files':63}
for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
for row in json.loads((HERE/'evidence.json').read_text())['cases']:assert sha(ROOT/row['path'])==row['sha256'],row['name']
for filename,target in [('accdsl-group-indirect-replay.log','replay.log'),('accdsl-group-indirect-record.log','record.log'),
                        ('accdsl-group-indirect-probe.log','initial-fixture-failure.log'),
                        ('accdsl-group-indirect-probe-02.log','repaired-discriminator.log')]:
    (HERE/target).write_bytes((Path('/tmp')/filename).read_bytes())
dump(HERE/'replay-observation.json',{**last,'log_sha256':sha(HERE/'replay.log'),
    'command':'python3 -B data/accounting-master/group-indirect-cash-20261025/verify.py'})
(HERE/'result.md').write_text('''# Verified legal bridges compose with conditional group cash removal

25 October2026. Fourteen focused tests and56 regressions pass at record and
read-only replay. Eight complete cases on two charts/four supplied category
combinations replay exactly against63 locked files. All frozen dependency
sources remain unchanged. Baseline snapshots and explicit adapters are retained.

GroupIndirectCash/1 recomputes the group report and each legal indirect bridge,
binds complete report requests/results and exact selected books, and preserves
both legal histories. Raw legal profit/adjustments are summed, then the negative
of explicitly removed internal operating flows is added. No residual is used.
The supported group profile leaves profit unchanged; wider methods remain open.

The asymmetric discriminators give raw operating cash−10 plus correction30,
and raw50 minus30, each yielding group operating20. The original two cases
have correction0 while preserving gross flow removal. The complete generated
states equal the retained snapshots after exactly three cash-flow identity
translations and one empty input schema addition. Full adapted report requests
and results match; original provenance is preserved, not claimed byte-identical.

Unrelated valid traces, swapped or missing owners, forged/rehashed results,
stale/reused pairs and changed dependencies refuse. An omitted pair remains
conditional and unadmitted; equality of amounts never fabricates a match.
The initial fixture failed because its postconditions were empty. A real
nonnegative-cash postcondition repaired it; the frozen engine was not weakened.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept finite group bridge | Complete exact replay, independent corrections and unchanged adapted legal reports pass | Integrity, population, binding and gross-pair checks pass | Supplied classifications, control and pair completeness | Integrate the equation and correspondence into4.27 | General consolidation, source/accounting admission, complete notes or forecast validity |

Strongest alternative explanation: a mathematically consistent result can use
incomplete or inappropriate supplied pairs/policies. The omitted-pair case and
false completeness/classification flags preserve that distinction. This is
deterministic conformance, with no stochastic ranking or performance claim.
CPU-only execution imports no GPU framework. Commands, environment, wall time,
git base and exact uncommitted bytes are preserved by the run manifest/locks.
Version4.26 remains governing until integration passes. All53/6/46 obligations
remain; S1–S5 partial,S6 held,S7/E3 deferred. Next:
docs/plans/accounting-group-indirect-integration-20261025.md.
''')
dump(HERE/'acceptance-manifest.json',{'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n)
    for n in ['accept.py','result.md','record.log','replay.log','replay-observation.json','run-manifest.json',
              'evidence.json','source-lock.json','initial-fixture-failure.log','repaired-discriminator.log']}})
print(json.dumps({'accepted':True,**last}))
