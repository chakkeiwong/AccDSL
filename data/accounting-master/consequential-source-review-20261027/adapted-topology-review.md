# Adapted topology: the checked implication and proof dependencies

27 October 2026. MC13–18/29–35; C3/C5. Retained published source:
docs/papers/All adapted topologies are equal Backhoff-Veraguas (2020).pdf,
SHA256 72040d8c94c9a2b123946789cc9dc2c438e658c997417c458b8b8d347188f5a7,
DOI10.1007/s00440-020-00993-8, PTRF178:1125–1172. Physical1–48 have now
been inspected, including the full article proof sections and references.
This expands the earlier bounded reading; it does not certify every external
dependency. Physical34 and45 were also rendered and visually checked.

Theorem1.2 concerns finite discrete time and Polish state spaces with bounded
compatible metrics. It identifies the adapted Wasserstein, symmetrized causal
Wasserstein, information, extended weak and optimal-stopping topologies. The
stopping costs in that statement are bounded, continuous and adapted.
Theorem1.3 and Lemma1.4 extend to unbounded metrics using finite pth moments,
moment convergence and the stated growth conditions. Neither theorem supplies
equal metric constants, continuity of discontinuous default indicators, small
state representations or identification from company reports.

## Proof chain actually inspected

Section2 defines disintegration and integration maps. Disintegration is
measurable but generally not weakly continuous. Section3, Lemmas3.1–3.9,
constructs the maps between nested distributions and information laws using
integration and compatible graph-supported measures. The hard continuity step
is Lemma3.8. Its proof in3.2 uses Lemma3.10, reproduced from Eder[24],
Lemma4.2. Lemma3.10 controls a measure-dependent modulus near a graph law;
it is not a global uniform Lipschitz constant.

Section4 extends two-period causal costs to nested distributions. Lemmas4.9,
4.11–4.15 and Theorems4.18/4.22 establish the metric and topology argument;
Theorem4.23 passes to finite N. The compactness step uses Lemma1.7/Eder[24],
Lemma3.3. Relative compactness of integrated laws is not continuity of the
disintegration map, and the space of graph laws need not be closed in the
larger nested space. Section5's Aldous equivalence additionally uses Eder[24],
Lemma4.1 for composition with a graph-supported measure. Section6 uses
ordinary Wasserstein moment convergence and the same compactness dependency.

Section7 transfers stopping rules through causal couplings. Lemma7.1 bounds
the value difference by the expected maximum reward difference; its proof
averages auxiliary randomized stopping rules and compares their average with
the pure stopping infimum. Remark7.2 gives a c SCW1 bound when every reward
has the stated common Lipschitz constant. Lemmas7.3–7.5 construct
convergence-determining tests. These results do not grant randomization or
extra observations to an issuer's chosen policy class.

## Two literal proof details

On physical34/printed1158, Lemma4.13's sketch displays C with rho and Wp
without powers, although equation25 optimizes rho^p+Wp^p. These are different
objectives for general p. The corresponding local expression must retain both
powers. The powered expression is convex in the measure argument; a general
unpowered Wp expression cannot silently replace it. The source also cites
weak-transport[9], Theorem1.2. This inspection has not independently completed
that external attainment proof or its moment/compactness requirements.

On physical45/printed1169, Lemma7.5 chooses m bounding |f| and |h|, then sets
all unwanted stopping costs to m+1. Its terminal cost is f*h, whose bound can
be m^2. The displayed Snell-envelope equality is wrong for an arbitrary m
satisfying only the printed bounds. The finite diagnostic below tests this
specific equality. The local repair is to choose M bounding both |f| and
|f*h|, then use M+1 at every unwanted stopping date. Bounded f and h always
permit that choice. This is a repair of the proof construction, not evidence
against the stated topology theorem.

## Exact diagnostic contract

Question: does the printed stopping construction represent its proposed test
for every bound m allowed by the printed wording? Comparator: the two-date
minimum displayed in Lemma7.5. Criterion: exact equality with an independent
backward stopping calculation on the finite tree. A mismatch vetoes that
literal construction; it does not veto the research direction. Source hash and
finite-tree validity are hard vetoes. Floating point, sampled paths, rankings
and performance play no role.

Use dates1,2,3, f=3, and two equally likely branches. At date2 the branch is
observed; terminal h is3 or−6/5. At date1 both branches remain possible.
Thus m=3 is a permitted bound. Compare unwanted cost4 with repaired cost10.
The exact source identity, inputs, backward values and decisions are preserved
by verify_topology_stopping.py in topology-stopping-verification.json. This
is a local proof diagnostic, not a numerical experiment or empirical study.

## Current manuscript consequence

The current27-claim ledger does not directly cite this article. C18 in
simulation/lit-08-compression-3.tex instead uses Beiglböck–Pflügl–Schrott,
Definitions2.6–2.8, Proposition3.6, Theorem3.9, Theorem5.4 and Remark5.7.
Its current paragraph explicitly retains potentially measure-valued state,
randomization and stochastic-basis restrictions. C03 separately retains the
convexity, strategy-transfer and continuous-time metric limits of its actual
sources. No new guarantee or change to those paragraphs follows from this
secondary-source reading. Their exact implication review remains separate.

| Decision | Primary criterion | Veto / uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|
| Retain finite-time topological scope | Statement and article proof chain inspected; named Eder dependencies inspected | Weak-transport attainment and standard external dependencies remain scoped | Preserve source edition and exact assumptions | Equal constants or threshold continuity |
| Repair literal stopping construction locally | Exact comparison completed: printed1/5 differs from27/10; repaired27/10 equals27/10 | Printed m bound need not dominate f*h | Retain the existing calculation without rerunning its writer | Theorem falsification or issuer-policy validity |
| Preserve current manuscript | No direct new implication currently promoted | C18/C03 have their own source obligations | Review their actual sources and sentences | Complete source, manuscript or independent acceptance |

Correction metadata is reused from the dated26October exact source-support
record: OpenAlex is_retracted=false and no update notice in inspected Crossref
fields. Those bounded observations do not establish exhaustive correction
clearance. No associated executable method is adopted; author-code inspection
for this theorem-only article is not a substitute for inspecting its proofs.

## Completed diagnostic and dependency continuation

topology-stopping-verification.json records the completed exact check. With
m=3 and unwanted cost4, backward induction gives1/5, while the printed
two-date expression gives27/10. With M=9 and unwanted cost10, both give27/10.
The literal construction is wrong for this permitted m; the strengthened bound
repairs this example and the unwanted-date exclusion argument. The calculation
uses exact fractions and all branches, with no sampling or statistical ranking.
Its successful one-shot writer has not been rerun.

eder-dependency-review.md records the completed14-page reading of
arXiv1905.00856v1, exact hash and bounded metadata check. It inspects
Lemma3.3, Theorem4.1 and Lemma4.2 with their local proof dependencies,
including a missing-bar repair in Lemma3.4. The weak-transport attainment
source used by Lemma4.13 remains a separate unread dependency. These findings
limit proof certification; they do not create a global continuation blocker.
