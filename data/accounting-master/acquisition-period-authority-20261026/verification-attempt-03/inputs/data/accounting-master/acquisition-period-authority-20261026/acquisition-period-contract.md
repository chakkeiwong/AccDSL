# Requirements for a conditional acquisition-period group method

27 October 2026. This specification follows the dated source analysis in
authority-matrix.md and the checked ConditionalControlGroupScope/1 boundary.
It is not a registered method, posting implementation or actual accounting
admission. Source, control, classification and measurement facts remain inputs
whose support must be assessed separately.

## Question and financial scope

The next method must explain how a change in control changes the group balance
sheet, income, equity and cash-flow reconciliation during a reporting period.
Today GroupPeriodReport/1 requires the same two books and control edge throughout
the period and full ownership. It cannot answer that question for a75% acquisition.
The legal books must survive unchanged; consolidation adjustments belong in a
separate dated worksheet with explicit origins and a reconciled report.

Start with a single gain of control under an explicitly selected ordinary
business-acquisition route, one reporting currency, aligned reporting dates and
no later loss of control during the selected interval. These are provisional
engineering limits, not project-wide requirements. An asset acquisition,
common-control combination, investment-entity exception, separate financial
statement or change without loss of control selects a different route. A loss
and regain is two dated events, not one continuous-control interval. Missing
facts or an unsupported route produce unresolved dependencies and no journal.

## Required inputs and their relationship

| Input | Required content | Refusal or unresolved outcome |
| --- | --- | --- |
| Reporting context | Entity, consolidated/separate scope, basis, currency, fiscal interval, selected edition/elections and source identities | Wrong entity/scope or incomplete applicable authority cannot become an admitted method |
| Control timeline | Original whole-interval assertions, actor/cutoff, exact instants, assessed control date and evidence; explicit calendar embedding for date-only books | Gaps/conflicts retain alternatives; legal conversion is not substituted for control |
| Acquisition route | Acquirer/acquiree, business assessment, common-control and investment-entity dispositions | Unknown or unsupported route prevents ordinary-acquisition lowering |
| Legal histories | Parent and acquiree snapshots immediately before/after the event and at closing; originating journals and flows for each segment | Fiscal opening is not the acquisition snapshot; a whole-year total cannot be prorated without support |
| Acquired items | Complete identified asset/liability population, acquisition-date amounts, source/basis, exception assessment and subsequent method | No unmeasured item becomes zero; an unchanged legal balance is not automatically fair value |
| Consideration | Each transferred item, who transfers/receives it, date, cash/noncash classification, measurement and separate-transaction disposition | Face value80, economic price17000/441 and supplied carrying amountC are not interchangeable |
| Previous interests/relationships | Separately typed prior equity, financial claims and pre-existing relationships; their carrying/measurement/settlement treatment | Debt is not automatically the prior equity interest remeasured under AASB3 paragraph42 |
| NCI and ownership | Current rights, qualifying measurement election, exact ownership-return periods, preference rights and potential-rights exception |75% of shares is not a universal allocation rule or a complete NCI measurement |
| Group adjustments | Acquisition allocation, policy alignment, intercompany balances/flows/profits, relevant tax and later measurement | Every adjustment names support and origin; a residual is not a balancing plug |
| Revisions | Effective/acquisition date, information availability, provisional/revised amounts, measurement-period status | Later available information must not rewrite an earlier actor view silently |

Each supplied measurement should carry an amount expression or an explicit
unknown with its unit, sign convention, reference date, measurement method and
supporting source. Only independently supported amounts can become literal
postings. A conditional expression remains conditional through reporting.

## Acquisition-date reconciliation

For an ordinary business-acquisition branch, let T denote consideration
transferred measured under the selected rule, Q the measured NCI, P the
acquisition-date fair value of a qualifying previously held equity interest,
and A and L the recognised acquired assets and assumed liabilities. All are
amounts at the same date in the same reporting currency; A and L are positive
aggregate magnitudes. P is not a debt balance. The excess in AASB3 paragraph32 is

    E = T + Q + P - (A - L).

