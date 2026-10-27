# Retained debt disclosures now use native measurement types

28 October 2026. Unified T01/T03/C01/C04; MC03/05/06/07/08/10/13/19/27/28/33.
Plan: docs/plans/company-state-debt-measurement-20261028.md.

The adapter constructs twelve distinct reported debt quantities from thirteen
inspected Note9/XBRL occurrences. Principal appears in two tables and retains
both provenance pointers as one quantity. Native TemporalMeasurementConstraints/1
checks the principal-to-carrying reconciliation, current/noncurrent partition
and maturity allocation using the reported USD-million scale and reporting
instant. The independently supplied printed values pass exact witness checking.
All124 checks pass in attempt-02.

Financial meaning survives the lowering:97,341 principal less321 unamortized
adjustments and358 hedge adjustments equals96,662 carrying debt. Current10,912
plus noncurrent85,750 equals96,662. The next reported principal bucket10,930
differs from current carrying debt by18. Substituting either principal for
carrying or the first maturity bucket for current carrying produces a checked
contradiction. Changing the deduction sign also fails. These checks address
mistakes that common currency and date types alone cannot detect.

Maturity classifications retain the actual observation instant2024-09-28.
They do not become realized2025–2029 cash flows or exact legal payment dates.
The separate issuance-proceeds reading retains its2023-10-01 through2024-09-28
period, original source card and exact_economic_zero=false. Native type checking
accepts that observation; it remains outside the coupled debt equations because
no supported roll-forward is available. The compiler correctly rejects an
unused observation, and the adapter supplies no artificial equation to bypass it.

The result includes all source cards, the new source-time card,15 original
issuer dependency rows and180 target obligations. Historical queries at
2024-10-31,2024-11-01 and2026-10-28 remain unresolved: raw vendor dates and saved
acquisitions cannot supply missing clock meaning or actor access. An audit
measurement definition is retained, but policy_input and executable_opening
remain null. Source, accounting, actor and forecast admission remain false.

## Repair and interpretation

Attempt01 stopped before numerical evaluation because the implementation
assumed every selected concept used the US-GAAP namespace. The inspected hedge
adjustment is an Apple extension. The exact namespace is now preserved, and a
negative control rejects silently standardizing it. Failed code and the failure
record remain in attempt-01; repair-01.md explains the correction.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain reported-measurement adapter | Full source/quantity mapping and independently checked printed relations |124 checks pass after namespace repair | Unrounded amounts, supported history and contract structure | Trace source-backed contract/operation dependencies and retain missing inputs | Actual company opening or debt cash-flow simulation |
| Preserve period and population distinctions | Maturity instant and issuance period remain distinct; no unsupported bridge | Wrong dates, context, scale, concept and substitutions refused | Instrument allocation and actual payment dates | Connect retained contract/exhibit evidence where available | Current carrying equals next principal payment |
| Keep historical access unresolved | No date field silently acquires publication or actor-receipt meaning | All requested historical views withhold admission | Authoritative source chronology and access | Continue independent construction; seek exact timing evidence only for dependent claims | Historical availability or forecasting eligibility |

This is exact arithmetic on displayed quantities, not a claim that rounded
reported values are exact economic amounts. No stochastic ranking is involved.
The run manifest binds source/compiler identities, commit, command, environment,
CPU-only status, elapsed time and output paths. The native result preserves
its own conditional status and scope.

Post-run review: an explicit interpretation can still be wrong even when the
compiler and hash checks pass. Here the inspected PDF captions, relationship
signs and exact source concepts support the narrow mappings; broader accounting
acceptance remains pending. The mapping is an auditable actual-source step
beyond the synthetic cross-case join, but the legal instrument population and
whole-company state remain unknown. No broad requirement closes.
