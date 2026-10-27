# Filing adapter decisions from inspected source

Use native Arelle facts as the candidate structured-filing input, with an AccDSL
preservation layer. Evaluate Docling for PDF and document layout alongside a
deterministic PDF baseline. Neither library supplies the financial-context,
historical-admission or review contract by itself. Docling's XBRL graph export
loses information required by that contract and should not become the retained
financial record.

This is a source/interface audit and proposed integration, not an executed
adapter, benchmark or product selection. Sources below are exact retained files;
source-register.json supplies full commit URLs and SHA256 values, and
source-anchors.json supplies checked line ranges and excerpt hashes. The
retained October 2 branch snapshots remain unchanged in sources/retained.

## Version and license boundaries

| Component | Inspected official pin | License and reproducibility limit |
| --- | --- | --- |
| Arelle | `01f6a4656c2c6551d2f05f31c9d74366d133ee7e`, commit dated 2 October 2026 | LICENSE.md identifies Apache-2.0 and separate dependency/plugin terms. pyproject uses a dynamic SCM version; the audit identity is the commit. Dependency/plugin/taxonomy locks remain required. |
| Docling | `eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`, pyproject version 2.133.0 | MIT code license. The retained official README explicitly assigns individual model terms to their originating packages. Model weights and optional dependencies were not acquired or licensed by this audit. |
| docling-core | `d7cef4c10a7574c02ba9ea1b02c9c494dfe8b0df`, version 2.99.0 | MIT. It is within Docling's declared `>=2.98.0,<3.0.0` range, but no installation or runtime compatibility check was performed. |
| pdfplumber | `4c64b92d5caccd71c645e98e0fabb0c4dba7ff45`, stable branch commit | MIT. Selected Python implementation inspected; pdfminer and other dependencies remain unpinned. |

These pins permit reconstruction of this inspection. They are not recommended
production locks or a statement that the newest branch is the best release.
License anchors are L01-L03; package metadata is V01-V02. The model-license
qualification is retained README lines 151-154 (hashed in retained-register.json).
Three obsolete inferred Docling paths returned HTTP 404; the source register
preserves the failed requests and the resolved reading-order path. Table-model
inference internals were not inspected, so accuracy or model mathematics cannot
be inferred from the available table result types.

## Capabilities and required preservation

Anchor IDs refer to source-anchors.json. Native source field availability is
distinct from faithful interpretation of the issuer's disclosure.

