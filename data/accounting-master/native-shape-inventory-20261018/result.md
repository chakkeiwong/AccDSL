# Complete retained-native structural inventory

18 October 2026. P16/P17/R06; MC01–06/23–25/27/28/30–35.

All 1,328 top-level XML elements are retained as individually located source
occurrences: 1,127 facts, 193 contexts, seven units and one schemaRef. All
3,988 checks pass, twelve intentional corruptions reject, and exact read-only
replay passes. Expat byte indices and independently parsed original fragments
agree. The one element without an ID is schemaRef; no duplicate IDs or missing
fact-context/unit joins were found. This is XML structural coverage only.

There are 968 decimal-looking lexical strings, 157 other text strings and two
nil facts. Seven decimal-looking strings have no unit: fiscal year, CIK, postal
code, area code, two maturity years and auditor firm ID. In particular, CIK
0000320193 must retain its leading zeros. Rational candidacy is a lexical
diagnostic, not a type decision. No taxonomy type is admitted by the inventory.
All unit-bearing non-nil facts in this file have decimal-looking strings.

The contexts contain 231 explicit members and four typed members. The typed
members occur in c-58 through c-61, on the remaining-performance-obligation
timing axis, with domain-element texts 2024-09-29, 2025-09-28, 2026-09-27 and
2027-09-26. A QName-only member conversion would lose their domain-element
content. Preserve the original span/tree and leave typed-domain interpretation
unknown until separately checked. There are 98 duration and 95 instant source
periods. This supplies no admitted financial-time assignment.

The seven units include USD, shares, USD per share, pure, two issuer-defined
measures (Vendor and Subsidiary), and EUR. Their numerator/denominator sides
and namespace expansion are explicit. There are 69 repeated fact-signature
groups; all occurrences remain. No selected fact has child elements. Fifty-six
text strings contain markup-like characters; this lexical screen does not
establish a taxonomy text-block type or authorize rendering that content.

| Structure | Disposition for broader proposed translation |
| --- | --- |
| 231 explicit members | Existing explicit-dimension fields can preserve tokens, expanded names, container and exact source spans |
| Four typed members | Preserve exact typedMember subtree/span; member_qname remains Unknown, member_token may be absent; add explicit conversion evidence instead of inventing a QName |
| Seven unitless decimal-looking facts | Retain reported characters and use Unknown candidate type/value unless inspected taxonomy supports a narrower interpretation; do not strip leading zeros |
| schemaRef without ID | Preserve a standalone occurrence with null element_id and explicit source-link evidence; do not invent an ID or count it as a fact |
| 56 markup-like text strings | Preserve decoded characters and original bytes; any portable Text representation needs a stated unvalidated-text conversion |
| 69 repeated signatures | Retain every occurrence and provenance identity; no deduplication |
| Seven units and all periods | Preserve source evidence; financial meaning remains Unknown |

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Deliver structural inventory | All top-level elements partitioned, located and independently fragment-checked | No protected-byte, source-join or fragment disagreement | Structural coverage does not imply economic completeness | Prepare bounded portable examples for typed dimensions, unitless numeric-looking facts and ID-less schemaRef | Complete portable filing, taxonomy validity or Arelle compatibility |
| Continue representation repair | Concrete new hazards identified | Novel structures are repair triggers, not continuation vetoes | Candidate typing and effective runtime remain unverified | Extend proposed examples without altering frozen schemas/evidence | New admitted accounting facts |
| Preserve not_ready | Additive internal source evidence | No global continuation veto | Wider methods, sources and independent acceptance remain open | Refresh controls and continue authorised preparation | Whole requirement/program completion |

Post-run red-team: the structural classifier treats non-link/non-context/non-unit
root children as facts for this pinned instance. Counts reconcile with the
prior inventory and every entry remains inspectable, but this is not a generic
taxonomy-based classifier. Namespace redeclaration, DTD/entity declarations and
CDATA are unsupported and checked absent. An original-slice mismatch would
invalidate this locator result. No stochastic comparison or ranking applies.

Actual commands were check.py --check-only, check.py --record once, and check.py
read-only. The run manifest binds exact source/code/output hashes, environment,
commit and elapsed time. Only standard-library CPU source checks ran; no
upstream Arelle, numerical framework, GPU, network or empirical campaign. The
protected 3.44 manuscript, 53 obligations, six interactions and 46 operations
remain unchanged; independent acceptance remains pending.
