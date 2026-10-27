# Writing a repeated-operation company path

CompanyPathTextDraft/1 expresses the existing CompanyOperationPathDraft/1 input
as declarations. It adds no economic rules. A reader writes one initial year,
followed by one or more continuation years. The parser preserves operation
order, claim identities, exact amounts and explicit unknowns; the existing
interpreter determines recognition, settlement, failures and annual reports.

Each declaration occupies one line and ends in a semicolon. Tokens containing
spaces or punctuation can use shell-style quoting as parsed by Python shlex;
this is tokenization only, with no shell evaluation, substitution, includes or
comments. Multiline scalar strings are unsupported. Rational values use reduced
numerator/positive-denominator form, including 0/1. Truth values are true, false
or unknown. Unknown numeric values and operation instants use unknown.

## Blocks and initial state

The first line is: path profile name assumption; where profile is
CompanyOperationPathDraft/1. It is followed by initial_year; and its complete
declarations, ending in end_year;. Each later year begins continuation; and
also ends in end_year;. The document ends in end_path;.

The scalar declarations are name, assumption and depreciation_method.
The initial year additionally declares profile CompanyOperationsDraft/1;
opening_digest; and information archival_exogenous_stress;. Each scalar
declaration takes one value before its semicolon. Object declarations use the
positional arguments below.

| Declaration | Arguments, in order |
|---|---|
| source | path sha256; initial year only |
| context | entity book currency; initial year only |
| period | start end_exclusive |
| inventory | method unit_cost |
| debt | principal fixed_rate floating_rate floating_share coupon_years |
| facility, initial year | id limit drawn reserved eligible |
| facility, continuation | id limit reserved eligible |
| loan | facility_id principal annual_rate day_count fee interest_cash_class |
| tax | rate method |

The initial-year opening_claims; declaration opens an explicit array, followed
by opening_claim id ledger amount; entries. Similarly, assets; precedes
asset id cost life accumulated in_service; entries. The parser adds no missing
arrays or default values; the existing typed schema decides valid array lengths.
Continuations cannot redeclare source, context, opening claims, assets,
information or opening identity; execution carries those from the preceding
complete conditional year.

## Operations and settlement allocations

Every year declares operations; before its events. Each event has the form
operation id kind instant payload_arguments;. The common header supplies a
unique operation ID, a supported kind and a UTC instant or unknown. Payload
arguments follow this table.

| Operation kind | Payload arguments |
|---|---|
| purchase | units claim_id |
| delivery | units unit_price control_transferred claim_id |
| collection, supplier_payment | None on the operation line; use allocate |
| payroll, dividend | amount |
| plant_addition | asset_id cost life in_service |
| facility_draw, facility_interest, facility_repayment | None |
| depreciation, interest, tax, close | None |

After declaring a settlement operation, write one or more
allocate operation_id claim_id amount; lines. An allocation must name a
previously declared collection or supplier payment in the same year. Duplicate
claim allocations within one operation are invalid. These lines do not reorder
events; the sequence of operation declarations retains the precedence used by
the interpreter, including equal-time events.

For example, one second-year delivery and its first fixed installment read:

    operation delivery-1-a delivery 2026-01-03T09:00:00Z 16/1 12/1 true sales-ar-2026-a;
    operation collection-1-a collection 2026-01-04T09:00:00Z;
    allocate collection-1-a sales-ar-2026-a 396/5;

This excerpt is part of a complete year: other claims and operations still need
their own declarations. The separately generated 90% policy changes this
allocation to 432/5. The text stores the resulting explicit operation input; it
does not silently rerun a policy when a delivery line changes.

## Checks and limits

The complete 176-line baseline example is
data/accounting-master/company-text-20261023/examples/baseline.accdsl.
Five alternatives include first- and second-year price revisions, unresolved
payroll, supplier failure and policy-generated collections. All six texts lower
to exactly their saved typed inputs and reproduce every saved result and report.
The 78 checks also exercise quoting, booleans, unknowns, duplicate declarations,
missing fields, forbidden later openings and malformed allocation references.

Parsing and accounting validity remain separate. A well-typed negative purchase
quantity can be preserved as authored input and rejected by accounting execution.
Text identity does not grant source access or temporal admission. Policy
declarations, general expressions, conditional branching, interim periods and
bank/group/insurance methods need further language design. These examples do
not certify parser resource-exhaustion resistance or a production API.
