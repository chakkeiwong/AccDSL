# Pinned processor alignment and duplicate interval behavior

20 October 2026. The selected Arelle commit
01f6a4656c2c6551d2f05f31c9d74366d133ee7e binds calculations by exact key
intersection, not by searching for a subset of dimensions. Context and unit
partition helpers first use equality-aware wrapper keys. Calculation keys then
contain concept, ancestor, a context integer hash and the canonical unit.
This supports equality as a contextual interpretation of intended alignment;
it does not supply a normative correction to Calculations 1.1 §5.1.

Three exact-commit helper acquisitions succeeded (Contexts, Units, Equivalence).
The complete helpers use dictionary grouping with equality-aware wrapper keys.
The context equality method checks equal dimension-name sets and individual
values; it does not implement subset matching. A later calculation key uses
contextNonDimAwareHash without retaining the context object in that key.
A constructed equal-hash/different-context witness shows information loss in
that key design; no actual hash collision or installed behavior was measured.

Inspection also found direct mismatches between selected calculation branches
and the declared interval/duplicate target. These are source-level findings
under stated inputs; upstream code was never imported or executed.

| Finding and source | Constructed consequence | Classification |
| --- | --- | --- |
| consistentFactValueInterval sets a same-precision inequality flag inside its loop, then replaces it with an interval-only predicate at line 500 | Values 1 and 3, both decimals 0, return the first interval under the authored branch trace; the contextual OIM6.2 rule rejects them | Wrong relative to the declared same-precision duplicate target |
| Interval inclusion flags accumulate by OR when an endpoint changes or ties | Exact 1 followed by truncated 0 at decimals 0 admits the singleton boundary 1, although truncation gives (-1,1) | Wrong intersection endpoint under the explicit truncation target |
| Excess-digit handling precedes duplicate rejection and skips precision comparison for that fact | 1.1 and 3 at decimals 0 produce excess-digits status instead of prior inconsistent-duplicates status | Different diagnostic order from §5.2 |
| insignificantDigits skips decimals <= -28 | Value 1 at decimals -28 passes the authored source guard despite not being a multiple of 10^28 | Missed excess-digits condition under that finite input |
| Negative weight swaps numeric endpoints without swapping their inclusion flags | [1,2) times -1 becomes closed at -2/open at -1 in the inspected operation instead of (-2,-1] | Wrong endpoint propagation |
| Final overlap uses OR between endpoint inclusion flags | Exact total 2 and computed [1,2) are admitted at the touching boundary | Wrong overlap result under the explicit intervals |

The exact-1/truncated-zero witness can be viewed as both an intersection
endpoint problem and a resulting inconsistent-duplicate miss. Separate positive
controls preserve same-value duplicates, ordinary mixed precision, nearest
disjoint intervals, nil-only sets and mixed nil. There are 14 authored witnesses,
18 AST/source checks, 20 source anchors and 24 direct input bindings; all
107 counted checks pass. Authored traces use exact rational values and inspect
the relevant branches without executing the upstream helper. Decimal contexts,
actual framework values, installed call paths and real-filing effects remain
unevaluated. No claim about a later release or existing upstream fix is made.

The current manuscript's duplicate-set statement is about the separate
ValidateDuplicateFacts.areWithinRoundingError API. Its cited behavior remains
supported. These findings concern the calculation helper and do not justify
rewriting that passage as if it had claimed universal library consistency.
Keep the additive reuse evidence and require operation-specific checks in any
later integration. No manuscript defect requiring a rebuild was identified.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain exact-key implementation evidence | Binding/helper chain inspected | No source identity veto | Normative alignment wording unresolved; hash behavior unobserved | Use equality only as an explicitly conditional arithmetic hypothesis | Authoritative clarification or generic OIM equality |
| Reject this pinned helper as a correctness oracle | Exact branch witnesses differ from declared target | Source mismatches supported | Runtime reachability/filing impact not measured | Independently implement mathematical interval diagnostics for retained data | Installed failure, current-release defect or issuer error |
| Continue internal preparation | Protected evidence and current candidate intact | No global continuation veto | Wider conformance/source/acceptance gaps | Conditional report arithmetic with exact duplicated-value and endpoint checks | Whole-row closure or final readiness |

The strongest alternative explanation is that upstream validation or a
particular dataset prevents some witnesses from reaching the helper. That
could limit practical impact but would not repair the inspected branch result
for its explicit inputs. A different pinned body, unreachable caller proof, or
new validation evidence would change the applicable conclusion. The weakest
evidence is actual execution and incidence. Candidate 3.44 remains 396 pages,
not_ready, with 53 obligations, six interactions, 46 operations and zero rows
closed. No stochastic comparison or ranking was performed.
