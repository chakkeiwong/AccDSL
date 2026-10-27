# DeclaredOperatingMethods/1

Builder inputs: valid CompanyBook/1,exact schema registry,explicit role map and
unit-cost memory pointer. Roles:cash,receivables,inventory,payables,payroll_payable,
revenue,cost_of_sales,payroll. Every role maps injectively to a declared account
with exact classification. The memory leaf has currency/goods-unit dimensions,
same company context and scale1; its rational value must be strictly positive.
Return six data-only CompanyMethodRegistry/1 entries. No callbacks or native
postings are imported. Runtime uses the checked requirements/monetary/memory engines.

purchase: nonnegative units; debit inventory and credit payables by units*unit_cost.
deliver: nonnegative units and consideration; require enough inventory; debit
receivables/credit revenue for consideration, debit cost_of_sales/credit inventory
for units*unit_cost. collect: nonnegative amount no greater than receivables;
debit cash/credit receivables. supplier_pay: amount<=-payables and<=cash; debit
payables/credit cash. payroll_accrue: nonnegative amount; debit payroll/credit
payroll_payable. payroll_pay: amount<=-payroll_payable and<=cash; debit payable/
credit cash. Cash flows for collections and payments are operating,with explicit
native origin names. Other entries have no cash flow. Zero activity is retained
as an event with zero effect,following the selected comparator.

Every event supplies approved as a typed hypothetical finding;unknown yields
unresolved,false unsupported. This is not a source-admission decision. Conditions
also require proper signs on relevant control accounts before/after the event.
Unit cost is read from current declared memory; all memory is preserved,including
unrelated typed fields. Account map is explicit and never derived from labels.
A builder creates method definitions only; registry digest and dependencies are
checked by the existing program. Positive findings are authored synthetic premises.

First conformance case uses full native account population and extra preserved
memory; second uses a different owner and arbitrary mapped account IDs. Native
Engine supplies independent transition/journal/cash comparisons,not execution.
Assets,applied history and journal metadata stay native comparison evidence;
no full native-state migration is claimed. Program final reports and matched text
are checked,with separately derived cash107,receivables15,stock25,payables10,wages
payable2,profit15,equity135. Statement-only notes remain missing pending the next
trace-derived roll-forward contract.

Refusal interpretation: the retained requirement engine has invalid/unsupported/
unresolved primitive statuses. A separate exact-result diagnostic identifies an
isolated false cash_available condition as economic_funding_failure,matching the
native funding-default example without relabelling any other failed/unknown finding.
The underlying refusal and hash remain visible. This does not close the mission's
future general typed economic-default result requirement; program status is unchanged.
