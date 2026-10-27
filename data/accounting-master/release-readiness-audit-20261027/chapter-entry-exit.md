# Chapter opening and ending inventory

Current audit cutoff: 5.50. These excerpts are not continuous chapter review.

## 1. The same statements can describe different companies

simulation/01-observations.tex

### Opening

\chapter[Different companies, identical statements]{The same statements can describe different companies}
\label{sim:observations}

A financial statement describes selected consequences of a company's activities. A simulation must explain how those consequences can change. These are different tasks. A balance of borrowing tells us how much debt is reported under a particular measurement basis and date. It does not, by itself, tell us when debt resets, who may demand repayment, which assets secure it, or whether management can replace it. Two companies can report the same debt and interest expense and respond very differently to the same increase in market rates. Recovering one plausible journal does not solve this problem. Even a complete journal may omit the contractual fact that determines the response.

This part develops a representation of companies for which evidence is incomplete. Its purpose is useful conditional simulation without concealing what the evidence leaves unresolved. The numerical examples are synthetic teaching cases, not estimates of actual company exposures. They make a distinction visible: a calculation can be internally exact while its interpretation remains conditional on an unverified assumption.

\section{A rate shock exposes the missing information}
Consider a company with cash of 95 and debt of 100 at the forecast origin. Its recent annual interest expense was 5. Suppose debt was outstanding throughout that year, interest was paid when accrued, there were no fees or derivatives, and carrying amount equalled principal. A five per cent fixed-rate loan fits these observations. So does a floating-rate loan whose reference rate plus spread happened to equal five per cent. A mixture fits as well.

Let $\alpha$ be the floating fraction of principal. Assume a two-percentage-point increase applies to that portion for the entire next year, with no cap, floor, maturity or hedge. Next year's interest payment is
\begin{align}
 I(\alpha)&=100(0.05)(1-\alpha)+100(0.07)\alpha\\
 &=5+2\alpha,\qquad 0\leq\alpha\leq1.\label{sim:interest-family}
\end{align}
The two terms are payments on fixed and floating portions. Historical observations admit every value of $\alpha$ in the interval. They imply interest between 5 and 7 under the shock, but supply no frequency distribution within that range. Uniform weights would be an additional judgment.

If interest is the only cash payment, closing cash is
\begin{equation}
 C(\alpha)=95-I(\alpha)=90-2\alpha.\label{sim:cash-family}

### Ending


\citet{shahnazarian2004} separates financial identities from behavioral relationships. \citet{caiani2016} specifies action sequences and financial counterparts in an agent-based economy. These approaches motivate separate accounting and behavior, but do not supply a universally transferable issuer policy. Responses must be estimated, supplied, bounded or left unresolved.

An output can distinguish historical explanations from future policies. One result may assume a floating share between 20 and 40 per cent and existing facilities only; another admits a stated refinancing offer. Averaging these without justified weights erases the question being answered. Conditional results remain informative even when an unconditional forecast is unavailable.

\section{Trees are explanations, not compulsory storage}
A tree displays mutually exclusive events, information arrival and subsequent decisions. It is useful for a small example. The continuum $\alpha\in[0,1]$ already contains infinitely many compatible companies, so a finite selection of branches is generally an approximation. An interval and symbolic formula can represent the same uncertainty more faithfully and compactly.

Branches must not imply that a signed contract is redrawn each year. Fixed versus floating may be a persistent unknown fact. Future demand may instead generate fresh realizations under a declared stochastic process. A model must preserve the distinction.

Sometimes a formula suffices; sometimes a split at a covenant threshold is needed; sometimes filtering a probability distribution is justified. In difficult cases the result must retain an unresolved region or bounded approximation. None of these choices requires a separate stored company for every imaginable world.

\section{A useful simulation explains its dependence}
For each result a reader should be able to identify its evidence, remaining histories, contractual and behavioral assumptions, and computational status. Balancing a projected balance sheet is weaker than this requirement. The model must explain why cash is available, why a payment occurs and what changes the answer.

The remainder of this part develops reconstruction, learning, scenarios, financing, accounting transitions and tractable computation. Failure cases accompany the mechanisms they test. Their purpose is to expose a specific mistaken inference and its repair, not to imply that a finite catalogue anticipates every future error.

## 2. Reconstructing joint admissible histories

simulation/02-reconstruction.tex

### Opening

\chapter[Reconstructing joint histories]{Reconstructing joint admissible histories}
\label{sim:reconstruction}

The useful starting point for simulation is a description of what the evidence permits. That description must connect opening balances, transactions, closing balances, notes and contractual facts across time. Without these links, individually plausible entries can be jointly impossible. With unjustifiably strong links, the model can exclude real alternatives because an analyst supplied a convenient default. Reconstruction is consequently both an accounting problem and an inference problem.

\section{An observation has a context}
A reported amount comes with a concept, entity or consolidated group, period, units, measurement basis and precision. Cash at a date differs from cash generated during a quarter. Continuing operations differ from the whole group. Millions differ from currency units. These distinctions determine which equations may use the number; they are not annotations that can be restored after arithmetic.

Let observation $o_i$ contain value $y_i$, context $c_i$, publication time $p_i$ and source location $\ell_i$. A reconstruction predicts $g_i(h,b;c_i)$ from history $h$ and accounting interpretation $b$. If the source rounds to increment $d_i$ using a declared rule, compatibility may take the form
\begin{equation}
 y_i-\frac{d_i}{2}\leq g_i(h,b;c_i)<y_i+\frac{d_i}{2}.
 \label{sim:rounding}
\end{equation}
The half-open endpoint is justified only by the assumed rounding convention. Other tie-breaking rules, signs and reporting practices require a different observation set. The printed absence of decimal places does not establish an exact underlying value.

A debt balance reported as 100 million might therefore permit nearby amounts. A difference of 0.4 million may be immaterial for a broad exposure chart and decisive for a covenant lying inside the reporting interval. Precision should survive extraction so that the query can determine whether it matters. An arbitrary numerical tolerance chosen for solver convenience is different from reporting precision. The first controls computation; the second describes evidence.

\section{Stocks constrain net movement}
For opening balance $B_0$, signed movements $m_k$ and closing balance $B_1$, the stock-flow identity is
\begin{equation}

### Ending


A practical sequence is to construct the important joint constraints, locate uncertainty crossing a decision threshold, and inspect sources capable of resolving it. The source may not exist or may remain inaccessible. The process still identifies the economic consequence of the gap and prevents extraction volume from being mistaken for identification.

\section{Provenance and multiplicity}
Two records can support the same assertion, and one record can support several constraints. Provenance needs to preserve these distinctions without treating duplicate records as additional worlds. The semiring treatment in \citet{green2007} concerns algebraic provenance for database queries; its value here is a disciplined account of how source contributions combine. It is not a probability assignment to economic histories.

If a source is withdrawn, a derived claim supported by another independent source may survive. If the withdrawn source supplied the only premise for a maturity date, the maturity should become unresolved. Recomputing only displayed totals can miss the effect on future liquidity. Dependencies should extend through contract state and policy eligibility to scenario results.

A stable identity for an economic fact is also different from the identity of a particular source assertion. Two filings can refer to the same loan with different labels. Merging them solely because the labels resemble each other risks combining different facilities; failing to merge verified duplicates can double debt. Entity and instrument reconciliation therefore needs evidence and reversible decisions.

\section{A method proposal for AccDSL}
The proposed reconstruction service accepts an evidence view, a declared domain and an assumption set. It returns a persistent constraint family, its known contradictions or unresolved mappings, and optional witnesses. Queries request possible outcomes, certain conclusions, bounds or distributions under separately admitted measures. A request for one witness should not trigger exhaustive enumeration.

Constraints should be grouped by their source and economic role. Observation intervals and unit conversions can often be checked before expensive solving. Linear bridges and discrete interpretation choices can then be combined, with nonlinear valuation isolated when possible. If a nonlinear method is needed, its completion status remains distinct from the accounting identities it evaluates.

The service should preserve both a stable source snapshot and a reusable symbolic family. A later disclosure can produce a refined version without overwriting the earlier one. A scenario uses a particular version and records which assumptions it adds. This is a concrete way to carry multiple possible journals and economic histories without creating a full independent database for each possibility.

## 3. Learning, persistent uncertainty, and who knows what

simulation/03-learning.tex

### Opening

\chapter[Learning and persistent uncertainty]{Learning, persistent uncertainty, and who knows what}
\label{sim:learning}

A future disclosure may resolve an uncertainty about today's company. It may also reveal nothing relevant. Simulation must allow both outcomes. It must distinguish a change in the company from a change in the analyst's knowledge, and distinguish the analyst's knowledge from information available to managers, lenders and investors. These distinctions determine which actions are possible and which apparent forecasting successes are merely uses of future information.

\section{Four dates attached to one fact}
A loan can be signed on 15 January, take economic effect on 1 February, appear in a report covering the quarter ending 31 March, and become public on 10 May. A system may ingest the report on 12 May. The signature, economic, reporting, publication and ingestion dates answer different questions. A forecast made on 30 April cannot use the 10 May disclosure simply because it describes a March balance.

For a report-based forecast origin $t$, let $D_t$ contain assertions available by $t$ under the declared availability rule. If the analysis uses public information, publication time is relevant. If it models a lender with private contractual access, the information rule differs. Ingestion time controls reproducibility of the system's own operation; it need not equal the earliest public availability.

A historical replay should therefore specify both the economic date and evidence cutoff. A corrected extraction performed today may accurately recover a number that was publicly available before the old cutoff. A new restatement published today was not available then. The first can repair a data-processing mistake in an old evidence view; the second changes the information set and must not be silently backfilled into the old forecast.

\section{Persistent unknown facts}
Let $\theta$ denote a contract characteristic fixed at inception, such as whether a loan is fixed or floating. Let $X_t$ denote changing economic state, including cash, accrued interest and remaining principal. A simple transition is
\begin{equation}
 X_{t+1}=T(X_t,\theta,a_t,\varepsilon_{t+1}),\qquad \theta_{t+1}=\theta_t.
 \label{sim:persistent-theta}
\end{equation}
Here $a_t$ is a decision and $\varepsilon_{t+1}$ a future innovation under the specified scenario or stochastic process. The second equation is essential. Uncertainty about a fixed contract does not license redrawing it each period. Refinancing or amendment can change the terms, but those are dated events with their own permissions and cash consequences.


### Ending

its causal effect. Actual actor access, registry completeness, instrument
terms and feasible financing still need evidence.

\section{A proposed information service}
AccDSL should represent evidence views and actor information views separately. An evidence view selects actual assertions by availability, revision and scope. An actor view specifies observable state variables, private contractual facts and signal channels at each decision date. Policies receive only that view and permitted memory.

Forward execution first applies events available at the current boundary, constructs observations, updates the relevant information state, and then permits decisions according to the stated timing. Alternative orderings are possible, but they must be explicit and tested. Moving a decision across an observation boundary changes the economic problem.

The service should refuse ambiguous timing where it affects the answer. It can still return a conditional comparison of both orderings. Such a comparison is preferable to silently selecting whichever ordering makes the simulation easier. Exact timestamps, time zones and publication lags matter when events occur on the same calendar date.

\section{Tests that discriminate information errors}
A useful test duplicates a world, changes an unobserved future shock and confirms that the current action remains unchanged. Another changes a privately known contract term and confirms that an informed manager's policy may change while a public analyst's evidence view does not. A third inserts a later restatement and checks that an earlier frozen forecast remains reproducible.

These are semantic tests. They do not require a fitted behavioral model. They establish that information restrictions are implemented as specified. Whether a particular manager actually follows the chosen policy is a separate empirical question. Keeping that distinction prevents a passing information test from being presented as behavioral validation.

A final test removes all informative observations and confirms that persistent uncertainty remains. A system that gradually collapses to a single history merely because a particle filter resampled or an optimizer selected one witness has confused computational concentration with evidence. The retained family and the approximation used for calculation must remain distinguishable.

## 4. Scenarios, interventions, and feasible decisions

simulation/04-scenarios.tex

### Opening

\chapter[Scenarios and feasible decisions]{Scenarios, interventions, and feasible decisions}
\label{sim:scenarios}

A scenario is a specified change to a model, not merely a new column of forecast numbers. It must say what changes, what remains structurally linked, what actors observe and how they may respond. A rate increase imposed on a contract schedule differs from conditioning an empirical model on periods when rates were high. A revenue decline with unchanged prices differs from one caused by price reductions. These distinctions determine the cash flows and the meaning of the result.

\section{Describe the experiment before calculating it}
A scenario request should identify the forecast origin, horizon, evidence view, shock variables, shock timing, transition rules, management policy and requested outputs. It should also specify whether the shock is a deterministic path, a random process or an ambiguity set. A phrase such as ``rates up 200 basis points'' leaves reset dates, currency curves, spread behavior and duration unresolved.

For a deterministic scenario $s$, let $u_t(s)$ be the imposed external path. The company evolves as
\begin{equation}
 X_{t+1}=T_t(X_t,\theta,a_t,u_{t+1}(s)),\qquad a_t=\pi_t(I_t).
 \label{sim:scenario-transition}
\end{equation}
The transition includes contractual events and operational behavior. The policy uses information available at its decision time. A statement projection is then a reporting map of the resulting events and states. Directly shocking a reported total can be a useful reduced-form approximation, but it requires an explanation of how the corresponding events and balances are reconstructed.

A scenario can also specify a set $\mathcal S$ of paths. The outcome family becomes
\begin{equation}
 \mathcal Y=\{F(h,s,\pi):h\in\mathcal H, s\in\mathcal S, \pi\in\Pi\}.
\end{equation}
This expression is not automatically a Cartesian product of arbitrary histories, shocks and policies. Feasibility may couple them. A lender's offer can depend on the company's contract state; a commodity shock can affect both sales and collateral; a policy may be admissible only for certain information states. These dependencies must remain in the defining relation.

### Ending


The model can retain two guarded regions without enumerating individual values. The breach region then triggers whatever cure, waiver or acceleration rules the contract specifies. It does not automatically trigger liquidation. An unresolved guard is a reason to preserve conditional outcomes or refine the family, not to choose the midpoint and declare compliance.

\section{Scenario comparison as a decision aid}
A useful comparison reports which conclusions hold across histories, which depend on a particular contract assumption and which depend on a policy. For instance, a rate increase may raise interest for every floating exposure but reduce the value of a fixed-rate liability under a separate valuation basis. These are different quantities and can move in different directions.

The result should separate cash liquidity, book income, book equity, market value and contractual compliance. A positive accounting profit does not guarantee payment capacity; a market-value loss does not necessarily cause an immediate cash outflow. Combining them into an unnamed risk score makes the mechanism difficult to audit.

A proposed dashboard can show a conditional envelope with witness histories at important boundaries and a list of assumptions that change the conclusion. The envelope should retain joint outcomes and timing. A worst cash value at one date and a worst debt value at another may come from different paths; presenting them as one path would mislead.

\section{Scenario failures and repairs}
A scenario can fail because its shock is underspecified, because the model omits an exposure, because behavior uses future information, because financing is infeasible, because the numerical calculation fails, or because the economic assumptions are outside their domain. These failures require different remedies. More Monte Carlo paths cannot repair an omitted contract or an information violation. A more detailed journal cannot repair an unidentified behavioral response.

AccDSL should therefore return a typed result: completed conditional simulation, unresolved history region, unsupported mechanism, infeasible action, economic distress event, or numerical failure. A run may contain several statuses across different regions. Dropping failed regions and renormalizing successful ones changes the target distribution and can systematically remove the worst outcomes.

The next chapters make the financing mechanisms explicit. Debt and equity are especially consequential because they can appear to solve every cash shortage if issuance is represented only as a balancing entry. Their economic terms, counterparties, timing and rights must determine whether the entry may occur.

## 5. Debt is a dated contract, not a balancing amount

simulation/05-debt.tex

