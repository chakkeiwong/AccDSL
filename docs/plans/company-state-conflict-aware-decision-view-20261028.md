# Conflict-aware decision view over the retained source selector

28 October 2026. C04/T03; MC05, MC10, MC11, MC25, MC33. Follow-up to
company-state-evidence-failures-20261028, whose22 cases and255 checks pass.

Audit finding: the old full result correctly labels conditional_conflict and
withholds a native definition, but its detached policy_evidence subrecord only
contains view/assertions/source_admission. A consumer that extracts that field
loses the unresolved/conflict status. The initial diagnostic did not directly
assert this interface requirement; a passing count did not complete the plan.
No existing production caller of the field was found in the scoped scripts,
tests or common-request path. Do not claim an observed production decision bug.

Repair the consumer boundary additively: call the pinned existing selector,
retain the full native audit result unchanged, and provide a separate decision
view whose outcome and executable-input status travel with the available
assertions. Conflicting observable assertions stay available as evidence of a
conflict, with no selected fact, native definition, probability or executable
permission. Unknown timing has no executable view. Invalid/unsupported results
stay unexecutable. A selected conditional view is still source-unadmitted and
is not authorization for production execution.

Primary criterion: all22 existing complete outcomes are preserved, and detached
views cannot label any of3 conflicts,2 unknown views,1 invalid or1 unsupported
case as supported conditional inputs. Selected views contain only the existing
safe projection fields. Full decision views before cutoff must remain identical
when only the future correction changes. Missing/extra-field and forged child
projection tests refuse. Assertions remain intact in conflict rather than being
silently censored. Neither truth nor source-family completeness is established.

Baseline: exact current information_views.py plus its source dependency chain.
No code in that frozen path changes. Pin inherited scripts before invocation.
Use an exact output comparison against all22 retained cases. The wrapper must
not reconstruct source selection, change supersession, merge aliases, assign
weights, or implement a new chronology model. It is a consumer projection only.

Vetoes: changed source hash, changed full native outcome, loss of observable
conflict evidence, unsupported status treated as usable, future metadata in the
detached view, or missing outcome discriminator. Stop that assertion and repair;
continue unrelated work. Case counts are explanatory only. No numerical default,
market probability, actual actor access, forecast, independent acceptance or
release promotion. Run CPU standard-library tests into a fresh exclusive
consumer-attempt directory and retain manifests and failed attempts.

