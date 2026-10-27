# Bounded P18 sectors integration review

You are an independent read-only reviewer. No tools, files, commands, edits or further reviewers. Review only this self-contained packet, not the whole proposal.

Check bank and insurance schedules against accepted fixtures. Distinguish initial unconditional default law, survival conditioning and changed forecast; gross/net EIR, allowance and statements; CSM/RA/LRC/LIC, nonzero discount and reinsurer separation. Find actual calculation or source-boundary errors.

Accepted P16 architecture and P17 scoped methods are comparison baselines, not proof of full readiness. The candidate builds (122 pages, zero serious LaTeX warnings); render inspection is separate. Current ASC, whole real-company semantics, insurance transition/full VFA, actual regulatory/actuarial data, and human acceptance remain open. Do not label those honestly retained gaps a new P18 transcription failure. Source provenance is frozen; no new literature search is claimed.

Budget the review to finish in one response. Give at most 6 concrete findings, each with exact file/section and necessary repair, plus a brief reason for the verdict. Focus first on material mismatches; do not perform or narrate an exhaustive re-derivation of every case. Limit your final answer to 1000 words. End with exactly VERDICT: AGREE or VERDICT: REVISE. AGREE accepts only this packet's integration scope, with any minor nonblocking findings explicitly labelled.


## FILE docs/design/proposal/manuscript/chapters/15-banking.tex

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

Loan origination can debit loans and credit a customer deposit in the bank's
book. Subsequent transfer to another bank produces settlement flows. Treating
all loan growth as an immediate cash outflow would therefore encode a specific
funding assumption, not a universal banking identity. A system-wide model must
also link counterparties and settlement assets; single-company simulation
records external counterparties without claiming to close the whole economy.

An allowance calculation is a dated measurement based on forecast information.
For a single horizon, let EAD be a fixed exposure at default, PD the probability
of default, and LGD the mean loss fraction conditional on default. Ignoring
discounting, the illustrative expected loss in currency units is
\[
 L=EAD\times PD\times LGD.
\]
With exposure 100, default probability 0.02 and loss given default 0.4, it
produces 0.8. Changing those inputs to 0.04 and 0.5 produces 2, so the allowance
increase is 1.2 if there are no other movements. This calculation is a
demonstration model. A standard-specific expected-credit-loss implementation
must determine horizon, staging or other classification, discounting,
forward-looking information, write-offs and purchased-credit-impaired or
other special cases. The simple formula is not an IFRS 9 or US GAAP compliance
implementation.

Regulatory capital is computed in a separate prudential layer with its own
perimeter, eligibility, deductions, risk weights and transition provisions.
Accounting equity feeds a reconciliation to capital; it is not automatically
Common Equity Tier 1. Liquidity and capital constraints influence the
management policy, which in turn generates asset sales, funding or capital
events. A breached ratio can be an economically meaningful scenario outcome.
No hidden capital injection is permitted to repair it.

