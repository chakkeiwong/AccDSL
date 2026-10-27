# Native-XBRL evidence translation, proposed adjunct v1

This adjunct supplies a bounded proposed profile for the portable records in
L1/L2 of `language-ir-contract-v1.md`, using E1/E3, T1/T2 and I1. It addresses
MC01–06/23–25/27/30–35. Its profile, synthetic source packet, expected records
and consistency checker are in
`data/accounting-master/native-xbrl-translation-20261018/`.
The profile is a proposal awaiting independent implementability review; it
does not modify the active P16 index or register a production schema.

## Source, reading and financial meaning

Retain the complete original instance as a BlobRef and SourceVersion before
reading facts. Every fact, context and unit gets its own UnitOccurrence with
half-open byte offsets in those exact bytes and a structural path. An optional
XML ID supplements that locator; it does not replace it. Equal fact values at
different locations remain distinct occurrences and assertion candidates.
Offsets must come from an independently checked lexical source map in a future
adapter. A parsed tree, source line, fragment identifier or reserialization
alone cannot recover original byte offsets. The supplied offsets are authored
for the retained synthetic UTF-8 file, not produced by Arelle.

The documentary input packet is an authored reading of that XML, including
every retained field and raw span. It is not a serialization of an Arelle
session. LegacyImport retains the packet's exact bytes and original ID; the
separate SourceVersion retains the XML bytes. A future native packet needs
its own pinned decoder, upstream validation results and checked lexical map.
The packet's explicit fixture type labels are author assumptions, not inspected
taxonomy declarations. No XSD, DTS or XBRL validation is claimed.

Original tokens, XML-decoded text, proposed numeric values, declaration defaults
and presentation remain distinguishable. The profile does not ingest
effectiveValue or defaults as reported source text. Missing financial meaning
is Unknown with a reason and obligation_refs. A non-applicable unit is explicitly
NotApplicable. Neither is zero. All produced financial readings are candidates;
the converter has no admission or posting authority.

The fixture's reported_text concatenates decoded character data in document
order, including child text and tails. This is an explicit text view, not raw
XML or a scalar interpretation of mixed content. Nested element markup remains
in the original occurrence; mixed content produces no supported scalar value.

## Field correspondence and source boundary

The comparator is Arelle commit
`01f6a4656c2c6551d2f05f31c9d74366d133ee7e`, retained in the preparation source
directory. The accompanying source-anchors.json binds exact files and ranges.

| Source field | Portable destination and transformation | Refusal or distinction |
| --- | --- | --- |
| Complete XML bytes, origin | SourceVersion.original_bytes_ref, origin | Acquisition/publication/vintage/issuer are unknown in the synthetic case; filesystem time supplies none of them |
| Element ID, structural path, exact bytes | UnitOccurrence.locator and source_ref | IDs need not be unique in malformed input; duplicate IDs block reference resolution without deleting either occurrence |
| Fact element QName | ReportedAssertion.concept, expanded namespace/local name plus retained lexical occurrence | ModelObject.qname constructs a QName (225–230); full ModelValue resolution is not inspected here. The fixture expansion is independently declared against its namespace bindings |
| contextRef | ReportedAssertion.context_id_token; Context.source_context_ref links the separately retained context | ModelFact.contextID reads the attribute (179–181), then context looks up a dictionary (184–191). Missing/ambiguous context stays unknown |
| unitRef | ReportedAssertion.unit_id_token; Context.source_unit_ref | unitID strips whitespace (199–201). Retain original attribute spelling. No reference means unknown for a numeric candidate; a nonnumeric fixture may declare NotApplicable |
| Literal fact content | ReportedAssertion.reported_text and candidate value | value may substitute default/fixed (392–400); textValue joins parsed nodes (ModelObject 285–295). Neither is an original byte string |
| Decimal token | Exact reduced Rational in candidate value | Base-ten conversion only; no precision multiplier, balance-sign reversal or invented scale. Non-finite, malformed, empty or unresolved type stays unknown |
| Fraction numerator/denominator | Separate tokens and exact quotient | fractionValue 403–410 returns components. Zero denominator is retained but has no numeric quotient; a fraction-to-decimal presentation cannot replace it |
| xsi:nil | Explicit attribute evidence plus Nil tag when true/1 | Absence differs from an explicit false. Nil has no numeric value; do not call a source-mutating setter |
| decimals, precision | Independent Present/Absent tokens | 308–346 can supply type defaults. Omitted accuracy remains omitted source evidence; no rounding interval or unrounded amount is inferred |
| xml:lang | Explicit/inherited/configured language provenance would be separate | This profile retains the explicit attribute and leaves effective language unknown; 349–368 can supply inheritance/configuration |
| Entity identifier | XbrlContextEvidence.identifier scheme and decoded text | 1149–1158 can prefer validated xValue and otherwise return textValue. A scheme/value is not a resolved legal entity or book |
| Period children | XbrlContextEvidence.period preserves form and tokens; Context.time is a proposed date-only interpretation or Unknown | 1038–1102 delegates normalization to XmlUtil. Reporting end is not publication; forever is not an infinite forecast authorization |
| Explicit/typed dimensions | Ordered XbrlContextEvidence.dimensions, container and raw source spans | 1211–1235 can consult dimension defaults. Only explicit instance members enter the reported list. Typed XML is retained with inherited namespaces, not flattened into a guessed scalar |
| Other segment/scenario children | XbrlContextEvidence.non_dimension_spans | 1247–1263 separates non-XDT content. Uninterpreted content blocks complete financial context; it is never discarded |
| Unit measures | Ordered numerator/denominator expanded QName lists with multiplicity | 1545–1554 sorts measures; 1585–1597 assembles divide units. Preserve XML order separately; no implicit cancellation, currency mapping or conversion |

