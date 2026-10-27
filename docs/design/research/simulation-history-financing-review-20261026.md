# Alternative histories, financing decisions and company simulation

26 October 2026. Targeted response to the user's three simulation questions.

AccDSL should preserve multiple economic histories compatible with a company's
disclosures and carry each history into its conditional scenario results. A
journal belongs in each history, but a journal cannot hold all the information
needed to simulate the company. Debt terms, shareholder rights, asset vintages,
customer obligations and management decisions can differ even when historical
postings are identical. This distinction is already part of the mathematical
design; the remaining work is to make it govern the financing implementation.

## What should be reconstructed?

There are two distinct identification problems. First, reporting aggregates
transactions. With fixed reporting mappings, if observations satisfy y = Az
and Av = 0, both z and z + v give the same observations whenever both satisfy
the other evidence and admissibility restrictions. Second, even an exact
journal may omit contractual conditions that have not yet affected a payment.
A fixed loan and a floating loan can have identical issue and interest entries
until the floating rate resets. The existing mathematical chapter explicitly
derives both problems [R1].

The unit to retain is therefore a jointly consistent candidate history:

| Component | Why the simulator needs it |
|---|---|
| Opening economic and accounting state | Establish cash, lots, obligations and recognised balances before subsequent events |
| Dated economic events and journal entries | Explain historical movements and reconcile every relevant report |
| Outstanding contracts and security registers | Determine reset dates, maturity, seniority, conversion, ownership and dilution |
| Accounting basis and elections | Determine recognition, measurement, presentation and treatment changes |
| Evidence and unresolved quantities | Distinguish observed facts, compatible explanations and unsupported assumptions |
| Behavioural policy assumptions | Determine future borrowing, investment, issuance, dividends and distress responses |

Behavioural assumptions should remain separately addressable even if a run
binds them to a history. Historical records do not automatically identify how
management will react to a new shock. A historical factual ambiguity, a legally
permitted accounting choice and a future random event are different things.

Store these alternatives as shared records, linked choices and constraints;
materialise dated journals for selected feasible histories when executing.
The fixed/floating fraction can remain a continuous unknown. A few simulated
witnesses do not exhaust that family. Do not enumerate arbitrary balanced
journals: balance is necessary, while economic events, notes, maturity
disclosures, account roles and the selected accounting rules also constrain
admissibility. All statements and notes in the selected evidence package must
be considered, not just the balance sheet.

These are hypothetical reconstructions, not competing versions of the
company's actual legal books. Disclosure revisions need their own version
history. New evidence should restrict the candidate family while preserving
what was known at an earlier information date. The system must not claim to
have recovered the actual journal merely because one candidate reconciles.

For history h and scenario s, retain the conditional output law K(h,s). Without
defensible weights over histories, the result is the family of those laws. A
mixture requires a separate justified measure; the number of encodings or
solver witnesses gives no probabilities. The existing design supplies this
distinction and a query-specific equivalence relation [R1].

The full historical event trace can be archived without replaying it in every
forward simulation. Execution can share a sufficient opening state when that
state preserves all requested future outputs under the relevant policies,
scenarios and horizon. Equality of current statement totals is insufficient.
Changing the query or admitting a new contract event can invalidate an earlier
grouping. This also means that histories need not remain computationally
separate forever: retain their provenance while sharing genuinely equivalent
execution.

The repository's small example starts both branches with cash 95, debt 100 and
equity -5. A rate shock produces interest 5 in the fixed branch and 7 in the
floating branch, leaving cash 90 or 88. The historical statements and journals
do not decide between them [R2]. A stronger next example should combine rate
resets, maturity/refinancing and share rights under the same evidence.

## Financing needs three distinct models

The first is contractual: what the company has promised and what actions it is
allowed to take. The second is economic: what financing is available, what it
costs and what management chooses. The third is accounting: how executed
transactions and subsequent measurements enter the books.

The current design distinguishes these responsibilities. Its debt module
lists contractual dates, face/proceeds, resets, amortisation, seniority,
collateral, covenants, options and conversion, with separate accounting
measurements. Its equity module calls for a dated security register [R3].
The old company engine implements a much smaller demonstration: issuance
posts an entered amount to cash and debt, or shares times price to cash and
capital [R4].

