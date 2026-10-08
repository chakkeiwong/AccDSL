# Apple tax recognition and settlement result

Completed 9 October 2026 under the [bounded plan](../../../docs/plans/accounting-apple-tax-20261009.md).
E01/C03/C08 advances MC01–05/07–12/15–16/19/28/30/32–35 and
G1/G4/G5/G7/G11/G13/G15/G16. The separate [Version 2.10 PDF](../../../docs/design/proposal/manuscript-tax-20261009/accounting-product-proposal.pdf)
has 141 pages and SHA256
`9d723b422b3d15b5545471730fe94eddba50f062e6099c32026e4f9fa61c6f20`.
Full proposal readiness remains **not_ready**.

The complete annual Note 7 reading and eighteen dependencies distinguish tax
recognition, balance movements, restricted assets and the following quarter's
reported payment. Twelve note units retain 109 monetary and three percentage
cells, including every comparative column in the four tax tables. Nine query
examples preserve the supported answers and missing facts. This is not complete
semantics of all surrounding notes/statements or the full Apple package.

## Checked consequences

Amounts below are USD millions unless stated otherwise. The [source note](source-note.md),
[source supplement](source-claim-supplement.json) and [calculations](tax-bridges.json)
preserve exact anchors, scopes, dates, signs and assumptions.

| Target or proposed shortcut | Quantity computed and verdict | Remaining explanation |
| --- | --- | --- |
| Tax expense equals cash paid | Current 32,780 plus deferred −3,031 equals expense 29,749; cash paid net is 26,102. Equality is wrong at displayed amounts | Recognition and settlement allocation |
| Current expense less cash explains total tax-payable change | Current plus noncurrent payables rise from 24,276 to 35,855, or 11,579. Expense less cash is 6,678, leaving 4,901 | Unallocated scope, vintage, currency and other movements; no causal journal identified |
| Net deferred-asset change equals the deferred benefit | Net DTA rises 1,951, versus benefit 3,031, leaving −1,080 | Allocation among profit, equity/OCI, currency and other causes remains unresolved |
| Rounded State Aid components conflict with the detailed charge | Displayed components yield 10,177, while the fine table gives 10,246. The latter lies within conditional nearest-rounding envelope [10,076.5,10,277.5] | Unrounded components and issuer rounding/tie rules; no genuine E05 conflict established |
| Quarter payment alone explains the dollar obligation movement | Opening 15,800, payment 11,900 and closing 3,400 require −500 in other net movements. Conditional outer interval [−650,−350] excludes zero | No exact FX/valuation/accrual entry identified; source currency commentary is qualitative |
| The same bridge in euros requires a nonzero other movement | EUR opening 14,200, payment 11,000 and closing 3,300 give +100, with conditional interval [−50,250] including zero | Zero-compatibility is not proof of no other movement or a common conversion rate |
| All restricted settlement funds are cash | Annual cash 2,600 plus securities 13,200; quarter-end cash 126 plus securities 3,300. The latter 3,426 sum is compatible with the rounded 3,400 obligation | Securities conversion, transfers, valuations and exact settlement entries |

The State Aid opening obligation is explicitly reported in annual MD&A; it is
not inferred from escrow. The following quarter explicitly reports the Ireland
payment and remaining obligation in both currencies. The current analysis thus
adds actual reported movement evidence while preserving the missing accounting
and funding details. A conditional payment of 11,900 at liability carrying value
debits payable and credits restricted cash equally, leaving no second expense
in that posting. This assumes the required cash conversion has already occurred
and excludes related gains/losses/fees. It is not Apple's reconstructed journal.

Gross DTA 34,873 less allowance 8,866 and DTL 6,805 gives net 19,202. Note 6's
asset presentation 19,499 has a different target; the difference 297 alone does
not establish a separate liability line or permission to offset jurisdictions.
The note retains specific temporary differences, indefinite carryforwards and
the valuation allowance. Indefinite duration does not prove recoverability.

Gross unrecognised benefits reconcile from 19,454 to 22,038 using all five signed
movement categories. The population excludes interest and penalties; the 1,070
settlement-related reduction is not automatically total cash paid. The 10.8bn
rate-impact subset and possible 5–13bn next-year decrease preserve their distinct
targets. No probability, cash timetable or future expense release is inferred.
The court history remains attributed to Apple, with no independent legal or
operative ASC determination from this unit.

## Validation and decision

