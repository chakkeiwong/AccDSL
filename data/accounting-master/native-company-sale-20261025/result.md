# Complete native sale adaptation — checked

NativeCompanySale/1 validates the full retained native state and event domain,
imports every existing lot into a declared company book, computes sale effects
through CompanyMethodCall/1 and restores the entire native state. The native
transition is used only as the comparator. A monkeypatch test makes it raise while
the adapter still proposes and applies, demonstrating that it does not supply the
candidate effects. Native structural validation and invariants remain active.

Nine focused methods pass;140 exact checks across23 cases preserve complete native
states,journals,gross flows and refusal reasons/statuses. The two-lot example splits
inventory20 into carrying15 and5. Selling the first for40 moves cash454 to494,
inventory20 to5 and cost of sales56 to71; the second lot remains exact. Selling
the second later for8 leaves cash502 and inventory0. Every native field outside
balances,date,seen,flows and lots is preserved exactly.

Unknown performance/proceeds remain unresolved,false performance and a fractional
sale remain unsupported,and the native negative-cash state retains funding_failure.
Tax-close/date,lot identity,refund control,inventory allocation,tax-base,disposed
stock,duplicate and malformed-source cases refuse. Rehashed result tampering and
Boolean/numeric substitution fail complete canonical replay.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Integrate selected full native adapter | Complete native and independent arithmetic comparisons pass | All tested state/event/control refusals preserved; source/schema malformed states rejected | Native fixed owner/chart and finite existing-lot population | Integrate,refresh coverage,compose corporate methods and statements | Generic company admission,source validity,full corporate simulator |

The strongest alternative explanation is a shared defect in native validation or
an untested native field interaction. Independent arithmetic and complete complement
checks constrain that risk; they do not establish accounting treatment. A changed
unsold lot,source complement or native refusal would overturn adapter acceptance.
No candidate repair was required. A planned test count was corrected from22 to the
actual23 authored cases before running the suite. Bounds remain engineering limits;
no scalability or runtime ranking is claimed. S1–S5 partial,S6 held,S7 deferred.
