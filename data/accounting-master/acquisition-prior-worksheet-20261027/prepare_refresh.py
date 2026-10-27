from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'refresh.py';assert not p.exists()
s=(H.parent/'acquisition-prior-interest-scope-20261027/refresh.py').read_text()
s=s.replace("NEXT='docs/plans/accounting-prior-interest-worksheet-20261027.md'","NEXT='docs/plans/accounting-prior-equity-integration-20261027.md'")
changes=[('gap-prior-interest-scope-refresh-20261027','gap-prior-worksheet-refresh-20261027'),
('gap-prior-interest-refresh-20261027','gap-prior-interest-scope-refresh-20261027'),
('Source-bound significant-influence and joint-control scope repair','Complete conditional prior-equity acquisition worksheet'),
('25 cases,11 controls,368 assertions; exact conditional relationship scopes,expressions and unresolved dependencies pass','8 cases,21 controls,334 assertions; full legal journals,group worksheets,parent-only remeasurement,NCI and cash pass'),
('Absence of control at20% ownership is mistaken for absence of significant influence or joint control','A converted debt claim is treated as prior equity or its settlement is included twice in acquisition consideration'),
('Require separately sourced significant-influence and joint-control assertions; unknown or positive relationships retain a method dependency.','Inspect issuer/creditor debt-conversion and pre-existing-relationship rules; distinguish consideration,settlement,extinguishment and equity fair values before computation.'),
('Prior relationship scope repaired conditionally; actual relationship assessment and full worksheet remain open','Finite prior-equity worksheet checked; debt-conversion/separate-relationship accounting remains open'),
('Prior-equity /2 scope repair passes25 cases/368 assertions; separate significant-influence and joint-control assertions required.','Prior-equity worksheet passes8 cases/334 assertions with explicit legal,valuation,tax and relationship assumptions; signed parent-only gain and full accounts checked.'),
('Execute accounting-prior-interest-worksheet-20261027.md; then integrate checked prior-equity companions and continue debt conversion,loss/ownership and general methods.','Integrate checked prior-equity companions under accounting-prior-equity-integration-20261027.md; then inspect debt conversion,loss/ownership and general methods.'),
('prior_interest_scope_result','prior_equity_worksheet_result'),
('Prior-equity relationship scope repaired; full conditional worksheet next.','Complete prior-equity worksheet checked; protected manuscript integration next.'),
('Compare complete prior-equity acquisition worksheets','Integrate checked prior-equity expressions,scope and complete worksheet'),
('Prior-equity relationship scope repaired','Complete prior-equity worksheet checked'),
('ConditionalPriorEquityExpressions/2 passes25 cases,11 controls,368 assertions.','ConditionalPriorEquityWorksheet/1 passes8 cases,21 controls,334 assertions.'),
('Typed prior relationship scope is checked; complete reports and actual','Complete conditional prior-equity journals and reports are checked; actual'),
('One checked relationship-scope repair delta and one influence/joint-control challenge added.','One complete prior-equity worksheet delta and one debt-conversion interface challenge added.')]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared complete worksheet refresh.')
