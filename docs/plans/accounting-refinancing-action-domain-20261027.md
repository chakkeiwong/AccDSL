# Specify the refinancing comparison's action domain

MC11/13/14/17/18/24/26/28/32–35; release C2/C4/C5. The governing
candidate is 5.54-R1. The ordered baseline read has covered the whole refinancing
chapter. Section 14.13 calls a policy set finite although its bridge principal
and term face vary continuously. Three sale choices do not resolve that issue.
The source is simulation/14-refinancing-case.tex in the selected package.

## Question and evidence contract

Question: which continuous financing actions are feasible under each specified
sale, receipt history and offer, and when does replacing them with a minimum
funding witness preserve the requested answer?

Comparator: the chapter's dated cash sequence: opening 12, wages 10 on day 3,
old debt plus coupon 32 on day 4, sale proceeds 15 times the sold fraction,
bridge principal a at day 4 with an upfront fee 1 and repayment a+1 on day 6,
receipt 18 on day 5 in H1 or day 9 in H2, and term debt at a supplied price q
on day 5 with fixed fee 2 and face cap 40. Preserve the separate inventory
covenant variant. Unknown real terms remain unknown.

Primary criterion: derive the complete nonnegative-cash action domain for each
fixed sale choice and offer-activation case, and check the formulas against
direct dated event arithmetic. Preserve failed sequences and their reasons.
Provide an exact counterexample where minimum financing loses a higher minimum
cash balance despite equal fees and terminal cash. Explain the objective and
information assumptions before any claim of optimality or finite enumeration.

Promotion vetoes: treating enumeration over sample amounts as continuous
completeness, charging a term fee when there is no issue, netting away an
intermediate shortfall, using H1/H2 before the actor observes it, or changing
offer/measurement assumptions. A failed identity triggers repair. Corrupted
baseline or the existing eight-hour deadline stops dependent work; a candidate
failure does not stop independent work. Case counts and clean builds are
explanatory only.

No optimal real-company financing, calibrated price, standards admission,
unrestricted policy completeness, stochastic superiority or production engine
will be claimed. Results are a conditional mathematical specification and
small deterministic documentary reference. Store them under
data/accounting-master/release-pursuit-20261027/refinancing-domain/.

## Plan and skeptical audit

1. Pin the exact selected chapter and retain its section 14.13 wording. Inspect
   existing reference evidence before adding a new calculation.
2. Write the domain in the chapter's notation: sold fraction z in {0,1/2,1},
   bridge amount a in (0,30], term amount b in [0,40], with no-issue and
   positive-issue cases separated. Derive cash immediately after each payment.
   State that q is supplied and positive, not endogenous in this calculation.
3. Check direct event arithmetic at boundary and interior amounts for the two
   receipt histories, supplied prices and covenant variants. Check the exact
   counterexample a=16 versus a=17 for full sale and H1 with no term issue.
   The continuous conclusion must follow from the written inequalities,
   not from the number of sampled rational cases.
4. Repair the reader-facing section in a protected successor. Preserve all old
   numerical examples and citations. Explain when finite enumeration is valid
   and when the continuous subproblem must remain. Read the complete repaired
   chapter, build both volumes and verify/reproduce the package before selection.

Default audit: fractional share of sale is restricted to three supplied offers,
not assumed continuously divisible. Financing quantities are continuous because
the text supplies caps but no denominations. Fixed fees and the absence of
interest depending on bridge amount are inherited illustrative terms, not
recommended finance defaults. Test their consequence early: bridge principal
cancels from day-6 cash while altering day-4 cash. Information is conditional
on a stated history; a policy across histories must separately enforce when
the receipt state becomes observable. A finer amount grid is only a hypothesis
about a different action domain, not a remedy for an unsupported finite claim.

The skeptical audit passes this bounded plan. It directly tests the written
action domain, preserves intermediate cash and separates feasibility from a
liquidity objective. The cheapest discriminating example is the two bridge
amounts above; no solver installation, stochastic sampling or long experiment
is needed. Arithmetic uses Python fractions on CPU; seeds are inapplicable.

Reader: a financially literate implementer. Entry knowledge is the offer
calendar, debt proceeds and covenant interaction. The open question is what
exactly may be enumerated. Exit understanding should distinguish a finite
contract choice, a continuous funding amount, a feasibility witness and an
optimal policy. The manuscript changes must preserve that distinction without
turning the chapter into a validation checklist.

## Pre-run timing refinement

The earlier teaching checker verifies the chapter's displayed arithmetic but
does not define a complete action domain. No retained generic enumeration
supports the finite claim. Reuse its facts and keep its accepted output intact.

The continuous domain also exposes a hidden same-day assumption. If a very
small term issue yields less cash than its fixed fee, settling it before the
day-5 receipt can create a temporary shortfall that disappears in a daily net
total. For the primary domain, specify that any day-5 receipt is credited
before B settles and that the fee is withheld atomically from proceeds. This
ordering is an explicit local comparison assumption, not a reported issuer
fact or a claim about the original offer. Add the opposite order as a separate
counterexample, with its extra cash-prefix constraint. Keep the choice of the
issue amount separate from the time the cash settles: observing the receipt
does not waive a notice period.

The corrected plan passes: every cash outflow has a prefix check, the new order
is declared, and a test will demonstrate why the assumption matters. No
continuous conclusion will be drawn solely from rational samples.

## Integration and reproducible example

The direct event checks and both counterexamples pass. Integrate the repaired
section into a protected 5.54-R2 successor of the exact 5.54-R1 package, retaining
all other sources. Supply a small standard-library companion that reruns this
conditional example in an explicitly new output directory; include a concise
expected-counterexample record and scope/readme. Check it with isolated Python
from a separate directory. This adds reproducible evidence for this new example
only and does not close the package's wider executable dependency queue.

The reader-facing repair names the continuous amount domain, initial/date and
same-day assumptions, the two cash identities and their sufficiency proof,
then distinguishes feasibility from minimum-cash optimization. Preserve the
old offer numbers, source citations and later conversion/accounting argument.
The unit remains a local mathematical derivation, not an imported new theorem.

## Rendered review repair

Attempt 01 builds and passes 428 preservation/build checks. The complete
chapter read found two small exposition defects: the no-sale branch adds zero
sale proceeds, so the sufficiency explanation should say nonnegative proceeds;
and the same-day counterexample joins its parameter list and conclusion with a
comma splice. Repair these sentences, preserve attempt 01 source/PDF bytes and
verification, then rebuild as attempt 02. No equation, example or assumption
changes. The exact arithmetic run remains accepted and is not repeated.
