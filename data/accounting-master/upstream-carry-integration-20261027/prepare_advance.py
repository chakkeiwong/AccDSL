from pathlib import Path
H=Path(__file__).resolve().parent;p=H/'advance.py';assert not p.exists()
s=(H.parent/'intragroup-upstream-integration-20261027/advance.py').read_text()
changes=[('5.34','5.35'),('5.33','5.34'),('801 pages','802 pages'),('801 main pages','802 main pages'),('800 pages','801 pages'),
('gap-intragroup-upstream-integration-refresh-20261027','gap-upstream-carry-integration-refresh-20261027'),
('gap-intragroup-upstream-refresh-20261027','gap-upstream-carry-refresh-20261027'),
('accounting-intragroup-upstream-carry-20261027.md','accounting-prior-interest-acquisition-20261027.md'),
('accounting-intragroup-upstream-integration-20261027.md','accounting-upstream-carry-integration-20261027.md'),
('intragroup-upstream-integration-20261027/result.md','upstream-carry-integration-20261027/result.md'),
('intragroup-carry-integration-20261027/result.md','intragroup-upstream-integration-20261027/result.md'),
("v['checks']==686","v['checks']==701"),('686 checks','701 checks'),('686 document checks','701 document checks'),('262 predecessor','263 predecessor'),('preserve 262','preserve 263'),('144 evidence','157 evidence'),
('**236 total / 215 body','**237 total / 216 body'),('**236 pages**','**237 pages**'),('**235 pages**','**236 pages**'),('**215 body pages**','**216 body pages**'),('**214 body pages**','**215 body pages**'),
('cross_interface_challenges=76,successor_deltas=77','cross_interface_challenges=77,successor_deltas=79'),
('Protected upstream inventory manuscript integration','Protected upstream opening/NCI carry manuscript integration'),
('upstream inventory, external supplier cash and conditional NCI attribution','upstream retained profit,NCI and later margin/tax release'),
('Upstream inventory, external supplier cash and conditional NCI attribution','Upstream retained profit,NCI and later margin/tax release'),
('upstream inventory attribution','upstream opening and NCI carry'),('Upstream inventory attribution integrated','Upstream opening and NCI carry integrated'),
('Next: audited upstream opening equity and NCI carry.','Next: source-qualified prior-interest acquisition.'),
('compare complete upstream opening equity,NCI and later margin/tax release; then prior interests/debt conversion,loss/ownership and general methods.','inspect prior-equity and separate-transaction authority,then specify and compare prior interests/debt conversion,loss/ownership and general methods.'),
('Compare upstream two-year opening equity and NCI carry','Inspect and specify prior-interest acquisition and conversion boundaries'),
('Next is upstream two-year carry','Next is prior-interest acquisition'),
('Upstream retained/NCI balances,unrecognised tax and recurring equipment schedules are explicit dependencies of the next financial unit.','Prior-equity classification,remeasurement,OCI,tax and separate-transaction treatment are explicit dependencies of the next financial unit.')]
for old,new in changes:assert old in s,old;s=s.replace(old,new)
assert '20262027' not in s
compile(s,str(p),'exec');p.write_text(s);print('Prepared exact-anchor 5.35 advancement.')
