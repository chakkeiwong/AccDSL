# ComparativeRestatement/1

This is a read-only reference exchange for the fixed synthetic PPE case.
Its exact JSON requests and results are in `attempt-01/exchanges.json`;
the admitted facts and catalog are bound by `input-lock-v2.json`. The contract
does not instantiate a production query service or post a correction.

The request has exactly `wire`, `operation`, `context`, `selector`,
`public_cutoff`, `system_cutoff`, and `findings`. The wire is
`ComparativeRestatement/1`, the operation is `report`, and the context must
equal the catalog's entity/book/currency/unit/rule/profile. Dates are canonical
ISO calendar days. The selector has exactly `mode`, `year`, and `edition`.
Years are integers 2023–2025, excluding booleans. `edition` mode names one
edition covering that year. `latest_available` requires a null edition.

An eligible edition covers the requested full year, is published by the public
cutoff and ingested by the system cutoff. The fixed catalog selects the latest
publication, then ingestion, then identifier. The latter tie breakers are
deterministic ordering within this authored catalog, not a general conflict
resolution policy. A report returns all full-year columns of its selected
edition; `requested_year` identifies the requested subset's anchor.

Findings have exactly the keys defined by `TRUE_FINDINGS`, `EPS_FINDINGS`,
and `material_earliest_opening_effect` in the pinned calculator. Each is a
Boolean or null. Authority and tax admission are required for all calculations.
Public shares, public issuance filing and voluntary EPS must each be false.
Restated reports additionally require reliable original information, availability
at authorization, reasonable obtainability, misapplication, material error,
full practicability and no hindsight, and a known earliest-opening materiality
finding. Original editions do not require later correction findings. Unknowns
do not become false or establish impracticability.

The fixed annual model starts with capital/cash 200, pays 120 for one asset on
1 January 2023, earns annual cash income 50, deducts fiscal depreciation 20,
and pays the previous year's tax on the following 31 March. Zero residual,
straight-line old/correct lives 144/72 months and rate 1/4 are supplied
hypotheses inherited from the protected example. The model returns annual
depreciation, PPE, fiscal basis, deferred liability, pretax/current/deferred/net
earnings, cash, current tax payable and equity. It also returns annual cash and
equity movements. No partial-year generalization is implied.

Success has status `conditional_complete`, a full selected-edition record,
context and input/catalog identities, the columns, cash/equity movements and
any corrected opening, comparative/current-opening differences and equity
bridge. Rational amounts are exact strings. `third_statement` is the corrected
1 January 2024 position only when its effect is supplied as material. The
opening is not a 2023 annual performance column. `posts_correction` is false
and `mutations` is always empty. Repeating a request returns the same report
and cannot post either the discovery correction or its presentation again.

Refusal has a reason, no selected edition or report, and no mutations.
Malformed/contradictory requests and changed bytes are `rejected`; unavailable
editions, missing bytes or unknown findings are `unresolved`; known out-of-scope
years, EPS requirements or false admission conditions are `unsupported`.
`attempt-01/adverse.json` preserves concrete reasons and expected outcomes.
No amount or report can be supplied by the caller to override the reconstruction.

Estimate changes, partial/cumulative impracticability, policy changes, other
tax laws, other assets, other report calendars, conflicting actual publications
and public-entity EPS need their own methods. The retained historical
EU source supports only the inspected steps, not a current applicability
decision or equivalence of complete accounting standards.
