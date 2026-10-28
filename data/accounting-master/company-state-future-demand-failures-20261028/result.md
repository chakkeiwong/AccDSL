# Future demand, nonanticipativity and complete-table admission

28 October2026. C04;MC03/04/11/25/26/28/33. Original targets SIM-F012
and LIT-F004 retain their original statuses and multi-actor residuals.
The unchanged cross-mechanism finite solver and independent forbidden-action
oracle agree with hand-constructed full sets across18 cases and79 checks.

The new discriminator has cash1 and an indivisible order0/order1 chosen
before demand0/demand1 is observed. Exact matching, no disposal and no
backorder are explicit synthetic constraints, not general company behavior.
No hidden-information policy can match both demands; learning the demand
only at the second date does not repair the earlier order. Early observation
permits one policy. Allowing overstock instead gives a viable common order1
policy, and a demand-independent target permits both orders. Full-set
comparisons, altered internal labels and ordering controls guard against
merely hardcoding an empty result. No demand probability is assumed.

A post-run red-team probe exposed a separate input-boundary gap: removing
only the demand0/order1 refusal leaves observable-cell action coverage intact,
and the bare native solver returns order1 as feasible. Its full-table result
remains correct. The inherited native contract relies on complete protected
support; its local observable-cell guard does not prove world/action coverage.
Both native and oracle can share this omitted-row assumption, so agreement
alone cannot establish completeness. The false-feasible request and result
are retained in admission-attempt-01/missing-refusal-witness.json.

The repair adds BoundFinitePolicyRequest/1 in bound_request.py. Its trusted
caller supplies an external expected identity covering the complete rows,
action domains and revelation regime. The adapter checks that identity and
the pinned native implementation before invoking the existing solver, then
returns the complete native policy set. An embedded self-signed identity
cannot authorize a changed request. A newly admitted identity is explicitly
a new question. Row order is identity-bearing; semantic reorder reuse is not
implemented. Source truth and completeness must be established by the caller;
a hash alone cannot discover an unknown omitted world.

Admission-attempt-01 passes69 checks: all18 complete cases are preserved and
all12 dropped/changed/duplicated request variants are refused before native
execution. The full raw native witness remains available; no protected native
code or earlier evidence was rewritten. Other unbound callers are not repaired
by the existence of this adapter and must retain the complete-input precondition.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain scoped nonanticipativity evidence | Native, oracle and independent hand full sets agree | Hidden/late exact-match infeasibility preserved; viable controls pass | Real actor information and broader horizons | Continue actor/source admission and original failures | General production enforcement |
| Reject unbound altered tables | Removing one refusal must not create a valid admitted question | Bare native call produces false feasibility on incomplete support | Whether upstream caller establishes complete world/action support | Require bound admission before these scoped requests | Native algorithm fails on complete admitted data |
| Retain bound request adapter | Preserve full sets and reject all12 mutations |69 checks pass; source/request identity enforced | Trusted expected identity must come from independently admitted source | Connect to supported source owners with explicit scope | Hashes prove real-world truth or exhaustiveness |

Research intent and default audit are in the two plans. Exact two-world,
two-date deterministic policies and complete rows are synthetic hypotheses
chosen to isolate anticipation and support loss. Counts/runtime are explanatory;
there is no stochastic ranking, empirical forecast or behavioral default.
Manifest records pin native code, oracle, plans, input tables and original
failure-map identity. Commands:

    python3 -B data/accounting-master/company-state-future-demand-failures-20261028/check.py
    python3 -B data/accounting-master/company-state-future-demand-failures-20261028/check_admission.py

Both commands create exclusive attempt directories and must not be rerun there.

Post-run red team: a dishonest or incomplete expected identity can still
admit the wrong problem. The adapter prevents altered transport from silently
changing an already admitted finite request; it does not establish the
admission's original authority. This is an implementation-boundary repair,
not rejection of nonanticipative policies or the simulator program. No global
continuation veto fired. Remaining real source/actor, general policy and
complete201-row failure obligations continue.

