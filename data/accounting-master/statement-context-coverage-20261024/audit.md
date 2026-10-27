# Full statement context audit

24 October 2026. The audited plan is
docs/plans/accounting-statement-context-coverage-20261024.md. Existing source
readings, both build_network.py implementations, original relation ledgers and
the portable observation pointers were inspected before extending the model.

The baseline contains 69 annual and 74 interim relations. Annual roles are
57 displayed pass/fail checks and 12 explanatory residuals; interim roles are
54 displayed checks, 12 residuals, three derived subtotals and five cross-period
endpoint comparisons. Those original roles remain in the preserved record.
New interpretation must correct two weaknesses rather than blindly copy them.

1. The annual other-equity, operating-reconciliation and working-capital
subtotals compare against hardcoded calculated totals. They do not provide
independent source targets, so their apparent zero residual is not independent
evidence. The interim builder already classifies its equivalents as explanatory.
Classify all six as derived subtotals, retain the old constants for provenance,
and expose no independent residual for them.
2. Portable contexts for equity and cash-flow endpoint rows retain the report
period string even when measurement_kind is instant balance. The exact instant
is retained in the pointed reading's measurement_date. Resolve that pointer and
expose the measurement instant separately; preserve the portable context unchanged.
Using the reporting interval as the stock's economic date would be wrong.

Two annual relations use the displayed debt-issuance dash. The earlier builder
uses a disclosed zero-contribution convention for its displayed-total checks.
This extension preserves the dash and returns unresolved arithmetic unless an
explicit convention is supplied in a future reviewed route. Five interim
relations explicitly remove an absent annual row. Retain those omissions; the
interim listed-row arithmetic is not a fact that the omitted transaction is zero.

The exact retained reading pointers resolve all 102/100 current rows and 27/27
opening comparisons. Ledger opening aliases are different from portable row
IDs (opening.cash versus opening.balance.cash). Record an explicit mapping;
do not edit original identities. Monetary, per-share and weighted-share values
retain distinct units. Stock-flow bridges need both dated endpoints and period
movements; cross-statement equality requires a declared same-measurement relation.
Closing cash equality is a displayed population comparison, not proof of
unrestricted legal cash or of the same population at every date.

The revised implementation will classify every relation, resolve each operand
and its measurement time, recompute arithmetic and retain its original purpose.
It will reconstruct the balance-change comparison from equity endpoint rows,
classify all six derived subtotals honestly, preserve all explanatory differences,
and report the two dash-dependent annual calculations as unresolved. All other
results remain displayed arithmetic, without exact latent or history admission.

Audit passes after these scope corrections. Primary acceptance is complete
source/ledger preservation, explicit context rules, independently checked
arithmetic, matched authoring and rejection of altered dates/units/aliases.
No proxy count certifies accounting or simulator completeness. Missing actual
state and the unresolved dash convention limit dependent claims; no global
continuation veto has fired. Source-driven generalization is still internal work.
