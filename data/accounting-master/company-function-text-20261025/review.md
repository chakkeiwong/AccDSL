# Matched text review — 25 October 2026

The frontend now produces exact CompanyFunctions/1 requests and separately
identifies the supplied UTF-8 source. Eighteen focused test methods cover quoted
Unicode, LF/CRLF, block structure, duplicate declarations and JSON keys, forward
calls, refusal cases, limits and original byte/column locations. The 285 exact
comparison checks cover six saved requests and their complete materializations;
the three completed cases reproduce all three years of financial statements.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional function source | Exact typed requests, compilations and complete financial results | Parser, source-span and protected-baseline checks pass | Full language remains incomplete | Integrate the checked syntax | Whole simulator completeness |
| Retain original-source spans | Independent byte slices and codepoint-column checks | Unicode/CRLF and changed-spacing checks pass | No token-level debugger or runtime exception mapping | Explain declaration-level scope | Complete source diagnostics |

The first run found a faulty forward-call fixture and inconsistent propagation
of semantic error types. Both were repaired before recording; attempt-01 keeps
the earlier sources. This was an implementation/harness repair, not rejection
of the function design. The protected typed compiler did not change.

The strongest alternative explanation is that matching finite fixtures leaves
uncovered parser/compiler combinations. Structural refusals, exact lowering
and independent source slicing support the bounded extension, not a proof for
every source program. A newly found ambiguity or wrong byte span would trigger
repair. No continuation veto remains. No stochastic ranking, empirical policy
estimate, accounting admission or forecast inference is made.
