# Sector posting boundary: inspected alternatives

25 October2026. Plan: docs/plans/accounting-sector-posting-boundary-20261025.md.
The source inspection below precedes a new implementation. It does not rerun or
reclassify frozen releases, and makes no current-law or actuarial claim.

| Candidate | Actual computed quantity | Posting obstacle | Decision |
|---|---|---|---|
| SectorReferenceBinding/1 bank/insurer assessments | Selected native reference closures; profiles declare no accounting effect | No journal can be inferred from an assessment handle | Preserve as identity evidence only |
| SectorCompany/1 | Finite report with legal tax, FX, ownership and sector deltas; posts=false | Mixed contexts, supplied mappings and notional openings need separate contracts | Preserve report; do not relabel it as execution |
| PerformingEIRSchedule/1 / POCIDatedSchedule/1 | Certified intervals and linked proposed journals | Exact-rational book cannot post independently rounded endpoints; root/interval semantics need a separate design | Keep bank bridge open; no midpoint or endpoint default |
| InsuranceOrigins/1 loss_schedule | Exact rational signed journals, dated loss origins and liability/cash states | Need exact owner/unit/state binding, loss-component memory and event sequencing | Select as the smallest ready sector posting discriminator |

Read the complete loss_schedule calculation and its closed shape, findings and
refusal behavior, its retained loss-service-finance case and full saved result,
its semantic contract and prior source-reading record. The retained historical
EU text at lines55131–55187 was inspected directly: the loss component is part
of the remaining-coverage liability; the selected fixed proportional allocation
is a local assumption, not prescribed universally. No new authority is imported.

The retained example opens cash200, liability100 and loss component20. Its
first date2026-01-01 has finance10, release55 (revenue44 and loss reversal11),
and cash claims50: liability55,K11,cash150,equity95,profit−5. At2027-01-01,
finance−5 and release50 (revenue40,reversal10), then claims45, close liability
and K at0,cash105,equity105,cumulative profit5. Six signed journals and six
loss-component origins are available. K is memory within L; adding it as a
second liability would double count. No capital or opening cash is posted again.

The host book needs an explicit reporting interval containing the native event
dates. Do not silently reinterpret1January as31December or force annual carry.
A first bounded adapter can retain that full interval and report cumulative
states at both dates. Period-close policy remains separate. Extra host balances
and memory must be preserved, with no method writes outside declared roles.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Select exact insurance loss schedule | Complete native signed journals and memory origins are available and reconstructible | No interval-to-point conversion or missing journal | Host mapping, date sequencing and full-source/domain admission | Audit and implement a bounded native-result-to-book adapter | General IFRS17 engine, actuarial valuation or banking integration |

The strongest alternative explanation is that faithful execution preserves a
supplied but inapplicable accounting assumption. Source/accounting/eligibility
flags must therefore remain false. A changed source, forged native result,
wrong opening or mixed date invalidates the adapter evidence; candidate failure
requires its scoped repair. Wider sector directions remain viable.
