# Version 2.3 bounded author review

8 October 2026, Asia/Hong_Kong. Reviewed the final PDF at SHA256
`479fd8007fab98b7ee8393a732e183010bcfbd24df027f8dea5998ce43aad030`.
The final render manifest and its page hashes are bound in `render-review.json`.
The reader and scope are those in `manuscript-plan.md`: accounting designers
and implementers deciding when filing extraction supplies usable evidence.

Read the final body slice in order, PDF pages 98–101 (printed 91–94). Page 98
establishes stable source/run identity; page 99 carries typed exchanges into
the literal/scale example and then the actual annual taxonomy archive. The new
dependency paragraph explains why an issuer archive is insufficient. Page 100
answers the two operational questions: test an offline path's existence/hash,
and inspect validation status plus messages/model errors instead of trusting
the default boolean. Its closing paragraphs separate taxonomy terms from code
licences. Page 101 resumes the engineering/accounting/scientific acceptance
distinction. The final line of page 99 starts the offline paragraph and it
continues naturally on page 100; it is a page break, not missing text.

Inspected title page 1, contents pages 5–6 and all bibliography pages 122–127
(printed 115–120) individually at readable resolution. Contents places 13.13
on printed page 92 and chapter 14 on 94, matching the actual pages. Arelle's
commit and API citation, both FASB notices and XBRL's copyright source are
legible. The FASB references explicitly retain the unversioned/2027 date
qualification. Bibliography entries span the 122/123 and 123/124 breaks without
lost text. URLs wrap inside the margins; the inherited contracts-paper URL
breaks after `https:`, but the full link remains visible. No clipping, missing
glyph, overlapping text or new citation placeholder was found in this slice.
The contact-sheet display was not used as reading evidence.

Answers available from the repaired section:

* The issuer archive needs outside concept and type definitions. The static
  graph locates declared references and identifiers; it does not run XBRL
  validation or decide whether a reported accounting interpretation is right.
* A nonexistent cache path must preserve an unresolved dependency. The adapter
  checks files and hashes before loading and preserves the original addresses.
* `validationExitCode` must be enabled, and status, diagnostics and model errors
  examined together. Facts, contexts, units and source occurrences must be
  copied before closing the session.
* Unchanged taxonomy reuse has source-specific notice conditions; historical
  applicable terms and the actual Software Notice remain unresolved. A source
  licence cannot clear every dependency or authorise a distribution.

| Ledger | Author verdict and limit |
| --- | --- |
| Reader comprehension | The section now explains two concrete failure mechanisms and the proposed response. Independent reader/human comprehension remains pending. |
| Mathematical integrity | No mathematics was changed by this insertion. Existing scale arithmetic remains intact; no new whole-document rederivation is asserted. |
| Source fidelity | New software claims identify the inspected source pin. Static findings, proposed runtime behavior and unestablished historical terms remain distinct. Exact source/quote checks are in the dossier. |
| Typography/rendering | The named 13 pages were inspected from the final PDF. This is a bounded rendered inspection, not a new read of all 127 pages. |

Strongest alternative explanation: the static graph could omit a discovery
mechanism required by a later validator. Runtime tests of the actual resolver
would expose that limitation; zero unresolved recorded edges does not refute it.
The weakest evidence remains runtime compatibility and complete component
licensing. Neither is represented as accepted. No new substantive defect in
the bounded manuscript insertion requires a TeX change in this closeout.
