"""Index new intragroup evidence while preserving original acceptance bytes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'data/accounting-master/release-plan-execution-20261027'
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
clauses = {r['id']: r for r in read(BASE / 'acceptance-clauses.json')['rows']}
originals = {r['id']: r for r in read(BASE / 'release-acceptance.json')['rows']}
baselines = {str((BASE / p).relative_to(ROOT)): digest(BASE / p)
             for p in ['release-acceptance.json', 'acceptance-clauses.json']}
support = {
 'MC06.02': ('Complete legal books and consolidation adjustments remain separate in all five copied profiles.', 'Other consolidation methods and independent accounting acceptance remain open.'),
 'MC06.04': ('Reciprocal credit/settlement, full internal-profit elimination, outside resale and later release reproduce with complete expected accounts and gross cash origins.', 'Multi-lot, FX, impairment, changing ownership and broader intragroup transactions remain separate methods.'),
 'MC13.03': ('Dated legal/group journals and complete carry bridges reproduce and reconcile without hidden balancing entries.', 'This is read-only conditional arithmetic, not transactional commit/durability validation.'),
 'MC13.05': ('Balanced output retains all five admission/authorization/execution flags as false.', 'Actual accounting and source admission require separate evidence and decisions.'),
 'MC15.01': ('Supplied qualifying outside sales preserve their revenue premises and exact receipts/costs.', 'General revenue contracts, collection dynamics and actual recognition facts are not validated.'),
 'MC15.02': ('One-lot downstream/upstream purchases, internal balances, settlement, cost and resale have complete replay evidence.', 'General inventory costing, multiple lots, losses and impairment are outside the profile.'),
 'MC15.03': ('Second-year legal and acquired-basis depreciation and tax release remain active in the full closing accounts.', 'The schedules are supplied examples; no general asset, payroll or financing capability is added.'),
 'MC15.04': ('Closed legal/group openings retain prior equity, NCI, inventory margin and tax; unknown tax preserves 28 unresolved responses.', 'General multi-period control, tax and carry applicability remain open.'),
 'MC16.01': ('Every declared balance/profit report field matches its complete expected output and rational identities.', 'Complete statutory presentation and notes for an actual company are not supplied.'),
 'MC16.02': ('Owners/NCI profit and closing equity, internal cash cancellation and surviving outside flows are independently checked.', 'This does not establish every cash-flow classification or all equity changes.'),
 'MC16.04': ('Each retained synthetic history reproduces its full supplied report set, legal journals and consolidation worksheets.', 'The profile-specific report set is not the full disclosure package required by broad MC16.'),
 'MC18.02': ('Recognition/nonrecognition/unresolved tax, settlement/credit and resale alternatives remain separate complete results.', 'These selected alternatives do not establish complete probabilistic or continuous history families.'),
 'MC24.03': ('Five exact profile versions, recursive imports and native source-lock reads are identified in one manifest.', 'Other interfaces, authoritative versions and migrations remain separate.'),
 'MC24.04': ('The declared native request/result goldens reproduce exactly and independent fixtures are reevaluated.', 'No new grammar, general compilation or independent implementation is established.'),
 'MC25.04': ('All 351 full results replay with zero normalization; every input identity remains unchanged.', 'Random streams and production recovery across other profiles are not tested.'),
 'MC26.04': ('All 147 malformed/out-of-profile controls retain exact refusal results; unknown tax is not converted into a valid report.', 'This is typed refusal behavior, not a general solver infeasibility/completeness result.'),
 'MC30.03': ('Native locked source editions and exact manuscript passages are preserved as declared dependencies.', 'Source interpretation/applicability was not newly adjudicated; retention does not grant redistribution rights.'),
 'MC31.02': ('Thirty inspected executable modules run five declared profile subsets from a copied tree.', 'Other native, company, bank and insurer runtime integrations remain outside this replay.'),
 'MC31.03': ('The resolved Python environment, distribution versions and observed installed-file hashes are recorded.', 'No clean installation or independent-machine compatibility check has occurred.'),
 'MC33.01': ('Complete frozen outputs, separately authored fixture fields and 8,432 rational assertions support bounded conformance.', 'Fixtures inherit predecessor premises; independent domain/implementation acceptance remains required.'),
 'MC33.04': ('Engineering and numerical replay pass under supplied synthetic facts; accounting/scientific/reader acceptance stays distinct.', 'Counts and replay success cannot promote broad release acceptance.'),
 'MC34.01': ('This supplement binds current reproduction to exact original clauses without replacing the frozen index.', 'Only these bounded increments are newly assessed.'),
 'MC34.04': ('The replay exposed and repaired a new diagnostic attribution error while preserving native behavior and the failed run.', 'Cross-method interactions outside the five selected profiles remain unassessed.'),
 'MC35.02': ('Feasible dependency, arithmetic and preservation work was completed internally.', 'Additional internal joins and source checks remain before external referral.')}
rows = []
for identifier, (increment, residual) in support.items():
    clause = clauses[identifier]
    acceptance = originals[clause['parent']]['original_condition']['acceptance']
    assert acceptance == clause['original_acceptance']
    assert sha256(acceptance.encode()).hexdigest() == clause['original_acceptance_sha256']
    rows.append(dict(id=identifier, condition=clause['condition'], original_acceptance=acceptance,
        original_acceptance_sha256=clause['original_acceptance_sha256'], supported_increment=increment,
        remaining_condition=residual, full_requirement_closed=False, scope_waiver=False,
        disposition='bounded_evidence_added_original_acceptance_remains_open'))
evidence_names = ['result.md','preservation.json','preparation-03/bundle-manifest.json',
    'attempt-02/checks.json','attempt-02/independent-checks.json','attempt-02/access-audit.json',
    'attempt-02/run-manifest.json','attempt-02/environment-lock.json','failure-review.md']
record = dict(date=datetime.now(timezone.utc).isoformat(), baseline_records=baselines, rows=rows,
    evidence={str((HERE / p).relative_to(ROOT)): digest(HERE / p) for p in evidence_names},
    prior_companion_supplement='data/accounting-master/internal-evidence-companion-20261027/acceptance-supplement.json',
    status=dict(engineering='bounded_pass', numerical='exact_conditional_rational_checks_pass',
                accounting='actual_admission_pending', scientific='no_forecast_claim', reader='independent_acceptance_pending'))
with (HERE / 'acceptance-supplement.json').open('x') as stream:
    json.dump(record, stream, indent=2); stream.write('\n')
lines = ['# Intragroup evidence and remaining acceptance', '',
 'All original acceptance bytes are preserved. The five copied profiles add the',
 'following bounded evidence; every broad requirement remains open.', '',
 '| Clause | Added evidence | Remaining condition |', '| --- | --- | --- |']
for row in rows: lines.append(f"| {row['id']} | {row['supported_increment']} | {row['remaining_condition']} |")
lines += ['', 'Exact original wording and hashes are in acceptance-supplement.json. The prior',
           'source-to-report supplement remains separately linked. No original condition',
           'has been waived or replaced by a test count.', '']
with (HERE / 'acceptance-supplement.md').open('x') as stream: stream.write('\n'.join(lines))
assert all(digest(ROOT / p) == h for p, h in baselines.items())
print(json.dumps(dict(clauses=len(rows), frozen_records_preserved=True, broad_closures=0)))