### Opening

\chapter[Debt contracts and financing]{Debt is a dated contract, not a balancing amount}
\label{sim:debt}

Debt issuance joins a cash transaction today to promises about future payments and creditor rights. A journal can record proceeds and a liability without describing those promises. A structural model can describe the promises without supplying the accounting measurement. Scenario simulation needs both, together with a financing policy and a model of whether counterparties accept the proposed issue. Confusing these layers can make a company appear liquid while its funding equation is economically inconsistent.

\section{Five amounts that should not share one symbol}
For a debt instrument distinguish face or promised payment $F$, gross proceeds $P$, net cash received $P-f$ after issuance costs $f$, accounting carrying amount $B$, and market value $V_D$. They may coincide in a simple par loan at inception. They need not coincide for discounted debt, transaction costs, accrued interest, modifications or subsequent market changes.

The gross contractual promise is relevant to redemption. Net cash is relevant to liquidity. Carrying amount is relevant to the balance sheet under the selected basis. Market value is relevant to valuation or repurchase. A debt-to-equity covenant may use yet another defined measure. Reusing one variable called debt for all of these quantities creates errors that can remain hidden in a par, no-fee example.

A debt record also needs currency, lender, borrower, issue and settlement dates, maturity, coupon or reset rule, day count, amortization, seniority, collateral, covenants, options and modification rights. Unknown terms remain unknown. A model can support a bounded profile without implementing every clause, but its unsupported terms must not silently default to benign values.

\section{The one-period pricing equation}
Consider a loan issued at date zero and settled at date one. Let $D$ be the date-one default indicator. If there is no default, the lender receives promised amount $F$. If default occurs, the lender receives actual recovery $R$, measured in date-one currency units. Let $r$ be a risk-free one-period rate. Under the illustrative assumption that discounting the expected payoff at $r$ is appropriate, lender break-even is
\begin{equation}
 P(1+r)=\mathbb E[(1-D)F+DR].
 \label{sim:debt-pricing}
\end{equation}
This equation is a pricing assumption for the example. Under physical probabilities, discounting at a risk-free rate requires an appropriate risk-neutrality or pricing justification. More generally, with stochastic discount factor $M$,
\begin{equation}

### Ending

when a consolidated closing statement appears fully funded.

The typed conditional implementation translates the retained examples and
records selected findings through the common monetary and memory engine.
An unresolved finding produces no successor state. Recording a known finding
changes no cash, carrying amount, shares or historical missed amount. This
establishes a limited representation and execution result. Multiple concurrent
clauses, the full instruments, actual notices and amendments, and the economic
consequences of acceleration still require their own admitted methods.

\section{Implementation proposal}
The debt module should maintain immutable contract versions, a dated obligation schedule, current economic state and separate accounting measurements. Events include issue, draw, reset, accrue, coupon, amortize, redeem, amend, breach, cure, accelerate, restructure and recover. Each event has preconditions, amounts, dates and successor state.

Existing repository methods already cover bounded issue, accrual, coupon, redemption and conversion calculations, and newer declared methods preserve timing and debt memory. They are useful foundations. They do not by themselves establish a general pricing model, market capacity, legal default process or complete instrument admission. The extension should compose with their checked boundaries rather than describe those capabilities as absent.

The smallest discriminating financing fixture should include proceeds different from face, positive recovery, a fee paid at issuance, a maturity shortfall and an unavailable refinancing offer. A second fixture should add two creditors with priority and delayed recovery. A third should test unknown rate terms and a covenant boundary. Passing these checks establishes the specified mechanics; empirical pricing validity and legal applicability require separate evidence.

## 6. Equity funding, ownership, and dilution

simulation/06-equity.tex

### Opening

\chapter[Equity and ownership]{Equity funding, ownership, and dilution}
\label{sim:equity}

An equity issue can provide cash while changing ownership and future claims. A model that records only an increase in cash and book equity captures one accounting consequence but misses the allocation of control and value. A structural model that charges an issuance cost captures a financing friction but does not automatically create a share register. Scenario simulation needs quantities, prices, rights, holders and dates, together with an explanation of who is willing to subscribe.

\section{Book equity, market value and share capital}
Book equity is the residual of recognized assets and liabilities under an accounting basis. Market equity value is the value assigned to owners' economic claims. Legal share capital is a legally defined component of capital that may be related to nominal share values. These quantities have different meanings. Dividing book equity by shares produces book value per share, not automatically the market subscription price.

A company can have positive book equity and insufficient cash to pay a maturity. It can have negative book equity and valuable future opportunities. Limited liability can bound the value of a shareholder's claim below by zero in a model without forcing the accounting residual to zero. The simulator should retain these quantities separately and define any relation between them.

Let $N$ be the number of existing ordinary shares, $V_E$ the total economic value assigned to their claim, and $p=V_E/N$ a per-share value when shares are homogeneous and $N>0$. This division presumes that $V_E$ refers to exactly that class. If preferred shares, options or noncontrolling interests are included in total equity value, allocating all of it to ordinary shares is wrong.

\section{A simple cash issue}
Suppose the company issues $n$ new homogeneous ordinary shares at subscription price $p_s>0$. Gross proceeds are $G=np_s$. If cash issuance costs are $f$, net cash is $G-f$. With no simultaneous repurchase or conversion, the post-issue count is
\begin{equation}
 N^+=N+n=N+\frac{G}{p_s}.
 \label{sim:share-issue}
\end{equation}
An existing holder with $n_i$ shares has ownership fraction $n_i/N$ before and $n_i/(N+n)$ after the issue, assuming that holder does not subscribe. This is percentage dilution. Its economic consequence depends on the price received and the use of the proceeds.


### Ending


If management can defer 10 of the payment at a cost, the capped issue may become feasible. That is a different policy and contract path, with future obligations. If a shareholder loan supplies the missing 5, it creates debt and related rights. The model should show these alternatives explicitly rather than use a generic balancing source.

\section{Proposed register and execution methods}
A dated security register should identify issuer, class, units, holder or holder category, rights, issue price where relevant, subscription and settlement state, and links to conversion or cancellation events. Outstanding, authorized, treasury and potentially issuable units should be distinct. Changes should reconcile through events.

An equity-financing method should accept a funding request, eligible offers, authorization limits and actor policy. It returns an accepted transaction or a shortfall. The transaction then produces cash, ownership and accounting events. Price formation may be supplied or solved by a separate model; the result records which.

The repository's simple shares-times-price postings and bounded capital events are useful components. The proposed extension adds offer feasibility, class rights and ownership evolution. It should reuse existing atomic posting and timing checks while adding negative cases: zero or negative subscription price, unsupported class, duplicate settlement, insufficient authorization, failed subscription and inconsistent conversion.

\section{What the equity checks establish}
Conservation checks can establish that cash equals settled subscriptions less costs and that share movements reconcile. Waterfall checks can establish that distributions do not exceed available value under the assumed priority rules. Timing checks can establish that ownership changes occur at the declared event date.

These checks do not establish that an issue price is fair, that investors will subscribe, that a legal approval is valid or that management will choose the modeled action. Those claims need their own evidence. The simulator should be able to give useful conditional calculations while keeping these unresolved questions visible.

A useful adversarial fixture issues shares below an assumed pre-issue value, then compares percentage dilution with wealth transfer. Another changes the price while holding funding need fixed and tests an authorization cap. A third combines conversion and redemption to ensure that the same obligation is settled once. These examples expose mistakes hidden by a simple par issuance with unlimited demand.

## 7. From economic events to coherent statements

simulation/07-events.tex

### Opening

\chapter[Events and financial statements]{From economic events to coherent statements}
\label{sim:events}

A scenario produces a sequence of events. Financial statements summarize selected consequences of those events under a reporting basis. Keeping this direction explicit makes it possible to ask whether an output follows from a plausible company history. Starting with independently forecast statement lines and inserting a balancing amount reverses the logic: it can make the accounts add up while leaving the economic transaction unexplained.

\section{An event carries more than an amount}
An event identifies actors, instrument or resource, effective time, settlement time, currency, quantity, conditions and provenance. A sale can transfer goods today, be recognized under a specified rule today, and be collected next month. A loan draw can be approved today and settle tomorrow. A derivative can change value without an immediate cash transfer.

The event layer should therefore represent economic occurrence separately from recognition, measurement and payment. The accounting layer maps admitted events and estimates to postings. The reporting layer aggregates postings into statements. The mapping may create noncash movements, and some economically relevant commitments may be disclosed without a current journal amount.

\citet[Sections 3.3--3.5]{pierson2020} explicitly separates accrual, payment and reporting accumulation in a system-dynamics setting. Its simple debt-delay mechanism is acknowledged as limited. The lesson for AccDSL is the separation of clocks, not the adoption of that simplified debt mechanism as a general contract engine.

\section{A credit sale and collection}
Consider a synthetic sale of goods for 30, with inventory cost 18, recognized at delivery and collected later. Ignore tax, returns and credit impairment for this illustration. At delivery, the postings are a debit to receivables and credit to revenue of 30, and a debit to cost of sales and credit to inventory of 18. Cash has not increased.

At collection, cash increases by 30 and receivables decrease by 30. Revenue is not recognized again. The two events explain why profit and operating cash can differ during the interval. A scenario that delays collection changes receivables and liquidity even if recognized revenue is unchanged.

If the sale is instead prepaid, receipt creates a different sequence under the selected recognition rule. The same annual revenue and cash collection can conceal different within-year funding needs. An annual-only model can be adequate for some questions, but it cannot claim to resolve a monthly liquidity trough that its time aggregation removes.

\section{Balanced entries are necessary, not sufficient}

### Ending


For example, cash 10, a receipt of 20 and payment of 25 produce closing cash 5 regardless of order. If payment comes first and no overdraft is permitted, the path is infeasible despite the positive closing balance. A minimum-cash query requires the event sequence. A closing-balance query alone would not detect the problem.

\section{Stock-flow consistency across counterparties}
When several entities are modeled, a payment by one is a receipt by another, subject to fees, taxes and timing. Keeping counterpart links helps detect money creation or disappearance. In an external-counterparty boundary, the system can record the flow leaving the modeled domain rather than pretending the counterparty does not exist.

The stock-flow consistent approach in \citet{caiani2016} gives a useful example of explicit sectors and transaction sequence. Its named cash-flow measures must be interpreted in its own definitions: a quantity called operating cash flow in that model subtracts principal repayments and should not automatically be mapped to an accounting statement category. Reusing labels without inspecting definitions is a semantic error.

AccDSL should therefore give each reported or derived quantity a definition and units. A label match is a candidate mapping, not proof of equivalence. This is especially important when connecting economic simulators, accounting standards and regulatory templates.

\section{A coherent event-to-report method}
The proposed method first admits an economic event under its contractual and behavioral premises. It updates quantities, rights and obligations. It then invokes the accounting rule for the declared basis and context, validates the posting bundle, and updates report accumulators. Source and scenario provenance accompany each stage.

At reporting boundaries, the system reconciles opening balances, movements and closing balances, checks units and perimeter, and preserves unresolved amounts or conditional interpretations. It does not force an unsupported movement into a generic other line merely to close the statement. A residual can be displayed as a diagnostic requiring explanation.

This sequence supports both concrete witnesses and symbolic families. If every member of a region has the same event rule, amounts can remain symbolic. If a guard changes the rule, the region must split or retain a piecewise expression. Accounting coherence then applies within every admissible branch, not just to an average statement that no individual history produces.

## 8. Keeping uncertainty without enumerating every world

simulation/08-compression.tex

### Opening

\chapter[Compact uncertainty]{Keeping uncertainty without enumerating every world}
\label{sim:compression}

Twenty binary unknowns have more than a million assignments. A company can have thousands of contracts, continuous unknown amounts and decades of possible events. Explicit enumeration is therefore an unsuitable default. The alternative is to represent the family and compute the answer demanded by a question. This can save enormous work, but cannot guarantee that every problem has a small exact solution.

\section{Representation size and answer size}
A formula containing twenty Boolean variables can describe all $2^{20}$ assignments without listing them. A solver may answer whether any assignment violates a cash constraint without printing every world. If the user asks for all distinct journals, the output itself can be enormous. No representation can print an exponentially large answer in fixed small space.

Continuous uncertainty sharpens the distinction. The family $0\leq\alpha\leq1$ has infinitely many members, but interest $5+2\alpha$ is a finite exact answer. Useful computations include symbolic propagation, optimization over a region and classification of regions by behavior. Enumeration is one method, not the definition of correctness.

\citet{darwiche2002} compares knowledge-compilation languages by succinctness and supported queries and transformations. Its definitions of directed acyclic representations, decomposability and determinism explain why sharing and structural restrictions help. Its tradeoffs also warn against assuming that a compact formula makes every query cheap. Compilation can itself be expensive.

\section{Three different graphs}
An evidence graph links assertions to sources and interpretations. A constraint graph links variables through relations. An execution graph links states through dated events. Their edges have different meanings. Source support is not causation; a constraint edge is not a probabilistic independence statement.

An expression DAG can share a repeated discount factor or subtotal. An immutable history graph can share common event prefixes. A transition graph can merge states only when relevant future behavior is equivalent. Confusing these forms of sharing can turn an engineering optimization into an unjustified economic assumption.

Economic feedback may remain cyclic while expression storage is acyclic. Debt price and investment policy can be simultaneous unknowns. An acyclic residual evaluator does not eliminate the fixed-point problem. The representation and solution method answer different questions.

\section{Share common structure without merging worlds}

### Ending


Provenance remains separate even when computations are shared. Two sources supporting one fact need not duplicate arithmetic, but their independent support matters if one is withdrawn. Execution identity must not replace source identity.

\section{Trees as selected explanations}
A small tree is useful for showing information arrival, choices and counterexamples. It can be generated from the symbolic family for a question. Nodes should identify whether they are exact worlds, samples, regions or hypothetical observations.

A representative tree is not exhaustive unless the finite model and coverage establish that claim. Branch probabilities require a measure. Pruning a display branch must not silently delete it from the calculation or renormalize remaining probabilities. A region can instead remain visible as an unresolved aggregate.

A hybrid interface can show important branches, formulas and bounds together. Users expand regions affecting their decisions. This preserves explanation while avoiding compulsory exhaustive materialization. The underlying family remains authoritative when a new question requires a different partition.

\section{Budgeted computation}
A query should state resources and acceptable result types. Exact values, certified bounds, feasible witnesses and statistical estimates are distinct deliverables. If exact work exceeds budget, return partial bounds and unresolved regions. Do not substitute an unsupported point merely because the interface expects a number.

Priority can go to liquidity, covenant, default and decision boundaries. This is a query-specific strategy and must not remove rare regions from a tail-risk calculation. The next chapter develops sampling and other approximations while preserving the distinction between retained possibilities and sampled evidence.

The layered proposal is symbolic constraints, shared immutable records, dependency-aware elimination, guard-based splitting, justified aggregation and controlled approximation. Each layer has a correctness condition. Choosing a graph instead of a tree is useful engineering, but the mathematical and economic obligations remain.

## 9. Approximate inference and simulation without false certainty

simulation/09-approximation.tex

### Opening

\chapter[Approximate simulation]{Approximate inference and simulation without false certainty}
\label{sim:approximation}

Exact symbolic calculation will not solve every useful company model within available resources. Approximation is therefore necessary. Its legitimacy depends on naming the quantity being approximated and preserving the distinction between numerical evidence and economic possibility. A finite sample can estimate an expectation under a declared distribution. It cannot, by itself, characterize every history compatible with disclosures. A fitted surrogate can interpolate a function well while giving the wrong answer at a default boundary.

\section{Choose the target first}
Different questions require different methods. An expected cash balance, a worst-case cash balance, a breach probability, a feasible breach witness and a policy value are different targets. A method appropriate for one can be misleading for another. Sample averaging targets an expectation; minimizing over samples supplies a witness-based bound on a minimum, not an exact worst case.

