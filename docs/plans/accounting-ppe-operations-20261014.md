# P17-04/P18 continuation: component replacement, disposal and revaluation

14 October 2026. MC02/04/07/11/13–16/19/20/28/30/32–35; E07/G4/G12/G15/G16.
Protected baseline: Version 2.77, 234 pages, SHA256
`678881a3c000433207ab5875a82c4f482a5519706c12e8390fe502ea3c8bd69d`.
The work supplies accounting methods and checked documentary cases. Runtime
implementation and the historical controller remain held.

## Question and skeptical audit

Can a reader reconstruct component replacement/disposal and whole-class
revaluation from dated facts through asset memory, entries, profit, OCI, cash
flow and equity? Compare with `corporate-methods-v1.md` and Version 2.77's
corporate-methods section: basic depreciation and prospective estimates already
exist, but the replacement rule lacks a full case and revaluation lacks an
asset-specific history. Repeating the earlier 100/10/three-year example would
not close this gap. Balanced entries and added pages are not pass criteria.

The source audit found a material date mismatch in a possible 2023–2026
cash-flow comparison. Retained AASB116 compilation 6 (31 December 2022,
F2023C00192) and its official HTML identify annual starts 2023-01-01 inclusive
to 2027-01-01 exclusive. AASB107's misleading `jun2023` filename contains
compilation 5 dated 31 December 2023; the HTML interval is 2024-01-01 inclusive
to 2026-01-01 exclusive. Do not borrow the AASB15 upper date or assert that
either historical edition is current authority beyond its recorded interval.
Repair: compare statements for calendar 2024/2025. Revaluation's 2023
depreciation/measurement history supplies opening balances under AASB116;
no cash-flow presentation claim is made for that prior year.

The revised audit passes: exact historical sources, dated synthetic facts,
class membership and per-asset surplus/loss memory precede calculations.
Administrative equipment consumes benefits in these periods, so depreciation
is expense rather than an inventory cost. Fair values are admitted synthetic
inputs, not an uninspected valuation algorithm. No stochastic comparison,
hardware dependency, live-company posting or accounting-policy superiority is
being tested. A missing valuation or class member prevents an unconditional
revaluation result; it does not invalidate independent cost-model work.

## Evidence contract and research intent

Primary criterion: exact dated journals and independent state/statement
reconciliation for both cases, with a wrong but balanced treatment exposed by
each relevant rule. A source/application mismatch, double-counted old component,
cross-asset netting of revaluation history, wrong profit/OCI split or unexplained
cash/equity difference vetoes the affected example and triggers repair.
Source hashes, journal balance, build and preservation are integrity diagnostics.
Missing whole-company facts, tax and human acceptance block those larger claims,
not provisional drafting. Stop this unit only if its artifacts cannot support
the specified calculation; continue independent ready units after a scoped block.

These cases establish no current IFRS/US/ASBE compliance, market fair value,
complete tax result, general financial-statement compliance or runtime
conformance. Preserve results in
`data/accounting-master/p17-completion-20261014/P17-04/ppe-operations/` and the
method in `docs/design/proposal/methods/ppe-operations-20261014.md`.

## Defaults and assumptions