\section{A bank's cash, allowance and capital in one path}

The bank reference state contains settlement cash 30, gross loans 100,
allowance 0.8, deposits 110 and equity 19.2. Originating a loan of 20 first
debits loans and credits the borrower's deposit. A subsequent transfer of 15
to another bank debits deposits and credits settlement cash. Loan origination
and external cash use are consequently distinct events. Receive loan interest
6 in cash and credit deposit interest 2 to customer balances. Remeasure the
allowance to 2.4, posting an additional loss of 1.6. The resulting state is
cash 21, gross loans 120, allowance 2.4, deposits 117 and equity 21.6.
Net assets are $21+120-2.4=138.6=117+21.6$.

Now 25 of deposits runs off. The declared funding policy uses cash first,
then a committed facility with limit 10. It draws 4 and settles 25, leaving
cash zero, deposits 92 and wholesale debt 4. A runoff of 40 instead leaves
9 unpaid even after the maximum facility draw. The simulator records default
and retains the unpaid deposit obligation. It does not assume unlimited
central-bank or shareholder funding.

The prudential calculation is a separate, illustrative policy. Deduct 2 from
accounting equity to obtain capital 19.6; apply a 75\% risk weight to gross
loans for risk-weighted assets 90. The resulting ratio is $19.6/90$.
Neither the deduction nor the weight is a Basel default. Actual prudential
packages require jurisdiction, exposure class, eligibility, buffers and dated
rules, with a reconciliation from the accounting book. The structure follows
the need to model capital and liquidity jointly in
\citet[Section 2]{behn2019}, without transferring that paper's estimated
preferences or shock parameters to this bank.

For a richer credit adapter, partition borrower cohorts by currency, vintage,
credit state, remaining maturity, collateral and measurement category. At date
$t$, supply scenario probabilities, conditional default-time probabilities,
exposure paths, conditional loss severity and discount factors. Its expected
loss calculation has the declared form
\[
 L_t=\sum_s p_s\sum_{k\in H}
  d_{t,k}\Pr(\tau=k\mid s,\mathcal F_t)
  \E[\mathrm{EAD}_k\mathrm{LGD}_k\mid\tau=k,s,\mathcal F_t].
\]
The conditional product expectation retains dependence between exposure and
severity. The horizon $H$ concerns eligible default times; associated cash
shortfalls may continue later. The rule package decides twelve-month versus
lifetime default scope, credit-state transfers, interest basis and write-off
recognition. Changes in allowance must be attributed to origination,
derecognition, transfers, revised expectations, currency and write-offs.
Contract and prudential support can be specified now, while full IFRS~9/CECL/
ASBE classification and paragraph-level validation remain later obligations.

\input{sections/bank-methods}



## FILE docs/design/proposal/manuscript/chapters/16-insurance.tex

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

The module API accepts policy/cohort state, economic assumptions, non-economic
assumptions and information date. It returns a measurement vector, movement
attribution and proposed recognition events. Experience differences, changes
in assumptions, finance effects and service effects remain separately
identifiable. Reinsurance held has its own record and measurement; it is not
an automatic percentage offset to every insurance liability.

Scenarios can alter discount curves, mortality, morbidity, lapse rates,
inflation, catastrophe losses and policyholder behaviour. Their joint
dependence and cohort exposure must be declared. A portfolio total can match
history while hiding very different guarantee and duration profiles. This
makes alternative economic histories especially valuable, but also limits
what public-data reconstruction can identify. A full insurance package needs
actuarial and accounting review beyond the core release.

\clearpage
\section{Insurance service and reinsurance in a complete cohort}

The example uses one-year policies and a one-year proportionate treaty starting
when those policies are recognised, with uniform service for each. Both groups
qualify for premium allocation through the one-year conditions in paragraphs
53(b) and 69(b); paragraphs 62--62A determine treaty recognition. Assume no
acquisition cash flows, investment components, significant financing or onerous
remaining coverage. Claims and recoveries are expected within a year of the
claims being incurred. The inspected AASB~17 text incorporating IFRS~17 specifies
the movements in paragraphs 53--59, allocation in B126 and separate reinsurance
requirements in 63--70A \citep{aasb17}. Gross and ceded groups retain distinct
identities.

Begin with capital and cash of 20. Receive premium 120 and recognise a
remaining-coverage liability of 120. Pay reinsurance premium 24 and recognise
a coverage asset of 24. After half the uniform service, recognise revenue 60
by releasing gross coverage and reinsurance expense 12 by releasing its
coverage asset. Estimated incurred claims are 40, of which 30 is paid;
the remaining-claim risk adjustment is assumed to be 2. Gross claims expense
is therefore 42 and incurred-claims liability is 12. Assume the treaty
reimburses half the gross expected claims, recovery cash of 15 has arrived,
the risk transferred is valued at 1, and reinsurer non-performance has zero
expected effect in this example. The reinsurance claims asset is
$20+1-15=6$, and recovery income is 21.

Cash is $20+120-24-30+15=101$. Assets are cash 101, remaining reinsurance
coverage 12 and claims recovery 6, totalling 119. Liabilities are remaining
gross coverage 60 plus incurred claims 12, totalling 72. Profit is
$60-42-12+21=27$ and equity is $20+27=47$. These balances reconcile without
netting reinsurance against the insurance liability. If counterparty credit
risk changes, the recovery measurement changes through its own inputs; it
does not mechanically halve every gross liability or risk adjustment.

Longer-duration business adds a fulfilment-cash-flow vector, discount curve,
risk adjustment, contractual service margin, loss component and coverage-unit
schedule. Select portfolio and annual cohort, assess onerous grouping, project
cash flows within contract boundaries, discount with the declared financial
assumptions, measure non-financial risk separately, and attribute subsequent
movements to new business, experience, assumptions, finance and service.
Future-service changes adjust the supported service-margin operation subject
to the loss rules; current/past-service effects enter their specified result
components. Unsupported variable-fee, transition or loss-recovery operations
must stop those dependencies explicitly. A PAA example does not implement
these longer-duration methods by implication.

\enlargethispage{3\baselineskip}
An actuarial reserve adapter also needs a concrete estimation contract.
For cumulative claims $C_{i,k}$ by origin year $i$ and development year $k$,
the chain-ladder point method estimates each factor from matched observed
cells, $\widehat f_k=\sum_i C_{i,k+1}/\sum_i C_{i,k}$, then projects the
latest cumulative claim along the remaining factors. A triangular example
with rows $(100,150,180)$, $(120,180)$ and $(140)$ gives factors 1.5 and
1.2, outstanding amounts 36 and 112 for the unfinished rows, and total 148.
\citet[Sections 2--3, equations (1)--(3)]{mack1993} makes explicit the
conditional-mean and variance assumptions and independence across origin
years; its aggregate-error discussion retains dependence from shared estimated
factors. A single final-development observation cannot supply an empirical
tail variance without an additional assumption. The adapter therefore returns
the point projection and marks uncertainty estimation unavailable in this tiny
example. It supplies neither a full predictive distribution nor an IFRS risk
adjustment. Calendar effects, inflation, changing claims handling and tail
selection require separate sensitivity and validation before real use.
\input{sections/insurance-methods}



## FILE docs/design/proposal/manuscript/sections/bank-methods.tex

\hypertarget{state-and-event-order}{%
\section{State and event order}\label{method-bank-methods-state-and-event-order}}

The dated credit methods use the selected amortised-cost, interest and impairment provisions of AASB 9 \citep{aasb9dated}. The following loan has different inputs from the earlier liquidity example, so its allowance and final equity are calculated separately.

BankState contains cash/reserves by settlement venue and currency; deposits by customer, access rights and maturity; assets by contract, gross carrying amount, allowance, original EIR, accrued cash flows, collateral and credit state; undrawn commitments; funding lines and covenants; accounting equity; regulatory mappings; and evidence/information views. LoanState separately retains origination credit risk and current risk, SICR finding, credit-impaired/POCI status, forbearance, modification, write-off and recovery history. Aggregating by today's loan balance alone loses both staging evidence and later response to shocks.

Each time step first admits information known then, forms permitted credit and liquidity forecasts, chooses behavior under that information, and schedules due events. Accrual, actual settlement, impairment measurement and regulatory queries have separate business identities. A deposit received from outside debits cash/reserves and credits deposit liability. A loan credited to the borrower's deposit debits loans and credits deposits without initially transferring reserves; a transfer to another bank then debits deposits and credits reserves. A loan paid directly outside instead debits loan/credits reserves. These two funding paths cannot be treated as identical cash events. Deposit interest debits interest expense/credits deposit or accrued payable; withdrawal requires settlement funds.

\hypertarget{expected-credit-loss}{%
\section{Expected credit loss}\label{method-bank-methods-expected-credit-loss}}

For each admitted scenario j and date t, calculate contractual due flows minus the cash expected to be received, including supported collateral/enforcement cash and timing; discount the shortfall under the applicable original EIR or specified exception. With mutually exclusive exhaustive scenario weights w\_j, ECL is the sum of w\_j times those present-value shortfalls. Default-time hazards must be converted to disjoint default-time probabilities; summing cumulative PDs over dates counts the same default repeatedly. Collateral recoveries cannot be credited both in LGD and as a second recovery cash flow. A shorthand PD\ensuremath{\times}LGD\ensuremath{\times}EAD is admissible only if its definitions and discounting reproduce the specified cash-shortfall calculation; it is not a universal replacement.

Expected credit loss (ECL) measures the discounted expected cash shortfall. A significant increase in credit risk (SICR) changes the general method's default horizon. Purchased or originated credit-impaired (POCI) assets follow a separate method. For the general approach, twelve-month ECL considers lifetime shortfalls arising from possible defaults during the next twelve months; it is not just unpaid cash in those twelve months. SICR uses the change in lifetime default risk since initial recognition, reasonable forward-looking information and the applicable rebuttable presumptions. Do not install a two-times-PD or 30-day rule as an unconditional universal trigger. Lifetime ECL follows a supported SICR finding; cure needs a supported reversal of that finding. Subsequently credit-impaired assets use original EIR on amortised cost for interest in subsequent periods; POCI has a separate credit-adjusted-rate and cumulative-change method.

The general measurement interface requires scenario\_cashflows, law\_ref, information\_view, horizon\_admission, credit\_assessment and discount\_rule. An unweighted history set can produce conditional losses or loss bounds, but cannot produce an unbiased probability-weighted ECL by silently using equal weights. Return measurement\_unresolved for the ECL claim. Trade receivables and certain other assets use the separately applicable simplified approach; the general loan staging rule must not overwrite AASB 9.5.5.15--16.

\hypertarget{full-loan-and-allowance-roll-forward}{%
\section{Full loan and allowance roll-forward}\label{method-bank-methods-full-loan-and-allowance-roll-forward}}

Assume a fixed-rate non-POCI amortised-cost loan originated for 100, one terminal payment 121 two years later, original EIR 10\%, no fees, collateral, modifications, FX or taxes. At origination the assumed lifetime scenarios are: default in the first twelve months with probability 0.1, default during the following year with probability 0.1, and no default with probability 0.8. Either default gives terminal collection 60.5. The first twelve-month ECL includes lifetime loss from the first scenario only: 0.1\ensuremath{\times}(121\ensuremath{-}60.5)/1.1\ensuremath{^2}=5; initial lifetime ECL would be 10. Debit loan 100/ credit cash 100; debit impairment 5/credit allowance 5. Gross 100, allowance 5, net 95.

At year-one accrual the loan has survived the first window and is not yet credit-impaired: debit gross loan 10/credit interest 10. Survival alone would give remaining default probability 0.1/0.9=1/9. A subsequent, separately admitted credit forecast revises that conditional probability to 0.2; it is an authored forecast update, not a Bayes calculation from survival alone. Its lifetime weights are 0.8/0.2, with a separately established SICR finding; ECL=0.2\ensuremath{\times}60.5/1.1=11. Debit impairment 6/ credit allowance 6. Gross 110, allowance 11, net 99. The ratio change alone is not the defined SICR test. Immediately afterward, a distinct, ordered credit-impairment event establishes that only 60.5 will be collected at maturity. Required allowance is 110\ensuremath{-}60.5/1.1=55; debit impairment 44/credit allowance 44. Net 55.

In the next full year interest revenue is 55\ensuremath{\times}10\%=5.5. The gross contractual accretion is 11. One consistent decomposed posting debits gross loan 11, credits interest revenue 5.5 and allowance 5.5: gross 121, allowance 60.5, net 60.5. This reconciles gross and net-interest bases without counting the same expected loss again. Collect 60.5: debit cash/credit gross 60.5. When no reasonable expectation of remaining recovery is established, debit allowance 60.5/credit gross 60.5. Both balances reach zero. A mere delinquency is not that write-off finding. Subsequent unexpected cash recovery is recorded with its own recovery-income method and evidence; it does not restore an old live receivable by default.

\begin{longtable}[]{@{}lrrrrr@{}}
\toprule
\begin{minipage}[b]{0.11\columnwidth}\raggedright
Moment\strut
\end{minipage} & \begin{minipage}[b]{0.14\columnwidth}\raggedleft
Cash, opening 200\strut
\end{minipage} & \begin{minipage}[b]{0.14\columnwidth}\raggedleft
Gross loan\strut
\end{minipage} & \begin{minipage}[b]{0.14\columnwidth}\raggedleft
Allowance\strut
\end{minipage} & \begin{minipage}[b]{0.14\columnwidth}\raggedleft
Deposit liability\strut
\end{minipage} & \begin{minipage}[b]{0.14\columnwidth}\raggedleft
Equity, opening 20\strut
\end{minipage}\tabularnewline
\midrule
\endhead
\begin{minipage}[t]{0.11\columnwidth}\raggedright
Initial loan and allowance\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
100\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
100\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
5\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
180\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
15\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.11\columnwidth}\raggedright
Year-one accrual and SICR\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
100\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
110\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
11\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
180\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
19\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.11\columnwidth}\raggedright
Credit impairment\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
100\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
110\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
55\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
180\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
\ensuremath{-}25\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.11\columnwidth}\raggedright
Maturity accrual\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
100\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
121\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
60.5\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
180\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
\ensuremath{-}19.5\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.11\columnwidth}\raggedright
Collection and write-off\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
160.5\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
0\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
0\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
180\strut
\end{minipage} & \begin{minipage}[t]{0.14\columnwidth}\raggedleft
\ensuremath{-}19.5\strut
\end{minipage}\tabularnewline
\bottomrule
\end{longtable}