Let $Y=F(H,S,\pi)$ under a declared joint measure for history $H$ and scenario $S$. Monte Carlo draws $Y_1,\ldots,Y_n$ give the sample mean
\begin{equation}
 \widehat m_n=\frac1n\sum_{i=1}^nY_i.
\end{equation}
Under independent identical sampling and finite variance, its variance is $\operatorname{Var}(Y)/n$. Those conditions are part of the claim. Correlated paths, importance weights or adaptive sampling require a different variance treatment. The formula does not apply merely because the output file has $n$ rows.

Without a probability model, a finite collection of histories can still be useful for explanation and testing. It should be called a set of witnesses or selected cases. Equal frequencies in that collection do not establish probabilities in the underlying company family.

\section{Sampling a persistent parameter}
If a contract type is fixed but unknown, sample it once for a simulated world and retain it through time. Draw future innovations according to their conditional process. This produces the intended joint law of parameter and trajectory. Redrawing the type each period approximates a different model.

The distinction remains important after filtering. Resampling particles may duplicate a parameter value as a computational operation; it does not mean the company changed contract. Particle identity and world identity must not be confused. A lineage record can preserve which parameter and past events each particle represents.

### Ending


A useful report can state that breach is impossible in one region, possible with a verified witness in another, and probabilistically estimated in a third under an admitted measure. These are compatible forms of information. Reducing them to one unlabeled scalar would lose their meaning.

\section{Stopping rules}
A numerical budget should specify what makes an approximation adequate for the decision. A tolerance on expected cash may be appropriate for planning; a confidence interval for breach probability may be needed for a probabilistic statement; a certified lower bound may be needed for a robust safety claim.

Stopping because the sample mean appears stable can miss a rare region. Repeatedly checking a confidence interval without accounting for the stopping design can alter its coverage. A deterministic residual tolerance does not establish statistical accuracy. The stopping criterion should match the target and method.

If the required evidence cannot be obtained within budget, the answer remains provisional or unresolved. This is not a reason to discard the model's useful conditional results. It is a reason to state what is known, what remains uncertain and which computation would discriminate the remaining cases.

\section{Proposed approximation records}
Each approximation should record its target, retained family, measure if any, sampling or discretization rule, random seeds, support assumptions, error estimates, failed regions and method version. A run manifest supports reproduction; the reader-facing result should explain the consequences rather than expose every internal field.

Tests should include a small exact reference, a rare-event fixture, a persistent-parameter fixture, a boundary-sensitive fixture and an intentionally unsupported region. Comparison should use the same model and query. A fast method solving a simplified target is not a faster solution to the original target unless the difference is quantified.

The objective is controlled approximation, not universal exactness. The system can remain useful while refusing an unjustified probability or exact bound. Retaining the original family ensures that future evidence and better methods can revisit uncertainty that today's computation could not resolve.

## 10. Decisions when probabilities and histories remain ambiguous

simulation/10-decisions.tex

### Opening

\chapter[Decisions under ambiguity]{Decisions when probabilities and histories remain ambiguous}
\label{sim:decisions}

A simulator can describe possible consequences without selecting an action. A decision method needs an objective, a feasible policy class and a treatment of uncertainty. These are substantive choices. Worst-case liquidity, expected shareholder value and minimax regret answer different questions. No accounting identity selects among them. When uncertainty persists over time, the choice also determines how plans respond to new information.

\section{Evaluation before optimization}
For a fixed policy $\pi$, let $V(\pi,h,s)$ be a defined payoff or cost. It may be terminal cash, discounted owner distributions, service continuity or another quantity. Its units and horizon should be stated. Combining several objectives requires weights or constraints that should remain visible.

Evaluating a supplied policy is often the safest first task. It separates economic mechanics from policy selection. Once those mechanics are checked, optimization can search over an admissible class. A numerical optimizer should not be allowed to choose actions outside contractual rights or use information unavailable to the actor.

The distinction also helps interpret historical behavior. A policy that would maximize a modeled objective need not describe what management actually did. Simulation under that policy is a normative or counterfactual exercise unless behavioral evidence supports its use as a forecast.

\section{Expected value under a declared measure}
If a joint probability measure $P$ is admitted, a policy can be evaluated by $\mathbb E_P[V(\pi,H,S)]$. The distribution must preserve dependence between history, shocks and signals. A posterior over report-compatible histories is one possible input, but its prior and likelihood assumptions remain part of the result.

If two histories have equal likelihood under all retained evidence, their posterior odds depend on prior odds. More observations of the same uninformative kind do not remove that dependence. The robust Bayesian analysis of \citet{giacomini2021} makes this issue explicit for set-identified models. Its application here motivates sensitivity to unresolved prior choices, not an automatic probability for each journal.

A report can show policy rankings under several admitted priors. If every prior gives the same ranking, that conclusion is more robust to the specified ambiguity. If rankings differ, a single average conceals a material decision sensitivity. The next useful evidence may be the fact that distinguishes those priors' consequences.

\section{Worst-case evaluation}

### Ending


Without defensible probabilities, one can report the range of improvements across possible signal outcomes and criteria. A guaranteed improvement may be zero even when some outcomes are valuable. This is a meaningful conclusion and avoids assigning probabilities merely to produce an expected number.

\section{Selecting a method for a user question}
For disclosure explanation, preserve possible and certain answers. For a supplied stress, evaluate conditional mechanics. For planning under an admitted distribution, estimate expected values and relevant risks. For a safety requirement across compatible histories, use robust feasibility and bounds. For competing actions without probabilities, consider dominance and explicitly chosen robust or regret criteria.

Dominance is particularly useful: if one feasible policy performs at least as well in every admitted world and strictly better in some, it can be preferred under many monotone criteria. If policies cross, the choice depends on preferences or probability assumptions. The simulator should show that dependence rather than invent a universal ranking.

A method-selection interface should ask for a criterion only when the user has requested a decision that the evidence alone cannot determine. It can still complete mechanical comparisons and identify dominant or infeasible options. This preserves progress while keeping value judgments explicit.

\section{Implementation and validation}
A decision record should specify actor, objective, information, feasible actions, uncertainty set or measure, commitment convention, horizon and terminal treatment. Terminal assumptions matter: liquidating assets at book value at the horizon can create an artificial reward and change earlier decisions.

Small exact finite examples should compare direct policy enumeration with recursive methods. Include the fixed-type pasting counterexample, an information-revelation example, a capacity-constrained financing example and a case where expected value and robust choice disagree. These fixtures discriminate semantic errors before expensive numerical optimization.

Passing them establishes the specified criterion and timing mechanics. It does not establish that the criterion describes management or that the uncertainty set is empirically adequate. Those remain separate assumptions or research questions. The system can support several methods without declaring one a universal default.

## 11. Solving the economic equations that the model actually states

simulation/11-numerics.tex

### Opening

\chapter[Solving the economic equations]{Solving the economic equations that the model actually states}
\label{sim:numerics}

A correct financial representation can still be evaluated by the wrong numerical method. Conversely, a numerical method can converge accurately to equations that describe the wrong financing problem. The first obligation is to state the target equations, their timing and their feasible domain. Only then does it make sense to choose a solver or train a neural approximation. The risky-debt convention discussed earlier illustrates why a small residual is insufficient: an inconsistent cash convention can be solved very accurately.

\section{Separate identities, conditions and approximations}
Accounting identities reconcile stocks and flows. Contract equations determine obligations from terms. Behavioral conditions describe choices. Equilibrium conditions connect counterparties and prices. Numerical approximations evaluate these relations with finite resources. They should not be treated as interchangeable equations in an undifferentiated loss.

An accounting identity can often be enforced exactly by construction. A lender pricing equation may involve an expectation and an endogenous default rule. A management optimum may require inequalities and boundary conditions. A reporting standard may require a categorical treatment selected by facts. Each type needs a suitable validation method.

A residual vector can combine them for computation, but the result should still report each component in meaningful units. A small average residual can hide one economically decisive violation, especially when large accounting amounts dominate the scale. A pricing residual of one currency unit and a share-count residual of one share are not directly comparable without a declared normalization.

\section{The Bellman problem}
For a finite-horizon shareholder problem, let $x$ be state, $a$ a feasible action, $d_t(x,a)$ the current net distribution to the modeled owners, and $\beta$ a discount factor under the chosen valuation formulation. A Bellman equation is
\begin{equation}
 V_t(x)=\sup_{a\in A_t(x)}\left\{d_t(x,a)+\beta\mathbb E[V_{t+1}(X_{t+1})\mid x,a]\right\}.
 \label{sim:bellman}
\end{equation}
The expectation uses the declared transition law and information. If an action depends on private information or a belief state, the state must be defined accordingly. The terminal value $V_T$ is an assumption with economic consequences, not merely a numerical boundary condition.


### Ending


Stochastic comparisons require uncertainty evidence. One seed or a few short runs can nominate a candidate but cannot establish superiority from descriptive averages alone. Hard failures, descriptive differences and statistically supported rankings should remain separate. This is particularly important when rare defaults dominate economic conclusions.

\section{A proposed solver interface}
The solver receives a typed economic problem: state domain, timing, objectives, constraints, transition and observation laws, price equations and requested accuracy. It returns functions or policies together with target residuals, feasibility diagnostics, unresolved regions and reproducibility information.

A solver should not mutate the economic model to obtain convergence without recording the change. Smoothing, truncation, penalty relaxation and altered terminal values define modified problems. Their relation to the original target must be evaluated. A successful run on a modified problem is not an implicit solution of the original.

AccDSL can support several solvers behind the same problem definition. The interface should preserve method-specific limitations rather than force every solver to claim identical guarantees. A certified finite result, a local numerical solution and a learned approximation can all be useful when labeled accurately.

\section{The smallest justified numerical program}
Begin with a one-period debt model whose face, proceeds and recovery are distinct. Verify cash-leg pricing and limited-liability conventions exactly. Add a finite-state dynamic model with explicit feasible policies and compare enumeration with backward induction. Then add borrowing limits, equity issuance and default transitions one at a time.

Only after these targets are stable should a learned solver be compared on the same equations. The comparison needs a predeclared primary criterion, veto diagnostics, budget ladder and heldout downstream checks. Training settings remain hypotheses until supported on this target.

This staged approach does not postpone the difficult economic questions. It exposes them early in forms that can be checked. The purpose of deep learning is to accelerate a well-defined computation, not to make an ambiguous financing model appear resolved through a low loss value.

## 12. Validation, adversarial cases, and the limits of a simulation

simulation/12-validation.tex

### Opening

\chapter[Validation and failure analysis]{Validation, adversarial cases, and the limits of a simulation}
\label{sim:validation}

A credible simulator should fail intelligibly when its premises are insufficient. It should also be tested against cases where a plausible implementation gives a confident but wrong answer. The purpose of validation is not to accumulate a large count of passing assertions. It is to distinguish errors in evidence, representation, economics, accounting, information, numerical calculation and interpretation. Each class requires a different test and a different repair.

\section{What is being validated}
There are at least three separate questions. Does the implementation compute the specified model? Is the specified model mathematically and economically coherent? Does the model usefully describe the company or decision under study? A passing unit test can answer part of the first question. It cannot answer the third by itself.

For example, a simulator can correctly implement unlimited borrowing at a fixed rate. That implementation may pass every accounting reconciliation. It remains unsuitable for a claim about refinancing risk unless unlimited borrowing is an appropriate premise. Conversely, a realistic financing model can be implemented with the wrong proceeds convention. The two failures should not be blurred into a generic low accuracy score.

A validation record should state the claimed target, quantity actually computed, comparison method and interpretation. If the target is a worst-case cash bound but the method reports a sampled minimum, the mismatch is explicit. The sampled result may still be useful as a witness; it should not inherit the stronger claim.

\section{An extensible failure taxonomy}
No finite catalogue can prove that every possible simulation failure has been anticipated. New contracts, standards, behaviors and software interactions can create new cases. A systematic taxonomy is nevertheless valuable because it exposes the dimensions along which failures arise and guides new tests.

The taxonomy used here follows the calculation: evidence admission, historical reconstruction, economic state, actor information, scenario definition, feasible behavior, financing, accounting, aggregation, approximation and reporting. Cross-cutting dimensions include time, units, entity, dependence, precision and provenance. A failure can occupy several categories. A maturity error, for example, affects evidence, timing, financing and liquidity.

Coverage should be expressed by mechanisms and boundaries, not only by scenario count. One thousand random rate paths do not test a missing conversion clause. A single carefully designed positive-recovery case can expose a proceeds-versus-face error that many no-default paths miss.

\section{Evidence admission failures}

### Ending


A completed run also needs a trace to its assumptions and evidence. Reproducibility requires exact versions of source views, rules, methods and numerical settings. A content hash identifies a file; it does not prove the file's correctness. Both provenance and substantive validation are needed.

\section{From catalogue to implementation work}
The proposed failure catalogue should be machine-readable enough to link each mechanism to a fixture, expected outcome and relevant chapter, while the manuscript explains why the failure matters. New cases can be added without claiming that the catalogue is exhaustive.

Implementation can proceed by vertical slices. A slice reconstructs a bounded history family, applies a scenario and policy, generates events and journals, produces statements and reports unresolved regions. This is more discriminating than implementing isolated formula modules without a source-to-result case.

The first slice should preserve ambiguous debt type, issue proceeds distinct from face, a binding financing limit and actor information. Later slices add ownership rights, group transfer constraints, persistent tax state and approximate inference. Each slice should retain the wider open scope rather than redefine the mission to match what is easiest to execute.

\section{What successful completion would mean}
For this document, success means an explicit and traceable argument, checked illustrative calculations, preserved prior work, inspected source support and a clear account of proposed methods and their failure cases. It does not mean that all methods are implemented or that the product is ready for unrestricted use.

For the simulator, success is query-specific. It means the implementation computes the declared target within its stated evidence and numerical guarantees, preserves unsupported regions, and explains the economic dependence of the result. Whole-company applicability requires coverage of the actual company's material contracts, events and reporting basis.

The following worked chapters apply these principles to complete small problems. Their purpose is to make the design reconstructible: the reader can follow observations through competing histories, decisions, financing, journals and outcomes, and see exactly where a different assumption changes the answer.

## 13. A complete small company: from reports to divergent stress outcomes

simulation/13-company-case.tex

### Opening

\chapter[A company reconstructed and stressed]{A complete small company: from reports to divergent stress outcomes}
\label{sim:company-case}

The earlier examples isolate individual mechanisms. This chapter joins them in one synthetic company so that every projected balance can be traced to an event. The company is deliberately simple: one currency, one legal entity, no tax, no dividends, no acquisitions and no other comprehensive income. These exclusions make the arithmetic inspectable. They do not describe a complete real-company model. The point that carries over is the need to preserve compatible economic histories and their joint statement consequences.

\section{The opening statement}
At the beginning of the historical year, the company has cash 40, receivables 30, inventory 50 and property carrying amount 80. Its liabilities are debt 100 and trade payables 40. Equity is 60. All amounts use one currency unit.
\begin{center}
\begin{tabular}{lr|lr}
\toprule Assets&Amount&Liabilities and equity&Amount\\\midrule
Cash&40&Debt&100\\
Receivables&30&Trade payables&40\\
Inventory&50&Equity&60\\
Property&80&&\\\midrule
Total&200&Total&200\\\bottomrule
\end{tabular}
\end{center}
The equality is an accounting starting point. It does not identify customers, inventory units, asset vintages or debt terms. We initially admit the balances as exact to focus on hidden composition. A later section reintroduces rounding and source uncertainty.

The company operates during the year and reports sales 120, cost of sales 70, cash operating expenses 25, interest expense 5 and depreciation 10. With no tax in this teaching model, profit is 10. The cash-flow information reports customer receipts 130, supplier payments 50, operating-expense payments 25, interest payments 5 and capital expenditure 20. No debt is issued or repaid.

### Ending


