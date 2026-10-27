# Native condition coverage before implementation

24 October 2026. Comparator sources: typed_return_transition_v1.py:118–190 and
company-return-execution-20261024/native_returns.py:42–69,91–174; exact memory
operations: typed-memory-effects-20261024/examples.py:25–58.

Restricted request: one complete fixed native state, one fixed event skeleton,
explicit domains only for unknown actual_units, unit_handling, unit_deterioration,
inventory_nrv (settlement) or proceeds (sale). Refund/handling cash facts, dates,
identities, methods, fraction and Boolean findings stay fixed known/unknown.
Unknown state-derived inputs remain unresolved. Domains never overwrite known
event facts. This restriction is an authored fragment, not a universal default.

| Native condition | Enforcement in the new family | Why sufficient in this fragment |
| --- | --- | --- |
| Closed state and event schemas; exact rational/date formats | Original structural validators before compilation | Full definitions retained; selected numeric unknown slots are separately typed domains |
| Selected USD/legal context and settlement/sale method | Original schema/context checks, no context conversion | Event date remains in original method type context |
| Opening balance, cash, allocation, lot/tax/disposition invariants | Original native invariant on complete fixed opening | No symbolic opening is introduced |
| Lifetime event uniqueness | Fixed event ID absent from opening seen | Candidate arithmetic cannot change ID |
| New settlement lot / existing undisposed sale lot | Fixed collection checks before solving | No symbolic collection identity or topology |
| Period, state and tax-close chronology | Original selected prerequisite expressions, fixed exact date values | No time is chosen by solver |
| Component identity and unsettled state | Original selected predicates | Fixed component and state |
| Rights/handling/performance findings; whole-lot fraction | Original exact predicates and consequences | Unknown remains unresolved; false preserves unsupported |
| 0 < returned <= sold; handling >=0; 0 <= deterioration <= cost; NRV >=0 | Original numeric selected constraints in every monetary branch | Shared numeric inputs, strict bound preserved |
| Exact refund/handling cash | Original selected constraints against fixed external facts | Domains cannot invent unknown cash evidence |
| Nonnegative sale proceeds | Original selected inequality | Shared proceeds variable |
| Journal balance and cash-flow sum | Original piecewise identity checks; both original replays | No balancing amount or financing inserted |
| Closing cash >=0 | Add opening_cash + journal_cash >=0 to every branch | This omitted condition distinguishes funded and unfunded candidates |
| Closing inventory allocation | Preserve original memory update and replay | Settlement adds V to inventory and new lot; sale removes the lot's fixed carrying cost from both |
| Closing refund/recovery allocation and rights closure | Original memory operations and replay | Settlement releases exactly the fixed opening component balances and zeros both; sale preserves them |
| New lot units/carrrying/tax base and disposition | n>0, n(c-d)>=0, NRV>=0 imply V>=0; original updates and replay | Tax base equals V, new lot live; sale zeros all three fields and marks disposed |
| Other inventory and prior lots | Unchanged fixed opening fields except selected sale lot | Opening invariant already checked |
| Unique tax adjustment and seen IDs | Fixed event uniqueness plus original append operations | Every old adjustment ID is already in seen; new ID cannot duplicate one |
| Complete next state, journal and flows | Replay TypedReturnTransition and native transition on each exact candidate | Any mismatch vetoes implementation; cannot count a failed witness as empty family |

Every family branch includes the same fixed structural checks and funding
constraint. Exact formulas/provenance remain in manifests. Independent candidate
replay is a second check; it does not replace the preceding completeness argument
for the selected fragment. Fractional quantities remain allowed by the original
reference; integer lots, unknown source-state reconstruction and general method
chains remain open. No continuation veto fired.