Total interest 15.5 less impairment 55 is loss 39.5, equal to 100 advanced minus 60.5 received. The negative equity state survives; no missing branch or capital plug restores solvency. These five dates jointly test allowance, recognition and bank balance-sheet arithmetic. The same loss cannot also be deducted directly from gross before the stated write-off.

For a non-derecognized loan modification, AASB 9.5.4.3 requires gross PV at original EIR and a modification result, then allowance and SICR reassessment under 5.5.12. For example gross 110 changed to a single future 110 at original 10\% gives revised gross 100 and modification loss 10 before any allowance change. This is separate from the financing method's issuer-liability ten-percent test. A derecognition decision requires its own asset conditions and cannot reuse that threshold.

\hypertarget{funding-capital-and-decision-policies}{%
\section{Funding, capital and decision policies}\label{method-bank-methods-funding-capital-and-decision-policies}}

Liquidity simulation settles the dated net payment queue by venue/currency, respecting encumbrance, available cash, committed line terms and admissible actions. Haircut/eligibility and transferability come from a versioned policy; market value alone is not available liquidity. With cash 20, due withdrawal 30 and an admitted usable facility 8, even a full draw leaves shortfall 2. Record the default/unresolved settlement according to the event's legal model. Raising exactly 2 of new equity without an investor event is an invented financing source. Interbank contagion requires explicit counterparties and settlement priorities; it cannot be inferred from aggregate deposits.

A RegulatoryAssessment reads an accounting view and an independent jurisdiction, date, perimeter, eligibility, deductions and exposure-weight policy. It outputs capital components, RWA/exposure measures, liquidity measures and reconciliations with their distinct denominators. Illustratively, equity 20 minus an assumed regulatory deduction 2 yields capital 18; assumed RWA 125 gives 14.4\%. Those inputs are synthetic, not a Basel rule, national capital approval or default threshold. No binding capital-policy numbers have been inspected for a target bank here. Use the Basel/national source and actual bank facts before real admission.

Behavior under capital/liquidity constraints is a separate economic model. Specify feasible actions, objectives, information set and ties before solving; failure to find an action returns policy\_failure or default under the stated contract. Halaj/Behn sources can motivate candidate behavior but cannot calibrate it for an individual bank. A forecast experiment must compare simple fixed-book, contractual runoff and explicitly estimated policy baselines with time-safe data, before claiming a predictive improvement. CECL and other bases retain separate authority/method branches in the dated-authority discussion.


## FILE docs/design/proposal/manuscript/sections/insurance-methods.tex

\hypertarget{group-state-and-general-measurement}{%
\section{Group state and general measurement}\label{method-insurance-methods-group-state-and-general-measurement}}

The following cases apply selected general-measurement and service-allocation provisions from the retained AASB 17 compilation \citep{aasb17}. They extend the premium-allocation example without presuming actuarial calibration or a complete insurer model.

The general method distinguishes fulfilment cash flows (FCF), including an
explicit risk adjustment (RA), from the contractual service margin (CSM),
which holds unearned profit. The liability for remaining coverage (LRC)
concerns future service; the liability for incurred claims (LIC) concerns
service and insured events already experienced. Keeping these components
separate makes a change in future estimates different from an unpaid claim.

Contract records retain insured risks, premiums/benefits, service and settlement dates, options/guarantees, cancellation/repricing rights and acquisition costs. Group admission evaluates portfolio/similar-risk management, onerous status and required issuance cohorts under AASB 17.14--24, recognition under 25--28 and boundary under 34. Cash outside the boundary belongs to future contracts, not this group's profit. GroupState retains expected dated cash flows, current discount curves, inception rates, explicit risk adjustment, CSM, loss component, LRC/LIC, coverage units, service experience and assumption vintages. Same premium totals are not sufficient state for merging different guarantees or claim tails.

General measurement follows 32--38: fulfilment cash flows are probability-weighted future net outflows, adjusted for timing/financial risk without double counting, plus explicit non-financial risk adjustment. CSM removes initial unearned gain under its conditions; an initial net loss is recognized under 47, not negative CSM. Paragraphs 40--44 separate remaining coverage and incurred claims. For a nonparticipating group, accrete CSM at the specified locked-in rate, apply future service changes at their required rate to CSM up to its available amount, record any excess loss and allocate current service over current plus future coverage units under B119. B96--B97 distinguish future service from incurred-claim changes, financial changes and current experience; not every revision is a CSM adjustment.