Rounding intervals can also be jointly constrained by a total. Treating each line's rounding error independently may admit totals outside the reported balance-sheet interval. The feasible family should retain the total relation rather than merely widen every number separately.

\section{An explanation the system should produce}
For the worst witness, an explanation should identify the concentrated receivable history, floating debt, customer default, rate increase, supplier payment and lack of an eligible funding response. It should show cash 13 and equity 43 with their bridges. It should identify which facts are observed and which are alternative assumptions.

The explanation should not say that the real company will fail. It should say that a compatible history produces the stated shortfall under the specified shock and policy. If the threshold is internal, it should call it a target shortfall. If a covenant consequence is modeled, it should name that consequence and its premises.

A second explanation can identify the source that would exclude the witness, such as a verified customer concentration note or fixed-rate contract. This turns the simulation into a guide for focused investigation. It also makes disagreement productive: a reviewer can challenge a premise rather than merely distrust the final number.

\section{What this complete case establishes}
The case connects reports, compatible histories, events, journals, cash and equity. It shows why identical statements do not identify shock response, why joint restrictions matter, why financing needs a transaction and why timing matters. All numerical relations are small enough for exact checking.

It does not establish a calibrated corporate model, a universal customer-default process or a reporting-standard treatment for every event. Those would require additional facts and authority. The bounded example is valuable because it exposes the mechanisms without pretending those wider questions are resolved.

An implementation fixture should store the input observations, the four initial history cases, the optional dependence restriction, the event sequence, expected journals and final statements. It should also test the rejected variants: equal branch probabilities without a measure, independent marginal output selection, a late facility draw and a cash-balancing equity plug. These are concrete failures of the target semantics.

## 14. A refinancing crisis: dates, offers, covenants, and recovery

simulation/14-refinancing-case.tex

### Opening

\chapter[A refinancing crisis in dated events]{A refinancing crisis: dates, offers, covenants, and recovery}
\label{sim:refinancing-case}

A year-end debt ratio can look manageable while a particular morning's payment is impossible. This chapter follows a synthetic treasury problem through dated cash events. The company has several potential responses, but each has conditions. The purpose is to show how financing feasibility differs from choosing a debt amount in an optimization formula. All offers and legal consequences below are assumptions of the example; they are not estimates or statements of general law.

\section{The payment calendar}
At the opening of day 1, unrestricted cash is 12. A customer receipt of 18 is due on day 5, wages of 10 on day 3, an old loan principal of 30 on day 4 and its coupon of 2 on day 4. Inventory worth 20 in the accounting records can be sold, but only through a specified offer. There is no automatic overdraft.

If all receipts and payments are netted over five days, closing cash is
\begin{equation}
 12+18-10-30-2=-12.
\end{equation}
The total shortfall is 12. But the timing problem is larger: after wages, cash is 2 before the day-4 debt payment of 32. The company needs 30 by day 4, even though 18 is expected the next day. A facility that supplies only the final net shortfall cannot bridge the maturity.

The receipt is also uncertain. In history H1 it is contractually due and collected on day 5. In H2 it is subject to customer acceptance and may be delayed to day 9. Both histories fit an opening receivable of 18. The financing decision must distinguish the customer's contractual obligation, actual collection policy and the analyst's uncertainty.

\section{Three offers}
Offer A is a bridge facility settling on day 4 before the old payment, with maximum principal 30 and a fee of 1 withheld at draw. Its repayment of principal plus 1 is due on day 6. Offer B is a term debt issue settling on day 5, priced at 0.9 per unit face, with a fixed fee of 2 and maximum face 40. Offer C is an inventory sale settling on day 4, paying 15 for inventory carried at 20.

These offers have different cash, accounting and future consequences. A supplies short-term cash but creates another near maturity. B can supply longer funding but arrives too late to pay the old loan without a bridge or deferral. C supplies timely cash and incurs a disposal loss under the illustrative carrying-value treatment, while removing inventory needed for operations.

### Ending


The implementation reuses the exact fixed-offset timestamp parser and partitions
the query at every eligible interval boundary. It retains every covered,
uncovered, unknown or conflicting piece. Equivalent timestamp offsets denote
the same instant, and adding a future correction leaves an earlier view's
control conclusions unchanged. The checked cases include all two-cell combinations
of control, no control and unknown control, as well as revision conflicts,
coverage gaps, missing ancestry and corrupted source identities.

This gives the simulator a precise way to carry unresolved control history
alongside otherwise balanced company books. It does not yet connect an admitted
real history to acquisition measurement, changing group membership or complete
financial statements. The next financial composition must supply those methods
and their dated authority while preserving the source and actor-view distinctions.
Neither a successful funding transfer nor a complete conditional interval
partition can supply the missing accounting evidence.

## 15. A recapitalization: cash raised, rights transferred, and incentives changed

simulation/15-ownership-case.tex

### Opening

\chapter[A recapitalization and its owners]{A recapitalization: cash raised, rights transferred, and incentives changed}
\label{sim:ownership-case}

A financing plan can save a company while reducing the value held by its existing owners. It can also dilute their percentage without reducing their value. Distinguishing these outcomes requires a security-level calculation. This chapter follows a synthetic recapitalization with ordinary shares, a preference offer and a convertible claim. The terms are stipulated so the arithmetic can be reconstructed. They illustrate mechanisms rather than legal or valuation conclusions for a real issuer.

\section{The company before financing}
There are 100 ordinary shares. Existing operating assets have a stipulated economic value of 600, cash is 20 and a senior debt payment of 80 is immediately due. For the first comparison, assume asset value is unchanged by financing and there are no other claims. Before paying debt, residual economic equity value is $600+20-80=540$, or 5.4 per ordinary share.

The company nevertheless cannot pay 80 from cash 20. It needs 60 of additional cash. Positive economic equity value does not eliminate this liquidity problem. Selling assets, borrowing, issuing equity or negotiating deferral are different possible responses. We first study an ordinary-share offer.

Book assets may have a different carrying amount. Nothing in the calculation requires book equity to equal 540. If the model uses book equity to set a subscription price of 5.4, it would be making a separate valuation assumption. Here 540 is a supplied economic valuation used only for the illustrative allocation.

\section{A fairly priced ordinary issue}
Suppose investors subscribe at 5.4 with no fees, and the company raises exactly 60. New shares are $60/5.4=100/9$, about 11.1111. Cash becomes 80 and is paid to the senior creditor. Remaining assets are 600, there is no debt, and shares total $1000/9$.

Post-transaction value per share is
\begin{equation}
 \frac{600}{1000/9}=5.4.
\end{equation}
Existing holders retain value 540, and new holders own value 60. Their percentages change, but no value is transferred under these assumptions. The creditor receives its contractual 80. The cash injection solves liquidity without creating extra value by itself.

### Ending


The histories differ in gross funding, repurchase behavior and prices. If future policy extrapolates issuance discounts or repurchase commitments, the distinction matters. A note disclosing gross proceeds and repurchases can narrow the family. Without it, a single implied price of 3 is not established as an actual transaction price.

This example parallels the receivables and debt bridges. Net movements constrain sums but do not identify gross events. The security register should therefore permit unresolved transaction families while preserving observed opening and closing counts.

\section{An end-to-end fixture}
A useful fixture starts with the 100-share company, the debt maturity and the cash need. It evaluates ordinary issuance at fair and discounted prices, fixed fees, authorization limits, preference rights and conversion. Each transaction updates cash, liabilities, shares and rights before producing statements.

Expected failures include using book value as an unstated subscription price, ignoring the authorization cap, counting conversion shares against the old denominator, paying mutually exclusive preference and conversion rights together, and treating an unsigned offer as settled cash. Each failure has a specific input that exposes it.

The fixture should also retain unresolved accounting classification as a legitimate result where full terms are absent. A financing calculation can be mechanically complete while a statement presentation remains conditional. That distinction is preferable to inventing a universal accounting rule to make the example look finished.

\section{What the case adds to simulation design}
Equity funding is a transaction among actors with claims, rights and constraints. Its effect cannot be reduced to an external-equity cost scalar when ownership and future decisions matter. Nor can share count alone establish value transfer. Prices, fees, rights and valuation premises jointly determine the result.

The proposed AccDSL design therefore keeps a dated security register, offer and settlement states, class-specific payoff rules and actor objectives. It can use a simple homogeneous-share profile when appropriate, but retains the boundary that tells a user when richer terms are required. This makes dilution and financing consequences explicit without pretending that every security must always be simulated at maximum detail.

## 16. A decision before and after disclosure: an exact learning example

simulation/16-learning-case.tex

### Opening

\chapter[A decision before and after disclosure]{A decision before and after disclosure: an exact learning example}
\label{sim:learning-case}

Learning matters only through a specified relation between hidden facts, observations and decisions. This chapter constructs that relation explicitly. The example is finite, so every policy and probability can be checked by enumeration. It demonstrates why two companies with equal current statements can require different information states, and why preserving only unconditional future cash distributions is insufficient for adaptive decisions.

\section{Two hidden exposures}
A company must choose a hedge before a future settlement. Its exposure type is either A or B. Under type A, hedge A avoids a loss of 10 while hedge B avoids none. Under type B, hedge B avoids a loss of 10 while hedge A avoids none. Each hedge costs 2. Doing nothing costs nothing and leaves the loss 10.

For the first calculation, assume type A and B each have probability one half. This probability is a supplied teaching assumption. The company has enough cash to execute either hedge and can choose at most one. Current financial statements do not distinguish the types.

Net loss after the correct hedge is 2, after the wrong hedge is 12, and after no hedge is 10. Without further information, either hedge has expected loss 7, so a risk-neutral expected-loss policy chooses either hedge rather than doing nothing. Symmetry gives two equally optimal actions. The model should not invent a preference between them.

\section{A noisy signal}
Before choosing, the actor can receive a signal labeled A or B. Let the signal be correct with probability $q$, symmetrically across types, with $q\geq1/2$. Bayes' rule with equal priors gives posterior probability $q$ for the signaled type. Following the signal yields expected loss
\begin{equation}
 L_{\rm signal}(q)=2+10(1-q)=12-10q.
 \label{sim:signal-loss}
\end{equation}
The first term is hedge cost. The second is the loss when the signal is wrong. At $q=0.9$, expected loss is 3; at $q=0.5$, it is 7, matching no informative signal.


### Ending


This compact belief is sufficient because the future depends on the past only through the fixed type posterior under the declared model. If signal quality is itself unknown or past actions create commitments, $p_t$ alone may cease to be sufficient. The state must then include those additional quantities or their joint belief.

\section{Compression tests from the example}
A proposed compression should preserve the joint type-signal distribution, action availability, costs and timing. It should reproduce expected loss 3 for informative signals and 7 for uninformative signals. It should refuse to merge those technologies for an adaptive policy query.

A separate test can merge states differing only in an irrelevant customer label when neither payoffs nor observations depend on that label. This establishes a valid reduction within the small model. Positive and negative examples are both needed: a system that never merges is safe from one error but does not solve the computational problem.

Changing the query to one fixed hedge can make a coarser compression sufficient. The approval should be scoped to that query. Reusing it for information acquisition or adaptive hedging without rechecking would repeat the original mistake.

\section{What the case teaches about trees}
The full tree has hidden types, signals and actions. Hidden type branches need not be visible to the actor. Signal branches define information partitions, and actions before a signal must be shared across indistinguishable worlds. A drawing that places separate decisions under each hidden type can accidentally imply forbidden knowledge.

A belief-state or symbolic implementation can encode the same problem without storing every path. It must still preserve the information partition. The tree is a useful explanatory projection of that structure, not its only possible storage form.

The central requirement is therefore not one point per possibility. It is preservation of the joint relation among persistent facts, observations and feasible decisions. This example gives exact numbers against which a proposed representation can be tested before it is applied to a much larger company.

## 17. Continuous history families: projection, optimization, and threshold refinement

simulation/17-continuous-methods.tex

### Opening

\chapter[Continuous families and exact bounds]{Continuous history families: projection, optimization, and threshold refinement}
\label{sim:continuous-methods}

A finite list of histories is often an inadequate description even of a small company. Unknown rate exposure, customer allocation, asset age and settlement timing can vary continuously. The right question is frequently whether a conclusion holds over a constrained region. This chapter develops several exact small calculations and shows where they cease to be adequate. The methods are proposals for bounded profiles, not a claim that every company reconstruction is a linear program.

\section{An affine exposure family}
Let $x$ be foreign-currency debt maturing soon and $a$ the floating share of total debt. Suppose disclosed margins imply $0\leq x\leq50$ and $0\leq a\leq1$. A simplified next-period cash requirement under currency depreciation $d$ and rate increase $r$ is
\begin{equation}
 Q(x,a)=Q_0+dx+100ra.
\end{equation}
If $d$ and $r$ are nonnegative and the two unknowns are jointly unconstrained beyond their bounds, the maximum is $Q_0+50d+100r$ and minimum is $Q_0$. These extrema occur at feasible corners. No grid is needed.

Now add a disclosure that the floating portion is entirely within the foreign-currency debt maturing soon, so $100a\leq x$. The feasible family is no longer a rectangle. The minimum remains $Q_0$, but the maximum floating share is one half, giving maximum $Q_0+50d+50r$. The relation changes the worst case even though debt total remains 100.

The condition is a stipulated example, not an inference from the margins alone. It illustrates why exact bounds must optimize over the joint constraints. Independently maximizing every marginal amount can overstate or understate the relevant result depending on signs and relationships. A constraint-aware bound carries the assumptions that make its corner feasible.

If the query includes a hedge whose receipt increases with $x$, the coefficient on $x$ can change sign. Monotonicity should be derived from the full expression, not assumed from a variable's label. A larger foreign-currency exposure can have a smaller net cash effect when a linked hedge changes at the same time.

\section{Linear programs as a bounded exact method}
When observations, bridges and query are linear in continuous unknowns, a bound can be formulated as a linear program. Let $z$ collect amounts and let $Az\leq b$, $Ez=e$ define the family. The minimum cash query is

### Ending

The present declared-program runner validates a fiscal opening at the period start with no flows. It therefore refuses a midperiod current book as its opening. The selected continuation uses the same typed event engine directly for one instruction, retains the actual prefix unchanged, and reports the resulting book against the original period opening. This is a checked single-step interface. A general program-resumption interface still needs explicit bindings for both books, the verified prefix and the remaining commands; it cannot be implemented by resetting a date or discarding prior flows.

\section{Resuming selected payments without losing their history}
\label{sim:coupon-program-resume}

A selected same-period runner now extends the checked coupon prefix through several supplied instructions. Its plan retains the original period opening for reports and the current book for execution. It also identifies the original source, selected method registry, verified prefix, complete future instruction list and resource limits. A checkpoint's cursor counts only accepted new instructions. The earlier coupon refusal remains in its archive; it is not replaced by the outcome of a later payment.

