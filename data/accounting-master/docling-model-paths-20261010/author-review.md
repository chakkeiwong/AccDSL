# Author review of Version 2.26

Candidate: 168 pages, SHA256
`d7c60268490921ec7edbc964ece351ebcdbd478ce422fa20b59de844e3ab48d7`.
Status: `independent_reader_pending`; human/domain acceptance pending.

The new paragraphs let an implementer distinguish requesting OCR from observing
an engine's processing, and a model name from retained model bytes. Source
inspection supports these distinctions; actual OCR, offline operation and
package compatibility remain untested. The material is provisional design prose.

I read final PDF pages 137–142 in order at 120 dpi, two full-page images per
call. Page 137 supplies identity and exchange context. Page 138 supplies the
numeric/context and page-loss examples; its exit is the subset question carried
onto page 139. Page 139 completes that explanation and adds the unperformed OCR
stage, then the model identity/download distinction. Both new paragraphs are
complete on this page, with source attribution and their later-execution limit.
Its taxonomy and Arelle examples extend the same dependency issue; the final
Arelle limitation continues onto page 140. Page 140 preserves the comparison,
component terms and historical-taxonomy limitations. Page 141 distinguishes
engineering, accounting and scientific acceptance, making the limits of the
new source findings explicit. Page 142 continues its conformance table without
a new pagination defect. This is a bounded slice, not a chapter or document read.

Separately inspected navigation pages 1–7, again no more than two images per
call. The title reports Version 2.26; Section 13.13 and Chapter 14 page numbers
match the rendered pages. The final build log has no warning/box diagnostic;
that fact is a rendering check, not a comprehension verdict.

Answers to the before-edit questions, from the rendered slice:

1. Yes. Automatic OCR can select no engine, warn, and return pages. The adapter
   needs requested mode, selected engine/model and page outcome, with required
   OCR that never occurred recorded as unprocessed.
2. The layout preset references moving `main`; neither that name nor the table
   tag supplies hashes of the weights and preprocessing files actually used.
3. Remote inference and model acquisition are different paths. A supplied
   local folder prevents fallback in the inspected layout helper but does not
   establish the folder's identity or all downstream network behavior.
4. Source branches explain these failure possibilities. Hash-bound assets and
   later isolated execution are needed for actual offline behavior; source
   inspection has not performed OCR or established its quality.

| Ledger | Author verdict |
| --- | --- |
| Reader comprehension | The local transition adds a concrete missing-stage case before model identity; the four questions are answerable. Independent comprehension is pending. |
| Mathematical integrity | No equation, derivation or numeric finding changed. No new mathematical validation claimed. |
| Source fidelity | Same-pin source anchors distinguish warning/pass-through from language error and local-path presence from byte identity. No observed Apple failure or runtime claim. |
| Typography | Six body/adjacent pages and seven navigation pages inspected; no clipping, malformed citation or new table break found in that slice. |

Natural prose review found concrete subjects and attributed code behavior.
Qualifications prevent specific runtime/identity inferences; they do not replace
the finding. No source claim or old qualification was deleted. No human voice
or full proposal acceptance is certified by this author review.
