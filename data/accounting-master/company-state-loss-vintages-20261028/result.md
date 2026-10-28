# Legal loss vintages and conditional tax

28 October 2026. C04, original SIM-F042. Attempt01 passes211 checks across28
loss proposals and11 apply checks using the unchanged reconciliation and
conditional loss-ledger modules. All treatment, eligibility, utilization and
nonexpiry premises remain explicitly synthetic.

Loss40 is generated in2026. Income30 in2027 uses30 and leaves10. Income30 in2028
uses only10, leaving taxable income20 and conditional gross current tax5 at
the supplied rate1/4. The same lot retains its origin, original40, used40,
remaining0 and expired0. Distinct step IDs and contiguous intervals preserve
the sequence. A separate negative10 branch after generation retains the
original40 and adds a new10 vintage, totaling50. The same negative10 after
using30 gives remaining10 plus new10, totaling20. Neither branch produces
cash, a refund or a deferred-tax asset.

Zero and fractional income preserve exact arithmetic. The expiry control
permits use30 on December31 before an exclusive January1 expiry and expires
the remaining10 at period close. The following income30 has no eligible
balance and produces conditional tax7.5. Attempted use on an exclusive
December31 expiry refuses. These are the declared close-day rules, not a
statement of any actual jurisdiction's law.

Overuse, duplicated lot use or step IDs, omitted intervals, forgotten lots,
reset balances, wrong jurisdiction and forged hashes refuse. Unknown cap,
eligibility, expiry or opening inventory remains unresolved; false eligibility
is unsupported. An altered proposal cannot be applied. The independently
supplied annual financial openings establish only loss-ledger continuity,
not native financial-book carry across those years.

One control exposes a necessary source boundary. A caller can invent an extra
loss30, alter the lot's original quantity and the prior history consistently,
then recompute the input digest. The conditional ledger accepts that internally
consistent premise and allows tax0. It is wrong relative to the retained
loss40 history, whose correct second-year conditional tax is5. Comparing the
request to the exact prior accepted state and original lot quantity detects
the substitution. Internal conservation and a self-supplied digest do not
authenticate legal history. The current result claims no such authentication;
source/previous-state binding remains a separate admission requirement.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain original recurrence discriminator |40/30/30 and negative10 branches agree with independent recurrence and lot histories | Double use, lost history, wrong expiry and unknown handling checked | Actual eligibility, caps, expiry and taxable income | Preserve source and prior-state bindings in composed requests | Tax-law correctness or full financial carry |
| Retain coherent-history control | Original lot and exact prior-state comparison reject invented loss30 | Arithmetic checks alone intentionally pass | External authenticity of supplied legal history | Bind immutable accepted predecessor rather than accepting a caller's self-hash | Generic ledger authenticates history |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Invalid usage/history and altered apply refuse; coherent source substitution fails the independent oracle |
| Statistically supported ranking | Not applicable: deterministic rational arithmetic |
| Descriptive-only differences |211 checks and case counts describe this unit only |
| Default readiness | No tax, executor or loss-policy defaults change |
| Next evidence needed | Source-backed rights, exact predecessor binding and admitted tax treatment |

Post-run red team: a consistent conditional history is still only a premise.
This unit validates arithmetic and identity under supplied assumptions, not
actual losses. That distinction is the weakest acceptance link and is retained
as an open construction obligation. No global continuation veto fired.

The loss-ledger and current program regression suites pass30 tests. Final
verification matches all1,179 protected hashes, including997 frozen release
files; the program remains structurally valid. This refresh verifies28 source
hashes and preserves every original task criterion, status and dependency.
The live count is43 original failures reviewed and158 outside this continuation.
Main reading remains336/831. No broad requirement or release is closed.
