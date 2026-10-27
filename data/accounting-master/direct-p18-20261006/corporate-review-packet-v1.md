# Bounded P18 corporate integration review

You are an independent read-only reviewer. No tools, files, commands, edits or further reviewers. Review only this self-contained packet, not the whole proposal.

Check the copied corporate, lease/tax, financing, group and FX numerical methods against the accepted fixture. Look for transcription errors, contrary old/new assumptions, standards overclaims and explanations that prevent reconstruction. Arithmetic is document evidence, not product or authority certification.

Accepted P16 architecture and P17 scoped methods are comparison baselines, not proof of full readiness. The candidate builds (122 pages, zero serious LaTeX warnings); render inspection is separate. Current ASC, whole real-company semantics, insurance transition/full VFA, actual regulatory/actuarial data, and human acceptance remain open. Do not label those honestly retained gaps a new P18 transcription failure. Source provenance is frozen; no new literature search is claimed.

Budget the review to finish in one response. Give at most 6 concrete findings, each with exact file/section and necessary repair, plus a brief reason for the verdict. Focus first on material mismatches; do not perform or narrate an exhaustive re-derivation of every case. Limit your final answer to 1000 words. End with exactly VERDICT: AGREE or VERDICT: REVISE. AGREE accepts only this packet's integration scope, with any minor nonblocking findings explicitly labelled.


## FILE docs/design/proposal/manuscript/chapters/08-modules.tex

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
report cannot be assigned that presentation regime solely because the latest
installed package includes it.

IFRS, US GAAP and ASBE packages share economic contracts and events where
appropriate, but produce separate accounting books. A reconciliation between
books consists of explained adjustments with origins in differing treatments,
not a renaming of accounts. The first implementation can preserve all three
source bases even while only a selected subset has executable rules. Such a
source is represented as observed information with unsupported simulation
treatments, rather than being silently converted to the supported basis.

The official IFRS overviews for IFRS 9, IAS 32 and IFRS 17 establish the relevant
scope of financial-instrument measurement, presentation and insurance
contracts \citep{ifrs9,ias32,ifrs17}. They are orientation sources, not substitutes
for reviewed paragraph-level implementations. The retained official Ministry of Finance ASBE~21 page now supports selected
lease provisions. Its entity-specific issuance and amendment chain and other
ASBE authority remain incomplete. Current ASC access is also unresolved.
Historical amendments and issuer policies inform proposed comparisons without
substituting for operative authority. These source limits are addressed
explicitly in the following dated-method discussion.

\section{Non-financial companies}

The initial industry package covers sales, collections, purchases, payments,
inventory movements, payroll, capital expenditure, depreciation and basic
financing. Revenue recognition is a separate rule from invoicing and cash
collection. A service contract may generate a performance event before an
invoice, creating a different asset from an unconditional receivable. Customer
advances create obligations before revenue. Returns, rebates and variable
consideration need separate assumptions and subsequent adjustments.

Inventory state includes quantity, cost, location, ownership and lot or cohort.
A costing method is selected within the reporting package's permissible
domain. An aggregate stock can support a simple model only if its approximation
is declared. A commodity-price shock can expose differences between old and
new inventory that an average value suppresses. Fixed-asset state likewise
requires acquisition dates, components, useful lives, residual values,
depreciation method, tax basis and impairment history when those affect the
requested forecast.

Industry extensions add economic mechanisms without bypassing the accounting
core. Construction requires performance and completion states; extractive
industries require reserves, depletion and restoration obligations; utilities
may require rate-regulation treatment; software businesses may require
contract liabilities and development-cost decisions. The module manifest
states what is represented, what is executable, and what remains aggregated.

\section{A matched inventory case across reporting profiles}

Standards packages need operation-level decisions. For interchangeable goods,
the inspected AASB~102 text incorporating IAS~2 permits FIFO or weighted
average in paragraph 25 and explains both in paragraph 27
\citep{aasb102}. The reproduced ASBE~1 text specifies FIFO, weighted average
or specific identification in Article 14; its official Ministry version could
not be retrieved in this review, so that reproduction has provisional source
status \citep{asbe1copy}. Caterpillar's company-authored 2024 report states
that it principally uses LIFO and supplies a FIFO comparison
\citep[Note 1.C]{caterpillar2024}. That is evidence of a disclosed US-GAAP
company policy; full ASC~330 paragraph authority remains an acquisition task.
It is not a rule that every US company must use LIFO.

Take the same purchases in three separate books: ten units at 5, followed by
ten at 7, then delivery of twelve units. FIFO charges $10(5)+2(7)=64$ to
cost of sales and leaves inventory 56. LIFO charges $10(7)+2(5)=80$ and
leaves inventory 40. Periodic weighted average uses cost $120/20=6$, charges
72 and leaves 48. The physical deliveries and supplier cash flows agree;
profit and carrying inventory differ by the selected costing rule. A concept
mapping cannot remove that difference. The FIFO/average selector in an
IAS~2 profile rejects LIFO as an unsupported election under the inspected
paragraph. The US company profile admits its evidenced LIFO policy while
retaining its narrower authority. An ASBE package remains source-provisional
until the attributed text and applicable amendments are officially verified.

Inventory impairment illustrates another required memory. Under inspected
AASB~102 paragraphs 28--34, an item costing 56 written down to net realisable
value 50 records expense 6. If the conditions reverse and net realisable
value becomes 54, reversal is 4, capped by original cost; the previous
write-down must therefore remain in state. The reproduced ASBE~1 Article 19
also addresses reversal within the earlier provision. This paragraph is not
used to assert the US treatment, whose primary authority was unavailable.
Source limitations constrain the treatment claim, while the separate-book
method and exact costing calculations remain fully specified.

\input{sections/corporate-methods}

\input{sections/corporate-extensions}


\input{sections/standards-methods}


## FILE docs/design/proposal/manuscript/chapters/14-financing-groups.tex

\chapter{Financing, ownership and the group boundary}
\label{ch:financing-groups}

A company can preserve the same operating assets while changing who supplies
its funding and who shares its results. The following cases move from debt
cash flows to ownership, then to the reporting boundary of a group. Each
numerical example states its own contract; the coupon-bearing convertible
below and the later zero-coupon modification are different instruments.

\section{Debt and hybrid financing}

The contract layer for a debt instrument stores issuer and holder perspective,
currency, issue and settlement dates, issue proceeds and legal face amount.
Its payment terms include coupon/index/spread, reset and fixing dates,
day-count convention, payment calendar, amortisation schedule and maturity.
Its rights and protections include seniority, collateral, covenants, options,
conversion terms, guarantees and linked hedges. Missing terms are
explicit unknowns. A single carrying amount cannot stand in for this record.

The accounting layer stores the classification decision and its evidence,
initial measurement, carrying amount, accrued interest, effective-rate method,
unamortised fees or discounts, fair-value disclosures, impairment or credit
adjustments where applicable, and presentation mappings. Contractual interest,
effective-interest expense, realised cash payments and fair-value changes are
separate quantities. The zero-coupon example in Chapter~\ref{ch:execution}
provides a minimal conformance case for this separation.

