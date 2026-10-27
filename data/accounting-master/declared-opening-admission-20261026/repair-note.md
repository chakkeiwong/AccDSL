# Opening-template preparation repair

The first preparation attempt rejected a rational declaration before writing
templates. MethodRequirements/3 accepts dimensional source types and lowers
them internally. Passing an already encoded rational type removed the required
dimensions/scale fields. Inputs and constants now retain original dimensional
types; the existing compiler owns lowering. Text/date/Boolean had masked that
mistake in earlier nonnumeric eligibility stages. No native code changed.

The first full run matched all 58 audited cases, then found a real mismatch on
a Boolean carry-policy value. Native equality rejects it as explicit_policy;
typed binding rejected it earlier as text:text. The policy stage now declares
exact structural field/value equality, the operation actually used by native
validate. Numeric/date predicates retain the typed requirement evaluator.
Original templates are archived under attempt-01; no frozen predecessor changes.
