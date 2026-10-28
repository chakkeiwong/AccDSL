# What existing software can contribute to a company-state simulator

A reported debt balance, a loan's interest payment and the set of histories
compatible with a filing are different quantities. Existing software can help
with each, but an answer at one level does not settle the others. A parser may
identify two facts correctly while leaving their economic relationship unknown.
A coupon calculator may price a fully specified instrument while leaving its
existence in the company's books unresolved. A solver may preserve every
solution to supplied constraints while omitting a contract the source did not
fully describe. AccDSL needs to preserve these distinctions when connecting
components.

The retained code gives concrete examples. This comparison concerns the saved
Arelle, QuantLib and ACTUS sources and the exercised local Z3 wrapper. It is
not a statement about their latest releases. Exact file identities, inspected
ranges and remaining tests are recorded in the accompanying software review.
No external parser, pricing library or ACTUS service was installed or executed
for this comparison.

## Facts with the same structure can still disagree

The inspected Arelle fact object retains context and unit references separately.
Its concept-context-unit hash combines the concept QName, dimension-aware
context hash and unit hash. That makes it useful for finding candidate groups;
the hash contains no fact value and supplies no source-occurrence identity.
The item branch of isDuplicateOf checks concept, parent, context and unit, but
does not compare the item values. A separate value comparison handles numeric
precision and optional interval consistency. These operations answer different
questions, as the code itself makes explicit.[1]

The companion duplicate validator distinguishes complete duplicates from
consistent rounded values. Complete duplicates require both equal decimals
metadata and equal values. For a numeric set that is not complete, consistency
is assessed through the rounding ranges, with an additional requirement that
facts reporting the same decimals have equal numeric values. Its deduplication
methods can return the first fact for each decimals/value combination, remove
lower-precision members of consistent pairs, or select the highest-precision
fact from a consistent set.[2]

That selection is useful for a calculation, but the selected subset is not the
complete evidence record. AccDSL should keep every original occurrence and
the relationship between the selected value and the discarded representatives.
Otherwise a valid deduplication operation could erase the table location needed
to explain a later conflict or correction. Nor does a duplicate grouping show
that two vendors provide independent evidence: provider lineage and likelihood
dependence require their own assumptions.

The retained Apple example makes the distinction tangible. Its repeated debt
total appears at two unsegmented locations, while another occurrence with the
same current amount belongs to a dimensional context. The local context test
keeps both selected total occurrences as provenance for one quantity and keeps
the dimensional occurrence distinct. It does not run Arelle or establish a
general extractor. The next Arelle comparison must reproduce those occurrence,
context and value distinctions on the same retained inputs, then test conflicting
values and a revision affecting only one provider alias.[3]

The 2 October ModelInstanceObject snapshot is byte-identical to the file in the
retained 5 October register for commit 01f6a4656c2c6551d2f05f31c9d74366d133ee7e.
This establishes the source connection used here. It does not resolve the
selected importer's dependency environment, taxonomy closure or source terms;
those remain separate tasks in the existing importer proposal.[4]

## Interest depends on more than a rate increment

The QuantLib FloatingRateCoupon constructor accepts payment and accrual dates,
an index, fixing lag, gearing, spread, day counter, arrears flag and fixing
convention. If a fixing lag is not supplied, it uses the index's fixing lag;
an empty day counter similarly uses the index's day counter. The coupon
registers with both the index and the evaluation date. Reproducible use therefore
requires the relevant index, calendar and evaluation state, not just a numerical
rate and principal.[5]

Its fixingDate selects the accrual end when the coupon is in arrears and the
accrual start otherwise, then advances using the index's calendar and fixing
convention. The rate calculation requires a pricer and delegates to
swapletRate. The price method discounts the coupon amount at its payment date.
These are distinct operations: fixing determines the rate information used,
accrual determines the earned amount and payment timing determines discounting.
The inspected file alone does not justify replacing every pricer with
reference rate plus spread.[5]

AccDSL's original reset discriminator is intentionally narrower. It assumes
principal 100, reference rate 3%, spread 2%, actual-days/365 and specified January/July
resets. A two-point shock at the July reset affects 184 days in 2027, giving
interest 5 + 2(184/365). The independent daily sum confirms that calculation.
It does not test a fixing lag, business-day adjustment, arrears pricer or market
curve. Those differences define the next comparison with a version-matched
pricing implementation; they cannot be treated as rounding error.[6]

The QuantLib file's recorded content hash verifies, but the inspected register
identifies a mutable branch snapshot rather than a matched source commit and
dependency build. The appropriate next step is to resolve that exact version
and its index/pricer dependencies, then specify their relevant conventions.
Selecting a current release merely because it is available would change the
comparison.

