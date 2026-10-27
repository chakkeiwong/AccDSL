# Declared company period reports — checked reference

CompanyBookReport/1 produces account-mapped balance sheet,income,direct cash-flow
and equity reports from compatible declared company books. Every account belongs
to exactly one line matching its declared classification. Cash activities retain
separate receipts,payments,net amounts and original flow records. Direct equity
movements must be explicitly explained per equity account;no balancing plug is used.

Fifteen focused methods pass. Forty-two comparisons across five cases cover two
company charts,payment and sale/contribution arithmetic,and compatible full-year
native statement fields. In the sale/contribution case,assets160 equal liabilities30
plus equity130;income40 less expenses15 gives profit25;opening equity100 plus direct
contribution5 plus profit25 gives closing130. Cash rises100 to145,with operating40
and financing5. In the retained annual case,profit99/2,cash983/2 and equity1343/2
match the native report,as do every asset/liability/income/expense line and all
direct cash activities. Native indirect cash flow is not part of this new profile.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Integrate recorded-period reporting | Complete mappings,exact independent/native fields and cash/equity identities pass | Missing/overlapping accounts,unexplained movements,stale contexts and prior-event cash references rejected | Snapshots and supplied movement explanations do not prove complete economic history | Integrate,refresh coverage,audit close/carry | Complete fiscal events,notes,indirect cash flow or accounting compliance |

Pre-test inspection removed an unnecessary opening/closing memory-schema equality:
annual events may add a lot while the account map remains compatible. Both books
are validated independently;reporting makes no memory-migration claim. A targeted
test then showed that a current cash flow could cite an opening-history event.
The reporter now requires every flow's event in the post-opening history suffix.
Earlier code and the failing test log remain in attempt-01. The repaired15-test
suite passes. Strongest alternative explanation: omitted offsetting events can
leave every financial identity balanced. Accordingly fiscal_complete and
notes_complete remain false;notes can only be missing,unsupported or unresolved.
Equity explanations reconcile amounts but do not prove event-level causation.

No numerical ranking or standards conclusion follows. S1–S5 remain partial,S6
held,S7 deferred. Run/source details are recorded in manifest.json and source-lock.json.
