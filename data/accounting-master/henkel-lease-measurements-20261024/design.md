# HenkelLeaseMeasurements/1

This finite reference binds selected measurements from the exact retained
Henkel2025 annual-report audit. It uses TemporalMeasurementConstraints/1 and
JointMeasurementConstraints/1 unchanged. The supported relations concern
consolidated EUR-million measurements in the2025 document, including its2024
comparatives. They neither specify an individual lease nor create an executable
company opening.

## Request and source preservation

The closed request has profile, inventory_sha256, selected_relations,
rounding_hypothesis and identity_hypotheses. The inventory hash is fixed. Selected
relation IDs must be unique and drawn from the19-entry registry. The identity
map has exactly the selected IDs; each value is null or the exact proposed
premise returned by identity_hypothesis. The rounding premise is null or the
exact proposed EUR-million hypothesis. Callers cannot submit replacement amounts,
dates, owners, units, relations, formulas or source records through this adapter.
The separate closed resource budget uses the original engine's bounds.

Each result preserves all104 numeric and12 qualitative observations, the full
14-entry missing-state inventory, all source locations and reported literals.
The54 measurements used by the full registry reference those same observation
IDs; shared observations remain shared variables across relations. Unselected
and unsupported source content is retained rather than silently discarded.
Hashes protect46 prior files, and the original source-lock is checked transitively
before building any request. The Apple binder and synthetic lease engine remain
unchanged.

## Measurement time and conditional equations

The registry contains nine relations per presentation year: current/noncurrent
liability sum; gross ROU less accumulated depreciation/impairment; depreciation
category sum; undiscounted maturity sum; cash subtotal components; signed
liability stock-flow; signed closing versus positive carrying value; cash-flow
redemption sign; and maturity-table carrying value versus liability total.
The nineteenth relates2025 opening liability to2024 closing liability.

Snapshot relations require equal measurement dates. Period expenses and cash
flows retain calendar-year half-open intervals. Each liability bridge opens on
December31 preceding the interval and closes on its last included day. The
bridge includes the cash subtotal once; interest paid and redemption appear
only in their component relation. The temporal validator checks these roles
before lowering to the existing scalar solver. Quantities and time remain in
the preserved definition and lowering certificate.

No numeric interval is supplied by default. A missing rounding or identity
premise leaves the assessment unresolved. Empty selection reports
no_asserted_system while preserving the complete source inventory. An explicit
optional hypothesis proposes nearest rounding at one EUR million, with exact
half ties away from zero. For displayed d>0, its inverse interval is
[d-1/2,d+1/2); for d<0 it is(d-1/2,d+1/2]; for d=0 it is(-1/2,1/2).
These are mathematical consequences of the hypothesis, not claims about
Henkel's rounding convention. The printed '-0' remains in source_mapping; its
conditional numeric interval is the same as zero's, without inferred negativity.
Construction dashes receive no numerical interval.

Category sums containing unquantified construction dashes, the incomplete ROU
movement bridge, cash-versus-expense attribution and discounted/undiscounted
equality are outside the exact relation registry. A future extension needs
explicit additional evidence or premises; it must not turn those omissions into
zero amounts or balancing transactions.

## Results and replay

With all19 relations and both kinds of proposed premises, the54-variable joint
system has an exactly checked witness. This proves conditional compatibility of
the selected measurements. It does not identify actual unrounded balances, prove
that the issuer uses the proposed rounding rule or establish complete history
feasibility. The strict displayed-as-exact2024 ROU comparison is contradictory:
1,173-543=630, while net ROU is displayed as631. That counterfactual fails; the
source is not rejected on this basis.

Zero cell budget returns unknown, not infeasible. Source or schema corruption
returns invalid. Original temporal and joint validators retain their own
distinctions. verify_result rebuilds the full result and compares all fixed
fields; saved witnesses are checked mathematically against intervals and every
equation, and runtime fields must be finite and nonnegative. Solver witness
choice and measured runtime are not required to be byte-identical. The adapter
is a bounded design reference, not a persistence or durable-execution service.

Source admission, accounting admission, native-state admission and execution
stay false; actual history and complete membership stay unknown; executable
opening stays null. No authority, probability or forecast is added.
