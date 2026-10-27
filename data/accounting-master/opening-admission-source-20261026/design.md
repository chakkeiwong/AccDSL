# Direct opening-admission source

Question, comparator and evidence criteria are in
docs/plans/accounting-opening-admission-source-20261026.md. The plan passes
skeptical audit: stage order is observable and must survive; opening admission
must not silently validate future commands. The existing typed compiler and
admission evaluator remain the semantic owners.

The document begins with opening_admission and explicit text/typed profiles,
then context, dependency(file,digest,reason), residual and ordered stage
declarations. A stage header gives id, operation and reason. Within it, one
check declaration supplies the operation's arguments, or predicate binds and
a begin_rules/end_rules block supply the existing MethodRequirements/3 rule.
Every stage ends with end_stage; the document ends with end_opening.

Structural check argument forms are: record_fields(path,fields),
record_values(path) with repeated record_value(name,literal), text(path,label),
equals(path,literal), typed_book(), map_values(path,schema),
role_population(roles), role_injective(), role_classes() with repeated
role_class(role,classification), cash_role(role), memory_leaf(),
memory_type(type), opening_report(), commands(maximum). Schema, path, field and
equality literals retain exact JSON notation. The operation and its ordering
are always directly declared; no complete algorithm JSON is accepted.

Predicate bindings are prefix expressions: (path PATH_JSON TYPE_JSON),
(role_balance ROLE_STRING TYPE_JSON), (memory_pointer TYPE_JSON). The original
opening compiler validates binding roles/types and unconditional predicates.
All stages compile before admission, including later stages after a failing
envelope. External dependency digests refer to reused semantics; changes to
authored predicates recompute template identities without manual hash edits.

Resource limits, token rules and UTF-8 source spans reuse the eligibility
frontend. The bounded limits have compatibility provenance and are engineering
choices, not performance evidence. Exact full-template/result equality is the
primary criterion. Counts and source length are explanatory. Failure location
granularity is recorded; unknown semantic detail is not described as token
precision. No forecast, whole-language, accounting or acceptance claim follows.
