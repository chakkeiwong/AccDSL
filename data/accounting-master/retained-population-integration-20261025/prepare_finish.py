from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'finish.py').exists()
text=(ROOT/'data/accounting-master/population-overlap-integration-20261025/finish.py').read_text()
changes=[
 ('docs/plans/accounting-retained-population-overlap-20261025.md','docs/plans/accounting-source-history-reassessment-20261025.md'),
 ('data/accounting-master/network-history-integration-20261025/coverage.json','data/accounting-master/population-overlap-integration-20261025/coverage.json'),
 ('pages = [1, 391, 392, 393]','pages = [1, 392, 393, 394]'),
 ('4.36','4.37'),
 ('Cash populations and conditional overlap integrated','Retained population constraints integrated'),
 ('Source populations and optional aggregate overlap constraints integrated in4.37.','Conditional overlap and retained temporal source network composed in4.37.'),
 ('11 focused tests,48 regressions,10 complete exchanges and4 explicit witnesses replay.','6 focused tests,34 regressions,8 complete exchanges and2 full-system witnesses replay.'),
 ('Retained PDF and tagged cash facts, precision and dimensions are preserved; no residual account is invented.','All114 source observations/38 relations survive; six regions/four equations form120/42.'),
 ('Unknown overlap and equal totals retain distinct decompositions; disjoint restricted-cash addition is rejected.','The complete256/143 source report, distinct populations and unresolved dash remain preserved.'),
 ('Cover and PDF391–393','Cover and PDF392–394'),
 ('how can overlap regions constrain the retained temporal network without replacing source observations?','which substantive simulator dependency remains after completed source/history and overlap composition?'),
 ("['cash-population-reconciliation-20261025','population-overlap-20261025',HERE.name]","['retained-population-overlap-20261025',HERE.name]"),
 ('Attach conditional overlap regions to unchanged retained temporal source observations','Reassess broader simulator dependencies after completed source/history and overlap composition')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
compile(text,'finish.py','exec');(HERE/'finish.py').write_text(text)
print('Prepared4.37 control refresh')
