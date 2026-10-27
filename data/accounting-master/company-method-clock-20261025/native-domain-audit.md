# Native applicability audit before adapter promotion

Inspected native_returns.py invariant and transition (lines42–69 and91–147),
shared_tax_continuation_v1.py invariant/transition, and the explicit projection
fixtures retained with CompanyBookTransition/1. Named binding passes its explicit
request comparisons, but those fixtures are not complete native adapters.

| Obligation | Existing selected fixture | Required for reusable native adaptation |
|---|---|---|
| Native source/state shape and account population | Retained case supplies them; captured complement restores all fields | Validate the entire imported native state and explicit mapping; retain unsupported imported fields |
| Inventory allocation across every lot | Selected sale fixture asserts one lot and checks inventory = cost + other inventory | Enumerate/check all lots or state an enforced one-lot domain; never forget another lot |
| Return refund/recovery controls and settled rights | Checked by native invariant before comparison | Execute native-domain validation during import and after export, with status preserved |
| Units, carrying, tax base and disposition | Retained lot satisfies native constraints | Require nonnegative quantities/carrying, correct tax base and live/disposed consistency |
| Whole-lot fraction and selected method | Fixture asserts fraction 1 and chooses the method | Reject changed fraction, unknown method and absent/disposed lot explicitly |
| Performance finding | Bound requirement preserves true/false/unknown | Retain exact finding and provenance; no default true |
| Event and tax-close dates | Comparison supplies matching event_date | New binder derives date from event metadata; import native close date; refuse backdated event |
| Tax payment authority and available payable/cash | Authored fixture mirrors positive/available/control requirements | Preserve native unknown/unsupported/funding_failure distinctions and full state invariants |
| Reporting and source complement | Entire native after-state/payment reports match on selected cases | Explicit complement round trip and full applicable native reporting; no generic closing inference |

Decision: named-method binding is supported; general native-adapter admission is
unsupported. Missing domain coverage blocks that stronger conclusion, not further
development. Next: implement one complete native-domain import/export boundary and
its adverse cases, then compose admitted direct methods in one declared book.
No new source claim, forecast comparison or professional judgment is required.
