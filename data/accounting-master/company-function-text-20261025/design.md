# Matched function source and exact locations

The frontend accepts UTF-8 bytes, or a string encoded without normalization.
The header is: program CompanyFunctions/1 <quoted-name>;
Main input, literal, input_ref, node and output declarations retain the earlier
expression notation. Function declarations use an explicit block:

    function complement;
    parameter discount '{"kind":"number","dimensions":{},"context":null}';
    returns '{"kind":"number","dimensions":{},"context":null}';
    param_ref d discount;
    literal one '{"kind":"number","dimensions":{},"context":null}' 1/1;
    node r sub one d;
    result r;
    end_function;

A call is: call <node-id> <function-name> <argument-node>...;
Functions may refer forward; recursion is rejected by the pinned typed compiler.
Function blocks cannot nest. Parameters precede returns, which precedes local
nodes; result ends the body and must be followed by end_function. Main
declarations may surround function blocks, but end_program occurs exactly once.
Blank lines are allowed; comments and includes are unsupported. Each nonblank
physical line contains one semicolon-terminated declaration. Semicolons inside
quoted tokens are literal text, not statement separators.

Types are strict JSON with duplicate keys and nonfinite constants rejected.
Values use true, false, unknown or canonical rational tokens. POSIX-style token
quoting is syntax only: no shell execution, interpolation, command substitution,
environment lookup or host eval. Quoted command-looking names remain text.

The result binds source_sha256, typed request_sha256, pinned compiler_sha256,
frontend_sha256, the exact typed request and its compilation. A declaration
record contains its kind, path in the typed request, zero-based byte_start and
byte_end (end-exclusive), one-based physical line, and one-based Unicode-codepoint
column_start/column_end (end-exclusive). Its slice includes the semicolon and
excludes leading/trailing spaces or tabs and line endings; each slice has a
SHA256. End markers name the enclosing path with their own distinct kind.
Locations always address original bytes, never a canonical rendering. Expanded
node origins can be joined to declarations by function scope/node identity;
this is not a runtime stack debugger.

LF and CRLF are accepted and preserved by source hashes and byte offsets. Lone
CR, NUL, UTF-8 BOM and other ASCII controls except tab/LF are refused. No Unicode
normalization is applied. Canonical rendering emits LF and deterministic quoting;
input/output mapping keys are sorted, while function/parameter/node list order
is preserved. Rendering may differ from source yet reconstruct the same request.

Convenience limits:524,288 source bytes,16,384 bytes per physical line and12,000
declarations. They precede typed/expansion checks and are not performance claims.
Compiler hash failure refuses source before semantic admission. Compilation
evaluates no expression value and generates no events. A selected division by
zero can parse/compile, then return invalid when separately evaluated.

This syntax covers bounded functions, not all simulator methods, module dispatch,
dates, polymorphism or endogenous decisions. No temporal, historical-execution,
real-behavior or forecast admission is inherited.
