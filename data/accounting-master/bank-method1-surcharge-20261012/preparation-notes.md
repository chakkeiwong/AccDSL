# Preparation repairs and reading scope

The first XML normalizer stopped when it assumed all six API requests had
succeeded. The preserved §217.401 response is HTTP 429/HTML. The corrected
inventory records all receipts and admits only the five successful XML bodies.
Tables occur under nested DIV/TABLE elements; the initial GPOTABLE-only table
inventory was empty. Exact nested table captions, headers and row cells are now
retained in sections.json. These were preparation defects, not legal findings.

The official 2025 and 2026 section PDFs each contain complete §217.401 across
physical pages 1–2, printed 630–631, with portions of adjacent sections. Both
2025 pages and 2026 page 1 were visually read; the 2026 page 2 render is exactly
identical to the inspected 2025 page 2 image. The 2026 header explicitly says
1–1–26 Edition. Raw text, source bytes and all four renders remain retained.

The first annual-edition text comparison failed because the 2026 extraction
includes publisher production metadata between the two definition pages.
Removing the VerDate block alone left its separate operator line, causing the
second comparison to fail. The final comparison excludes both precisely
recorded metadata blocks by their literal content and bounding boxes. It removes
running headers/page numbers, isolates the §217.401-to-§217.402 body, collapses
whitespace and retains hyphenation. Complete normalized definitions then match.
definition-comparison.json preserves the exact removed text and whether it was
inside the selected body. No operative wording was silently corrected. The
production date string is not treated as publication or historical availability
evidence. These extraction differences do not establish an E05 source conflict.

Sections 217.400, .402, .403 and .404, all their tables and the full annual
§217.401 definitions were read. The April .403 response was compared completely
with January: operative paragraphs, table headers and cells agree, but the
Method 2 caption changes a colon to an em dash. The first source checker wrongly
assumed full equality and failed; its result and code remain in intermediate/.
The corrected checker preserves this exact punctuation difference separately.
No .401 API success or complete later amendment chain is claimed.
The retained April §3.11(a)(1)(v) cross-reference was read directly. Report
instructions, actual FR Y-15 values, year-specific global denominators, score
rounding/interval conventions, Method 2 calculation and supervisory facts remain
unverified. No bank score, capital buffer or payout is computed.
