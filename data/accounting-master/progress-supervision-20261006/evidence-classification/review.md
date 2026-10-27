# Focused supervisor review

The repair addresses MC25 and MC33–MC35: false stagnation caused by rejecting
supporting references alongside a located proposal finding. The preserved
controller rejected both recorded P16 reports. Replaying their actual output,
timestamps and file hashes through the repaired monitor counts two findings and
clears the checkpoint request. The original run remains recorded as a failed
process and no proposal acceptance changes.

Reviewed the report-validation path, role checks, clock/acknowledgement path,
novelty keys, incremental event parser, checkpoint recovery boundary, campaign
restart and worker instructions. Support is limited to progress notes in source
or deliverable folders and the proposal check schema in exact run/phase/check
locations. Missing files, changed hashes, missing locators, malformed check
records and other operational records reject the report. Failed checks can be
support: their result does not need to pass to explain an unfinished contract.

At least one substantive located file remains mandatory. Support is recorded
separately and omitted from finding novelty; changing support or the next action,
or duplicating/reordering references cannot renew the same finding. Editors
retain the previous substantive-file and phase-scope checks. Support never saves
an editable checkpoint or supplies phase acceptance. No timing, retry, stop,
cleanup or acceptance rule was changed.

Validation: 29 focused supervision tests passed. The two incident regressions
fail on the preserved old controller (three assertions across two tests, no
errors), and pass on the repaired controller. All 240 controller and 21 proposal
tests passed without skips. Original test logs, actual-report replay and source
diffs are saved here. Startup will rerun the required suites after loading the
updated controller.

Skeptical result audit: the replay establishes removal of this specific false
stall. It does not show that a live planner will finish, or that five minutes is
an optimal progress window. Reports remain cooperative worker claims backed by
files and locators, not automated semantic proofs. A differently worded but
equivalent conclusion can still appear novel; bounded time, terminal reviews
and the campaign's no-progress stop remain necessary. Unbounded support
admission was rejected: arbitrary run files and checker-only reports stay
excluded. No new independent model review was performed for this local repair;
this is supervisor source review plus deterministic regression evidence.

Decision: resume the authorized proposal campaign after verifying protected
files and preserving the historical failure. Reset only its accumulated
no-progress boundary for this diagnosed scheduler defect, with a reconciliation
receipt. Keep the original campaign deadline, per-invocation limit and five
editable retries. Product implementation remains disabled. A new live failure
requires diagnosis; this receipt does not authorize an automatic reset loop.
