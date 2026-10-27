"""Refresh the four live program controls for this completed unit."""
from pathlib import Path
R=Path(__file__).resolve().parents[3]
old="""Next: recover the Calculations1.1 normative schema from the exact publication
URL whose earlier trusted request timed out. Preserve that failed receipt and
the explicitly non-normative appendix copy; compare actual declarations and
imports if recovery succeeds. No old/new calculation adoption or rounding
policy is selected by source recovery. Historical currency intervals,full
XHTML/DTR/schema validity,installed correspondence and build identities remain."""
new="""The Calculations1.1 publication-schema recovery is complete at
data/accounting-master/r06-calc11-schema-recovery-20261020/: exact publication
URL HTTP200/no redirect,1,343 bytes,three source anchors,13 bindings and36
checks. The namespace-aware declaration/text profile matches AppendixA's
explicitly non-normative copy; exact bytes differ. No imports/includes/redefines
occur. DTS/runtime/report adoption and rounding policy remain unselected; the
Section5.4 duplicate-reference qualification is separate and open. R08 closes
no row;3.44/396/not_ready and53/6/46 remain.

Next: resume the independent insurance91/B135 source question. Inspect the
retained official navigation for the actual Basis for Conclusions lead named
by the derecognition materials,then fetch a directly supported route under a
bounded plan. Do not repeat completed calculation or discovery inventories.
Preserve original88(b)/89(b) OCI origins and the unsupported mixed-origin
termination disposition. Historical currency intervals,full validation and
actual installed/build identity remain open."""
names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md']
contents={n:(R/n).read_text() for n in names}
assert all(t.count(old)==1 for t in contents.values())
for n,t in contents.items():(R/n).write_text(t.replace(old,new))
print('Updated four live controls; no mission row closed.')
