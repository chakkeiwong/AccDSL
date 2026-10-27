# Authored settlement policies

A fixed cash allocation and a collection fraction specify different decisions.
Changing an invoice price leaves a fixed allocation unchanged. Reapplying a
fraction to the new invoice instead changes the collection. SettlementPolicyDraft/1
makes the latter instruction explicit: it names the input path, year, delivery
operations, receivable claims, collection operations, fraction and installment
shares. It produces a new conditional input path and a trace of each generated
amount. The original fixed instructions remain queryable.

For Northstar's second year, two invoices each rise to 192 after the price
revision. The original two installments each collect 79.2 per claim. The declared
90% rule generates 86.4 per installment, leaving 19.2 per claim. Across two claims
and two installments, cash increases by 28.8 and receivables decrease by 28.8.
Revenue and profit stay equal because the policy changes settlement rather than
recognition. These are exact consequences of the authored instructions; the
fraction is an illustrative assumption rather than a fitted behavioral relation.

The generator preserves every other input and uses the existing canonical
rational representation. Unknown fractions or invoice inputs stay unresolved.
Collections must follow delivery in the authored schedule. Duplicate claim or
operation identities are invalid. An additional collection against a targeted
claim outside the policy is unsupported in this draft, because no priority rule
has been specified. Generated paths still undergo accounting execution: policy
materialization alone does not prove cash sufficiency or a complete year.

The saved trace binds the policy, parent input, generated input, prior and new
allocation amounts, invoice totals and uncollected amounts. Recomputing this
trace verifies policy correspondence; replay checks accounting consequences.
Policy information times remain unadmitted. Existing source or annual-path
timestamps cannot establish when this new instruction was chosen.

The 99-check reference and its exact report comparisons are under
data/accounting-master/company-policy-20261023. This is a bounded design
increment awaiting integration into the provisional manuscript, not a complete
policy language or production runtime.
