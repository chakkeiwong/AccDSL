# Source method recipes

The audited plan is docs/plans/accounting-method-recipe-source-20261026.md.
The protected constructor and expander remain the semantic owners. No new
financial operation or implicit default is introduced.

A parameterized_recipe header selects text/typed/transition profiles, followed
by context, input_schema, ordered parameter(name,type,source), residual and one
begin_method/end_method block in the existing complete method declaration
grammar. Parameter sources are event_input, event_metadata, book_metadata,
input_schema and pointer with literal/previous-parameter segments.

Method scalar arguments accept (parameter "name"). Nested memory data may
use (record (field "name" VALUE) ...) or (array VALUE ...); ordinary exact JSON
literals remain available for data. Requirement manifests, monetary formulas,
postings and flows retain direct declarations and prefix expressions. Manifest
selection hashes are computed after substitution, not manually authored.

An ordered_expansion header contains a complete base recipe block, map_pointer,
row_type declarations, row_replace and suffix_replace declarations, residuals
and end_expansion. A replacement explicitly gives an id expression, path
expression and scalar value expression. The replacement opcode and literal
write-value wrapper are fixed by the verb. Expressions are const(type,value),
row(field), key(), event_metadata(field), event_input(name,type), date_lt,
date_le, if, operation_id(prefix), and path with text-valued child expressions.
Both branches are preserved for the original expander's type checks.

The source parser rejects duplicate/incomplete syntax and retains half-open
UTF-8 spans. Structural lowering is separate from contextual construction.
Template construction errors identify the method/expansion declaration span
rather than pretending to know one exact token. Parent offsets for embedded
blocks must be translated to the original source. Unused/forward parameters,
scope, row types, pointer escaping and operation bounds remain original checks.

Alternative rejected: whole-template JSON or generic node-tree syntax would
avoid the source-authoring obligation. Existing method syntax plus explicit
parameter/data expressions exposes the actual arithmetic, posting and memory
operations while preserving typed structure. The finite tests support this
surface only; broader financial algorithms and acceptance remain open.
