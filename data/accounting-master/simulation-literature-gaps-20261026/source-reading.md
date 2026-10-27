# Source reading and recovery scope

26 October 2026. This record distinguishes retrieval, targeted technical
inspection and an adopted method. Source bytes, URLs, identifiers and hashes
are recorded in [source-recovery.json](source-recovery.json). No paper-wide
certification or method implementation follows from this bounded assessment.

## McCarthy (1982)

William E. McCarthy, The REA Accounting Model: A Generalized Framework for
Accounting Systems in a Shared Data Environment, The Accounting Review,
LVII(3), July 1982, pp. 554–578. The title page confirms this identity. The
author website supplies the retained 25-page scan. The old metadata DOI was
not independently verified and is not used to establish identity here.

Physical pages 1, 2, 6, 10, 15, 20 and 25 were inspected as rendered images.
They include the article identity; the discussion of monetary, aggregation
and integration limitations; the introduction of REA; agents and control
relationships; event imbalance and claims; event combinations; and references.
This is selected-page inspection, not a full technical review. In particular,
there is no inspected proof here that an REA representation uniquely recovers
a company's history or preserves every future scenario outcome.

The scan contains no usable text layer. The local text/mccarthy1982.txt file
contains page markers rather than extracted article prose; it must not be
used as if it were a searchable full text. Images remain available for reading.
No OCR installation was performed. Next: read all substantive pages, map the
event/resource/agent relations to the actual AccDSL representation, and compare
the same reconstruction and simulation tasks. The access blocker alone closes.

## Pflug and Pichler (2012)

Georg Ch. Pflug and Alois Pichler, A Distance for Multistage Stochastic
Optimization Models, DOI 10.1137/110825054. The retained author-hosted
23-page manuscript is associated with the 2012 publication. It is not claimed
byte-identical to the publisher edition. The author publication page and
Crossref response are retained.

Targeted reading covered physical pages 1–13, 15 and 22–23 across this work
unit: the setup, increasing information, multistage distance, stability
argument and relevant appendix on conditional structure. Theorem 6.1 and
its proof on pages 10–11 were also inspected as rendered pages. This is not
a complete review of every algorithm, example or numerical result.

Definition 5.1, page 6, equation (5.2), restricts both conditional marginals
of the joint coupling relative to the two filtrations. It therefore encodes
more than terminal outcomes. Theorem 6.1, page 10, concerns the optimal value
in equation (6.1), with a convex decision set, a loss convex in the decision,
and uniform Hölder continuity in the random path. Its conclusion bounds the
optimal-value difference by the Hölder constant times the nested distance
to the Hölder exponent, for distance order at least one.

The proof on pages 10–11 constructs a transferred decision by conditional
expectation, obtains admissible information dependence from the coupling
constraints, uses Jensen's inequality, and applies epsilon-optimality and
symmetry. These steps explain why convexity matters. A financing action set
containing only discrete issue/refuse/default choices cannot automatically
use the same conditional-average construction. A default indicator need not
meet the continuity condition. Even an applicable optimal-value bound does
not by itself give default-probability accuracy or the regret of a particular
implemented policy.

Next: state the actual company decision class and observation process, map
the assumptions, and derive the narrower valid result or reject that transfer.
Read subsequent adapted-transport/decision-stability work before choosing a
compression method. No new theorem for AccDSL is proved here, and no numerical
claim from this paper is promoted. Correction status and official-code
correspondence remain unchecked beyond retained metadata fields.

## Epstein and Schneider (2007)

Larry G. Epstein and Martin Schneider, Learning Under Ambiguity, Review of
Economic Studies 74, 1275–1303, DOI 10.1111/j.1467-937X.2007.00464.x. The
29-page author-hosted PDF carries the published article's pagination. The
earlier SSRN version has a distinct identifier and is not conflated with it.

Targeted reading included the introduction; physical pages 6–10 (printed
1280–1284, Sections 3.1–3.3); pages 14–16 (printed 1288–1290, long-run
beliefs); and appendix pages 24–28 (printed 1298–1302), including the proof
of Theorem 1. The empirical portfolio exercise in Section 5 was not reviewed
in full and is not used as AccDSL evidence. Reading the proof structure is
not a claim that every displayed algebraic line has been independently
verified or that the source is free of typographical errors.

The model uses a finite period state space, parameter priors, a set of
likelihoods, compactness/full-support conditions and a memoryless mechanism.
Equation (5), printed p. 1283, gives Bayesian updating within a particular
prior/likelihood theory. Equation (6) reevaluates theories by relative
likelihood, with a parameter alpha controlling retention. The text explicitly
permits a previously disregarded theory to re-enter after later evidence.
This rule differs from hard logical exclusion by contradictory source facts.
Neither the reevaluation parameter nor the assumed likelihood set is a
default for AccDSL.

Theorem 1, printed p. 1288, assumes a finite parameter space, convergence of
empirical frequencies, a unique maximizer of the specified limiting log-data
density, prior support, and a lower bound on positive prior mass at that
maximizer. The proof on printed pp. 1300–1302 uses likelihood separation and
the retained-theory criterion. The discussion on p. 1289 distinguishes
concentration on a parameter from remaining ambiguity about future signals.
It does not guarantee that an arbitrary public-disclosure model identifies
the true contract, especially when the observation or identification
assumptions fail. Maximizing the specified limiting criterion must not be
silently equated to recovering an unrestricted true economic state.

Next: compare hard compatibility, a single posterior and sets of posteriors
using fixed contract types and explicitly informative or uninformative
signals. Review the observation model and the policy preference separately.
No robust filter or recursive decision rule is adopted in this work unit.

## Other retained leads and failed retrievals

- Francis–Rowell: Crossref metadata confirms the specific 1978 Financial
  Management article and DOI 10.2307/3664904. The new author-associated
  ResearchGate PDF route returned HTTP 403. This attempt adds no technical
  text; earlier routes remain in the existing survey.
- Gentry: metadata confirms the 1979 EJOR identity and DOI. The existing
  retained source remains the 1974 working paper. Missing derivation and
  journal-version correspondence remain open.
- Strebulaev–Whited: metadata supplies the published DOI 10.1561/0500000035
  and an Emerald publisher route, distinct from SSRN 10.2139/ssrn.2091854.
  The new PDF request returned HTTP 403. Existing local equation inspection
  remains credited; a correction/edition conclusion does not follow.
- ACTUS: the official technical-specification page is retained and links to
  the dictionary and organization repositories. Its linked specification
  version was not matched to dictionary/core bytes in this assessment.
- Maliar-related repository: the retained GitHub response identifies commit
  4f086d9a2586969406a00f88d3b036ba1413b8d3 and tree
  130be64115b03d32ffc458d0b5bd30bf0ea3e9f3. The paper/author linkage and
  technical contents were not audited here. A commit response is not a local
  implementation copy, and Krusell–Smith evidence would not automatically
  validate the risky-debt/equity target.
- Warren–Shelton (1971), A Simultaneous Equation Approach to Financial
  Planning, DOI 10.1111/j.1540-6261.1971.tb01753.x, appeared as a metadata
  lead. It is a candidate historical comparison only; its technical body was
  not inspected.

Crossref responses for the five queried titles did not expose correction
relations in the returned fields. This is a limited metadata finding, not
comprehensive erratum or retraction clearance. Built-in web retrieval returned
no usable results in this work unit; retained author, publisher and API
responses were obtained through direct retrieval. No web citation identifiers
are invented. No inaccessible source is ranked as inferior on that basis.
