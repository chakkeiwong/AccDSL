# Typed quantities and intermediate state constraints checked

24 October 2026. TypedAffineHistory/1 preserves complete dimensional definitions
before exact affine lowering and independently replays every opening, event,
snapshot measurement and declared state constraint. All 303 conformance checks,
76 targeted unit methods, 11 recorded cases and 259 protected inputs pass. The
unit suite includes 18 new typed-history methods plus preserved regressions; these
counts overlap and are not independent evidence.

The authored stock example starts with cash 20, inventory carrying amount zero
and zero units. A four-unit restock at fixed cost two precedes a three-unit sale
at fixed price three and cost two. Closing cash is 21, inventory carrying amount
two, units one and the credit equity balance is -23. These are constructed inputs
for conformance, not issuer facts or an approved revenue/cost method.

Reversing the same-day order preserves those closing quantities but produces
intermediate stock -3. The explicit stock interval [0,100], applied at opening
and after each event, makes this ordered family infeasible. Omitting the constraint
permits the algebraic candidate and reports that state constraints were unchecked.
The reference does not silently infer operational requirements or treatment authority.

The monetary embedding matches two independently replayed histories from the
unchanged predecessor. Context, dimension and uncompensated scale mismatches reject
before solving. Missing premises are unresolved; missing target facts allow only
a candidate; resource exhaustion remains unknown. Exact semantic verification
permits alternate valid witnesses and rejects forged traces or conflict labels.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain typed affine reference within its declared scope | Exact comparator and independent prefix/measurement replay pass | No type, prefix, preservation or replay veto; bound expansion before recording | Nonlinear effects, integer lots, candidate admission and real facts remain outside scope | Add matched strict byte/text authoring across the inspected conditional profiles, then integrate the substantive state result | General operational sufficiency, accounting compliance, real-company reconstruction or finished DSL |

Pre-record red-team repairs: bounded expanded constraint terms as well as state
instances; built symbolic states incrementally; rejected unnamed currency; repaired
a premise-conflict test so it changes meaning rather than just adding an invalid
field. The smallest strong alternative explanation is that examples only test
fixed affine incidence. That is the explicit profile restriction; no unknown
price product, native contract method or endogenous event completeness is claimed.
Any independently valid counterexample to replay/type agreement triggers repair.

Version 3.65 remains 448 pages, not_ready; this increment is not yet integrated.
S1–S5 partial; S6 held; S7 deferred. No whole MC requirement closes.
