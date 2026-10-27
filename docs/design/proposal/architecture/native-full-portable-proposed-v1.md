# Full retained-native documentary translation

This proposed full-file example composes the selected-source and source-hazard
conversion specifications without changing their frozen records or the core
native-XBRL proposed body types. It applies only to the pinned Apple instance
and its complete 1,328-element inventory. It is authored specification evidence,
not upstream output or a registered runtime profile.

Preserve all 1,127 fact occurrences, 193 contexts, seven units and schemaRef.
Every original occurrence keeps its byte interval, source path and XML ID or
explicit null ID. Retain full source context trees, typedMember subtrees and
namespaces in the documentary input. SourceVersion identifies original XML;
LegacyImport identifies the distinct documentary packet. All repeated facts
retain separate occurrence/assertion/context records.

Source-context and source-unit evidence use existing fields. Explicit dimensions
keep axis/member QNames and typed dimensions keep form=typed, member_token=null,
member_qname=Unknown and exact source span. All financial context fields,
including time, remain Unknown. Source periods are not promoted to financial
time. Source unit numerator/denominator are separately preserved, including
issuer-defined measures. Absent unit applicability remains Unknown.

The candidate policy is deliberately lexical. A unit-bearing decimal-looking
source string becomes a reduced exact rational Decimal candidate, without sign
changes, rounding or decimals scaling. Unit presence plus lexical form does not
establish taxonomy typing. Nil stays Nil. The seven unitless decimal-looking
strings retain Unknown Values, including exact reported characters and leading
zeros. Other strings are marked UnvalidatedText in the documentary packet and
mapped to portable Text by the separate decoded-unvalidated-text method. This
method preserves all characters, including escaped markup, without executing,
sanitizing or admitting their taxonomy type. The original lexical class and
taxonomy_type=Unknown remain in the packet. These distinctions prevent the
broader translation from silently generalizing the first twelve examples.

Every translated core body field has one owned source mapping. Exact values use
equal_decoded_value; conversions/Unknowns/constants use the bound general method,
and UnvalidatedText Value conversions must use the dedicated text method.
The existing closed schemaRef adjunct retains name, attributes and typed local
occurrence Ref with resolution_status=not_run. It remains outside core Record
schemas and supplies no resolved taxonomy edge.

Portable type/Ref/field correspondence and every original-source join are checked.
The complete inventory reconciles occurrence coverage. All financial interpretations
stay candidate-only. Full XML translation does not establish full disclosure
meaning, compliance, taxonomy/XBRL validity, source publication availability,
upstream behavior, installed compatibility or an operating accounting product.
