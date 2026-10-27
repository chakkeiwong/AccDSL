"""Prepare additive credit only for the repaired revision candidate."""
from pathlib import Path
H=Path(__file__).resolve().parent;S=H.parent/'acquisition-worksheet-progress-20261027'
assert not (H/'refresh.py').exists()
code=(S/'refresh.py').read_text()
code=code.replace("G=H.parent/'gap-acquisition-worksheet-refresh-20261027'","G=H.parent/'gap-acquisition-revision-refresh-20261027'")
code=code.replace("PLAN='docs/plans/accounting-acquisition-revisions-20261027.md'","PLAN='docs/plans/accounting-acquisition-worked-integration-20261027.md'")
code=code.replace("RESULTS=['data/accounting-master/acquisition-worksheet-20261027/result.md','data/accounting-master/acquisition-consideration-20261027/result.md']","RESULTS=['data/accounting-master/acquisition-revision-prefix-repair-20261027/result.md']")
code=code.replace("a['active_work_plan']=='docs/plans/accounting-acquisition-worksheet-20261027.md'","a['active_work_plan']=='docs/plans/accounting-acquisition-revisions-20261027.md'")
code=code.replace("OLD.name=='gap-acquisition-design-refresh-20261027'","OLD.name=='gap-acquisition-worksheet-refresh-20261027'")
start=code.index('for p,title,scope in zip(');end=code.index('\n    audit[',start)
code=code[:start]+"for p,title,scope in [(RESULTS[0],'Acquisition revisions with chronology,eligibility and original preservation','26 full cases,15 refusals,703 assertions. Earlier /1–/3 candidates are superseded after preserved discriminating failures; /4 remains conditional.')]:"+code[end:]
start=code.index('for title,case,p in [');end=code.index('\n    fail[',start)
code=code[:start]+"for title,case,p in [('Unknown availability admits a pre-discovery or ineligible acquisition revision','Keep discovery lower bounds and retrospective eligibility separate; unknown access cannot create an impossible revised worksheet.',RESULTS[0]),('An unsupported future revision invalidates the original report','Evaluate a revised candidate only when eligible and potentially available; retain full original plus held candidate/refusal when its method is missing.',RESULTS[0])]:"+code[end:]
code=code.replace("audit['successor_deltas'][:-2]","audit['successor_deltas'][:-1]")
code=code.replace('Cash-only and cash/new-parent-equity synthetic acquisition worksheets pass complete account/journal/report comparisons; actual admission remains false.','Repaired /4 acquisition revision views pass26 cases/703 assertions,retaining chronology,eligibility and earlier full reports; actual admission remains false.')
code=code.replace('Execute accounting-acquisition-revisions-20261027.md; then extend prior-interest/debt conversion,loss/ownership,eliminations and general item methods with independent full reports.','Integrate checked worksheet/consideration/repaired revision companions under accounting-acquisition-worked-integration-20261027.md; then extend intragroup,prior-interest/debt conversion,loss/ownership and general items.')
code=code.replace('Dated measurement revisions are next.','Repaired dated revisions are checked;worked manuscript integration is next.')
code=code.replace('Two scoped deltas and two interface challenges are added.','One repaired-candidate delta and two interface challenges are added.')
code=code.replace("acquisition_worksheet_result=RESULTS[0],acquisition_consideration_result=RESULTS[1]","acquisition_revision_result=RESULTS[0]")
code=code.replace('Version5.29 unchanged. Synthetic acquisition worksheets and cash/noncash consideration pass full comparisons; dated revisions next. Actual debt conversion/admission remain unresolved.','Version5.29 unchanged. Repaired /4 dated acquisition revision views pass full comparisons;worked integration next. Prior debt conversion/actual admission remain unresolved.')
code=code.replace("'Bind dated acquisition revisions to complete actor views'","'Integrate full worked acquisition,consideration and repaired revision explanations'")
start=code.index("notice=f'''");end=code.index("\nnew={",start)
code=code[:start]+"""notice=f'''## Acquisition revision repair checked — 27 October2026

Version5.29 remains governing:790 main pages;223 total/204 body simulation pages.
ConditionalAcquisitionRevisionView/4 passes26 cases,15 controls,703 assertions.
Three preserved counterexamples supersede /1–/3; source truth/admission stay open.
Result:{RESULTS[0]}. Worksheet/consideration/revision companions await integration.
Active financing plan:{PLAN}.
Independent plan:{independent}.
Full program:{base}/closure-program.md.
All53 obligations,six interactions,46 operations and18 packages remain open.
S1–S5 partial;S6 held;E3 deferred. Continue feasible internal work.

'''"""+code[end:]
(H/'refresh.py').write_text(code);print('Prepared guarded repaired-revision credit without changing live controls.')
