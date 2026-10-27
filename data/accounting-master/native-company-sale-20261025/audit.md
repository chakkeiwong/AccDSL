# Pre-implementation native sale audit

Question, comparator and vetoes follow accounting-native-company-sale-20261025.md.
Inspected the exact native invariant and sale branch, structural schema, generic
book transition and named direct-event binder. The native transition must remain
outside the adapter's computation; a monkeypatch test will make it raise if called.

Material defaults: native fixed owner/chart is an enforced source domain, not an
inferred general company profile; all existing lot IDs form a fixed closed memory
schema; native account classes are explicit; metadata date uses the new binder;
global resource limits retain the existing reference bounds. Extra lots are the
first discriminating case, followed by native controls and refusal categories.

Full native invariant validation on import/export is appropriate here: the purpose
is to preserve the selected native domain while the generic effects compute the
transition. Exact native comparison alone would otherwise miss stale complementary
state. If an imported state is structurally malformed, classify invalid; valid
native-state domain refusals preserve their native status. Audit passes for this
bounded adapter. No statistical,whole-company,source or accounting promotion claim.