| Choice and provenance | Justification and status | Failure mode and early check |
|---|---|---|
| Historical Australian for-profit AASB116.7/12–15/29–55/60–62/67–73 and AASB107.16/18/20/43 | Retained primary sources; supported only in the recorded edition/interval | Not-for-profit class-offset rules or newer presentations imported silently; inspect scope, exceptions and compilation tables |
| Two declared synthetic companies; one currency, exact units, no rounding | Teaching convenience, not issuer facts or one assembled company | Spurious cross-case aggregation; retain separate ledgers and openings |
| Zero residuals, even annual use, unchanged supported lives, no other impairment | Authored measurement assumptions; simple inputs expose replacement and revaluation mechanisms | Wrong depreciation destination/timing or hidden impairment; assert available-use dates, remaining lives and assessment dependency |
| Cash purchases/sales; no selling costs, leases, held-for-sale interval, grants or routine rental disposals | Narrow transaction facts; ordinary derecognition under 67–72 | Unsupported gross revenue or lease treatment; reject the affected scope rather than generalize |
| AASB116.35(b) elimination of accumulated depreciation; surplus transfer only on disposal | Permitted presentation/transfer choices; not mandatory policies | Lost gross/accumulated audit trail or transfer through profit; retain pre/post amounts and reconcile equity |
| Entire two-item revaluation class; reliable fair values supplied by assumption | Makes 36–40 and per-asset memory testable; no fair-value-engine claim | Selective valuations or offset between assets; exact member-set and individual history checks |
| Pretax presentation | Tax law/bases absent; not a claim that tax is zero | Equity called post-tax/compliant; label slice and preserve AASB112 dependency (116.42) |

## Exact cases and execution

1. Cost model: open 1 January 2024 with cash/capital 200. Buy and immediately
   use an administrative asset comprising shell 80/eight years and old component
   20/two years. At 31 December 2024 depreciate 10 each. On 1 January 2025
   replace the old component: remove its remaining 10, buy new component 30
   with three-year life and begin use immediately. Depreciate shell/new 10
   each during 2025. On 31 December 2025, after depreciation, control passes
   to a cash buyer for 90. Derive gross-cost/accumulated removals, loss/gain,
   closing balance sheets, both cash-flow presentations and equity. Expose
   retained-old-component and ordinary-servicing capitalization errors.
2. Revaluation: two administrative machines A/B form the whole elected class.
   Original costs 100/40, lives five/four years, available 1 January 2023.
   Opening historical capital/cash before purchase 200. At 31 December 2023,
   depreciation 20/10 gives 80/30; reliable assumed values 120/24 give A's
   surplus 40 and B's profit-or-loss decrease 6. This establishes the 2024
   opening only. In 2024 depreciate over remaining four/three years, then
   value both at 45/22. In 2025 depreciate over remaining three/two years,
   then value both at 50/11. Immediately afterward sell A/B for 50/11, and
   transfer any remaining surplus directly to retained earnings. Show why
   2023's net class increase 34 cannot all be OCI for these for-profit assets,
   and why a disposal surplus transfer cannot be recycled through profit.
3. Independently check complete journal-derived balances against component
   roll-forwards and explicit expected statements using exact fractions.
   Include missing class/valuation, wrong scope and balanced wrong-entry
   dispositions. Retain the original cost-model/estimate example unchanged.
4. Copy the protected source tree to Version 2.78, integrate the explanation
   near PPE, build via `scripts/accounting_document_tools.py build`, inspect
   affected pages, and verify equation/citation/source preservation. Record a
   result with decision table, actual commands/timing and red-team findings.
5. Refresh the residual matrix and six live controls; audit and continue the
   next ready corporate or cross-cutting unit. Whole-company assembly and
   whole-candidate/human review remain P17-11/P18/P19 obligations.

Pre-mortem: plausible totals can conceal asset-history errors; net class OCI
and a capitalized maintenance payment both balance. The early discriminating
checks compare the individual component exits, asset-specific OCI/P&L routing
and explicit eligibility to the retained paragraphs, independently of journal
balance. Commands use system Python/fractions and document tools only; no new
dependency, numerical framework, GPU or external worker is needed.

Pre-acceptance repair: the first arithmetic check passed, but its proposed
immediate sale at 55/12 differed from the same-date fair values 50/11 without
facts explaining the difference. The revised case sells at 50/11, giving zero
disposal gain; the separate cost-model case already demonstrates a gain.
This removes an unnecessary valuation assumption. The initial plan, method,
calculation and build are preserved under `ppe-operations/initial-model/`.
The next calculation/build validates the revised case; the earlier pass cannot
be reused for its changed statements. An unresolved section reference is also
removed in favor of a located same-chapter description.