For a successful three-instruction suffix, processing one event per call, two per call or the whole suffix produces the same terminal checkpoint. The complete accepted journals, dated flows, current book and cumulative report agree with independent arithmetic and uninterrupted execution. This comparison also covers a later unaffordable payment, duplicate identity and backwards date. In each case, execution retains the accepted prefix and leaves the refused instruction first in the remaining list.\footnote{\path{data/accounting-master/coupon-program-resume-20261027/} retains sixteen cases and 48 chunk comparisons, with 824 assertions and eighteen adverse controls. A separate audit adds 493 assertions, twelve controls and two exact byte-boundary comparisons. The first attempt is preserved: its comparator incorrectly required identical duplicate-refusal wrappers. The generic runner detects a duplicate command before calling the event engine; the selected runner retains the engine's duplicate-event diagnostic. Both reject the same instruction and preserve the same financial state.}

An execution pause has a different meaning from a refusal. A call may consume its allowed number of instructions while another valid instruction remains; this returns a budget pause and can continue from the checked cursor. An economic or chronology refusal stops before the offending event, which cannot be silently skipped on a subsequent call. Changing that event requires a newly identified plan. A complete, refused or resource-limited checkpoint remains unchanged when submitted again under its existing plan.

Resource limits apply to the entire selected suffix, not afresh to each chunk. The inherited command ceiling is 64 and the default trace allowance is 8 MiB. A deliberately smaller allowance exposes the boundary exactly: 82,883 bytes fit the first accepted trace row, but not the second. An allowance of 82,882 bytes accepts no row. The runner retains the next command and reports the unchanged accepted state in both cases. Splitting execution into additional calls does not enlarge the allowance. These limits govern this diagnostic implementation; they neither determine the financial shortfall nor prove that a larger economically feasible schedule is impossible.

The checkpoint's hash is necessary for identifying the supplied record but is insufficient for validating it. The selected interface recomputes the bounded accepted prefix from the identified source, registry and instruction list, then compares the complete checkpoint. This detects altered request metadata even when a narrower financial comparison would still find the same balances. It also detects a changed opening, skipped cursor, missing trace, erased refusal, modified report or enlarged plan budget. Recomputed validation does not append a second accepted event or duplicate a cash flow.

This evidence establishes a selected same-period partial-coupon interface. It does not migrate the general program runner, support every method or reporting-period transition, or establish durable exactly-once commits under concurrent writers. Repeated prefix computation is also a cost, not a scalability result. The distinction between original opening, accepted current book and remaining instructions nevertheless supplies a concrete starting point for broader resumption contracts without erasing the company's earlier history.

## 18. Reference computations that distinguish a useful approximation from a wrong answer

simulation/18-computation-cases.tex

### Opening

\chapter[Reference computations and diagnostic experiments]{Reference computations that distinguish a useful approximation from a wrong answer}
\chaptermark{Reference computations}
\label{sim:computation-cases}

A method can be tested most clearly when a small version of its target is known exactly. This chapter constructs such targets for cash bounds, breach probabilities, policy comparison and residual minimization. The calculations are analytic reference cases. They are not a benchmark ranking and do not supply empirical evidence about a real company. Their role is to expose errors that a large simulation can conceal behind apparently stable averages.

\section{An exact distribution from a declared prior}
Return to cash $C=90-2\alpha$, and now deliberately assume $\alpha$ is uniform on $[0,1]$. This assumption is not inferred from the financial statements. It creates a transparent probabilistic reference. Cash is uniform on $[88,90]$, with mean 89 and variance $4/12=1/3$.

For a covenant requiring cash at least 89.4, breach occurs when $\alpha>0.3$. Its probability is 0.7. The expected cash conditional on breach is the mean of the interval $[88,89.4)$, namely 88.7. These quantities answer different questions: unconditional mean, breach frequency and severity conditional on breach.

A simulation with the right mean but the wrong breach probability is not accurate for covenant analysis. For example, a two-point approximation placing equal mass at 88 and 90 has mean 89 but breach probability one half. Matching the first moment does not preserve threshold events.

The exact distribution also gives quantiles. Under the usual left-continuous generalized-inverse convention, the $p$-quantile is $88+2p$ for $0<p<1$, with endpoint values defined by continuous extension. The convention should be explicit when discrete mass points are introduced, because quantile definitions can differ at jumps.

\section{A discrete grid with known bias}
Approximate $\alpha$ by equally weighted midpoints $(i-1/2)/n$, for $i=1,\ldots,n$. The mean of the grid remains one half, so mean cash is exactly 89 for every $n$. Breach frequency is the fraction of midpoints above 0.3. For $n=4$, midpoints are 0.125, 0.375, 0.625 and 0.875, giving breach probability 0.75.

The mean check passes perfectly while the breach estimate differs from 0.7. Increasing $n$ improves the discretization in this example, but its error depends on the threshold's location relative to the grid. A convergence study should examine the queried event, not only smooth moments.


### Ending


Penalty methods can be useful algorithms. Their residual feasibility must be assessed against the original constraint and the required tolerance. A small violation may be immaterial for some economic quantities and decisive when it represents issuing more shares than authorized or paying cash that does not exist.

\section{Designing a fair method comparison}
A comparison should use the same evidence family, objective, policy class, timing, terminal condition and accuracy target. A faster method that omits a recovery term is not a faster solution of the original pricing model. A method trained on a smaller domain should not be compared as though it covers the full stress region.

The baseline ladder can include exact finite enumeration, a refined classical numerical method, the plain proposed approximation and any enhanced version. Tuning budgets and stopping criteria should be declared. A deliberately weak comparator can establish only a narrow improvement over that comparator.

For stochastic methods, use replications and uncertainty analysis appropriate to the claim. If several candidates pass hard validity screens but differences are not statistically resolved, describe them as viable under current evidence. Runtime, tail error and objective values from a few seeds remain descriptive unless the predeclared analysis supports ranking.

\section{What to retain from a run}
A run should preserve the model and data version, command, environment, seeds, hardware mode, wall time, outputs and the plan defining the question. It should record which diagnostics are validity vetoes, which trigger repair and which merely explain behavior.

The result note should identify whether a failure invalidated the harness, implementation, target or candidate. A candidate failing a planned stress can motivate a repair phase. It does not automatically reject the broader research direction. A broken harness, by contrast, prevents interpreting the candidate comparison.

For the present manuscript, these are proposed experiments and exact reference calculations. No stochastic ranking is claimed. The accompanying arithmetic script checks the deterministic examples and records its scope. Future numerical runs should use these cases to establish semantics before making claims about scalable performance.

## 19. What the literatures contribute, and where their assumptions stop

simulation/19-literature.tex

### Opening

\chapter[What the literatures contribute]{What the literatures contribute, and where their assumptions stop}
\label{sim:literature-synthesis}

The simulation problem crosses several literatures because it combines inference from incomplete reports, accounting representation, dynamic corporate finance, sequential information and computational approximation. No inspected source supplies the entire system. The useful synthesis identifies the problem each source actually solves and the additional work needed for AccDSL. A source's notation or software can be valuable without becoming a universal model of a disclosed company.


\section{Economic events and accounting views}
McCarthy's REA model provides a useful architectural antecedent. Resources,
events and agents, linked through stock-flow, duality and control relations,
organise economic activity before particular accounting views are produced
\cite[pp.~560--570]{litclosemccarthy}. Double entry can be one external view. Claims
can be derived from imbalances or retained as base records when their uses
warrant it. The paper also recognises the practical need for aggregation and
the fact that measurement and periodicity are not settled by a database schema
\cite[pp.~568--576]{litclosemccarthy}. These distinctions support an event-and-contract
representation with journal views. They do not imply that disclosures identify
a unique event history, or supply the likelihood of observing a disclosure.




### Ending

time meanings: a hypothetical future disclosure updates an actor inside that
run, not the analyst's actual present evidence.

\section{What remains to be researched}
The survey is broad but not exhaustive. Important remaining questions include scenario-reduction guarantees for adaptive company policies, robust filtering with static unidentified parameters, strategic disclosure, multi-creditor restructuring, real-company policy estimation and empirical forecast evaluation. Some require additional primary sources; others require derivations and data specific to the target company.

The earlier Francis--Rowell simultaneous-equation lead remains technically uninspected because attempted routes did not provide the paper. It cannot be declared inferior or irrelevant on that basis. The missing Gentry derivation and source-version questions also remain explicit.

A source gap blocks the unsupported claim, not all independent work. The methods already derived here can be specified and checked while the literature queue continues. This keeps research honest without allowing an inaccessible paper to become a reason to stop every implementation task.

\section{The resulting method proposal}
The synthesis favors a joint history family, dated contract and ownership state, actor-specific information, explicit scenario semantics, feasible policy generation, event-to-accounting translation and query-driven computation. Each component has a distinct literature basis and a distinct local obligation.

No single source validates their composition. The worked cases and proposed tests supply initial evidence for the interfaces, while broader implementation and empirical studies remain necessary. The design should therefore preserve the origin and scope of each assumption instead of presenting the synthesis as an established off-the-shelf theory.

The next chapter turns this method proposal into concrete records and algorithms. Its engineering choices remain replaceable. What must survive replacement is the meaning of evidence, uncertainty, information, financing and result status developed throughout this part.

## 20. Implementing the proposed methods without losing their meaning

simulation/20-implementation.tex

### Opening

\chapter[Implementing the proposed methods]{Implementing the proposed methods without losing their meaning}
\label{sim:implementation}

The preceding chapters define what a result means. Implementation should preserve that meaning across extraction, reconstruction, simulation and reporting. The engineering choices in this chapter are proposals and can be replaced. The essential requirements are stable: evidence is not an assumption, a history family is not a sample, actor information is not global state, a financing request is not cash, and numerical failure is not default.

\section{Evidence records}
An evidence assertion needs a source identifier and exact location, value or text, concept, entity, dimensions, units, basis, period and precision. It also needs publication and ingestion information, extraction method and review status. A correction links to the assertion it revises instead of deleting it.

The record should preserve original text alongside normalized values. A normalized number can be checked against the source, and an unresolved phrase remains visible. A mapping from source label to model concept is a separate interpretation with its own support. This allows the mapping to change without pretending the source changed.

An evidence view selects assertions for a particular cutoff and purpose. It can represent as-published, currently restated or analyst-reviewed information. The view should be immutable once used for a frozen result. A new correction creates a new view and an explicit dependency change.

\section{Assumptions as first-class inputs}
An assumption record identifies the quantity or relation supplied, its scope, provenance and role. Examples include a fixed management payout policy, an offer price, a prior over debt types or a terminal liquidation rule. A convenient default should be marked as a hypothesis or baseline rather than disguised as observed evidence.

Assumptions can conflict. A policy allowing unlimited borrowing conflicts with an offer cap if both claim to govern the same action. The system should detect or expose such inconsistencies. Precedence rules must be explicit; silently favoring whichever input was loaded last is unsafe.

Sensitivity should vary assumptions by identity. If one assumption supplies both customer delay and credit loss, changing only one derived field can produce an inconsistent variant. A structured assumption relation makes the intended intervention and its dependencies visible.

\section{History families}

### Ending


Adapters should be checked against small independent cases and preserve unsupported outcomes. A service exception must not become zero cash flow. A missing risk series must not silently carry forward an unrelated value. Dependency and license review remain necessary before selecting a runtime, but no external adoption is claimed by this manuscript.

\section{Incremental implementation}
The first vertical slice should support a bounded history family, exact event timing, simple debt and equity offers, actor information and coherent statements. It should include both successful and refused paths. The worked company and refinancing cases provide expected outcomes.

The next slice can add class rights, conversion, group transfers and persistent tax or asset state. Later work can add nonlinear pricing, partially observed policy optimization and controlled approximation. Each stage should preserve the full mission's open requirements rather than imply that a small slice closes whole-company representation.

A slice is complete only when its source-to-result behavior is checked and its unsupported scope is explicit. A collection of isolated module tests is useful but insufficient for composition. The critical interactions are where financing, information and accounting meet.

\section{Review and release evidence}
A release should preserve model and source versions, exact fixture results, numerical validation where applicable and rendered documentation. Engineering conformance, accounting authority, scientific validity and human comprehension remain separate evidence categories.

A clean PDF or passing arithmetic script does not establish product readiness. A reader-facing explanation must still make assumptions and derivations understandable. A human review can identify comprehension problems that mechanical checks miss; its absence does not prevent provisional drafting but does prevent claiming that acceptance occurred.

The stable documentation links should point to a built, identified candidate with an honest status. Historical manuscripts and hashes remain available. This allows the design to advance without rewriting evidence from earlier stages or confusing the newest document with a completed system.

## 21. Groups, counterparties, and contagion across otherwise coherent statements

simulation/21-group-contagion.tex

### Opening

\chapter[Groups, counterparties, and contagion]{Groups, counterparties, and contagion across otherwise coherent statements}
\label{sim:groups}

A company group is not a single bank account. Consolidation can eliminate internal balances for reporting while cash remains held by particular entities, currencies and custodians. Stress can also propagate through guarantees, collateral and common counterparties. These mechanisms make group simulation a natural test of whether the model preserves economic rights beyond accounting totals. The examples here stipulate transfer and priority rules; actual legal applicability requires source-specific authority.

\section{Consolidated cash and entity cash}
Consider a parent P and subsidiary S. P holds cash 5 and owes external debt 20 tomorrow. S holds cash 30 and owes external suppliers 8 the following day. The consolidated cash balance is 35. It exceeds the parent's debt maturity, but that fact does not establish that P can pay.

Suppose S may transfer at most 10 before tomorrow because the remainder is restricted or needed under a binding local rule. P can assemble 15 and has a shortfall of 5. A consolidated cash forecast that deducts 20 from 35 reports 15 remaining and misses the entity failure.

If a transfer of 15 is permitted instead, P can pay but S's remaining cash must still cover its own obligations. The transfer is not free group liquidity: it changes where resources are held and can create an intercompany claim or distribution. The event should be represented in both entities before consolidation.

\section{Intercompany loan mechanics}
Suppose S lends 15 to P. S records an intercompany receivable and cash outflow; P records cash and an intercompany payable. P then repays external debt 20 using its original 5 plus the loan. Consolidated cash falls from 35 to 15 and external debt falls by 20. Internal claims eliminate in the consolidated statement under the stipulated perimeter.

The internal loan nevertheless matters for future entity liquidity. P owes S according to its terms. If S later needs cash, it cannot spend a consolidated elimination entry. A model that deletes internal contracts after consolidation loses repayment dates and possible stress transmission.

Interest on the internal loan can affect entity tax and distributable earnings even when consolidated interest eliminates. Currency differences can create further effects. The general engine should retain legal-entity records and produce consolidation as a reporting view rather than using the consolidated view as its only state.

\section{A guarantee creates contingent support}

### Ending


This does not require every query to load every field. Dependency-aware execution can select the relevant subgraph. A parent liquidity query follows transfers and guarantees; a consolidated revenue query follows perimeter and eliminations. The underlying representation preserves the links needed when the question changes.

Unknown links can be represented as alternatives. A guarantee's existence, cap or trigger may be unresolved. The query can report outcomes conditional on those terms and identify the source that would resolve them. Inventing no guarantee as a default would systematically favor benign outcomes.

\section{Tests for group coherence}
A transfer test should show equal and opposite cash movements before fees and consistent internal claims. A consolidation test should eliminate internal balances without deleting entity state. A collateral test should prevent recovery exceeding the shared pool. A timing test should prevent late cash from funding an earlier obligation.

A guarantee test should create the correct successor claim or loss under the stipulated rules and avoid double payment. A currency test should preserve native units through conversion and reporting. A cross-default test should distinguish threshold, cure and acceleration.

These tests are stronger than a final consolidated balance-sheet equality. They examine the mechanisms that can make a group fail despite apparently sufficient aggregate resources. Passing them establishes the specified small cases, while actual legal and regulatory applicability remains tied to source evidence.

\section{What cannot be compressed away}
For group liquidity, entity location, currency, transfer rights and dates are often essential. For recovery, collateral and priority are essential. For behavior, information and contractual discretion are essential. A compression that removes them may still reproduce current totals while changing stress outcomes.

The practical method is to retain a rich underlying state and derive query-specific summaries. A summary approved for one purpose can be refined for another. This avoids both extremes: duplicating the entire group for every possibility and collapsing the group into totals that cannot explain who can pay whom.

## 22. When the model itself is incomplete: missingness, misspecification, and research priorities

simulation/22-model-risk.tex

### Opening

\chapter[When the model itself is incomplete]{When the model itself is incomplete: missingness, misspecification, and research priorities}
\label{sim:model-risk}

Preserving all histories inside a model does not protect against a missing mechanism outside it. A feasible family can be exact and still omit a guarantee, a customer concentration or a financing restriction. This chapter examines how to represent that limitation without abandoning useful analysis. The aim is to make conditional conclusions precise and to direct further work toward omissions that can change decisions.

\section{Unknown value versus absent mechanism}
An unknown interest rate can be represented by a variable if the contract form is known. An unknown existence of a guarantee requires an alternative contract structure. A mechanism the language cannot express is a different limitation. These cases should not share one generic null.

A missing value within a supported form can often be bounded or inferred. A missing structural alternative can change the dimension and event logic of the family. An unsupported mechanism may require a new model component before any bound is meaningful. The result should identify which kind of gap it faces.

For example, allowing a loan rate between zero and twenty per cent does not cover a missed conversion right. A wider rate interval cannot reproduce the ownership change caused by conversion. Numerical sensitivity over existing parameters is not a substitute for structural coverage.

\section{The disclosure package defines an evidence boundary}
A company filing can incorporate other documents by reference or discuss risks without quantifying them. A reconstruction based only on primary statements may omit material terms in notes, exhibits or subsequent events. The evidence package should state which documents and passages were considered.

Coverage has stages: retrieval, parsing, interpretation and model admission. A page can be retrieved but not parsed; parsed but not understood; understood but outside the current executable profile. These distinctions matter for the completeness claim.

An unresolved passage should remain linked to relevant model areas. A guarantee discussion may block a claim that all contingent obligations are represented. It need not block a simple historical revenue reconciliation. Scope should be query-sensitive rather than all-or-nothing.

\section{Missingness can be informative}

### Ending


Dependency tracking should identify which results need recomputation. A source affecting one loan should not require rebuilding unrelated evidence, but its effects may propagate through liquidity, default and group guarantees. The dependency graph must follow economic consequences as well as direct formulas.

\section{Communicating model risk}
A useful explanation states the result, the assumptions that drive it and the specific unresolved mechanisms that could change it. It does not bury the conclusion under generic warnings. For example, ``cash remains above 14 for all retained histories provided the facility remains drawable after customer default'' identifies a meaningful condition.

If that condition is not established, say so directly and show the alternative result. Avoid presenting a conditional safe outcome as unconditional safety. Equally, do not describe every unresolved mechanism as inevitable disaster. The family should distinguish possible, necessary and unassessed consequences.

The reader should be able to see whether more evidence, a different policy or a better computation would resolve the issue. These are different next steps. A numerical approximation gap cannot be closed by another disclosure if the model already knows the relevant fact; a missing contract clause cannot be closed by more solver iterations.

\section{A defensible stopping point}
A query can be complete within a declared scope even when the entire company model is incomplete. Completion means that the requested target has been computed with the stated guarantees and that material excluded mechanisms are disclosed. It does not mean all uncertainty has disappeared.

A broader product-readiness claim requires broader coverage and evidence. The 150--300-page treatment is a documentation deliverable, not proof of that readiness. The manuscript remains a candidate whose assumptions, sources and proposed methods require continued implementation and human review.

This distinction permits useful progress. It avoids both false certainty and paralysis. The system can answer bounded questions accurately, retain uncertainty honestly and identify the concrete work needed to support stronger conclusions.

## 23. Memory across reporting periods: taxes, vintages, arrears, and future rights

simulation/23-memory-case.tex

### Opening

\chapter[Memory across several reporting periods]{Memory across reporting periods: taxes, vintages, arrears, and future rights}
\label{sim:memory-case}

Two companies with the same current statements can differ because their past creates different future rights and obligations. A simulation that keeps only current totals forgets this memory. This chapter follows several small examples over more than one period. The examples use stipulated accounting and tax rules solely to expose state requirements. They are not claims about a particular jurisdiction's current law.

\section{A loss carryforward}
Assume a teaching tax system with rate 25 per cent, no refund for current losses, unlimited use of carried losses against future positive taxable income and no expiry. Let $L_t$ be unused losses entering period $t$ and $T_t$ taxable income before using them. For positive $T_t$, used losses are $U_t=\min(L_t,T_t)$. Cash tax and next loss balance are
\begin{align}
 \operatorname{Tax}_t&=0.25\max(T_t-L_t,0),\\
 L_{t+1}&=\max(L_t-\max(T_t,0),0)+\max(-T_t,0).
\end{align}
The second equation covers both profit and loss periods under these simplified rules. A positive income reduces available losses; a negative income adds its magnitude.

Company A enters with losses 40 and company B with none. Both have the same current cash, assets and book equity because the example assumes no recognized deferred tax asset. Next period taxable income is 30. A pays no cash tax and retains losses 10. B pays 7.5. Current statements alone do not identify that difference.

In the following period taxable income is again 30. A uses its remaining 10 and pays 5; B pays 7.5. Over two periods, tax is 5 versus 15. Omitting loss memory overstates A's tax. Treating the original loss as an immediate refund would instead overstate its initial cash. Both errors can occur in simple effective-tax-rate forecasts.

\section{Limits and expiry change the recurrence}
Now impose a rule that losses can offset at most 50 per cent of positive taxable income in a period. With $L_0=40$ and $T_0=30$, usable losses are 15, tax is 3.75 and remaining losses are 25. The earlier recurrence is no longer correct.


### Ending


Possible remedies include extending the horizon, adding a justified continuation value, requiring terminal funding coverage or reporting residual obligations separately. Each changes the decision problem in a stated way. No terminal rule is universally correct for all company questions.

\section{A sufficient state is query-relative}
For a one-day payment query, asset age may be irrelevant while settlement dates are essential. For a five-year capital plan, vintages and replacement needs matter. For tax cash, legal loss pools matter; for book equity, deferred tax measurement also matters.

The underlying representation should preserve these quantities where supported, while the active execution state can be reduced for the query. A sufficiency argument names the allowed scenarios, policies, outputs and horizon. It is not a permanent declaration that discarded details never matter.

This is how compact simulation can coexist with rich historical evidence. The system need not replay every old event at every step, but it must retain the memory that determines future events and the provenance needed to reconstruct it after revisions.

\section{Implementation tests across periods}
A loss-pool test should distinguish cash tax from deferred tax measurement and preserve expiry cohorts when required. A vintage test should produce different replacement paths from equal carrying amounts. An arrears test should prevent double expense and apply payments in the stipulated order.

A cure-clock test should distinguish receipts before and after the deadline. An option test should preserve unexercised rights through quiet periods. A horizon test should retain obligations beyond the final reporting date. Each case targets a specific missing state variable.

The tests should also verify legitimate aggregation. Identical loans with the same terms and dates can sometimes be combined additively. Identical inventory units can be pooled by cohort. The goal is sufficient memory, not maximal detail for its own sake.

## 24. Evaluating a real-company simulator: what evidence would support its use

simulation/24-evaluation.tex

### Opening

\chapter[Evaluating a real-company simulator]{Evaluating a real-company simulator: what evidence would support its use}
\label{sim:evaluation}

The exact cases in this part establish useful semantics, but a real-company simulator needs a broader evaluation. It must represent disclosures, preserve important uncertainty, generate coherent events and provide decision-relevant results. These objectives cannot be reduced to one extraction score or one forecast error. This chapter proposes an evaluation design and explains what each result would and would not establish. No empirical evaluation is claimed to have been performed here.

\section{Define the unit of evaluation}
A unit can be a source assertion, a contract, a reporting period, a company history family, a scenario query or a policy decision. Accuracy at one unit does not automatically transfer to another. Correctly extracting a debt total does not establish that maturity and option terms are represented.

A company-period case should identify its document package, entity perimeter, accounting basis, evidence cutoff and materiality scope. A scenario case adds shocks, policies, information and requested outputs. These definitions prevent evaluation from quietly changing the target after seeing results.

The unit should also preserve unresolved content. If a system refuses an unsupported instrument, that can be correct behavior within a bounded profile. The evaluation should distinguish honest refusal from silent omission, while still recording the coverage limitation for the full mission.

\section{Source-to-model traceability}
For each material modeled assertion, a reviewer should be able to reach the source passage and interpretation. Conversely, material source passages should have a disposition: represented, irrelevant to the declared query, unresolved or outside the executable profile.

This bidirectional trace catches different failures. A model assertion without a source may be an assumption or hallucination. A source passage without a disposition may be an omission. A correct numeric total can coexist with a missed covenant note that changes the stress result.

The evaluation should sample across difficult formats and concepts, including scanned notes, tables with overlapping dimensions, incorporated documents and revisions. A convenient set of clean tables is insufficient evidence for whole-filing coverage. The selection procedure and omissions should be recorded.

\section{Annotation and disagreement}

### Ending


Rendered document review is also distinct. It can reveal missing symbols, broken references and unreadable derivations. A clean build cannot establish that a reader understands the argument. The manuscript should remain provisional until actual human comprehension evidence is available.

\section{A proposed staged evaluation}
First establish exact semantics with the synthetic cases in this part. Then evaluate source-to-model coverage on a bounded real disclosure package, preserving unresolved content. Next test historical reconstruction against withheld facts and carefully defined reporting bridges.

Only after those stages should a forecast or policy study claim economic performance. Its plan must identify target companies, time cutoffs, baselines, tuning protocol, primary criterion and uncertainty analysis. A failure at an earlier stage can invalidate interpretation of the later results.

The stages are dependencies, not excuses to stop independent work. Source research, documentation and bounded implementation can continue while empirical data or human review remain pending. The full mission remains open until its specified evidence exists.

\section{What a defensible conclusion sounds like}
A strong narrow conclusion might state that a method reproduces all exact cash and ownership transitions in a declared profile and preserves the tested information restrictions. Another might state that a predictive distribution outperforms a named baseline under a predeclared score with uncertainty evidence on a stated sample.

Neither conclusion should be expanded into universal accounting compliance or company forecasting ability. A failed candidate can be rejected without rejecting the entire uncertainty-preserving approach. A successful small model can justify the next experiment without becoming a production default.

The evaluation program should make those distinctions easy to maintain. That is the practical counterpart of the manuscript's central idea: preserve what is known, preserve what remains possible, and make every stronger conclusion earn its evidence.

## 25. Failures at the joins: how individually plausible methods produce a wrong simulation

simulation/25-interactions.tex

### Opening

\chapter[Failures at the joins between methods]{Failures at the joins: how individually plausible methods produce a wrong simulation}
\label{sim:interactions}

Many serious errors occur where two reasonable methods meet. A contract engine can calculate coupons correctly while an accounting adapter treats them as expense under an incompatible basis. A particle filter can implement its weights correctly while a policy sees hidden future state. A consolidation routine can balance while a liquidity engine spends cash in the wrong entity. This chapter examines these joins and proposes checks that target the interaction rather than one isolated module.

\section{Reconstruction followed by valuation}
Suppose historical debt carrying amount is 100 and an analyst reconstructs face as 100. A valuation engine then prices the promise correctly. If the carrying amount included an unamortized discount or accrued interest, the promise was misidentified before pricing began. The valuation solver can return a precise answer to the wrong contract.

The interface should require a distinction among observed carrying amount, inferred face and supplied valuation terms. If face is unknown, pricing should operate conditionally over its feasible values or request a supported mapping. A test should include face 110, carrying amount 100 and proceeds different from both.

The repair is at the reconstruction boundary, not by adjusting the discount rate until price matches book value. Such calibration would hide the missing contractual amount and could distort every later scenario. A book-to-contract bridge should explain the difference with admitted movements and measurement rules.

\section{Valuation followed by cash forecasting}
A bond's market value falls after rates rise. A cash forecast that treats the decline as a cash inflow because the liability became cheaper creates money unless the company actually repurchases or settles the debt. The valuation change is not itself a financing event.

If repurchase is allowed, it requires a market offer, available cash, quantity and settlement date. The company may realize an economic benefit by paying less than face, but it still spends cash to do so. Accounting gain or loss depends on carrying amount and the applicable treatment.

A discriminating test changes market rates while holding contractual payments and policy fixed. Cash should not change merely from revaluation unless a contract or collateral clause creates a payment. A second test enables repurchase and checks the explicit transaction.

\section{A hedge followed by accounting classification}

### Ending

The first intake therefore records missing evidence explicitly. For each of
the nine closed histories, it retains the complete dated nominal record and
leaves the new receipt and its allocation unknown. Zero-valued historical
components remain visible; an unknown new receipt is not replaced by zero.
Actual prior collection identities submitted as new receipts are rejected
because those collections are already represented. The checked intake has no
financial effects and accepts no positive recovery in this version. Its 50
adverse controls test preservation and refusal boundaries, not recognition of
an actual recovery. The reproducible result is in
\path{data/accounting-master/credit-recovery-intake-20261027/result.md}.

This limited interface makes the remaining work concrete. A positive recovery
method needs authentic receipt evidence, a supported allocation and a justified
post-derecognition treatment. Those additions must preserve the original
write-off finding and financial history, rather than retrospectively rewriting
them to match a later outcome.

## 26. A fully solved risky-debt model before any neural approximation

simulation/26-finite-finance.tex

### Opening

\chapter[A fully solved risky-debt model]{A fully solved risky-debt model before any neural approximation}
\label{sim:finite-finance}

A small structural model can make the financing equations completely transparent. This chapter solves one with two future asset states. It is deliberately restrictive: one period, one creditor, no tax, no fees initially, no bankruptcy costs, no interim distributions and risk-neutral pricing with zero risk-free rate. These assumptions isolate the relationship among promised repayment, proceeds, default, recovery and equity value. They are not a general corporate-finance specification.

\section{Assets and claims}
At the final date, assets available to creditors and shareholders are 60 in the low state and 140 in the high state, each with probability one half. A debt contract promises face $F\geq0$. The creditor receives the smaller of face and available assets. Shareholders receive the positive residual.
\begin{align}
 D(A,F)&=\min(F,A),\\
 E(A,F)&=\max(A-F,0).
\end{align}
For every state, $D(A,F)+E(A,F)=A$. This conservation relation is exact under the stipulated priority and absence of costs. Default occurs when assets are insufficient for the promise, with equality treated as full payment.

Debt proceeds at issuance are the expected creditor payoff because the pricing rate is zero and risk neutrality is assumed. Economic equity value is the expected shareholder payoff. Therefore
\begin{equation}
 P(F)=\tfrac12\min(F,60)+\tfrac12\min(F,140),\qquad V_E(F)=100-P(F).
\end{equation}
The expected asset value 100 is allocated between the claims. Face does not equal proceeds once default becomes possible.

\section{Solve the price schedule by regions}

### Ending

goodwill or consolidated statements can be measured. The next question is how
to preserve that separation through the control-changing exchange.

\section{Separating consideration from the other parts of an exchange}
\label{sim:conversion-transaction-partition}

Obtaining control through a debt exchange raises a question that the separate debtor and creditor worksheets cannot answer alone: which amounts belong to the acquisition of the business? A transaction may also settle an existing relationship or pay for services. Before measuring goodwill, the company must distinguish consideration for the acquired business from effects accounted for separately. The acquisition guidance requires that separation and discusses the reasons for a transaction, who initiated it and its timing; no one indicator by itself settles the classification \citep[paras.~51--53 and B50--B53]{aasb3scope2026}.

Consider an explicitly supplied example in one currency at one measurement date. Four identified components are assigned values of 80 for acquisition consideration, 20 for separate debt settlement, 5 for acquisition costs and 3 for another separately accounted transaction. Their inventory sums to 108, while the declared consideration bucket contains only 80. The difference is not a residual to be forced into goodwill. Nor does this example infer the 20 settlement amount from a loan's face or carrying value: both the amount and its assigned purpose are supplied premises.

The finite calculation gives each component a distinct identity and retains its source, availability date, amount and assigned accounting purpose. It requires an explicit assertion that the supplied inventory is complete for the question. Reordering the four components leaves the same records and sums. An unknown settlement amount is not zero; missing allocation, coverage or source-timing premises leave the requested totals unresolved. Relabelling debt as a previously held equity interest or as acquisition consideration cannot establish the missing accounting premise.

These checks establish arithmetic conditional on the supplied partition. They do not determine the appropriate measured allocation for the intended conversion-to-control transaction. The inspected acquisition paragraphs explain separation and settlement of pre-existing relationships, but do not by themselves establish that loan-specific allocation. The remaining work is to support the relationship treatment, transaction assignments and measurement basis before constructing goodwill and acquired-basis statements.\footnote{\path{data/accounting-master/conversion-control-transaction-20261027/} retains the source inquiry, 33 finite cases including all 24 orderings of the four components, 21 refusal controls and 351 assertions. The calculation produces no goodwill, journals or consolidated report. The saved source inquiry distinguishes an irrelevant supplemental document from unavailable further support; neither is evidence that applicable guidance does not exist.}

\clearpage\label{sim:body-end}
\part{AccDSL product and implementation design}

## 27. The product decision

chapters/01-purpose.tex

### Opening

\chapter{The product decision}
\label{ch:purpose}

A company's accounts describe the financial consequences of its activities,
but they leave much of the activity itself unobserved. Revenue combines many
sales, a borrowing balance combines contracts with different terms, and a
provision combines estimates about uncertain future payments. Aggregation is
necessary for reporting. It also makes the inverse task---recovering economic
history from published reports---fundamentally different from entering known
transactions into a ledger.

AccDSL will preserve this distinction. Its first product is an evidence-backed
representation of a company's historical record. Its second is a set of
compatible histories and current economic states. Its third is a collection of
conditional simulations, each explaining how a particular history, accounting
treatment and business response produces future journals and reports. These
products share identifiers and provenance, so an analyst can move from a
forecast balance to the assumption or disclosure responsible for it.

The recommended design is a small, typed accounting language over a shared

### Ending

\section{What constitutes a useful first implementation}

The first demonstrator should reconstruct three reporting dates and the
intervening annual and interim flows for one company, including at least one
restatement or revised comparative. It must preserve a borrowing-composition
ambiguity and execute the fixed/floating example through both journals and all
affected statement lines. A synthetic company supplies known hidden history;
a public company supplies realistic disclosure and extraction problems. Their
roles differ: the synthetic case tests preservation and rejection of known
alternatives, while the public case tests traceability and practical coverage.

Success is a reproducible chain of evidence and computation, with identified
gaps. A convincing-looking complete ledger reconstructed from incomplete
disclosures would fail this product contract if its assumptions were hidden.
Forecast accuracy requires a later evaluation with historical information
cutoffs and suitable baselines; it is not established by the first demonstrator.

## 28. A complete company and a real disclosure

chapters/13-reference-company.tex

### Opening

\chapter{A complete company and a real disclosure}
\label{ch:case}

\section{What a balance must remember}

Northstar Components is a synthetic seller of one homogeneous good. Its
disclosures, transactions and contract terms are specified together, so we can
check whether reconstruction preserves a known possible history. All amounts
in this example are currency units, not thousands. The company has no foreign
currency, subsidiaries, leases, returns or other comprehensive income. These
are declared features of the example, not assumptions to impose on an imported
company. Its source package and expected results are supplied in
\code{fixtures/northstar.json}.

At the beginning of 2024, Northstar holds cash of 60, receivables of 20,
inventory of 30 and plant costing 100 with accumulated depreciation of 20.
It owes suppliers 20 and lenders 100. Share capital is 50 and retained earnings
are 20. Thus assets of 190 equal liabilities of 120 plus equity of 70.
Inventory consists of six units costing 5 each. The existing plant depreciates
by 10 a year, with no residual value. The loan remains outstanding throughout

### Ending

and the auditor heading support printed page 163, physical page 165, for
navigation \citep[Items 8 and 15; printed pp.~156 and 163]{jpmorgan2023tenk}.
The wrong target is printed page 156, physical page 158. Both use
the same two-page offset, so changing the offset cannot reconcile the targets.
A proposed navigation correction preserves the literal statement. If a
counterfactual earlier view had accepted the wrong target, its selected page
set, bounded search and coverage summary would need reconsideration, while
the literal and an independently sourced statement amount could remain usable.
A one-page negative search could never establish absence from the whole filing.

That review proposal has its own issuer and source dependencies. It supplies
no Apple financial constraint, no posting permission and no observed human
decision. The connected financial result and the separate review proposal can
therefore be inspected together without joining their companies' histories.
Section~\ref{sec:real-package-reference} gives the exact exchange locations
and rejection boundaries that preserve these distinctions.

## 29. Representing a company's historical record

chapters/02-history.tex

### Opening

\chapter{Representing a company's historical record}
\label{ch:history}

Northstar's corrected receivable, Apple's debt measurements and its deferred
revenue show why the source record must retain more than a label and a number.
Section~\ref{sec:apple-revenue} distinguishes a reported balance, a derived
movement, a dated expectation and an unquantified obligation.
Section~\ref{sec:apple-commitments} adds the contract and delivery facts needed
to turn a commitment into a future payment. The procedures below determine
which assertions enter a model and which remain unresolved.

\section{The record is a collection of assertions}

The original record includes financial statements, notes, accounting policies,
auditor opinions, management discussion, segment tables, security terms,
regulatory returns and subsequent announcements. A complete ingestion process
accounts for every page and every extracted block. A complete financial model
is a stronger claim: it would require economically relevant information that
public reports may never disclose. AccDSL therefore reports document coverage,
semantic coverage and simulation coverage separately.

### Ending

example commits financing, service, incurrence and settlement as four
separate events. After settlement, retrying the exact original financing
request returns its original receipt and reports no additional commit;
today's evidence revision does not turn that retry into a new assessment.
Changing the request while retaining the business-event identity is a
conflict. The request's original bindings, historical admission and required
bytes must still validate before receipt lookup.

A new conclusion that the treaty came later does not itself authorize an
entry reducing the committed reinsurance asset. A correction proposal must
identify its accounting treatment, effective period, affected accounts and
opening-balance consequences under the applicable authority. Without that
support, the proposed assessment returns \code{TREATMENT\_UNSUPPORTED},
retains the revised conditional calculation and creates no journal.
Versioning supplies the record of a correction; it cannot supply the
accounting rule that makes the correction appropriate.

## 30. What the literature contributes

chapters/03-literature.tex

### Opening

\chapter{What the literature contributes}
\label{ch:literature}

The research problem crosses accounting, databases, programming languages,
econometrics and document understanding. Each field resolves part of it. The
review below distinguishes results that can be adopted directly, engineering
ideas that need adaptation, and evidence that does not establish the intended
product capability. Source versions and technical anchors are recorded in the
accompanying research ledgers. The search includes work outside the original
collection, with public-index searches and backward and forward citation
searches through 2 October 2026. It is a scoped design survey, rather than a
claim to enumerate every paper in these fields.

\section{Accounting structure and company dynamics}

\citet{nehmer1997}, especially Sections 2--5, supply a useful algebraic
starting point: balances occupy a structured state space, transactions change
that state, and aggregation relates detailed accounts to reports. This supports
a distinction between conservation constraints and permitted transactions.
An entry can conserve the accounting total and still be an inadmissible

### Ending

\clearpage
\section{The remaining design problem}

The combined literature provides algebra for journals, semantics for missing
information, temporal storage, provenance, contract languages, rule languages,
inference methods and extraction tools. The unresolved integration problem is
to retain their distinctions while connecting them: a disclosure constrains
economic histories; a history supplies contract and behavioural state; a
scenario drives events; accounting rules produce journals; reporting rules
render statements; and every step remains explainable.

The design is therefore an integration proposal with several local
mathematical constructions. Its originality and empirical advantage have not
been established by this survey. Its practical merit will depend on the
acceptance cases, accounting review and comparative implementation work in
Chapter~\ref{ch:validation}.

## 31. Architecture and reuse

chapters/04-architecture.tex

### Opening

\chapter{Architecture and reuse}
\label{ch:architecture}

\section{One representation, several authoring methods}

The architectural centre is a typed intermediate representation (IR), not a
text parser. A document extractor, a human editor, a Python library and the
AccDSL compiler all create the same records. This allows a modeller to begin
with a reviewed structured file and later add convenient notation. It also
allows source extraction to improve without changing accounting semantics.

\begin{figure}[ht]
\centering
\begin{tikzpicture}[node distance=7mm,>=Latex,
 box/.style={draw=ink,rounded corners,align=center,text width=112mm,
 minimum height=10mm,font=\small,fill=papergray}]
\node[box] (e) {Documents and tagged filings\\immutable evidence, source spans and reporting contexts};
\node[box,below=of e] (h) {Typed historical representation\\observations, entities, contracts, mappings and constraints};
\node[box,below=of h] (i) {Compatible histories and declared assumptions\\discrete alternatives, continuous families, optional weights};
\node[box,below=of i] (s) {Scenario execution\\economic events, accounting rules and balanced journal batches};

### Ending

between feasible sets and distributions. These responsibilities cannot be
delegated implicitly to whichever parser or solver is convenient.

External components receive narrow requests and return typed responses.
A contract adapter returns scheduled events, cash-flow quantities, state
changes and source/model references; it does not directly mutate the ledger.
A valuation adapter returns a measure, currency, date, method and numerical
status; the accounting package decides whether and where to recognise the
change. A solver returns feasibility or bounds with scope and completeness
status. A language model proposes source-linked mappings or interpretations;
it cannot commit an unsupported assertion as fact.

The architecture consequently permits deterministic reference execution,
alternative solvers and later acceleration without changing the meaning of a
historical observation or a journal entry. Performance work begins only after
the same semantic cases pass through these interfaces.

## 32. Historical compatibility and future simulation

chapters/05-mathematics.tex

### Opening

\chapter{Historical compatibility and future simulation}
\label{ch:math}

\section{Define what is observed before inverting it}

Let $D_k$ be the disclosures available under information cutoff $k$. Each
numeric observation $d_i$ has a context: entity or group perimeter, concept,
measurement basis, dimensions, currency, period and precision. These contexts
are part of the observation operator, not additional columns that can be
discarded after extraction.

A candidate history $h$ contains an opening economic and accounting state,
events through the last historical date $T$, contract terms, accounting
policies, consolidation relationships and latent quantities. Let $M$ denote
the declared model scope: its event templates, admissible rule versions and
allowed unknowns. It excludes arbitrary events that the chosen model has no
way to represent. The reporting operator $O_i(h)$ produces the quantity to
which observation $i$ refers, including its basis and perimeter.

Reported numbers are often rounded. If a number $v_i$ is rounded to the nearest

### Ending

one fully specified model. Financial filings alone do not establish these
causal equations or identify their effects.

An intervention request must name its target, replacement equation, structural
parents and disturbance law and satisfy acyclicity or a separately supported
equilibrium rule. Correlated disturbances remain joint. The initial company
profile supports imposed exogenous stress; the continuous and causal methods
described here require separately admitted extension schemas and signatures.
They do not silently expand the initial finite-law interface.

At every decision date, behavior and measurement receive the admitted historical
view and permitted simulated past. The scheduler's knowledge of a complete
future stress path is not permission for a manager to foresee it. A perfect-
foresight policy needs an explicit additional assumption. Common random numbers
can improve a paired numerical comparison while establishing no causal effect
in actual company data.

## 33. The accounting language

chapters/06-language.tex

### Opening

\chapter{The accounting language}
\label{ch:language}

\section{What the current language can express}

A company model needs to keep disclosures, possible histories and chosen
methods distinct as its accounts evolve. A reported balance constrains a
history; it does not reveal every contract or transaction that generated it.
A collection policy supplies a behavioural assumption; it does not establish
what a customer will pay. An accounting method turns an eligible event into
state changes and postings; a balanced result alone does not establish that
the method applies. The language makes these distinctions explicit so that
reports retain the meaning of the facts and assumptions behind them.

The current design has several checked, bounded language profiles. Together
they cover source-constrained histories, conditional company paths, selected
shared-book operations and complete method authoring. Their interfaces are
explicit, but they are not yet one complete whole-company grammar.
The earlier source compositions in Sections~\ref{sec:common-program-authoring}
and~\ref{sec:invariant-source-authoring} make complete methods, registries,

### Ending

\code{UnsupportedTreatment} & Add a reviewed capability or leave the affected
output incomplete.\\
\code{UnbalancedBatch} & Reject the atomic update and diagnose the posting rule.\\
\code{SolverIncomplete}, \code{NumericalFailure} & Preserve the target and
inputs; repair or change the computational method.\\
\code{InsufficientSimulationState} & Add declared conditional assumptions or
request a family of results.\\\bottomrule
\end{tabular}
\end{center}

Warnings can describe low extraction confidence or an approximate economic
model, but they do not replace these errors. A required unknown input prevents
a concrete unconditional result. The analyst can add a declared conditional
assumption, request bounds, or leave that output incomplete. Every path has a
different, explicit result type; there is no generic fallback to zero.
\end{minipage}\par

## 34. Reconstruction and execution procedures

chapters/07-execution.tex

### Opening

\chapter{Reconstruction and execution procedures}
\label{ch:execution}

\section{Ingest, reconcile and construct histories}

The historical procedure starts with a filing manifest. It records documents,
reporting dates, publication dates, revisions and expected statements and
notes. Tagged filings are parsed through an XBRL adapter; PDF and HTML sources
are segmented into text, tables, captions and references. The original bytes
and extraction output remain immutable. Re-running an improved extractor
creates a new extraction version with links to the same source.

For each table, the importer first resolves headers, units, signs, periods and
dimensions. It then proposes concept mappings. A deterministic validator checks
subtotal arithmetic, duplicate facts, comparative consistency and cross-note
references. Every proposed repair creates a new reading. The system may suggest
that an OCR value is 10 rather than 70, but only a reviewed correction or an
explicit alternative allows that reading into a validated model.

Reconciliation proceeds from local totals to movement schedules. A debt bridge

### Ending

future outcomes are inaccessible. A stress path may be announced in advance,
but this is an explicit visibility policy. Otherwise management sees only its
current and past values. A bank's allowance at the opening date may use a
forecast distribution of defaults; it must not inspect the outer simulation's
future realised default. Inner valuation randomness has a separate stream
domain from outer realised outcomes.

Funding follows a declared waterfall: available cash, committed eligible
facilities up to their limits, and separately authorised capital actions.
Each action checks collateral, covenants and settlement timing. If an amount
remains due, record an economic funding failure and the unpaid obligation.
If required valuation or accounting is unsupported, stop the affected
dependencies as incomplete. The branch manifest preserves the last committed
state, completed outputs, unavailable outputs and reason. These distinctions
let an analyst see a meaningful bad outcome without confusing it with broken
computation.

## 35. Accounting methods for an operating company

chapters/08-modules.tex

### Opening

\chapter{Accounting methods for an operating company}
\label{ch:modules}

\section{A common core with distinct accounting books}

The common core governs evidence, time, money, events, journals and provenance.
Reporting standards govern recognition, measurement and presentation within
that core. The design preserves three levels of meaning: economic terms such
as a promise to pay cash; an accounting treatment under a particular standard;
and a company's reported label or extension. These levels are connected by
explicit rules and mappings, rather than collapsed into one universal chart
of accounts.

A rule package includes a standards register with jurisdiction, issuer class,
effective dates, transition provisions, permitted elections, paragraph
references, implementation version and tests. The package selector uses the
entity, reporting basis, period and adopted elections. It must distinguish a
standard's mandatory effective date from permitted early adoption. For example,
the IFRS Foundation's IFRS 18 overview states an effective date of 1 January
2027 with earlier application permitted \citep{ifrs18}. A 2026 historical

### Ending

Recheck operative amendments/transition; no automatic extension\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.47\columnwidth}\raggedright
Issuer policy discloses LIFO, regulator text unavailable\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
Retain issuer assertion; do not upgrade it into universal US authority\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.47\columnwidth}\raggedright
Foreign basis label replaced by local label\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
Reject as a standards conversion without recognition/measurement bridge\strut
\end{minipage}\tabularnewline
\bottomrule
\end{longtable}

