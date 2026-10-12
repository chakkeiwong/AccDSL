# Bounded diagnosis before editing

The protected Version 2.44 PDF and source hashes are checked against the closed
integration evidence. Its clean LuaLaTeX/BibTeX build is retained; rebuilding
that frozen directory would unnecessarily change bound outputs. The separate
candidate will receive a full normal build. Baseline pages 54–55 and 148–149
were rendered and read at normal page resolution before candidate creation.

| Anchor | Reader question and missing bridge | Planned repair | Preservation risk |
| --- | --- | --- | --- |
| PDF 54, Section 4.5 | Does a table-structure model also read the printed numbers? The broad Docling paragraph does not divide structure from text supply | Explain image-to-structure/boxes and externally supplied text, then the paper's measured target | Accidentally attribute whole-document or accounting accuracy to cropped-table TEDS |
| PDF 54–55 transition to financial QA | Why do table scores leave financial interpretation unresolved? The limit is asserted but no component-level example makes it concrete | Use Table 4's input and text source to explain the scope before returning to QA benchmarks | Delete old benchmark comparisons or imply an unmeasured parser ranking |
| PDF 148–149, Section 13.13 | Once model files are fixed, what evidence must a table conversion preserve? Text matching and structural repair are absent from the account | Retain text-cell locations and before/after structure, using the later pinned consumer as implementation evidence | Treat the original paper and later OTSL/checkpoints as identical |

Entry knowledge: readers already know that extraction proposes evidence and
that accounting validation is separate. The new burden is the division among
structure prediction, text acquisition and matching/correction; no equations
or training protocol are introduced. The source paper supplies the decisive
example. The adapter then records the evidence needed to review that division.
Old source/version/licence qualifications, paragraphs, displays and references
remain verbatim. Adjacent prose will be inspected for transition and pacing.

Cold-reader questions, fixed before editing:

1. What does TableFormer predict, and where do the words/numbers originate?
2. How could cell matching change the apparent row/column structure?
3. What population and content treatment underlie 95.4/90.1/93.6, and why do
   those values not answer whether a whole debt note is interpreted correctly?
4. Why must the later 4.0.2 consumer be identified and evaluated separately?
5. What should the adapter retain so a reviewer can trace a disputed cell or
   structural correction to its input?

The target is a material, supported local explanation with readable transitions.
Author answers and a clean build will not establish independent or human
acceptance. Full readiness remains not_ready.
