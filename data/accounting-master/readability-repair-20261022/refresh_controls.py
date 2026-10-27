"""Refresh the four declared controls once after local evidence is frozen."""
import hashlib
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in json.loads((U/'completion.json').read_text())['bindings'].items():
    assert sha(R/name)==digest,name
out=U/'controls-after'
assert not out.exists()
controls=json.loads((U/'protection.json').read_text())['controls']
block='''## 22 October 2026 — Version 3.47 local repairs complete

Current candidate: **Version 3.47, 401 pages; not_ready**.
PDF: docs/design/proposal/manuscript-readability-20261022/accounting-product-proposal.pdf
SHA256: b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db

Version 3.46's completed author diagnosis covers all 401 pages and 676 nodes
in 67 ordered segments, with 17 chapter/appendix and eight cumulative-prefix
syntheses. It remains immutable at
data/accounting-master/readability-repair-20261021/regression/.

Version 3.47 repairs its seven confirmed prose/navigation defects and thirteen
literature author-subject agreement passages found in local review. The cash
interpretation is direct, the compiler reference reaches Section 7.4, source
qualifications remain, and the hedge pointer reaches following Section
10.12.10. All 144 source files remain; seven changed files reverse exactly to
3.46. All 219 displays and 727 citation occurrences are preserved. The final
build has no critical warnings or out-of-page text. Actual local rendered
review covers 26 pages, including the full literature chapter and neighboring
transitions. The first build is retained separately.

The frozen local repair and additive R08 assessments are at
data/accounting-master/readability-repair-20261022/. Safe replay: verify.py
without flags. Never rerun completed preparation, amendment, build, render,
record or control-refresh stages.

All 53 obligations, six interactions and 46 operations remain, with zero
whole-row closures. Full Version 3.47 ordered regression begins separately
with every judgment pending; no earlier reading credit transfers. Independent
reader, implementability, domain and human acceptance remain pending. No
global continuation veto has fired.

Next: execute docs/plans/accounting-readability-regression-20261022.md, with
fresh evidence under readability-repair-20261022/regression/. Review in small
ordered segments, then synthesize chapters, cumulative prefixes and the whole
argument. Preserve the final candidate while diagnosing; continue ready
internal research after the reading and any confirmed repair.

The reserve-originals inquiry remains bounded access evidence: 19 receipts,
58 bindings, no new technical paper; original/final comparisons remain open.
Do not repeat rejected publisher/SSRN/ETH routes without a new legitimate lead.
The source inquiries and open nonadditive EPS, general hedge attribution,
zero-weight reversal, insurance91/B135 interaction and build/validation
correspondence remain internal work. Allocation, current authority and actual
entity preferences remain separate dependencies.

The E3 target and six scientific choices remain unselected; all 192 vintage
admissions remain false. They block dependent empirical work, not independent
review or source research. Runtime/controller, installations, empirical runs,
acquired-code execution, commits, outreach, publication and fees remain held.
Earlier dated records below retain their historical scope.
'''
pending=[]
for name in controls:
    path=R/name
    text=path.read_text()
    before,marker,rest=text.partition('## 21 October 2026 — Version 3.46 repairs\n')
    assert marker and text.count(marker)==1,name
    _,marker2,after=rest.partition('\n## 20 October 2026 — current source frontier\n')
    assert marker2,name
    pending.append((path,before+block+marker2+after))
out.mkdir()
records=[]
for path,text in pending:
    old=sha(path)
    path.write_text(text)
    (out/path.name).write_text(text)
    records.append(dict(path=str(path.relative_to(R)),before=old,after=sha(path)))
(out/'refresh.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(dict(controls=len(records),version='3.47',full_regression='pending',whole_rows_closed=0)))