A MeasurementInput must resolve cash-flow/law, discount, risk-adjustment method, service grouping and coverage-unit evidence. Missing probabilities or RA support permit conditional sensitivity cases but block a source-supported measurement. Risk adjustment is the compensation the entity requires under 37; a standard deviation, confidence quantile or arbitrary percentage is only a candidate method until justified for that entity. Disclosures and the confidence-level equivalent, where applicable, are separate obligations. Market-consistent financial inputs and entity risk compensation must not be conflated.

\hypertarget{complete-two-year-general-measurement-case}{%
\section{Complete two-year general-measurement case}\label{method-insurance-methods-complete-two-year-general-measurement-case}}

Take a two-year nonparticipating group with one premium 120 received at inception, claims expected/actually incurred and paid 40 each year, zero discount rate, RA 10 initially released 5 with each equal service year, no acquisition costs, investment component, lapses, taxes, finance changes or reinsurance. Coverage units are 1 in each year because equal benefits and coverage are assumed. Before premium payment, expected net cash outflow is 80\ensuremath{-}120=\ensuremath{-}40, RA 10, FCF \ensuremath{-}30 and CSM 30, with net initial carrying amount zero. After the premium debit cash 120/ credit LRC 120. Its components are remaining expected claims 80, RA 10 and CSM 30.

Each year releases expected service claims 40, RA 5 and CSM 15: debit LRC 60/ credit insurance revenue 60. Incur claims 40: debit service expense 40/credit LIC 40; payment debits LIC 40/credits cash 40. End of year one: cash 80, LRC 60 (claims 40, RA 5, CSM 15), LIC 0 and equity/profit 20. End year two: cash 40, liabilities 0, cumulative equity/profit 40. Revenue 120 and claims 80 reconcile to premium 120 less claims cash 80. No investment component has been mistaken for revenue.

At year-one close, a separate pre-next-service change increases the remaining claim estimate from 40 to 60, RA unchanged. FCF rises 20; consume remaining CSM 15 and recognize service loss 5. LRC rises from 60 to 65, comprising FCF 65, CSM 0 and loss component 5 as a tracked portion, not an added liability on top. Debit service loss 5/credit LRC 5 with component transfer CSM\ensuremath{\rightarrow}FCF 15. A decrease of 8 in the revised future claim estimate, before any additional service/finance movement, first reverses loss 5 and restores CSM 3. FCF 57 plus CSM 3 gives LRC 60. Credit loss reversal 5/debit LRC 5. This tests 48--52 ordering. Later systematic allocation of loss component to releases/finance must reduce it to zero by coverage end; it cannot be amortized as revenue a second time.

In a separate case, an already-incurred unpaid claim estimate rises 40 to 48. Debit service expense 8/credit LIC 8; do not consume future-service CSM. A discount-rate change is financial under B97; its profit/OCI route follows the selected permitted finance policy. The zero-rate base case does not remove the need for separate current and locked-in rate calculations in a real group.

For the unreversed onerous alternative, carry the loss component through the remaining service year. Opening LRC 65 comprises future claims 60 and RA 5, with CSM 0 and loss component 5 within that LRC. A declared proportional allocation assigns 5/65 of each expected claim/RA release to the loss component, consistent with paragraphs 49--52 and B124's revenue exclusions. The expected claim release allocates 60/13 to loss reversal and the RA release 5/13; the total is 5, leaving loss component 0. Debit LRC 65, credit revenue 60 and credit loss reversal 5. Separately incur and pay claims 60 through LIC. Period profit is 60\ensuremath{-}60+5=5; combined with first-year profit 20 and the earlier onerous loss 5, lifetime profit is 20. Closing cash 20 equals equity 20 and all liabilities are zero. Treating all 65 as revenue while also reversing loss 5 overstates profit by 5.

\hypertarget{nonzero-discount-and-service-allocation}{%
\section{Nonzero discount and service allocation}\label{method-insurance-methods-nonzero-discount-and-service-allocation}}

A second complete case keeps premium 120, two equal coverage units and RA 10, but expected and realized claims are 44 after one year and 48.4 after two years. Both the inception and current discount curves remain a flat 10\% throughout; there are no new estimates, options, fees, taxes, investments or OCI election. This RA schedule is an authored measurement input, not an actuarial calibration: it declines by 5 per year, with its entire change in the service result under 81. All other insurance finance effects go to profit or loss. The retained source supports the mechanics in 44, 80--88,B119 and B123--B124.

At inception the present value of the two expected claims is
\[
 \frac{44}{1.1}+\frac{48.4}{1.1^2}=40+40=80.
\]
 FCF before premium is 80+10\ensuremath{-}120=\ensuremath{-}30, CSM 30, and after premium LRC 120. In year one the claim PV accretes 8; CSM accretes 3 at the locked-in rate. Allocate the resulting CSM 33 across the two current/future units, releasing 16.5. Revenue is expected claims 44 plus RA 5 plus CSM 16.5=65.5. Service expense 44 and finance expense 11 leave profit 10.5. After paying 44, cash 76 and LRC 65.5 (claim PV 44, RA 5, CSM 16.5) reconcile to equity 10.5.

In year two claim PV accretes 4.4 and CSM accretes 1.65. Release all remaining CSM 18.15, RA 5 and expected claims 48.4, giving revenue 71.55. Service expense 48.4 and finance expense 6.05 leave profit 17.1. Final cash/equity 27.6 equals premium 120 minus claims 92.4; all group liabilities are zero. Total revenue 137.05 less finance expense 17.05 equals premium 120. Setting revenue equal to cash premium each year or releasing 15 of CSM each year would ignore the specified financing. These are separate component calculations followed by debit finance expense/ credit LRC for accretion, debit LRC/credit revenue for service and the stated LIC recognition/settlement entries. Cash is deliberately assumed uninvested.

\hypertarget{paa-reinsurance-and-valuation-methods}{%
\section{PAA, reinsurance and valuation methods}\label{method-insurance-methods-paa-reinsurance-and-valuation-methods}}

The preceding premium-allocation case states separate eligibility and recognition timing for gross insurance and reinsurance. PAA under 53--59 requires the one-year coverage or nonmaterial-difference condition; a short payment lag is not the eligibility test. LRC starts with received premium and applicable acquisition adjustments, then releases insurance revenue under the prescribed service pattern. LIC still measures incurred obligations using the applicable fulfilment-cash-flow rules; the allowed short-settlement discount simplification needs its own conditions. Emerging onerous facts require a loss assessment; a premium balance cannot be presumed sufficient.

Reinsurance has its own group, boundary, recognition time, counterparty risk, cash-flow, CSM/cost and possibly loss-recovery component under 60--70A. Do not multiply every gross insurance liability by a quota share: excluded claims, limits, deductibles, timing, reinstatements and counterparty non-performance matter. Claim 100 with an eligible 50\% recovery but expected 90\% collectability gives conditional expected recovery 45, not 50; altering transferred insurance risk and reinsurer non-performance are different inputs. This simple calculation does not establish treaty recognition or RA by itself. Gross liability 100 remains; reinsurance recovery is a separate asset/measurement with its own authority.

