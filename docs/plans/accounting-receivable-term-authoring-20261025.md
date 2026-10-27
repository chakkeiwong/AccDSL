# Matched authoring for prospective receivable terms

25 October 2026. S3/S4/S5; MC02/05/08/10–13/16/19–22/24–28/30/32–35.
Baseline: the frozen ReceivableTermHistory/1 typed reference, two charts,
nine events and one carry per case, with the 61-file source lock. Version 4.24
integrates the semantics but does not yet supply textual authoring.

## Question and evidence contract

Can explicit text commands produce the exact same typed requests and complete
results as the checked structured term operations, including historical
assessment bases and carry? The comparator is the retained typed requests and
results, not agreement between two new adapters sharing the same code.
Pass requires source-to-typed-command round trips and exact correspondence for
every transition, carry and final state on both charts. Negative tests must
reject altered/missing/extra imports, malformed or duplicate inputs, unsupported
operations, stale terms, wrong types and attempts to override carry policy.
Unknown or refused commands retain the successful prefix without claiming
complete execution. Prior engine/schema/hash failures veto acceptance.

No accounting accuracy, language superiority, complete history, real-source
admission or production readiness follows. This is deterministic conformance;
statistical inference, seeds and GPU use do not apply. Preserve results under
data/accounting-master/receivable-term-authoring-20261025/ with exact requests,
results, sources, tests and a run manifest. Read-only replay must agree.

## Skeptical audit and assumptions

Reuse the frozen declared-command lexer/grammar and its bounded JSON string
semantics under a new explicit text profile. This is a compatibility choice,
not a new language default. Header translation must affect only the header;
quoted customer identities and premises must survive byte-for-byte in values.
The four existing import slots hold explicit opening book, schemas, term-state
configuration and report context. Hash-bound import data must reconstruct
exactly the supplied state and period-report opening; no migration or
no-prior-amendment premise is invented by the compiler.

Execution accepts only the three checked event operations and period carry.
The grammar can parse report commands, but this profile refuses them explicitly;
new report behavior is outside this increment. Carry requires its cutoff to
equal the current book date, uses the explicit report opening/mapping, and
delegates preservation policy to the frozen typed carry. Do not infer a
different closing date or fabricate transactions. Source and typed-input bounds
remain in force; adapter limits are inherited and identified by dependency pins.

The plan passes this audit. The earliest discriminator is the full first-chart
round trip against retained evidence, followed by all events on both charts.
A failure must be classified as parser, import binding, request construction
or engine refusal before repair. Do not modify frozen dependencies to make an
adapter test pass. Syntax rejection is a compile failure; stateful refusal is
an execution stop with an intact prefix. Unknown input is unresolved, not zero.

## Execution and next work

1. Add the explicit program envelope and text adapter; pin dependencies.
2. Exercise exact retained cases and adversarial source/import/state cases.
3. Record bounded logs and source lock; replay without rewriting evidence.
4. Refresh requirements/checkpoint and integrate authoring into a successor
   manuscript only after rendered review under a separate integration plan.

After that, reassess the next broader method gap against the mission, retaining
real-source reconstruction, fiscal/measurement methods and group/sector work.
E3 remains deferred. No installation, outreach, fee or background campaign.
