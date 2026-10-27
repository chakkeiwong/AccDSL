from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'refresh.py';assert not p.exists()
s=(H.parent/'acquisition-intragroup-carry-20261027/refresh.py').read_text()
changes=[
('gap-intragroup-carry-refresh-20261027','gap-intragroup-upstream-refresh-20261027'),
('accounting-intragroup-carry-integration-20261027','accounting-intragroup-upstream-integration-20261027'),
('accounting-intragroup-carry-20261027','accounting-intragroup-upstream-20261027'),
('gap-observation-frontier-refresh-20261027','gap-intragroup-carry-integration-refresh-20261027'),
('5.32','5.33'),('798','800'),('233 total / 212 body','235 total / 214 body'),
('Complete two-year downstream opening bridge and retained-margin release','Complete upstream inventory, gross supplier cash and NCI attribution'),
('14 full cases,27 controls,598 assertions; full closed openings,bridge,journals,group reports and negative NCI profit pass','66 full cases,36 controls,3922 assertions; full legal journals,group worksheets,supplier cash and NCI attribution pass'),
('A downstream attribution or unchanged opening is silently applied to an upstream sale','Prior upstream margin or its tax is carried into the wrong owners or repeated at opening'),
('Acquire subsidiary inventory externally after control,then compare full upstream unrealised/realised profit and NCI without altering acquisition measurements.','Close full legal and group accounts,carry only the established opening bridge,then compare upstream margin release and NCI under recognised and unrecognised tax.'),
('Selected downstream carry checked; upstream attribution remains next','Selected upstream one-year attribution checked; upstream opening/NCI carry remains next'),
('Two-year downstream carry passes14 cases/598 assertions with full closed opening/group bridge,recurring depreciation/tax and negative NCI attribution.','Upstream inventory passes66 cases/3922 assertions with complete journals,external supplier cash,full elimination and conditional NCI/tax attribution.'),
('Integrate checked carry under accounting-intragroup-upstream-integration-20261027.md; then compare post-control upstream trade and NCI with independent full accounts.','Integrate checked upstream attribution under accounting-intragroup-upstream-integration-20261027.md; then compare upstream two-year opening equity,NCI and margin release.'),
('Integrate checked downstream and subsequent realisation companions; preserve independent observation-map work','Integrate checked upstream and prospective-policy companions; preserve independent work'),
('intragroup_carry_result','intragroup_upstream_result'),
('Two-year opening carry and retained-margin release checked','Upstream journals,supplier cash and NCI attribution checked'),
('Integrate checked two-year opening carry and margin release','Integrate checked upstream inventory and NCI attribution'),
('independent observation-map companions','independent prospective-policy companions'),
('Two-year downstream carry checked','Upstream inventory attribution checked'),
('ConditionalDownstreamCarry/1 passes14 cases,27 controls,598 assertions.','ConditionalUpstreamInventory/1 passes66 cases,36 controls,3922 assertions.'),
('Closed opening accounts,recurring depreciation/tax and negative NCI are checked; actual','Full legal journals,external supplier cash and NCI attribution are checked; actual'),
('two-year downstream carry','upstream inventory attribution'),('version 5.30 retained','version 5.33 retained'),
('downstream two-year carry does not establish upstream attribution or actual continuing schedules/control.','one-year upstream attribution does not establish upstream retained/NCI carry or actual continuing schedules/control.'),
('Integrate checked carry,then compare upstream with an independent acquisition/post-control boundary','Integrate checked upstream,then compare two-year opening and margin release'),
('independent observation-map work','independent prospective-policy work'),
('One checked carry delta and one upstream interface challenge added.','One checked upstream delta and one carry interface challenge added.'),
('two-year carry companion awaits integration','upstream companion awaits integration'),
]
for old,new in changes:
    assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared new upstream refresh.')