For direct participation, test B101's conditions using the actual underlying items, substantial-share and variation judgments. Retain underlying fair values, entity fee share and guarantee/risk-mitigation choices; .45 and B101--B118 specify the variable-fee adjustments to CSM, with onerous and mitigation exceptions. A local component illustration of a qualifying share: underlying-value increase 20 and entity's fixed 10\% share gives candidate variable-fee change 2; eligibility, guarantees and other FCF changes must be evaluated before posting. The full option/guarantee valuation and transition calculations are further supported profiles, with source and numerical obligations, not an assumed linear fee model.

The claims-development example above supplies an estimation input, not a
recognition rule. Its point projection is 148, but the single observed final
factor leaves its variance unresolved. In the general method the factors are
\[
 \widehat f_k=\frac{\sum_{i\in O_k} C_{i,k+1}}{\sum_{i\in O_k}C_{i,k}},
\]
where $O_k$ contains origin years with both required observed cells. Each
incomplete row is projected through the remaining factors. The same triangle
therefore has ultimate claims 180, 216 and 252, with unpaid amounts 0, 36 and
112. Tail development, calendar inflation, zero or negative cells and dependence
need explicit extensions. The conditional means, variance scaling and
independent-origin-year assumptions behind the inspected Mack error formulas
\citep[equations (1)--(3), Theorems 1--3]{mack1993} cannot turn this tiny
triangle into a predictive law or a justified insurance risk adjustment.

\hypertarget{interfaces-exclusions-and-acceptance-cases}{%
\section{Interfaces, exclusions and acceptance cases}\label{method-insurance-methods-interfaces-exclusions-and-acceptance-cases}}

Insurance events are group\_recognize, premium\_settle, service\_release, claim\_incur, claim\_settle, assumption\_change, onerous\_change and treaty\_change, each bound through the event-basis, authorization and commit contracts to the exact group/version, evidence and information view. Journals and component roll-forwards must reconcile independently; a component reallocation is not always a net liability change. Invalid grouping, missing rate/law, unsupported option valuation, ambiguous contract boundary or unknown service units produces the corresponding unresolved/outside-scope result. Failed numerical paths retain their coverage/mass, without successful-only normalization. Modified contracts need the applicable derecognition analysis; no new ID can erase unfavorable old-group obligations.

Initial transition requires an actual method choice and eligibility for full retrospective, modified-retrospective or fair-value transition under Appendix C, with acquisition, grouping, past service and historical-rate records. This collection does not claim an executed transition or a general VFA valuation. The nonzero-rate general case and onerous allocation through expiry above are finite specification examples. Required later acceptance still includes a priced guarantee, acquisition/reinsurance interaction, transition and actuarial backtesting. These retained obligations prevent the two-year illustration from being described as full insurance-domain readiness.


## FILE docs/design/proposal/methods/method-boundary-v1.md

# The common boundary of a financial method

A financial method turns an admitted economic event and opening state into a
proposed accounting consequence. It does not acquire facts, decide a company's
reporting framework, calibrate a probability law or commit its own output. Those
responsibilities have separate owners in P16. This specification and the domain
methods below propose the implementation behavior required by MC02, MC04–MC25,
MC27–MC29 and MC34–MC35. No domain engine is implemented by these documents.

## M1. Method definitions and inputs

Each versioned MethodDefinition has the eight groups in standards-mapping-v1.md,
plus the following closed header. Its identity is a portable P16 Ref; its
contents include nonempty method_id/version, event_kind, state_schema,
event_schema, journal_schema, delta_schema, output_schema, required_contexts,
authority_requirements, preconditions, algorithm, account_roles,
report_mappings, numerical_capability, examples and unsupported_cases.
All schema names resolve through the posting profile's immutable schema lock.
Each precondition has an id, typed predicate, required input/admission references
and a defined consequence of false or unknown. Domain tables specify economic
fields; money is an exact rational with a Context Ref, dates use the P16 time
contract, counts are integers and rate conventions are named. Unknown is an
explicit tagged value, never an omitted field, zero, false or default rate.

The input is P16 AccountingEventBasis/v1. Its event_ref resolves to the named
domain event, opening_ref to the domain state and chart_ref to the account-role
mapping. Method-specific facts may be reached from evidence_refs or the admitted
assumptions_ref, but their provenance survives. The branch's immutable book_mode
and the posting profile determine whether synthetic or real-workspace evidence
can authorize posting. Neither a checked teaching example nor the native
assess_only response is a PostingAuthorization. A source-supported method still
needs the actual contract, entity, date and judgment inputs for a real branch.

Applicability is evaluated in order: framework/jurisdiction and operative dates;
entity/transaction scope; contract and recognition facts; elections; numerical
capability; account/context bindings. Evaluate every material precondition and
retain each finding. A false required fact gives ineligible, an unknown required
fact gives unresolved, and an event outside the declared method gives outside_scope.
Do not overwrite a known false finding merely because another fact is unknown.
Missing authority or unverified amendments cannot yield source-supported
permission. A standard's explicit presumption, such as the identified-asset
substitution rule, is itself a conditional rule requiring its stated conditions;
it is not interchangeable with a blanket missing-data rejection.

## M2. Proposed operation and journal semantics

The future method evaluator is a pure operation of the resolved EventBasis and
its posting profile. It produces findings, either a proposed journal/delta or
explicit absence, required disclosures, and numerical status. It reads only the
admitted evidence/time/information view. It cannot observe a future simulated
realization while measuring a current expectation or deciding today's behavior.
Source-period accounting is recomputed from that source's admitted view;
an updated view creates a new derivation with explicit invalidation lineage.

For eligible inputs, apply the domain recurrence to an immutable opening state,
then derive journal lines and the independent economic delta. A journal line has
account role, debit or credit, positive rational quantity, currency/context,
entity, book, event and method bindings. Zero lines are omitted. Negative effects
reverse sides; they are not negative debit quantities. Each currency/book journal
balances. Cross-currency exchanges name both legs, functional amounts and rate
evidence; their raw currency quantities are never summed as one unit.

Validate domain conservation separately: cash movement equals settlements;
inventory quantity/cost equals admitted lot movements; debt face amount is not
silently replaced by carrying value; share count is not a money balance; group
eliminations have matched counterpart and perimeter evidence. A balanced entry
with the wrong depreciation life or effective-interest base fails the method.

P16 A1 controls authorization and commit. accounting.authorize@1 recomputes the
method/profile findings and produces PostingAuthorization/v1. A proposed
JournalProposal and EconomicDelta bind the same basis and authorization. The
outer accounting.commit@1 request carries the sole expected head/generation;
AccountingCommitArguments carries only the four specified Refs. Exact replay
precedes freshness. A new valid request atomically commits journal, economic
state and receipt; failure commits none. Domain business-event identities remain
stable across retries and include actual contract/lot/cohort source identity.
The method definitions here do not add operations to a running registry.

The method identifiers below are package members, not new platform operations.
Their versioned records belong in an ExtensionPackage's `method_refs` and
`state_requirements`; required schemas, authority and capabilities are pinned
in the same package lock. An operation still uses its exact P16 I2 signature.