The lifecycle must support issuance, recognition, accrual, reset, coupon,
principal repayment, modification, derecognition, default, recovery and
conversion. A modification event first determines which accounting operation
the selected standard requires; it does not always mean issuing a new loan.
An embedded option can affect valuation and classification without being
exercised. A derivative linked as a hedge requires both the economic contract
and any applicable accounting designation; economic risk reduction alone does
not establish hedge-accounting eligibility.

Hybrid instruments make interpretation particularly consequential. IAS 32's
overview discusses liability/equity classification and the separation of a
compound instrument \citep{ias32}. The executable classification must consider
the full terms and the selected standard version. US GAAP or ASBE treatment
must be implemented under its own rules rather than inferred from an IFRS
classification. Where the terms are not disclosed sufficiently, alternative
classifications can coexist only if each is actually compatible with the
known terms and applicable rules.

\section{Equity and ownership}

Equity has both monetary accounts and security quantities. The security
register records share class, issued and outstanding quantities, treasury
holdings, par or stated value where applicable, voting rights, dividend rights,
redemption features, options and conversion relationships. Monetary equity
accounts include contributed capital, reserves, retained earnings and other
components required by the selected basis. These records evolve together
through issuance, repurchase, cancellation, split, dividend and conversion
events.

A stock split changes quantities and per-share measures without necessarily
changing aggregate monetary equity. A cash dividend affects distributions and
cash rather than current operating expense under the corresponding ordinary
equity treatment. Repurchases and employee share awards require their own
rules. Earnings per share uses a dated quantity schedule and rules for potential
ordinary shares; simply dividing profit by the closing share count is
insufficient when shares change during the period.

Funding simulations must connect the quantity register to market assumptions.
An equity issue at a scenario-dependent price changes cash raised, shares and
dilution. The model must state whether it targets a fixed cash amount, a fixed
share count or a capital ratio. These are different management decisions even
when the historical statement would report the same aggregate proceeds.

\section{A compound bond exposes classification dependencies}

Consider an issuer receiving 100 for a two-year bond paying annual coupons of
5 and principal 100 at maturity, with a holder option to convert that principal
into ten ordinary shares. Assume its currency is the issuer's functional
currency, no other options, fees or contingent settlements, and that the
conversion feature qualifies as equity under the selected rule. A comparable
liability without conversion yields 10\%. The inspected IAS~32-equivalent
text requires separate liability and equity components and measures equity
as the residual \citep[paragraphs 28--32, AG30--AG32]{aasb132}.

The liability's present value is
\[
 L_0=\frac{5}{1.1}+\frac{105}{1.1^2}
     =\frac{11050}{121}\approx91.3223,
 \qquad E_0=100-L_0\approx8.6777.
\]
Issue debits cash 100 and credits these two components. Under the stated
effective-interest schedule, the first coupon leaves liability
$1.1L_0-5=1050/11\approx95.4545$; after the second coupon it is 100.
Redemption debits liability and credits cash 100. Alternatively, conversion
at maturity debits liability and credits equity 100 while issuing ten shares;
the original equity component remains in equity. AG32 supports the absence
of a gain or loss on that maturity conversion. Exact rational valuations are
kept before the declared monetary rounding.

A variable-number share settlement, cash alternative or other clause can
change classification. The contract record must therefore retain these terms;
it cannot select liability/equity accounts independently of the coupon,
conversion and settlement rules. Early repurchase and induced conversion
invoke separate operations: the inspected AG33--AG35 text describes allocation
and the induced-conversion consideration difference. They are not implemented
by changing the maturity date of the simple example. US-GAAP and ASBE
classification require their own dated authority; the IFRS-oriented split is
never silently reused under another basis.

\input{sections/financing-methods}

\section{Control and an elimination book}

The consolidation procedure selects the control graph at each date, aligns
supported accounting policies and presentation currencies, combines controlled
entity books, and posts acquisition, elimination and non-controlling-interest
adjustments in a separate book. A control conclusion needs evidence and a
rule version. Ownership percentage alone is insufficient. Unknown purchase
allocation, currency translation or unmatched intragroup differences remain
named unresolved adjustments rather than unexplained balancing entries.

For a simplified acquisition, assume control is established, all net assets
are already at the relevant acquisition measurements, no tax or goodwill
arises, and non-controlling interest is measured proportionately. A parent
has cash 60, investment 40 and equity 100; an 80\%-owned subsidiary has cash
30, plant 20 and equity 50. Consolidation debits subsidiary equity 50,
credits investment 40 and credits non-controlling interest 10. Group assets
are cash 90 plus plant 20, and group equity is 100 attributable to the parent
plus 10 to other owners.

A subsequent intragroup loan of 10 shifts cash from parent to subsidiary,
creates a receivable and payable, and is eliminated by debiting payable and
crediting receivable 10. Group totals remain 110. An unmatched loan currency
or settlement date would block that exact elimination. If the parent instead
sells its entire interest for 44 immediately after the initial state and
loses control, the group removes subsidiary cash 30, plant 20 and
non-controlling interest 10, recognises cash consideration 44 and gain 4;
remaining cash/equity is 104. More complex acquisitions and retained interests
require additional measurement operations; this example fixes the structure
and arithmetic without certifying a complete consolidation standard.

\input{sections/groups-fx-methods}



## FILE docs/design/proposal/manuscript/sections/corporate-methods.tex

\hypertarget{operating-events}{%
\section{Operating events}\label{method-corporate-methods-operating-events}}

The operating methods use the selected revenue, inventory and asset provisions of \citet{aasb15dated,aasb102,aasb116dated}. The lease and gross-tax case uses the dated lease, income-tax and cash-flow compilations \citep{aasb16dated,aasb112dated,aasb107dated}. Each rule still needs the entity, period, transaction facts and elections described below.

Every event uses the event-basis, authorization and commit contracts described in Section~\ref{sec:posting-permission}. The event inputs described here are required in addition to identity and date. Each object identifier resolves to its contract, context and admitted source or assumption. A purported cash collection does not establish a sale; a purchase order does not establish receipt.


Revenue, billing and collection are separate transitions. A delivery event names
the contract, performance obligation, quantity, allocated price and control
evidence. Recognition first releases a related contract liability; earned
consideration not yet unconditional creates a contract asset. Both credit
revenue. A missing control finding or unresolved price constraint leaves the
recognition unresolved.

An invoice or right-to-payment event names the contract, bill and unconditional
amount. It debits the receivable and credits an existing contract asset, with
any excess recorded as a contract liability. A collection names that receivable,
settlement and amount and debits cash while crediting the receivable. An excess
payment needs a separate customer-advance method; it cannot be credited to
revenue merely because cash arrived. These transitions retain cumulative
performance, billing and collection independently.

Purchasing starts when the company receives owned goods, not when it places an
order. The event records lot, quantity, unit cost and ownership evidence, debits
inventory and credits the payable. Consigned or unreceived goods cannot pass
that ownership condition. Consumption or sale identifies an available lot
allocation, quantity and admitted cost formula; it debits cost of goods sold
or an eligible production asset and credits inventory. Overselling does not
create stock. Supplier payment separately debits the payable and credits actual
cash. Insufficient cash blocks that settlement and can trigger a separately
modelled default; it never creates a hidden loan.