These decisions establish a common procedure and specific proposed treatments. The recovered ASBE lease notice and tax interpretation support the stated application schedules and conditional example. Broader authority coverage remains incomplete: operative US sources, ASBE sector methods, actual tax law and presentation conditions, and the applicable amendment and entity-election evidence still require internal investigation.

## 36. Financing, ownership and the group boundary

chapters/14-financing-groups.tex

### Opening

\chapter{Financing, ownership and the group boundary}
\label{ch:financing-groups}

A company can preserve the same operating assets while changing who supplies
its funding and who shares its results. The following cases move from debt
cash flows to ownership, then to the reporting boundary of a group. Each
numerical example states its own contract; the coupon-bearing convertible
below and the later zero-coupon compound example are different instruments.

\section{Debt and hybrid financing}

The contract layer for a debt instrument stores issuer and holder perspective,
currency, issue and settlement dates, issue proceeds and legal face amount.
Its payment terms include coupon/index/spread, reset and fixing dates,
day-count convention, payment calendar, amortisation schedule and maturity.
Its rights and protections include seniority, collateral, covenants, options,
conversion terms, guarantees and linked hedges. Missing terms are
explicit unknowns. A single carrying amount cannot stand in for this record.

The accounting layer stores the classification decision and its evidence,

### Ending

