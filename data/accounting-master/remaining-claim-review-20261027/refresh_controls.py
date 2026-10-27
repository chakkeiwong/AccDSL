"""Advance only live controls after the successful bounded claim review."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

H = Path(__file__).resolve().parent
R = H.parents[2]
new_plan = 'docs/plans/accounting-executable-evidence-closure-20261027.md'
old_plan = 'docs/plans/accounting-remaining-claim-review-20261027.md'
rel = str(H.relative_to(R))
digest = lambda p: sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
checks = read(H/'attempt-01/checks.json')
assert checks['passed'] and len(checks['checks']) == 1245 and not checks['remaining']
assert (R/new_plan).is_file()
prior = read(H.parent/'current-claim-reconciliation-20261027/control-refresh.json')
for path, expected in prior['frozen'].items():
    assert digest(R/path) == expected, path
paths = [r['path'] for r in prior['controls']]
backup = H/'controls-before'
backup.mkdir(exist_ok=False)
prepared = {}
block = '''## Current execution — 27 October 2026

Governing candidate **5.54**, 834 main pages and 263 total / 242 body
simulation pages, remains **not_ready**. Four stable PDF/TeX links select it.
Main SHA256: 2fab07216d933c450f9e8d7f486ab326e58a99cb026095302c330d1a1f3e98ef.
Simulation SHA256: 1eb01507caaf7529f479433253c1bc8ba0752307f43cef25e3a0330877a4eb5c.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Acceptance index: data/accounting-master/release-plan-execution-20261027/release-acceptance.md.
Clause-level work: data/accounting-master/release-plan-execution-20261027/acceptance-clauses.md.
Current result: data/accounting-master/remaining-claim-review-20261027/result.md.
Current claim ledger: data/accounting-master/remaining-claim-review-20261027/current-claim-ledger.json.
Remaining release work: data/accounting-master/remaining-claim-review-20261027/remaining-work.md.
Active plan: docs/plans/accounting-executable-evidence-closure-20261027.md.

All 27 mapped claims now have bounded current dispositions. The latest twelve
cover inference, financing, disclosure, causal identification, implementation,
numerical objectives, evaluation and conditional risk. All 1,245 checks pass
and 554 files are preserved. These checks do not accept the wider citation
population, all manuscript arguments, full runtimes or broad mission goals.
The earlier C21 supersession and repaired coupling hypotheses remain explicit.
No new manuscript repair was required by this review.

The 411-file document package relocates; both volumes match normalized page
text. The selected source/history adapter preserves 236 observations, 101
equations and 180 unresolved obligations in two contexts. It supplies no
actual issuer history, joined cross-context history or executable opening.
The source/opening compatibility reference has 12 complete replays and 14
boundaries. Its new adapter and wider executable dependencies remain outside
the two included runnable components. Trace and stage those dependencies next.

All 35 original MC provisions and 114 acceptance rows are preserved. The 156
authored clauses are work units, not accepted conditions; 201 failure rows are
targets/evidence, not 201 executed tests. All 53 obligations, six interactions,
46 operations and 18 packages remain open. S1–S5 partial; S6 held; E3 deferred.
Internal source, specification and manuscript work continues before any focused
external referral. No publication, outreach or paid engagement is authorized.

Package/build result: data/accounting-master/selected-history-integration-20261027/result.md.
Current company audit: data/accounting-master/real-company-acceptance-20261027/result.md.
Compatibility: data/accounting-master/source-opening-compatibility-20261027/compatibility.md.
Selected source/history result: data/accounting-master/selected-reading-history-20261027/result.md.
Ordered manuscript reading: data/accounting-master/release-pursuit-20261027/progress.md.
Historical assessments below are preserved.
'''
for name in paths:
    path = R/name
    destination = backup/name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    if path.suffix == '.json':
        doc = read(path)
        key = 'active_execution_note' if name.startswith('scripts/') else 'active_execution'
        active = doc[key]
        assert active['active_work_plan'] == old_plan
        active.update(active_work_plan=new_plan, full_gap_plan=new_plan,
            remaining_work=rel+'/remaining-work.md', latest_internal_result=rel+'/result.md',
            remaining_claim_review=rel+'/result.md', current_claim_ledger=rel+'/current-claim-ledger.json',
            latest_reset_memo=rel+'/reset-memo.md', compression_next_plan=new_plan)
        active.setdefault('completed_plan_evidence', {})[old_plan] = rel+'/result.md'
        active['next'] = ['Trace and stage source/history/opening/report executable evidence dependencies',
            'Continue C2/C4 residuals and saved ordered manuscript reading',
            'Preserve bounded source limits; keep S6 held and E3 deferred']
        prepared[name] = json.dumps(doc, indent=2, ensure_ascii=False)+'\n'
    else:
        text = path.read_text()
        start = text.index('## Current execution — 27 October 2026')
        end = text.index('Historical assessments below are preserved.', start)+len('Historical assessments below are preserved.')
        prepared[name] = text[:start]+block.rstrip()+text[end:]
records = []
for name, content in prepared.items():
    path = R/name
    before = digest(path)
    assert before == digest(backup/name), name
    path.write_text(content)
    records.append(dict(path=name, before=before, after=digest(path)))
for path, expected in prior['frozen'].items():
    assert digest(R/path) == expected, path
for name, content in prepared.items():
    assert (R/name).read_text() == content, name
with (H/'control-refresh.json').open('x') as stream:
    json.dump(dict(passed=True, controls=records, frozen=prior['frozen'], next_plan=new_plan), stream, indent=2)
    stream.write('\n')
print(json.dumps(dict(passed=True, controls=len(records), next_plan=new_plan)))
