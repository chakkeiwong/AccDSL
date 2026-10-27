"""Advance only the four authorised live controls for this completed source unit."""
from pathlib import Path

R = Path(__file__).resolve().parents[3]
old = """Next: trace the pinned text-block validator's actual caller/configuration and
three explicitly named entity dependencies. Preserve the 56-fragment XML
structure result and source/projection distinction. Inspect retained source
before new bounded acquisition. Full XHTML/DTR/schema validity, source
ambiguities, normative schema copy, installed correspondence and build
identities remain."""
new = """The R06 caller/entity inquiry is complete at
data/accounting-master/r06-textblock-dependencies-20261020/: twelve HTTP200
acquisitions,27 anchors,48 bindings,176 checks and17 exact Git blob identities.
One concrete FERC caller is profile-guarded; base legacy profiles are commented.
The six DTD/entity edges retain253 declarations. Equal checker/declaration
counts conceal &there; versus &there4;,neither present literally in the frozen
56 fragments. The source treats inline document sets differently in caller
and DTD selector. Actual Apple profile/runtime impact remains unestablished.
No expansion or upstream execution occurred; R08 closes no row and3.44 stays
396 pages/not_ready. Safe replay is verify.py without flags only.

Next: audit the independent historical-currency duty left by the completed
seven-unit inquiry. Inspect authoritative maintenance-agency sources and exact
fact periods; current code membership alone cannot establish past validity.
Keep all873 currency-bearing results partial until date-supported evidence
exists. Preserve the56-fragment structural result and source/projection
distinction. Full XHTML/DTR/schema validity,installed correspondence and build
identities remain."""
names = ['docs/plans/accounting-master-current.md',
         'docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-mission-requirements.md',
         'data/accounting-master/next-plan.md']
contents = {name: (R / name).read_text() for name in names}
assert all(value.count(old) == 1 for value in contents.values())
for name, value in contents.items():
    (R / name).write_text(value.replace(old, new))
print('Refreshed four authorised live controls; no mission row closed.')
