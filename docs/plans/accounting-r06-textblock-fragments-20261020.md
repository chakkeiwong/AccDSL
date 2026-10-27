# R06 — retained escaped text blocks and XML fragment structure

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–06, MC23–26, MC28–35.
Output: data/accounting-master/r06-textblock-fragments-20261020/.

Question: what can be established about the XML fragment structure of the
56 retained text-block values without confusing raw evidence, one XML
decoding step, embedded structure, display text and XHTML conformance?
These strings total 941,509 UTF-8 bytes; the largest is 130,498 bytes.
No selected string contains a DOCTYPE, ENTITY declaration, XML declaration,
or namespace declaration. These inventories guide scope, not conformance.

Evidence contract: use the exact retained instance/declarations and DTR
2020/2022 textBlockItemType, xmlNodesItemType and escapedItemType annotations.
Read primary XML content/well-formedness/reference rules. If a specific XHTML
claim is evaluated, inspect its exact version and distinguish whole-document
rules from fragment requirements. At most two bounded primary-document
acquisitions, 45 seconds each; no renderer, browser, package install,
schema processor or acquired code executes.

The primary criterion is an occurrence-by-occurrence bound structure record:
original escaped source slice, decoded string hash, parse outcome under an
explicit synthetic wrapper with no supplied namespaces, element/attribute/
text/tail inventory, and exact character-content preservation. The wrapper
only permits a sequence of top-level nodes and text; it does not supply XHTML
namespace, schema, doctype, CSS or rendering semantics. A changed source/hash,
unexplained missing text or XML parser rejection vetoes that local result.
Parser rejection of a broader document construct means outside this profile,
not automatic invalidity of a DTR value.

Research intent: expected failures are repeated HTML unescaping, silent
tag-stripping, lost tail text, invented default namespaces, rendered/display
equivalence claims, namespace/attribute requirements omitted because XML
well-formedness passes, and parser fixture success promoted to full validity.
A failure triggers explicit preservation/refusal or a source-specific repair.
Protected-byte changes and uncontrolled runtime execution veto continuation.

Default audit:

| Choice | Provenance / reason | Failure mode and diagnostic | Status |
| --- | --- | --- | --- |
| Exact already-decoded string | Prior source/portable correspondence | Second unescape changes literal markup; nested entity fixture | Required evidence boundary |
| No-namespace synthetic wrapper | Avoid inventing inherited namespace context for the stored string | Unbound prefixes fail; inventory every expanded tag | Local structural hypothesis |
| Standard-library ElementTree | Available local structure diagnostic, no installed XBRL dependency | Comments/processing instructions lost by default; preserve them explicitly and compare ordered text/tail tokens | Diagnostic only |
| No DTD/entity/declaration profile | Actual finite selected strings have none | Broad parsing could fetch or expand data; reject before parse and mark outside_scope | Convenience profile |
| Exact token stream, not HTML display | XML characters/elements have inspectable order | Styles/table order omitted from a display claim; preserve attributes and state that display is unchecked | Reviewed local target |
| XHTML edition | Not pinned by the retained annotation wording | Choosing XHTML 1.0 silently could overclaim; any comparison is explicitly conditional | Unselected implementation decision |

Skeptical audit passes for this finite structural question. A successful
wrapped parse would not establish XHTML membership, accessibility, rendering,
sanitization, accounting interpretation or an installed validator. Source
annotations explicitly add duties beyond base string membership. Check
content and namespace assumptions first, preserve a real entity-containing
example, then add independent event/token and malformed/boundary fixtures.

Deliver source extracts/receipts, 56 structural records, exact preservation
checks, readable boundary note, result/review, six source ledgers, run manifest,
completion/protection bindings and additive R08 supplement. Keep all frozen
Values and validation flags; edit only four live controls. Preserve
3.44/396/not_ready,53/6/46,zero whole-row closures,HEAD/index/empty staging and
36 dirty paths. Standard-library Python,-B,CUDA_VISIBLE_DEVICES=-1. One-time
prepare/construct/check/record; no-argument replay is read-only.
