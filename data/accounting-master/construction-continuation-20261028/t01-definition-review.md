# T01 definition review against the original criterion

28 October 2026. Review plan:
docs/plans/company-state-definition-review-20261028.md.

The original criterion is: economic/contract state, accounting memory,
parameters, actor information, histories and changing populations distinguished;
refusal and historical query dependencies traced. The current definitions
satisfy this criterion for the declared operations and existing native
responsibilities. Mark T01 complete as a definition task. This decision does
not assert a general source-to-company constructor, every industry implementation,
admitted real-company data or release acceptance.

| Original component | Concrete definition and checked responsibility | Decision |
| --- | --- | --- |
| Economic/contract state | native-construction-contract-v1.md separates resources, claims, terms and accounting values; common-state-owners.md maps27 native profiles, including finite bank commitments and selected receivable terms; the extended REA reading distinguishes commitments from completed events | Defined with explicit limits; no universal lifecycle claimed |
| Accounting memory | Native account balances, claim recognition/settlement counters, asset cost/life/depreciation, typed book memory and carry responsibilities remain distinct; all14 company-operation kinds have a read/effect/guard inventory | Defined and traced; unsupported basis conversions remain explicit |
| Parameters | Supplied prices, lives, rates, methods and tax conventions are separately owned assumptions; policy generation, equality validation and target comparison have different effects | Defined; provenance/admissibility remains a separate application obligation |
| Actor information | actor-information-requirements.md binds observation/action requirements to exact operation, View, evidence closure, cutoffs, replay and authority responsibilities; the common caller refuses unimplemented actor operations | Defined; actual identity/receipt is T03/C01 and endogenous policies are T07 |
| Histories and queries | Typed annual, year-qualified event-prefix, claim and asset queries retain origins and complete executed histories; recorded-period book reporting is distinct; bank exact replay retains the old query result before new-view/head freshness | Traced for supported operators; no arbitrary interval or cross-owner query implied |
| Changing populations | New claim/cohort IDs, opening versus created origin, settled/fully depreciated retention, per-owner context and unsupported transfer/split/merge/lifecycle requests are explicit | Defined; common transport does not merge economic populations |
| Refusal dependencies | Native guards and full results remain authoritative; null population means not inspected; partial prefixes survive; common caller separates envelope failures from native refusal and exceptions | Traced; checks cover selected native behavior, not exhaustive conformance |

The actor review inspected the original bank information closure and request/
response code and the exact-time successor contract/code/result. The native
query View is not an authenticated actor. Query publication receipts are not
human receipt evidence. Policy description supplies no selected action or
posting permission. Those distinctions repair the remaining definition gap
without introducing a fictional common decision engine.

The common request passes304 deterministic checks over39 cases, preserving
entire direct results for three supported capabilities plus independent policy
and interim-report amounts. These checks support the implementation described
by the definition. They are not the criterion for T01 completion. The owner
review's166 checks preserve27 profile meanings and16 compatibility edges;
neither count establishes general composability.

| Decision | Primary criterion | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete T01 definition task | Every original component has explicit meaning, native owner and trace/refusal | No unassigned definition prerequisite found in the declared scope | Independent implementer/reader acceptance and broader operations | Use these definitions in downstream tasks once their survey prerequisites pass | Whole DSL design complete or T05 implementation delivered |
| Preserve original program | Original criterion/edges/requirements stay verbatim; only T01 status and next actions change | U00 and B03 prerequisites already complete | Survey S02/S04/S06/S07 still open | Continue independent survey, source admission and failure review | Permission to bypass remaining dependencies |
| Preserve release holds | Selected/provisional releases and original acceptance populations unchanged | No release promotion requested or inferred | Source-grounded whole-company construction and independent acceptance | Keep S1–S5 partial, S6 held, E3 deferred | Forecasting or production readiness |

Post-review red team: the strongest contrary interpretation is that T01 meant
an implemented universal constructor. Its recorded deliverable is a state
specification linked to operations and types, and its criterion asks for
distinctions and traces. That stronger implementation belongs to later tasks
and cannot be introduced as an unstated prerequisite. Conversely, a newly
found undefined required state category or unsupported asserted mapping would
reopen T01. This is internal design review, not independent acceptance.
