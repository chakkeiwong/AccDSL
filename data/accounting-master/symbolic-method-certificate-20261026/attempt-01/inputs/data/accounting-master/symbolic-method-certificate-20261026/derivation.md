# From typed expressions to exact financial equations

26 October 2026. This is a local derivation about the selected synthetic
accounting methods. It imports no new literature proposition.

A journal that balances can still charge twice the contractual coupon. The
certificate therefore checks each account change and each cash-flow origin,
together with the conditions permitting the change and the retained borrowing
history. Debit balances are positive and liability credit balances negative.
The starting book has cash11/2, other assets189/2 and old debt-100. The two
coupons are I1 and I2; the second-date operating receipt is R. Each coupon is
supplied as one-period interest, without a day-count calculation. R is6 or7.

## Parameter meaning and the surrounding program

The template parameters are I1,I2,R (the book's exact USD monetary type), mode
(text fixed/floating) and right (Boolean). For fixed mode both coupons are5.
For floating mode I_t=100 min(3/50,max(3/100,r_t)), r_t in[1/50,2/25]. Thus
I_t lies in[3,6]. The template places parameters at both selected coupon
predicates, the selected receipt predicate, the eight mode predicates, three
amount inputs, and opening mode/right. Its metadata comparison verifies these
locations and the complete remainder of the program. Two named charts and four
ordered pay/draw combinations are the finite variants. Unsupported charts and
operators are rejected.

The template itself is outside the common runtime language. Literalization
replaces the five parameters by typed scalar values, chooses the two order
names and recomputes method digests. No state transition is executed during
literalization. The parameter replacement introduces no new expression form;
ordinary typed validators check the resulting program. Universal statements
here concern valuations with valid exact encodings within existing runtime
size limits. They do not promise acceptance of arbitrarily long encodings.

All non-expression metadata is compared to the inspected pinned bridge:
opening book, report mapping, schemas, source scope, IDs, dates, classes,
account maps, input declarations, bindings, dependency lists, refusal policies,
operation order and memory-write structure. Predicate/posting/flow expressions
and memory values are the only masked leaves. Their meanings are independently
checked. The baseline comparison is deliberately restrictive: it can reject
an equivalent reordered program. It does not prove the baseline builder itself.
Independent binding tables also prevent a changed source from inheriting a
correct-looking coefficient under a misleading variable name.

## Equality for all known valuations

An affine form is the finite coefficient map a together with constant c,
meaning c + sum_j a_j x_j. Constants, bound references and parameters translate
to a constant or a unit coefficient. Addition combines coefficients and
constants; subtraction subtracts them. Induction on this grammar proves that
the form has exactly the value of the original expression. Fractions are exact
rationals, with zero coefficients removed; there is no numerical tolerance.
Hence identical forms denote identical functions of all their typed arguments.

For eq,le,lt the normalizer records the operator and the affine form of left
minus right. The operator remains distinct: x<0 and x<=0 disagree at zero.
Non-numeric comparisons retain their full symbolic operands. Boolean all/any
retain all children and only sort their order; not and Boolean equality retain
their structure. These transformations preserve predicates for known values.
This derivation does not assert equivalence for arbitrary partial/unknown
valuations, where evaluation provenance and refusal diagnostics can differ.
The original required-input lists and on_false/on_unknown policies stay exact.

## Independent accounting target

Accruing I_t increases interest expense by I_t and decreases interest payable
by I_t; it writes due_t=I_t. Paying decreases cash by due_t and increases the
payable by due_t, writes paid_t=due_t and records the pay action. It requires
cash>=due_t. Drawing pays the same interest atomically, borrows1, charges a
fee1/4 and therefore changes cash by3/4-due_t. Facility debt changes by-1 and
fee expense by1/4. Gross flows retain borrowing+1, fee-1/4 and interest-due_t.
The draw requires the right, an unused facility, due_t>11/2 and
cash+3/4>=due_t. It writes used=true and records the draw action.

The receipt increases cash by R and decreases the income credit balance by R.
Repayment uses the signed facility balance L: cash changes by L and facility
debt by-L, requiring cash>=-L. Repayment does not restore the used flag. Before
and after every method, the payable equals accrued-minus-paid history:
-interest_payable=due1-paid1+due2-paid2. The used flag equals whether either
retained action is draw. Phase, date, mode, source and clause conditions bind
these effects to the selected sequence. After a refused payment, accrual and
its unpaid obligation remain in the previously accepted state.

expected_forms.py authors these relations directly in coefficient form. It
imports neither the candidate normalizer nor the builder. certificate.py
extracts actual declared expressions and compares them with those targets.
The verifier checks symbolic method forms in both charts, exact literalization
against28 earlier concrete premises, finite chart/action/mode/right structural
instances and mutations. Sample comparisons connect the template to those
programs; they are not the proof of universal expression equality.

## What remains before region execution is certified

A method relation is not a completed history-region proof. Sequential
substitution, reachable preconditions/postconditions, strict region boundaries,
refused prefixes, observation partitions and policy choices still need their
own certificates. No continuous-region obligation is discharged by this unit.
The3872 retained obligations remain unresolved until that composition is
checked. Source admission, accounting authority, general DSL correctness,
nonlinear expressions, durable storage and production scale are independent.
