# Apple tax recognition, restricted funds and settlement

9 October 2026. Authorised E01/C03/C08 proposal preparation; MC01–05/07–12/
15–16/19/28/30/32–35 and G1/G4/G5/G7/G11/G13/G15/G16. Baseline is the closed
139-page Version 2.9. Full readiness remains `not_ready`; product implementation
and the historical controller remain held.

## Question, population and evidence contract

What do the retained annual and interim disclosures identify about tax expense,
tax balances, restricted funds and settlement? Read complete annual Note 7,
partition its material content, and inspect the precise dependencies in annual
Notes 1/4/6, annual/interim statements, interim Note 4 and both MD&A tax/State Aid
passages. There is no standalone interim income-tax note. Preserve A07/A10/A11
as historical proposed assertions and add this deeper reading separately.
Broad statement context may be retained while only declared tax/funding rows
are formalised. This is not complete note coverage outside annual Note 7 or
whole-company semantics.

Comparator: Version 2.9 and explicit shortcuts equating total tax expense with
cash paid, tax-payable change with current expense less payments, net deferred-
tax-asset change with deferred benefit, and restricted-fund movement with new
tax expense. Test them against source context and stated bookkeeping identities.
Primary pass: faithful complete reading of the declared tax note, explicit
source/date/currency/precision mapping, checked numerical consequences, and
clear separation of reported movements, unresolved residuals and authored
conditional journals. Counts and build success are explanatory only.

Source/sign/date/unit errors, invented residual causes, unlabelled accounting
assumptions or a misleading stock-to-flow identification veto dependent claims.
A failed shortcut triggers the next scoped reconciliation; it does not reject
the source or end the research direction. Corrupt sources, invalid identities
or unsupported equivalences stop dependent work until repaired. No probability,
tax-law conclusion, full ASC authority, actual journal reconstruction, complete
history family, full package semantics or independent acceptance is claimed.

Artifacts: `data/accounting-master/apple-tax-20261009/`, with a separate
`docs/design/proposal/manuscript-tax-20261009/` candidate. Deterministic source
and arithmetic work only; no stochastic ranking or benchmark ladder applies.

## Skeptical audit and assumptions

The screening found a finer 10,246-million State Aid line alongside rounded
10.2/15.8/4.8-billion narrative amounts and an 823-million benefit decrease.
Do not manufacture a conflict from their displayed centres. Annual Note 6 has
both current and noncurrent tax payables: either alone is a wrong baseline for
the proposed total-payable bridge. Note 7's net DTA and Note 6's asset amount
also differ in target. The quarter's payment and remaining obligation have
both euro and dollar amounts at different dates; their ratios are not a
verified common exchange rate. The quarter lies after FY2024.

The plan passes after preserving those targets, refusing causal assignment of
residuals, and making any journal illustration conditional. Full Note 7 reading
must retain uncertain-tax-position scope, the valuation allowance and the
management range about possible future decreases. That range is not a payment
forecast or probability law. No external tax or legal authority is promoted
from Apple's account of the court decision.

| Material choice / provenance | Status and reason | Failure mode / early check |
| --- | --- | --- |
| Retained annual PDF and interim HTML | Pinned case sources, not new sampling | Wrong versions/columns: compare exact hashes, date headings and originals |
| Full annual Note 7 plus named dependencies | Bounded population answering recognition and settlement | Missing payable class/escrow classification: inspect Notes 4/6 and interim MD&A before calculating |
| USD millions with EUR separately retained | Reported scales converted explicitly | Mixing currencies or fiscal periods: separate units and dates in each bridge |
| Nearest rounding when evaluating compatibility | Conditional sensitivity hypothesis; issuer rule unverified | False exactness: carry each displayed quantum and retain the tie-rule uncertainty |
| Total-payable/current-expense/cash identity with an other-movements term | Local diagnostic model, not a complete tax ledger | Treating the residual as a known journal: label it unallocated and list missing allocation/FX/timing facts |
| Conditional settlement journals, if useful | Teaching illustration of liability settlement at carrying value | Pretending to know cash/securities liquidation or realized FX: state assumptions and distinguish reported payment from authored posting |
| Existing Python, PDF/HTML tools, LuaLaTeX | Convenience tools, no installs | Extraction/layout mismatch: original page and derived-view inspection plus final render |

Pre-mortem: a perfectly balanced illustration could hide an invented tax asset,
offset permission, timing or exchange rate. Restrict the example to explicit
assumptions and avoid deriving actual journal allocations. Source arithmetic
cannot certify US tax treatment or forecast applicability.

## Execution and stopping point

1. Preserve four live pointers and the prior closed unit/candidate; verify prior
   manifest references using pointer relocations. Record existing Git HEAD;
   preserve unrelated dirty work without Git mutation.
2. Map complete annual Note 7 and named dependencies; retain raw text/DOM tables
   and original page locators. Inspect annual PDF and clearly labelled derived
   interim HTML pages at readable size. Check all declared table columns.
3. Reconcile current/deferred components, statutory-rate bridge, DTA/DTL and
   valuation allowance, gross uncertain-benefit movements, payable/cash and
   State Aid timing/precision. Record unsupported causal links explicitly.
4. Integrate Version 2.10 after Chapter 9's existing lease/tax example, preserving
   previous argument and bibliography. Introduce the real-source question and
   notation locally; show the calculations needed to follow it.
5. Build, inspect affected/adjacent pages and navigation, check preservation,
   record source/numerical/interpretation limits and provisional author review.
6. Update the four live master records and requirements supplement with the
   checked result and next concrete task. Preserve all MC/G obligations, five
   E streams, forty exhibit targets and 136 unverified publication dates.

Use `CUDA_VISIBLE_DEVICES=-1 python3` for local helpers. Build command:
`latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex`.
No network, new dependencies, GPU, paid review, outreach or external publication
is planned. One bounded source/integration unit; repair local defects before
completion and preserve failed attempts if generated evidence changes. The
unit stops at checked integration, with a concise result and run manifest.

Reader questions: How can current and deferred tax produce the total expense?
Why is cash paid different? Which payable classes are included? What does the
State Aid charge offset, and which numbers have coarser precision? What changes
when restricted funds settle a previously recognised obligation? Why is a
possible gross-UTB decrease not a distribution of future cash payments?
