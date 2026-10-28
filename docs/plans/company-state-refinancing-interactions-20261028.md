# Refinancing across debt, tax and ownership: SIM-F066

28 October 2026. C04; MC05/09/10/11/12/13/18/25/28/33/34.

Question: does a supplied complete refinancing sequence preserve debt identity,
dated cash, tax premises and share ownership when individually balanced modules
are joined? The comparator is an independently calculated full journal sequence,
plus deliberately stale tax/ownership views. No empirical research or E3 forecast.

Skeptical audit finds that shared_tax_reassessment_v1 operates on a lease/tax
book with its own state and loss contracts. It is not compatible with the
declared company program merely because both expose cash balances. Do not splice
these schemas or claim general tax integration. Reuse the unchanged declared
company executor and financing method builder, with a separate authored, narrow
tax calculation and homogeneous-share memory on one explicit declared book.
Existing generic financing equity issuance changes capital but does not track
share ownership; this case must update shares explicitly. A checksum-only test
does not answer the question: compare every accepted transition and final report.

Synthetic premises: opening cash30, inventory170, old debt100, capital100 and
100 old shares; supplied service revenue20 received in cash; new debt80 and
10 new shares at2 fund repayment100; fee4 is immediately deductible expense;
new interest2 is deductible and paid; current tax is one quarter of positive
income, without deferred tax, losses, credits or refunds. The old debt is
extinguished at carrying amount without gain/loss. These are teaching hypotheses,
not actual accounting policies, prices, rights or law. The complete comparator
ends with cash40.5, old debt0, new debt80, tax3.5, net income10.5 and old ownership
10/11. At the pre-refinancing cash-revenue checkpoint, tax is5 and old ownership1.
Dates, entity, currency, measurement basis, share units and event IDs must remain
attached to each result. Tax settlement follows a freshly derived tax view;
the view records its actual book, account roles, policy and source premises.

Primary pass: independent full balances/journals, debt memory, share quantities,
tax and cash-flow totals agree under two account maps; replay reproduces them;
stale pre-refinancing views cannot be reused. Wrong-date, wrong-unit, duplicate-ID,
foreign-schema and wrong-entity requests refuse without mutating the accepted
prefix. Missing tax premises stay unresolved. Cache validity requires the
whole scoped dependency set, not matching cash or tax amounts alone.

Diagnostics: balance/replay/count/runtime are engineering explanations, not
source or economic admission. A mismatched journal, missing dependency or
silently coerced schema vetoes this candidate and triggers repair. Corrupt
protected inputs or an invalid comparator veto the run until repaired; no
candidate failure stops independent ready work. A finite cash sequence cannot
establish general module compatibility, legal refinancing, tax compliance,
complete source interpretation or whole-company simulation readiness.

Default audit: exact rationals and deterministic enumeration are reviewed
engineering choices for this finite case; supplied amounts/rate/timing are
hypotheses. Two account maps test incidental-name dependence but cannot prove
all schema compatibility. The smallest diagnostic is one joined execution
before expanding controls. Pre-mortem: the run could balance while omitting
shares or old debt, or pass using a tax schema it never consumed. Inspect those
states directly and preserve the explicit tax-adapter boundary.

Run bounded CPU-only python3 -B checks under
data/accounting-master/company-state-refinancing-interactions-20261028/.
Save every failed attempt, source hashes, exact inputs/results, command, commit,
environment and timing. No imports of GPU frameworks, installation or defaults
change. After the unit, refresh its disposition and current checkpoint, verify
protected releases, then continue SIM-F067 and ordered reading from355.
