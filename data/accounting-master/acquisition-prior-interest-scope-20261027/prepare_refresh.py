from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'refresh.py';assert not p.exists()
s=(H.parent/'acquisition-prior-interest-20261027/refresh.py').read_text()
changes=[('gap-prior-interest-refresh-20261027','gap-prior-interest-scope-refresh-20261027'),
('gap-upstream-carry-integration-refresh-20261027','gap-prior-interest-refresh-20261027'),
('accounting-prior-interest-acquisition-20261027.md','accounting-prior-interest-worksheet-20261027.md'),
('Typed prior-equity remeasurement and OCI expressions','Source-bound significant-influence and joint-control scope repair'),
('19 cases,19 controls,365 assertions; exact conditional prior-equity/OCI expressions and unresolved dependencies pass','25 cases,11 controls,368 assertions; exact conditional relationship scopes,expressions and unresolved dependencies pass'),
('A symbolic prior-equity expression is used as if it supplied legal books,tax or measured group reports','Absence of control at20% ownership is mistaken for absence of significant influence or joint control'),
('Compare complete explicitly supplied prior-equity legal journals,remeasurement,new cash,group reports and NCI without inventing tax or combined investment measurements.','Require separately sourced significant-influence and joint-control assertions; unknown or positive relationships retain a method dependency.'),
('Typed prior-equity expressions checked; full measured prior-equity worksheet remains next','Prior relationship scope repaired conditionally; actual relationship assessment and full worksheet remain open'),
('Prior-equity symbolic extension passes19 cases/365 assertions with explicit FVTPL/equity-FVOCI presentation and unresolved debt/legal/tax dependencies.','Prior-equity /2 scope repair passes25 cases/368 assertions; separate significant-influence and joint-control assertions required.'),
('prior_interest_symbolic_result','prior_interest_scope_result'),
('Prior-equity symbolic branches checked; full conditional worksheet next.','Prior-equity relationship scope repaired; full conditional worksheet next.'),
('Prior-equity symbolic classification checked','Prior-equity relationship scope repaired'),
('ConditionalPriorEquityExpressions/1 passes19 cases,19 controls,365 assertions.','ConditionalPriorEquityExpressions/2 passes25 cases,11 controls,368 assertions.'),
('Typed prior-equity and OCI expressions are checked; complete reports and actual','Typed prior relationship scope is checked; complete reports and actual'),
('One checked prior-equity symbolic delta and one measured-worksheet challenge added.','One checked relationship-scope repair delta and one influence/joint-control challenge added.')]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared scope repair refresh.')