A tangible-asset event records component cost, residual value, useful life,
depreciation method and the date it becomes available for use. Initial debit to
PPE has a corresponding cash or payable credit; depreciation later debits
expense or an eligible asset and credits accumulated depreciation. Employee
service records earned pay, deductions and employer obligations for the service
period, separately from settlement. Unknown labour or tax law cannot become a
zero payable.

Closing derives revenue, expenses, OCI and owner movements from those events
using admitted statement mappings. It checks cash, inventory, financing and tax
roll-forwards rather than introducing a balancing entry. These event fields
form the method's required inputs; each identifier resolves to the same
contract, context and evidence used by its authorization.


AASB 15 paragraphs 9, 22, 31, 35--43, 47--59, 73--86 and 105--108 provide the selected revenue conditions; the retained compilation applies to the stated for-profit FY 2024 example. Variable consideration is estimated under a selected method and admitted only subject to the significant-reversal constraint, not recognized solely because its unconstrained expectation is positive. Principal versus agent, returns, warranties, contract modifications and distinct bundles require their own scoped decision records. If their facts are unresolved, retain alternative eligible methods; do not borrow the simple delivery rule by label.

The following schedules make the distinction between performance and billing explicit. For one performance obligation with price 100, cumulative revenue 60, unconditional bills 50 and collection 30, AR=20, CA=10, CL=0 and cash=30. Revenue 60 is represented by those three assets. Billing before performance changes intermediate balances but not the final result. For bills 80 instead, AR=50, CA=0, CL=20; net assets remain 60. Cumulative performed-service cost 40 then 70 posts 40 then 30, not 110. A downward revision follows the correction method and keeps the old result tied to its original view.

For this simple contract, let $R$ be cumulative recognised revenue, $B$
unconditional billings and $C$ collections, with $0\leq C\leq B$. The unpaid
bills determine accounts receivable (AR); performance in excess of billing is
a contract asset (CA), while billing in excess of performance is a contract
liability (CL). After each event,
\[
 \mathrm{AR}=B-C,\quad \mathrm{CA}=\max(R-B,0),\quad
 \mathrm{CL}=\max(B-R,0),\quad \text{cash received}=C.
\]
This recurrence applies per contract, with no impairment, variable consideration or unbilled prepayment; it is not permission to offset unrelated contracts. For billing 80 before delivery, debit AR 80/credit CL 80. Recognizing service 60 later debits CL 60 and credits revenue 60. Collecting 30 debits cash 30/credits AR 30, leaving AR 50 and CL 20, without a second receivable or an artificial contract asset. If service comes first, recognize CA 60/revenue 60, then bill AR 80 against CA 60 and CL 20. Both orders end at the same state. Cash received before an unconditional bill needs an explicit advance event that debits cash and credits CL and records the advance applied to later billing; it cannot pass through collect(AR).

Inventory uses identified cost for non-interchangeable items or the admitted cost formula for interchangeable items. AASB 102.9, 23, 25 and 28--34 support lower of cost/net realizable value, relevant cost formulas and write-down/reversal conditions. A method never chooses LIFO merely to fit a reported balance. In a second lot example, purchases are 10 units at 2 and 10 at 3, followed by sale of 12 units. FIFO gives cost 26 and stock 8 units/cost 24. Weighted average gives cost 30 and stock 20. Under the same given selling price 48, margin differs 22 versus 18. Both alternatives require their own permitted policy, consistent application and evidence; matching total cash does not remove the difference. NRV 16 for the remaining FIFO lot records expense 8, inventory allowance 8; recovery to NRV 22 reverses 6, leaving allowance 2. Recovery to 30 is capped at original cost 24. US LIFO remains a separately sourced question.

The retained AASB 116.7/15, 29--30 and 48--62 support cost and depreciation. Asset 100, residual 10, three-year even use gives 30 per full year. A year-two estimate change after first-year depreciation to residual 10 and three remaining years gives (70\ensuremath{-}10)/3=20 prospectively; an error in original cost is a correction, not an estimate change. Component replacements derecognize the replaced component's remaining amount before recognizing its replacement; no perpetual double asset. Borrowing-cost capitalization, impairment, provisions, employee benefits and share-based payment are specified as additional scoped methods below, not silently assigned zero in real-company cases.

\hypertarget{lease-and-tax-integration}{%
\section{Lease and tax integration}\label{method-corporate-methods-lease-and-tax-integration}}

A lease connects asset use, a financing obligation and income tax. The following schedule extends the operating-company example by separating these three measurements. The retained lease and tax dossiers supply the dated provisions, modification case and assumptions. The official lease compilation is dated December 2023 despite the older filename. The right-of-use (ROU) asset represents the admitted use of the leased asset. Its cost, the lease liability, accumulated depreciation, remaining payments, rate version and option judgments are separate state fields. Tax retains carrying amounts, legal tax bases, reversal dates, enacted/substantively-enacted rate evidence, recovery support, and original profit/OCI/equity allocation. The deferred tax asset (DTA) and deferred tax liability (DTL) are retained gross before any permitted offset presentation. A liability schedule is not a tax-base schedule.

For the two annual 121 payments at 10\%, initial liability and ROU are 210. Year-one interest is 21, liability after payment 110, depreciation 105 and ROU 105. Year two interest is 11, and both balances finish at zero. A same-asset modification just after year one creates two future payments 144 at revised 20\%, PV 220, so liability increases 110 and ROU increases 110 to 215. A payment index reset has different rate rules; it cannot reuse that modification blindly.

To demonstrate connection to company statements, assume a synthetic entity with opening cash/equity 500, no other opening balances, and annual cash service revenue 400 less cash operating costs 100, all recognized in their years. There are no dividends, other assets, debt, losses or permanent differences. Add the base lease above. Assumed tax law deducts cash lease payments against taxable income, attributes those deductions to the lease liability, gives zero tax bases to ROU/liability, and taxes profits at enacted 25\%. Sufficient usable profits and all recognition conditions for DTA are assumed. Tax is paid the following year. No current-period tax payment is invented from tax expense.

At commencement debit DTA 52.5 and credit DTL 52.5 in addition to the lease recognition. At year-one close DTA is 27.5 and DTL 26.25. The DTA reduction 25 is deferred expense; DTL reduction 26.25 is deferred benefit, net benefit 1.25. Taxable profit is 300\ensuremath{-}121=179; current tax/payable 44.75. Pretax book profit is 300\ensuremath{-}105\ensuremath{-}21=174, total tax 43.5 and profit 130.5. At year two, deferred expense 1.25 combines with current tax 44.75 to give total tax 46 on pretax profit 184.

\begin{center}
\begin{tabular}{lrr}
\toprule Closing balance & 2024 & 2025\\\midrule
Cash & 679 & 813.25\\
ROU asset & 105 & 0\\
Deferred tax asset & 27.5 & 0\\
Lease liability & 110 & 0\\
Deferred tax liability & 26.25 & 0\\
Current tax payable & 44.75 & 44.75\\
Equity & 630.5 & 768.5\\\bottomrule
\end{tabular}
\end{center}


