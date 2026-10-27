# Source reading and version boundaries

26 October 2026. This record supplements the source-specific inspection already
retained in `source-support.json`; it does not claim a fresh complete reading of
every old paper. All 26 sources cited in the new chapters have a retained local
copy and refreshed citation locations. The inherited bibliography remains an
exact byte prefix; the combined database contains 143 entries, of which 141 are
cited in the combined text. Two inherited FFIEC entries remain in the database
without a citation rather than being deleted.

## Scenario reduction

Dupačová, Gröwe-Kuska and Römisch, *Scenario Reduction in Stochastic Programming:
An Approach Using Probability Metrics*, retained 20-page 2000 preprint,
repository DOI 10.18452/8244. Repository discovery responses are retained in
`sources/`. Text extraction is illegible, so all twenty pages were inspected
as rendered images during drafting. Inspection covered Section 2, Theorem 2.1
and its proof, conditions C1–C4, Remark 2.2 and the quoted Theorem 2.3; Section 3,
Theorems 3.1, 3.2 and 3.5 and proofs, Algorithms 3.6 and 3.7; Section 4's experiment,
tables and metric; and the references. This copy has no appendix.

The source supports optimal probability redistribution for a fixed retained
subset under its admitted metric/cost assumptions. Choosing that subset is a
separate problem, and the reported sequential algorithms are heuristics. Its
stochastic-program stability results have solution, integrability and regularity
conditions. External theorem dependencies were not independently reproved. The
source's reported C implementation was not obtained or executed, and the later
journal version was not matched. No company default-accuracy or performance
claim is transferred from its electrical-load experiment.

Chapter 9's expected-output Lipschitz bound, uniform-policy-error regret bound
and discontinuous-threshold counterexample are local derivations. They are
identified as such in the text. The three-state redistribution example and
threshold construction are included in the exact arithmetic record. Preserving
intermediate actor information remains a distinct requirement.

## Aggregation and dynamic ambiguity

Givan, Dean and Greig: retained 62-page author-hosted manuscript of the 2003
article. Sections 3.1–3.3 and 4.1–4.3 and appendix Theorems 4–7 were inspected,
including the full proof of Theorem 7 and its supporting lemmas. Fixed-action
sequence equivalence does not supply the policy equivalence needed when choices
respond to intermediate information. The MDP bisimulation result is distinguished
from Chapter 8's local finite-horizon extension that preserves the joint
successor, observation and requested-output law. No general financial-state
minimizer has been implemented or proved tractable.

Epstein and Schneider: September 2002 author preprint of *Recursive
Multiple-Priors*. The domain, axioms, Definition 3.1, Theorem 3.2 and relevant
appendix proof structure were inspected. Rectangularity is relative to the
specified information filtration and probability family. It does not license
redrawing a fixed unknown contract each period. The manuscript's persistent-type
counterexample is a local construction. Later-version identity and every external
theorem dependency are not independently established by this record.

## Financing and prior technical reviews

The supplied Chak Wong lecture is retained unchanged in `sources/`; its digest
matches the original MathDevMCP source. Chapter 5 cites both that note and the
retained Strebulaev–Whited December 2012 source. Equations 3.26–3.28, including
the printed equation 3.27, were checked in the earlier financing review. The
face/proceeds mismatch is exposed by a positive-recovery calculation; it is not
attributed solely to a transcription error in the lecture. Current publisher
erratum status remains unresolved. The coherent face convention, its recovery
multiplier and the fully solved finite model are derived in the new text.

The source-specific records for Maliar–Maliar–Winant, Duarte–Fonseca, Giacomini–
Kitagawa, Shahnazarian, Caiani and Pierson reuse the inspected method, equation,
appendix and selected official-code anchors in the retained financing review.
Julia Fonseca's name was corrected against the primary NBER source. Learned
solver code equivalence, convergence and target-specific numerical performance
have not been established. ACTUS retains its separate specification/dictionary/
runtime correspondence gap. The earlier Gentry appendix/version and Francis–
Rowell full-text gaps remain open; unsupported derivations are not imported.

The precise record for each citation is in `source-support.json`. Earlier source
and code reviews remain at `docs/design/research/simulation-history-financing-
review-20261026.md`, `docs/design/research/uncertainty-representation-20261026.md`,
and the evidence paths named by each source record.

## Literature audit continuity

The six existing research ledgers under `docs/design/research/` remain intact:
`source-support.json`, `citation-venue.json`, `backward-snowball.json`,
`forward-snowball.json`, `claim-support.json`, and `omissions.json`. This task's
source support and citation maps supplement them with the exact new chapter
uses and recovered versions. Citation counts are dated discovery metadata and
never evidence of correctness; uncollected counts and venue metrics are unknown.

The new recovery does not establish exhaustive backward or forward screening.
Remaining research includes adaptive scenario-reduction guarantees, robust
filtering of persistent unidentified types, strategic disclosure and broader
restructuring models. The failure catalogue and literature synthesis expressly
remain extensible. The uninspected Francis–Rowell lead is a source gap, not a
rejected competitor. A professional referral is not proposed; these remain
internal source and implementation tasks.
