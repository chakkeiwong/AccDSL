# Separate native settlement policy effects

28 October 2026. T01/C04; MC08, MC10, MC13, MC18, MC19, MC26, MC28,
MC32 and MC35. Source comparison: company-state-rea-policy-reading-20261028.md.

## Intent and evidence contract

Question: can the same declared settlement amounts be generated as proposed
inputs, checked as exact equalities, or compared as targets without confusing
these effects? Comparator: the retained SettlementPolicyDraft/1 generator and
the unchanged native CompanyOperationPathDraft/1 executor on the exact
second_year_price_revision parent. This is an engineering discriminator; no
behavioral or legal claim is made.

The local request must explicitly select generate_inputs, validate_equalities
or compare_targets. Exact equality is the declared constraint for this bounded
case, not a universal interpretation of a collection policy. Targets report
signed actual-minus-target differences and never fail native execution merely
because those differences are nonzero. Generation retains the original
materialization and executes its child through guarded population admission.
Validation/comparison inspect the original supplied path and never rewrite it.

Primary pass criterion: exact hand-derived amounts agree for the three roles;
unchanged native full results remain attached; target-only differences cannot
become constraints or accounting postings. Hard vetoes: wrong parent/context,
digest mismatch, malformed request, lost native history or a comparison using
an unexecuted event as if executed. Unknown required amounts remain unresolved.
Explanatory diagnostics: check counts and runtime. No stochastic ranking,
forecast, authority, source admission or whole-company acceptance follows.

## Skeptical audit and assumptions

The earlier parent mistake is repaired and must not recur: the policy belongs
to the retained price-revision path, whose invoice is 16 times 12 = 192. The
9/10 rule with two equal installments prescribes 432/5 for each targeted
allocation; the supplied path contains 396/5. Thus each actual-minus-target
difference is -36/5. The retained complete parent is the baseline.

The three-role vocabulary is a local design choice justified by the inspected
2006 distinction, not an implementation imported from REA. Its earliest test
uses identical numbers and changes only the requested role. Rational arithmetic
and existing native guards are reviewed inherited defaults for this exact
profile; no rounding, tolerances or probability models are added.

Partial native histories are a material risk. A collection that has not
executed has no realized allocation. Return all row outcomes, preserve known
violations separately, and mark overall evidence incomplete when a required
row is unavailable. A zero executed allocation remains an observed zero.
Unknown openings produce no comparison population. Actor/public requests
and cross-owner meanings remain unsupported; audit-only source identities
are not actor admission.

Audit verdict: the bounded comparison may execute. An implementation or
expectation failure stops only this attempt; retain it and repair before a new
attempt. The source's heuristic patterns and absent contract lifecycle do not
justify extending this work into commitment execution.

## Execution

Add a closed request and dispatcher under
data/accounting-master/company-state-policy-effects-20261028/. Reuse the
existing policy module and guarded population inspection; do not change their
financial semantics. Retain request/result identities, complete native
results, actual/target differences and unresolved obligations. Test baseline,
matching child, full-collection later failure, malformed/wrong identities,
unknown policy, unknown opening and unexecuted target events. Preserve every
attempt, manifest and check result. Document the supported meaning and
remaining common-owner/actor gaps in the live specification and master.