All **148 source/arithmetic checks** and **33 candidate/preservation checks**
pass on their first runs. The source check compares the entire annual tax-note
text with its original PDF pages, verifies selected rows and identities, and
retains interim DOM/context evidence. All nine original annual source pages
and three derived interim pages were inspected. The print view is derived,
with text preservation checked; it is not an original browser screenshot.

All 40 earlier mathematical displays and all 66 bibliography entries survive,
with one new diagnostic equation. Two existing source files change and one
section is added. The earlier Apple narrative and source-admission text remain
intact. Twelve rendered candidate pages were inspected for layout/navigation;
pages 71–75 were read continuously at full size, as recorded in the
[author review](author-review.md). Independent and human acceptance remain pending.

The first sandbox build failed before PDF output because LuaLaTeX had no
writable font cache. Its logs are retained under `sandbox-build-attempt/`.
One trusted retry succeeded with clean final LuaLaTeX/BibTeX logs; no manuscript
repair or layout rebuild was needed. Build success and check counts are scoped
engineering evidence, not accounting or human acceptance criteria.

The first closeout stopped because two live records still named Version 2.9
after a documentation edit failed to match its target. Those dependent edits
were completed before the final closeout; the failed script and diagnostic are
retained under `first-closeout-attempt/`. Source and candidate checks and the
PDF were unaffected.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Integrate the bounded tax reading | Declared note and dependencies mapped; source and arithmetic consequences checked | No source/date/sign/scale defect found | Author-only semantics and missing transaction facts | Retain V2.10 and extend the material-source queue | Whole-package coverage or tax-law correctness |
| Reject zero-residual aggregate shortcuts | Reported balances cannot be connected by those shortcuts | Nonzero 4,901 and −1,080 differences; USD settlement-only book fails conditional rounding | Different accounting populations and omitted movements | Preserve explicit unknown movements; seek actual allocation evidence | Filing error or uniquely identified FX/expense journal |
| Retain conditional settlement example | Journal balances and assets/liabilities fall equally under stated assumptions | No arithmetic or balance-equation failure | Actual cash conversion, liability carrying value and currency entries | Use as a scoped explanation of recognition versus settlement | Complete actual issuer history |
| Keep readiness negative | Five wider E obligations remain | Whole-mission acceptance evidence incomplete | Package, authority, literature, interfaces and human evidence | Continue master program | Product implementation, publication or paid review readiness |

The failed equalities reject shortcuts, not the sources, the research direction
or valid bookkeeping identities. They triggered the planned residual analysis
and conditional settlement explanation. The sandbox failure was an environment
restriction and was repaired; no continuation veto remains. Engineering
integrity, arithmetic validity and accounting interpretation retain separate
limits. No stochastic comparison or method ranking is involved.

Post-run red team: the strongest alternative explanation is a scope mismatch
between current expense, reported payable and net cash taxes, together with
unreported transaction allocations. That would explain why a residual exists
without making it an independent journal. Unrounded values, dated currency and
transaction records could refine or overturn a particular bridge. The weakest
evidence is missing issuer-level reconciliation and pending independent semantic
review; the precise rounding rule is also unverified. Neither rounded
compatibility nor balanced example entries establish legal/accounting validity.

## Continuation and preservation

Next: E01/C03 earnings per share and share-count changes, starting with annual
A06/A16 and interim I04/I08 (Notes 3/10 and 3/7 respectively). Inspect linked
equity statements, repurchase/cash rows and compensation/dilution dependencies
(annual Note 11, interim Note 8) before drawing movement conclusions. Preserve
the distinction between period-weighted shares, closing shares, share units,
authorised repurchases, actual purchases and settlement. Define and audit the
exact population before execution; do not divide an annual count into quarters
or infer cash from a share-count change.

The four live master records identify V2.10 and that task. All MC01–MC35/G1–G18,
five E01/E05/E07/E08/E14 workstreams, forty exhibit targets and 136 unverified
publication dates remain. The completed E05 search and failed acquisition
routes are not repeated. Product implementation and the old controller stay held.

Preservation checks retain 118 baseline files, 115 prior-unit manifest
references, 1,266 historical protected files, 518 upstream references and six
controller records. Pre-V2.10 pointer bytes are in `pointers-before/`; older P19
paths resolve through the continuation baseline. The run manifest binds the
current plan, sources, commands, environment, timing, outputs and review. No
network request, install, Git mutation, fee, outreach or publication occurred.