| Proposed method family | P16 operation and ownership |
| --- | --- |
| Corporate, financing, bank and insurance events | `scenario.project@1` constructs conditional future events; `accounting.assess@1` evaluates the native assess-only request. Separately, `accounting.authorize@1` evaluates EventBasis under a supported posting profile; `accounting.propose@1` returns journal and delta; `accounting.commit@1` requests the atomic mutation. `report.build@1` derives statements. No assessment result substitutes for authorization. |
| Group, FX and cross-basis adjustments | The same accounting sequence applies in a declared adjustment book with source entity-book and perimeter dependencies; `report.build@1` aggregates that compatible view. A method must not silently mutate legal-entity books. |
| Dated rule selection | Applicability predicates are part of the method/posting profile assessed by the accounting operations. A proposed authority/election reading uses `review.propose@1` and the separately authorized `review.commit@1`; selecting a framework is not itself posting permission. |
| Reconstruction and numerical queries | `history.construct@1`, `history.refine@1` and `history.query@1` retain their declared scopes, capabilities and coverage. A root/discount routine is a method dependency, not a replacement history endpoint. |
| Probability and forecast | Native supported operations use `uncertainty.evaluate@1` and separate `uncertainty.admit@1`/`uncertainty.select@1`. `scenario.project@1` supplies exogenous stress. Continuous and causal methods here are proposed extension capabilities: they remain unsupported by the initial P16 finite/exogenous profile until their schemas, signatures and conformance are separately admitted. |
| Source and software preparation | `source.prepare@1` returns candidates and traversal obligations; review operations handle admission, and `model.compile@1` constructs candidate IR. An extraction result never includes a fabricated acceptance receipt. |
| Literature support | Support records are evidence for `review.propose@1`; review decisions and `record.explain@1` preserve claim-specific admission and lineage. Literature checking creates no accounting or solver authority. |

For a corporate `deliver` event, for example, `event_ref` identifies its exact
contract/obligation/quantity/allocation/control record, `opening_ref` resolves
the R/B/C and inventory/receivable state, and `method_ref` names that scoped
delivery recurrence. The EventBasis also binds all P16 context, authority,
assumption, view, branch and chart fields; domain shorthand cannot omit them.
The authorization names that exact basis and profile. Proposed journal and
independent delta then carry the same basis/authorization Refs. Report methods
consume the resulting frozen branch, not an unrelated cumulative revenue value.

## M3. Financial boundaries and result status

Recognition time, event time, payment time and report availability remain distinct.
An obligation can exist when cash is insufficient; that shortage can trigger a
separate modeled default or funding action. It does not erase the obligation,
invent a loan or commit an impossible payment. Conditional forecasts retain
default states and their accrued liabilities. Unsupported law, failed numerical
evaluation and unexplored alternatives retain their own P16 coverage regions.

Run all statements and notes from one common path. The ledger view carries
signed account balances plus economic schedules; statement maps partition each
account's relevant movement and explicitly split mixed roles. Profit, OCI,
owner contributions/distributions and opening equity reconcile. Cash flows
exclude noncash recognition and separately reconcile FX effects on cash.
Parent, subsidiary, consolidation adjustment and tax books remain distinct;
their consolidation is a query over dated compatible books, not deletion of
the source entries. Intercompany cash is not group external cash.

Examples in this collection use unrounded rationals internally. Displaying
2.50 does not change its identity. A real posting quantum needs a declared
rounding/tie policy and a separate residual allocation rule. Numerical methods
that only enclose a value may post only if the whole certified enclosure maps
to the same authorized rounded amount; otherwise return rounding_unresolved.
An approximate estimate without that certificate remains approximate with its
own tolerance, provenance and downstream sensitivity. No library float or
sample maximum acquires exact status from its JSON serialization.

## M4. Aggregation and retention

Retain contract/lot/cohort detail unless the query's sufficient-state rule is
proved for the selected methods, horizon, scenarios and reporting maps. An exact
grouping map G must satisfy G(T(s,e))=Tg(G(s),e) and Q(s)=Qg(G(s)) for every
admitted state/event in that scope. This is a local proof obligation, not an
algorithm claiming to decide equivalence for arbitrary software.

Two fixed-rate bullet debts with identical currency, payment dates, seniority,
effective rate, accounting category and scenario response can sum principal and
carrying amount when all transitions/reporting are additive and no per-contract
threshold, fee or option is queried. Two loans of 50 at 2% and 8% instead produce
aggregate annual interest 5 only in that unchanged year. Replacing them by one
5% loan loses the response when the second resets, defaults or matures first.
Even identical current journals cannot prove that replacement safe. Grouping
bank loans across credit grades or insurance contracts across required groups
likewise requires preserved risk/cohort dimensions; arithmetic equality at one
date is insufficient.

A change of scenario, query, method, perimeter, authority, observation or horizon
invalidates the corresponding sufficiency certificate and its descendants.
Recompute from retained detail or return resolution_insufficient. Approximate
grouping needs a specified error bound for the actual queried quantity and its
supporting evidence; none is established merely by the examples here.


## FILE docs/design/proposal/methods/method-cases-v1.json

