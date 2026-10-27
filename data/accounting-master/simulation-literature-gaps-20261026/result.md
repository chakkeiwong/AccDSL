# What remains missing from the simulation literature review

26 October 2026. Assessment of the current AccDSL design and its simulation
volume; a source-research supplement, not a new manuscript release.

The most consequential gap is the argument connecting the literature to the
company we want to simulate. We have useful accounts of incomplete information,
accounting events, dynamic financing and sequential decisions. We have not yet
established when their combination preserves the feasible histories, information
and decisions of an issuer reconstructed from public reports. More references
will help only if we also establish those connections.

The starting evidence is Chapter 19 of the simulation volume, its 26-source
support map, the October research dossiers and the current S1 research record.
This assessment groups the unresolved work into nine families. It is a scoped
audit, not a claim that these are the last gaps that can be discovered. The
governing candidate remains Version 5.3, 717 pages, not_ready at assessment
entry. No manuscript or implementation release is promoted here.

## What changed in this assessment

Three primary texts are now retained under docs/papers, with original source
bytes and SHA-256 hashes in [source-recovery.json](source-recovery.json).

- **McCarthy (1982), the REA accounting model:** a new author-hosted route
  supplied the 25-page original article. The title and selected technical pages
  were inspected visually. The old access blocker is resolved. The scan has no
  usable text layer; complete technical reading and comparison with AccDSL
  remain open. Its recovery does not establish that REA solves reconstruction
  from financial statements.
- **Pflug and Pichler (2012), multistage distance:** an author-hosted manuscript
  supplies a better starting point for studying compression that respects
  information over time. Definition 5.1, Theorem 6.1 and its proof were inspected.
  The theorem assumes convex decisions and a convex loss with uniform Hölder
  continuity in uncertainty. A discrete financing choice or a discontinuous
  default indicator does not automatically meet those assumptions. This is a
  source for a transfer argument, not permission to compress arbitrary scenarios.
- **Epstein and Schneider (2007), learning under ambiguity:** the author-hosted
  published article separates an unknown persistent parameter from ambiguity
  about the likelihoods generating observations. Sections 3.1–3.3, Theorem 1
  and its appendix proof were inspected selectively. It helps formulate the
  distinction between learning a contract type and learning how disclosures
  are generated. Its memoryless data model, prior/likelihood restrictions and
  reevaluation rule are assumptions to assess, not AccDSL defaults.

The [reading record](source-reading.md) specifies the inspected pages and the
limits of each conclusion. No new solver, learned model or empirical result was
adopted. Earlier inaccessible-source and frozen manuscript records remain
historical evidence; dated supplements record the revised McCarthy status.

## The remaining gaps and how to close them

