# Preserve exact shared-factor credit measurements before book admission

25 October 2026. S2-S5; MC02/07/08/10-13/16-18/24-28/30/32-35.
Baseline: nine retained dated-credit requests/results, their unchanged native
calculator and independently authored stage targets. Representation audit:
data/accounting-master/credit-posting-representation-20261025/.

## Question, derivation and skeptical audit

Can exact linked expressions preserve all nine journal/state sequences,
including non-rational accrual, without choosing numerical endpoints? The
candidate is a read-only documentary CreditLinkedSchedule/1, not a new amount
silently accepted by the existing rational company book. Recompute and bind
the complete retained native request/result before applying the exact layer.

For the supplied fixed rate r>-1, define a=1+r and the unique positive z with
z^365=a. Uniqueness follows because x^365 is strictly increasing for x>0.
A d-day factor is z^d. Finite Laurent expressions use rational coefficients.
For integer exponent e=365q+s with0<=s<365, z^e=a^q z^s, including negative e
because a>0. Addition and multiplication followed by this substitution preserve
the value at the specified positive root. A reduced zero polynomial proves an
identity. A nonzero polynomial does NOT prove inequality: z^365-a can be
reducible. Return not-certified when a required identity does not reduce to
zero, unless an explicit special case applies. At r=0 use z=1 directly.

Only division by a nonzero rational or a power of z is required for these
schedules. No general polynomial division, sign test, root selection, ordering
or universal canonical algebraic-number equality is claimed. Internal scalar
expressions are bound to the exact native context and rate; financial outputs
add their existing currency-unit meaning. The arithmetic helper is not a
general dimensional DSL type system.

The audit passes for a finite exact representation. The old interval result
does not contain a symbolic graph; rebuild expressions from the same retained
events with an explicit recurrence, rather than pretending its separate bounds
encode dependence. Check independent authored targets and accounting identities
at every stage to reduce the risk of merely duplicating a source mistake.
Keep the existing rational-book type unchanged; source/accounting/posting
admission remain false. An exact-only adapter would omit six of nine cases;
this layer addresses that representation gap first.

## Evidence contract and defaults

Primary pass: all nine complete exact sequences preserve native journal IDs,
dates, fields, cash and contract origins; every journal sums to a certified
zero expression. At each stage prove N=G-L, gross-origin recurrence, remaining
cash PV and cash+N=opening capital+profit. Compare accumulated signed journals
to state and profit. Match every independent authored rational or affine-factor
target. Retain explicit refusal for unretained/forged native requests/results.

Numerical cross-check: enclose each normalized expression using certified
native factors at scale24 for powers0..364, then exact rational interval sums.
Require this new enclosure to be contained in the saved native enclosure for
every stage/journal amount. If containment cannot be shown, record an
inconclusive certificate and inspect it; do not silently substitute overlap.
Containment is a numerical consistency check, not proof of accounting truth.
The exact recurrence and identity checks supply the algebraic evidence.

Defaults:365 comes from the retained ACT/365F convention; r and events are
supplied historical hypotheses. Degree<365 follows from the relation, not an
optimization guess. A 7305-day power budget mirrors the native horizon;
1024-bit rational coefficients and365 terms are defensive implementation
limits tested at their boundary, not economic restrictions. Certificate scale24
is the largest existing supported scale and an explicit validation choice; no
native tolerance changes. All limits yield explicit unsupported diagnostics.

Vetoes: context/rate mix, source/hash mismatch, lost event or origin, nonzero
journal, uncertified required identity, failed enclosure containment, mutation
of native evidence or any implicit point posting. These block dependent
acceptance until repaired. A failed candidate triggers bounded repair, not
rejection of credit simulation. Runtime/counts are explanatory only. No
statistical ranking, general compliance or product readiness follows.

1. Implement the small context-bound rational polynomial helper and exact
   recurrence; first discriminate July accrual, write-off and terminal clearing.
2. Check zero/negative rates, leap dates, irregular receipts, both revision
   kinds, and exact rational projections across all retained cases.
3. Test context/rate mixing, malformed expressions, budgets, unsupported
   division and a reducible-polynomial non-equality trap. Test forged input and
   native refusals. Preserve complete symbolic outputs and certificates.
4. Record actual commands/environment/hashes, independent targets, failures
   and exact read-only replay. Audit the proposed host boundary only after
   the representation evidence passes.
5. Integrate the bounded result and refresh master controls, keeping exact
   expressions distinct from numerical approximation and source uncertainty.

Artifacts: data/accounting-master/credit-linked-measurements-20261025/.
No workers, commits, installations, GPU, outreach, fees or forecasting.
All53/6/46 remain; S1-S5 partial,S6 held,S7/E3 deferred. No whole row closes.
