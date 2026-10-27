# Optional partial sale of one recovered lot

The selected synthetic book already records each recovered lot's units,
carrying amount, tax base, acquisition date and disposal status. The protected
whole-lot sale consumes all of them. RecoveredLotSale/1 is a separate optional
method; it does not alter or reinterpret that existing method.

The caller supplies an event identity/date, lot identity, sold units q and cash
proceeds P. The method requires explicit affirmative declarations of proportional
allocation, homogeneous units, divisibility, unchanged measurement basis,
performance completion and equal carrying/tax-base treatment. Every declaration
has caller provenance. Unknown findings are unresolved, false findings unsupported,
and malformed declarations invalid. Provenance records the caller's premise;
it does not verify that premise or establish accounting-law admission.

Let N>0 be the lot's units immediately before this sale, C>=0 its carrying
amount and T=C its selected tax base. For 0<q<=N, f=q/N is the fraction of the
remaining lot sold. Release fC of carrying amount and fT of tax base. The
remaining record is (N-q,C-fC,T-fT). Preserve its original identity and
acquisition date. It is disposed exactly when q=N. A positive-quantity lot with
zero cost remains undisposed until its units are exhausted.

For cash proceeds P>=0, debit cash P and cost of sales fC; credit revenue P
and inventory fC. The sum of debit-positive postings is P+fC-P-fC=0. Cash flow
is P. Inventory falls by the same fC removed from the selected lot, leaving
all other lots and other_inventory unchanged. Profit increases by P-fC;
the asset increase is P-fC, so equity including profit changes by the same
amount. In the indirect operating bridge, profit P-fC plus the inventory
reduction fC gives the same cash receipt P. No tax expense is assessed here.

The retained fixture has N=2,C=T=20,cash452 and total inventory80. Selling
one unit for15 releases10,leaves units1/carrying10/tax base10,cash467 and total
inventory70. A second one-unit sale for15 releases10 and exhausts the lot,
leaving cash482 and total inventory60. The combined financial effects equal
the original full-lot sale for30 under the same conditions; the two dated
events and cash-origin records remain distinct. These are hypothetical controls.

Each proposal binds full before-state,event,method source lock and complete
after-state. Apply recomputes and compares the entire proposal. No caller
assertion,content hash or balanced journal alone establishes acceptance.
The existing shared-book invariant validates state allocation and chronology.
Only balances,date,seen,flows and the selected lot may change. No old return
settlement,tax adjustment,lease,source or opening history changes.

Statement checks use the protected shared-book report's account classification
and exact profit,equity,gross cash and indirect bridge expressions. A full sale
is compared to that report's original execution path. A partial sale is checked
by independent equations; the existing report dispatcher does not yet execute
the optional event. Annual integration,matched source syntax,heterogeneous cost
allocation,remeasurement,partial return-right settlement and actual admission
remain separate tasks. This method is a conditional mechanism,not a cost-policy
recommendation or production inventory system.
