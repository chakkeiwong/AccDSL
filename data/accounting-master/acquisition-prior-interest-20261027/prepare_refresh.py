from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'refresh.py';assert not p.exists()
s=(H.parent/'acquisition-intragroup-upstream-carry-20261027/refresh.py').read_text()
changes=[
('gap-upstream-carry-refresh-20261027','gap-prior-interest-refresh-20261027'),
('accounting-upstream-carry-integration-20261027','accounting-prior-interest-worksheet-20261027'),
('accounting-intragroup-upstream-carry-20261027','accounting-prior-interest-acquisition-20261027'),
('gap-intragroup-upstream-integration-refresh-20261027','gap-upstream-carry-integration-refresh-20261027'),
('5.34','5.35'),('801 pages','802 pages'),('801 main pages','802 main pages'),('236 total / 215 body','237 total / 216 body'),
('Complete upstream opening/NCI carry and later margin release','Typed prior-equity remeasurement and OCI expressions'),
('36 full cases,27 controls,1121 assertions; full upstream opening/closing accounts,journals and NCI/tax timing pass','19 cases,19 controls,365 assertions; exact conditional prior-equity/OCI expressions and unresolved dependencies pass'),
('A prior interest or debt conversion is treated as new cash consideration without remeasurement or transaction separation','A symbolic prior-equity expression is used as if it supplied legal books,tax or measured group reports'),
('Inspect acquisition/prior-interest and debt-conversion authority,then compare prior carrying value,fair value,remeasurement and consideration boundaries.','Compare complete explicitly supplied prior-equity legal journals,remeasurement,new cash,group reports and NCI without inventing tax or combined investment measurements.'),
('Selected upstream carry checked; prior-interest/debt-conversion acquisition boundary remains open','Typed prior-equity expressions checked; full measured prior-equity worksheet remains next'),
('Upstream carry passes36 cases/1121 assertions with complete closed openings,NCI,margin release and recognised/unrecognised tax timing.','Prior-equity symbolic extension passes19 cases/365 assertions with explicit FVTPL/equity-FVOCI presentation and unresolved debt/legal/tax dependencies.'),
('Integrate checked upstream carry under accounting-prior-interest-worksheet-20261027.md; then inspect and specify acquisition with prior interests/debt conversion.','Execute accounting-prior-interest-worksheet-20261027.md; then integrate checked prior-equity companions and continue debt conversion,loss/ownership and general methods.'),
('intragroup_upstream_carry_result','prior_interest_symbolic_result'),
('Upstream opening/NCI carry and later margin release checked; manuscript integration next.','Prior-equity symbolic branches checked; full conditional worksheet next.'),
('Integrate checked upstream opening/NCI and tax carry','Compare complete prior-equity acquisition worksheets'),
('Upstream opening and NCI carry checked','Prior-equity symbolic classification checked'),
('ConditionalUpstreamCarry/1 passes36 cases,27 controls,1121 assertions.','ConditionalPriorEquityExpressions/1 passes19 cases,19 controls,365 assertions.'),
('Complete upstream opening/NCI,tax timing and later release are checked; actual','Typed prior-equity and OCI expressions are checked; complete reports and actual'),
('upstream retained/NCI carry does not establish prior-interest acquisitions or actual continuing schedules/control.','typed prior-equity expressions do not establish complete measured reports,legal-book accounting or tax.'),
('Integrate checked upstream carry,then inspect prior-interest and conversion boundaries','Compare full prior-equity worksheet with explicit legal/measurement/tax premises'),
('One checked upstream carry delta and one prior-interest interface challenge added.','One checked prior-equity symbolic delta and one measured-worksheet challenge added.'),
]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared prior-equity refresh.')
