"""Advance four live controls once after verified local repair completion."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

U=Path(__file__).resolve().parent
R=U.parents[2]
assert (U/'completion.json').exists()
subprocess.run([sys.executable,'-B',str(U/'verify.py')],check=True)
snapshot=U/'controls-after';snapshot.mkdir()
text='''## 21 October 2026 — Version 3.46 repairs

Current candidate: **Version 3.46, 401 pages; not_ready**.
PDF: docs/design/proposal/manuscript-readability-20261021/accounting-product-proposal.pdf
SHA256: 4a516701b3105ea778807f7143eb4d457f6d18cd439d8fc7172e1d9506cd1be5

The complete Version 3.45 author diagnosis covers all 401 pages and 676 nodes
in 74 ordered segments, with 17 chapter/appendix and eight cumulative-prefix
syntheses. It remains immutable at
data/accounting-master/reserve-risk-integration-20261020/regression/.

Version 3.46 repairs its three confirmed defects: the tax project-history
opening, the lease filename aside and the initial-library/query scope claim.
All 144 source files are retained; exact reversible comparison preserves
219 displays and 727 citation occurrences. Four files change only through
declared title/date and passage replacements. The final build has no critical
warning or out-of-page text. Local rendered review covers 139–141,159–161,
385–387 and title1; full exact-candidate review remains pending. No earlier
reading credit transfers. Evidence and additive R08 assessments are retained in
data/accounting-master/readability-repair-20261021/.

All 53 obligations, six interactions and 46 operations remain, with zero
whole-row closures. Independent implementability, domain and human acceptance
remain pending. No global continuation veto has fired.

Next: conduct the exact Version 3.46 argument review under a fresh inventory,
then continue the consequential Wang1995, Merz/Wüthrich2014 and England2019
original-source/edition inquiries. Use bounded actual-view segments, at most
six pages per segment and three images per tool call. Record specific node and
equation judgments, chapter/prefix syntheses and the final argument assessment.
The source inquiries and open nonadditive EPS, general hedge attribution,
zero-weight reversal, insurance91/B135 interaction and build/validation
correspondence remain internal work. Allocation, current authority and actual
entity preferences remain separate dependencies.

The E3 target and six scientific choices remain unselected; all 192 vintage
admissions remain false. They block dependent empirical work, not independent
review or source research. Runtime/controller, installations, empirical runs,
acquired-code execution, commits, outreach, publication and fees remain held.
Safe completed-repair replay: readability-repair-20261021/verify.py without
flags. Never rerun completed preparation, build, record or refresh stages.
Earlier dated records below retain their historical scope.

'''
names=('docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md')
bindings={}
for name in names:
    p=R/name;old=p.read_text()
    start=old.index('## 20 October 2026 — Version 3.45 integration')
    end=old.index('## 20 October 2026 — current source frontier',start)
    p.write_text(old[:start]+text+old[end:])
    target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    bindings[name]=hashlib.sha256(p.read_bytes()).hexdigest()
(snapshot/'result.json').write_text(json.dumps({'version':'3.46','controls':bindings,'next':'exact-candidate review'},indent=2)+chr(10))
print(json.dumps({'controls_refreshed':len(bindings),'version':'3.46','pages':401,'readiness':'not_ready'}))