| Priority / ID | Missing argument or evidence | Work needed to close the stated gap |
|---|---|---|
| First / L01 | **Compression that preserves learning and decisions.** Similar statement totals or terminal distributions need not preserve what actors learn, their feasible policies, or default/covenant outcomes. | Read nested-distance and subsequent adapted-transport work, compare with the already inspected aggregation/scenario-reduction sources, and derive the result in our state, action and information notation. Separate exact aggregation, optimal-value bounds, implementable policy transfer and threshold accuracy. Test revealing versus uninformative signals and a covenant boundary before admitting an approximation. |
| First / L02 | **Persistent ambiguity and sequential updating.** A fixed but unknown loan type must not be redrawn each year. Bayesian probabilities, hard compatibility sets and multiple-prior preferences solve different problems. | Compare set refinement, Bayesian filtering, robust Bayesian updating and recursive ambiguity under explicit observation models. Inspect static-parameter particle methods and their failure modes. Establish what survives uninformative observations, what can be ruled out by evidence, and what merely receives smaller probability. Preserve actor-specific information and original cross-time restrictions. |
| First / L03 | **Financing, ownership, default and restructuring.** The local cash-proceeds/face-value repair is useful, but does not specify every refinancing, recovery, equity or creditor decision. | Resolve the retained Strebulaev–Whited equation conventions against a matched edition or correction, then expand the source treatment to debt maturity, seniority, collateral, refusal to refinance, issuance costs, conversion and dilution, bargaining and multi-creditor recovery. For each selected mechanism derive cash, promises, ownership and valuation together; compare constrained policy choices on identical facts. |
| Next / L04 | **Historical accounting and financial-planning alternatives.** Francis–Rowell remains technically inaccessible; Gentry's referenced derivation and 1974/1979 correspondence remain unresolved; McCarthy is newly available but incompletely read. | Finish REA reading and a fair same-task comparison. Seek a legal institutional or author copy of Francis–Rowell using the verified identity. Obtain the missing Gentry derivation and compare the working paper with the journal article. Record equations, initialization, financing closure and empirical limits rather than treating unavailable competitors as inferior. |
| Next / L05 | **ACTUS specification–dictionary–runtime correspondence.** Service-code inspection and a requested core dependency do not establish a compatible executable contract model. | Retain a mutually compatible specification, dictionary, core revision and dependency lock. Trace each adopted event through schedules, state transition and payoff code. Compare event order, dates, day counts, business-day rules, signs, defaults and risk observations against hand-derived cases. Verify explicit horizon and observation cutoffs. |
| Next / L06 | **Learned-solver paper–code–target correspondence.** A useful economic solver paper does not establish that its code solves the risky-debt/equity problem in the supplied note. | Verify author/paper links and pin official code for each proposed method, including Maliar and the newer financing solver. Audit states, equations, conditional expectations, sampling, differentiation, constraints and the joint price/value solution. Only then design a target-specific numerical protocol against exact or well-checked classical cases. |
| Next / L07 | **Disclosure, missingness and causal interpretation.** A report can be selectively disclosed, aggregated, delayed or revised; an intervention need not preserve an empirically fitted response rule. | Extend primary-source reading on disclosure incentives, missing-data mechanisms and causal identification. Specify what the analyst and management know and when. Compare exogenous observation models with selective disclosure. State which shocks are mechanical stresses, conditional forecasts or identified causal interventions. |
| Later, with design now / L08 | **Company policy estimation and empirical evaluation.** Public accounting identities alone do not identify management's investment, financing or payout policy. | Survey structural estimation and validation using the existing corporate-finance/microsimulation seeds. Map observable quantities to policy parameters and identify remaining observational equivalence. Specify vintage-correct estimation and evaluation, credible baselines, uncertainty and tail/calibration criteria. Keep actual predictive runs deferred under the current program. |
| Throughout / L09 | **Survey coverage, versions, corrections and contrary results.** The citation ledger does not prove systematic comparison of all material alternatives. | Screen backward and forward citations around each decision-relevant claim; retain source-specific inclusion/exclusion reasons and searches with dates. Reconcile working papers, journal versions, code and corrections. Preserve negative results and sources that narrow a proposed method's applicability. Close a declared search scope, not an assertion of universal completeness. |

L01–L03 come first because their answers can change the meaning of the simulator.
L04–L06 can proceed independently where public sources are available. L07
constrains L02 and L08: learning and policy estimation can be misleading if the
process producing the observations is wrong. L09 accompanies every work unit.
The machine-readable [gap register](gaps.json) records exact existing anchors,
source leads, proposed checks and closure criteria for each family.

### Why the compression gap deserves first attention

The proposed design already avoids allocating a separate full company for every
possibility. It retains joint constraints, shares common histories and splits
only where a query requires it. That controls representation cost without
asserting that all queries become easy.

Approximate merging asks a harder question. Two models can have the same final
cash distribution while one reveals a funding shortfall before an investment
decision and the other reveals it afterwards. A method that preserves only
final cash cannot establish that the investment decision remains equivalent.
This is a proposed diagnostic construction, not a newly executed AccDSL test.

Pflug–Pichler's conditional coupling constraints in Definition 5.1 address
information as well as random outcomes. The proof of Theorem 6.1 transfers a
policy using conditional expectation and then uses convexity. An average of
two admissible discrete actions need not be an admissible financing action;
the proof therefore cannot simply be reused for a hybrid company model.
Moreover, an optimal-value bound is not automatically a bound on a particular
deployed policy's regret or on default probability. We need to state which
quantity an approximation preserves and prove or test that claim separately.

A useful first research deliverable is a finite case with the same opening
statements and final unconditional outcomes but different signal timing,
followed by a covenant case at and around the exact boundary. Compare an exact
enumeration with the proposed compressed representation. Declare the permitted
policies and information before comparing results. Larger performance studies
should follow only after this semantic comparison is sound.

### Why learning needs its own comparison

Three updates can look superficially similar but mean different things. Hard
evidence can eliminate an incompatible historical contract. A Bayesian model
can change its probability after a noisy signal. A multiple-prior model can
change a set of distributions used to evaluate decisions. We should not treat
their surviving representations as interchangeable or count them to manufacture
probabilities.

In Epstein–Schneider, equations (5)–(6) combine Bayesian updating within a
theory with likelihood-based reevaluation of theories. A theory disregarded
at one date may be reconsidered later. That differs from permanently excluding
a factually impossible contract. The paper's long-run result also requires
identification and support conditions; it does not show that every uncertainty
in public financial reports disappears with more observations. Future
likelihood ambiguity can persist even when its parameter concentrates.