## Proposed date interpretation

For a valid four-digit Gregorian date-only duration, propose [startDate,
endDate+one calendar day). For a date-only instant, retain the original date as
the financial date; a next-midnight accessor value is a separate normalization,
not a later reported date. Reject an empty/reversed duration interpretation.
For dateTime, timezone uncertainty, forever or malformed input, this bounded
profile leaves financial time unknown and retains the source period unchanged.
It does not collapse intraday times into Date or assume the machine timezone.

XmlUtil.datetimeValue (969–1034) distinguishes date-only and time-bearing
values: addOneDay applies to date-only input, 24:00:00 rolls forward, fractional
seconds are truncated to microseconds, and some exceptions can leave a maximum
year sentinel. Its tzinfo helper (961–967) adds signed hours and positive
minutes directly. These are reasons to retain original tokens and require
independent validation, not proposed validation rules. No accessor was executed
and no categorical upstream conformance verdict is established here.

## Closed documentary profile

`profile.json` declares exact body fields and type signatures for SourceVersion,
UnitOccurrence, XbrlContextEvidence, XbrlUnitEvidence, Context,
ReportedAssertion, ConversionMethod, ImportMapping, ImportComparison and
LegacyImport. Every record uses exactly L1's six fields. Each kind has its own
versioned proposed schema; a profile cannot reinterpret a frozen native digest.
All body Ref links occur in dependencies, with no extra dependencies. Required
transitive record closure is finite and acyclic. BlobRefs require separate
exact byte closure. Dependencies and ImportMapping.outputs are canonical sets;
XML measure/dimension order, occurrence lists and mappings retain their order.

Every output body's top-level field has a mapping. source_path is a JSON
Pointer into the retained authored packet; target_path is a JSON Pointer into
the output record. Equal-decoded mappings require exact JSON typed equality;
all other mappings require a ConversionMethod Ref. Several fields may map to
one record and one source field may explain several candidate outputs. Context
and unit joins are explicit conversions, not string equality. The comparison
covers every output and ordered mapping, not just successful numeric facts.
Metadata fields kind/schema/key/revision are profile construction metadata,
not asserted issuer statements. A SourceVersion maps the original XML BlobRef,
not the packet's different BlobRef.

Each mapping must address its own source entry: the root for SourceVersion,
the corresponding context/unit for its evidence and occurrence, and the
corresponding fact for its occurrence, Context and assertion. Direct aliases
are source_blob to original_bytes_ref, fixture_id to document_identity and
attributes to source_attributes. Equal mappings point to the exact decoded
field; conversion mappings point to that owning entry. The checker separately
checks each converted field's stated semantics; a method name alone is not
evidence of a valid conversion. This scoped pointer convention is proposed
for this fixture, not a general multi-source provenance language.

The proposed methods specify construction, exact decimal/fraction conversion,
date-only interpretation, QName reading, explicit nil interpretation and
candidate Context creation. Unsupported readings remain retained and unknown.
The source packet also retains unmapped attributes and child content through
the complete original bytes and occurrence spans; this is archival retention,
not semantic completion of every source field.

Schema validity and correspondence are bounded engineering checks. Admission
requires a separate E4 review decision in a requested immutable view; the
input packet, proposed Context and converter cannot grant it. No operation
request, runtime result, accounting entry or external service is implemented by
these files. General native parsing, taxonomy resolution/validation, a checked
lexical map, real-filing translation, full context admission, exact dependency
locking, build compatibility and rights clearance remain open.