Newer declared-financing code does more: it checks typed amounts and dates,
tracks debt memory, splits simple-interest accrual at financing boundaries,
and distinguishes dividends declared from payments. Its own prerequisites
explicitly exclude valuation and contract admission. Equity shares and price
are event inputs; the inspected method does not maintain a share register.
A separate compound-instrument example supplies a bounded issue/accrue/
redeem-or-convert lifecycle. These are useful components, not a general
financing choice, market-pricing or default model [R5].

For debt, keep promised repayment, cash proceeds, carrying amount, market
value and accrued interest separate. Also retain issue costs, coupon or
index/spread, payment dates, maturity, creditor priority, covenants, guarantees
and recovery terms. Distinguish interest expense from contractual coupon and
from cash settlement. A rate shock may affect future cash coupons, refinancing
costs or valuation differently depending on the instrument and measurement
basis.

For equity, distinguish book equity, economic equity value and the legal
securities held by shareholders. Under an explicitly stated simple share
issue with no simultaneous repurchase, gross proceeds E, issue price P > 0
and existing share count N:

    new shares = E/P
    closing shares = N + E/P
    net cash received = E - issue costs

An existing holder who does not subscribe retains N_old/(N + E/P) of the
post-issue shares, assuming a single class with equal rights. The price must
be supplied by a declared market/valuation/offer model; dividing book equity
by shares does not define a financing market. Multi-class rights, conversion,
repurchases and rights offers require their own rules.

A cash-raising target, a fixed share-issuance target and a capital-ratio target
give different management decisions after a price shock. The policy must name
which target applies, respect available facilities and authorisations, and
allow financing failure. Accounting should record the resulting transaction
under the selected basis. It must not create unlimited debt or equity to
remove a cash shortfall.

## A debt convention problem in the supplied note

The note correctly makes debt pricing, default and equity value mutually
dependent. However, its cash-flow and pricing equations use incompatible
meanings for the same b-prime under their stated common-contract interpretation.
The cash-flow equation raises b-prime/(1 + risky rate) now and subtracts the
inherited debt b due now; next period, b-prime becomes that inherited debt.
This treats b-prime as promised repayment. The pricing equation instead
treats b-prime as the amount advanced and b-prime times (1 + risky rate) as
the solvent repayment [R6].

This is not a transcription accusation. The retained December 2012
Strebulaev–Whited paper prints both conventions in equations (3.26) and (3.27),
printed pages 93–94; the latter was also inspected as a rendered page [S1].
An unrecorded redefinition could explain the display, but no such mapping
is supplied by the inspected passage. The paired equations are wrong relative
to the note's claim that they describe one consistently defined debt position.
Whether a corrected edition or erratum exists remains unchecked.

Use separate symbols to derive the cash flows. Let F > 0 be the amount
promised next period, P the lender's cash advance now, y the quoted yield,
D the next-period default indicator, and R the actual recovery paid in
default. For a one-period zero-coupon claim, without fees:

    P = F/(1 + y)
    lender payoff = (1 - D)F + DR

Under the explicitly assumed risk-neutral lender and constant risk-free rate r:

    P(1 + r) = E[(1 - D)F + DR | current information].

Substituting the first equality gives

    F(1 + r)/(1 + y) = E[(1 - D)F + DR | current information].

Multiplication by (1 + y), which is known at issuance, gives

    F(1 + r) = (1 + y) E[(1 - D)F + DR | current information].

The printed convention instead omits the factor (1 + y) on the recovery
term. Zero recovery or no default can conceal the discrepancy. Holding the
default probability at 10%, recovery at 40, face at 100 and risk-free rate at
5% gives expected payoff 94, proceeds 1880/21 (about 89.52381) and yield 11/94
(about 11.70213%). The printed equation implies yield 11/90 (about 12.22222%).
Using its implied proceeds with the stated face payoff leaves a lender
break-even residual of 44/101 (about 0.43564). These exact calculations are
retained in the diagnostic below. The probabilities are invented diagnostic
inputs, not estimates or branch weights.

Alternatively, define the state/control as the cash advanced and make promised
repayment equal to that advance times (1 + y). Then the cash-flow equation,
future liability state and recovery/default arguments must all be changed
consistently. Changing just the pricing equation is not sufficient to audit
the entire model, its derivatives or its numerical implementation.

