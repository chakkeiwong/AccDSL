# Named company methods and direct clocks — checked

CompanyMethodRegistry/1 selects declared data-only methods by name under a pinned
company context. CompanyMethodCall/1 checks account role classifications, schemas,
exact input populations and method identities. Date and identity bindings are
derived from actual event metadata; callers cannot supply a conflicting duplicate.
All entries are statically prepared before any selected predicate is assessed.

Eighteen focused methods pass. Twenty-one exact comparisons cover two company
payment layouts, a complete-lot sale and unknown/false applicability findings.
Materialized requests, entire transitions and provisional applications match the
explicit CompanyBookTransition/1 comparators. No underlying effect semantics change.
The regression suite retains24 company-book methods and their35 native comparisons.

The clock test makes a sale date precede the native tax close while retaining a
valid generic book date. Binding the predicate's date to that event rejects the
sale. Supplying another date input is rejected before the method runs. This is
direct-event clock evidence; assessment, measurement and carry clocks are unsupported.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Integrate bounded named binding | Exact request/transition/application comparisons pass | Conflicting dates, stale identities, schema/type errors and malformed unused entries rejected | Native domain and import/export coverage incomplete | Integrate and execute audited native-domain boundary | Method admission, generic native compatibility, accounting compliance |

No candidate repair was needed after the audit. Static inspection and tests agree
on the declared direct-event scope. The strongest alternative explanation is that
an explicit comparator itself omits a native prerequisite. native-domain-audit.md
lists this risk rather than promoting the fixture to an adapter. A failed native
invariant would block that adapter but would not invalidate named data-only binding.
S1–S5 remain partial,S6 held,S7 deferred. No whole requirement closes.
