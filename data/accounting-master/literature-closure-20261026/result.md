# Literature and method-transfer execution result

26 October 2026. **Substantial execution completed; the full gap-closure program remains partial.**
The plan was written, skeptically reviewed, repaired and executed. Review is
author self-review, not independent or human acceptance. The local mathematical
results and bounded runtime checks support their stated models, not a complete
scholarly survey or a general company simulator.

## Read the work

- [Reviewed plan](../../../docs/plans/accounting-literature-closure-20261026.md) and [continuation audits](plan-review.md).
- [Governing document](../../../docs/AccDSL-latest.pdf): Version 5.12, 741 pages, not_ready.
- [Simulation volume](../../../docs/AccDSL-simulation-foundations.pdf): Version 5.12, 26 chapters, 183 total pages and 165 body pages.
- [21-page supplement](../../../docs/design/research/simulation-literature-closure-20261026/supplement.pdf) and [source](../../../docs/design/research/simulation-literature-closure-20261026/supplement.tex).
- [Gap disposition](gap-status.md), [remaining closure sequence](remaining-work.md), and [failure coverage](failure-coverage.md).
- [Final author review](final-review.md), [rendered review](rendered-review.json), [verification](verification.json), and [artifact manifest](artifact-manifest.json).

The standalone satisfies the requested 150–300-page length. Length does not
establish scientific or implementation completeness. The old design remains
[archived](../../../docs/archive/accounting-product-design-v1.2-20261026/ARCHIVE.md).
The concurrent post-opening language reassessment remains the active master plan.

## Findings that can guide implementation now

1. Statements constrain joint economic histories without identifying their
   journals, contracts or future exposures. Preserve joint restrictions and
   persistent contract state, with journals as dated consequences. Every
   unresolved possibility need not become a separate explicit tree node.
2. Sharing states must preserve feasible actions, actor information and the
   joint continuation law needed by the query. The finite compression proof
   gives a conditional coupling bound. Small average cash error alone does
   not control default or policy changes at covenant thresholds.
3. Evidence intersection, Bayesian learning, multiple priors and source
   correction are different operations. Preserve persistent types through
   updates. Stagewise worst-case pasting can change admitted dependence;
   a nested risk objective can differ from the original objective.
4. Debt face, proceeds, discounting and recovery must satisfy one dated lender
   equation. The user's note has a local principal/face inconsistency: the
   example's lender break-even discrepancy is -44/101. The external note is
   unchanged; this is not a verified publisher erratum. Creditor participation,
   owner liquidity, fees and ownership need separate checks.
5. In the rate-reset interaction, both histories finish with cash8/assets112.
   The fixed-rate history borrows3; the floating-rate history fails the
   pre-financing covenant and raises equity6 with fee1. New owners acquire
   6/25. Book equity is9 versus12. Equal cash does not justify merging these
   histories. An omitted ownership update can leave the accounts balanced.
6. In the senior/junior example, owners prefer the risky policy. The consistent
   quote requires owner cash460/21, exceeding the available20. Funding is
   refused instead of manufacturing a balancing loan.
7. Silence may be informative; conditioning is not intervention. Learned
   solvers must use the intended conditional equation and derivative. A
   singleton-policy counterexample rejects the retained TC-VAE v1 transfer
   bound; published-edition correspondence remains unresolved.

## Evidence actually produced

| Evidence | Result | Scope |
|---|---|---|
| Local exact cases | 47 assertions pass | Rational arithmetic and finite model comparisons |
| Combined cases | 28 assertions pass | Revision, information, covenants, financing, dilution and risk definitions |
| Recent-method cases | 29 assertions pass | Source-transfer and policy-class counterexamples |
| Finite compression | 668 assertions pass | Discrete actions and three dates; restricted date/zero-cash policies, not all history-dependent policies |
| Persistent inference and financing | 350 assertions pass | Four priors ×27 observation sequences, correction replay and one-period financing feasibility |
| Typed runtime integration | 174 assertions pass across14 cases | I1/I2 through existing executor with native monetary fallback disabled; production code unchanged |
| ACTUS fixture arithmetic | 24 expected dated events match | Independent PAM01/PAM02 arithmetic, not execution of ACTUS |
| Original-code identity | 19 blobs verified | Eight Maliar/SMC and eleven TC-VAE blobs; static identity, not reproduction |
| Source records | 27 sources and27 claims | Reading scope and edition recorded individually; not25 whole-paper readings |
| Coverage | 61 forward records,72 appearances,29 backward leads,13 omission categories | Bounded screening, not exhaustive coverage |
| Manuscript preservation | 448 checks pass;222 predecessor sources protected | Twelve scholarly insertions,18 bibliography additions and one reversible running-header repair |

The first six rows contain **1,296 exact/local/runtime assertions**. The later
particle-MCMC diagnostic adds 24 assertions, for **1,320 total**. Counts
are explanatory bookkeeping; the derivations and discriminating cases supply
the evidence. Compression guarantees require uniform joint-kernel premises;
no learned uniform-error guarantee is established. Filter checks do not
identify any real company's prior or likelihood.

