# Explicit late partial-coupon instruction

27 October 2026. Implements accounting-coupon-partial-settlement-20261027.md.
Skeptical audit passes for a new selected method; predecessor programs are frozen.
The upstream carry record and its refusal archive are external identified inputs.
Selection binds that exact record, current next-opening and a new typed registry.
Only the cumulative paid2 amount and phase change in contract memory; original
action2 remains none and the original due-date refusal remains in the archive.

The example pays 85/16 on 2028-01-02, or two instalments of 85/32 on January 2
and 3, using only carried cash. This is an authored synthetic instruction. Both
leave cash zero, payable 1/16 and paid2 85/16. No income or expense is recognized
again. A partial-only method requires 0<amount<outstanding and amount<=cash;
the strict remaining-claim condition makes its partial2 phase exact. Full
settlement already exceeds available cash in these retained cases and needs a
separately supplied funding event. No funding, penalty or default is invented.

Primary criteria: full independent state, journal, flow, report and immutable
history equality on draw/pay and draw/draw origins on both charts. The selected
wrapper freezes the new registry and invokes the existing typed program/runtime;
native financial fallback is disabled. Check the source-defined arithmetic for
cumulative paid2, exact pre/postconditions and no hidden callback. Separate
instructions can share final balances while retaining distinct dated gross flows.

Adverse controls: early/duplicate IDs, stale origin/selection, impossible payment,
zero/negative amount, overwritten cumulative paid2, reset used/action history,
changed cash-flow activity, lost refusal, and false admission. Retained outputs
must reject corruption; a balanced result alone is insufficient. Replaying a
pure evaluation is not durable-store idempotence. Event/source completeness and
actual contractual/accounting applicability remain unresolved. At most three
fresh 120-second CPU attempts, GPU hidden, no dependency installs.
