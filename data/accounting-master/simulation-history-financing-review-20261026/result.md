# Simulation-history and financing review result

Repo work date: 26 October 2026. This is a targeted design/source assessment
under [the reviewed plan](../../../docs/plans/accounting-simulation-history-financing-review-20261026.md).
The [reader-facing assessment](../../../docs/design/research/simulation-history-financing-review-20261026.md)
answers the three user questions. No engine, frozen release, external note or
manuscript was modified. No experiment or neural training campaign was run.

## Decision table

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Preserve joint economic/contract histories with journals | Existing design and aggregation derivation support it | No design veto; implementation remains bounded | Available disclosures may not identify contracts or policy | Add integrated same-report/different-shock cases on shared IR | Recovery of the actual legal journal or exhaustive real histories |
| Extend financing subledgers and policy interface | Current code's state and explicit exclusions inspected | No implementation-readiness promotion | Real contract facts, applicable accounting treatments and management response | Add instrument and equity register, explicit policy and failure semantics | General accounting compliance or predictive validity |
| Do not import the paired debt equations unchanged | Dated lender cash legs disagree under a shared face convention | Positive-recovery exact diagnostic exposes a mismatch | Whether a corrected source edition/redefinition exists | Use explicit advance and promised payoff; then re-derive affected model equations | A complete audit of the lecture or rejection of risky-debt research |
| Retain neural solvers as later candidates | Relevant paper algorithms inspected | No solver/runtime promotion; target tests absent | Target-specific optimisation, default boundary, pricing and state coverage | Establish an independent discrete benchmark first | General convergence, superiority or readiness to train |

## Inference status

| Evidence category | Status |
|---|---|
| Hard veto screen | A common face/proceeds interpretation fails lender break-even for the positive-recovery diagnostic; no engine test failure is asserted |
| Statistically supported ranking | None; no stochastic comparison was run |
| Descriptive-only differences | None used to rank methods; the reported toy yields are exact algebraic consequences of specified inputs |
| Default-readiness | No financing or numerical default was changed or promoted |
| Next evidence needed | Integrated event/statement cases, admitted contract and accounting rules, benchmark validation, then a separately reviewed solver protocol |

## Checks and run manifest

Command actually run:

```text
python3 data/accounting-master/simulation-history-financing-review-20261026/check_arithmetic.py
```

All exact Fraction assertions passed. The positive-recovery case gives
consistent proceeds 1880/21, yield 11/94, printed-equation yield 11/90 and
break-even discrepancy 44/101. No-default and zero-recovery cases coincide,
which explains why weak checks could miss the discrepancy. The fixed/floating
illustration reconciles both future balance sheets.

| Manifest field | Value |
|---|---|
| Git commit | Unavailable: project instructions identify an unusable .git marker; no repository initialised |
| Environment | System Python 3.11.15; standard-library Fractions; Linux WSL2 |
| CPU/GPU | CPU-only scalar arithmetic; no ML framework imported and no GPU detected or initialised |
| Data version | Synthetic inputs in the retained script; exact source hashes in source-manifest.json |
| Random seeds | N/A: deterministic exact arithmetic |
| Wall time | Initial tool command reported under 0.1 seconds; not a performance measurement |
| Outputs | arithmetic.json, check_arithmetic.py, source-manifest.json, source-support.json, inspected text extracts, eq. (3.27) page image, reader-facing note |
| Plan | docs/plans/accounting-simulation-history-financing-review-20261026.md |
| Result | This file |

## Source-support and survey limits

The new source manifest preserves byte-identical copies of three papers from
MathDevMCP into docs/papers, hashes the user's unchanged note, and identifies
the excerpts used. The note's pricing statement faithfully reproduces the
printed equation; the identified problem is its consistency with the cash
advance and next-period repayment in the same model. Printed p.94/PDF p.97 was
visually inspected in addition to text extraction.

The online search calls returned no usable source payloads in this turn.
Primary local texts therefore supply the technical claims. A direct NBER
publisher-page fetch succeeded and confirms the Duarte/Fonseca title, authors,
May 2026 issue and DOI 10.3386/w35283. It showed no explicit withdrawal or
correction notice in the inspected metadata; this is not an exhaustive
retraction clearance. The Strebulaev/Whited publisher lookup returned HTTP 403
both in the sandbox and on the authorised trusted retry. Current corrections
remain not checked; no claim of latest-edition identity is made.

This targeted review reuses the existing simulator survey and source-support
records. Its additions are in source-support.json. Citation counts and venue
rankings were not collected; they are unnecessary for the bounded derivation.
An exhaustive literature survey, current correction clearance and source-code
audit of proposed neural solvers remain open. No solver dependency is selected.

Backward leads retained from Strebulaev/Whited §3.6: Moyen (2004), Hennessy and
Whited (2007), Titman and Tsyplakov (2007), Pratap and Rendon (2003), Cooley and
Quadrini (2001). Duarte/Fonseca also identifies Gao, Whited and Zhang (2021) as
a model/grid comparator. These are candidates for the next financing-method
review, not technically inspected support in this result. Giacomini/Kitagawa's
related identification literature remains in the existing survey; the present
claim uses only the inspected definitions and posterior decomposition.

Forward snowballing was not completed. Current citation metadata are unavailable
in this bounded review. Omission risks include the direct costly-equity and
dynamic-capital-structure papers, maturity/refinancing and covenant models,
accounting-specific reconstruction/event models, and debtor-specific accounting
authority. They do not invalidate the cash-leg derivation; they prevent claiming
an exhaustive literature review or selecting a general financing model.

## Red-team assessment and continuity

Strongest alternative explanation of the pricing finding: b-prime or recovery
may be silently rescaled between displayed equations. The inspected text gives
no transformation. An explicit mapping that preserves both dated cash legs,
default arguments and actual recovery would overturn the mismatch conclusion
for that interpretation. Merely matching the no-default case would not.

Weakest evidence: no current erratum clearance or official solver-code audit;
the recommendation is architectural. Numerical checks establish the specified
algebra, not the correctness of an endogenous default equilibrium.

The result rejects importing one inconsistent convention pair; it does not
reject risky-debt models or the research direction. The prescribed repair is
explicit proceeds/face notation and a complete re-derivation before numerical
implementation. The remaining history, contract and policy work can proceed.

A fresh checkpoint read found Version 4.41 / 536 pages / not_ready, newer than
the inherited Version 4.40 summary. Additive entries reference this review;
the existing master next-plan and release hashes are preserved. MC08–18,
MC24–26 and MC28–35 gain scoped research/diagnostic evidence; no whole
requirement closes. Human judgment of prose and general product acceptance
remain pending.