initial effect to accumulated translation differences. Hyperinflationary
functional-currency equity items also use the estimated initial rate.
Comparatives are not restated for this amendment. Keep these transition
adjustments distinct from subsequent-period profit or OCI
\citep[IAS~21.60M]{eu20242862}.

The accompanying disclosures identify affected currencies and restrictions,
transactions and carrying amounts, rates, estimation methods and assumptions,
and exposure to risk. A foreign operation also needs the additional
information in paragraph A20, including relevant support arrangements
\citep[IAS~21.57A--B, A18--A20]{eu20242862}.
These methods extend the documentary group design. They do not silently add
fields or supported events to the closed \texttt{GroupForeignOperation/1}
exchange profile; its successor must explicitly bind the additional histories
and assessments before an implementation can claim these operations.


## 37. Credit losses and the bank balance sheet

chapters/15-banking.tex

### Opening

\chapter{Credit losses and the bank balance sheet}
\label{ch:banking}

The funding and default distinctions become central in a bank. A loan creates
an asset, customer payments affect settlement liquidity, and a forecast of
credit loss affects an allowance before cash is lost. The first case connects
funding to a simple allowance; the later dated loan schedule separates credit
stages, interest recognition and eventual recovery.

\section{Banks: accounting capital is not regulatory capital}

