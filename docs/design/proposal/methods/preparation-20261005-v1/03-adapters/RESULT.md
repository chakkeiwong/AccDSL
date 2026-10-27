# Adapter preparation result

Keep native Arelle as the structured-filing candidate and Docling as a
PDF/layout candidate, both with original-source preservation and explicit
context/review layers. The inspected Docling XBRL graph export cannot be the
canonical financial record: it omits collected dimensions, simplifies composite
units, loses original occurrence context and prints normalized date boundaries
without preserving source-date semantics. These findings reject that export
choice, not all uses of either library.

Completed deliverables:

* `capability-matrix.md`: actual code/interface/license findings, source-to-output
  losses, side effects, matched-task alternatives and decision limits.
* `source-register.json`, `retained-register.json`, `source-anchors.json`: 39
  official files at four recorded commits, 15 copied prior references, 36
  claim-anchor groups, full hashes and three recorded 404 requests. The actual
  Apple filing is additionally retained and pinned in `apple-instant-case.json`.
* `adapter-cases-v1.json`: 16 proposed source/context/location/failure cases.
* `evaluation-protocol.md`: matched-input baseline ladder and separate
  transcription/context/table/mapping/support/unknown-coverage evaluation.
* `checks/verification.json`: 202 passing bounded checks, command/environment,
  exact evidence classes and limitations.
* `annotation-cross-review.json`: independent investigator review of packet 4,
  two identified source-fidelity defects repaired by its author and rechecked.

The real Apple FY2025 Q1 f-134/context c-17 case preserves Assets 344,085 million
USD and source instant 2024-12-28. Arelle's retained date helper produces the
next-midnight boundary 2024-12-29T00:00:00. The diagnostic executes that helper
alone, plus Docling's retained hash helper and the docling-core origin validator
body with explicitly recorded stand-ins. These local checks confirm the stated
mechanisms; no Arelle, Docling or pdfplumber package was installed/imported/run.

Additional preservation findings: the Docling origin hash clips a hexadecimal
SHA256 to 64 bits; its asset timestamp is a save timestamp without timezone
evidence; its stream hash helper consumes the current BytesIO suffix; Markdown
can omit OCR text inside pictures; and failed-page placeholders may remain in
the document. Preserve full source bytes/hash, original locators and explicit
time receipts independently, with structured conversion results and failures.

The packet-4 cross-review checked original Apple byte spans and selected rendered
Munich Re, Midea and HSBC statement pages. It found HTML parser-normalized names
being called original markup and defective Munich support strings still labeled
as faithful literal text. Both are repaired. The rechecked labels remain
provisional exposed development evidence; this review is not blind annotation,
human adjudication, complete financial semantics or accounting acceptance.

## Skeptical final review

The main risk was mistaking available fields for preserved output or successful
parsing for faithful support. Actual export and helper implementations reveal
concrete counterexamples, now represented in cases. Commit pins do not freeze
dependencies, models or taxonomies; version-range compatibility is not an
installation result. Source claims are bounded to inspected files/lines. The
synthetic collision proves that a 64-bit field cannot preserve the full digest,
not that a real malicious source collision was found. The typed-dimension
failure remains a source-derived hypothesis for a future integration test.

No empirical ranking or confidence threshold is supported. Model performance,
OCR language coverage, multi-page table behavior, runtime compatibility,
dependency/model licenses and complete alternative surveys remain untested.
The evaluation protocol keeps these uncertainties explicit and does not borrow
an unrelated benchmark's threshold or an upstream model default.

## Proposed integration

At a stopped master boundary, register this whole packet as candidate P17
preparation. P16 should consider its occurrence/source sidecars, exact financial
context, typed errors and separate time evidence in the remaining interfaces
and persistence contracts. P17 should pin the selected deployment environment,
inspect any additional model/adapter choices, and execute the concrete contract
cases only after the initial profile is resolved. P18 can incorporate the
capability/limit explanation and examples; P19 should verify the specific
adoption decisions and preservation evidence. Do not mark any phase or full MC
requirement accepted from this packet.

All created files stayed in this packet's `/tmp` directory. The AccDSL worktree
and frozen corpus were read only. Sources and references use relative packet
paths so the supervisor can import a reviewed copy without altering originals.
