"""Reconcile live master pointers after bounded replay; preserve frozen records."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
rel = str(HERE.relative_to(ROOT))
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
prior = read(HERE.parent/'remaining-claim-review-20261027/control-refresh.json')
checks = read(HERE/'attempt-04/checks.json')
assert checks['passed'] and checks['checks'] == 1667
assert read(HERE/'preservation.json')['original_inputs_unchanged']
new_plan = 'docs/plans/accounting-refinancing-action-domain-20261027.md'
old_plan = 'docs/plans/accounting-executable-evidence-closure-20261027.md'
assert (ROOT/new_plan).is_file()
active = read(ROOT/'scripts/accounting_master_catalog.json')['active_execution_note']
assert active['active_work_plan'] == old_plan
assert active['current_candidate'] == '5.54-R1;834 pages;not_ready'
for key in ['current_pdf','standalone_pdf']:
    assert digest(ROOT/active[key]) == active[key+'_sha256']
for name, expected in prior['frozen'].items():
    assert digest(ROOT/name) == expected, name
links = {str(p.relative_to(ROOT)):str(p.readlink()) for p in (ROOT/'docs').iterdir() if p.is_symlink() and p.name.startswith('AccDSL')}
backup = HERE/'controls-before'
backup.mkdir(exist_ok=False)
block = f'''## Current execution — 27 October 2026

Governing candidate **5.54-R1**, 834 main pages and 263 total / 242 body
simulation pages, remains **not_ready**. The four stable PDF/TeX links select it.
Main SHA256: {active['current_pdf_sha256']}.
Simulation SHA256: {active['standalone_pdf_sha256']}.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Acceptance index: data/accounting-master/release-plan-execution-20261027/release-acceptance.md.
Current result: {rel}/result.md.
Current reset: {rel}/reset-memo.md.
Remaining work: {rel}/remaining-work.md.
Active plan: {new_plan}.

The isolated 234-file replay component passes 1,667 checks across 37 complete
exchanges. Native financial results and statuses match; seven timings, one
independently checked existential certificate and two conflict-label orders
have explicit comparison rules. No undeclared Python-visible access or changed
input was observed. All 236 observations, 101 equations and 180 unresolved
issuer obligations remain. Full source reconstruction, other runtimes,
recipient access and clean installation are still outstanding.

All 27 mapped claims have bounded current dispositions in
data/accounting-master/remaining-claim-review-20261027/current-claim-ledger.json.
The already built 5.54-R2 refinancing successor awaits rendered review and
isolated package reproduction before selection. Ordered baseline reading
reached page 132; resume at 133 with current-version delta checks.

All 35 original MC provisions and 114 acceptance rows are retained. The 53
obligations, six interactions, 46 operations and 18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Internal work continues before any focused
external referral; no publication, outreach or paid engagement is authorized.
Historical assessments below are preserved.'''
prepared = {}
for row in prior['controls']:
    name = row['path']
    path = ROOT/name
    target = backup/name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path,target)
    if path.suffix == '.json':
        doc = read(path)
        key = 'active_execution_note' if name.startswith('scripts/') else 'active_execution'
        item = doc[key]
        assert item['active_work_plan'] == old_plan
        item.update(active_work_plan=new_plan, full_gap_plan=new_plan,
            remaining_work=rel+'/remaining-work.md', latest_internal_result=rel+'/result.md',
            latest_reset_memo=rel+'/reset-memo.md', executable_replay_result=rel+'/result.md',
            executable_replay_manifest=rel+'/preparation-04/bundle-manifest.json',
            compression_next_plan=new_plan)
        item.setdefault('completed_plan_evidence',{})[old_plan] = rel+'/result.md'
        item['next'] = ['Complete the saved 5.54-R2 refinancing derivation/page/package review',
            'Continue ordered baseline reading at physical 133 with successor delta checks',
            'Continue original C1/C2/C4 acceptance residuals; S6 held and E3 deferred']
        prepared[name] = json.dumps(doc,indent=2,ensure_ascii=False)+'\n'
    else:
        text = path.read_text()
        start = text.index('## Current execution — 27 October 2026')
        end = text.index('Historical assessments below are preserved.',start)+len('Historical assessments below are preserved.')
        prepared[name] = text[:start]+block+text[end:]
records = []
for name, content in prepared.items():
    path = ROOT/name
    before = digest(path)
    assert before == digest(backup/name)
    path.write_text(content)
    records.append(dict(path=name,before=before,after=digest(path)))
for name, expected in prior['frozen'].items():
    assert digest(ROOT/name) == expected
for name, target in links.items():
    assert str((ROOT/name).readlink()) == target
with (HERE/'control-refresh.json').open('x') as stream:
    json.dump(dict(passed=True,controls=records,frozen=prior['frozen'],links=links,
                   next_plan=new_plan),stream,indent=2)
    stream.write('\n')
print(json.dumps(dict(passed=True,controls=len(records),next_plan=new_plan)))