2024 assets 811.5 equal liabilities 181 plus equity 630.5; 2025 assets 813.25 equal liabilities 44.75 plus equity 768.5. Select financing classification for lease interest under the retained AASB 107 regime. Direct operating cash is 300 then 255.25 after the first tax payment; financing lease cash is \ensuremath{-}121 each year; no investing cash arises. Indirect operating cash in year one is profit 130.5 plus depreciation 105 plus interest 21 minus deferred benefit 1.25 plus unpaid current tax 44.75 = 300. Year two gives profit 138 +105 +11 +1.25 =255.25. The second tax payable settles next year. Zero OCI and no owner transactions mean the equity change equals cumulative profit. This case tests gross tax, cash timing and financial-statement coherence, not a real entity's tax law.

\hypertarget{returning-to-the-company-forecast}{%
\section{Returning to the company forecast}\label{method-corporate-methods-returning-to-the-company-forecast}}

The Northstar case remains the broader ordinary-company teaching baseline: collections, purchases/payments, inventory, payroll, PPE, financing, tax, statements, annual/interim and revision views are already specified. Its 2024 collection/purchase/payment solution is 245/155/145. The 2025 forecast in the Northstar reference fixture opens with cash 74.6 and equity 90.6, spends 20 on capital expenditure at period end, pays dividend 8 and uses a base floating rate 7\%. Its simplified tax is settled in the year earned. The running case uses fixed-rate share $\alpha$; here floating-rate share $x=1-\alpha$ describes the same uncertainty. For 2025 the same unknown floating fraction $x\in[0,1]$ determines every
statement amount:
\begin{align*}
 I(x)&=5+2x, & \text{pretax profit}(x)&=82-2x,\\
 \text{tax}(x)&=16.4-0.4x, & \text{profit}(x)&=65.6-1.6x,\\
 \text{operating cash}(x)&=48.6-1.6x, & \text{closing cash}(x)&=95.2-1.6x,\\
 \text{equity}(x)&=148.2-1.6x, & \text{assets}(x)&=288.2-1.6x.
\end{align*}
Receivables 55, inventory 40, net PPE 98, payables 40 and debt 100 complete the
balance sheet. Liabilities are 140 for every $x$, so the common cash/equity
slope preserves the accounting identity. There is no default distribution on
$x$. At a 9\% floating rate the all-floating history has interest 9, profit
62.4, cash 92, equity 145 and assets 285. The annual cash bounds still cannot
establish daily payment solvency without event-date cash flows.

The lease/tax example extends the interaction evidence without changing the original Northstar fixture or pretending that its teaching 20\% tax formula is an IAS 12 method. In a real-company package, each required method is admitted separately and unsupported operations remain visible. The extended obligations for pensions, impairment, provisions, valuation and share-based payment are in the additional corporate methods that follow; omission from a finite company case never proves the actual company has none.


## FILE docs/design/proposal/manuscript/sections/corporate-extensions.tex

\hypertarget{employee-benefits}{%
\section{Employee benefits}\label{method-corporate-extensions-employee-benefits}}

The additional methods below use the selected IAS 19, IAS 36, IAS 37, IFRS 2, IFRS 13 and IAS 23 provisions in the original 2023 EU incorporating regulation \citep{eu20231803}. This is historical mechanism support; later amendments and actual entity facts remain separate applicability inputs.

DefinedContributionState retains service periods, promised contribution formula, contributions due/paid and applicable legal terms. For earned service requiring contribution 10, debit employee expense 10/credit payable 10; payment settles it. Calling a plan defined contribution needs the limited-obligation facts; a guaranteed benefit or additional funding obligation cannot disappear by name.

The defined-benefit obligation (DBO) measures accrued employee benefits under the stated actuarial assumptions. DefinedBenefitState retains employee/cohort service, benefit formula, projected salary, retirement/turnover/mortality assumptions, discount-curve currency/term, obligation, plan-asset fair value, asset ceiling, contributions, benefits and remeasurements. IAS 19.67--74 requires projected unit credit and the stated service attribution; .83 supplies discount-rate requirements. Assumptions are separately admitted measurements, not constants provided by the accounting rule. A one-employee toy plan promises 100 for each completed service year, paid after year two, with certain completion, zero salary growth and supported 10\% discount. At year-one end accrued benefit 100 due in one year has PV 1000/11. In year two that opening obligation accretes 100/11 and the second earned benefit adds 100; obligation 200 then settles 200. Merely using current salary times years without timing would give the wrong year-one obligation.

A separate funded-plan roll-forward supplies an independent statement example: opening DBO 100, plan assets 80 and net liability 20; current service 12; interest 5 on DBO, interest 4 on assets at 5\%; contributions 10 at year end; benefits 8 paid from plan at year end; actuarial obligation loss 7; actual asset return 6. DBO closes 100+12+5\ensuremath{-}8+7=116, assets 80+6+10\ensuremath{-}8=88, net liability 28. Expense is 12+1=13, OCI loss is 7\ensuremath{-}(6\ensuremath{-}4)=5. Debit service expense 12/credit net pension liability 12; debit interest expense 1/credit liability 1; debit OCI 5/credit liability 5; debit liability 10/credit cash 10. End liability 20+13+5\ensuremath{-}10=28. Plan-paid benefits reduce both DBO and plan assets and do not cause a second employer cash payment. IAS 19.113, .120--127 supports these components; remeasurement OCI is not recycled to profit under 122. A surplus requires the asset ceiling and applicable minimum funding analysis, not recognition of any calculated negative liability.

Unknown actuarial inputs give conditional obligations or measurement\_unresolved. Curtailment, settlement, amendment and multi-employer/insured arrangements need their own fact conditions and measurement-date remeasurement. A buyout is not settlement if obligations remain. Sensitivities vary one assumption only when that conditional meaning is explicit; correlated risks require joint scenarios.

\hypertarget{impairment-and-provisions}{%
\section{Impairment and provisions}\label{method-corporate-extensions-impairment-and-provisions}}

ImpairmentState retains asset/CGU boundaries, carrying amounts, allocated goodwill, corporate assets, recoverable-amount inputs and previous impairments/depreciation. IAS 36.9--10 determines indicators and mandatory annual tests. Recoverable amount is the higher of value in use and fair value less disposal costs (.18); it is not the lower of two pessimistic scenarios. VIU needs the supported cash flows, forecast horizon/growth, discount and exclusion of inappropriate financing/tax or uncommitted restructuring effects under 33--57. Compute conditional values if those estimates are unknown; do not infer them from historical profitability.

For a cash-generating unit (CGU), assets excluding goodwill 100 plus goodwill 20, recoverable amount 90: loss 30 first removes goodwill 20 and then reduces other assets 10 subject to their floors under 104--105. Debit impairment 30/credit goodwill 20/credit asset allowance 10. If the asset floor is 95 the requested reduction to 90 is impermissible; apply the remaining allocation/recognition conditions, not a forced plug. For a standalone cost-model asset with carrying 80, recoverable 60, recognize 20 loss. At a later measurement before further depreciation, supported recovery to 90 permits reversal only 20 to the no-impairment 80 ceiling (.117--119). Goodwill impairment is not reversed (.124). Different dates require the hypothetical unimpaired depreciation path, not the old nominal cost as cap.