Source-reading.md, software-audit.md and the six source/citation/snowball/claim/
omission ledgers preserve technical scope. Hart–Moore1991 was inspected across
all62 scanned pages; the1994 edition is unmatched. Kara–Yüksel2020 was read at
Assumption1.1, Theorems4.2–4.4 and relevant proofs/appendix. Its robustness
result requires policy optimality from every initial state, not merely from
one initial prior.

Dated correction checks do not prove absence of errata. A retry overwrote two
initial metadata-search responses; their hashes remain but the bytes are lost.
Fresh exact-DOI responses are preserved under new names. The helper now archives
existing responses by hash; paper/code bytes were not affected. Successful
integrity checks do not erase this provenance limitation.

## Integrated documents and verification

The successor was rebased on independently advanced Version5.11, preserving
selected-source integration. Baseline PDF SHA256:
05ff78c88e9b3c1a1ec3cc87bc5d0df6b718ca1fd8a206c0003b65928e4b2a90.
The verifier reconstructs all222 predecessor source files by reversing declared
additions. Chapters3,5,8,9,11,19,25,26 receive the new arguments beside their
prerequisites. Main and standalone share the simulation chapter files.

| Final document | Pages | SHA256 |
|---|---:|---|
| Governing Version5.12 | 741 | 87da6f2a6bd7c56ea7718202047b9722b3de0b4e22e7f3aa4638d0a7fcb64622 |
| Simulation Version5.12 | 183 total /165 body | 63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5 |
| Supplement | 21 | fab1cd6367dede6aa8a362f19d9fdc0b9452be1572a916f231caa74a7b5900a9 |

All citations resolve; the supplement has24 bibliography entries. Main retains
five inherited underfull warnings and introduces none. Standalone/supplement
builds are clean. Author visual inspection covers all21 supplement pages,
49 selected standalone pages and71 selected main pages, including additions,
neighbors, contents and complete bibliographies. A Chapter18 running-header
collision was repaired and re-inspected. The whole741-page manuscript was not
re-reviewed. Human readability and independent acceptance remain pending.

## Decision and inference status

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain exact results | Equalities and finite comparisons pass | No failed reference assertion | Transfer beyond authored assumptions | Use scoped reference cases | General correctness |
| Retain scoped source findings | Technical anchors inspected | Invalid policy-class, rectangular-family and objective transfers rejected | Dependencies and editions | Named primary-source tasks | Exhaustive survey |
| Accept bounded runtime correspondence | I1/I2 reference/executor agree | Information, face/cash and ownership negative cases detected | Default, composition, source admission | Dated settlement methods | Production readiness |
| Keep ACTUS runtime unaccepted | Matched execution absent | Compatibility missing | Runtime behavior | Inspect matched core and execute conformance | External runtime passed |
| Advance documents to5.11 | Preservation, builds and scoped review pass | No new source/build failure | Whole-document and human acceptance | Keep not_ready and active master plan | Completed mission |
| Keep empirical defaults unpromoted | No empirical criterion evaluated | No identified target/evaluation | Forecast validity | Separately controlled E3 protocol | Forecast ranking |

| Inference status | Assessment |
|---|---|
| Hard veto evidence | Counterexamples reject specific false merges, anticipative policies, financing/objective conventions and altered probability families |
| Statistically supported ranking | None; no stochastic comparison was run |
| Descriptive-only evidence | Counts, coverage, pages and metadata visibility |
| Default readiness | No empirical, learned or production default promoted |
| Next evidence | Named source closure, broader composition and identified downstream evaluation with uncertainty |

## Particle-MCMC continuation

[Original proof dependency and exact counterexample](pmcmc-dependency.md) closes
the original-access/scoped target-proof task and adds two primary sources.
Refreshing a current likelihood estimate changes an exact target probability
from1/2 to10/19. All24 rational checks pass; the pinned PMMH rejection branch
retains its prior estimate. This note was completed after the frozen PDFs and
is linked separately; scalable inference and SMC2 adoption remain open.

## Remaining work

R1–R9 in remaining-work.md remain substantive: primary editions/dependencies;
competing methods; mixed/continuous compression with computable premises;
company likelihoods/policies; multiperiod, multicreditor and missed-payment/
default methods; matched external code; broader source-to-runtime composition;
and deferred empirical evaluation. R10's bounded manuscript integration and
alias update are complete; final verification passes 214 mechanical checks.

The existing67-mechanism index is extended by interactions and methods, not
replaced or declared exhaustive. S1–S5 remain partial, S6 held, E3 deferred,
and the governing document remains not_ready. No full MC requirement closes.

The final rebase preserves concurrent carried-claim work. Prior inspected page
bodies were pixel-compared: unchanged except covers/contents, re-inspected
directly. Eight added/context pages were also inspected; bibliography bodies
are identical after a two-page shift. See rebase-render-comparison.json.