For a general pricing model, replace the elementary break-even equation with
P = E[m((1 - D)F + DR) | information], using a declared stochastic discount
factor m, or an explicitly justified pricing measure. A real-world default
probability and risk-free discounting alone do not specify market risk premia.
Actual multi-creditor recovery must follow the admitted priority and legal
process, not automatically the aggregate recovery formula in this toy model.

Two other translations need care. First, the paper's §3.6 cash-flow equation
credits the present value of a future interest tax deduction at issuance;
the authors explicitly call this a simplifying timing assumption. AccDSL must
not post it as an actual cash tax receipt without a separately justified tax
event. Second, the generic external-financing cost eta(e) can represent the
cost to aggregate shareholders in a structural model. It does not determine
share counts, offer prices, ownership or jurisdiction-specific capital
postings. Those are additional accounting and security-register requirements,
not evidence that aggregate value models must always carry individual shares.

Limited liability likewise caps equityholder value, not book equity. Negative
book equity and economic default are distinct outcomes. A simulation must
specify liquidation, restructuring, ownership changes, unpaid obligations and
future operating status rather than simply setting every accounting balance
to zero when the value function reaches its default region.

## What the inspected literature contributes

| Literature and technical anchor | Relevant finding | Implication and limit for AccDSL |
|---|---|---|
| Giacomini–Kitagawa, retained April 2020 draft of the 2021 paper, §§2.1–2.3, Definitions 1–2, equations (2.2)–(2.4) [S2] | Observationally equivalent structural parameters can retain a conditional prior that the data cannot update; a class of priors yields lower and upper posterior probabilities. | Supports preserving unresolved alternatives and weight sensitivity. Equal fit to a finite report package is not by itself proof of observational equivalence for every possible dataset; the paper does not reconstruct company journals. |
| Shahnazarian (2004), §§2.3–2.8, especially (2.23)–(2.28); retained earlier review also covers behavioural equations [S3] | Stock movements relate new debt and repayments, investment, disposals and depreciation; behavioural assumptions supply additional choices. | Accounting bridges constrain histories but do not determine borrowing or investment. Swedish tax/data assumptions are not transferable defaults. |
| Pierson (2020), §§3.3–3.5 and retained author model [S4] | Accrual/payment stocks and discrete reporting differ; equity includes a share count. The source itself calls for replacing its simple debt-delay structure in an operational financing model. | Preserve dates and security quantities; use a real contract schedule for instrument detail. Reporting consistency alone supplies no financing-market model. |
| Caiani et al. (2016), §§2.1, 3.1.3, 5.2, Appendices A/B; retained official-code inspection [S5] | Agent transactions, loan/vintage state and within-period ordering are distinct from behavioural rules and accounting checks. | Preserve counterparties and event ordering. The source's OCF includes loan principal repayments and cannot silently become statement operating cash flow. |
| Strebulaev–Whited (2012), §§3.4–3.6, especially (3.26)–(3.28) [S1] | Financing decisions, default and loan pricing depend on the firm's state; pricing and equity value interact. | Useful economic model structure. Reconcile the printed debt convention and tax timing before implementation; aggregate net debt loses distinctions relevant to real contracts. |
| Maliar–Maliar–Winant (2021), §§2.3–2.4, Definitions 2.6–2.9, Algorithm 1 and constrained example §4 [S6] | Neural approximations can solve specified Bellman/Euler/lifetime objectives with explicitly handled expectations and constraints. | A solver begins after the economic model is specified. Low training loss does not identify a historical journal or supply missing accounting semantics. |
| Duarte–Fonseca (May 2026 working paper), §§2.1.3–2.1.5, 3; Appendices A.3.4 and A.5 [S7] | One-period bond prices and equity value are solved jointly; issuance costs depend on subperiod financing needs. A lagged value network is used for pricing during training, followed by grid refinement. | Useful candidate numerical organisation. Its default conditions, recovery, units and tax-adjusted pricing differ from the lecture model; it is not a drop-in implementation. A.5's local grid search is not an independently checked global-optimality guarantee. |

