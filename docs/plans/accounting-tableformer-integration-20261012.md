# Explain TableFormer structure, text and score boundaries

12 October 2026. E08/C06, E14/C07, P18; MC23/25/29–35, G8/G9/G10/G18.
Separate candidate Version 2.45; protected Version 2.44 is the 181-page PDF in
manuscript-score-rounding-20261012, SHA256
1bb455c8f139be17908b5cec5599012ab5eae860a11b0a07f3ee4bb5bb6cecb8.
Evidence: data/accounting-master/tableformer-paper-20261012 and the retained
4.0.2 loader/model-card units. Finish source checks before candidate edits.

Target readers are accounting researchers and implementers selecting an
ingestion method. They should explain why correct-looking cell geometry does
not establish correct extracted text or financial meaning, and why a published
score cannot be assigned to an unidentified later checkpoint. The repair unit
is the literature extraction discussion and the adapter's table/text behavior,
with their local transitions and changed bibliography pages. This is bounded
provisional author review, not whole-document or independent/human acceptance.

Diagnosis: the existing discussion names table recognition and separated
licences but does not teach how TableFormer gets its cell text, how matching
can alter structure, or what the model-card score actually measures. The
tempting inference is that a table predictor supplies a self-contained table
of accounting facts. The original paper, supplement and later consumer divide
that task among image-based structure, supplied text and matching/correction.
The argument runs from that division to the reported cropped-table evaluation,
then to the evidence that a later implementation must retain for review.

Preserve all old paragraphs, all 48 displays, all 89 existing bibliography
entries, source boundaries and substantive qualifications. Add precise paper,
supplement and pinned-consumer references, without scattering training settings
or internal workflow into reader-facing prose. Copy the baseline source outside
the new candidate tree. Change only the two indicated source files, version
label, added references and generated build products. Read the baseline local
PDF slices before editing, then inspect final changed pages and their immediate
transitions at readable resolution.

Evidence contract: the comparator is the exact protected Version 2.44 source
and PDF. Pass requires supported material prose changes, intact old content,
all old displays/references, a clean project-normal LuaLaTeX/BibTeX build,
resolved citations/references, preserved source hashes, and inspected rendered
changes. Lost content, mismatched version/hash, unsupported metric transfer or
unread relevant source veto this candidate. A compilation pass is engineering
evidence only; author reading cannot certify reader comprehension. No scores,
timings or proxy counts select a parser or authorize runtime work.

Default audit: 4.0.2 is the previously inspected lower-bound source candidate,
not an installed recommendation. Original paper training choices and later
configurations remain source facts, not local defaults. The score is explicitly
Table 4 structure with content and externally supplied PDF text. Do not infer
beam search in the original paper or label code argmax a proven paper mismatch.
The source's printed loss ambiguity remains in the preparation record because
this repair makes no training-reproduction claim.

Skeptical audit passes: the baseline is exact, comparison populations and
versions stay separate, validation addresses the edited argument, no runtime
environment is imported, and the stopping condition is bounded author-reviewed
integration. Keep E01/E05/E07/E08/E14 open and full readiness not_ready. A
source or build failure triggers focused repair; missing human acceptance
blocks promotion, not continued internal work.

Artifacts: data/accounting-master/tableformer-integration-20261012, candidate
docs/design/proposal/manuscript-tableformer-20261012. Record actual commands,
hashes, content checks, changed-page reading, source and comprehension limits,
result and manifest. Refresh four live controls, make a scoped commit, then
continue with the exact OTSL follow-up identified in the Docling report,
under a new bounded source plan. No installation, inference, fees, outreach,
publication or restart of the former controller.
