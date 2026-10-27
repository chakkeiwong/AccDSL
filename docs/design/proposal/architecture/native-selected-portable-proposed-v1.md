# Selected native filing readings in the proposed portable envelope

This additive specification instantiates the existing proposed native-XBRL
record bodies for twelve retained Apple FY2024 native facts. It changes no
registered type or frozen fixture. These are authored specification examples
based on actual source bytes, not records emitted by Arelle or an installed
AccDSL importer. The source reader and record profile retain their separate
evidence labels.

## Identities and source ownership

The input is the exact `native-occurrence-bytes-20261018/readings.json`, whose
historical `portable_record_status` remains `not_yet_translated`. That token
describes its original evidence state. This successor records a separate
translation without altering the input. The LegacyImport original-bytes BlobRef
identifies that documentary JSON packet. SourceVersion original-bytes BlobRef
identifies the retained 1,359,552-byte XML instance. They must differ. The input
packet is closed by its pinned identity and checked reader, not by the synthetic
PACKET schema, which has an incompatible authored-fixture origin.

Each selected fact, context and unit has its own UnitOccurrence. Locators use
absolute, zero-based, half-open UTF-8 byte intervals in the XML, plus the
retained source path and unique XML ID. No serialization supplies these offsets.
SourceVersion keeps all twelve namespace bindings, the retained path as its
document identity and a `retained-file:` origin. Acquisition, issuer admission,
publication and historical availability remain Unknown. The registrant text
and source entity identifier are evidence, not an admitted issuer mapping.

Every body field of a translated SourceVersion, UnitOccurrence, source context,
source unit, candidate Context or ReportedAssertion receives exactly one
ImportMapping entry. Its input pointer belongs to the corresponding packet
entry; global source metadata uses the packet root. Exact equality uses
equal_decoded_value. Structural reshaping, joins, Unknown annotations, explicit
constants and type changes use an explicit ConversionMethod. Metadata records
ConversionMethod, ImportMapping, ImportComparison and LegacyImport are checked
against this specification separately, avoiding a circular mapping.

## Conversions and preserved uncertainty

Source contexts preserve identifier scheme/text, unadjusted source period
tokens and explicit dimension axis/member/container. The selected dimension
has an exact original byte span inside c-13. No additional non-dimension
qualifiers occur in these four selected contexts. Unit numerator/denominator
are separate lists; unprefixed `shares` expands using the source default
namespace. QName representation splits an expanded name into namespace URI
and local name without changing its meaning.

Each fact gets a separate Context even when its source context or value repeats.
Source-context and source-unit references join by exact XML identifiers. An
absent unit stays Unknown: the selected source alone does not establish that a
unit is inapplicable. Financial legal entity, book, perimeter, basis, currency,
time, calendar and dimensions all stay Unknown, preserving the prior reasons
and adding the portable empty obligation-reference list. A duration or instant
in source evidence is not an admitted financial time.

ReportedAssertion preserves XML-decoded character data, all attributes, concept,
raw context/unit/decimals/precision/language tokens and exact candidate values.
Absent source text on the nil element maps to the empty portable reported_text
string; the Nil value and original packet retain its absence, so this is an
explicit conversion, not equal decoded value. Decimals is not a scaling factor.
Numeric candidates use the previously checked exact reduced rationals.

The separate `decoded-markup-as-text` ConversionMethod maps f-356 MarkupText
to portable Text by retaining the decoded characters verbatim. Its original
MarkupText tag and escaped original XML remain in the pinned packet and source
bytes. Text here describes the portable string representation, not taxonomy
typing, plain-text sanitization, executed markup or accounting interpretation.
The value-field mapping must name this method; the general conversion method
cannot silently absorb the distinction.

Root language en-US remains packet evidence. The fact has no explicit language
attribute and effective language stays Unknown pending the applicable rule.
Both f-207 and f-256 survive as distinct assertions and occurrences despite
identical source context, unit and value.

## Validation boundary

Use the unchanged six envelope fields, proposed body types, canonical Ref
algorithm and complete dependency lists. Require exact output membership, field
coverage, source ownership, conversion identity and semantic correspondence.
Corruption examples rebuild dependent Refs where necessary so they test the
semantic error rather than merely an obsolete digest. Source spans, per-share
denominator, dimensional context, nil/zero/sign/decimal values, repeats, absent
language and financial Unknowns are separate checks.

This finite translation leaves full-filing translation, taxonomy/lexical
validation, installed compatibility, original acquisition provenance and
financial admission open. It supplies no extraction accuracy, legal compliance
or empirical forecast evidence.