## Contract events still need company meaning

The retained ACTUS service obtains a projection end from termination, maturity,
amortization or settlement dates. If none is present, its controller falls back
to the current local time plus five years. For AccDSL, that fallback would make
an otherwise identical request depend on its execution date. The caller must
therefore supply an explicit horizon or return an unresolved result.[7]

The service's risk observer divides observations by their supplied base and
looks up the last time-series value at or before the requested time. This is
a carry-forward rule; it does not estimate a future rate process or establish
when a company or lender learned the observation. Equal timestamps inserted
into its map also use ordinary key replacement, so source multiplicity and
conflicting reports must be handled before that map is constructed. Empty or
before-first lookup is not a typed financial unknown in the inspected path.[7]

The exported event includes type, time, currency, payoff, notional, rate and
accrued interest. Those fields are useful proposed contract consequences. They
do not contain the original source assertions, legal-book owner, accounting
journal or reasons why a proposed transaction was authorized. Floating-point
event amounts also require an explicit comparison policy against AccDSL's exact
rational fixtures.[7]

The retained PAM arithmetic already checks 24 published events. It remains
independent fixture arithmetic, not execution of the ACTUS core. The service
requests core 1.1.0, while retained specification, dictionary and test revisions
have their own identities. A matched accessible implementation and its
initialization, calendar, risk-input and event-order behaviour are still needed
before claiming runtime equivalence. The new simple rate schedule does not
remove that requirement.[8]

## A solver preserves the model it is given

The local rational solver declares finite integer/Boolean choices, validates
the supported arithmetic fragment and retains formulas and unresolved search
regions. It rejects symbolic multiplication outside its affine fragment and
undeclared variables. Explicit budgets can return partial or unknown results.
These are substantive behaviours of the inspected wrapper; the bare word
sat does not describe its full result.[9]

The two-year loan case shows why the constraint matters. With one persistent
type, the exact interest paths are (5,5) and (7,7). Dropping type equality permits
(5,7) and (7,5), even though the annual marginal values remain 5 or 7. Total 12
then becomes feasible. The solver correctly answers both supplied problems;
only one represents the original no-amendment premise. Model construction must
therefore preserve the source-supported cross-time relationship. Solver
success cannot recover an omitted premise.[6]

The same division of responsibility applies to declared company methods.
The gross-equity example preserves two histories with identical closing cash
and shares but different gross flows. Deliberately removing the retirement's
share update leaves balanced financial statements and a repeatable native
result, yet the share count is wrong. Independent operation-specific checks
are therefore necessary alongside source identity, dimensional typing and
journal balance.[10]

These components can form useful parts of the simulator when their inputs and
limits remain explicit. Source parsing proposes facts; interpretation connects
them to quantities and contracts; contract calculations propose dated economic
consequences; accounting methods update books and memory; and reconstruction
retains the jointly feasible alternatives. The remaining work is to demonstrate
those connections on the same supported histories, with unknowns and conflicts
preserved throughout.

Source anchors (all paths relative to the repository):

1. docs/design/research/software/Arelle_Arelle-arelle_ModelInstanceObject.py,
   lines 179–235, 465–579; item-duplicate and value-equality branches inspected.
2. docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/arelle__ValidateDuplicateFacts.py,
   lines 34–284; complete/consistent sets and deduplication methods.
3. data/accounting-master/company-state-context-failure-20261028/result.md;
   company-state-evidence-failures-20261028/result.md in the same parent.
4. docs/design/proposal/methods/preparation-20261005-v1/03-adapters/source-register.json;
   docs/design/proposal/methods/selected-reuse-20261015.md.
5. docs/design/research/software/lballabio_QuantLib-ql_cashflows_floatingratecoupon.cpp,
   lines 33–107; full retained implementation inspected, no execution.
6. data/accounting-master/company-state-persistent-rate-failures-20261028/result.md
   and attempt-01 formulas/native/schedule results.
7. docs/design/research/software/actus-interface-20261023/EventController.java,
   lines 31–44, 97–139; TimeSeries.java, lines 26–46, 109–119; Event.java, lines 6–28.
8. docs/design/research/actus-interface-boundary-20261023.md;
   data/accounting-master/literature-closure-20261026/software-audit.md and
   actus-fixture-results.json. Historical missing-core findings are dated evidence.
9. scripts/rational_solver_v1.py, lines 90–140, 202–319; retained exact-case results
   referenced in 6. Installed Z3 reports 4.16.0; this observation is not a new lock.
10. data/accounting-master/company-state-gross-equity-history-20261028/result.md
    and its retained missing-share-update negative fixture.