ProvisionState retains obligating past event, present legal/constructive duty, outflow assessment, estimate distribution, settlement dates, risk/discount basis, reimbursements and evidence. IAS 37.14 requires present obligation, probable outflow and reliable estimate; .36--47 governs best estimate/risk/discount. An intended future operating expenditure without that duty is not a provision. Assume an established obligation to pay 121 in two years, deterministic amount, appropriate 10\% rate and no double-counted risk: recognize expense/provision 100, accrete interest 10 then 11, settle 121. The passage-of-time increase is borrowing cost under 60. If the obligation is an eligible asset restoration cost, initial debit follows that asset's method rather than always expense; later changes need the applicable restoration interpretation. Contingent liabilities/disclosures remain visible when recognition conditions are not met; no generic 0.5 threshold may substitute for the relevant standard's required analysis.

\hypertarget{share-based-compensation}{%
\section{Share-based compensation}\label{method-corporate-extensions-share-based-compensation}}

AwardState distinguishes equity versus cash settlement, grant/vesting/service dates, granted units, grant-date fair value, service/nonmarket/market conditions, expected units vesting, cumulative expense and changes/cancellations. IFRS 2.7--11, 15--23 supports the employee equity-settled method. With 100 units, grant value 3, two-year service condition and all expected to vest, year-one cumulative expense 150 and equity 150. At vesting only 80 satisfy the service condition: cumulative 240, second-year expense 90. Debit employee expense and credit equity. Failure of a market condition is different under 21; if the employee satisfies other vesting conditions, it does not automatically reverse the grant-date measured service expense. Unknown conditions cannot be represented by a single forfeiture percentage without their type and evidence.

Cash-settled awards remeasure the liability under 30--33. Same 100 expected units, half service and current unit fair value 4 gives liability/expense 200 at year one; 80 actual units and value 5 at settlement gives total 400, second expense 200, then debit liability 400/credit cash 400. Reusing the equity grant value 3 would be wrong. Actual award valuation requires the specified model/market inputs, option rights, volatility, dividends and calibration; the fair values 3/4/5 are case inputs. Modifications and settlement-choice arrangements require their own conditions, with the original minimum expense and increment analyzed under the applicable provisions rather than overwriting the original grant.

\hypertarget{fair-value-and-capitalization-boundaries}{%
\section{Fair value and capitalization boundaries}\label{method-corporate-extensions-fair-value-and-capitalization-boundaries}}

A ValuationRequest names the unit of account, market/date, asset/liability characteristics, principal/accessible market, technique, input hierarchy, counterparty/own non-performance risk where relevant, calibration and sensitivity. IFRS 13.24, .42--43 and .67--80 guide the selected measurement. Quoted identical asset price 7 for 10 units gives 70 in a qualifying Level 1 case; a blockage discount based only on holding size cannot reduce it to 63 under 69/80. A present-value illustration 111 due next year at an independently supported 11\% rate gives 100; that equality does not establish the rate, market comparability or accounting classification. Historical EIR, an impairment discount, risk-neutral pricing and a physical expected return answer different questions.

Borrowing-cost capitalization requires a qualifying asset, eligible costs, commencement/suspension/cessation dates and the specific/general-borrowing calculation, before moving interest into cost. IAS 23.8--25 supplies these rules in the retained historical EU text: for specific borrowing, eligible actual costs less temporary investment income; for general borrowing, the applicable weighted rate and cost ceiling. Commencement requires expenditures, borrowing costs and necessary preparation activities; extended inactive periods can suspend it, and substantial completion ends it. Assume specific borrowing 100 outstanding during a full eligible construction year at 5\%, with an admitted expenditure schedule and temporary investment income 1 on temporarily unused funds during that period. Net capitalized cost is 4. Real admission still needs the dated standard, actual schedule and eligibility evidence. It is not a default 5\% add-on to all assets. Internally developed intangibles likewise need research/development separation and all applicable recognition criteria; a forecast of future sales does not establish an asset.

The extension interface returns the stated measured components, proposed journal, economic delta, disclosures and unresolved inputs under the event-basis, authorization and commit contracts. Calculation success does not permit another operation to fill a missing authority/fact with a default. Real-company acquisition/tax/employee/valuation evidence and the full exceptions remain explicit internal preparation, with proposed answers and competing treatments retained for any later authorized domain review.


## FILE docs/design/proposal/manuscript/sections/financing-methods.tex

\hypertarget{schedules-and-initial-classification}{%
\section{Schedules and initial classification}\label{method-financing-methods-schedules-and-initial-classification}}

The following liability and ownership methods use selected dated AASB 9 and AASB 132 provisions \citep{aasb9dated,aasb132}. Issuer, holder, contractual cash flow and accounting measurement remain separate throughout the schedule.

DebtContract contains parties, currency, principal, issue/settlement dates, payment calendar, fixed/index/spread/reset terms, compounding/day-count, business-day adjustment, principal changes, fees, options, security, priority and legal default/remedy terms. Each term has evidence/admission provenance. The economic schedule emits due cash independently of the recognition method. A market-value adapter may value that schedule but cannot choose amortised cost, FVOCI, FVTPL or liability/equity classification.

An investor's classification evaluates business model and contractual cash-flow features; a debt label alone cannot establish the AASB 9.4.1.2/4.1.2A conditions. At initial recognition the selected 5.1.1 rule measures fair value and qualifying costs as appropriate. An unknown day-one observable-value condition yields unresolved under 5.1.1A/B5.1.2A. The retained acquisition cases distinguish FVTPL expensed fees, amortised-cost fees, original EIR and POCI credit-adjusted EIR. No rate method inferred from market value can overwrite the contract rate.

For an issuer with a plain amortised-cost debt, net proceeds 100 and one legally due payment 121 at the end of two annual periods, the exact EIR solves 100=121/(1+r)\^{}2, hence r=10\%. Issue debit cash 100/credit debt 100; year-one debit interest 10/credit debt 10; year-two debit interest 11/credit debt 11; redemption debit debt 121/credit cash 121. Outstanding contractual payment stays 121 until settled even while carrying value is 100 or 110. Total interest 21 equals cash outflow 121 minus proceeds 100. An immediate transaction fee 2 changes net proceeds to 98 and the EIR root; retaining 10\% is wrong. The numerical root method is in the numerical-method discussion; an irrational rate is not silently an exact rational.

A fractional period uses the declared convention. Annual-effective 21\% over half a year produces factor 1.1 and interest 10 on 100; simple proration gives 10.5 and is wrong for that contract. A floating coupon resets from the admitted fixing available at the reset date, not a later observed rate. Actual day-count and holiday-calendar versions are immutable inputs. Unknown fixings preserve conditional paths, rather than defaulting to the latest value.

\hypertarget{modification-extinguishment-and-default}{%
\section{Modification, extinguishment and default}\label{method-financing-methods-modification-extinguishment-and-default}}

At a modification, retain original and replacement terms, counterparty, fees, effective date, legal-release evidence and original EIR. Determine derecognition before measurement. AASB 9.3.3.1--3.3.3 and B3.3.1--B3.3.6 govern the selected issuer-liability cases. The quantitative ten-percent test compares the PV of new terms, including specified borrower/lender fees, at original EIR against remaining original PV. It is not a universal asset test, nor proof that every change below ten percent is immaterial; changed currency, rights and other qualitative terms need the applicable analysis. Insufficient evidence remains unresolved. Third-party payment without legal release does not extinguish debt.

