# Make particle-weight timing explicit

MC12/14/18/26/29/30/32–34; C3/C5. Reader: an accounting researcher or
implementer who knows conditional probability and wants to preserve an admitted
history distribution when resampling numerical particles. This is a bounded
repair of section 9.3, within the now-read approximation chapter (R2 physical
pages 82–92). Baseline source is the selected 5.53-R1
simulation/09-approximation.tex; both protected parent versions are retained.

The current equation is correct for sequential importance sampling without
intervening resampling. Calling it a generic incremental weight without stating
that convention can cause a reader to multiply a parent's weight twice after
resampling. The source algorithm distinguishes these cases explicitly. Preserve
the equation and identify its convention; derive the ancestor-proposal ratio
for the resampled case and show a small exact counterexample. Do not claim an
existing AccDSL runtime has this defect: this unit concerns exposition.

Question: does the proposed explanation make the target, ancestor selection,
weight reset and retained contract identity unambiguous? Comparator: exact
Bayes update for two persistent types, with unequal prior weights and opposing
likelihoods. Primary criterion: correct SIS, ordinary resampling and a different
ancestor proposal produce the same exact target under full finite summation;
double-counting a parent weight and omitting a required proposal ratio produce
the predicted different distributions. These are deterministic identities,
not assertions about finite stochastic sample accuracy or algorithm superiority.

Promotion vetoes: a wrong target/proposal ratio, an unsupported source equation,
lost original equation/citation, or confusion between particle copying and a
changed contract. Continuation veto: corrupted baseline or source. A failed
arithmetic case triggers repair of the explanation. Counts, sample size and
rendered layout are explanatory; successful compilation cannot certify the
statistical method. Artifact: exact-check.json, source-reading.md, source-delta
and a protected reader-facing replacement for later successor integration.

The source is the locally retained Doucet and Johansen tutorial, version 1.1,
December 2008 with March 2012 typographical corrections. Inspect its section
3.3 equations (29)–(30), sections 3.4–3.5 including adaptive resampling, and
the immediately relevant support/model definitions. Keep the edition and later
correction-check limits explicit. No original-code algorithm is being promoted;
the local exact checker is an arithmetic illustration of the density ratio.

Skeptical audit: uniform prior weights would conceal double weighting, so use
3/4 and 1/4. A random resampling draw would mix Monte Carlo variation with the
algebraic issue, so enumerate the proposal support exactly and separately show
one stated four-particle allocation. Treat the supplied finite empirical measure
as the target of this one update; it is not the exact original filtering law.
Require proposal support wherever the target mass is positive. Preserve all
current source/financing additions when integrating later. The plan passes
these scoped checks. CPU-only rational arithmetic; no seeds or training,
dependencies, external engagement or default-policy changes are required.

The reader enters knowing that a fixed unknown contract persists and particles
may be copied. The new question is how copying changes the weight calculation.
The density-ratio derivation shows that ancestor selection already represents
the old weight; the two-type example makes double counting visible. The exit
question is whether adequate ancestor diversity survives, answered by the
following existing section. Full manuscript and independent-reader acceptance
remain open.

## Protected integration after the exact check

The 81 finite cases and stated two-type counterexample pass. The live 5.54
candidate has now integrated the selected-source/history adapter and preserves
every 5.53-R1 correction byte-for-byte in the affected simulation files. Use
its exact 411-file package as the successor baseline. Prepare
docs/design/proposal/manuscript-filter-v554r1-20261027/ with only the reviewed
section replacement, cover versions and README explanation changed. Preserve
all old displays and citations and all other package files, including the
source/history reference. Do not add an unreviewed numerical implementation.

Build both volumes, inspect the complete repaired approximation chapter and
affected navigation, verify the package and reproduce it from a separate /tmp
copy. Select only if the live links still select the pinned 5.54 parent, using
exact pre-write guards and preserving whichever technical plan has advanced.
The skeletal whole-document node rubric remains incomplete; chapter-level
regression is not whole-Part or whole-book acceptance. This bounded integration
passes the skeptical audit because it corrects a diagnosed implementer ambiguity
without replacing the filtering target, source edition or existing engine.

## Rendered regression repair, 27 October 2026

The complete chapter read found an ambiguous attribution in section 9.12:
"The source's Section 2" follows discussion of three separate papers. Name
Dupačová and coauthors explicitly and retain the Section 2/Remark 2.2 anchors.
This is a local attribution repair, not a new theorem or support claim. Preserve
build-01 PDFs and source before editing; use build-02 and distinct verification
records. Recheck the chapter and navigation against the final PDF hashes.
The amended plan passes: the exact existing source is identified, no equation
or citation is removed, and the build result is not treated as source acceptance.
