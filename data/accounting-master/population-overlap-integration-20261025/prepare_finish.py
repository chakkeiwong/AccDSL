"""Prepare this increment's one-time control refresh from inspected precedent."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'finish.py').exists()
text=(ROOT/'data/accounting-master/network-history-integration-20261025/finish.py').read_text()
changes=[
 ('docs/plans/accounting-cash-population-reconciliation-20261025.md','docs/plans/accounting-retained-population-overlap-20261025.md'),
 ('data/accounting-master/statement-history-integration-20261025/coverage.json','data/accounting-master/network-history-integration-20261025/coverage.json'),
 ('pages = [1, 390, 391, 392, 393]','pages = [1, 391, 392, 393]'),
 ("{'MC01','MC04','MC05','MC09','MC10','MC24','MC28','MC32','MC33','MC34','MC35'}","{'MC01','MC04','MC06','MC09','MC20','MC24','MC28','MC35'}"),
 ('4.35','4.36'),('531','532'),
 ('Retained network histories integrated','Cash populations and conditional overlap integrated'),
 ('Selected source-network and opening-history constraints integrated in4.36.','Source populations and optional aggregate overlap constraints integrated in4.36.'),
 ('10 focused tests,44 regressions and11 complete exchanges replay.','11 focused tests,48 regressions,10 complete exchanges and4 explicit witnesses replay.'),
 ('Full256-observation/143-relation reports and both source/history constraint systems remain preserved.','Retained PDF and tagged cash facts, precision and dimensions are preserved; no residual account is invented.'),
 ('Reported openings reject prior constructed histories; population differences and source dash remain explicit.','Unknown overlap and equal totals retain distinct decompositions; disjoint restricted-cash addition is rejected.'),
 ('Cover and PDF390–393','Cover and PDF391–393'),
 ('what source evidence supports the different reported cash populations and their overlap?','how can overlap regions constrain the retained temporal network without replacing source observations?'),
 ("['retained-network-history-20261025',HERE.name]","['cash-population-reconciliation-20261025','population-overlap-20261025',HERE.name]"),
 ('Resolve source cash populations and overlap before repairing history mappings','Attach conditional overlap regions to unchanged retained temporal source observations')]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
compile(text,'finish.py','exec');(HERE/'finish.py').write_text(text)
print('Prepared one-time control refresh')
