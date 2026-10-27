# Native offline resource resolution, proposed adjunct v1

This adjunct specifies documentary prerequisites for the selected optional
native-XBRL adapter. It complements the proposed field translation and the
existing L1/E1/I1 contracts; it neither registers a production schema nor
implements a loader. Its evidence is in
`data/accounting-master/native-offline-resolution-20261018/`.
MC01/02/04/05/23–25/27/30–35; G2/G9/G11/G17/G18.

## What an offline request must identify

A resource has a logical URI and separately an exact byte identity. The URI
is not a content hash, publication date or proof of availability. Before a
future loader opens a resource, its proposed resolution receipt must identify:

| Field | Required meaning |
| --- | --- |
| Source occurrence | Ref to the referring document and exact attribute occurrence, retaining the original reference text |
| Base chain | Each explicit xml:base and the document base, in resolution order; absent and ignored bases remain distinguishable |
| Resolution method | Versioned method and effective platform/configuration; a graph traversal method is distinct from an upstream loader method |
| Logical target | Resolved resource URI and fragment separately; expected namespace where supplied |
| Mapping | Explicit source-URI to target-URI/path mapping with provenance, or identity mapping; no implicit HTTP/HTTPS alias |
| Expected bytes | BlobRef, retained path, byte count and acquisition evidence; an archive member also identifies its containing archive |
| Actual open | Actual URI/path, opened-byte hash/count, decoder transformations and cache/package/loader decisions; pending until observed |
| Validation | Separate byte-match, namespace/fragment, XML, schema, XBRL and accounting states with logs and errors |
| Outcome | resolved_bytes, missing_resource, changed_bytes, ambiguous_mapping, unsupported_reference or runtime_mismatch, with an affected-reference list |

These are proposed receipt duties, not a new parallel financial Record envelope.
A future registered body must use L1 typed Refs/BlobRefs. The supplied JSON
examples are documentary plans: `actual_open` is null and
`runtime_equivalence` is not_checked. They cannot stand in for a runtime receipt.

## Pinned source behavior and its consequence

The source comparator is Arelle commit
`01f6a4656c2c6551d2f05f31c9d74366d133ee7e`. All line spans below are bound
in source-anchors.json, including the exact retained file hash.

ModelDocument.load first normalizes the URI and can reuse an existing model
document (75–85). Mapping precedence is file-source, package manager, then
disclosure-system mapping (114–120), followed by archive or WebCache lookup
(126–132). Loader hooks can intervene (151–168, 194–199). A mapped pathname
therefore does not identify which bytes a parser actually consumed. Record the
logical URI, mapping decisions, actual open and resulting byte identity.

WebCache.getfilename calls URL-transform hooks before its ordinary lookup
(555–559). Non-HTTP input may return directly (567–575); an archive reference
recurses (577–588). The offline branch can return a built-in cache path, or a
computed cache pathname even when absent (601–611). normalizeFilepath can
substitute an existing HTTP/HTTPS counterpart (351–378); urlToCacheFilepath
can use configured and built-in redirections (434–527). The proposed adapter
must reject undeclared substitutions and missing or changed bytes. An offline
flag is neither a byte-match result nor proof that every possible loader or
plugin path makes no network call.

WebCache.normalizeUrl uses platform and path operations (382–429).
ModelDocument.baseForElement has its own ancestor-base handling (1036–1063).
The existing static graph used a separate documented traversal. Their
equivalence has not been executed or proved for arbitrary inputs. Do not
replace the upstream method by urllib.urljoin while claiming native parity.

ModelDocument opens via FileSource.file with stripDeclaration=True in its
ordinary branch and invokes a parser with base_url=filepath (185–203). Retain
original bytes before decoder transformations and record parser-consumed bytes
or a precisely identified transformation. FileSource, ModelObjectFactory,
PackageManager, PluginManager and some helper behavior have not been inspected
in this unit. Parser external-entity behavior and complete no-network execution
remain open; absence of a DOCTYPE in this retained set does not settle them.

Session documents process-wide shared state and one active session per process
(28–39); run closes package/plugin global instances and constructs or reuses
the controller (141–161). RuntimeOptions declares requested values, not a
receipt of effective configuration. CntlrCmdLine sets offline mode before
options that may request resources (1678–1689). A future run must preserve
effective plugin/package, cache and disclosure-system state, structured logs
and ownership/close behavior. Existing selections remain unchanged.

## Bounded documentary resolution

The retained graph contains 27 resources and 3,551 reference occurrences.
The proposed map preserves their exact logical URIs and bytes, with identity
aliases only. For this static check, split resource and plain fragment; resolve
relative archive paths against the logical archive document and HTTP(S) paths
with the prior graph's declared method. Keep relative references relative to
their logical source, not to the physical .body storage filename.

Reinspect each XML attribute occurrence and its element path. Check an explicit
expected namespace against the target schema, and a plain fragment against a
unique id/xml:id. No implicit percent decoding, query rewriting, backslash
conversion, alternate scheme, case folding or extra URI alias is admitted in
this bounded subset. Retain an unsupported reference and request a method
extension; do not invent a successful resolution. The supplied set contains
no xml:base or DOCTYPE, so neither is handled by the checked subset.

Static closure covers only the enumerated import/include/redefine, xlink href,
typedDomainRef and schema-location hints. A future validator may discover
another resource. That event holds the affected validation, preserves its
reference and logs, and starts a new explicit acquisition/mapping decision.
It cannot silently use an ambient cache or turn this finite list into a claim
of complete DTS, filing-package or financial-semantic coverage.

## Exact dependency prerequisites

The retained pyproject declares Python >=3.10, fifteen base requirements and
three build requirements. These are compatibility ranges, not a resolved lock.
Keep the selected extras empty until a reviewed task needs them. Do not copy
the authoring interpreter's tfgpu packages into a proposed production baseline.

Before runtime promotion, identify the target OS/architecture, exact Python
build/ABI, Arelle source and distribution artifact, build backend and tools,
transitive distribution names/versions/hashes, platform markers/extras, and
native extension/library identities where relevant. Preserve source/build
and binary notices separately from the dependency graph. Pin the resolver
policy, mappings, local and built-in cache identities, effective plugins and
packages, disclosure system, parser/entity configuration and decoder behavior.
Then check actual opens, structured errors, schema/XBRL validation and portable
output correspondence. Missing fields remain null with reasons; no exact
version is guessed from a range, source date or this machine's environment.

This completes a documentary prerequisite specification, not the dependency
lock. Real-filing portable translation, installed compatibility, historical
taxonomy terms, distribution rights and independent acceptance remain open.
