# Audit tax-close compatibility with the mixed book

24 October 2026. S2–S4; MC05/11/13/16/24/26/28/35; G2/G4;
operations P17-04.10 and P17-04.11.

## Skeptical audit

The original native tax method operates on a closed 22-account return book.
The new shared book has 25 accounts, lease memory and other_gains. Merely
renaming the profile, dropping fields or projecting balances would not preserve
the tax target. The old pretax function enumerates its original INCOME list;
the new recorded report includes the lease gain. Its tax close also advances
tax_closed_until to the exclusive end, while the shared invariant currently
requires that value to be no later than the state date. Those are material
compatibility issues, not permission to patch frozen references.

The audit must separate original-method correctness under its original scope
from validity on the mixed state. It must retain actual original tax examples,
not use a modified mixed state as an original comparator. Losses, lease tax bases
and recognition findings are unknown unless explicitly supplied. No actual tax
law or company facts are inferred from a synthetic 25% fixture rate.

## Question and evidence contract

Can the existing return tax-close method execute on the complete mixed state
without dropping accounts, changing premises or violating temporal invariants?
Primary criterion: full native state/method compatibility and complete coverage
of the mixed book's pretax accounts, tax premises and close times. Original
native tax-control results must still match their saved outputs exactly.

Hard vetoes for direct reuse: incompatible schema, omitted income, missing lease
tax facts, unsupported negative current-tax route or incompatible close dates.
These veto direct reuse; they do not veto design of a protected successor.
Balance, runtime and test counts are explanatory diagnostics only. A difference
in descriptive amounts is not a stochastic ranking. No statistical inference
or accounting-compliance conclusion is intended.

## Execution

1. Pin native return/report sources, saved original tax controls, complete mixed
   requests/results and the relevant schemas. Locate original controls before
   selecting a comparator; do not reconstruct them with new owners or dates.
2. Replay original tax controls and pass the unchanged mixed state to the native
   boundary. Record exact refusal and preserved inputs.
3. Derive and check the income-account coverage difference in project notation.
   Test existing state-date versus exclusive-tax-close invariants separately.
   Inventory missing tax bases, loss/refund and period-completion evidence.
4. Record a decision table distinguishing failed reuse from failed direction.
   Design the next smallest successor around explicit facts and unresolved
   outcomes. Preserve all historical code; refresh master controls and continue.

The inherited 25% rate is only an original fixture premise. Original cash-paid
tax, zero return tax bases and full deferred-balance reversal are scoped original
choices, not defaults for leases or actual jurisdictions. An early diagnostic
is the full saved mixed-result pretax comparison. Exact commands, environment,
source hashes and outputs belong in
data/accounting-master/shared-tax-compatibility-20261024/.
