# Particle-weight clarification in 5.54-R1

The protected successor explains when to retain a particle's old weight and
when ancestor selection already accounts for it. The original SIS display and
all citations survive. A new density-ratio derivation retains the ancestor
proposal correction, with a two-contract example showing the wrong answer from
double weighting. The complete approximation chapter also now names Dupačová
and coauthors where an ambiguous source reference obscured the assumptions.

Baseline: selected 5.54, whose complete 411-file package is preserved. The only
source changes are the approximation chapter, two cover versions and README.
All selected-reading/history additions and prior coupling/opening/EPS/edition
repairs remain. The candidate has 834 main pages and 263 total/242 body simulation
pages. It remains not_ready.

The exact checker previously passed 81 finite two-state cases and the stated
counterexample. This turn did not rerun that accepted writer. Direct Bayes and
correctly weighted enumeration yield (1/2,1/2); double parent weighting yields
(3/4,1/4), and omitting the correction under uniform ancestor proposals yields
(1/4,3/4). These compare deterministic density ratios relative to a supplied
empirical measure. They do not rank stochastic algorithms or establish an
exact finite-sample posterior.

Both final builds and all 425 source/build checks pass. The complete repaired
chapter was read in order; 19 rendered pages have exact final PDF/image bindings.
An attribution ambiguity found during attempt01 was repaired in attempt02;
old PDFs, source and build records are retained. The other chapter images match
those viewed in attempt01 exactly. No original display or citation was removed.

The 411-file package verifier passes. Each volume was rebuilt in a separate
/tmp copy: every page has the same normalized text, references are resolved,
and recorder files show no hidden input from the original worktree. The copy
uses the existing TeX environment; this is document reproduction, not a clean
installation test or full executable-evidence closure.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Accept the local clarification provisionally | Target/proposal derivation, retained exact checks and source conventions agree | No lost original equation/citation or observed target mismatch | Wider source corrections, model admission and finite-sample approximation | Preserve explicit resampling convention in any later implementation | General particle-filter accuracy, convergence or runtime defect |
| Select the checked manuscript successor | Source preservation, build, chapter rendering and relocated document reproduction pass | No package or parent mutation observed | Whole-document reading, executable closure and independent acceptance | Continue ordered review and current C1–C5 work | Release-ready design or whole-book acceptance |

The source reading distinguishes the inspected Doucet–Johansen tutorial edition
from later correction/code checks not completed here. Its algorithmic conventions
support this derivation; asymptotic statements are not newly promoted. The
strongest alternative failure is model misspecification despite perfect weight
algebra. State-space likelihood admission, support loss, genealogical collapse
and finite-sample uncertainty therefore retain separate treatment in the text.

The current master refresh preserves the active technical claim-review plan,
original acceptance populations and all frozen release hashes. It corrects the
stale docs index and records ordered author reading through protected baseline
page132, with a new question about finite-policy scope in section14.13.
All 53 obligations, six interactions, 46 operations and 18 packages remain open;
S1–S5 partial, S6 held and E3 deferred. No independent acceptance is claimed.
