# Refinancing preserves distinct debt, tax and ownership dependencies

28 October 2026. SIM-F066; C04; MC05/09/10/11/12/13/18/25/28/33/34.
Attempt02 passes293 exact checks with11 saved native programs and13 dependency
controls. Full inputs, transitions, reports and local source snapshots are
preserved in attempt-02; manifest.json records command, commit, environment and
elapsed time. Setup01 and attempt01 are retained with their fixture/test repairs
in setup-diagnostics.md. CPU-only deterministic work; no statistical ranking.

The supplied company starts with cash30, inventory170, old debt100, capital100
and100 old ordinary shares. It receives service revenue20, issues new debt80
and10 shares at2, repays old debt100, pays fee4 and new interest2, then accrues
and pays tax3.5. Every transition agrees with an independently specified journal
under two account maps. Final cash is40.5; old debt is0 and new debt80; net
income is10.5; equity including profit is130.5; old owners hold10/11. Gross
financing receipts and payments are each100 despite zero net financing cash.
Replay, dated cash-flow identities, debt memory and complete reports agree.

Before refinancing, the tax view gives5 and old ownership1. Reusing those
values after the fees, interest and new shares is wrong relative to the
declared question. A negative comparator deliberately supplies old tax5 to
the native program: the books still balance, but cash is39 instead of40.5.
The joined evaluator derives tax from the accepted pre-accrual book and binds
the entire scoped book, schema, role map and supplied tax policy. Stale views
therefore stop before tax accrual/settlement. A coherent event rename changes
the binding even when immediate cash is unchanged; an incoherent rename is
invalid because the cash flow references an absent event.

Same-cash changes to dates, event identities, ownership and retained memory
invalidate reuse. Source/rate changes, tampered cached values, unknown premises,
unmodeled income/expense and unsupported tax treatments retain distinct
stale/invalid/unresolved/unsupported outcomes. Native controls refuse wrong
share units, foreign entity or tax-book profile, backdated events, duplicate
identities, unmatched debt clocks and overpayment. Accepted prefixes and
unexecuted commands are preserved.

This is a narrow authored tax adapter on the declared company book. The existing
shared_tax_reassessment_v1 lease/tax schema was inspected and is incompatible
with this book; it was not spliced into it or represented as integrated.
Immediate fee/interest deductibility, tax rate1/4, homogeneous shares, revenue
recognition and debt repayment at carrying amount are explicit synthetic
premises. Approval/offer/source facts, deferred tax, losses, credits, different
share rights, actual refinancing law and broad module compatibility remain open.
The runtime accepts explicit tax amounts; only the scoped joined evaluator
checks the supported calculation. It is not a general native tax service.

| Decision | Primary criterion | Veto diagnostic | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain complete-sequence F066 evidence | Full journals, debt, tax, ownership and report agree under both maps | All293 checks pass after preserved harness repairs | Supplied terms and tax/ownership scope | Connect broader compatible methods under explicit contracts | General tax/schema integration |
| Reject stale pre-refinancing views | Tax5/ownership1 differ from tax3.5/ownership10/11 | Scoped dependency checks reject reuse | Source identity does not authenticate a source | Supply reviewed source meanings and broader model cases | Actual law or admitted authority |
| Continue construction | Local harness errors repaired; original records preserved | No global continuation veto | Omitted model mechanisms and incomplete surveys | Execute F067 and ordered reading from355 | Release readiness or E3 forecasting |

Post-run red-team: passing a conditional example can conceal an omitted income
account or incompatible book; explicit income-scope and foreign-profile controls
address these local risks. A new relevant accounting treatment, share right or
tax fact would require a new supported scope, not automatic reuse. The weakest
substantive evidence remains the authored premises. Original status and broad
package acceptance stay unchanged.
