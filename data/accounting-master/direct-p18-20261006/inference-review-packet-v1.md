# Bounded P18 inference integration review

You are an independent read-only reviewer. No tools, files, commands, edits or further reviewers. Review only this self-contained packet, not the whole proposal.

Check the Northstar common parameter and source clocks, history constraints, measure and probability handling, Gaussian/Bayes/causal derivations and numerical error boundaries. Check teaching order and supported initial versus later inference scope.

Accepted P16 architecture and P17 scoped methods are comparison baselines, not proof of full readiness. The candidate builds (122 pages, zero serious LaTeX warnings); render inspection is separate. Current ASC, whole real-company semantics, insurance transition/full VFA, actual regulatory/actuarial data, and human acceptance remain open. Do not label those honestly retained gaps a new P18 transcription failure. Source provenance is frozen; no new literature search is claimed.

Budget the review to finish in one response. Give at most 6 concrete findings, each with exact file/section and necessary repair, plus a brief reason for the verdict. Focus first on material mismatches; do not perform or narrate an exhaustive re-derivation of every case. Limit your final answer to 1000 words. End with exactly VERDICT: AGREE or VERDICT: REVISE. AGREE accepts only this packet's integration scope, with any minor nonblocking findings explicitly labelled.


## FILE docs/design/proposal/manuscript/chapters/13-reference-company.tex

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
2024; both possible contract types charge 5\% during that year.

The six months ending June and December provide two successive observation
periods. Here the chosen accrual convention assigns one half-year to each.
Cash-flow dates within a half-year are not recovered from a period aggregate;
the synthetic history supplies a feasible ordering in which inventory is
purchased before delivery and customer receipts precede the payments they fund.
More detailed liquidity questions require more detailed dates.

\begin{center}
\begin{tabular}{lrr}
\toprule Movement & First half & Second half\\\midrule
Delivered sales on credit &110&150\\
Customer collections &110&135\\
Inventory purchases on credit &70&85\\
Supplier payments &65&80\\
Cost of goods delivered &75&90\\
Payroll paid &20&22\\
Plant purchased at period end &10&12\\
Depreciation &5&6\\
Interest accrued and paid &2.5&2.5\\
Tax expense &1.5&5.9\\
Tax paid &3.5&3.9\\
Dividends paid &4&5\\\bottomrule
\end{tabular}
\end{center}

Each row has an economic meaning before it has a posting. Delivery of the
good transfers control and creates an unconditional receivable; invoicing is
assumed simultaneous in this example. Collection settles that receivable.
Purchases increase inventory and trade payables; paying the supplier settles
the payable. Delivery separately removes inventory at cost. Plant purchases
are capital expenditure, while depreciation consumes its service potential.
The addition of 10 enters service after June and has a five-year life, producing
one unit of second-half depreciation. The addition of 12 enters service after
December and has a twelve-year life.

Tax is deliberately simple: 20\% of positive profit before tax, with all these
expenses deductible and no deferred tax. The first-half payment exceeds its
tax expense by 2, leaving prepaid tax; that prepayment is used in the second
half. A genuine corporate tax package would need jurisdiction, tax basis,
losses, timing differences and payment schedules. The example's tax rule
governs its own numbers only.

\section{Recovering movements without inventing invoices}

Suppose the annual report discloses sales of 260, cost of sales of 165 and the
opening and closing working-capital balances, while the collection and purchase
totals are hidden. Under Northstar's explicit no-write-off, no-acquisition and
no-currency-effect scope, the three bridges are
\begin{align}
35&=20+260-C,\label{eq:ns-ar}\\
20&=30+P-165,\\
30&=20+P-S.
\end{align}
Here $C$ denotes collections, $P$ purchases and $S$ supplier payments, all in
currency units over the same year. Substitution gives $C=245$, $P=155$ and
$S=145$. These are identifiable aggregate movements within this model. They do
not identify which invoice was paid on which day. If acquisitions or write-offs
are admitted, their movement variables enter the same bridges and these totals
may cease to be unique.

The loan remains different. Write $F$ and $V$ for fixed and floating principal.
The source imposes $F+V=100$, $F,V\geq0$ and
$0.05F+0.05V=5$. The last equality adds no information about the split.
Both endpoints and every intermediate allocation survive. Northstar therefore
has identified working-capital totals and an unidentified financing exposure
in the same joint historical family. A solver must not turn its convenient
witness $F=0$ into the company's recovered contract.

The model's historical slots are one delivery, collection, purchase, supplier
settlement, payroll, plant addition, depreciation, interest, tax payment and
dividend per half-year. Each slot represents a classified aggregate event.
The template for collection contributes $+C$ to cash and $-C$ to receivables;
its state effect reduces the unpaid receivable pool by $C$. The purchase
template adds inventory quantity $P/5$, inventory cost $P$ and a payable $P$.
A cash-balance identity by itself cannot substitute for either template.

\section{The complete historical statements}

The corrected statements follow from those movements. Temporary income and
expense accounts close to retained earnings at each half-year boundary;
annual income is the sum of the two periods' classified movements, excluding
closing entries.

\begin{center}
\begin{tabular}{lrrr}
\toprule Balance & Opening & June & December\\\midrule
Cash &60&65&74.6\\
Receivables &20&20&35\\
Inventory &30&25&20\\
Plant, net &80&85&91\\
Prepaid tax &0&2&0\\
Total assets &190&197&220.6\\\midrule
Trade payables &20&25&30\\
Debt &100&100&100\\
Share capital &50&50&50\\
Retained earnings &20&22&40.6\\
Liabilities and equity &190&197&220.6\\\bottomrule
\end{tabular}
\end{center}

Annual revenue of 260 less cost of sales 165, payroll 42, depreciation 11 and
interest 5 gives profit before tax of 37. Tax expense is 7.4 and profit is 29.6.
Other comprehensive income is zero under the declared scope, so total
comprehensive income is also 29.6. Equity moves from 70 to
$70+29.6-9=90.6$ after dividends.

The cash-flow statement supplies an independent reconciliation. Collections
245 less supplier payments 145, payroll 42, interest 5 and tax payments 7.4
produce operating cash of 45.6. Investing cash is $-22$ and financing cash
is $-9$, giving a cash increase of 14.6. The indirect route gives the same
operating cash: profit 29.6 plus depreciation 11, minus the receivables
increase 15, plus the inventory decrease 10 and the payables increase 10.
The prepaid-tax balance is zero at both annual endpoints. The two cash routes
use different information and therefore provide a useful check on classification.

\section{A correction changes what was knowable}

The original interim filing reported revenue of 120 and receivables of 30.
Ten units of revenue had been recorded before delivery. Its tax expense was
3.5, profit 14 and equity 80. The annual filing subsequently corrected the
interim revenue and receivable by 10 and recognised the excess tax payment as
prepaid tax of 2. Corrected interim profit is 6 and equity is 72, as above.
The original statement remains an accurate record of what was published, even
though its revenue recognition was wrong under the stated delivery rule.

For the temporal fixture, the original report becomes available on 1 August
2024 and is ingested on 3 August. The correction and annual report become
available on 2 March 2025 and are ingested on 5 March. An investor-information
query as of September 2024 returns 120. The same query as of 3 March 2025
returns 110 when evaluated using the subsequently acquired archive. A query
that additionally asks what the database contained on 4 March still returns
120. Publication and ingestion answer different questions.

The annual total 260 and corrected interim total 110 share revision group
\code{v2}, so second-half revenue is $260-110=150$. Subtracting the original
120 would yield 140, but that result mixes incompatible revisions. The query
must reject the subtraction unless a reviewed compatibility relationship
supports it. A later date alone does not establish such a relationship.

\section{One economic scenario, several complete futures}

