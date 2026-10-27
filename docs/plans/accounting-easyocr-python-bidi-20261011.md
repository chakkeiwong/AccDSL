# EasyOCR's unpinned bidirectional-text dependency

11 October 2026. E14/C07; MC23/30/31/34/35. Continue internal proposal
preparation. No installation, model execution or distribution is authorised.

## Research intent and evidence contract

Question: what source, licence and version constraints apply to the
`python-bidi` package used by the inspected EasyOCR 1.7.2 Reader path?
The comparator is the closed EasyOCR source/asset and checkpoint-rights units.
Their exact `requirements.txt` says only `python-bidi`, while the Reader imports
`bidi.get_display`; they do not specify a resolved release or its terms.

Select one current non-yanked stable PyPI release as an *inspection candidate*,
not a package lock or project default. Preserve exact PyPI response, candidate
version, distribution filename/hash, package-declared licence metadata and
source licence text. The primary pass is an authenticated edition-specific
source/terms record and a precise statement of what remains unproved for an
actual dependency resolution. The hard veto is wrong package or version,
hash mismatch, absent inspectable licence body, or treating issue allegations
as authoritative terms. Metadata alone is a discovery signal; release and
source bytes are primary evidence. A failed source candidate does not veto
continued E14 work.

The result must distinguish copyright/licence terms, compatibility of the
imported API, and a legal distribution interpretation. Inspecting source can
identify the first; it cannot establish installed compatibility, transitive
resolution, all model rights or legal clearance. No runtime performance,
accuracy or default-policy claim follows. Retain result, exact bytes/hashes,
bounded checks, manifest and next frontier in
data/accounting-master/easyocr-python-bidi-20261011/.

## Skeptical default and plan audit

EasyOCR's unpinned dependency is inherited, not a reviewed default. Selecting
the latest release is a convenient current hypothesis; it could differ from
an installer-chosen historical/compatible version. Record the chosen version
as a candidate, inspect its declared Python constraints, and leave the lock
open. PyPI `license` metadata can be stale or ambiguous; compare the source
licence file and package metadata. A source archive can be corrupt or wrong;
check the PyPI digest before reading. A licence label is not legal advice;
state exact text and its distribution implication only as a question to be
resolved for the intended use. The smallest diagnostic is metadata plus one
verified sdist with its licence and import module.

The plan passes because the baseline is the pinned EasyOCR 1.7.2 source,
the candidate-selection status is explicit, source identity is a veto,
and the output cannot by itself promote runtime use or legal clearance.
Use a bounded response-size cap and preserve any denied request once.