On the first anniversary above, old remaining 121 has PV 110. Replace with 133.1 due at the original maturity date, one year after the modification, with no fees and an explicit supported substantial-terms conclusion: PV 121 differs by exactly 10\%, satisfying the inclusive test. Assume separately supported new fair value 118; debit old debt 110, debit extinguishment loss 8, credit new debt 118. The new EIR is 133.1/118\ensuremath{-}1, not automatically the old rate. If the replacement is instead a stated non-substantial same-currency reduction to 115.5, no fees or other changes, PV 105 leads to debit debt 5/credit modification gain 5 under the B5.4.6 recalculation mechanism, then interest 10.5 and settlement 115.5. The actual change below ten percent still needs the qualitative finding. Repurchase of carrying amount 110 for 108 extinguishes the repurchased obligation: debit debt 110/credit cash 108/credit gain 2. Unamortised fees belong in the carrying amount before that comparison, not a second gain adjustment.

If cash available is 80 against debt 121 due, record the due obligation and an unpaid/default economic state; payment 80 leaves contractual unpaid 41 only when that partial payment actually occurs. Do not cancel the remaining liability, recognize a waiver or issue a loan unless a separately admitted event authorizes it. Covenant acceleration, cross-default, cure periods, collateral realization and restructuring require the actual legal terms and priority waterfall. A scenario may explore specified alternatives with explicit assumptions; it may not silently select the cheapest settlement as an accounting fact.

\hypertarget{equity-and-compound-instruments}{%
\section{Equity and compound instruments}\label{method-financing-methods-equity-and-compound-instruments}}

EquityInstrument retains class, voting/distribution/liquidation rights, issued, treasury and outstanding counts, par/legal-capital requirements and conversion terms. Share counts are integer quantities separate from currency balances. Issue 100 ordinary shares at 2 with no fees: debit cash 200/credit equity 200, issued and outstanding 100. Repurchase 10 at 3 for treasury: debit treasury-equity 30/ credit cash 30; outstanding 90, issued 100, treasury 10. Reissue 5 at 4: debit cash 20/ credit treasury-equity 15/credit other equity 5; outstanding 95, treasury 5. There is no trading profit under the selected AASB 132.33 rule; a statutory par split requires that jurisdiction's facts. Dividend declaration creates a liability only at the admitted point at which the obligation exists; proposal of a dividend is not itself payment or automatically an expense.

For a qualifying fixed-for-fixed issuer conversion option in functional currency, AASB 132.28--32 separates liability fair value and residual equity. Assume total issue proceeds 100, standalone debt fair value 90, zero coupon, maturity two years and cash redemption 100 or fixed 10 ordinary shares; no extra derivative, tax or fee. Issue debit cash 100/credit debt 90/credit conversion-equity 10. Effective interest accretes debt 90 to 100. At maturity conversion under original terms debits debt 100 and credits issued-share equity 100; the original equity 10 stays in equity (a permitted internal transfer is not income). Shares increase 10 and no redemption cash leaves. Redemption instead debits debt 100/credit cash 100; unexercised equity is not remeasured into profit. AG 32 supports no conversion gain/loss in that stated case. Variable share count, cash alternatives, foreign currency and changed conversion terms require classification/modification analysis; they cannot be forced into this example.

Financial statement mappings separate interest, modification/extinguishment results, owner transactions and cash settlement. A financing-liability note reconciles opening carrying amount, cash proceeds/repayments, effective interest, fees, conversions, modifications and FX. Total shares and earnings-per-share denominators need dates and dilution conditions; outstanding shares at year end are not a substitute for a weighted period denominator. Full option valuation, hedge accounting, EPS and legal-capital regimes remain explicitly additional methods; the proposed records preserve their required inputs.


## FILE docs/design/proposal/manuscript/sections/groups-fx-methods.tex

\hypertarget{perimeter-and-consolidation-state}{%
\section{Perimeter and consolidation state}\label{method-groups-fx-methods-perimeter-and-consolidation-state}}

The acquisition, control and currency methods below use the inspected IFRS 3, IFRS 10 and IAS 21 provisions in the retained 2023 EU text \citep{eu20231803}. The acquisition with goodwill is a new example; it does not change the preceding zero-goodwill case.

ControlAssessment records investor/investee, relevant activities, rights and their substantive/protective character, variable returns, ability to use power, principal/agent analysis, effective interval and evidence. IFRS 10.5--9 requires power, returns and their connection, with reassessment on changed facts. An 80\% share count is evidence to analyze, not an automatic substitute for control. Unknown control yields separate conditional perimeters and unresolved group results; no entity disappears merely to make reconciliation easy.

PerimeterVersion binds control intervals, ownership classes, report cutoffs, functional/presentation currency, policy-alignment adjustments and the exact source entity books. ConsolidationAdjustment is a distinct group book with matched counterparty/event references; legal-entity journals remain intact. The procedure is: select time-compatible entity books; apply supported policy alignment; translate them; add like balances/movements; eliminate investment against acquisition equity; eliminate intragroup balances, income/cost and unrealised gains; allocate profit/OCI to owner/NCI; reconcile all statements and movement notes. IFRS 10.19--23/B86--B96 support these steps. Reporting-date differences need B92--B93's conditions and intervening adjustments; a generic nearest-date join is invalid.

\hypertarget{acquisition-and-ownership-case}{%
\section{Acquisition and ownership case}\label{method-groups-fx-methods-acquisition-and-ownership-case}}

Assume a business combination, no common-control transaction, parent obtaining control and 80\% of ordinary residual interests for cash 96. Acquiree identifiable assets fair value 160 and liabilities 60 give net 100. There is no prior interest, contingent consideration, tax difference, separately unrecognized intangible, transaction cost or impairment; those absences are synthetic facts. Select proportionate-share NCI under IFRS 3.19: NCI 20 and goodwill 96+20\ensuremath{-}100=16 under .32. In parent books debit investment 96/credit cash 96. In the consolidation overlay, debit acquiree acquisition equity 100 and goodwill 16, credit investment 96 and NCI 20. Only post-acquisition income enters group performance. Asset measurement exceptions, deferred tax and a bargain gain reassessment under .36 would change the calculation; goodwill cannot absorb an unexplained missing balance.

If post-acquisition net profit is 20, all accrued in retained earnings with no dividend/OCI, NCI increases 4 to 24 and parent's attributable profit is 16. Parent buys another 10\% for 15 while retaining control: transfer 12 from NCI (10\% of current net 120), credit cash 15 and debit parent equity 3. Remaining NCI 12; goodwill 16 unchanged; no new profit. IFRS 10.23/B96 makes this an equity transaction. This example has equal ordinary rights; preference rights need their actual allocation and cannot use a simple ownership fraction.

