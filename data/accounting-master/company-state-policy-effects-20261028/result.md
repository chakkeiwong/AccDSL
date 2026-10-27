# Native policy effects remain separate

28 October 2026. T01/C04; MC08/10/13/18/19/26/28/32/35.
Plan: docs/plans/company-state-policy-effects-20261028.md.

Attempt-01 passes 144 deterministic checks over 19 cases. The closed
CompanyPolicyEffectRequest/1 dispatches three explicit effects for the exact
CompanyOperationPathDraft/1 owner. It reuses SettlementPolicyDraft/1 and the
guarded population inspector; neither existing module is modified.

For the retained price-revision parent, each selected invoice is 192. The
9/10 rule with half shares prescribes 432/5 per installment, whereas the
supplied path contains 396/5. Thus actual-minus-target is -36/5 for each of
the four selected claim allocations. compare_targets preserves the full
native result and reports those differences without an equality verdict.
validate_equalities also preserves the full result and records four known
violations. generate_inputs uses the existing materialization, records its
verification and executes the child; the earlier complete year is unchanged.
An equality request on the matching child satisfies all four constraints.

The full-collection case remains generated_inputs while its native execution
is partial: the unchanged third-year collection over-settles a claim. These
are separate statuses, and native_execution_complete is false. A second
control makes a required collection unexecutable: the two earlier known
differences remain available, two actuals remain null, and overall comparison
evidence is unresolved. It does not return a completed comparison or silently
replace the unavailable allocations by zero. Unknown opening claims similarly
produce no inspection population. Executed zero allocations, by contrast,
remain known zeros.

Wrong owner, effect, actor view, identities and context, malformed requests,
stale policy parent and unknown policy fractions retain distinct refusal or
unresolved results. All requests leave source/actor/legal/behavioral/forecast
admission false. The role vocabulary is a local implementation of the
distinctions examined in the REA reading, not code imported from that paper.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain bounded dispatcher | Three roles produce independently expected distinct effects and unchanged baseline histories | 144 checks pass, including partial/unknown controls | Broader rule types, periods and owners | Connect to common state/operation definitions | Generic rule engine or complete constructor |
| Preserve incomplete comparisons | Unexecuted allocations remain unknown; known violations retained | Partial and unresolved opening cases pass | Actual source and authority | Continue T03/C01 independently | Real company compliance or actor knowledge |
| Continue T01 | Native effect ownership stays explicit | No original criterion relaxed | Common owner mappings, commitments and actor operations | Inspect existing owner semantics and commitment theory | T01 or release completion |

No stochastic experiment or ranking is performed. All counts are engineering
diagnostics. Strongest alternative explanation: these small authored paths
cover the chosen generator but not arbitrary policy languages. A new native
owner, comparison relation, amendment rule or actor view needs its own stated
meaning and discriminator. The complete source-hashed run manifest, checks,
full results and code snapshots are retained in attempt-01.
