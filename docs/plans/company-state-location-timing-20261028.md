# Entity transfer limits and cash timing: SIM-F039/040

28 October 2026. C04; MC07/08/09/10/13/14/17/19/20/24/28/33/34.

Question: does preserving legal entity, currency and settlement order change
the ability to meet a specified payment? Baselines are original SIM-F039:
parent cash5, maturity20, subsidiary cash30, transfer cap10; and SIM-F040:
foreign receipt after foreign debt payment. Use exact bounded constraints plus
the existing declared book methods. No source-admitted transfer permission or
whole-company liquidity model is asserted.

Skeptical audit: group cash35 cannot answer whether the parent has20. Netting
end-period receipts cannot answer whether cash exists at payment time. A
single-book execution cannot prove cross-book atomic settlement. Test the
original inequalities independently, then matched conditional native legal
books; explicitly keep atomic multi-book execution outside this unit. The
comparison must change only cap, location or event date. Do not accidentally
allow borrowing, FX conversion or equity issuance as a hidden rescue channel.

For F039, the only permitted parent inflow is transfer x, with0<=x<=cap and
x<=30. Payment20 requires5+x>=20. The whole cap10 domain is infeasible;
cap15 is the exact boundary. Unknown cap retains the conditional threshold,
not a fabricated permission or default. Native examples model collection of
an explicitly assumed existing intercompany receivable, paired with the
subsidiary's payable settlement. They test matched entries; neither an
aggregate balance nor one leg alone supplies evidence that settlement occurred.

For F040, use an explicit EUR book with opening cash0, receivable20 and debt20.
A receipt on January3 cannot pay debt on January2. A January1 receipt can.
Separate USD or another entity's cash cannot be substituted for EUR liquidity;
native typed inputs and exact dates must preserve those contexts. No exchange
rate or within-day order is inferred. Same-day alternatives must be explicitly
ordered and reported as such. A reordered future receipt with an earlier debt
date must refuse rather than grant access to future funds.

Intent/evidence contract: primary pass is exact local cash feasibility and
full native balance/memory/flow preservation. Deliberate aggregate, currency
and chronology shortcuts must fail the independent criterion. Unknown transfer
rights remain conditional. Lost unknowns, a wrong book/currency, non-atomic
partial mutation on refusal or a false payment is a promotion veto and repair
trigger. Invalid harness/protected hashes is a continuation veto until repaired.
Counts and runtime are explanatory, not completion criteria. No stochastic
ranking, default change, insolvency conclusion, FX service, forecast or release.

Assumption audit: initial cash, maturity and cap are the original synthetic
case. Intercompany receivable/payable30 is an explicit settlement mechanism
chosen for the native example, not an inferred dividend or legal entitlement.
EUR20 and three named dates are convenience values to isolate timing; zero,
boundary and fractional variants test arithmetic. Two account maps test name
independence. Existing exact solver budget is a reviewed local diagnostic
budget only; incomplete results must remain Unknown. Preserve formulas,
programs, results, source hashes and failed attempts under
data/accounting-master/company-state-location-timing-20261028.
