# Closing and carry audit

Inspected native_reports.carry and the checked generic report. Native carry resets
interest and tax memory;these are domain rules,not generic defaults. Require exact
per-leaf policies and explicit retained account. Do not treat a passing report as
authority for a completed fiscal close. This reference carries recorded balances
provisionally and retains all incompleteness flags.

Independent derivation:temporary balance sum S=-profit. Closing entries -b sum
-S;retained entry S balances the journal and increases credit equity by profit.
Cash and all other permanent accounts remain unchanged. Positive and negative
profits must both work. Period endpoint is structural timing only. Preserve IDs;
the close itself receives a new identity. No silent migration or tax-date advance.

Primary criteria and vetoes match the plan. Source bounds and deterministic tests
are sufficient for this engineering reference,not accounting promotion. Strongest
alternative explanation is a declared but economically wrong reset;the engine
checks type and explicitness,not authority. Test memory policies exhaustively and
retain their provenance. Audit passes;no human choice or global blocker is known.
