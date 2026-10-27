"""Attach bounded new evidence to original clauses without rewriting them."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'data/accounting-master/release-plan-execution-20261027'
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
frozen = {str((BASE / n).relative_to(ROOT)): digest(BASE / n)
          for n in ('release-acceptance.json', 'acceptance-clauses.json')}
clauses = {r['id']: r for r in read(BASE / 'acceptance-clauses.json')['rows']}
originals = {r['id']: r for r in read(BASE / 'release-acceptance.json')['rows']}
preserved = read(HERE / 'preservation.json')
assert preserved['checks'] == 2981 and preserved['archive_members_verified']
assert digest(HERE / preserved['archive']['path']) == preserved['archive']['sha256']

# Each entry states the supported increment, exact residual and next work.
support = {
 'MC24.03': ('The two component manifests identify unchanged native interfaces and every imported file; conflicting shared bytes are refused.', 'Only the selected source/opening/history/report profile chain is assembled; other authoritative interfaces and migrations remain separate.', 'Trace the next manuscript capability to its exact profile, entry points and dependencies.'),
 'MC24.04': ('The native source parent, separate reading and complete downstream requests/results reproduce with independent rational checks.', 'Authored source-to-packet interpretation and general source-to-IR compilation are not reconstructed; the complete demonstration language remains a distinct fixture.', 'Extend goldens only where a manuscript claim requires an unrepresented interface.'),
 'MC24.05': ('One documented command executes both declared components from a copied tree.', 'This is author execution of reference code, not compatible independent implementation.', 'Prepare precise interface questions and retain pending independent implementation acceptance.'),
 'MC25.01': ('Thirty-seven native exchanges include complete positive and adverse inputs, output variants and refusal evidence.', 'Other API and adapter signatures and their joins are outside the replay population.', 'Identify a consequential unsupported join before adding a case.'),
 'MC25.03': ('Input, code, manifest, original result and archive identities are checked; both source views retain their distinct provenance.', 'Hash agreement does not test general event idempotency or semantic migration.', 'Link separate idempotency and migration examples to their original clauses.'),
 'MC25.04': ('Financial results and status comparisons reproduce; seven timings, one independently valid nonunique certificate and two conflict-set orders have explicit comparison rules.', 'General random-stream allocation and replay across all runtimes are not tested.', 'Retain exact comparison scopes and examine the next runtime independently.'),
 'MC25.05': ('Successful replay evidence survives transfer from temporary execution storage to a verified archive.', 'This storage copy does not test crash recovery, transactional durability or product recovery semantics.', 'Use existing recovery specification and cases for those distinct duties.'),
 'MC26.04': ('Unresolved-history outcomes remain unresolved; incompatible opening intervals have independent contradiction checks.', 'These cases do not establish completeness of conflict extraction or all solver-unknown causes.', 'Preserve unresolved versus infeasible distinctions in subsequent joins.'),
 'MC26.05': ('Result budgets and statuses compare unchanged; the launcher bounds each child invocation and preserves raw logs.', 'No resource envelope, scalability result or general timeout-response conformance has been measured.', 'Check claimed timeout semantics in the native profile before a dedicated resource test.'),
 'MC30.03': ('The retained issuer ZIP, instance, PDF and 30 raw fact/context/unit records have checked identities; the selected reading is separately reproduced.', 'Edition/application authority, PDF-caption semantics, source availability at historical dates and whole-filing completeness remain separate.', 'Retain the reviewed presentation binding and investigate only consequential unresolved sources.'),
 'MC31.02': ('The declared native subset executes from one identified tree using both unchanged child drivers.', 'Other reuse integrations and runtime families are not covered.', 'Select the next consequential runtime from manuscript claims and trace its dependency closure.'),
 'MC31.03': ('Python and dependency versions plus installed-file identities are retained in both environment locks.', 'The original environment is reused; no clean installation or independent-machine compatibility result exists.', 'Specify recipient prerequisites and access dispositions before an authorized installation study.'),
 'MC31.04': ('The record distinguishes actual composition/replay evidence from static source inspection.', 'Elapsed time is descriptive; there is no performance or superiority comparison.', 'Use separate criteria and a predeclared baseline for any later performance study.'),
 'MC33.01': ('Complete expected and observed outputs and independent rational checks accompany all declared exchanges.', 'Expected records and source readings may share authored interpretation errors; unrepresented cases and independent review remain open.', 'Review omitted interfaces and full expected states before extending the executable evidence.'),
 'MC33.04': ('Engineering reproduction passes within the stated boundary while accounting, scientific and reader acceptance remain separately pending.', 'No independent acceptance has been supplied by this run.', 'Keep these dispositions distinct in the current release index.'),
 'MC34.01': ('This supplement binds the new result to exact original clause wording and original acceptance identities.', 'It supplements selected provisions; it is not a complete new assessment of all 156 clauses.', 'Continue clause-specific reconciliation as additional results are obtained.'),
 'MC34.02': ('The README, manifests and result identify current support and source-construction/environment/access residuals.', 'Whole-filing construction, other runtimes, recipient source access and independent acceptance remain required.', 'Trace the next consequential dependency rather than copy unrelated historical trees.'),
 'MC34.04': ('Both child manifests remain enforced in the combined tree, with 190 equal shared files and no observed cross-component undeclared access.', 'Audits cover Python-visible calls after startup, not arbitrary native syscalls or every accounting interaction.', 'Inspect the next shared-state interaction under its own original assumptions.'),
 'MC35.02': ('Feasible local source, arithmetic, software and preservation checks are complete for this bounded unit.', 'Other feasible internal work remains; no external referral is needed for packaging residuals.', 'Continue internal dependency and interface work.'),
 'MC35.05': ('Pending human acceptance is recorded without interrupting independent ready internal work.', 'Author checks cannot confer reader, implementation or domain acceptance.', 'Finish internal preparation before presenting focused acceptance questions.')
}
evidence_paths = [
 HERE / 'result.md', HERE / 'preservation.json', HERE / 'attempt-01/result.json',
 HERE / 'preparation-01/companion-manifest.json',
 HERE / 'attempt-01/source-reconstruction/checks.json',
 HERE / 'attempt-01/source-reconstruction/access-audit.json',
 HERE / 'attempt-01/source-to-report/checks.json',
 HERE / 'attempt-01/source-to-report/independent-checks.json',
 HERE / 'attempt-01/source-to-report/access-audit.json',
 ROOT / 'data/accounting-master/executable-evidence-closure-20261027/execution-review.md',
 ROOT / 'data/accounting-master/retained-source-reconstruction-20261027/result.md']
evidence = {str(p.relative_to(ROOT)): digest(p) for p in evidence_paths}
rows = []
for identifier, (increment, residual, next_work) in support.items():
    clause = clauses[identifier]
    original = originals[clause['parent']]['original_condition']['acceptance']
    assert clause['original_acceptance'] == original, identifier
    assert sha256(original.encode()).hexdigest() == clause['original_acceptance_sha256'], identifier
    rows.append(dict(id=identifier, parent=clause['parent'], condition=clause['condition'],
        original_acceptance=original, original_acceptance_sha256=clause['original_acceptance_sha256'],
        supported_increment=increment, residual=residual, next_action=next_work,
        disposition='bounded_evidence_added_original_acceptance_remains_open',
        full_requirement_closed=False, scope_waiver=False))
report = dict(date=datetime.now(timezone.utc).isoformat(),
    profile='AccDSLAcceptanceEvidenceSupplement/1',
    baseline_records=frozen, evidence=evidence, rows=rows,
    scope='New companion evidence only; preserves the 114 frozen rows and 156 authored clauses.',
    status=dict(engineering='bounded_reproduction_pass', accounting='not_admitted_by_replay',
                scientific='no_forecast_or_superiority_claim', reader='independent_acceptance_pending'),
    full_release_closure=False)
with (HERE / 'acceptance-supplement.json').open('x') as stream:
    json.dump(report, stream, indent=2); stream.write('\n')
lines = ['# Acceptance evidence added by the internal companion', '',
 'The original acceptance records remain byte-identical. This supplement adds bounded',
 'evidence to the provisions below; it closes no broad requirement and grants no waiver.', '',
 'Engineering reproduction passed. Accounting admission, scientific validation and',
 'independent reader/implementation acceptance remain distinct and pending.', '',
 '| Clause | New supported evidence | Remaining condition and next work |',
 '| --- | --- | --- |']
for row in rows:
    lines.append(f"| {row['id']}: {row['condition']} | {row['supported_increment']} | {row['residual']} {row['next_action']} |")
lines += ['', 'Exact original wording, baseline hashes and result-file identities are retained in',
          '`acceptance-supplement.json`. See `result.md` for execution scope and `README.md`',
          'for reproduction instructions. The two component run records preserve full checks',
          'and all comparison exceptions. Counts are not acceptance scores.', '']
with (HERE / 'acceptance-supplement.md').open('x') as stream:
    stream.write('\n'.join(lines))
assert all(digest(ROOT / p) == h for p, h in frozen.items())
print(json.dumps(dict(rows=len(rows), frozen_records_unchanged=True, full_requirements_closed=0)))
