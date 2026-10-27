# Explicit settlement policy — result

23 October 2026. S3/S4; MC13–16/18/23–26/28. SettlementPolicyDraft/1 passes
99 deterministic checks. It materializes an optional policy into a distinct
operation path and preserves the saved fixed-allocation path. The example uses
the prior illustrative 90% collection rule, without estimating payment behavior.

The two 2026 deliveries each create a 192 receivable. Each of two collection
operations originally allocates 396/5 to each claim. The policy generates 432/5
for each of those four allocations. Total collections therefore increase by
144/5 (28.8); closing cash rises by 28.8 and receivables fall by 28.8. Revenue,
cost, profit and all unrelated annual lines remain equal. Each claim retains
96/5 (19.2). The full next-year path also replays with its fixed settlement
instructions preserved.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the optional policy draft | Exact four-allocation diff, claim conservation, all 29 annual report deltas and subsequent-year replay pass | Unknown inputs remain unresolved; duplicate identities, malformed amounts, wrong claims and policy/result mismatches are refused; extra collections against targeted claims are unsupported | A synthetic fraction has no behavioral evidence; policy timing remains unadmitted | Add text authoring and integrate the checked design increments | Optimal payment behavior, empirical prediction, accounting compliance or a product default |

The pre-recording test harness had incorrect expectations: it counted a 28.8
total change as 14.4, attempted to read an operation ID from an allocation,
and expected a whole-path invalid result where the interpreter correctly retained
the first year and returned a partial path. Those were diagnostic errors, not
accounting repairs. The final comparisons use exact rational arithmetic and
saved result bytes. A later lexical audit found that the generator accepted
unreduced rational strings despite the interpreter's canonical convention. The
prior 97-check code/evidence is retained under before-canonical-rational-repair;
the current checks reject noncanonical fractions and invoice values.

The policy schema is closed and non-executable. A generated path still requires
the trusted interpreter to establish accounting feasibility. A correct policy
trace can generate a liquidity failure in another scenario; materialization does
not promise successful execution. The generator changes no unspecified date,
claim, opening, accounting method or future-year instruction. Timing for the
policy itself remains unresolved.

Post-run red team: this single fraction rule is narrow and its conservation
depends on targeting newly issued claims with no other same-year collections.
More general schedules need explicit priority, outstanding-balance and timing
semantics. Hash consistency cannot establish that a path follows the policy;
the materialization verifier recomputes it. An independent interpreter or real
company collection evidence could alter the scope judgment, but neither is
claimed here. No research-direction or global continuation veto fired.

Run command, environment, input/code hashes and duration are in manifest.json.
Read-only replay: CUDA_VISIBLE_DEVICES=-1 python3
data/accounting-master/company-policy-20261023/verify.py.
