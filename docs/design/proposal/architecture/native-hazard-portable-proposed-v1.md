# Portable examples for typed dimensions and untyped source tokens

This proposed adjunct reuses the native-XBRL Record bodies unchanged. Its
authored examples come from the complete retained-instance structural inventory.
They are specification examples based on source bytes, not upstream output.

Four typedMember occurrences in c-58 through c-61 preserve their segment
container, lexical/expanded axis name and exact original typedMember span.
The existing Dimension form is typed, member_token is null, and member_qname
is Unknown because a typed domain subtree is not an explicit member QName.
The immutable documentary packet retains the entire subtree including domain
element name, text, attributes, children, tails and inherited namespace bindings.
Original XML bytes remain separately identified by SourceVersion. The source
dates are not assigned financial-time or taxonomy-validated scalar meaning.

The seven unitless decimal-looking facts f-57, f-59, f-13, f-14, f-934, f-935
and f-1127 retain exact reported_text, all source attributes and source-context
joins. Their Value is Unknown with the reason that lexical digits do not establish
taxonomy type. This preserves CIK 0000320193 exactly. source_unit_ref also stays
Unknown because an absent unitRef alone does not prove applicability. All
financial context fields and effective language remain Unknown as in the
preceding selected translation. Source c-1 and c-128 support these joins.

The schemaRef at root position 1 lacks an XML ID. Its UnitOccurrence uses
element_id=null, exact byte span, source path /1/1 and its original SourceVersion
Ref. Its portable key is a documentary occurrence key, never an invented source
ID. A separate closed source-link adjunct has precisely these fields:
schema=accdsl.native_source_link.documentary.proposed.v1, status=proposed,
occurrence_ref (the typed UnitOccurrence Ref), expanded_name (source QName),
source_attributes (ordered name/value pairs), and resolution_status=not_run.
It preserves the original schemaRef name and attributes, including xlink:href,
without asserting retrieval, taxonomy closure or resolved reference identity.
The adjunct is outside the core Record set and is not a registered type.

Every translated core body field, including the ID-less occurrence, has one
owned mapping into the documentary packet. Structural reshaping and deliberate
Unknowns use the named general ConversionMethod bound to this specification.
Exact decoded values use equality. The source-link adjunct is separately
checked against its packet entry and its resolved local occurrence Ref; it does
not add a circular Record dependency. LegacyImport points to the documentary
packet BlobRef, while SourceVersion points to the retained XML BlobRef.

The finite packet does not claim complete fact or context coverage. The source
schemaRef, typedMember subtrees and unitless lexical candidates remain evidence;
taxonomy validation, semantic normalization, accounting admission, installed
compatibility and full-filing translation remain open.
