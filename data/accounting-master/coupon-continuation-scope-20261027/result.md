# Equal financial balances do not authorize an unrestricted merge

27 October 2026. Attempt-01: 24 exact continuation cases, 514 assertions,
ten controls, 218 protected files; 7.894 seconds, Python 3.11.15, CPU with GPU
intentionally hidden. All pass. Original source, partial method and runtime
remain unchanged. See attempt-01/run-manifest.json for command and commit.

One payment of 1 on January 2 and two payments of 1/2 on January 2 and 3 leave
identical financial balances and contract memory: cash 69/16, unpaid claim 35/8,
cumulative paid2=1. Dates, seen IDs and dated gross cash flows differ. A fresh
January 2 instruction can follow only the first prefix. A January 4 instruction
whose ID appeared only in the split prefix is refused only there. Equal balances
therefore do not preserve the complete feasible-instruction set.

A common fresh January 4 payment of 1 succeeds from both prefixes. Both leave
cash 53/16, unpaid claim 27/8 and paid2=2. Numeric statements and gross activity
totals agree; complete reports still differ in dated gross origins and identity.
The sufficient restricted projection is same original obligations and memory,
same cumulative payment, common future dates no earlier than both current dates,
IDs fresh for both histories, identical supplied amounts and no other events,
provided bounded execution accepts. The recurrence then preserves numeric state
by induction. This does not preserve full history or constitute a quotient for
all future methods, observations and policies.

Pre-run inspection found a real interface limitation: DeclaredCompanyProgram/2
requires its opening at period start with empty flows. Passing a retained
midperiod book returns opening_report:opening_at_period_start. The selected
continuation therefore proposes one event directly through the unchanged typed
method engine, preserving the actual prefix book, and reports cumulatively from
the original period opening. It is explicitly a SelectedCouponContinuationStep/1,
not a general program-resumption feature. The generic refusal is retained as a
diagnostic and does not imply economic infeasibility.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reject balance-only full-history merging; retain restricted financial projection | Complete oracle comparisons and date/replay witnesses pass on four origins | Ten controls reject changed prefixes, identities, lost history, wrong report opening and false admission | General bounded program resume and cross-method compression remain open | Integrate result and define selected multi-event resume with explicit original opening and current prefix | No production checkpoint persistence, arbitrary-method quotient or actual accounting admission |

Red team: equal statements could be mistaken for equal history. Direct refusal
witnesses and full cumulative reports expose that mistake. Re-identifying an
altered prefix cannot bypass the independent prefix comparison. External source
authenticity and durable storage remain unverified. No global continuation veto.