If the applicable assessment supports positive E, it determines goodwill under
that branch. If E is negative, the reassessment required by paragraphs34–36
precedes any bargain-purchase gain. The implementation must not silently use
max(E,0) and insert the remainder into profit. When qualifying NCI is measured
as its proportional share, Q=q(A-L); a fair-value NCI election instead requires
its own measurement Q. Neither equation supplies a missing fair value or tax
effect. Symbols preserve missing measurements; they do not establish them.

For the debt-conversion example the appropriate T, Q, P, A and L remain
unresolved. The new creditor may have held debt rather than equity. AASB3
paragraphs51–53 and B50–53 require attention to pre-existing relationships and
separate transactions; the specific conversion's treatment requires its terms
and applicable financial-instrument analysis. The issuer's balanced C-to-equity
transfer does not derive the holder's acquisition consideration or goodwill.

## Period composition and reports

1. Partition the reporting interval at the exact gain-of-control instant and
   any subsequent ownership-return changes. Preserve source/cutoff views.
   Record the date-only calendar mapping explicitly. A date-only journal at
   the same boundary needs a declared event ordering or remains unresolved.
2. Carry the parent's own history throughout. Before control, report its
   investment/claim under its supported method; do not append the subsidiary's
   pre-control income and expenses to the group result.
3. At acquisition, create a separate consolidated opening worksheet. Reconcile
   legal carrying amounts to acquisition-date recognised amounts, eliminate the
   supported investment/equity balances, and record measured NCI and goodwill
   or the reviewed bargain gain. Preserve legal books and all mapping identities.
4. After acquisition, include the acquiree's complete supported income and
   expenses for the controlled interval. Apply acquisition-basis adjustments
   such as depreciation from the acquisition-date asset amount (AASB10 B88).
   Allocations use current ownership rights and the B90 exception when supported,
   not an automatic annual75% multiplier. Attribute profit and every OCI component
   to owners/NCI; do not floor a deficit NCI at zero (B94–B95).
5. Eliminate internal balances, income, expenses and flows under supported
   counterpart relations. A transfer before control is not retroactively an
   intragroup cash flow. Eliminate supported intragroup profit and its tax effects;
   the existing two full-balance pairs are not a complete elimination population.
6. Present acquisition/loss cash flows separately from other cash flows under
   AASB107 paragraphs39–42. Cash consideration is net of acquired cash for the
   applicable presentation. Keep gross consideration/acquired cash and noncash
   components for the required disclosures. Conversion itself is a noncash
   transaction under43–44, not a fabricated financing receipt/payment. A noncash
   acquisition can still change the group's cash perimeter, so cash acquired
   must not vanish merely because conversion transfers no cash.
7. Reconcile closing group assets/liabilities/equity, total profit, OCI, owners'
   and NCI movements, and cash from opening plus supported changes. Unresolved
   acquisition effects stay explicit; the report must not declare completeness.

An ownership change with continued control uses its separate equity treatment
(AASB10 paragraph23/B96; AASB107 42A–B). Loss of control requires the dated
derecognition, retained-interest and OCI branch (AASB10 B97–B99 plus applicable
amendments), not merely deleting the child from the closing group list.

## Evidence needed before an executable claim

Use an independently authored expected full journal/worksheet/report for the
same inputs. Compare every account, adjustment, origin, cash-flow class, profit,
OCI and NCI movement, not just the balance check. First demonstrate the existing
stable100% case as an exact special case. Then test one gain with partial
ownership, a pre/post-control transaction pair, fair-value versus proportional
qualifying NCI, acquisition-basis expense, cash/noncash effects, and revisions.

Adverse cases must include unknown prior control, equal endpoints with loss/regain,
wrong actor cutoff, sub-day boundary rounding, a debt claim labelled prior equity,
missing fair value/tax/exception, pre-control profit leakage, NCI deficit clipping,
unpaired elimination, a negative excess accepted without review, and reuse of
the stable-perimeter method. A failed candidate triggers the appropriate repair;
untrustworthy source bindings or an invalid comparator invalidate the affected run.

Implementation should begin with symbolic dependency/amount propagation and
independently authored algebraic invariants. That can test the method structure
without pretending to know the current fixture's measurements. Actual journal
posting remains held until the required facts, routes and full comparisons exist.
The wider simulator and independent source-time work can continue meanwhile.
