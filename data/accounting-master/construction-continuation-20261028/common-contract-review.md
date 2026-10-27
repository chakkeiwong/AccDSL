# Common construction contract review

28 October 2026. T01 remains in_progress. Reviewed draft:
docs/design/research/company-state-program-20261028/native-construction-contract-v1.md.

The original criterion is: economic/contract state, accounting memory,
parameters, actor information, histories and changing populations distinguished;
refusal and historical query dependencies traced. The bounded contract now
explains each distinction for the existing company-operation path and points
to its native owners. The task is not closed because the common cross-profile
construction request and actor/operation interfaces are still a proposed design
rather than one fully specified typed contract. This is a definition gap;
sector implementation is not silently made a prerequisite.

| Original component | Checked current coverage | Remaining definition work |
| --- | --- | --- |
| Economic/contract state versus accounting memory | Claim amounts/counters, cohort cost/life/accumulation, full native outputs and missing legal identities | Explicit common typed slots and ownership constraints across existing profile families |
| Parameters and actor information | Persistent supplied parameters separated from archival inputs; no actor receipt inferred | Common observation/action request carrying actor, cutoff and permitted operation meanings, linked to existing information profiles |
| Histories and historical queries | Annual report view, event prefixes and lifetime carry documented | Exact typed selection for requested historical queries across supported native profiles; unsupported queries must identify the missing operator |
| Changing populations | Additions, new claims, zero/closed balances retained in native histories | Common identity/lifecycle rules for supported additions/closures and explicit unsupported transfer/split/merge requests |
| Refusal and operation dependencies | All14 native kinds source-inspected; exact selected claim/cohort and financial guard controls | Check common projection preserves native refusal order and does not claim exhaustive static extraction |

Review verdict: retain as a concrete implementer draft and use it to define the
next typed request. Do not mark T01 complete from the14-kind count or clean
runtime checks. T05 owns sector/basis implementation and T03/C01 actual issuer
identity/access; their original requirements remain unchanged. The next T01
unit should bind a typed common request to exact native owners, refuse unsupported
cross-profile joins and preserve all unknowns, rather than adding another
isolated financial counterexample.

Source and numerical limits remain explicit. The contract uses the native
annual straight-line, homogeneous-cost, zero-fee and immediate-tax conventions.
It does not establish standards applicability. Self-review is not independent
implementability or reader acceptance. No broad requirement or release closes.
