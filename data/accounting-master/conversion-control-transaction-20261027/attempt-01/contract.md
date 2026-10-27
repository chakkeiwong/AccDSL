# Conditional acquisition-transaction component partition

27 October2026. MC04/05/17/19/20/24/25/28/30/33/34/35;W05/06/08/12/16.
Question: can a finite declared inventory keep consideration,pre-existing debt
settlement,other separate transactions and fees distinct without double count?
Profile ConditionalAcquisitionTransactionPartition/1 is a supplied allocation
record,not a rule for valuing conversion that confers control.

Source rationale and limitations are in source-review.md. AASB3 §51 supports
separate acquisition and non-acquisition amounts; §53 requires its own cost
treatment. The arithmetic total here is a reconciliation of supplied component
measurements,not an amount to insert into goodwill. The inventory deliberately
excludes NCI and any pre-existing equity measurement: those are separate
acquisition inputs with different roles. Prior debt cannot be labelled equity.

Input: explicit subject/actor/acquisition-date/cutoff,currency/unit,source text
and rationale,source availability,declared component IDs and up to16 records.
One unique record per declared ID is mandatory. Each has kind cash_transfer,
debt_claim_settlement,service_fee,or other_separate_transfer; role is
acquisition_consideration,debt_settlement,acquisition_cost,other_separate or
unknown; amount is a canonical nonnegative exact fraction or unknown. Cash
may belong to any measured role; debt must remain debt_settlement; service
fee remains acquisition_cost; other transfer remains other_separate. A record
may carry unknown role while its analysis remains incomplete. This is a
finite typing restriction,not a complete legal taxonomy. An unsupported
instrument/role is refused rather than silently reclassified.

Two explicit assertions,inventory_coverage and allocation_assessment,are
supplied_complete or unresolved. Only both supplied_complete,known amounts
and roles,and available source allow conditional totals by role. Actual
completeness is never established by this assertion. The source hash binds
context,currency/unit,inventory,records and these assertions. Unresolved
cases preserve the request,known partial totals and component-specific
dependencies; no final partition total. No report,goodwill or journal output
is permitted even for a complete supplied partition.

Fixture: independent cash80 acquisition consideration,debt-claim settlement20,
fee5 and other separate3 give a partition total108 but consideration only80.
The20 is an independently supplied synthetic settlement measurement,not a
loan carrying amount or universal B52 result. Zero debt settlement is a
distinct explicit case; unknown debt settlement is not converted to zero.
Ordering of the inventory/records is immaterial; duplicate/missing/extra IDs
invalidate the partition. Cases also split consideration across components,
change source timing,and exercise unknown allocation/coverage.

Evidence contract: primary criterion is independent full expected component
records and exact role sums,including permutation/splitting invariance and
unknown preservation. Type relabelling,double count,coverage loss,stale source,
wrong actor/date/unit or reporting permission veto promotion. Candidate
failure triggers repair; corrupt evidence invalidates the affected comparison.
The lack of a substantiated actual loan method blocks measured acquisition
claims,not this finite partition or independent ready work. Counts/runtime
explanatory. No actual authority,allocation,control or reporting admission.

Default audit:16 components is a resource bound; crossing it refuses rather
than claims complete coverage. Positive amounts are a finite restriction;
refunds and signed adjustments need a successor contract. Synthetic80/20/5/3
is an arithmetic diagnostic. Exact fractions avoid rounding assumptions.
Pre-mortem: balanced component totals may still reflect a false economic
assignment; retain supplied_assertions_only and all permission flags false.
CPU120seconds,three attempts,source locks,manifest,full comparisons and result.
No agents,installs,GPU,commits,fees,outreach,publication or E3.