In a separate alternative starting before that additional purchase, sell all 80\% for 130 when net assets 120, goodwill 16, NCI 24 and OCI zero. On loss of control, group gain=130+24\ensuremath{-}(120+16)=18. Derecognize individual assets/liabilities and goodwill, remove NCI, recognize consideration and gain. The separate parent book's investment gain is not added again. If 20\% is retained and 60\% sold for 100 with retained fair value 35, group gain=100+35+24\ensuremath{-}136=23; recognize the retained investment 35. Its subsequent associate/financial-asset method needs separately established significant-influence/classification facts. IFRS 10.B98--B99 also requires the appropriate prior-OCI treatment; this case assumes none.

\hypertarget{intercompany-inventory-and-tax}{%
\section{Intercompany inventory and tax}\label{method-groups-fx-methods-intercompany-inventory-and-tax}}

Assume parent's external inventory cost 60 is sold to its controlled subsidiary for 100 on credit, all still held at report date, tax ignored in the base case. Parent records AR 100/revenue 100 and COGS 60/inventory 60; subsidiary inventory 100/ AP 100. Consolidation debits AP 100/credits AR 100 and debits revenue 100/credits COGS 60 and inventory 40. Group inventory 60, revenue and COGS zero, and no group profit arises. When subsidiary later sells externally for 120, group COGS is 60 and profit 60, not 20; release the previously eliminated 40 in the continuing adjustment roll-forward. Reversing a closing overlay and recreating a new one must not recognize the profit twice.

If the purchaser's independently supported tax base is 100, group carrying amount 60 creates deductible difference 40. At assumed applicable 25\% and with all IAS 12 DTA conditions satisfied, recognize group DTA 10/deferred-tax benefit 10; reverse on outside sale. The original tax expense and cash obligations in the seller's tax jurisdiction remain. Different rates, recoverability or tax-law transfer rules change the answer; tax is not simply eliminated with group profit. For an upstream subsidiary sale, attribute elimination and related tax effects to the appropriate subsidiary/NCI performance; downstream parent's profit elimination does not mechanically reduce NCI by the same fraction.

\hypertarget{functional-currency-versus-group-presentation}{%
\section{Functional currency versus group presentation}\label{method-groups-fx-methods-functional-currency-versus-group-presentation}}

EntityCurrencyState names the functional currency and its evidenced rationale, foreign-currency nominal balances, monetary/nonmonetary classification, historical or fair-value measurement dates, rates and sources. IAS 21.21--23 and .28 require transaction-date translation and closing-rate remeasurement of monetary items; historical-cost nonmonetary assets retain transaction-date rates. A functional currency change is prospective under .35--37. Hyperinflation, lack of exchangeability and hedge accounting require separate applicable methods; do not import the historical .26 text into a later amended period without checking it.

Example: buy goods for foreign 100 at functional 1.2 per foreign unit; debit inventory 120/credit payable 120. Closing rate 1.3 gives payable 130 and FX expense 10, while inventory remains 120 before any NRV test. Pay at 1.25: debit payable 130/ credit cash 125/credit FX gain 5. Cumulative expense 5 matches 125 cash less 120 asset cost. Translating the inventory again to 130 would be wrong for this declared basis.

Group presentation is a different operation under IAS 21.39--41. A subsidiary has opening net assets 100, equity 100, no debt or distributions, annual profit 20 entirely earned at rate 1.25, and closing assets 120. Opening historical rate 1.2 and closing 1.3 give translated assets 156, contributed/opening equity 120 and profit 25; translation OCI 11 reconciles the difference. It is explained as 100\ensuremath{\times}(1.3\ensuremath{-}1.2)+20\ensuremath{\times}(1.3\ensuremath{-}1.25)=11, not a free balancing plug. If ownership is 80\%, parent/NCI shares of profit are 20/5 and OCI 8.8/2.2 under the stated equal rights. Use transaction rates; an average is acceptable only as a justified approximation, not when significant fluctuation invalidates it. Goodwill and fair-value adjustments follow IAS 21.47's foreign-operation treatment, rather than freezing them automatically in the parent's currency.

Group reports retain the translation reserve by entity, ownership and event. Loss of control requires the appropriate reserve reclassification under IAS 21.48 and IFRS 10.B99; a no-control-loss change transfers the relevant attribution in equity under applicable conditions. Cash translation effects reconcile cash separately from operating/investing/financing movements. An intercompany monetary balance's exchange result cannot simply be eliminated as if no currency exposure existed; IAS 21.45 and net-investment .32 require the substantive classification.


## FILE docs/design/proposal/manuscript/sections/standards-methods.tex

\hypertarget{rule-selection}{%
\section{Rule selection}\label{method-standards-methods-rule-selection}}

The proposed selection procedure distinguishes operative authority from historical source support. The retained sources include official AASB compilations, the original EU incorporating regulation and an official ASBE 21 publication \citep{aasb9dated,aasb15dated,aasb16dated,aasb112dated,eu20231803,mofasbe21}. Historical US lease additions are separately identified in the retained amendment source \citep{fasbasu201602}.

AuthorityRequirement contains issuer/framework, jurisdiction, entity class, annual-period/application interval, paragraph and local source Ref, incorporating instrument, amendment chain, transition, elections and unresolved dependencies. RuleSelection binds those requirements to the accounting event and evidence view. The algorithm evaluates chronological applicability first, then scope and facts, then available elections/transition, then measurement/presentation. If two supported rules can apply, retain the explicit alternative and required election; if one is contradicted by facts, mark ineligible. Missing current authority gives unresolved, never eligibility through a familiar rule name.

An unchanged historical report remains an assertion under its own basis and vintage. A harmonized comparison creates an adjustment book and reconciliation, with changed recognition/measurement explained. Label mapping alone cannot convert US GAAP to IFRS or ASBE. The four clocks and source version remain part of each rule dependency; later knowledge cannot leak into an original as-of view. Transition entries reconcile opening assets, liabilities, tax and equity, rather than changing old source bytes or plugging an unexplained amount.

\hypertarget{ifrs-and-incorporating-jurisdictions}{%
\section{IFRS and incorporating jurisdictions}\label{method-standards-methods-ifrs-and-incorporating-jurisdictions}}

The retained official AASB texts provide explicit IAS/IFRS incorporation for their stated entity/version scope. AASB 9/15 compilation dates are 31 December 2022 with the source covers' application window; AASB 16 compilation 8 is 31 December 2023, AASB 112 compilation 7 is 29 September 2023. Their filenames are not date evidence. AASB 102's older retained edition is selected historical support for inventory, not current 2024 applicability certification. The retained EU 2023/1803 original provides official EU-adopted IFRS 3/10/IAS 19/21/36/37/IFRS 2/13 passages inspected in this method investigation; its historical adoption scope and later amendments remain separate. The retained amendment investigation supplies additional source evidence, not a blanket acceptance of all rules in these standards.

Initial real-method admission is therefore claim-specific: the selected revenue, lease/tax, financing, credit, group/FX and insurance cases must resolve each named applicability prerequisite. For synthetic demonstrations, declare the chosen dated provisions and assumptions and use the synthetic book mode. No assertion of whole-IFRS compliance follows from those entries.

