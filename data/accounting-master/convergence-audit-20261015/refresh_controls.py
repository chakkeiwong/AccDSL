"""One-shot archive and explicit live routing refresh after the finite audit."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md',
 'docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
old='Next: execute the P17-11/P18-03/P19-01 convergence audit (docs/plans/accounting-convergence-audit-20261015.md). Reconcile all 53 original obligations against Version 2.93 and its interactions, distinguish missing design from actual-fact/runtime/human dependencies, and execute the highest-priority ready repair. Runtime execution remains held.'
new='Next: execute R01, the connected corporate portable specification (docs/plans/accounting-corporate-portable-20261015.md). The completed convergence audit locates all 53 obligations, credits delivered evidence and orders R01–R08 in data/accounting-master/convergence-audit-20261015/repair-queue.md. Complete exact corporate records, connected request/results and adverse/recovery behavior before R02 real-package integration. Runtime execution remains held.'
note='''## Convergence audit and finite continuation — 15 October 2026

The Version2.93 convergence audit now preserves all53 original obligations with
located current support, specific residuals and classified dependencies:
data/accounting-master/convergence-audit-20261015/evidence-ledger.json.
Its52 evidence files are retained as exact snapshots;81 protected files and
the100-entry unrelated index remain unchanged. Integrity checks do not grant
substantive acceptance or replace the negative Version2.72 full assessment.

Corporate, group/financing, bank, insurance and real-package interactions were
inspected. Northstar has complete financial statements, but IX01–IX06 and the
operation registry do not supply its complete portable request/result closure.
Insurance already has scoped exact exchanges. Apple and JPMorgan source/review
work is credited without inventing private histories or joining companies.

The finite repair queue is
data/accounting-master/convergence-audit-20261015/repair-queue.md.
R01 corporate closure → R02 real-package connection; R03 methods/sector scope,
R04 consequential literature, R05 future validation design and R06 reuse locks
feed R07 whole-candidate integration and R08 assessment/review/staging.
The immediate plan is docs/plans/accounting-corporate-portable-20261015.md.
Continue ready units after local failures; human feedback blocks acceptance,
not provisional repairs. No runtime/controller, installation, external outreach,
paid review or publication is authorized.

'''
archive=OUT/'control-before-r01'
assert not archive.exists(), 'one-shot archive already exists'
changes=[]
for name in paths:
 p=ROOT/name;before=p.read_text();after=before.replace(old,new)
 at=after.find('\n## ')
 if at>=0: after=after[:at+1]+note+after[at+1:]
 else:
  at=after.find('\n1. ');assert at>=0;after=after[:at+1]+note+after[at+1:]
 if name.endswith('accounting-continuation-requirements-20261007.md'):
  after=after.replace('Updated 14 October 2026.','Updated 15 October 2026.',1)
 assert before!=after and 'accounting-corporate-portable-20261015.md' in after
 changes.append((name,before,after))
for name,before,after in changes:
 dest=archive/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(before)
 (ROOT/name).write_text(after)
manifest=[{'path':n,'before_sha256':hashlib.sha256(b.encode()).hexdigest(),'after_sha256':hashlib.sha256(a.encode()).hexdigest()} for n,b,a in changes]
(OUT/'control-refresh.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'controls_updated':len(changes),'archive':str(archive.relative_to(ROOT))}))
