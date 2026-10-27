# Compose grouped queries with guarded state requirements

26 October 2026. MC20/24/25/28/33/34; S2–S4. Governing Version 5.13
remains unchanged while this internal design increment is checked.

Question: which query outcomes can become known or unknown scalar bindings
without allowing a missing, ambiguous or invalid query to satisfy a guarded
financial-state requirement accidentally? The preserved baseline is
MethodRequirements/3. Its false guard intentionally makes its body inactive;
required_known independently demands a known value. This behavior must remain.

Audit first: use a small truth table against the actual preserved engine.
Check active, inactive and unknown guards with known/unknown bodies and
required_known. Compare complete outcomes against explicit expected activation
and consequence, including no_active_requirements. No native financial calls.

Then implement a finite typed QueryGuardedInvariant/1 adapter. Each named query
recomputes GroupedRowQuery/1 from bound source inputs. Bind count, has_row or
selected_field explicitly; input types/roles must agree with the selected
guarded manifest. Selected scalar fields are known only for unique selection.
Allowed none gives has_row=false and selected_field=unknown. Ambiguous and
unresolved outcomes make has_row and selected fields unknown, never false.
An invalid query is a hard structural failure even behind a false guard.
There is no fallback value, tie breaker or invented row. Count is a
dimensionless exact rational with explicit type, not money.

Named queries include an explicit on_ambiguous choice (invalid or unresolved);
the selection requirement is part of the invariant declaration. Unknown query
inputs and incomplete coverage make the whole adapter unresolved even when
all consuming predicates are inactive. Allowed none is different: the
declared guard can legitimately make a nonexistent row's predicate inactive.
Required-known can still require that row, and a required query can refuse
none at its own allow_empty boundary. Preserve original engine findings and
query outcomes so consumers can distinguish inactive from satisfied.

Skeptical audit: this phase does not replace the native term validator or infer
all histories. Static finite queries alone do not enumerate every claim or
assessment. Dynamic query templates and per-parent/per-child rule instances
are a later explicit dependency. A successful guard truth table cannot close
that gap. Do not add a second predicate evaluator; reuse preserved v3.

Baseline/comparator: original dictionary scans supply selected values; the
unchanged v3 engine is called separately with those values. Full binding,
status, reason and v3 assessment comparisons are primary. Adverse cases include
missing group, absent row, unknown input, tied greatest, wrong binding type,
missing/extra binding, undeclared query, unused query and stale selection.
Native term/lifecycle/build callbacks disabled; freeze all query dependencies.

Defaults and risks: finite named-query count is a compatibility bound, not
a product restriction; verify overflow and no truncation. Exact scalar types
come from projection declarations; test wrong units/context even on empty
groups. Guard behavior is inherited and reviewed through the truth table, not
assumed to be whole-rule success. Ambiguity policy is explicit, not inherited.

Frozen-byte drift, input mutation, false known values or incorrect structural
success veto promotion. Harness/implementation defects trigger repair. Counts
and runtime are explanatory; no accounting authority, scientific ranking,
full validator or production readiness follows. Save design, probe, full
comparisons, controls and run manifest under
data/accounting-master/query-guard-composition-20261026/. CPU-only bounded work.
Afterward audit dynamic per-parent/per-child rule binding against the native
obligation table, then author the smallest complete term-state declaration.
No agents, commits, installs, GPU, paid review, outreach, publication or E3.
