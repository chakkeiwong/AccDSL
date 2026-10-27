# SelectedTermProgram/1

This bounded contract composes the already implemented SelectedTermEventText/1
executor. Inputs are a closed program, independently reviewed selection and its
expected digest. The program supplies its name, complete contract/rule source,
opening state, supplied coverage and 1–64 ordered commands. Each command has a
unique program ID and complete existing term-event or carry request, including
the expected-state digest. No request is rewritten to make a stale request fit.

The selection binds the entire program's canonical and insertion-order identity,
exact contract/rule source bytes and selected typed term rules. Identity helpers
compute transport hashes; they do not confer review or source authority. Changing
even a source comment/residual, opening, command order or coverage requires an
independent revised selection. The runner never makes that choice itself.

Compilation validates closed envelope, size/command limits, source structure and
selected identities before any command. Source and structural failures return
invalid_program, executed=false and no prefix. After compilation each command
uses the existing source executor and the current full state and supplied
coverage. Only its successful proposed result advances the local state. The
executor's returned coverage is inherited; there is no population generator.

All commands succeeding yields complete_provisional. A first-command refusal
yields refused; a later refusal yields partial, preserving every complete
successful result, the unchanged last successful state and coverage, the exact
failed command/result and untouched remaining commands. Underlying refusal,
unknown and failure stages are retained. The runner does not retry, skip,
normalize or replace a failed command. Inputs are never mutated.

The selected carry policy preserves immutable terms and resets the cursor. Its
complete report request/result remains part of the financial comparison. There
is no arbitrary standalone report command or generic selected-company migration
in this profile. All effects are local proposals; no store is committed and
source/accounting admission, actual population completeness, production
readiness and durability are not established.
