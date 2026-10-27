"""Create a separate V2.7 source candidate, leaving V2.6 intact."""
from pathlib import Path
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-adoption-20261008'
NEW=ROOT/'docs/design/proposal/manuscript-revenue-20261008'
NEW.mkdir(exist_ok=False)
for p in OLD.rglob('*'):
    if p.suffix in {'.tex','.bib','.lark'}:
        dst=NEW/p.relative_to(OLD);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.6','Version 2.7'))
p=NEW/'chapters/13-reference-company.tex'
addition=r"""
\section{Apple: revenue recognition and cash collection}
\label{sec:apple-revenue}

An iPhone sale can create revenue today and an obligation to provide services
later. Apple's annual revenue note separates delivered hardware and bundled
software from the right to receive product-related services such as iCloud,
Siri and Maps. It allocates the price and related discounts by relative
stand-alone selling prices. For the bundled services those prices are estimates,
because observable separate prices are unavailable. The hardware portion is
recognised when control transfers, generally on shipment; the service portion
is deferred and recognised straight-line over the estimated period of provision
\citep[Note 2, printed p.~35]{apple2024}. A historical model consequently needs
the allocation and service cohort as well as the sale date and amount. Neither
the product label nor the customer payment supplies those missing terms.

The note describes collection shortly after control transfer or the start of
service delivery. It does not specify one collection lag for every contract.
Products revenue also reflects expected returns, price protection and customer
incentives. Revenue excludes taxes collected for remittance to governments
\citep[Notes 1--2, printed pp.~34--35]{apple2024}. Together these qualifications
prevent a simple conversion of reported revenue into gross customer receipts.

Presentation creates a second distinction. Where Apple obtains control of a
third-party product before sale, it reports the gross amount billed. For
third-party applications sold through the App Store, its stated treatment
records only the retained commission in Services revenue. Services also already
includes recognition of the deferred value of services bundled with products
\citep[Note 2, printed p.~35]{apple2024}. Adding that recognition to reported
Services a second time would double count it; treating Services as gross App
Store customer spending would change the measured quantity.

The product and geographic tables describe different divisions of the same
sales. The five product/service rows sum to 391,035 million dollars in fiscal
2024 and 124,300 million in the quarter ended 28 December 2024. The geographic
segment sales sum to those same totals. They must not be added together.
Apple says the product mix is generally similar across segments, except that
iPhone represents a moderately higher share in Greater China. That qualitative
statement does not identify a product-by-region matrix
\citep[Notes 2 and 13, printed pp.~35--36 and 46--47]{apple2024}
\citep[Notes 2 and 10, printed pp.~6 and 11]{apple2025q1}.

\subsection{The movement that the note leaves unidentified}

At 28 September 2024 Apple reports total deferred revenue of 12.8 billion
dollars. At 28 December it reports 13.2 billion, and says that quarter's net
sales include 3.7 billion recognised from the deferred balance at the September
date \citep[Note 2, printed p.~6]{apple2025q1}. The balance sheet's December
current deferred-revenue line is 8,461 million, with 8,249 million at September
\citep[printed p.~3]{apple2025q1}. Those are current liabilities; the note's
larger amounts are totals. The precision differs too: the total is displayed
to tenths of a billion, whereas the current line is displayed in millions.

Let $D_0$ and $D_1$ denote opening and closing total deferred revenue. During
the quarter, let $A$ be additions to deferred revenue, $R_o$ revenue released
from the opening balance, and $R_n$ revenue released from amounts added during
the quarter. Let $M$ collect other signed movements, positive when they increase
the liability. These symbols describe a balance reconciliation; $M$ is not an
assertion that a particular adjustment occurred. In billions of dollars,
\begin{equation}
 D_1=D_0+A-R_o-R_n+M,
 \qquad A-R_n+M=D_1-D_0+R_o\simeq13.2-12.8+3.7=4.1.
 \label{eq:apple-deferred-movement}
\end{equation}
The source identifies $R_o$, not the whole release $R_o+R_n$. The 4.1 billion
residual therefore measures net additions after new-origin releases and other
movements at the displayed amounts. Calling it gross new deferrals, billings
or cash collected would be wrong relative to what has been calculated.

Rounding also matters. If each of the three displayed inputs is rounded to the
nearest 0.1 billion, a closed outer envelope for that residual is
$[3.95,4.25]$ billion: the lower endpoint uses $13.15-12.85+3.65$, and the
upper uses $13.25-12.75+3.75$. This is a conditional precision calculation,
not a verified issuer rounding rule or a bound on gross collections. Its
endpoints leave the treatment of exact rounding ties unspecified.

Two constructed histories make the missing movement visible. For this
illustration alone, use the displayed amounts as exact inputs and set $M=0$.
Keep the reported quarter's total revenue at 124.3 billion. The table supplies
two different choices for $A$ and $R_n$; other recognised revenue is the
remainder needed to match that total.

\begin{center}
\begin{tabularx}{\linewidth}{@{}Xrr@{}}
\toprule
Quarterly amount (USD billion) & History 1 & History 2\\\midrule
New deferrals, $A$ & 4.1 & 5.1\\
Release from those new deferrals, $R_n$ & 0 & 1.0\\
Release from the opening balance, $R_o$ & 3.7 & 3.7\\
Other recognised revenue & 120.6 & 119.6\\
Closing deferred revenue & 13.2 & 13.2\\
Total recognised revenue & 124.3 & 124.3\\\bottomrule
\end{tabularx}
\end{center}

Both histories satisfy the selected note totals, yet their new deferrals differ
by one billion. They are witnesses within this aggregate model, not reconstructed
Apple contracts or a fit to every financial-statement constraint. Additional
contract, cohort, return and movement information can rule out or refine them.
No probability attaches to either merely because two examples were written down.

The corresponding recognition entry debits deferred revenue and credits revenue
when service is provided. Receipt or billing of consideration that creates the
deferral instead credits deferred revenue and debits cash or, where an
unconditional right to payment exists, a receivable. Collection of that
receivable changes cash and receivables without creating revenue a second time.
For example, hold History 1's other revenue cash-settled and omit costs, taxes,
refunds and other movements solely to isolate this subsystem. Receiving its
4.1 billion of new consideration gives revenue-side cash inflow 124.7 billion.
If that new consideration is receivable at quarter end, cash inflow is 120.6
billion and receivables increase 4.1 billion. In both cases the asset increase
is 124.7, matched by a 0.4 increase in deferred revenue and 124.3 of revenue
before omitted expenses. These conditional entries explain the identification
problem; neither inflow is an estimate of Apple's actual cash collections.

\subsection{A dated recognition expectation is not a cash forecast}

At both September and December, Apple expects 64\% of the then-reported total
deferred revenue to be realised in less than a year, 25\% within one to two
years, 9\% within two to three years and 2\% after three years
\citep[Note 2, printed p.~36]{apple2024}
\citep[Note 2, printed p.~6]{apple2025q1}. These are two dated expectations
about two balances. Multiplication at the displayed December values gives
$13.2\times0.64=8.448$ billion in the first bucket. The corresponding September
calculation gives 8.192 billion. Their difference does not measure revenue
recognised during the intervening quarter: the dates, remaining horizons and
contract populations have changed.

The percentages divide an expected amount by recognition horizon. They do not
assign probabilities to alternative histories, fix collection dates or forecast
all future sales. The 8.448 billion calculation also cannot replace the reported
8.461 billion current liability. Rounded amount and percentage disclosures do
not justify an exact equality between those figures, and the query must retain
the source's distinct description of each quantity. A future calculation that
requires monthly service or receipts needs finer timing and payment evidence.

The note leaves another part of future service unquantified. For certain
long-term arrangements, Apple has not yet delivered the service, has no right
to bill for it and attributes the unbilled consideration entirely to that
undelivered service. It reports neither revenue nor an amount for those
obligations in this passage \citep[Note 2, printed p.~35]{apple2024}. A query
must retain an unknown amount; setting it to zero or equating it with recorded
deferred revenue would erase the distinction the company makes.

These disclosures therefore yield several different results. The total and
current deferred balances are reported observations. The 4.1 residual is a
derived net movement with unresolved components. The recognition buckets are
management's dated expectations, and the excluded consideration is unquantified.
Contract-level allocations, service lives, new-origin releases and collection
facts remain necessary for a particular future journal path. The annual and
interim periods also stay separate: the December 2024 quarter follows the
September 2024 fiscal year, so subtracting it from that annual revenue cannot
produce the year's final nine months. The complete revenue-note reading makes
these consequences explicit while the wider Apple disclosure package remains
only partly formalised.
"""
p.write_text(p.read_text()+addition)
p=NEW/'chapters/02-history.tex';t=p.read_text();old="Northstar's corrected receivable and Apple's several debt amounts show why\nthe source record must retain more than a label and a number. The procedures\nbelow determine which assertions enter a model and which remain unresolved."
new="Northstar's corrected receivable, Apple's debt measurements and its deferred\nrevenue show why the source record must retain more than a label and a number.\nSection~\\ref{sec:apple-revenue} distinguishes a reported balance, a derived\nmovement, a dated expectation and an unquantified obligation. The procedures\nbelow determine which assertions enter a model and which remain unresolved."
assert old in t;p.write_text(t.replace(old,new))
print(NEW.relative_to(ROOT))
