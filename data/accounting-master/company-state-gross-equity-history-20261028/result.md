# SIM-F006: gross equity histories survive equal closing totals

28 October 2026. C04; MC08/09/11/12/13/26/28/33. Attempt01 passes197 checks
across15 native executions and11 exact finite-note cases. This supplies scoped
evidence for the original failure without changing its inherited status.

The original histories are issue20 shares at3, and issue30 at4 followed by
repurchase and retirement10 at6. Both add cash60 and shares20. Starting from
cash10 and100 old shares, both close with cash70 and120 shares. Their gross
financing flows are60 versus120 and minus60. The implied net price3 is an
actual issue price in the first history; neither transaction in the second
occurs at3. Closing balances therefore cannot identify the transaction prices.

Both paths execute through the unchanged DeclaredCompanyProgram/2, for two
account-name owners. Every balance and memory field, journal account, dated
event identity, signed flow, income total, equity bridge, cash-flow activity
and reconciliation is checked against independent exact arithmetic. Native
verification replays each entire result. Undeclared native posting is disabled
throughout the checks. Full inputs and results remain in attempt-01/runs.json;
the independent expected states are in oracles.json.

## What is implemented

The retained factory already supplies a typed issuance method carrying newly
issued shares. This work adds separate immutable method data for retiring
those newly issued homogeneous ordinary shares. It is not an existing general
repurchase-library operation. It updates cash, the synthetic capital account,
share memory and gross financing flows. Old shares remain unchanged.

The method refuses purchases exceeding the available new shares, insufficient
cash, zero price, negative share input, duplicate or backdated events and a
retirement before issuance. Unknown price remains unresolved. Missing inputs
and wrong dimensions invalidate the request. Economic refusals preserve the
entire successful prefix and produce no final report.

The finite note comparison retains both candidates when notes are absent,
unknown or not yet available. At the declared availability cutoff, gross
proceeds60/repurchase0 selects the first, and120/60 the second. A contradictory
100/40 note selects neither, despite also netting to60. Changing future note
amounts leaves the earlier family unchanged. No probabilities or exhaustive
history coverage are asserted; note meaning and timing are supplied inputs.

## A deliberate wrong method exposes the verification boundary

Deleting the retirement's share-memory write and recomputing its method hash
still yields a complete provisional native result, with balanced statements.
The resulting new-share count30 is wrong relative to the target20. The
independent share oracle detects the error. A hash checks identity and a
balanced journal checks monetary conservation; neither proves that authored
economic methods update every required nonmonetary quantity. This negative
fixture stays with the evidence. It does not show a bug in generic typed
execution or establish general economic-method admission.

Legal authority, owner-specific rights, treasury versus retired classification,
par/share-premium/retained-earnings allocation, fees, tax and actual source
admission remain outside this synthetic method. The single capital-account
treatment is an explicit fixture choice, not a standards conclusion. T07 and
the complete company/share-register requirements remain open.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain SIM-F006 evidence | Both original paths and all state/report comparisons agree | No failed checks | Supplied finite histories and note semantics | Preserve the two histories and gross-note tests | General reconstruction completeness |
| Reject net-price-only reconstruction | HistoryB has prices4 and6 with net ratio3 | Exact original counterexample | Additional undisclosed histories | Constrain with separately supported gross notes | Actual issuer transaction prices |
| Retain missing-share negative fixture | Oracle finds30 instead of20 despite balanced books | Economic target fails for deliberately altered method | General admission of authored methods | Require operation-specific nonmonetary checks | Hash or journal balance proves semantics |
| Continue program | No continuation veto | Frozen code unchanged | Persistent loan type and shock timing | Audit SIM-F011/018 next | Completed financing package or release |

| Inference status | Assessment |
| --- | --- |
| Hard veto screen | Dimensional/structural errors and infeasible economic events refuse; independent share oracle rejects omitted update |
| Statistically supported ranking | None; exact deterministic calculations |
| Descriptive-only differences | Counts and execution time |
| Default readiness | No economic/accounting default promoted |
| Next evidence needed | Broader rights, source and treatment admission; persistent contract and reset checks |

The strongest alternative explanation is that the method succeeds because the
correct transactions are explicitly supplied. That is its bounded execution
question. It does not recover them from a filing. A different legal or accounting
treatment would require a new scoped definition, not reinterpretation of these
results. The weakest evidence remains general event-family and source admission.
The run manifest preserves30 source hashes, exact command/environment, commit
and wall time. Original criteria,201 failure rows and releases remain unchanged.

Verification after navigation refresh:47 existing program/financing/company
unit tests pass. The fresh final-verification.json confirms all1,179 checked
hashes, including452 selected and545 provisional release files, unchanged.
The40-task dependency graph validates. The supplemental disposition now covers
23 original rows;178 remain outside this continuation. C04's stale eight-row
remaining field is repaired without changing criteria, dependencies or status.
