# Company state includes relationships as well as quantities

A cash balance tells us how much cash a company reports. It does not identify
the customers whose payments produced it, the invoices those payments settled,
or the legal entity entitled to spend it. Those distinctions matter whenever
the next decision concerns collection, credit exposure, payment authority or
restricted funds. A company model therefore needs more than a vector of
balances, even when that vector is sufficient to reproduce a particular report.

McCarthy's1982 REA model addresses the organization of that richer information.
The inspected article develops resource, event and agent descriptions, with
stock-flow, exchange-duality, control and responsibility relationships
(printed561–564, Figures3–5). Its starting point is the information required
by different activities and decisions. Those local requirements are integrated
into a common description of the enterprise, together with procedures that
produce the required views (556–558). This is a method for designing an
information model. It is not an estimator that recovers an enterprise from a
published balance sheet.

The distinction helps place REA alongside the inverse-accounting example of
Arya and colleagues. That example starts with a specified transaction-incidence
matrix and studies the transaction information retained in account balances.
REA asks how to choose and relate the economic records from which such
accounting views can be formed. AccDSL needs both questions: what the selected
representation can retain, and what incomplete observations can identify
within it. Solving the second question cannot repair a missing counterparty,
contract or relationship in the first.

McCarthy's purchase example makes the construction concrete. Inventory is
linked to a purchase event, which identifies its vendor and internal buyer.
A cash-disbursement event identifies the relevant parties and is linked to
the purchase it pays for (565–566, Figure6). Integrating the two views requires
resolving their vendor descriptions and overlapping attributes. It also
requires deciding how purchasing and treasury personnel fit into the
enterprise's responsibility structure. Matching amounts or similar names
does not perform that integration.

For AccDSL, this motivates an explicit relationship dependency alongside each
numeric read. A collection operation may require a receivable amount, but it
also needs the claim identity, debtor, collecting entity, settlement allocation
and applicable currency. A principal payment similarly requires the debt
instrument and obligor; the total principal reported in a debt note cannot
identify either. The new Apple debt adapter preserves the difference between
principal, carrying amount and maturity classifications. The legal instruments
and allocations remain unresolved because the selected aggregate disclosures
do not supply them. This is a local design consequence of the inspected sources,
not a claim that the1982 paper specifies AccDSL's contracts.

Claims may need their own records. McCarthy explains how differences between
related exchange events can be represented as claims, and then considers when
claims should instead be explicit entities with attributes of their own
(568,571, Figure7). His examples include ageing categories for receivables and
security categories for bonds. Whether a claim is stored directly or derived
from linked events depends on the information that users need. The useful
point for simulation is that the relationship and its history must survive
either representation. A derived receivable still needs the events and
allocations from which it can be reconstructed.

The paper also separates economic descriptions from the procedures that
maintain or report them. It distinguishes immediate updates, periodic
adjustments, immediate views and periodic derivations according to timing and
whether they change underlying records (569–570, Figure8). That distinction
is directly relevant to accounting memory. A report query should not silently
change an economic event, while an authorized adjustment may change accounting
memory without changing a completed cash payment. Dates and procedure effects
must therefore be part of the operation specification, not inferred from the
fact that two outputs happen to have the same value.

This does not make accounting choices disappear. McCarthy explicitly says that
the framework does not resolve the difficult choices created by periodicity,
allocation and valuation (570). His treatment of accruals, event partitioning
and service consumption illustrates how accounting procedures may present a
different partition of activity from the one useful to other enterprise users
(572–574, Figures9–10). A common company model must preserve the underlying
distinctions needed by both. It cannot obtain cross-basis compatibility merely
by renaming accounts or copying a journal template.

The native affine dependency inspection now makes one part of this requirement
executable. For a supplied history, each account or memory value is represented
as a linear combination of opening values and event amounts. Each query retains
those exact dependencies. Separately, the inspection preserves every balance
condition, declared state constraint and measurement constraint at its relevant
event prefix. This separation matters: two terms may cancel in a report while
the underlying transaction still affects an intermediate cash constraint.

That calculation does not yet construct resource/event/agent relationships.
Nor does it establish whether the declared operation population includes every
economically relevant event. The next extension should attach typed endpoints
and relationship roles to the operation's numeric and procedural dependencies:
which claim is paid, which entity controls the resource, which event creates
or discharges the claim, and what evidence supports each link. Missing links
must produce alternative constructions or explicit unresolved obligations.
An implementation must not invent them because a numerical reconciliation
would otherwise be convenient.

Historical detail also deserves a separate decision. McCarthy treats full
event retention as an idealized starting point and discusses deliberate
aggregation and storage tradeoffs (562,572). This is not a mathematical proof
that a particular summary preserves all future queries. AccDSL's reduction
criteria remain responsible for that proof. The two perspectives are
complementary: REA helps identify meaningful records and relationships; the
local preservation argument must establish what a proposed simplification
keeps for specified reports, actions and information sets.

The article's ending is appropriately limited. It distinguishes conceptual
schema design from implementation and physical database design, and calls for
more complex implementations and user validation (575–576). Its treatment of
equity likewise distinguishes a computed residual from the transactions needed
to explain ownership contributions and distributions (575). These observations
support the project's current emphasis on implementable relationships and
operation contracts. They do not establish that the company-state design is
complete, that a database schema is a behavioral simulation, or that later REA
extensions can be omitted from the survey.

Source: William E. McCarthy, The REA Accounting Model: A Generalized Framework
for Accounting Systems in a Shared Data Environment, The Accounting Review57(3),
July1982,554–578, DOI10.2308/tar-4487748. All25 retained scan pages, including
Figures1–10, footnotes and references, were visually inspected on28October2026.
The local file and dated metadata are recorded in
data/accounting-master/company-state-rea-reading-20261028/. No original software
was imported or performance comparison made. Later REA policy/commitment work,
alternative accounting databases and the cited user-evaluation study remain
separate technical-reading tasks.