| Required information | Inspected behavior | Required AccDSL behavior |
| --- | --- | --- |
| Full original bytes and identity | Arelle's `objectId()` wraps a model object index (A04); it is not a portable source key. Docling `create_file_hash` computes SHA256 (D01), but docling-core `DocumentOrigin.binary_hash` masks a hex string to its low 64 bits (C01). | Store original bytes/full SHA256 and immutable source version outside library exports. Namespace every DOM/fact/item ID by the original source version. Retain Docling's native hash only as a tool field. |
| Literal versus transformed number | Arelle exposes contextRef/unitRef, decimal/precision metadata, nil flag and value; plain `value` can use a schema default/fixed value (A01). Inline `rawValue` itself excludes inline-excluded text, joins continuations and can collapse whitespace; `value` applies transforms, sign and scale with Decimal (A02). `effectiveValue` is a locale/formatted view. | Retain original element bytes and attributes, raw/transform result and transform version separately. Never use `effectiveValue` as literal disclosure. Do not scale `value` a second time. Distinguish nil, empty, zero, invalid and schema-derived defaults. |
| Complete financial context | Arelle has entity identifier/scheme, explicit and typed dimensions, non-dimensional context parts, units and periods (A01/A03/A05). It does not establish group perimeter, accounting basis, mapping equivalence or source vintage merely from those fields. | Preserve expanded namespace QNames, context XML, typed member contents, all unit numerator/denominator measures and referenced taxonomies. Attach other contextual facts with located support or explicit unknowns. |
| Date interpretation | Arelle deliberately adds one day to date-only instant/endDate when producing boundary datetimes; original-date accessors also exist (A03/A06). | Preserve lexical source dates and date precision alongside normalized boundaries. Flow end_exclusive may be the next day; a reported stock instant date remains the source date. These are economic/reporting dates, never publication time. |
| Occurrence and assertion identity | Arelle supplies native facts and equality/dedup diagnostics; complete or consistent duplicates can be removed by explicit OIM export options (A07/A08). Consistent duplicate checks use overlapping accuracy ranges. | Keep every occurrence. Treat equality/range diagnostics as candidate evidence only; require the full context and an explicit alias decision before linking assertion identities. Export without deduplication, and preserve source sidecar even then. |
| Precision and rounding | Arelle decimals/precision may be reported or schema-defaulted; `rangeValue(..., truncate=False)` returns closed half-unit bounds (A01/A09). | Keep origin of each accuracy attribute. A validation interval does not prove an issuer's tie convention or a probability law. Exact endpoint admission follows the evidence contract; no implicit nearest-rounding assumption for untagged PDF precision. |
| PDF layout, text and cells | Docling supports page/bbox/charspan provenance and untreated/sanitized text, with table cells, spans and header flags (C02-C05). Reading order can associate captions/footnotes and converts coordinate origins (D05). Empty table grid cells can be synthesized by the TableData view (C04). | Retain full structured document/ConversionResult and original PDF; preserve physical page, page dimensions, coordinate origin, rotation and extraction transformation. A charspan refers to derived text, not an original PDF byte interval. Empty generated cells and zero values remain different. |
| HTML source location | Docling HTML `_make_prov` returns None if rendered boxes are unavailable (D06). Exported internal item references are document-tree indices. | Retain original HTML and a DOM/ID/byte sidecar independent of rendered provenance. Do not invent PDF pages or treat a rendered box as byte provenance. |
| Tables across pages and financial meaning | The types can represent spans, references and footnotes. The inspected paths do not demonstrate complete multi-page financial-table joining, header scope or accounting interpretation. | Keep continuation/header alternatives and unresolved scope. Pilot exact current/prior-period, unit, parent/group and footnote cases before selecting an adapter. Never infer zero/hierarchy/additivity from blank/indentation alone. |
| Success and partial failure | Docling retains categorized errors, successfully processed pages and failed-page placeholders; timeout can yield PARTIAL_SUCCESS (D03/D04). `raises_on_error=True` is the conversion API default (D02). Arelle exposes run result, loaded models and structured logs (A10). | Inventory expected pages/units independently. Record per-page/fact failure and retain successful unrelated work. A present placeholder page is not extracted content; SUCCESS is not semantic or reference closure. Capture causes/logs before cleanup. |
| Time and review | Docling ConversionAssets timestamp is overwritten with `datetime.now().isoformat()` at save (D03), without timezone evidence in that call. No inspected export establishes publication, ingestion receipt, historical byte vintage or AccDSL acceptance. | Retain acquisition receipt with aware timestamp and full hash; keep publication evidence and review events distinct. Converted data starts as a proposal. Unknown publication stays unknown. |
| Reference closure | Arelle loads taxonomies and linkbases; Docling has document and local/remote resource options. Neither inspected path implements AccDSL's declared disclosure roots, edge dispositions, budget and immutable resume receipt. | Use a separate declared-package inventory and traversal. Preserve unavailable external notes, cycles and frontier; no library conversion count establishes closure. |
| Side effects and isolation | Arelle Session documents shared global state and one session per process (A10), and WebCache has configurable offline/caching/downloading paths (A11). Docling can resolve URL inputs (D02), fetch model artifacts when none supplied, enable OCR/table processing by default, and load optional services/plugins (D07). | Proposed evaluation uses local retained sources, explicit dependency/model/taxonomy manifests, offline resources, separate cache/output directory and worker process isolation. Do not assume remote-services=False also disables model downloads. No package or model was installed here. |