For 2025, assume demand for 30 units at price 10, unit purchase cost 5 and a
target closing inventory of eight units. Opening inventory is four units, so
the purchase decision is $30+8-4=34$ units, costing 170. Deliveries cost 150,
leaving inventory of 40. Collect 90\% of current sales and 10 of old
receivables: $270+10=280$, leaving receivables of 55. Pay old suppliers 30
and 130 of the new purchases, leaving payables of 40. Payroll is 50, capital
expenditure of 20 occurs at year-end and dividends are 8.

These decisions are inputs to a conditional forecast. They are not estimates
of demand or optimal management responses. No new borrowing is available.
Under the existing asset schedules, depreciation is $10+10/5+12/12=13$.
The new year-end asset begins depreciation in the next period. Let
$\alpha=F/100$. With the floating rate resetting to 7\%, interest is
$I=7-2\alpha$. Profit before tax is
$300-150-50-13-I=80+2\alpha$, giving tax $16+0.4\alpha$ and profit
$64+1.6\alpha$.

\begin{center}
\begin{tabular}{lrr}
\toprule 2025 statement amount & All fixed & All floating\\\midrule
Revenue &300&300\\
Interest expense &5&7\\
Tax expense &16.4&16\\
Profit and comprehensive income &65.6&64\\
Operating cash flow &48.6&47\\
Investing cash flow &$-20$&$-20$\\
Financing cash flow &$-8$&$-8$\\\midrule
Closing cash &95.2&93.6\\
Receivables / inventory / net plant &55 / 40 / 98&55 / 40 / 98\\
Assets &288.2&286.6\\
Payables / debt &40 / 100&40 / 100\\
Equity &148.2&146.6\\\bottomrule
\end{tabular}
\end{center}

The joint symbolic result is cash $93.6+1.6\alpha$, profit
$64+1.6\alpha$ and equity $146.6+1.6\alpha$, with the same
$\alpha\in[0,1]$ throughout. Selecting the smallest cash and largest equity
independently would describe no feasible company. A requested distribution
requires a measure over that same historical family; the accounting equations
do not supply one.

The later method schedules use the floating share $x$ rather than the fixed
share $\alpha$ used here: $x=1-\alpha$. Both parameterisations describe the
same joint family. Its 2025 opening cash is 74.6 and equity is 90.6; the
forecast spends 20 on period-end capital expenditure, distributes 8 and settles
its stipulated tax in the same year. These teaching assumptions are retained
when the later lease example introduces a different tax-payment schedule.

\section{Apple: source labels do not identify exposure}
\label{sec:apple}

The real reference package is Apple's 2024 Form 10-K and first-quarter 2025
Form 10-Q, for fiscal dates 28 September and 28 December 2024 respectively
\citep{apple2024,apple2025q1}. The annual balance sheet also supplies
30 September 2023. The annual filing is archived as the company's PDF from
AnnualReports; the interim filing is archived from SEC EDGAR with its inline
XBRL. Apple's Note 1 describes a 52/53-week year ending on the last Saturday
of September. Calendar-year assumptions would therefore misstate the periods.

The package inventory preserves every annual PDF page and every interim
top-level section, all thirteen annual notes and all ten interim notes.
It records internal cross-references and externally incorporated material,
including the proxy statement, as distinct obligations. Statement and debt
facts below are structured; policies, other notes and exhibits retain their
source locations and specific modelling obligations. This is complete
inventory coverage of the acquired files, with partial semantic formalisation.
It does not claim to reconstruct every Apple contract or to have acquired
every incorporated external document.

Apple's annual balance sheet reports assets 364,980, liabilities 308,030 and
equity 56,950, in millions of US dollars. Note 9 reports term-debt principal
97,341, unamortised discount/premium and issuance costs of $-321$, and hedge
accounting adjustments of $-358$. Thus its carrying amount is
$97{,}341-321-358=96{,}662$, split into current 10,912 and non-current
85,750. Fair value is separately disclosed as 88.4 billion. None of these
three measurements may replace another merely because a table calls it debt.

Note 9 identifies the notes as fixed-rate, then states that interest-rate
swaps effectively convert a portion to floating rates. Note 4 reports
interest-rate contract notional of 14,575 at the annual date. A notional is
neither a liability carrying amount nor sufficient information for an exact
interest sensitivity: reset timing, remaining periods, curve conventions and
hedge coverage still matter. The cross-reference connects the derivative to
the borrowing without erasing either contract.

At the interim date, total term-debt carrying amount is
$10{,}848+83{,}956=94{,}804$. Cash is 30,299, total assets 344,085,
liabilities 277,327 and equity 66,758. The interim debt note's rounded
``94.8 billion'' and the statement's 94,804 million can coexist; their
precision differs. Treating them as conflicting exact numbers would create
an artificial infeasibility.

To demonstrate a source-to-forecast calculation, freeze the interim balance
sheet and apply a \emph{marginal} financing stress for a following 13-week
period: a 200-basis-point rate increase, no principal change, no offsetting
hedge beyond the explicitly selected exposure, immediate cash settlement and
no tax effect. An assumed effective floating exposure $E=14{,}575$ million
produces $0.02\times(13/52)E=72.875$ million additional interest. This exposure
uses the annual notional as a conditional input; it is not asserted to be the
interim net sensitivity. Under that condition, debit interest expense and
credit cash by 72.875. The resulting marginal statements have cash 30,226.125,
assets 344,012.125, liabilities 277,327, equity 66,685.125, profit and comprehensive
income of $-72.875$, and operating cash flow of $-72.875$ relative to the frozen
baseline. The balance-sheet difference equals the equity difference exactly.

If exposure is instead only restricted to $0\leq E\leq14{,}575$, the
conditional added interest lies in $[0,72.875]$ before monetary rounding. That
restriction is a stress assumption and is not claimed to bound every real
Apple exposure. This real case verifies evidence, context, mappings and a
coherent marginal propagation. Northstar supplies the complete-company
forecast; a complete Apple forecast remains dependent on its unmodelled
operations and undisclosed terms.


## FILE docs/design/proposal/manuscript/chapters/02-history.tex

