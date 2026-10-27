from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'advance.py';assert not p.exists()
s=(H.parent/'intragroup-carry-integration-20261027/advance.py').read_text()
changes=[('5.33','5.34'),('5.32','5.33'),('800','801'),('798','800'),
('gap-intragroup-carry-integration-refresh-20261027','gap-intragroup-upstream-integration-refresh-20261027'),
('gap-partial-frontier-policy-refresh-20261027','gap-intragroup-upstream-refresh-20261027'),
('accounting-intragroup-upstream-20261027.md','accounting-intragroup-upstream-carry-20261027.md'),
('accounting-intragroup-carry-integration-20261027.md','accounting-intragroup-upstream-integration-20261027.md'),
('intragroup-carry-integration-20261027/result.md','intragroup-upstream-integration-20261027/result.md'),
('observation-frontier-rebase-20261027/result.md','intragroup-carry-integration-20261027/result.md'),
('685','686'),('261','262'),('145 evidence','144 evidence'),
('**235 total / 214 body','**236 total / 215 body'),('**235 pages**','**236 pages**'),('**233 pages**','**235 pages**'),('**214 body pages**','**215 body pages**'),('**212 body pages**','**214 body pages**'),
('cross_interface_challenges=75,successor_deltas=75','cross_interface_challenges=76,successor_deltas=77'),
('Protected two-year inventory carry manuscript integration','Protected upstream inventory manuscript integration'),
('closed opening equity, carried inventory margin and recurring equipment/tax explanations','upstream inventory, external supplier cash and conditional NCI attribution'),
('Closed opening equity, carried inventory margin and recurring equipment/tax\nare integrated. Negative NCI profit and the concurrent observation/frontier work are preserved.','Upstream inventory, external supplier cash and conditional NCI attribution\nare integrated. Prior carry and concurrent observation/frontier work are preserved.'),
('two-year inventory carry','upstream inventory attribution'),
('Two-year inventory carry integrated','Upstream inventory attribution integrated'),
('Next: audited upstream inventory and NCI attribution.','Next: audited upstream opening equity and NCI carry.'),
('compare complete upstream journals, supplier cash, group elimination and NCI attribution; then prior interests/debt conversion,loss/ownership and general methods.','compare complete upstream opening equity,NCI and later margin/tax release; then prior interests/debt conversion,loss/ownership and general methods.'),
('Compare upstream inventory, external supplier cash and NCI attribution','Compare upstream two-year opening equity and NCI carry'),
('Next is upstream attribution','Next is upstream two-year carry'),
('Upstream seller attribution and external supplier cash are explicit dependencies of the next financial unit.','Upstream retained/NCI balances,unrecognised tax and recurring equipment schedules are explicit dependencies of the next financial unit.')]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
compile(s,str(p),'exec');p.write_text(s);print('Prepared guarded upstream advancement.')
