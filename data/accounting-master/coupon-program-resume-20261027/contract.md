# Selected same-period resumption contract

27 October 2026. Implements accounting-coupon-program-resume-20261027.md.
MC05/11/12/13/16/17/18/24/25/26/28/33/34; W04/05/11/12/16/17.

Skeptical pre-run audit: the preceding prefix oracle checks financial equality
but does not by itself prove every runtime guard or every trace field. Therefore
an initial prefix must also equal a complete recomputation of the frozen
selected partial method. A newly supplied hash cannot authenticate changed
history. Exact source/selection/prefix identities are external premises, not
proof of real source truth. Do not modify frozen predecessors.

The selected plan binds source, selected registry, original opening, initial
current state, initial prefix instructions and full suffix. At most 64 suffix
commands are accepted into a plan. Reuse the existing static validator against
the original fiscal opening for method/schema validation; execute against the
actual midperiod current book with the unchanged typed event engine. Only
partial-coupon events are in scope. No report/carry/cross-period commands.

A checkpoint includes its cursor, complete accepted suffix trace, actual
current book, original-opening cumulative report, original refusal archive,
remaining suffix and one of paused_budget/complete/refused/resource_limited.
The cursor counts accepted commands only. Refused and resource-limited commands
remain first in the unexecuted suffix. A chunk may accept at most its positive
integer command budget. A terminal checkpoint is unchanged on another resume.

Validation recomputes the bounded prefix from the identified plan and compares
the whole checkpoint. Resume then extends only its accepted trace. This pure
evaluation is not durable exactly-once execution. The default 8 MiB trace budget
is inherited from DeclaredCompanyProgram/2; an explicit positive smaller budget
may be selected for deterministic resource-boundary controls. The budget is
part of the plan identity and accumulates across chunks. The count ceiling is
also plan-wide. Computational work spent validating is not a new accepted event.

The financial comparator independently builds every accepted state, journal,
dated flow and report from the external carry record. Chunk 1/2/all results
must have identical terminal checkpoints and match uninterrupted execution of
prefix plus suffix, where the combined command count is supported. Validity
checks distinguish economic guards, date/ID refusals, pause and resource limits.
Reports always start from the original January 1 book.

Primary criterion: full independent and uninterrupted comparisons on four
chart/action origins and four suffix families. Vetoes: source drift, cursor
skips, lost history, changed opening, different terminal outputs across chunks,
wrong report, or false admission. Local defects trigger repair; invalid upstream
evidence or three exhausted 120-second attempts stops this unit. Timing/size
are explanatory. No probabilistic ranking, actual accounting admission,
production persistence, arbitrary-method resume or unlimited resource claim.

Inputs use synthetic exact rationals and the existing operating convention.
Chunk sizes and a lower resource budget are explicit test conveniences, never
economic assumptions. Early diagnostic is one successful three-command suffix
under chunk 1 versus all, before the broader table. CPU only, GPU hidden,
native financial fallback disabled; no new dependency.

Attempt-01 audit repair: duplicate-ID diagnostics arise at different layers in
the two runners. Require exact duplicate_event versus duplicate_command_identity
reasons and identical rejected command/state; do not demand equal diagnostic
wrappers. All other complete comparisons remain unchanged. See repair-note.md.
