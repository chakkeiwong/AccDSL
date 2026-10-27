# Controlled expansion: review result and continuity

26 October 2026. The [design note](../../../docs/design/research/uncertainty-representation-20261026.md)
answers the tree/learning/explosion follow-up under the
[reviewed plan](../../../docs/plans/accounting-uncertainty-representation-20261026.md).

## Decisions

| Decision | Primary criterion | Veto / uncertainty | Next action | Not concluded |
|---|---|---|---|---|
| Retain joint constraints and share immutable records | Consistent with current language and storage semantics | General exact querying may still be exponential | Lazy evaluation of the existing shared IR | A graph solves worst-case complexity |
| Separate world, evidence and actor information | Current timing rules and inspected belief-update derivation | Actor knowledge and observation laws require explicit inputs | Add actor information/observation references | All managers share the analyst's uncertainty |
| Condition/refine rather than recreate a full tree | Explicit set and likelihood update semantics | No implicit probabilities; evidence revision differs from conjunction | Test persistent unknowns and revised observations | Every ambiguity must eventually resolve |
| Require compression to preserve learning | Local transition/observation sufficiency argument | Equal current or fixed-scenario reports are insufficient | Add observation-sensitive equivalence case | A general equivalence checker exists |
| Approximate only with explicit output meaning | Certified bounds, witnesses and statistical estimates distinguished | Rare modes, threshold crossings and resource stops remain visible | Query-specific exact/approximate result records | Sampling proves feasibility envelopes or completeness |

The supplied linear example is explanatory evidence, not a research experiment.
Command: `python3 data/accounting-master/uncertainty-representation-20261026/check_example.py`.
Its exact Fraction checks produce arithmetic.json. There are no random seeds
or empirical data. CPU scalar arithmetic only; no framework or GPU was used.
Python 3.11.15 is the previously identified system interpreter. The command is
expected to complete in less than a second; actual tool timing is not a
performance comparison. Git provenance is unavailable under the project's
unusable-.git instruction. No repository was initialised.

## Sources

All three primary PDFs were downloaded successfully from academic/author
hosts. source-manifest.json records byte identities and page counts. The
scanned Kaelbling preprint required rendered-page inspection; empty text
extraction was not mistaken for absent content. The retained images show
§§3.1–3.4 and the Bayes update on printed/PDF pp.9–12.

| Source | Classification / inspected support | Limits |
|---|---|---|
| Darwiche–Marquis, JAIR 17 (2002), pp.229–264 | DIRECT_METHOD; Definition 2.1, §2 decomposability/determinism, §§3–5 representation size and operations | Propositional compilation; no continuous AccDSL compiler implemented or selected |
| Kaelbling–Littman–Cassandra, 12 February 1998 preprint | DIRECT_METHOD; §§3.1–3.4, world/observation model, belief sufficiency and recursive update | Probabilistic model assumes specified transition/observation laws; does not justify weights for unweighted company histories |
| Doucet–Johansen, December 2008 v1.1 with March 2012 corrections | SURVEY_OR_TUTORIAL with inspected derivations; §§2.1–2.2, 3.3–3.6, 4.6 | Known model parameters in the stated setup; path degeneracy and finite-sample limits preclude treating particles as an exhaustive archive |

Acquisition routes (for provenance, not latest-version claims):

```text
https://www.cs.cmu.edu/afs/cs.cmu.edu/project/jair/pub/volume17/darwiche02a.pdf
https://www.cassandra.org/arc/papers/aij98.pdf
https://www.stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf
```

Online search/open calls returned no usable source payload this turn; direct
academic-source downloads supplied the inspected texts. No current citation
counts, venue metrics or exhaustive retraction/erratum search was completed.
Exact edition/correction information is identified rather than assuming the
filenames establish currency. No library or official solver code was adopted
or tested. Existing repo literature supports historical identification.

Backward/forward snowballing is not claimed complete. Important next leads
include dynamic probabilistic networks, certified state abstraction,
observation-preserving aggregation, static-parameter particle learning and
scenario reduction for multistage decisions. They would be needed for a
general algorithm selection or performance claim, which this note does not
make. The direct recommendations use only inspected definitions or explicit
local arguments.

## Red-team and acceptance

The main failure would be using graph sharing as a pretext to remove
dependencies, persistent uncertainty or information needed for future
decisions. The note distinguishes storage sharing from semantic merging and
approximation, makes actor information explicit and preserves an unfinished
frontier. Another risk is claiming an exact interval from arbitrary sample
endpoints: the example is exact because the function is affine and monotone
on the declared interval; this does not generalise to nonlinear cases.

Hard veto evidence concerns invalid compression assumptions, not a rejected
numerical candidate. No stochastic comparison occurred, no ranking is
statistically supported, no runtime default is promoted, and no whole mission
requirement closes. Runtime acceptance would require the examples specified
in the note, including information and resource-failure cases.

Current checkpoint at inspection: Version 4.42, 537 pages, not_ready. This
review leaves the manuscript, release hashes and existing master next-plan
unchanged. Additive requirements/checkpoint entries retain the recommendation.
Meaning and references were checked; human readability acceptance is not
asserted.