Docling's archive contains document/status/error/version/timing/confidence data;
an exported Markdown string is a presentation derivative. Its Markdown interface
supports filtering layers/labels, omits page-break markers by default, and
defaults `traverse_pictures=False`; its own documentation says picture traversal
is needed for OCR text nested in full-page pictures (C06). Retain structured
results and inventory before producing Markdown, and explicitly account for
content omitted from that view.

An additional input-state concern appears in Docling's `create_file_hash`: the
BytesIO branch reads from the current stream position without seeking to zero
or restoring it (D01). Passing a partly consumed stream to that helper hashes
the unread suffix. The preservation layer should compute its own original hash
before handing over a fresh/reinitialized stream. This is a source-level helper
finding; the packet does not claim every converter caller supplies a consumed
stream or fails to reset before parsing.

## Specific Docling XBRL losses

The inspected XBRL backend directly wraps Arelle and admits only
`Type.INSTANCE` (X01). It is not an independent XBRL parser and does not accept
Apple inline HTML through this backend. Missing Arelle causes an ImportError;
neither local nor remote taxonomy permission causes an initialization error;
loaded model errors are rejected. Initialization exceptions inside its try block
are wrapped as DocumentLoadError. Local taxonomy trees and instance bytes are
copied into a temporary directory; the code warns cleanup can leave open files
on Windows (X01). These paths were read, not exercised.

In `convert`, facts without a resolved concept are skipped. Text blocks are
whitespace-collapsed and reparsed as synthetic HTML. Numeric output retains a
concept key and a handful of text values, not the original fact ID/contextRef,
source locator, complete unit or full context (X02/X03):

* `dimensions` is populated but never used to construct the output. Even those
  populated strings keep local names rather than expanded QNames.
* The dimension formatting calls `memberQname.localName` without guarding typed
  dimensions. Arelle's typed members have no explicit `memberQname` (A05).
  This is a source-derived failure hypothesis for the typed-dimension fixture,
  not a runtime-reproduced exception.
* Unit output takes only the first numerator measure and labels it currency,
  losing denominator/composite units such as USD/share.
* `instantDatetime.date()` and `endDatetime.date()` print normalized boundary
  dates. The output does not label the latter as exclusive or preserve the
  original lexical date.
* Presentation traversal selects `parent[0]`; different presentation networks
  are not preserved by that selection. Calculation relationships link a weight
  to a child concept, while link role/network context is absent from the graph
  construction. That graph cannot serve as the complete calculation rule (X04).

The native Arelle-to-OIM path retains more context, including entity, dimensions,
composite units, periods and footnote links (A08). It is a credible exchange
candidate with original-source sidecars, not a reason to replace originals or
assert that every XBRL feature has an OIM representation. XML accuracy metadata,
inline lexical presentation, continuations and source locations must survive
outside the normalized exchange.

## Actual retained instant example

The retained Apple FY2025 Q1 inline filing contains `f-134`, Assets `344,085`,
unitRef `usd`, contextRef `c-17`, scale `6`, decimals `-6`, and transform
`ixt:num-dot-decimal`. The context says instant `2024-12-28`, SEC CIK
`0000320193`. Full source SHA256 is
`2f7629f0733f75b3155dd52f7ae6a8724468e3cde1a9ce32fbce96d98f1ec27e`.
`apple-instant-case.json` retains exact half-open byte spans and excerpts.

The normalized amount is 344085000000 USD. An isolated probe of Arelle's retained
date helper represents its date-only instant boundary as 2024-12-29T00:00:00, while the
original reported date remains December 28. The Docling formatting issue applies
to an equivalent native-instance context; it is not an observed Docling output
on this inline filing. Root packet 4 independently labels the statement and
Note 2 sales occurrences; their repetition is not evidence of two independent
financial facts.

