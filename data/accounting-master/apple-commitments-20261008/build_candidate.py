"""Create Version 2.8 once, preserving the closed Version 2.7 sources."""
from pathlib import Path
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-revenue-20261008'
NEW=ROOT/'docs/design/proposal/manuscript-commitments-20261008'
NEW.mkdir(exist_ok=False)
for p in OLD.rglob('*'):
    if p.suffix in {'.tex','.bib','.lark'}:
        q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
p=NEW/'accounting-product-proposal.tex'
p.write_text(p.read_text().replace('Version 2.7','Version 2.8'))
addition=r"""
\section{Apple: commitments and the cash needed to fulfil them}
\label{sec:apple-commitments}

The same distinction between recognition and cash arises when Apple buys
capacity and components. A lease liability measures one part of an existing
obligation; a purchase commitment describes goods or services still to be
acquired. A funding projection needs the payments arising from both, together
with new orders and operating decisions. Adding every disclosed amount would
mix measurements and could count the same requirement twice.

\subsection{From a lease liability to future payments}

At 28 September 2024, Apple's lease note reports the following amounts in
millions of dollars \citep[Note 8, printed p.~42]{apple2024}. The maturity table
first totals undiscounted payments and then deducts imputed interest to reach
the recognised liability. The right-of-use assets are reported separately.

\begin{center}
\begin{tabularx}{\linewidth}{@{}Xrrr@{}}
\toprule
Amount (USD million) & Operating & Finance & Total\\\midrule
Undiscounted lease payments & 13,518 & 1,272 & 14,790\\
Less: imputed interest & 1,984 & 376 & 2,360\\
Recognised lease liabilities & 11,534 & 896 & 12,430\\
Right-of-use assets & 10,234 & 1,069 & 11,303\\\bottomrule
\end{tabularx}
\end{center}

Thus $14{,}790-2{,}360=12{,}430$ reconciles the maturity and liability
measurements. The recognised liability is already included in the balance
sheet; it is not an extra cash requirement to add to 14,790. Its current
components total $1{,}488+144=1{,}632$ million, whereas the fiscal-2025 maturity
bucket is 1,991 million. A current carrying amount and a gross payment bucket
answer different questions. The right-of-use asset likewise need not equal the
remaining liability; these reported balances do not disclose the complete
amortisation, prepayment and modification history.

Apple also reports 849 million of fixed payments under additional leases that
had not commenced. It expects them to commence in 2025--2026, with terms from
less than one year to twenty-one years. Adding this separately disclosed amount
to the maturity total gives $14{,}790+849=15{,}639$ million. That sum is
consistent, under a nearest-0.1-billion rounding assumption, with the 15.6
billion of fixed lease obligations in management's cash-requirements discussion
\citep[printed pp.~25 and 42]{apple2024}. Numerical compatibility does not
establish a contract-by-contract reconciliation. It neither adds 849 to the
recognised liability nor identifies its commencement and payment dates.

The remaining lease information cannot supply those dates mechanically. The
note describes original terms typically no longer than ten years, with renewal
options, some reasonably certain to be exercised. Its weighted-average
remaining term of 10.3 years describes a different quantity. The reported
3.1\% discount rate, generally based on estimated incremental borrowing rates,
does not supply every contract's rate or the timing hidden in ``thereafter''.
Applying that one rate to invented year-end payments would introduce new
assumptions. The policy combining lease and nonlease components also has a
stated scope: corporate, data-centre and retail facilities
\citep[Notes 1 and 8, printed pp.~34 and 42]{apple2024}.

Fixed and variable costs add another distinction. For 2024, Apple reports
2.0 billion of fixed operating-lease cost, 1.9 billion of fixed operating-lease
cash payments and 1.0 billion of noncash right-of-use assets obtained for lease
liabilities. Variable costs across its leases were 13.8 billion; payments of
that kind primarily depend on purchases of output from the leased assets
\citep[Note 8, printed p.~42]{apple2024}. Historical expense is therefore not a
fixed future cash schedule. Forecasting it requires output, price and settlement
assumptions. Adding it to manufacturing commitments without identifying their
relationship could double count procurement requirements.

\subsection{Why a fall in commitments does not identify cash spent}

The purchase note and management discussion disclose different views. Note 12
lists 11,226 million of future payments under unconditional purchase obligations
whose remaining terms exceed one year. Its fiscal-2025 row is 3,206 million
\citep[Note 12, printed p.~45]{apple2024}. The term restriction selects
contracts; it does not place every payment beyond the coming year. The note
describes these as off-balance-sheet commitments, primarily involving supplier
arrangements, intellectual property, content and distribution rights.

Management's discussion provides additional near-term evidence. At the same
September date it reports manufacturing purchase obligations of 53.0 billion,
of which 52.9 billion is payable within twelve months. Other purchase
obligations total 12.0 billion, with 4.1 billion within twelve months; that
description includes capital assets as well as supplier, content and rights
arrangements \citep[printed p.~25]{apple2024}. A model confined to Note 12
would miss those reported aggregates. Conversely, subtracting 11.226 from 12.0
and labelling the difference short-term contracts is unsupported: the category
and term populations have not been reconciled, and the precision differs.

At 28 December 2024 manufacturing obligations are 39.8 billion, all payable
within twelve months. The interim report says contractual cash requirements
have not changed materially since the annual filing except for commercial
paper, manufacturing obligations and the State Aid tax payable
\citep[printed p.~16]{apple2025q1}. That qualitative statement is not an exact
December lease measurement or evidence that every lease remained unchanged.
The two manufacturing totals are dated observations over changing orders and
payment horizons. Their 13.2 billion difference does not identify purchases
or cash paid during the quarter.

To see what is missing, consider an explicitly simplified model in billions
of dollars. Let $O_0$ and $O_1$ denote a comparable population of undelivered
fixed-price orders at the two dates. Let $N$ be new orders and $F$ the value
removed when goods are delivered. Assume no cancellation, price or currency
change. Treat the displayed 53.0 and 39.8 as exact inputs for this illustration.
These assumptions define the example; the disclosure does not establish this
roll-forward convention for every reported obligation. The balance relation is
\begin{equation}
 O_1=O_0+N-F,\qquad F-N=53.0-39.8=13.2.
 \label{eq:apple-commitment-movement}
\end{equation}
With no new orders, delivery is 13.2. With 5.0 of new orders, delivery is 18.2.
Both leave the same closing undelivered amount of 39.8. The source balances
alone cannot choose between these conditional movements; actual contract
changes and delivery evidence could do so.

Payment is a further choice. Suppose the first history's 13.2 of delivered
goods all remain unsold inventory, with no opening payables, prepayments or tax.
Paying on delivery debits inventory and credits cash by 13.2: total assets and
profit do not change within this subsystem. Delivery on credit instead debits
inventory and credits trade payables by 13.2: assets and liabilities rise
together, with no immediate cash or profit effect. Settling that payable later
debits the payable and credits cash; consumption, sale or impairment would
require further entries. These examples isolate recognition and settlement.
They are not estimates of Apple's actual purchases or payments, or a fit to
all its financial statements. No probability follows from writing two histories.

Delivery assumptions also need the narrative that surrounds the purchase
table. Apple describes single or limited sources for some components,
industry-wide shortages and price fluctuations, and capacity or yield
constraints for new technologies. Suppliers may favour common components over
custom ones. Its named manufacturing locations describe outsourced production,
not a product-by-revenue-region allocation or ownership map
\citep[Note 12, printed p.~46]{apple2024}. A scenario in which input availability
changes may alter output, variable lease payments, inventory and receipts
together. The passage motivates those dependencies without identifying their
size or probabilities.

The same note, and the interim contingency note, preserve management's dated
assessment of unresolved legal claims. At each date, management states that
there was not at least a reasonable possibility that Apple had incurred a
material loss, or a material loss greater than a recorded accrual
\citep[Note 12, printed p.~46]{apple2024}
\citep[Note 9, printed p.~11]{apple2025q1}. It does not make litigation exposure
zero. Contract terms, supply constraints, commencement, delivery and settlement
must therefore remain in the historical record alongside reported balances.
They determine which future journal paths can be supported when a funding
question is asked.
"""
p=NEW/'chapters/13-reference-company.tex';p.write_text(p.read_text()+addition)
p=NEW/'chapters/02-history.tex';s=p.read_text();a=s.index('Northstar');b=s.index('\\section{',a)
s=s[:a]+r"""Northstar's corrected receivable, Apple's debt measurements and its deferred
revenue show why the source record must retain more than a label and a number.
Section~\ref{sec:apple-revenue} distinguishes a reported balance, a derived
movement, a dated expectation and an unquantified obligation.
Section~\ref{sec:apple-commitments} adds the contract and delivery facts needed
to turn a commitment into a future payment. The procedures below determine
which assertions enter a model and which remain unresolved.

"""+s[b:];p.write_text(s)
print(NEW)
