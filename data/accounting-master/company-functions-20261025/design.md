# Optional reusable pure functions

Profile `CompanyFunctions/1` contains `name`, `inputs`, `functions`, `nodes` and
`outputs`. Inputs and ordinary nodes retain CompanyExpressionsDraft/1 types and
canonical rational/Boolean/unknown values. A function declares `name`, ordered
`parameters` (`name`, `type`), `return_type`, local `nodes` and one `output`.
Local `param` nodes name parameters. A `call` node names a declared function
and ordered argument node IDs. Functions cannot read program inputs directly.
No host callable, import, file name, random draw or state mutation is permitted.

All function bodies, including unused functions and conditional branches, are
statically checked. Duplicate declarations, absent arguments, wrong parameter
or return types, lexical capture and cyclic local/call graphs are invalid.
The compiler expands each call to fresh local nodes; parameter nodes alias
caller arguments. Repeated calls share no local identities. Expansion origin
maps identify definition nodes and call sites. Declared argument dependencies
are retained separately from effective result dependencies, because an unused
parameter contributes no value to the result.

Evaluation is demand-driven, exactly as for manually inlined expressions.
Unused arguments and unselected conditional branches need not evaluate. Their
types and references still must be valid. An unused argument containing a
well-typed division by zero therefore does not invalidate a known result.
An unknown argument used by the result remains unknown; a known zero divisor
in the selected result remains invalid. This is an explicit semantic choice,
not an implicit call-by-value language.

The pinned predecessor expression engine supplies all arithmetic, type/context
combination, unknown propagation and evaluation. Its SHA256 is
`cd80145f61266346f15bdfa82062790bdeb8f4223c75beb1387ae5b140b2d449`.
The optional compiler checks that hash before loading it under a private module
name. It does not modify or monkeypatch the predecessor. Legacy metadata hashes
use their original escaping; the new request identity preserves Unicode, with
the two identities explicitly separate.

Initial convenience bounds: 32 functions, 16 parameters per function, 256 source
nodes per scope, 16 function-call levels, 64 local expression dependency levels,
and 2,048 emitted nodes across validation templates and the final expansion.
At most 2,048 scope visits are allowed as well, including alias-only calls that
emit no new arithmetic nodes. Template validation consumes these same budgets.
The complete serialized request is bounded to 262,144 UTF-8 bytes. These limits
are checked and reported; they are not scalability or performance claims.
Expanded graph depth must also remain within 64 before the old recursive
analyzer runs. Forward references are allowed within these bounds.

A lowered graph uses the old profile and can be supplied to its existing
policy adapter. New function-request, compiler and definition provenance must
accompany that graph; old temporal evidence is not inherited. This increment
exposes typed JSON declarations only. Matched textual syntax, parser spans,
portable module integration, dates, polymorphism, recursion, endogenous event
schedules and simultaneous behavioral solving remain open. Definitions and
their values must not be presented as estimated behavior or accounting policy.