The bounded diagnostic also executes the retained origin-hash validator body
with `int` standing in for its Uint64 alias and the retained hash helper with
standard-library BytesIO. It checks two different 256-bit hexadecimal inputs
that share the low 64 bits and a partly consumed stream. The date helper uses
stdlib `re` on the retained ISO pattern. These isolated function checks support
the stated local mechanisms; they do not exercise Pydantic, dependency resolution,
the full converter or library integration.

## Matched-task alternatives

| Task/input | Baseline and candidate | Fair comparison and residuals |
| --- | --- | --- |
| Native XBRL/inline facts | Located manual XML/inline inventory on bounded snippets; native Arelle facts; Arelle OIM plus preservation sidecar | Use identical source/taxonomy package. Manual XML inventory is a transparency baseline, not a general validator. OIM is an alternate exchange through Arelle, not independent parser confirmation. Check units, dimensions, date boundaries, nil/defaults, every occurrence and continuations. |
| Digital PDF text and tables | Native text-layer/located manual labels; pdfplumber with explicit table settings; Docling with explicit backend/OCR/table settings | pdfplumber exposes character geometry, page numbers, table bounding boxes and cells (P01-P03). Its singular `extract_table` chooses the largest table; compare all `find_tables` and retained cells. Its list-of-lists export loses geometry unless kept separately. It is a credible rule-based digital-PDF baseline, not an OCR system. |
| Scanned/image PDF | Human located transcription; a separately pinned OCR baseline; Docling OCR/layout candidate | No OCR model was selected or inspected deeply here. Agree language/rotation/scan strata and model licenses first. A digital-text-only baseline's missing output is a capability limit, not a fair general OCR accuracy ranking. |
| Untagged HTML/narrative | DOM-aware text/table extraction and located labels; Docling HTML output with DOM sidecar | Preserve hidden/inline-excluded content and visible occurrence roles separately. An XBRL tag is proposed structured evidence; a narrative paragraph can qualify its economic interpretation. Neither makes missing notes disappear. |

Camelot/Tabula are plausible additional table baselines and an independent XBRL
implementation would strengthen parser comparison, but their actual versions,
licenses and code have not been inspected here. They remain candidates for a
later bounded source audit, not claimed supported integrations. The protocol
does not wait for every possible alternative before doing the small manual and
pdfplumber/Docling development comparison.

## Reviewed decision and remaining work

| Decision | Primary evidence | Veto status | Main uncertainty | Next justified action | Unsupported conclusion |
| --- | --- | --- | --- | --- | --- |
| Prepare native Arelle preservation adapter specification | Located fact/context/value/period code | Native facts need sidecar/context admission | Full taxonomy and instance behavior unexecuted | Implement only after P16 interface agreement; run contract cases in a separately locked environment | General accounting truth or XBRL completeness |
| Keep Docling PDF/layout as candidate | Types, conversion/error paths, provenance and exports inspected | Origin truncation and presentation losses forbid export-only storage | Extraction/model performance unknown | Run the proposed development evaluation after model/dependency selection | Accuracy, latency, deployment/default readiness |
| Reject Docling XBRL graph as canonical financial record | Concrete context/unit/date/network losses | Contract preservation veto supported statically | Exact runtime error behavior untested | Retain native facts and test the stated counterexamples | All Docling uses are invalid |
| Use pdfplumber as matched digital-PDF baseline | Character/table paths inspected | No OCR capability conclusion for scans | Tuning and corpus performance unknown | Explicit small development tuning budget, then lock settings | Statistical superiority |

Post-review alternative explanation: native interfaces may expose information
not included in a chosen export; this audit criticizes that export boundary,
not all internal information. A later version may repair the graph losses.
Reinspection of a pinned repaired version plus executed counterexamples would
change that decision. The weakest evidence is runtime compatibility and model
behavior, which remain untested. No numerical rankings, runtime claims or phase
acceptance follows from these results.
