# Finite authored program composition

AuthoredCompanyProgram/1 supplies an opening book, book/report schemas, report
mapping, typed memory definition, exact hashed registry population and ordered
commands. Each event selects an explicit registry and method. A registry may
also supply method-input schemas; these are hash checked and must agree with
shared book schemas, but are not silently inserted into report requests.
This preserves the original native report/carry request identity.

The whole envelope and source/method identities validate before execution.
Registry entries validate against the actual current book when the command
uses them. Future-state validation is not fabricated. The next state is copied
only after native success and typed-book validation. Any refused command
retains the exact successful prefix, current state and unexecuted suffix.
Duplicate command identities are refused at their actual position.

Report and carry requests use the unchanged native functions. Carry policies
are explicit per leaf; there is no inferred preserve/reset policy. The typed
memory definition validates both sides. Reports advance the observed date but
do not assert event-population completeness. All admission/durability flags
remain false. Result verification recomputes the complete finite program.

The retained lifecycle materializer is used only to construct comparison
fixtures, before the program runs. Runtime consumes authored sources and typed
definitions directly. Explicitly recorded event projection preserves the
original specialization boundary. This finite program does not yet provide
general source-language syntax for registry resources or dynamic specialization.