The base lease in the saved dossiers (two annual 121 payments, 10\% rate, no qualifying exemptions or extra costs) has liability 210 initially, 110 after year one, 0 after year two. IFRS-equivalent cost-model ROU is 210/105/0; expenses 126 then 116. Income tax needs its own legal deductions and gross temporary differences, as the connected corporate case demonstrates. Revenue timing, inventory cost formula, financial instrument classification, control and contract boundaries are required rule predicates, not accounting options chosen after seeing which outcome fits best.

\hypertarget{us-gaap-proposed-methods-and-authority-limitation}{%
\section{US GAAP proposed methods and authority limitation}\label{method-standards-methods-us-gaap-proposed-methods-and-authority-limitation}}

The saved official FASB ASU 2016-02 Section A and later 2020-05/2021-09 amendments contain inspected historical ASC 842 additions. Their covers explicitly say an ASU is not authoritative. Current Codification access returned 403 again in this source investigation; the proposed methods cannot be marked current-authority-admitted. ASU amendments, historical FAS 109, issuer accounting policy and a model's memory are all insufficient substitutes for the operative ASC text and full applicable amendment chain. 

The same lease facts include ten-year remaining equipment life, fair value 1000, alternative use to lessor, no ownership transfer, no purchase option, two-year term and PV 210. Under the inspected historical 842-10-25-2/25-3 provisions, the stated facts support the proposed operating classification. Historical 842-20-25-6 and 35-3 yield single lease expense 121 per year, liability 210/110/0 and ROU 210/ 110/0. First year debit lease expense 121/credit liability 21/credit ROU 100; payment debits liability 121/credits cash 121. Next expense 121 decomposes into liability interest 11 and ROU reduction 110. The finance comparison uses the separate depreciation 105 plus interest 21/11 path. Changing classification facts is not a free election. The 75\%/90\% heuristics in the historical guidance cannot become universal requirements. This complete numerical contrast is useful despite the remaining current-authority limitation.

Proposed ASC 740 temporary-difference treatment retains tax base, reversal dates, enacted rates, valuation allowance and source-specific allocation/presentation. The saved historical FAS 109 and ASU 2019-12 provide inspected enactment support, not a completed current ASC 740 implementation. Under the matched PPE case, book 800/tax 600 at assumed 25\% yields DTL 50 and current tax 75 on taxable 300. A future 30\% rate that is merely substantively enacted but not legally enacted cannot be imported from the AASB 112 rule into this proposed US treatment; the saved matrix shows 75 versus 90 on a 300 closing difference under the declared 2025 facts. Actual legal enactment remains a separate jurisdictional fact.

The proposed CECL method for in-scope amortised-cost assets estimates lifetime expected cash shortfalls from origination using past/current/forecast evidence, with a documented reversion method beyond a reasonable/supportable forecast horizon and applicable instrument exceptions. It retains allowance roll-forwards, write-offs, recoveries, purchased-credit-deteriorated handling and off-balance commitments separately. It must not copy IFRS 9's 12-month/SICR staging to the same record. A candidate contrast: lifetime discounted loss 6 with 2 attributable to default events in the next year gives IFRS general Stage 1 candidate 2 versus CECL lifetime candidate 6, conditional on scope and method support. No current ASC 326 text was retrieved, and the attempted official amendment path returned 403; this contrast remains an explicitly unadmitted proposed reading, not a source-verified US requirement or posting example. Full current ASC 326, insurance 944, consolidation 810, FX 830 and relevant later amendments are specific internal source tasks before corresponding real admission.

\hypertarget{asbe-official-lease-support-and-remaining-tax-sources}{%
\section{ASBE official lease support and remaining tax sources}\label{method-standards-methods-asbe-official-lease-support-and-remaining-tax-sources}}

The official Ministry of Finance ASBE 21 page was successfully retrieved in this source investigation. The retained HTML and extracted text preserve the original Chinese wording. Page publication is 28 October 2019; article 68 states effect from 1 January 2019. The separate 2018 issuance notice with entity-specific staged application remains inaccessible, so the page alone does not establish every entity's adoption date or the complete amendment chain. The saved preparation packet's secondary reproduction remains historical evidence, with this new official source taking precedence for the actual inspected wording.

Articles 4--8 require control of identified use, economic benefits and direction; article 6 includes both conditions for substantive substitution and the express presumption when difficult to determine. Articles 14--18 specify commencement, ROU cost and PV, using implicit rate or incremental borrowing rate if the former cannot be determined. Articles 20--23 separate cost-model depreciation and periodic interest; articles 25--29 distinguish reassessment/index changes/modifications and their discount-rate rules. Articles 30--33 define the exemptions; a two-year term is not short-term. Articles 60--67 specify transition choices and disclosures; the chosen transition cannot be inferred from a present closing liability.

For the declared base lease, these inspected recognition/measurement provisions support proposed ROU 210/105/0 and liability 210/110/0 with expense 126/116, under the same stated facts, depreciation assumption and fixed rule version. A same-asset modification is tested against 28--29, rather than labeled a separate lease without increased scope and commensurate consideration. A 2019 first-adopter using article 61(2) records cumulative opening changes without adjusting comparatives, while 61(1) is retrospective; comparison datasets must retain that distinction and the entity's actual election.

Official ASBE 18 and Interpretation 16 pages still returned 502. The retained official 2023 MoF tax application case explicitly discusses equal lease temporary differences and Interpretation 16; it supplies a precise proposed answer for this case, not a complete current income-tax standard or real tax law. Reproducing the old initial-recognition exception from ASBE 18 without the later interaction would contradict this official application evidence. Keep gross lease DTA/DTL and the admitted tax-base/recovery assumptions in proposed calculations, but require operative text, effective-period/transition and actual law before real permission. Full ASBE 22 credit, consolidated statements, group combinations, and insurance revisions likewise retain named source dependencies; do not assert full IFRS equivalence from similar amounts.

\hypertarget{matched-case-outcomes-and-decision}{%
\section{Matched-case outcomes and decision}\label{method-standards-methods-matched-case-outcomes-and-decision}}

\begin{longtable}[]{@{}ll@{}}
\toprule
\begin{minipage}[b]{0.47\columnwidth}\raggedright
Input changed or withheld\strut
\end{minipage} & \begin{minipage}[b]{0.47\columnwidth}\raggedright
Required consequence\strut
\end{minipage}\tabularnewline
\midrule
\endhead
\begin{minipage}[t]{0.47\columnwidth}\raggedright
Framework changes with same lease facts\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
Preserve different expense/ROU paths and source strength, not just rename accounts\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.47\columnwidth}\raggedright
Method source present but target entity's adoption unknown\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
Unresolved applicability, no real posting authorization\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.47\columnwidth}\raggedright
ROU/liability initially equal\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
Still evaluate gross tax differences and later divergent balances\strut
\end{minipage}\tabularnewline
\begin{minipage}[t]{0.47\columnwidth}\raggedright
Historical rule supports method but a later reporting year is requested\strut
\end{minipage} & \begin{minipage}[t]{0.47\columnwidth}\raggedright
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

These decisions establish a common procedure and specific proposed treatments. The broader promised authority coverage remains incomplete. The new official ASBE lease support narrows that blocker; it does not erase the specific US, ASBE tax/sector, legal and current-applicability work. Feasible internal preparation continues without a paid engagement.


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
