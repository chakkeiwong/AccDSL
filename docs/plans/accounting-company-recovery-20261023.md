# Recovering authored company-family work

23 October 2026. S3/S4; MC08/11/18/24/25/28/34; G1/2/18. Policy-information,
scenario-family and typed-expression increments await manuscript integration.

## Question and skeptical audit

Can interrupted evaluation of the authored company family resume without
losing a member, changing the model, or duplicating publication? Compare with
the exact six-member CompanyScenarioFamilyDraft/1 full result. Prior corporate
portable exchanges define resume and lost-acknowledgement meaning, but their
search-partition checkpoint is not the current company-family state. Reuse
their distinction between work state and accounting state, rather than call a
search example evidence of company recovery.

Checkpoint only between complete member evaluations. A member's evaluated
result may itself be partial accounting; this is a finished work item and must
not be retried as if it were an interrupted computation. Intra-year recovery
and physical storage durability remain separate obligations. Recompute stored
members to validate exact results; record this validation work separately from
newly evaluated members so a scheduling budget does not imply a runtime bound.

Primary pass criterion: every budget split yields the same final complete
family result; checkpoints bind the exact family, source, engine descriptor,
completed ordered prefix and next member. Altered dependencies or a rehashed
false stored result are rejected. Explicit pure publication exchanges must
represent both no-commit and completed-commit lost-acknowledgement worlds;
exact retries return the stored decision, changed request identity conflicts,
and stale expected heads do not advance state. Refusals leave the world intact.

Promotion vetoes: treating partial accounting as unfinished scheduling, member
loss/duplication, changed model under resume, forged prefix accepted, Boolean
budget accepted as integer, partial publication, replay after head checking,
or changes to protected inputs. Missing comparator bytes is a continuation
veto for dependent work. A local defect triggers repair. Check counts/runtime
are explanatory. Passing supplies a reference exchange, not a persistent
runtime or proof of crash durability. No general migration is admitted; changed
schema/profile/method requires a new operation or a separately checked import.

## Assumptions and early diagnostics

| Choice | Provenance / reason | Failure mode | Smallest check | Status |
|---|---|---|---|---|
| Member boundary checkpoint | Existing family members are independent conditional evaluations | Partial accounting mistaken for interrupted computation | Stop after the two partial members and finish without reclassifying them | Bounded implementation-design choice |
| Ordered prefix | Current array order and stable member IDs | Skipped or duplicated work | Prefix reorder/missing/duplicate mutations | Required scope |
| Exact local replay | Prior trusted semantic verification | Hash integrity confused with correct results | Rehashed false prefix | Protected convention |
| Explicit work owner and immutable decision cache | Existing corporate retry semantics | Accounting effect repeated or stale retry refused | Lost acknowledgement, changed ID payload, later-head retry | Reference exchange hypothesis |
| Scheduling budget counts new members | Full replay needed to check stored prefix | Budget advertised as execution cost bound | Separate replay/new counts | Convenience scheduling policy |

Implement additively under data/accounting-master/company-recovery-20261023.
Record schema, examples, positive/adverse checks, source locks and manifest.
Use CPU-only deterministic diagnostics; smoke then one recorded full check and
read-only replay, each under five minutes. Preserve failed evidence before
repair. Audit verdict: proceed; no storage service, deployment, new financial
assumption or external approval is needed. Afterward integrate settled design
increments into a protected successor and retain S1–S5 partial/S6 held/S7 deferred.