\chapter{Representing a company's historical record}
\label{ch:history}

Northstar's corrected receivable and Apple's several debt amounts show why
the source record must retain more than a label and a number. The procedures
below determine which assertions enter a model and which remain unresolved.

\section{The record is a collection of assertions}

The original record includes financial statements, notes, accounting policies,
auditor opinions, management discussion, segment tables, security terms,
regulatory returns and subsequent announcements. A complete ingestion process
accounts for every page and every extracted block. A complete financial model
is a stronger claim: it would require economically relevant information that
public reports may never disclose. AccDSL therefore reports document coverage,
semantic coverage and simulation coverage separately.

Each source span receives a disposition: structured observation, narrative
assertion, relationship, policy evidence, contextual material, duplicate, or
unresolved extraction. ``Unresolved'' remains visible. A commitment buried in a
note is not discarded because it has no current balance-sheet line. An auditor's
qualification is retained as evidence about the record; it does not become an
automatic numerical haircut. Management's forecast is a dated assertion with
an author and modality, not an observed future outcome.

An observation is an immutable record with the fields below. Values inferred
from observations are separate records, linked by a derivation. This avoids
overwriting a company's statement with an analyst's preferred reconstruction.

\begin{longtable}{L{35mm}L{101mm}}
\toprule Field group & Minimum contents\\\midrule\endhead
Identity and source & Observation ID; document hash; filing identifier;
PDF page and bounding box or HTML/XBRL locator; literal text; extraction version.\\
Reporting context & Legal entity; reported group perimeter; statement or note;
instant or interval; standard and taxonomy versions; dimensions such as segment,
product, geography, seniority or measurement category.\\
Amount & Original string; parsed number; sign interpretation; unit; scale;
currency; precision or rounding interval; missing-value category.\\
Meaning & Source label; taxonomy QName when present; one or more proposed
concept mappings; whether the assertion is reported, estimated or conditional.\\
Timing & Economic validity when known; reporting period; publication and
availability timestamps; ingestion timestamp; correction or supersession links.\\
Reliability and review & Extraction confidence, reviewer decision, source
status and known contradictions, all distinct from a probability over histories.\\
\bottomrule
\end{longtable}

A narrative assertion adds actor, predicate, object, scope, quantifier and
modality. For example, ``substantially all debt is fixed rate'' has a source
span and a qualitative quantifier. It does not assert $\alpha=1$. A reviewed
interpretation can introduce a numerical restriction such as
$\alpha\geq a$, but the threshold $a$ remains an analyst assumption unless
the source defines it. Boilerplate policy language also does not prove that a
company holds a particular instrument.

\section{Different names, different measurements}

An accounting concept is more than a row label. ``Debt'' can refer to legal
principal, amortised carrying amount, undiscounted contractual cash flows or a
fair-value disclosure. These amounts can all be correct at the same date.
Likewise, ``revenue'' may be reported gross or net, a segment measure may differ
from the consolidated measure, and an alternative performance measure may
exclude selected expenses. A mapping must state its relationship: equivalent
meaning, component of, broader than, presentation reclassification, or
measurement transformation.

The common vocabulary will preserve source concepts as first-class identifiers.
Company extensions may inherit a broad economic category without being declared
identical to a standardised concept. For instance, an extension can be a
component of borrowings while retaining an unresolved split between lease
liabilities and other financing. Many-to-many mappings are allowed; each
mapping has applicable dates, dimensions and evidence. An aggregation mapping
does not silently become a measurement conversion.

Standards differ in recognition, measurement, presentation and disclosure.
Consequently, conversion between IFRS, US GAAP and Chinese Accounting Standards
for Business Enterprises (ASBE) is not generally a dictionary lookup.
The original basis remains preserved, and any comparison basis is a separate
derived book. The same principle applies to tax and prudential capital. A tax
loss carryforward, accounting deferred tax asset and regulatory capital
deduction can concern the same economic loss while belonging to different
measurement systems.

\section{Time, revisions and information availability}

At least four times matter. A machine may enter service in November; its cost
appears in the accounts for the year ending December; the annual report is
published in March; and AccDSL ingests the report in April. A later report may
revise the December comparative. These times answer different questions and
must remain distinct.

The storage model uses validity intervals for economic assertions and
transaction intervals for database versions, following the distinction in
\citet{snodgrass1986}. Publication and availability timestamps are additional
domain fields. Database transaction time records what AccDSL contained; it
cannot substitute for what investors could have known. An ``as known on''
query applies an explicit availability rule and does not include a later
restatement simply because its economic period is earlier.

AccDSL supports three named views: the original filing view; the latest
restated view, with a stated information cutoff; and a harmonised research
view, with explicit transformations. No view changes the stored source facts.
Corrections have links to the replaced assertion and a reason. Where two
sources conflict without a clear supersession relationship, both survive with
a conflict record.

Instant values and interval flows have different types. A balance at 30 June
is not a six-month flow. Calendar intervals use half-open boundaries
$[t_0,t_1)$ internally; a filing period ending 30 June maps to the next boundary
at 1 July in its reporting calendar. Quarter-only earnings may be derived from
year-to-date values only if the periods, basis, perimeter, units and revision
vintage are compatible. The derivation retains both source observations and
their correlated rounding uncertainty. Fifty-two/fifty-three-week calendars,
stub periods and reporting-date changes require explicit calendar objects.

Accounting-policy changes, estimate changes and error corrections also have
different temporal effects. The applicable rule package decides whether a
change is prospective, requires restatement, or adjusts opening balances.
The engine never infers that effect from a generic ``revision'' flag.

\section{The company boundary changes}

Legal entity, reporting group and economic exposure are separate dimensions.
Acquisitions, disposals, changes in control, joint arrangements, special-purpose
vehicles and non-controlling interests can change the reporting perimeter.
A group's increase in property need not be capital expenditure; it may reflect
an acquisition, a currency translation or a revaluation. The bridge between
opening and closing property must identify these movements before a scenario
model can extrapolate investment.

The company graph therefore stores dated ownership, control and counterparty
relationships. Control is an accounting conclusion with supporting evidence,
not a rule that blindly consolidates every majority-owned entity. Group
reporting combines entity books with a separate adjustment and elimination
book. Intragroup receivables and payables require matching counterparties,
currencies and dates. Unmatched eliminations remain unresolved; a balancing
``plug'' is not a recovered transaction.

Acquired opening balances, goodwill, purchase-price allocation, divested
operations and non-controlling interests each have their own event types.
Analyses can preserve reported scope or define a constant perimeter, but the
latter is a derived modelling assumption, not the original record.

\section{Further problems that the representation must handle}

Several difficulties extend beyond differences in standards, industries and
company labels. Recognition and settlement occur on different dates: a sale,
invoice, cash receipt and impairment can belong to four periods. Net balances
hide gross flows: repeated borrowing and repayment can leave the same closing
debt. Netting can conceal offsetting exposures and liquidity needs. Different
contractual maturities and repricing dates can share the same current carrying
amount. Guarantees, undrawn credit facilities, litigation and covenants can
be economically important before an asset or liability is recognised.

Foreign currency introduces transaction currency, functional currency and
presentation currency, together with different translation conventions for
stocks and flows. Currency translation effects must not be mistaken for cash
receipts. Inventory and depreciation depend on vintages or lots; an aggregate
stock and average age may be insufficient under a shock. Tax bases can evolve
differently from carrying amounts. Deferred tax recognition requires assumptions
about recoverability, rather than multiplication by a tax rate alone.

Public information is selectively disclosed and rounded. Duplicate XBRL facts
may agree, overlap within rounding bounds or contradict one another. A dash
can mean zero, immaterial, unavailable or inapplicable. Tables can mix units,
span pages and embed signs in parentheses. Text and table references can be
wrong in the source itself. AccDSL retains these distinctions and gives an
analyst a local repair path without pretending that extraction confidence
settles economic interpretation.

Finally, strategic behaviour matters. A firm may refinance, cut investment,
raise equity, change prices, breach a covenant or fail. A bank may preserve a
capital ratio by shrinking assets; an insurer may change reinsurance or asset
allocation. Such responses cannot be deduced from the balance-sheet identity.
They require explicitly calibrated or assumed policies, and alternative
policies must remain separate when the available record does not distinguish
them.

\section{Account for a disclosure before translating it}

The importer first freezes a filing package: documents, byte hashes, reporting
dates, availability evidence and incorporated references. It compares the
document's contents page and statement index with detected section and note
headings. A missing heading, table continuation or referenced exhibit creates
an obligation to resolve; successful text extraction cannot discharge it.
Each PDF page and each HTML content unit then has a stable locator and a
disposition. Child units such as a table or note belong to a parent page/section;
the importer records overlap instead of counting the same content twice.

Three denominators remain separate. Acquired-document coverage counts source
units with a disposition, including unresolved units. Semantic coverage counts
identified assertions whose meaning and context have been reviewed. Simulation
coverage counts the operations and exposures required by a specified query
that have supported state and rules. The first can be complete while the other
two are partial. An assertion inventory can itself be incomplete; until the
page/section reconciliation is reviewed, semantic coverage is a lower-bound
inventory rather than a percentage of all financial meaning.

Cross-reference traversal is a work-list algorithm. Start with the filing's
statement and note references, resolve each target against the acquired
manifest, add newly discovered targets, and stop when no unvisited target
remains or a declared resource limit is reached. Document hash plus target
locator prevents cycles from expanding forever. A target has one of four
results: resolved, duplicate of a resolved source, unavailable, or ambiguous.
The last two remain obligations. Apple's proxy and prior-filed agreements
show why closure over acquired files is weaker than closure over incorporated
disclosures. A manifest may declare a bounded acquisition scope, but must show
these outstanding references beside its completeness status.

A narrative translator records the actor, predicate, object, quantifier,
modality, applicable entities/dates and qualifications before proposing any
constraint. ``All notes are fixed-rate'' constrains contractual coupon type;
it does not constrain the combined note-and-swap exposure. ``May repurchase''
creates an authorised action with limits, not an obligatory payment.
``Substantially all'' remains qualitative unless a separately reviewed
assumption gives it a threshold. A conditional guarantee becomes an obligation
with a trigger and exposure, not a present liability merely because its maximum
amount is known. Unsupported predicates retain their literal text and links
to affected balances. The reviewer accepts the translation separately from
accepting that the text was extracted correctly.

\section{Mappings must establish a financial relationship}

A mapping record identifies source concepts, target concept, relationship,
applicable entity/basis/period/dimensions, evidence, reviewer and any required
transformation. Equivalence permits substitution only when all these contexts
match. A component relationship permits inclusion in a sum only through a
declared disjoint partition. A broader concept supplies containment, not an
equality. Reclassification changes presentation while preserving the stated
population and total; measurement transformation must supply an actual formula
and inputs. These relationships cannot compose indiscriminately: component
followed by equivalence remains component, while two measurement transforms
compose only if their intermediate bases and information dates agree.

For example, Northstar's product revenue might split into 180 domestic and
80 overseas, while its customer channel split is 200 wholesale and 60 retail.
Both classify the same 260. Adding all four numbers gives 520 and is invalid.
The partition records therefore share a population ID but have different axes.
To remove an axis, \code{sumOver} requires evidence that members are disjoint
and exhaustive for that context. Where the source supplies only named
segments, an explicit unallocated member carries the residual; it is not
assumed zero. Geography-by-product cells cannot be recovered from the two
marginals without further constraints or assumptions.

Apple supplies another counterexample: its vendor non-trade receivables arise
from component sales to manufacturing vendors, whose gains reduce product
cost of sales when the final products are sold (annual Note 4, p.~38).
They cannot be relabelled as ordinary revenue-generating trade receivables
without changing meaning. Likewise gross derivative assets and liabilities
cannot be silently netted. Company extensions can define these distinctions
and dated presentation changes; they cannot override mandatory recognition
rules in a selected standards package.

\section{Selecting original and revised assertions}
\enlargethispage{2\baselineskip}

The query procedure first filters assertions by the declared availability
cutoff, then by an optional database-time cutoff. A day-only filing timestamp
is conservatively available at the next local midnight in its named timezone;
any more precise rule needs evidence. Within the eligible set, explicit
supersession removes only the targeted assertions in matching contexts.
The superseding assertion must itself be eligible. Follow the acyclic graph
transitively; retain all maximal assertions if two eligible corrections
conflict. File order and ingestion recency never decide which is true.

The original view selects the initial assertion chain in a named filing;
the latest-available view selects eligible maximal versions; the harmonised
view adds reviewed transformations to those selections. A revision to revenue
does not automatically revise every note or change the company's accounting
basis. An estimate change takes effect in future measurements from its
specified date. An error correction may change a comparative and an opening
balance bridge, each as a new assertion with its own lineage. Northstar's
explicit query fixture in Chapter~\ref{ch:case} checks all these clocks without
assuming that the most recently stored row is always the appropriate history.

\input{sections/source-admission}


## FILE docs/design/proposal/manuscript/sections/source-admission.tex

\section{What an accepted reading permits}
\label{sec:source-admission}

Apple's inventory policy illustrates the distance between reading a sentence
and reconstructing a business. Its reported use of FIFO supports a proposed
cost-formula reading for the inventory and reporting contexts covered by that
policy. It does not reveal the quantities and ages of the actual lots, establish
that no write-down occurred, or supply the authority for every US accounting
treatment. Those are separate inputs to a cost and impairment calculation.
Similarly, a straight-line depreciation policy leaves useful lives, residual
values, components and available-for-use dates to be established.

The source preparation retains six located Apple policy passages: consolidation
of Apple and wholly owned subsidiaries; comparative reclassification; FIFO;
straight-line depreciation; the interim statement's estimates and annual-report
reference; and its 52/53-week fiscal calendar. Each proposed reading carries
the original document hash, extraction hash and exact character slice. These
are company assertions. The consolidation sentence, for example, cannot exclude
every partly owned entity without a control analysis. The calendar sentence
does not make every future fiscal year 52 weeks or make a contractual interest
year 365 days. The exact quotations and proposed predicates are retained in
\path{../methods/source-translations-v1.json}; the meaning explained here is
not an invented human acceptance of them.

A reading progresses through separate decisions. First, extraction review asks
whether the located words and numbers were transcribed faithfully. Translation
review asks whether the proposed predicate preserves their scope, quantifier,
exceptions and reporting context. A model then admits that predicate, or an
explicitly labelled assumption, for a particular purpose and information view.
Accounting eligibility subsequently asks whether a method applies to the actual
event. A faithful transcription of an erroneous company assertion is still
faithful transcription. The four decisions therefore cannot share a single
``approved'' flag.

An explicit presumption in a standard also differs from filling an unknown with
a convenient answer. Article 6 of the retained official ASBE~21 text requires
both practical ability throughout use and economic benefit for a substantive
substitution right. It specifies a presumption when that right is difficult to
determine. Applying that conditional rule requires its stated circumstances;
it does not transform missing lessor information into a reported fact. Nor may
a translator assign arbitrary numerical thresholds to ``substantive'',
``probable'' or ``highly probable''.

\section{Three meanings of disclosure coverage}

The Apple annual/interim preparation inventories 125 quantities, 13 annual notes,
10 interim notes, 70 exhibit references and seven further package obligations.
All 23 notes retain unresolved semantic content; none is recorded as fully
formalised. Downloading their pages answers a useful but narrower question
than constructing a complete company model.

Three populations make that distinction inspectable. Retained-unit coverage
partitions acquired documents into nonoverlapping pages or smaller leaf units,
including duplicates and unreadable material. Assertion-review coverage counts
the separately enumerated material assertions and their review decisions.
Query-exposure coverage identifies the sources, legal facts, methods and
authority that a particular result requires. A fully downloaded annual report
can have incomplete assertion review, and a reviewed debt total can leave a
refinancing query unresolved because an incorporated agreement is missing.
No weighted average of these populations establishes completeness.

Preparation begins with declared annual and interim roots and a policy for
following incorporated references. Each edge is recorded as satisfied,
duplicate or cyclic, outside the declared scope with a reason, inaccessible,
or still unexpanded. A bounded traversal saves its unexplored frontier and
budget so it can resume. An unknown external extent remains unknown. Acquired
proxy and registration documents improve the Apple record, but do not prove
that every executed amendment, issuance term and exhibit dependency has been
closed. The present real package remains incomplete for that reason.

\section{Displayed precision does not determine a rounding rule}

Suppose a statement displays 100 in millions. The scale establishes how the
literal is read; it does not establish how the issuer rounded its underlying
amount. Under an explicitly admitted nearest-rounding assumption, an integer
display $m$ at scale $s$ permits the conservative compatibility enclosure
\[
       s(m-\tfrac12)\leq y\leq s(m+\tfrac12).
\]
The closed endpoints accommodate an unknown tie rule within that nearest-rounding
model. A specified tie rule can exclude an endpoint. Truncation of a positive
amount instead permits $sm\leq y<s(m+1)$. Thus the illustrative display 100
corresponds to 99.5--100.5 million under the first assumption and 100--101 million,
excluding 101, under the second. These are different restrictions on a history.

The retained Apple arithmetic uses the first enclosure as a conditional
compatibility assumption; the issuer's rounding convention has not been
established. Without that assumption or source support, the record states
known display precision and unknown rounding convention and supplies no hard
half-unit constraint. A one-unit difference between a displayed total and the
sum of displayed components is consequently not enough to establish a
contradiction. The source value is scaled once, while its literal and precision
metadata remain available for inspection.

\section{Public availability and system possession are different views}
\label{sec:time-admission}

Northstar's correction explains why a result needs a reporting vintage. A
historical forecast also needs to establish when the exact document bytes were
available. A report downloaded today may carry an old date on its current web
page; that does not prove that the same bytes were public on that date. Public
availability evidence and an ingestion receipt answer different questions.

An investor-information query supplies a cutoff $K$. Each admitted source must
have supported public availability no later than $K$ and evidence linking the
selected bytes to that availability. Later ingestion is allowed. Later
extraction review can read eligible old bytes, but an interpretation that uses
later information fails the cutoff on its own dependencies. This view establishes
public availability, not actual investor awareness or the ability to trade.

A system-as-of query instead supplies an instant $S$ and requires an immutable
receipt showing possession of those bytes by $S$. Publication cannot replace
that receipt. An accepted-layer query also requires review decisions visible
by $S$; a raw-layer query may return a then-unreviewed document. A query asking
both what was public and what the system possessed must pass both filters.
Unknown publication alone need not block a pure possession question.

Archival exploration permits inspection of retained sources with incomplete
timing. With a cutoff, unknown publication yields an unresolved candidate,
not a cutoff-qualified selection. Without a cutoff, the archive may display
the retained lineage, explicitly without a historical-knowledge claim. A known
later version is excluded from an earlier view and cannot suppress an eligible
old assertion. An unresolved potentially relevant version keeps the affected
answer unresolved even when an older assertion is displayed.

Date-only evidence requires particular care. For publication date $D$ in a
named timezone, let $[a_D,b_D)$ be the interval from local midnight to the next
local midnight. A cutoff before $a_D$ excludes the source; a cutoff inside the
interval leaves availability unresolved; a cutoff at or after $b_D$ supports
admission on this date evidence. No arbitrary noon or fixed 24-hour duration
is inserted. Missing timezone leaves the instant comparison unresolved.

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[x=1cm,y=1cm,>=Stealth]
\draw[->] (0,0)--(12,0);
\draw[line width=2pt] (3,0)--(8,0);
\draw (3,-.15)--(3,.15) (8,-.15)--(8,.15);
\node[below,align=center] at (3,-.2) {local midnight\\$a_D$};
\node[below,align=center] at (8,-.2) {next midnight\\$b_D$};
\node[above] at (1.3,.1) {excluded};
\node[above] at (5.5,.1) {time unresolved};
\node[above] at (10.1,.1) {date supports admission};
\end{tikzpicture}
\caption{A dated publication supports historical admission only after its
possible publication interval has ended. The line marks uncertainty about an
instant, not a delay imposed on an already known timestamp.}
\end{figure}

Revision selection follows admission. Original selection returns eligible
roots; latest-available selection returns eligible assertions without an
eligible superseding descendant for the same context. Unrelated roots and
multiple live leaves remain competing assertions. A harmonised view adds
explicit transformations with their own admitted sources, method and opening
bridges. File order never selects a winner.

The synthetic interim example has original first-half revenue 120, revised
first-half revenue 110 and revised annual revenue 260. Compatible subtraction
gives second-half revenue $260-110=150$. The arithmetic $260-120=140$ is easy
but mixes incompatible vintages. An original-view display may show both source
amounts while refusing that derived flow. A change in calendar or perimeter
likewise requires a specific bridge.

The investigated real sources have not yet supplied a qualifying unresolved
same-context contradiction. Known revisions, different reporting bases and
synthetic conflicts remain useful cases of their own kinds. A genuine conflict
case must first match entity, perimeter, concept, dimensions, unit, basis,
period, versions and precision, and investigate extraction and supersession.
The absence of a qualifying example in a bounded search is not evidence that
the corpus contains no conflicts.


## FILE docs/design/proposal/manuscript/chapters/05-mathematics.tex

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
unit $q_i$, an illustrative admissible interval is
$[v_i-q_i/2,v_i+q_i/2)$ under the corresponding tie convention. The actual
rounding convention, scale and XBRL accuracy metadata govern the imported
constraint. A disclosure with unspecified precision does not acquire a
convenient tolerance silently. Write $\mathcal{I}_i$ for the justified
observation interval, and $C_M(h)$ for the joint accounting, contractual and
semantic constraints. Then the historical compatibility set is
\begin{equation}\label{eq:histset}
 \Hist_M(D_k)=\{h\in\mathcal{H}_M:
 C_M(h)\ \land\ O_i(h)\in\mathcal{I}_i\text{ for every applicable }i\}.
\end{equation}
Qualitative assertions enter as reviewed logical conditions, rather than
numeric intervals. Incompatible source contexts are never forced into the
same equation.

Equation~\eqref{eq:histset} distinguishes three outcomes. An empty set means
that the observations and declared model are inconsistent. A singleton means
that this model identifies a history at its chosen resolution. A larger set
preserves unresolved alternatives. An empty set does not prove that the
company's accounts are false: a wrong extraction, missing event type or
incorrect perimeter can cause the inconsistency. A singleton does not prove
that the model contains the real history.

\section{Why published statements cannot identify all transactions}

The simplest derivation uses fixed account mappings and a fixed basis. Let
$z\in\mathbb{R}^n$ contain unknown historical movement amounts. For $m$
disclosed aggregates, let $A\in\mathbb{R}^{m\times n}$ be the aggregation
matrix and $y=Az\in\mathbb{R}^m$. If there is a nonzero vector $v$ with
$Av=0$, then
\[
 A(z+v)=Az+Av=y.
\]
Both movement vectors give the same reports whenever both satisfy the remaining
constraints. Thus the feasible family is the affine set $z+\ker A$ intersected
with those constraints. Accounting requirements can shrink this family, but
do not generally eliminate it. For example, cash collections in a receivables
bridge are constrained by
\[
 AR_T=AR_0+\text{credit sales}-\text{collections}
       -\text{write-offs}+\text{other classified movements}.
\]
If the note does not distinguish acquisitions, currency effects and write-offs,
several collections paths may fit the same closing balance.

There is a second ambiguity beyond aggregation. In
Equation~\eqref{eq:running}, identical historical movements arise from different
contractual reset terms. Even recovering $z$ exactly would leave these terms
unidentified. AccDSL therefore infers economically relevant states and
contract terms alongside journal movements. A linear inverse solver over
statement lines alone cannot solve this second problem.

\section{The accounting state and its invariants}

For one entity book with $n_a$ accounts in one functional currency, let
$b_t\in\mathbb{Q}^{n_a}$ be
signed account balances, with debit amounts positive and credit amounts
negative. Exact decimal amounts can be represented as rationals with a power
of ten denominator. A journal batch $j_t$ contains the signed functional-currency
amounts posted by one atomic event or explicitly grouped event batch. Its
balance condition is
\begin{equation}\label{eq:posting}
 \boldsymbol{1}^{\mathsf T}j_t=0,\qquad b_t=b_{t^-}+j_t.
\end{equation}
If $\boldsymbol{1}^{\mathsf T}b_0=0$, substitution gives
$\boldsymbol{1}^{\mathsf T}b_t=
\boldsymbol{1}^{\mathsf T}b_{t^-}+\boldsymbol{1}^{\mathsf T}j_t=0$.
Induction establishes conservation through every committed batch. Opening
balances must therefore be supplied as a balanced, explained entry or a
balanced imported state with unresolved composition explicitly identified.

This proof establishes a bookkeeping invariant. It does not establish that an
amount belongs in the chosen account, that a contract exists, or that an
accounting standard permits a treatment. Posting validation additionally
checks account roles, ownership, currency conversions, applicability of rules
and event preconditions.

The balance vector includes temporary revenue and expense accounts during
the period. Period closing transfers their net balance to equity through
balanced entries. A reporting function can include current profit in equity
before closing, or use the closed book afterwards, but must not include it
twice. Income and cash-flow reports use classified movements and exclude
mechanical closing transfers from operating flows. Consequently statements
are functions of balances, journals, contract state and reporting rules:
\begin{equation}\label{eq:report}
 Y_{[u,v)}=R(b_{v^-},J_{[u,v)},X_{v^-},\rho,[u,v)).
\end{equation}
Here $\rho$ specifies the reporting basis and perimeter, and $X$ contains
economic state beyond ledger balances. Cash-flow classification is part of
$R$, not recoverable from the closing cash balance alone.

Each book has its own functional currency. Quantities such as shares, tonnes
and foreign-currency units are typed separately and never added to this
balance equation. A foreign-currency posting stores its original units and
the functional-currency valuation with its rate source. Translation into a
group's presentation currency and consolidation adjustments occur in a
separate book under explicit rules.

\section{Simulate events from economic state}

For a chosen history $h$, the state at $T$ is $X_T(h)$. It contains balances,
open contracts, lots or cohorts, unpaid accruals, commitments and other
quantities needed for future evolution. Let $s$ identify a scenario definition,
$U_t^s$ its supplied economic drivers, $a_t$ management's actions, and
$\varepsilon_t$ future innovations. A behavioural policy $\pi$ chooses
$a_t$ using the permitted information $\mathcal{F}_t$:
\begin{align}
 a_t&=\pi(X_t,U_{\leq t}^s,\mathcal{F}_t;\theta),\label{eq:actions}\\
 e_{t+1}&=\mathcal G(X_t,a_t,U_{t:t+1}^s,\varepsilon_{t+1};\theta),\label{eq:events}\\
 (j_{t+1},m_{t+1})&=\mathcal A(e_{t+1},X_t,r_{t+1}),\label{eq:account}\\
 X_{t+1}&=\mathcal T(X_t,e_{t+1},j_{t+1},m_{t+1}).\label{eq:transition}
\end{align}
The generator $\mathcal G$ emits events, such as a sale, rate reset, payment or default.
The accounting function $\mathcal A$ applies rule package $r$ and returns journal
postings plus measurement annotations $m$. The transition $\mathcal T$ updates economic
and ledger state atomically. A default can therefore change the loan's legal
status, expected recoveries, recognised allowance and cash collections through
related, but distinct, records.

This ordering is a reference abstraction. Within a date, event dependencies
and phases specify the actual order. Expectations used to measure an allowance
or provision must be calculated from the information permitted at that date.
They cannot use the realised future path of the simulation. An inner
expectation model may use quadrature, analytic formulas or nested simulation;
its approximation and seed belong in the measurement annotation.

Some scenarios specify a deterministic macroeconomic path while leaving
idiosyncratic defaults random. Others supply a joint stochastic driver model.
A risk-neutral measure used to value a derivative is distinct from the
real-world measure used to simulate business outcomes. Every stochastic
adapter declares its measure and conditioning information. The accounting
function receives the resulting valuation with that declaration.

\section{Preserve sets and distributions separately}

Let $K_{h,s}$ be the probability law of future reports produced by the forward
model conditional on history $h$, scenario $s$ and its declared behavioural
assumptions. A deterministic simulation is the special case of a point mass.
When no probabilities over historical explanations are justified, the natural
answer is a family of laws,
\begin{equation}\label{eq:family}
 \mathcal{K}_{M,s}(D_k)=\{K_{h,s}:h\in\Hist_M(D_k)\}.
\end{equation}
The system can report each explanation, bounds on a deterministic outcome,
or lower and upper event probabilities across this family. Those are different
result types. A range of conditional means is not a confidence interval, and
an envelope of conditional quantiles is not itself a single predictive
distribution.

If a defensible probability measure $\mu(dh\mid D_k,M)$ supported on
$\Hist_M(D_k)$ is supplied, histories and report outcomes must have specified
measurable spaces. Assume that $K_{h,s}$ is a probability kernel: it is a
probability measure on report outcomes for each $h$, and $h\mapsto K_{h,s}(B)$
is measurable for each measurable event $B$. The predictive law is then
\begin{equation}\label{eq:mixture}
 \Prob(Y^s\in B\mid D_k,M)=
 \int K_{h,s}(B)\,\mu(dh\mid D_k,M).
\end{equation}
For discrete explanations this is the usual weighted sum. For continuous
unknowns, integration uses the declared measure over those unknowns, not a
count of solver solutions. Bayesian weights require a prior and a likelihood;
expert weights remain labelled as elicited. A likelihood must not treat a
statement total and all its components as independent repeated evidence.
Deterministic equality constraints require a reduced parameterisation or
proper conditional-measure treatment, rather than an undocumented Gaussian
penalty with near-zero variance.

Suppose the fixed-loan explanation receives weight $w$ and the floating-loan
explanation receives $1-w$, solely as an illustration. Under the rate shock,
\[
 \Prob(I=5)=w,\qquad\Prob(I=7)=1-w,
 \qquad\E[I]=7-2w.
\]
The expected expense is useful but hides the two different outcomes. For a
general scalar output with finite second moment, put $m(h)=\E[Y\mid h]$.
Write $Y-\E[Y]=(Y-m(h))+(m(h)-\E[Y])$. The cross term vanishes because
$\E[Y-m(h)\mid h]=0$. Taking expectations of the squared expression gives
\begin{equation}\label{eq:variance}
 \operatorname{Var}(Y)=
 \E_h[\operatorname{Var}(Y\mid h)]+
 \operatorname{Var}_h(\E[Y\mid h]).
\end{equation}
The first term is uncertainty within a chosen explanation; the second captures
differences between explanations. This decomposition requires the measure
$\mu$. Without it, the system reports the family in
Equation~\eqref{eq:family}, rather than manufacturing a variance.

Weights themselves can be uncertain. For an admissible class $\mathcal{W}$
of measures, AccDSL can compute
\[
 \underline p(B)=\inf_{\mu\in\mathcal{W}}\int K_{h,s}(B)\,d\mu(h),
 \qquad
 \overline p(B)=\sup_{\mu\in\mathcal{W}}\int K_{h,s}(B)\,d\mu(h).
\]
If every measure supported on the feasible histories is allowed and point
masses are included, these bounds reduce to the infimum and supremum of
$K_{h,s}(B)$ over histories: averages cannot lie outside the range of their
integrands, and point masses attain, or approximate, the extremes. Narrower
weight restrictions require an explicit justification and a separate
optimisation problem.

\section{Resolution and computational limits}

For a requested horizon $H$ and scenario family $\mathcal{S}$, histories may be
grouped only when they have the same conditional law for all requested
outputs:
\[
 h_1\sim_{H,\mathcal{S}}h_2
 \quad\Longleftrightarrow\quad
 K_{h_1,s}=K_{h_2,s}\text{ on those outputs for every }s\in\mathcal{S}.
\]
This definition explains why individual sales can sometimes be replaced by
cohorts, while fixed and floating loans usually cannot be merged for an
interest-rate stress. Exact equivalence can be difficult to prove. A grouping
justified only by approximate numerical agreement carries an error criterion
and is not labelled exact. Source provenance remains available even when
execution shares a common state.

Bounds require comparable honesty. A linear program can provide certified
extrema for a supported linear model. A set of feasible sampled histories
provides observed extrema: its minimum is no smaller than the true infimum,
and its maximum is no larger than the true supremum. It therefore supplies
an inner exploration of possibilities, not a certified outer bound. Interval
methods may provide outer bounds that no single history attains. Every result
records which of these meanings applies.

The initial implementation offers exact bounded choices and linear constraints,
symbolic continuous families such as $\alpha\in[0,1]$, and explicit scenario
execution at selected feasible states. General nonlinear partial identification,
automatic model discovery and exhaustive enumeration of all economic histories
are research extensions, not promises made by the core language.

\section{A solver formulation for ordinary rounded disclosures}

The debt example used an exact principal. Real disclosures often do not.
Suppose debt is shown as 100 and interest as 5, each rounded to the nearest
unit with the declared half-open intervals $D\in[99.5,100.5)$ and
$I_0\in[4.5,5.5)$. Using an unknown fraction $\alpha$ and unknown total $D$
would introduce the product $\alpha D$. That expression is bilinear and is
outside the promised linear fragment.

Instead use principal amounts $F$ and $V$. The compatible family satisfies
\begin{equation}\label{eq:rounded-debt}
 F,V\geq0,\quad 99.5\leq F+V<100.5,\quad
 4.5\leq0.05(F+V)<5.5.
\end{equation}
Future interest is $I_1=0.05F+0.07V$. Its infimum is
$0.05\times99.5=4.975$, attained with $F=99.5,V=0$. Its supremum is
$0.07\times100.5=7.035$, approached as $F=0$ and $V$ tends to 100.5
from below, but not attained. A closed interval is a valid enclosure, but
its upper endpoint must not be reported as attainable. The exact solver check separately
tests that no better value exists and whether each endpoint is attainable.

For $D>0$, the amount representation is equivalent to the fraction
representation through $D=F+V$ and $\alpha=F/D$. At zero principal the fraction
is undefined and must be omitted or treated as irrelevant, not recovered.
A known fraction restriction $\alpha\geq a$ becomes $F\geq aD$ when
$D>0$ and $a$ is fixed. If both $a$ and $D$ are unknown, that product remains
nonlinear. Reformulation has a domain of validity; it is not permission to
send arbitrary formulas to a linear solver.

The supported exact fragment contains rational linear equalities, weak and
strict inequalities, and finite Boolean or enumeration choices. Guard
partitions become finite disjunctions. Posting in integer cents introduces a
different integer problem if performed before bounding. Consequently the
request specifies whether bounds apply before quantisation, after a monotone
declared rounding map, or to a bounded integer model. Approximate numerical
valuations carry error metadata outside the exact rational kernel. Solver
timeout, unsupported theory and unbounded objective have distinct responses;
none is relabelled as infeasibility.

\section{Building the family with explicit templates}

The reconstruction input is a model-scope record, not an invitation to invent
unlimited journals. It lists event templates, slots per entity and period,
allowed contract classes, source mappings, opening-state domains, calendars,
resolution and excluded operations. A template gives an incidence vector for
postings and a transition for economic state. Northstar's annual bridges
arise by substituting its collection, purchase and payment templates into
opening-plus-movement identities.

For each allowed slot, create an activity flag and nonnegative amount; an
inactive slot has zero amount. Instantiate the template's posting and state
constraints, unify variables referring to the same observation or economic
contract, and match report expressions to source domains through validated
context mappings. Add cross-note restrictions and choice-group dependencies
to this same formula. No separate account-by-account reconstruction is allowed.
Mark every constraint with its evidence, rule or assumption origin.

Enumerate the finite structural choices in a deterministic order. For each
cell, ask for feasibility and retain the continuous formula, rather than
enumerating real-valued solutions. An infeasible cell preserves a sufficient
conflicting subset; an undecided cell preserves its formula and reason. Search
is complete within the declared scope only when every finite cell has been
decided, every applicable observation has been matched or explicitly qualified,
and no resource truncation remains. A witness establishes existence in one
cell. It does not establish complete search, and complete search does not
establish that the scope includes the company's real history.

In Northstar the declared templates identify annual collections, purchases
and supplier payments, but retain every $F\in[0,100]$. Adding a verified note
that $F=60$ narrows this family by conjunction. Adding a proposed ``all floating''
reading to that revised view produces a rejected cell with the conflicting
note attached. Adding a rule that expenses a capital contribution would instead
fail treatment admission: inconsistent evidence and unsupported accounting
have different diagnoses.

\section{Which details may safely be combined}

A resolution record names the outputs, horizon, scenario family, grouping key,
required state, transformation and exact or approximate status. Safe exact
transformations are deliberately few. Cash balances in the same book and
currency can be added. Homogeneous inventory lots may be combined under a
weighted-average policy if ownership, cost basis, impairment state and future
costing treatment coincide. Debt principal can be added only within a group
sharing currency, coupon/reset function, fixing and payment calendars,
maturity, options, guarantees and measurement method. The transition and
reporting maps must be additive on that group.

The last condition supplies a short proof obligation. If a transition obeys
$T(x_1+x_2,u)=T(x_1,u)+T(x_2,u)$ and reporting is additive for every admitted
driver $u$, induction preserves equality after grouping. This does not apply
to covenant thresholds, counterparty netting, nonlinear guarantees or
lot-specific impairment. Two fixed loans with the same dates and rate can
share an execution state under this test. The fixed/floating pair cannot;
neither can two policies with different guarantees merely because their
current reserves match.

A changed horizon, scenario, rule version or requested output invalidates the
resolution approval and reruns the sufficiency check. Extending beyond a debt
maturity requires schedule detail that an earlier short-horizon view could
omit. Approximate cohorts retain the detailed source references and a stated
error criterion tied to outputs. Unless that error is bounded or evaluated,
the grouping remains an approximation awaiting evidence, not an exact quotient
of the history family.

\section{A finite probability model that can actually be evaluated}

Optional probability weighting begins with disjoint economic hypotheses and
a declared joint measure. As an illustration, assign fixed and floating
hypotheses prior probabilities 0.6 and 0.4. The stress itself leaves these
weights unchanged and gives mean interest $0.6(5)+0.4(7)=5.8$.
Suppose genuinely new observed evidence has likelihood 0.2 under fixed and
0.8 under floating. The unnormalised posterior masses are 0.12 and 0.32;
normalisation by 0.44 gives $3/11$ and $8/11$. These likelihoods are
illustrative inputs, not extraction-confidence scores.

The finite reference algorithm enumerates joint hypothesis and innovation
states, evaluates their declared joint mass and any observation likelihood
once, checks the nonzero normalising constant, and propagates the entire
statement vector on each state. It sums masses only across disjoint events.
Two overlapping labels such as ``fixed share at least one half'' and ``all
fixed'' are query views and cannot become two independent mixture components.
Totals and their components share an observation block so their evidence is
not counted twice. Continuous inference needs an additional parameterisation,
density or conditional measure and an assessed numerical method; the finite
algorithm supplies no guarantee for those extensions.

If the floating branch has an unsupported valuation operation, its mass 0.4
remains unresolved. The run may report the fixed result with successful mass
0.6, but cannot report 5 as the unconditional mean by renormalising away the
failure. A separately requested mean conditional on successful execution must
show that conditioning event and its mass. For unweighted families, an
unresolved branch blocks a complete envelope over the family. Economic default
is retained as a model outcome with remaining obligations, rather than being
treated as a computational error to remove.

\input{sections/inference-methods}


## FILE docs/design/proposal/manuscript/sections/inference-methods.tex

\section{Numerical precision is part of a financial method}
\label{sec:numerical-methods}

The affine family is useful for Northstar because the scenario fixes prices,
rates and operating coefficients while the debt share remains unknown. Other
contracts require roots or discount factors. Their numerical treatment must
state what is exact, what is enclosed and when a posted amount is determined.
An accounting name on a library call does not make its result exact.

Consider positive payments $C_i$ at positive times $t_i$ and a positive price
$P$. The effective annual rate solves
\[
 f(r)=\sum_i\frac{C_i}{(1+r)^{t_i}}-P=0,\qquad r>-1.
\]
Each term discounts a payment to the valuation date. In this positive-payment
case,
\[
 f'(r)=-\sum_i\frac{t_i C_i}{(1+r)^{t_i+1}}<0.
\]
Consequently a certified sign-changing bracket contains exactly one root.
The method uses stated bracket bounds and an expansion cap, evaluates signs
with outward error bounds, and bisects until the requested rate or value
enclosure is reached. An uncertified sign, unavailable bracket or exhausted
accuracy budget yields an unresolved numerical result. Mixed-sign cash flows
can have several internal rates of return; the preceding monotonicity argument
does not apply and cannot justify returning the first Newton iterate that
converges.

Net proceeds 100 and a payment 121 in two years give exactly 10\%. An immediate
fee of 2 changes proceeds to 98 and changes that root. Annual-effective 21\%
for half a year has the exact accumulation factor $\sqrt{1.21}=1.1$, so interest
on 100 is 10. Simple proration would give 10.5 and computes a different contract.
At annual-effective 10\%, the half-year factor $\sqrt{1.1}$ is irrational. For
rational time $p/q$ and positive $1+r$, exact rational power comparisons can
enclose the positive $q$th root of $(1+r)^p$. A negative $p$ first requires the
reciprocal. General exponential discounting needs a separately specified
error-controlled method.

A posting quantum of 0.01 does not eliminate this uncertainty. The whole
certified monetary enclosure must lie in one rounding cell under the admitted
tie rule. An enclosure from 1.0049 to 1.0051 crosses a half-cent boundary and
does not establish one posted amount. Refine within a declared budget or retain
rounding unresolved. This rule separates evidence for a numerical answer from
the accounting authority to use that answer.

\section{Updating a law without counting evidence twice}
\label{sec:inference}

Two financial histories can be compatible with the same reports without being
equally probable. Once an explicitly justified law is supplied, genuinely new
evidence may change it. For finite histories $h$, prior mass $p(h)$ and an
admitted observation likelihood $L(D\mid h)$, Bayes' rule gives
\[
 p(h\mid D)=\frac{p(h)L(D\mid h)}{\sum_g p(g)L(D\mid g)}.
\]
The denominator is the probability of that evidence under the declared model.
If it is zero, the condition is impossible in that model; dropping incompatible
histories and renormalising an empty collection cannot repair it.

For two histories with assumed prior masses $1/3$ and $2/3$ and likelihoods
$3/4$ and $1$, the unnormalised masses are $1/4$ and $2/3$. Their sum is $11/12$,
so the posterior masses are $3/11$ and $8/11$. If the second history's cash
calculation fails, the first still has mass $3/11$ and unresolved cash retains
mass $8/11$. A report giving the successful history probability one would
answer a different, success-conditioned question.

An observation has a semantic information identity as well as a file locator.
Reimporting the same observation through another file does not create a second
measurement. Repeating an identical admitted condition is idempotent: it keeps
the law and information lineage unchanged. Submitting an already consumed
observation as a fresh likelihood block is rejected as duplicate information.
Equal selected member sets alone do not prove that two conditions have the same
meaning. An admitted conditional kernel may divide a region's existing mass
when it is refined; the number of new representatives never determines that
division.

Continuous inference adds a measure choice. One must specify coordinates $z$,
domain, base measure, prior, observation mechanism and any transformation
Jacobian. \citet[Section 2.2, equations (2.5)--(2.8)]{stuart2010} supplies the
inverse-problem formulation, but does not establish identification or easy
sampling for a mixed accounting model. In particular, an exact accounting
equality can confine a model to a lower-dimensional set. Multiplying an ordinary
Lebesgue density by its zero-volume indicator is not a posterior construction.
One must parameterise the constrained model with its declared measure or supply
an actual measurement-error model. Adding convenient small noise changes the
target.

\section{A continuous example whose posterior can be checked}

A linear Gaussian model supplies a tractable comparison for later numerical
inference. Let an unknown economic quantity $z$ have prior mean $m_0$ and positive
definite covariance $V_0$. Let the observation be $y=Hz+\epsilon$, where
$\epsilon$ is independent Gaussian noise with positive definite covariance
$R$. The measurement-error assumption is substantive: it describes this example,
not rounding in every financial statement.

Multiplying prior and likelihood adds their quadratic forms. Terms that depend
on $z$ are
\begin{align*}
 &(z-m_0)^\top V_0^{-1}(z-m_0)
 +(y-Hz)^\top R^{-1}(y-Hz)\\
 &\quad=z^\top(V_0^{-1}+H^\top R^{-1}H)z
 -2z^\top(V_0^{-1}m_0+H^\top R^{-1}y)+\text{constant}.
\end{align*}
Completing the square therefore gives posterior covariance $V$ and mean $m$
through
\[
 V^{-1}=V_0^{-1}+H^\top R^{-1}H,\qquad
 V^{-1}m=V_0^{-1}m_0+H^\top R^{-1}y.
\]
The prior and observation contribute precision and precision-weighted
information. An implementation should solve factored linear systems rather
than explicitly form these inverse matrices, and reject an invalid covariance
or unsupported rank condition.

For $m_0=0$, $V_0=4$, $H=1$, $R=1$ and $y=2$, posterior precision is
$1/4+1=5/4$, variance is $4/5$ and mean is $(4/5)2=8/5$. A conditional cash
quantity $100+10z$ has mean 116 and variance 80. A second \emph{independent}
measurement of 2 would give precision $9/4$, variance $4/9$ and mean $16/9$.
Reusing the first measurement would produce those same numbers but would be
wrong for the stated information. The analytic example can distinguish numerical
error from information double counting.

For a bounded non-Gaussian scalar model, quadrature requires a stated domain
or tail truncation and sufficient integrand error bounds to enclose the
normalizer and requested moments. Without a positive lower normalizer bound,
the ratio remains unresolved. Mixed models can enumerate finite choices and
integrate each conditional continuous model, but combining branches requires
their evidence factors, not draw counts. Optional MCMC needs target-specific
parameterisation, tuning, independent chains, tractable correctness comparisons,
convergence and Monte Carlo error checks. This proposal supplies no generally
validated sampler or universal tolerance.

Nor can a more elaborate inference engine identify a quantity that the
observation model never sees. If reports constrain only total debt 100, the
likelihood may be constant in its floating share $x$. Its conditional prior
then remains unchanged. A uniform prior is a chosen assumption, not a discovery
from those reports. The inspected working version of
\citet[Sections 2.1--2.3, equations (2.2)--(2.4)]{giacomini2021} motivates
retaining posterior classes where a conditional prior cannot be revised.
For Northstar there is a simple direct deduction: under all probability
measures on $[0,1]$, the expectation of $5+2x$ lies in $[5,7]$, with endpoints
attained by point masses. This deduction imports no asymptotic theorem from
that paper's structural-vector-autoregression setting.

\section{A stress is not an observed condition or an intervention}

The interest-rate stress in Northstar fixes a future driver path. It supplies
no new evidence about the historical debt share. An observational forecast
instead conditions a joint law on information. A causal intervention needs
structural equations and an exogenous disturbance law, because it replaces
the mechanism determining a chosen variable while leaving other mechanisms
in place \citep[Section 3.2, equations (5)--(9) and (15)--(17)]{pearl2009}.

An elementary example makes the difference numerical. Let $U$ equal zero or
one with probability $1/2$ each, and assume
\[
       X=U,\qquad Y=2X+U.
\]
Observing $X=1$ establishes $U=1$ and hence $Y=3$. Intervening to set $X=1$
replaces the first equation. It leaves the original law of $U$, so $Y$ is 2 or
3 with equal mass and mean 2.5. Selection of a high-investment company and an
imposed investment policy can therefore answer different questions even under
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
