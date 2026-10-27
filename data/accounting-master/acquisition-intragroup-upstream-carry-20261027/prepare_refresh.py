from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'refresh.py';assert not p.exists()
s=(H.parent/'acquisition-intragroup-upstream-20261027/refresh.py').read_text()
changes=[
('gap-intragroup-upstream-refresh-20261027','gap-upstream-carry-refresh-20261027'),
('accounting-intragroup-upstream-integration-20261027','accounting-upstream-carry-integration-20261027'),
('accounting-intragroup-upstream-20261027','accounting-intragroup-upstream-carry-20261027'),
('gap-intragroup-carry-integration-refresh-20261027','gap-intragroup-upstream-integration-refresh-20261027'),
('5.33','5.34'),('800 pages','801 pages'),('800 main pages','801 main pages'),('235 total / 214 body','236 total / 215 body'),
('Complete upstream inventory, gross supplier cash and NCI attribution','Complete upstream opening/NCI carry and later margin release'),
('66 full cases,36 controls,3922 assertions; full legal journals,group worksheets,supplier cash and NCI attribution pass','36 full cases,27 controls,1121 assertions; full upstream opening/closing accounts,journals and NCI/tax timing pass'),
('Prior upstream margin or its tax is carried into the wrong owners or repeated at opening','A prior interest or debt conversion is treated as new cash consideration without remeasurement or transaction separation'),
('Close full legal and group accounts,carry only the established opening bridge,then compare upstream margin release and NCI under recognised and unrecognised tax.','Inspect acquisition/prior-interest and debt-conversion authority,then compare prior carrying value,fair value,remeasurement and consideration boundaries.'),
('Selected upstream one-year attribution checked; upstream opening/NCI carry remains next','Selected upstream carry checked; prior-interest/debt-conversion acquisition boundary remains open'),
('Upstream inventory passes66 cases/3922 assertions with complete journals,external supplier cash,full elimination and conditional NCI/tax attribution.','Upstream carry passes36 cases/1121 assertions with complete closed openings,NCI,margin release and recognised/unrecognised tax timing.'),
('Integrate checked upstream attribution under accounting-upstream-carry-integration-20261027.md; then compare upstream two-year opening equity,NCI and margin release.','Integrate checked upstream carry under accounting-upstream-carry-integration-20261027.md; then inspect and specify acquisition with prior interests/debt conversion.'),
('intragroup_upstream_result','intragroup_upstream_carry_result'),
('Upstream journals,supplier cash and NCI attribution checked','Upstream opening/NCI carry and later margin release checked'),
('Integrate checked upstream inventory and NCI attribution','Integrate checked upstream opening/NCI and tax carry'),
('Upstream inventory attribution checked','Upstream opening and NCI carry checked'),
('ConditionalUpstreamInventory/1 passes66 cases,36 controls,3922 assertions.','ConditionalUpstreamCarry/1 passes36 cases,27 controls,1121 assertions.'),
('Full legal journals,external supplier cash and NCI attribution are checked; actual','Complete upstream opening/NCI,tax timing and later release are checked; actual'),
('one-year upstream attribution does not establish upstream retained/NCI carry or actual continuing schedules/control.','upstream retained/NCI carry does not establish prior-interest acquisitions or actual continuing schedules/control.'),
('Integrate checked upstream,then compare two-year opening and margin release','Integrate checked upstream carry,then inspect prior-interest and conversion boundaries'),
('One checked upstream delta and one carry interface challenge added.','One checked upstream carry delta and one prior-interest interface challenge added.'),
]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared upstream carry refresh.')