A bank package needs instrument and cohort states for loans, securities,
deposits, wholesale funding, repos, derivatives, collateral and commitments.
For interest-rate analysis, currency and repricing buckets matter alongside
remaining maturity. For credit analysis, exposure, default state, loss severity,
recoveries, guarantees and their dependencies matter. For liquidity analysis,
deposit behaviour, collateral eligibility, encumbrance and payment timing matter.
These states can be represented at an explicitly chosen aggregation level;
the public record rarely identifies every contract.


### Ending

as one transaction. A repeated identifier with identical content has no
second effect; a changed payload conflicts. Lost acknowledgement preserves
the possible committed and uncommitted histories until reconciled.

Credit and collateral records likewise retain the original loan, current and
original terms, dated risk assessments, information cutoff, receipt law,
discount convention and source dependencies. Missing legal rights or credit
findings produce unresolved or explicitly conditional measurements. Actual
credit calibration, fees, continuing involvement and revolving collateral
remain separate method obligations. The historical Australian cases do not
automatically satisfy the distinct US prudential profile in
Section~\ref{sec:bank-prudential-connection}.

A RegulatoryAssessment reads an accounting view and an independent jurisdiction, date, perimeter, eligibility, deductions and exposure-weight policy. It outputs capital components, RWA/exposure measures, liquidity measures and reconciliations with their distinct denominators. Illustratively, equity 20 minus an assumed regulatory deduction 2 yields capital 18; assumed RWA 125 gives 14.4\%. Those inputs are synthetic, not a Basel rule, national capital approval or default threshold. Selected dated US national capital rules are inspected in the surrounding bank inquiry. A connected accounting-to-capital reconciliation for the same bank still requires its applicable perimeter, eligibility, deductions and exposure facts; the illustrative inputs above do not supply those facts.

Behavior under capital/liquidity constraints is a separate economic model. Specify feasible actions, objectives, information set and ties before solving; failure to find an action returns policy\_failure or default under the stated contract. Halaj/Behn sources can motivate candidate behavior but cannot calibrate it for an individual bank. A forecast experiment must compare simple fixed-book, contractual runoff and explicitly estimated policy baselines with time-safe data, before claiming a predictive improvement. CECL and other bases retain separate authority/method branches in the dated-authority discussion.

## 38. Insurance service, finance and claims

chapters/16-insurance.tex

### Opening

\chapter{Insurance service, finance and claims}
\label{ch:insurance}

An insurer receives cash before much of its service is delivered. Cash premium,
service revenue and profit therefore follow different schedules. A short
coverage example first connects gross insurance to reinsurance. The subsequent
two-year cases introduce unearned profit, loss allocation and finance one
change at a time.

\section{Insurance: cohorts and future service}

An insurer requires policy cohorts or groups with issue dates, coverage,
premiums, benefits, expenses, lapses, claims development, guarantees and
reinsurance relationships. Asset portfolios need their own contracts and
valuations. The liability state must distinguish expected future cash flows,
discounting, risk adjustments or margins, unearned profit measures where
applicable, incurred claims and movements between opening and closing states.
The IFRS 17 overview's distinction between measuring future cash flows and
recognising profit as service is provided motivates this separation
\citep{ifrs17}.

### Ending

with 88\% for 2023 and 87\% for the comparative period. These are dated
properties of the insurer's calculation, not universal IFRS parameters.
The rate also cannot be imported into the separate fair-value calculation
merely because that discussion mentions cost of capital. Reconstructing an
individual group still requires its cash flows, capital projections, curves,
allocations and supported transition-method choice
\citep[pp.~165, 183 and 185]{munichre2023annual}.

\clearpage
\hypertarget{interfaces-exclusions-and-acceptance-cases}{
\section{Interfaces, exclusions and acceptance cases}\label{method-insurance-methods-interfaces-exclusions-and-acceptance-cases}}

Insurance events are group\_recognize, premium\_settle, service\_release, claim\_incur, claim\_settle, assumption\_change, onerous\_change and treaty\_change, each bound through the event-basis, authorization and commit contracts to the exact group/version, evidence and information view. Journals and component roll-forwards must reconcile independently; a component reallocation is not always a net liability change. Invalid grouping, missing rate/law, unsupported option valuation, ambiguous contract boundary or unknown service units produces the corresponding unresolved/outside-scope result. Failed numerical paths retain their coverage/mass, without successful-only normalization. Modified contracts need the applicable derecognition analysis; no new ID can erase unfavorable old-group obligations.

Initial transition requires an actual method choice and eligibility for full retrospective, modified-retrospective or fair-value transition under AASB~17 Appendix C, with acquisition, grouping, past service and historical-rate records. This collection does not claim an executed transition or a general VFA valuation. The nonzero-rate general case and onerous allocation through expiry above are finite specification examples. Required later acceptance still includes a priced guarantee, acquisition/reinsurance interaction, transition and actuarial backtesting. These retained obligations prevent the two-year illustration from being described as full insurance-domain readiness.


## 39. Implementation contracts

chapters/09-implementation.tex

### Opening

\chapter{Implementation contracts}
\label{ch:implementation}

\section{Reference implementation and component boundaries}

The proposed reference implementation uses Python for orchestration and a deterministic
reference evaluator, exact decimal/rational arithmetic for booked amounts,
SQLite for transactional metadata and versioned records, and columnar files
for large scenario outputs. DuckDB is an optional analytical reader. These
are convenience choices justified by inspectability and modest initial scale;
they do not establish production performance. The IR and conformance tests
allow a later compiled executor without changing accounting meaning.
Committed journals, economic deltas, receipts and branch heads belong to the
one transactional store, including for simulation branches. Columnar files
hold derived analytical exports, never independently writable committed books.

\begin{lstlisting}
accdsl/
  evidence/       documents, spans, filing contexts, extraction versions
  model/          typed IR, entities, books, symbols, contracts

### Ending

setup, requirement and release metadata; they do not recommend a latest release
or assert that every later Python version works.

pdfminer adds charset-normalizer and cryptography. Its optional image dependency
on Pillow is separate from pdfplumber's unconditional Pillow requirement.
No extra is selected by this proposal. Likewise, a package with no declared
Python dependency can still contain native libraries and third-party notices.
The inspected pypdfium2 metadata expressly distinguishes its own licences from
dependency licences \citep{pypdfiummetadata2026}. An empty Python dependency field cannot certify the
native runtime or its distribution terms.

Before admitting an environment, choose its actual platform and Python build,
resolve all selected direct and transitive versions, retain their distribution
hashes and notices, and test the exact source-preserving exchange. The source
declarations make that task concrete. They leave the installation, native
compatibility and component-specific terms as separate evidence obligations.

## 40. Acceptance and implementation sequence

chapters/10-validation.tex

### Opening

\chapter{Acceptance and implementation sequence}
\label{ch:validation}

The reference cases now make several of the acceptance obligations executable
as design checks. Northstar provides full statements and a known compatible
history; Apple supplies real source contexts and a bounded marginal stress;
bank, insurance, consolidation and inventory fixtures test the core's broader
state requirements. They do not constitute a production implementation.

\section{Three different questions require different evidence}

Engineering correctness asks whether the implementation follows the specified
types, transitions and arithmetic. Accounting validity asks whether the
selected rules faithfully implement the applicable standards and disclosed
policies. Scientific validity asks whether the economic assumptions and
uncertainty representation support the intended forecasts or comparisons.
A balanced journal answers only part of the first question.

The implementation must therefore maintain separate validation results.
Compilation and deterministic examples cannot establish forecasting quality.

### Ending

provisional engineering limits for bounded failure behaviour, not measured
capacity or scientific defaults. They must be configurable and recorded.
Reaching a limit yields partial coverage with the unvisited formula/cells,
never an exhaustive-history claim. Peak memory and latency are measured only
after an implementation exists; a slower but semantically correct result
does not become a scientific failure.

Engineering release needs compiler/API equivalence, transactional replay and
adapter subset checks. Accounting release additionally needs paragraph-level
authority, dated applicability, exact fixtures and independent domain review
for every promoted operation. Forecast promotion additionally needs preserved
information sets, the stated baseline ladder, statistical uncertainty and
critical-regime vetoes. Human comprehension review remains separate from all
three. This version supplies a richer design candidate and reference
checks while preserving these outstanding acceptance decisions.
\appendix

## 41. Portable operation reference

chapters/17-portable-reference.tex

### Opening

\chapter{Portable operation reference}
\label{app:portable-interfaces}

These proposed versioned operations share the request and result envelope in
Section~\ref{sec:versioned-operations}. Required inputs are explicit even when
a list is empty. An expected head mentioned below refers to the common envelope,
never a second argument. The registry is a lookup reference after the financial
and transaction meanings have been explained in the body. These are specified
exchanges, not deployed endpoints.

\section{The corporate exchange package}
\label{sec:corporate-exchange-reference}

The Northstar example in Section~\ref{sec:northstar-portable} supplies a closed
instance of \code{CorporateJointHistory/1}. Its package is retained at
\path{data/accounting-master/corporate-portable-20261015/}. The files
\path{record-schemas.json} and \path{portable-exchanges.json} contain the closed
record bodies, signature-specific arguments, complete immutable records,
required byte references, exact submitted request bytes, results and the
before/after store worlds. The accompanying semantic definition is

### Ending

leaves both results null. A rejected proposed EPS projection can retain the
independently calculated company result while returning null EPS. Missing
bytes or incomplete findings are unresolved; different known methods are
unsupported; invalid shapes, changed bytes or projection mismatches reject.
Mutations are always empty and acceptance is
\code{conditional\_documentary\_only}. The schemas also retain the selector's
combined \code{blocked} status for a propagated unresolved/unsupported result.

This exchange checks two explicit documentary worlds. It supplies neither
an arbitrary-company import nor a migration of the whole financing profile.
The separate early-conversion policy in Section~\ref{sec:eps-actual-conversion} is
limited to the unchanged original equity right; this exchange still checks
conversion at maturity. Other early-conversion terms, differing tax bases,
broader rights, actual authority and live publication require their separate
methods and evidence. Independent technical and human/domain acceptance
remain pending.

## 42. Core grammar, records and execution details

chapters/11-contracts.tex

### Opening

\chapter{Core grammar, records and execution details}
\label{app:contracts}

\section{Preserved Core 0 teaching grammar}

The grammar governing the preserved Core 0 teaching examples is reproduced
from \code{spec/core-0.lark}. It does not enlarge the first matched text
frontend beyond the portable profile described in the body. Names are
case-sensitive ASCII identifiers; strings are UTF-8 with JSON escaping. All
literal words in the grammar are reserved. The companion contract specifies
valid dates, exact rational literals, argument arity, type/context checks and
package resolution. A syntax parse is not semantic validation.

\lstinputlisting[basicstyle=\scriptsize\ttfamily]{spec/core-0.lark}

\section{Required core record definitions}

The historical closed machine-readable definitions remain in the original
design directory at \path{spec/core-ir.schema.json}. They define contexts, source spans,
observations, narratives, coverage units, mappings, partitions, entity/control

### Ending


\begin{center}
\begin{tabular}{lll}
\toprule Requirement & Primary implementation area & Conformance cases\\\midrule
R1 & Evidence registry and extraction adapters & T03, T09\\
R2 & Context/version model and cutoff queries & T03, T04\\
R3 & Types, mappings and package selection & T02, T12, T13\\
R4 & Symbols, choices and constraint graph & T05--T10, T14\\
R5 & Posting, closing and consolidation & T01, T11--T13\\
R6 & Contract and behavioural interfaces & T05, T11, T15, T16\\
R7 & Conditional output and probability types & T06, T07, T18\\
R8 & Explanation graph and report dependencies & T09, T11--T13\\
R9 & Capabilities and versioned modules & T02, T14--T16\\
R10 & Run records, scheduler and replay & T03, T17, T18\\\bottomrule
\end{tabular}
\end{center}

## 43. Research basis and outstanding review

chapters/12-research.tex

### Opening

\chapter{Research basis and outstanding review}
\label{app:research}

\section{Source collection and reading scope}

The initial research catalogue records 32 verified paper PDFs: 25 retrieved
from external sources and seven preserved copies from the original collection.
Later source inquiries retain additional papers and their technical reading
in separate versioned records, including the reserve-risk and bootstrap
studies used in Chapter~12. The initial count therefore describes that
catalogue, not the full expanded library.
Filenames use the title, first author's surname and year. Publication years
are used where an archived working version underlies a later publication;
the catalogue identifies the actual version read. The original collection
has not been renamed or modified. Standards pages, contract specifications,
software source snapshots and metadata are stored separately from papers.

The survey considered accounting algebra and DSLs, corporate and bank
simulation, incomplete and temporal databases, provenance, inverse problems,
partial identification, model averaging, causal scenarios, contract languages,

### Ending

bounded populations and relevance decisions. Screening is still distinct from technical reading: deferred
provenance, temporal-query, bank-optimisation, extraction and actuarial
follow-ups remain identified expansion risks. An omitted-paper reason does
not make that paper technically reviewed or make the survey exhaustive.

This document specifies the product; it does not report a completed engine.
The companion review records cover deterministic example arithmetic,
bibliography/build checks, rendered-page inspection and author review. Human
comprehension review, independent accounting review and implementation
conformance remain separate future evidence. They are not replaced by a clean
LaTeX build or by the quantity of literature collected.
\bibliographystyle{plainnat}
\begingroup\raggedright
\bibliography{references}
\endgroup
\end{document}