{
  "schema": "accdsl.proposal.p17.finite-document-cases.v1",
  "purpose": "Exact synthetic document calculations, not runtime engine conformance or accounting authority. Expected values were transcribed from the named specification examples; source interpretation requires separate review.",
  "cases": {
    "revenue": {
      "document": "corporate-methods-v1.md#C1",
      "inputs": {
        "revenue": "60",
        "billings": [
          "50",
          "80"
        ],
        "collection": "30"
      },
      "expected": {
        "bill50": [
          "20",
          "10",
          "0",
          "30",
          "60"
        ],
        "bill80": [
          "50",
          "0",
          "20",
          "30",
          "60"
        ],
        "prebill80": [
          "80",
          "0",
          "80",
          "0",
          "0"
        ]
      }
    },
    "inventory": {
      "document": "corporate-methods-v1.md#C1",
      "inputs": {
        "lots": [
          [
            "10",
            "2"
          ],
          [
            "10",
            "3"
          ]
        ],
        "sold": "12",
        "sales": "48",
        "nrv": [
          "16",
          "22",
          "30"
        ]
      },
      "expected": {
        "fifo_cost": "26",
        "fifo_stock": "24",
        "average_cost": "30",
        "average_stock": "20",
        "margins": [
          "22",
          "18"
        ],
        "write_down": "8",
        "reversal": "6",
        "cap": "24"
      }
    },
    "ppe": {
      "document": "corporate-methods-v1.md#C1",
      "inputs": {
        "cost": "100",
        "residual": "10",
        "life": "3",
        "new_remaining_life": "3"
      },
      "expected": {
        "first_charge": "30",
        "next_charge": "20"
      }
    },
    "lease_tax": {
      "document": "corporate-methods-v1.md#C2",
      "inputs": {
        "opening_cash": "500",
        "revenue": "400",
        "cash_cost": "100",
        "payments": [
          "121",
          "121"
        ],
        "rate": "1/10",
        "tax_rate": "1/4",
        "modified_payments": [
          "144",
          "144"
        ],
        "modified_rate": "1/5"
      },
      "expected": {
        "initial": [
          "210",
          "52.5",
          "52.5"
        ],
        "interest": [
          "21",
          "11"
        ],
        "profit": [
          "130.5",
          "138"
        ],
        "pretax": [
          "174",
          "184"
        ],
        "tax": [
          "43.5",
          "46"
        ],
        "deferred_expense": [
          "-1.25",
          "1.25"
        ],
        "ocf": [
          "300",
          "255.25"
        ],
        "closing": [
          [
            "679",
            "105",
            "27.5",
            "110",
            "26.25",
            "44.75",
            "630.5"
          ],
          [
            "813.25",
            "0",
            "0",
            "0",
            "0",
            "44.75",
            "768.5"
          ]
        ],
        "modification": [
          "220",
          "110",
          "215"
        ]
      }
    },
    "debt": {
      "document": "financing-methods-v1.md#F1-F2",
      "inputs": {
        "proceeds": "100",
        "terminal": "121",
        "years": 2,
        "rate": "1/10",
        "fee": "2",
        "substantial_terminal": "133.1",
        "new_fair_value": "118",
        "reduced_terminal": "115.5",
        "repurchase": "108",
        "cash_available": "80"
      },
      "expected": {
        "carrying": [
          "100",
          "110",
          "121"
        ],
        "interest": [
          "10",
          "11"
        ],
        "replacement_pv": "121",
        "difference_ratio": "1/10",
        "extinguishment_loss": "8",
        "modified_pv": "105",
        "modification_gain": "5",
        "modified_interest": "10.5",
        "repurchase_gain": "2",
        "unpaid": "41"
      }
    },
    "shares": {
      "document": "financing-methods-v1.md#F3",
      "inputs": {
        "issued": "100",
        "issue_price": "2",
        "repurchased": "10",
        "repurchase_price": "3",
        "reissued": "5",
        "reissue_price": "4",
        "compound_proceeds": "100",
        "compound_debt": "90",
        "converted_shares": "10"
      },
      "expected": {
        "cash_flows": [
          "200",
          "-30",
          "20"
        ],
        "outstanding": "95",
        "treasury": "5",
        "reissue_equity": "5",
        "compound_equity": "10",
        "compound_interest": "10",
        "conversion_cash": "0"
      }
    },
    "group": {
      "document": "groups-fx-methods-v1.md#G2",
      "inputs": {
        "ownership": "4/5",
        "purchase": "96",
        "assets": "160",
        "liabilities": "60",
        "profit": "20",
        "extra_fraction": "1/10",
        "extra_price": "15",
        "sale_all": "130",
        "sale_partial": "100",
        "retained_fv": "35"
      },
      "expected": {
        "net_acquired": "100",
        "nci_initial": "20",
        "goodwill": "16",
        "profit_parent": "16",
        "nci_later": "24",
        "nci_transfer": "12",
        "parent_equity_reduction": "3",
        "nci_after_purchase": "12",
        "sale_gain": "18",
        "partial_sale_gain": "23"
      }
    },
    "intragroup": {
      "document": "groups-fx-methods-v1.md#G3",
      "inputs": {
        "external_cost": "60",
        "internal_price": "100",
        "outside_sale": "120",
        "tax_base": "100",
        "tax_rate": "1/4"
      },
      "expected": {
        "eliminated_profit": "40",
        "group_inventory": "60",
        "outside_profit": "60",
        "dta": "10"
      }
    },
    "fx": {
      "document": "groups-fx-methods-v1.md#G4",
      "inputs": {
        "purchase_foreign": "100",
        "initial_rate": "1.2",
        "closing_rate": "1.3",
        "settlement_rate": "1.25",
        "net_opening": "100",
        "profit": "20",
        "profit_rate": "1.25",
        "ownership": "4/5"
      },
      "expected": {
        "inventory": "120",
        "payable_close": "130",
        "fx_loss": "10",
        "cash_settlement": "125",
        "settlement_gain": "5",
        "assets_translated": "156",
        "profit_translated": "25",
        "oci": "11",
        "parent_oci": "8.8",
        "nci_oci": "2.2"
      }
    },
    "bank": {
      "document": "bank-methods-v1.md#B3",
      "inputs": {
        "loan": "100",
        "terminal": "121",
        "recovery": "60.5",
        "rate": "1/10",
        "initial_default_masses": [
          "1/10",
          "1/10"
        ],
        "later_pd": "1/5",
        "opening_cash": "200",
        "deposits": "180",
        "opening_equity": "20"
      },
      "expected": {
        "initial_ecl": "5",
        "initial_lifetime_ecl": "10",
        "survival_only_pd": "1/9",
        "year1_ecl": "11",
        "credit_impaired_allowance": "55",
        "net_interest": "5.5",
        "allowance_accretion": "5.5",
        "cash_end": "160.5",
        "total_interest": "15.5",
        "total_impairment": "55",
        "profit": "-39.5",
        "rows": [
          [
            "100",
            "100",
            "5",
            "180",
            "15"
          ],
          [
            "100",
            "110",
            "11",
            "180",
            "19"
          ],
          [
            "100",
            "110",
            "55",
            "180",
            "-25"
          ],
          [
            "100",
            "121",
            "60.5",
            "180",
            "-19.5"
          ],
          [
            "160.5",
            "0",
            "0",
            "180",
            "-19.5"
          ]
        ]
      }
    },
    "funding": {
      "document": "bank-methods-v1.md#B4",
      "inputs": {
        "cash": "20",
        "withdrawal": "30",
        "facility": "8",
        "equity": "20",
        "deduction": "2",
        "rwa": "125"
      },
      "expected": {
        "shortfall": "2",
        "capital": "18",
        "ratio": "18/125"
      }
    },
    "insurance": {
      "document": "insurance-methods-v1.md#I2",
      "inputs": {
        "premium": "120",
        "claims": [
          "40",
          "40"
        ],
        "ra": "10",
        "ra_releases": [
          "5",
          "5"
        ],
        "service_units": [
          "1",
          "1"
        ],
        "future_increase": "20",
        "future_decrease": "8",
        "incurred_increase": "8"
      },
      "expected": {
        "initial_fcf": "-30",
        "initial_csm": "30",
        "revenue": [
          "60",
          "60"
        ],
        "profit": [
          "20",
          "20"
        ],
        "rows": [
          [
            "80",
            "60",
            "20"
          ],
          [
            "40",
            "0",
            "40"
          ]
        ],
        "loss_component": "5",
        "onerous_lrc": "65",
        "reversal": "5",
        "restored_csm": "3",
        "revised_fcf": "57",
        "revised_lrc": "60",
        "lic_change": "8"
      }
    },
    "claims": {
      "document": "insurance-methods-v1.md#I3",
      "inputs": {
        "triangle": [
          [
            "100",
            "150",
            "180"
          ],
          [
            "120",
            "180"
          ],
          [
            "140"
          ]
        ],
        "gross_claim": "100",
        "quota_share": "1/2",
        "collectability": "9/10"
      },
      "expected": {
        "factors": [
          "1.5",
          "1.2"
        ],
        "ultimate": [
          "180",
          "216",
          "252"
        ],
        "outstanding": "148",
        "last_factor_observations": "1",
        "reinsurance": "45"
      }
    },
    "pension": {
      "document": "corporate-extensions-v1.md#X1",
      "inputs": {
        "dbo": "100",
        "assets": "80",
        "service": "12",
        "rate": "1/20",
        "contribution": "10",
        "benefits": "8",
        "actuarial_loss": "7",
        "actual_return": "6",
        "unit_benefit": "100",
        "unit_discount": "1/10"
      },
      "expected": {
        "dbo_end": "116",
        "assets_end": "88",
        "net_liability": "28",
        "expense": "13",
        "oci_loss": "5",
        "year1_unit_pv": "1000/11",
        "year2_unit_interest": "100/11",
        "unit_settlement": "200"
      }
    },
    "impairment": {
      "document": "corporate-extensions-v1.md#X2",
      "inputs": {
        "assets": "100",
        "goodwill": "20",
        "recoverable": "90",
        "floor": "95",
        "standalone": "80",
        "lower_recoverable": "60",
        "later_recoverable": "90"
      },
      "expected": {
        "total_loss": "30",
        "goodwill_loss": "20",
        "other_loss": "10",
        "floor_remaining": "5",
        "standalone_loss": "20",
        "reversal_cap": "20"
      }
    },
    "awards": {
      "document": "corporate-extensions-v1.md#X3",
      "inputs": {
        "granted": "100",
        "grant_fv": "3",
        "years": "2",
        "vested": "80",
        "cash_fv1": "4",
        "cash_fv2": "5"
      },
      "expected": {
        "equity_expenses": [
          "150",
          "90"
        ],
        "cash_expenses": [
          "200",
          "200"
        ],
        "cash_settlement": "400"
      }
    },
    "valuation": {
      "document": "corporate-extensions-v1.md#X4",
      "inputs": {
        "units": "10",
        "quoted_price": "7",
        "payment": "111",
        "rate": "11/100",
        "borrowing": "100",
        "borrow_rate": "1/20",
        "temporary_income": "1"
      },
      "expected": {
        "quoted_value": "70",
        "pv": "100",
        "net_borrow_cost": "4"
      }
    },
    "lease_basis": {
      "document": "standards-methods-v1.md#S2-S4",
      "inputs": {
        "opening": "210",
        "payments": [
          "121",
          "121"
        ],
        "rate": "1/10",
        "us_single_expense": "121"
      },
      "expected": {
        "us_rou": [
          "110",
          "0"
        ],
        "us_rou_reduction": [
          "100",
          "110"
        ],
        "finance_rou": [
          "105",
          "0"
        ],
        "finance_expense": [
          "126",
          "116"
        ]
      }
    },
    "finite_law": {
      "document": "forecasting-methods-v1.md#Q3",
      "inputs": {
        "prior": [
          "1/3",
          "2/3"
        ],
        "likelihood": [
          "3/4",
          "1"
        ]
      },
      "expected": {
        "evidence": "11/12",
        "posterior": [
          "3/11",
          "8/11"
        ],
        "unresolved_mass": "8/11"
      }
    },
    "gaussian": {
      "document": "forecasting-methods-v1.md#Q3",
      "inputs": {
        "mean": "0",
        "variance": "4",
        "h": "1",
        "noise_variance": "1",
        "observation": "2",
        "cash_constant": "100",
        "cash_slope": "10"
      },
      "expected": {
        "mean": "8/5",
        "variance": "4/5",
        "cash_mean": "116",
        "cash_variance": "80",
        "independent_second_mean": "16/9",
        "independent_second_variance": "4/9"
      }
    },
    "causal": {
      "document": "forecasting-methods-v1.md#Q4",
      "inputs": {
        "prob_u1": "1/2",
        "x_coefficient": "2",
        "u_coefficient": "1",
        "intervene_x": "1"
      },
      "expected": {
        "observed_mean": "3",
        "intervention_mean": "2.5"
      }
    },
    "joint_forecast": {
      "document": "corporate-methods-v1.md#C3",
      "inputs": {
        "x": [
          "0",
          "1/2",
          "1"
        ],
        "ar": "55",
        "inventory": "40",
        "ppe": "98",
        "ap": "40",
        "debt": "100",
        "opening_equity": "90.6",
        "opening_cash": "74.6",
        "capex": "20",
        "dividend": "8"
      },
      "expected": {
        "interest": [
          "5",
          "6",
          "7"
        ],
        "profit": [
          "65.6",
          "64.8",
          "64"
        ],
        "cash": [
          "95.2",
          "94.4",
          "93.6"
        ],
        "equity": [
          "148.2",
          "147.4",
          "146.6"
        ],
        "assets": [
          "288.2",
          "287.4",
          "286.6"
        ]
      }
    },
    "rounding": {
      "document": "source-preparation-methods-v1.md#D3",
      "inputs": {
        "displayed": "100",
        "scale": "1000000",
        "literal_digits": "1234",
        "scale_exponent": -3
      },
      "expected": {
        "nearest_enclosure": [
          "99500000",
          "100500000"
        ],
        "truncation_enclosure": [
          "100000000",
          "101000000"
        ],
        "inline_value": "1.234",
        "double_scaled_value": "0.001234"
      }
    },
    "roots": {
      "document": "forecasting-methods-v1.md#Q2",
      "inputs": {
        "rate_exact": "21/100",
        "half_factor": "11/10",
        "rate_irrational": "1/10",
        "proceeds_after_fee": "98",
        "payment": "121",
        "root_bracket": [
          "1/10",
          "1/5"
        ],
        "bisect_steps": 80
      },
      "expected": {
        "exact_half_interest": "10",
        "incorrect_simple_interest": "10.5",
        "certified_sqrt_lower": "1.0488",
        "certified_sqrt_upper": "1.0489"
      }
    },
    "insurance_nonzero": {
      "document": "insurance-methods-v1.md#I2a",
      "inputs": {
        "premium": "120",
        "claims": [
          "44",
          "48.4"
        ],
        "rate": "1/10",
        "ra": "10",
        "ra_releases": [
          "5",
          "5"
        ],
        "units": [
          "1",
          "1"
        ]
      },
      "expected": {
        "claim_pv": "80",
        "initial_csm": "30",
        "revenue": [
          "65.5",
          "71.55"
        ],
        "finance": [
          "11",
          "6.05"
        ],
        "profit": [
          "10.5",
          "17.1"
        ],
        "csm_release": [
          "16.5",
          "18.15"
        ],
        "rows": [
          [
            "76",
            "65.5",
            "10.5"
          ],
          [
            "27.6",
            "0",
            "27.6"
          ]
        ],
        "total_revenue": "137.05",
        "total_finance": "17.05"
      }
    },
    "insurance_onerous": {
      "document": "insurance-methods-v1.md#I2",
      "inputs": {
        "opening_cash": "80",
        "future_claims": "60",
        "ra": "5",
        "loss_component": "5",
        "original_year1_profit": "20"
      },
      "expected": {
        "allocation": [
          "60/13",
          "5/13"
        ],
        "revenue": "60",
        "reversal": "5",
        "year2_profit": "5",
        "cash_end": "20",
        "equity_end": "20",
        "loss_component_end": "0"
      }
    }
  }
}
