# Matched text authoring for pure company functions

25 October2026. S2–S4; MC13/14/23/24/25/26/28/32/34/35.

Question: can bounded function source text represent exactly the checked typed
declarations and preserve their full policy/accounting consequences? Comparator:
the sealed CompanyFunctions/1 compiler and six saved policy cases. Primary
criterion: exact text/typed identity, deterministic canonical rendering and
matching full financial results. Veto: ambiguous scope, duplicate declaration,
wrong type, lost unknown, incorrect raw-byte/source-span binding or host-code
execution. Parser/build counts are explanatory only.

The grammar extends the existing line-oriented expression notation with explicit
function, parameter, return, parameter-reference, call and end-function forms.
Use quoted tokens and a strict duplicate-rejecting JSON type decoder. Preserve
Unicode text exactly; do not normalize names or source bytes. Text and typed
request identities differ and are both retained. Source locations refer to
the original UTF-8 bytes and lines, and never to canonical re-rendered text.

Skeptical audit: reuse the exact function compiler for semantic validation,
not a second type system. Parse only; compilation must not evaluate arguments
or generate events. Bound raw bytes, line lengths and declarations before
expansion. Defaults are scoped engineering limits, not throughput evidence.
Every accepted declaration maps to a source span; no file include, import,
shell expansion or external function body is admitted. Keep unused-argument
and unknown semantics inherited from the pinned compiler.

Execute: specify a compact grammar and error behavior; implement the optional
frontend; check nested functions are refused, forward calls work, duplicate
keys/names and malformed endings fail, and quoted Unicode/CRLF source locations
reproduce exact byte slices. Round-trip all six fixtures and compare complete
financial results. Record the exact tests and independent source-offset checks.
Then integrate only checked outcomes into a protected manuscript successor and
refresh full coverage before selecting the next broader simulator dependency.

This is bounded reference language work. Arbitrary functions, polymorphism,
dates, endogenous scheduling, simultaneous solving, actual behavior and
historical/forecast admission remain open. A parser failure triggers local
repair; an invalid protected baseline is a continuation veto until resolved.
