# Same-period continuation after a conditional tax assessment

24 October 2026. The question, baseline, vetoes and non-conclusions are in the
linked execution plan. The schema audit finds that direct invocation of the old
profile cannot retain a separate payable; reuse requires explicit extension.

ConditionalSharedTaxContinuation/1 requests contain an exact origin tax state
and its digest plus ordered operations. Recompute the origin with tax-state v1,
including its original full native report and loss proposal. Seed one complete
SyntheticReturnLeaseTaxBook/1 record by retaining every native field and account,
adding income_tax_payable, replacing the balances with the verified tax balances,
and retaining native, accrual and payment identities in a single seen history.
Append the origin's actual tax cash flows. Dates reflect the last tax operation.
Tax assessment coverage and original close cursor retain their separate meanings.

Operations are native {kind, event} or tax_payment {kind, event}. Native event
format and method selection are the original shared book's. The account schema
is explicitly extended to 26 accounts. The selected return monetary program is
instantiated with that entire registry; its memory input/output schemas retain
all fields. The original lease component kernel maps its exact journal to the
complete registry. No account is removed, netted or plugged to fit an old schema.

An ordinary event must be at or after the exclusive assessed endpoint and no
earlier than current state date, while remaining inside the declared native
period. Payments require explicit affirmative instruction, positive amount,
unique id, outstanding payable and cash, and may share the accrual day. Every
method changes only its declared component memory and financial footprint.
Current-tax expense and deferred balances are fixed after seeding; only explicit
payments can change payable. Post-assessment return adjustments are retained for
a future assessment; this increment does not calculate that reassessment.

The result includes the complete origin calculation, full 26-account book,
ordered trace and gross cash origins. Stop at the first refused operation,
retain the completed prefix and identify the remainder. Apply recomputes the
entire result with canonical comparison and returns an in-memory state only.
Repeated requests are replay, not globally unique durable commits. All source,
accounting, annual, persistence and financial-year-carry flags remain false.

Financial reporting uses the original opening and current complete balance
vector with the original classifications plus a distinct tax payable. Recompute
profit, equity, direct and indirect cash. The indirect bridge adds the movement
in income-tax payable, leaving trade payable separate. Four exact identities
must hold; stopped-prefix statements describe only completed events.

Tests compare original component effects where scopes match, independently
calculate shared-cash competition, reject ordinary events on the last assessed
day, preserve zero/deferred/tax states, and reject duplicate/tampered/unknown
requests. A finite first-year assessment in a two-year native window is an
explicit synthetic timing control, not annual completeness or a real company.
The next period-carry phase remains separate. Audit passes for this bounded
extension; a source mismatch or missing exact identity is a repair veto.