The synthesis is architectural, not a theorem that one simulator is best.
Preserve what is known and unresolved; specify behaviour and contracts;
generate economic events; apply accounting; then aggregate reports. Contract
libraries such as ACTUS can contribute schedules and payoffs, but the retained
interface investigation does not establish a matched executable accounting
adapter or a management policy [R7].

## Recommended next work

1. Implement an end-to-end history-family case on the existing shared IR.
   Preserve continuous/discrete alternatives, evidence dates, shared unknowns
   and the same historical financial statements; retain divergent future
   journals and statements after rate and liquidity shocks.
2. Extend the financing state with instrument/tranche records and a dated
   equity security register. Reuse checked event clocks and atomic postings.
   Distinguish face, proceeds and accounting measurement from the outset.
3. Add an explicit, initially exogenous funding policy with available
   facilities, limits, refinancing decisions and issuance targets. Test a
   cash shortfall that remains a financing failure.
4. Add a small, independently checked risky-debt/default pricing model with
   the debt convention fixed. Keep economic default and numerical failure
   separate. Compare alternative feasible actions at nonsmooth boundaries.
5. Evaluate a neural solver only when that benchmark and the event/accounting
   translation are established. Training-distribution coverage, default-boundary
   checks, held-out pricing, policy checks and downstream reports must be part
   of the target-specific evidence contract.

Acceptance examples should include identical historical postings with different
future resets; refinancing unavailable at maturity; proceeds different from
promised repayment; equity issuance after a price shock; fees paid at actual
dates; and default with retained obligations and specified recovery. General
history reconstruction or whole-company forecast validity remains open.

## References and repository anchors

- R1: [mathematical history/state/probability design](../chapters/05-mathematics.tex), historical compatibility, event simulation, sets/distributions and resolution sections.
- R2: [execution chapter](../chapters/07-execution.tex), identical-history/different-future and financing examples.
- R3: [debt and equity modules](../chapters/08-modules.tex), debt contract/accounting layers and equity register.
- R4: [bounded company engine](../../../scripts/company_execution_v1.py), Engine.apply, issuance branches.
- R5: [declared financing methods](../../../scripts/declared_financing_methods_v1.py), [schedules](../../../scripts/declared_financing_schedules_v1.py), and [compound financing example](../../../scripts/corporate_financing_v1.py).
- R6: [user's note](/home/chakwong/python/MathDevMCP/docs/risky-debt-maliar-deep-learning-lecture-note.tex), risky-cash-flow and risky-pricing equations; original source unchanged.
- R7: [existing simulator survey](financial-statement-simulator-survey-20261023.md), [ACTUS comparison](actus-interface-boundary-20261023.md), and [equations/events synthesis](simulator-equations-and-events-20261025.md).
- S1: [Strebulaev and Whited (December 2012 version)](../../papers/Dynamic%20Models%20and%20Structural%20Estimation%20in%20Corporate%20Finance%20Strebulaev%20%282012%29.pdf).
- S2: [Giacomini and Kitagawa (2021; retained 2020 draft)](../../papers/Robust%20Bayesian%20Inference%20for%20Set‐Identified%20Models%20Giacomini%20%282021%29.pdf).
- S3: [Shahnazarian (2004)](../../papers/A%20Dynamic%20Microeconometric%20Simulation%20Model%20for%20Incorporated%20Businesses%20Shahnazarian%20%282004%29.pdf).
- S4: [Pierson (2020)](../../papers/Operationalizing%20Accounting%20Reporting%20in%20System%20Dynamics%20Models%20Pierson%20%282020%29.pdf).
- S5: [Caiani et al. (2016)](../../papers/Agent%20based-stock%20flow%20consistent%20macroeconomics%20Towards%20a%20benchmark%20model%20Caiani%20%282016%29.pdf); technical/source-code review retained in R7.
- S6: [Maliar, Maliar and Winant (2021)](../../papers/Deep%20learning%20for%20solving%20dynamic%20economic%20models%20Maliar%20%282021%29.pdf).
- S7: [Duarte and Fonseca (May 2026)](../../papers/AI%20for%20Structural%20Estimation%20Duarte%20%282026%29.pdf).

The [execution/source record](../../../data/accounting-master/simulation-history-financing-review-20261026/result.md) separates checked derivations, inspected editions and remaining source gaps.