The first AccDSL comparison should therefore include a revealing signal, an
uninformative signal, a noisy contradictory signal, a corrected disclosure and
two actors with different knowledge. It must distinguish revision of evidence
from ordinary conditioning and numerical loss of a particle from elimination
of an economic possibility. These are proposed cases; no new reference results
are claimed here.

## Specific source blockers

**Francis–Rowell (1978):** the title, authors and DOI 10.2307/3664904 are
confirmed in retained metadata. A newly tried author-associated download
returned HTTP 403. Earlier failed routes remain recorded. Full technical text
is still needed; library access or a legal author manuscript is the next route.
No purchase or outreach was undertaken.

**Gentry:** retain the 1974 working paper as 1974. The 1979 EJOR article has
DOI 10.1016/0377-2217(79)90027-4, but its derivation and equivalence to the
working paper have not been checked. A missing referenced appendix is a
specific mathematical gap, not a generic request to collect more references.

**Strebulaev–Whited:** retained metadata identifies published DOI
10.1561/0500000035 and a publisher route; the new PDF request returned HTTP 403.
The local source-convention derivation remains separate from correction status.
Empty correction/relation fields in Crossref do not establish that no erratum
exists. Exact publisher/author correspondence remains to be checked.

**Learned methods and ACTUS:** discovery of a repository, commit or current
download page does not establish a matched release. The evidence directory
retains a Maliar-related repository commit response and the official ACTUS
technical-specification page. Code linkage and runtime compatibility remain
open. Existing selected ACTUS service inspection remains credited.

## A practical way to close the gaps

Use one bounded research note per consequential claim. Each note should retain
the correct source version, inspect the technical section and relevant proof
or appendix, reproduce the necessary relation in AccDSL notation, and state
which source assumptions apply. Where official code exists and reuse is
proposed, inspect it alongside the paper. Finish with a small case that would
expose the most plausible wrong transfer and update the manuscript only to the
extent that the evidence supports it.

For L01, the deliverable is an information-preserving compression argument and
its failure cases. For L02, it is a comparison of updating semantics with fixed
latent contracts. For L03, it is a dated financing and recovery model whose
cash flows, liabilities and ownership agree. These are substantial technical
deliverables even if each uses only a few carefully read papers.

A paper download closes **access**. Reading closes a stated **source question**.
A derivation and discriminating check can support a specified **transfer**.
Neither alone validates the combined company simulator. Rejected transfers
should remain documented with the precise failed assumption and the narrower
use, if any, that remains viable.

## What citations alone cannot fix

Actual accounting authority, company contracts, reporting dates, ownership
rights, tax facts and management information must come from suitable evidence.
Runtime conformance requires implementation checks. Predictive calibration
requires appropriately dated data and outcomes. These obligations interact
with the literature review but do not disappear when the bibliography grows.
The existing 67 failure mechanisms and 169 exact teaching checks are useful
bounded evidence, not proof that every scenario failure has been covered.

No whole mission requirement closes in this assessment. The immediate result
is a repaired access status, two technically useful new sources, and an
ordered research program with explicit completion evidence. The current
implementation queue and manuscript bytes are preserved.

## Evidence and verification

- [Existing simulation source support](../simulation-monograph-20261026/source-support.json)
  and [technical reading](../simulation-monograph-20261026/source-reading.md).
- [Chapter 19 source synthesis](../../../docs/design/proposal/manuscript-simulation-foundations-20261026/simulation/19-literature.tex).
- [Existing uncertainty representation argument](../../../docs/design/research/uncertainty-representation-20261026.md)
  and [history/financing review](../../../docs/design/research/simulation-history-financing-review-20261026.md).
- [ACTUS boundary audit](../../../docs/design/research/actus-interface-boundary-20261023.md)
  and [financial-statement simulator survey](../../../docs/design/research/financial-statement-simulator-survey-20261023.md).
- [Current S1 scope at assessment entry](../insurance-identity-integration-20261026/remaining-work.md)
  retains its historical McCarthy blocker; the dated supplement here supersedes
  that access status only.
- [Source recovery](source-recovery.json), [reading scope](source-reading.md),
  [gap register](gaps.json) and [verification](verification.json).

Author review is provisional. No independent reader acceptance, source-wide
theorem certification, production conformance or predictive validation is
claimed. Verification checks file integrity and the assessment's references;
it is not evidence that the open research questions have been solved.
