# Proposed first implementation profile

The first implementation should connect a company's disclosures, alternative
histories, economic events and complete statements. A financing-only example
would leave the working-capital, operating-asset, tax and reporting interfaces
untested. The proposed domain is therefore a bounded corporate company; the
initial authoring interface is typed constructors into the portable IR, with a
matched, bounded textual notation. These are separate choices. This proposal
addresses MC01–MC35 without asserting that every requested method is now supplied.

## Scope and the alternatives compared

P15 compared four candidates. Corporate/shared-IR and typed-library-first can
have exactly the same domain and differ only in authoring. Instrument-first
would make financing lifecycle work earlier, but cannot meet the whole-company
goal until the operating-company continuation is added. Broad sector-first
would require bank, insurance, group and cross-standard methods at entry, with
more currently unresolved authority. The chosen order exposes interactions in
one connected company while specifying extension requirements now. It does not
establish that this order is cheapest, fastest or easiest to use.

The profile is `CorporateJointHistory/1`. It includes one legal entity and book
per branch, a declared domestic functional currency, annual/interim evidence,
multiple source vintages and reviewed alternatives. Context and schema design
retain multiple-entity/perimeter/currency fields so an unsupported operation
is explicit. “One book” is an execution scope, not a global uniqueness rule for
companies or future groups. A company with subsidiaries, leases or contingencies
cannot be admitted as a closed single-company model merely by omitting them.

Evidence preparation must account for the declared statement and note inventory,
incorporated references and unresolved source units. Readings, interpretations,+assumptions and treatment eligibility are separate layers. Investor-information,
system-as-of and exploratory archival questions use the time contract's distinct
admission rules. Exact financial quantities, source precision and conditional
rounding assumptions remain distinct. Source limitations accompany each dependent
query; there is no global “complete” flag inferred from pages parsed.

The initial economic methods must connect sales/delivery/collection, purchases/
inventory/cost of sales/payables, payroll, tangible-asset additions/depreciation,
simple debt/equity/dividends and a declared simple tax model. They produce profit,
balance sheet, cash flows and changes in equity from the same event histories.
The simple tax model is an authored teaching assumption; actual tax requires
P17's jurisdictional method. Northstar supplies a closed synthetic example,
not proof that these methods cover Apple or a representative real issuer.

The initial reconstruction method is the history contract's admitted-template,
rational affine family with finite choices and bounded integers. It preserves
unidentified debt mix, unknown payment timing and other query-relevant state.
The declared half-year event slots do not recover invoices or prove daily
liquidity. Querying a finer horizon requires refinement or an unresolved answer.
Exact bounds require whole-domain reasoning and endpoint attainability; search
witnesses and explored extrema are not promoted to complete families or bounds.

Scenario execution initially supports imposed exogenous paths with explicit
behavior and information restrictions. Joint finite rational probability is an
optional extension under the admitted-measure contract. Unweighted alternatives
remain valid initial results. Continuous inference, causal interventions,
calibration and empirically validated forecasts require P17 methods and later
execution evidence. An imposed interest-rate stress does not reweight historical
contract alternatives or become a probability forecast.

Typed constructors must express all included records without embedding opaque
Python functions. The bounded text frontend initially covers the matched debt
and constraint fragment; unsupported declarations produce located diagnostics.
Textual whole-company authoring is a later frontend obligation, with the same
domain semantics and validation. Deferring that parser does not defer the
whole-company typed model, the DSL design or the portable representation.

## Acceptance examples and limits

The primary integrated example is the protected Northstar disclosure fixture
and chapter, interpreted through the new contracts. Its opening and half-year
events support independently calculable statements and a continuous debt family.
For the 2025 stress, let x be the floating fraction. The common joint result is:

| Quantity | Conditional value in currency units |
| --- | --- |
| Debt interest | 5 + 2x |
| Profit before tax | 82 − 2x |
| Tax at the stipulated 20% rate | 16.4 − 0.4x |
| Profit | 65.6 − 1.6x |
| Operating cash flow | 48.6 − 1.6x |
| Closing cash | 95.2 − 1.6x |
| Closing equity | 148.2 − 1.6x |
| Closing assets | 288.2 − 1.6x |

Here 0 ≤ x ≤ 1, payables plus debt are 140, receivables 55, inventory 40 and
net plant 98. Every row uses the same x. The endpoints are not equiprobable
scenarios, and the output is not a rectangular box of independently selectable
amounts. Changing the floating rate to 9% changes the interest slope to 4 and
the cash/profit/equity slopes to −3.2; independent arithmetic must detect that
change even if both frontends share an erroneous constant.

Acceptance of the specification requires exact expected exchanges for the
following connected cases, with preserved sources and explicit assumptions:

1. Annual/interim source inventory, missing incorporated reference, alternative
   narrative translation, rounding unknowns and separately admitted constraints.
2. Joint working-capital reconstruction and unidentified fixed/floating debt
   mix, with known aggregate movements and unknown intraperiod timing.
3. Conditional 2025 events, eligible treatments, balanced proposals, reconciled
   complete statements and debt-mix dependence, plus a changed-rate control.
4. Original versus corrected interim information views without later-information
   leakage; no automatic source-derived accounting permission.
5. Partial or unsupported region preservation, unavailable methods, exact versus
   approximate capabilities and unweighted versus admitted-measure queries.
6. Valid replay, changed-payload conflict, concurrent stale-head rejection,
   unknown commit recovery, review correction/invalidation and failed migration.

The shared platform examples exercise these connections alongside retained
evidence/time/history/uncertainty/accounting examples. A bounded real filing
case must retain its full declared inventory and all unformalized disclosures;
Apple's partial source preparation cannot satisfy that case by itself. E05's
real source-backed conflict and P17's dated accounting methods remain proposal
work. A document calculation satisfies only the finite arithmetic part of this
list. Runtime acceptance additionally needs implemented source/typed lowering,
solver/simulator, transaction fault tests and adapter checks. Human understanding
and accounting/forecast validity have separate evidence.

## Dependencies and retained later work

Implementation should proceed in dependency order, after the proposal has been
completed and the user has authorized implementation:

1. Versioned record definitions, exact values/context, source byte retention,
   dependency closure and pinned package/schema loading.
2. Review and time selection, provenance/invalidation, immutable views and the
   initial transaction store's receipt/replay behavior.
3. Typed constructors and validation; the matched debt text fragment and source
   maps; independent expected IR and adverse input cases.
4. Admitted history templates, joint affine constraints, finite-choice search,
   partial checkpoints, typed capability failures and query-dependent refinement.
5. The connected corporate economic and accounting methods with their actual
   authority, event scheduling and information boundaries; statement mapping.
6. The integrated company case, source corrections, replay/recovery and bounded
   real-filing coverage; then optional justified measure operations and adapters.

P17 must complete actual source-grounded methods for corporate operations,
bonds/equity, groups/FX, IFRS/US GAAP/ASBE, banks and insurers. The extension
records in I4 make dependencies visible; they do not count as method completion.
Examples must include a changed group perimeter, intercompany elimination and
FX translation, credit loss and credit-risk memory, and insurance service/
measurement memory. Imported official rules and software interfaces require
located inspected sources and explicit limits. General nonlinear inference,
calibrated forecasting, multiwriter throughput and distributed durability are
later implementation/evaluation obligations, not inferred from prototype tests.

P18 integrates the completed methods and contracts into the governing LaTeX
manuscript and inspects its actual rendering. P19 assesses the full proposal
against MC01–MC35 and G1–G18. The current architecture may be judged specified
within its scope while those later proposal blockers remain open. Neither that
judgment nor a successful PDF build authorizes product implementation.
