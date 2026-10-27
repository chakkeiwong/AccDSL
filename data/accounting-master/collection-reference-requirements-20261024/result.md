# Finite collection prerequisites checked; ordered lifecycle remains open

24 October 2026. The scoped collection fragment passes 259 checks, 69 combined
unit-test methods, 15 retained comparisons and 198 protected input identities.
Eleven retained comparisons agree on the selected snapshot conditions. Four
counterexamples intentionally pass those conditions while the full native
validator rejects their lifecycle: equal-date sale before creation, missing sale
lot, double whole-lot sale and two complete settlements. The next plan repairs
that separate ordered boundary; these are not silently counted as full matches.

MethodCollections/1 declares uniqueness, exact-one reference resolution,
nondecreasing order and guarded per-row requirements. It distinguishes complete,
partial and absent collections, retaining observed order and unknown reasons.
Known duplicates and order reversals remain invalid despite unrelated unknowns.
Every result leaves source/accounting admission, eligibility and execution false.
The retained adapter is an explicit selected-field projection of a synthetic
record; raw source admission and broad record-schema equivalence are unclaimed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Limit |
| --- | --- | --- | --- | --- | --- |
| Accept finite snapshot fragment | Independent completeness/identity/reference/order expectations and 11 selected native comparisons pass | Malformed types, mappings, rows and resource-limit violations reject | Finite cases and partial-membership semantics do not establish all-history inference | Preserve this version and implement ordered identity lifecycle | No full native-validator or accounting-method equivalence |
| Reject full-method promotion | Four preserved lifecycle counterexamples remain visible | Promotion veto only; the planned repair addresses precisely this missing dependency | Unknown actions and incomplete sequences need conservative trace semantics | Implement the next audited lifecycle plan | No rejection of the simulator research direction |

The inherited guarded scalar semantics and exact types remain unchanged. New
engineering hypotheses are the explicit row, constraint and expanded-work limits;
boundary tests verify acceptance/refusal. Partial membership preserves relative
order of known members and never invents missing identities. Row templates keep
their own required-known rules and all source/type declarations.

Post-run red team: a snapshot projection can omit exactly the state needed by
a later action. The four counterexamples make that limitation executable rather
than hiding it in prose. A full method must also enforce monetary state, atomic
effects, replay and reporting. The observed failures reject only promotion of
the current fragment to that stronger scope. No continuation veto fired.
No stochastic ranking, empirical forecast claim or whole MC closure follows.

Version 3.60 stays 432 pages and not_ready; collection semantics are not yet
integrated into the manuscript. S1–S5 partial, S6 held, S7 deferred.
