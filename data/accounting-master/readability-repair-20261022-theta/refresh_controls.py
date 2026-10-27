"""Refresh live pointers once after the local repair has been frozen."""
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert (U / 'completion.json').exists() and not (U / 'controls-after').exists()
for name, digest in load(U / 'completion.json')['bindings'].items():
    assert sha(R / name) == digest, name
block = '''## 22 October 2026 — Version 3.48 theta prerequisite repaired

Current candidate: **Version 3.48, 401 pages; not_ready**.
PDF: docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf
SHA256: 6a2acd8e3e01e6127eb89112a168216ee12b3244b3e56c814f1d2d1c56b90f0e

R347-D01 is locally repaired: theta is defined before the policy and event
generator as the declared behavioural/event-generation parameters, with values
specified by the chosen history, scenario and model assumptions. No calibration,
parameter values or probability model was added. The title and one passage are
the only source changes. All 144 source files, 219 exact displays and 727
citation occurrences remain. Labels and references are unchanged. One clean
build produced no critical warnings or out-of-page text. Extracted text and
word positions change only on pages 1, 88 and 89; six actual rendered pages
(1, 2, 87–90) received local inspection.

The frozen repair and additive R08 assessments are at
data/accounting-master/readability-repair-20261022-theta/.
Safe replay: verify.py without flags. Never rerun completed preparation,
build, render, recording or control-refresh actions. All 9,211 predecessor
bindings and 36 tracked dirty paths were preserved; HEAD/index are unchanged.

Version 3.47's full diagnosis remains immutable at
data/accounting-master/readability-repair-20261022/regression/: all 401 pages,
676 nodes, 98 ordered segments, 17 chapter/appendix syntheses, eight cumulative
prefixes and the document synthesis. Its sole confirmed defect is the one
repaired here. This predecessor reading supplies no full Version 3.48 reading
credit. Full successor chapter/cumulative/document regression remains pending.
Independent reader, implementability, domain and human acceptance remain
pending. All 53 obligations, six interactions and 46 operations remain;
zero whole rows close, and no global continuation veto has fired.

Next: continue independently ready internal method/source preparation, beginning
with the existing nonadditive EPS discriminators and a bounded source/theory
inquiry under a new audited plan. Preserve their refused general-selector
status until an argument addresses the actual counterexamples. General hedge
attribution, zero-weight CGU reversal, insurance91/B135 interaction and
build/validation correspondence remain open. The reserve-originals inquiry is
bounded access evidence only; do not repeat rejected routes without a new lead.

The E3 target and six scientific choices remain unselected; all 192 vintage
admissions remain false. They block dependent empirical work, not internal
preparation. Runtime/controller, installations, empirical runs, acquired-code
execution, commits, outreach, publication and fees remain held. Earlier dated
records below retain their historical scope.

'''
changes = []
for name in load(U / 'protection.json')['controls']:
    path = R / name
    before = path.read_text()
    assert sha(path) == sha(U / 'controls-before' / name), name
    start = before.index('## 22 October 2026 — Version 3.47 local repairs complete')
    end = before.index('## 20 October 2026 — current source frontier', start)
    after = before[:start] + block + before[end:]
    changes.append((name, before, after))
target = U / 'controls-after'
target.mkdir()
for name, before, after in changes:
    path = R / name
    path.write_text(after)
    copy = target / name
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_text(after)
with (target / 'manifest.json').open('x') as f:
    json.dump(dict(scope='Live control refresh after frozen local repair',
        files=[dict(path=name, before_sha256=sha(U / 'controls-before' / name), after_sha256=sha(R / name))
               for name, _, _ in changes]), f, indent=2)
    f.write('\n')
print(json.dumps(dict(refreshed=len(changes), version='3.48', readiness='not_ready', whole_rows_closed=0)))
