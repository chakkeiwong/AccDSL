from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'finish.py').exists()
text=(ROOT/'data/accounting-master/retained-population-integration-20261025/finish.py').read_text()
changes=[
 ('docs/plans/accounting-source-history-reassessment-20261025.md','docs/plans/accounting-fiscal-timeline-20261025.md'),
 ('data/accounting-master/population-overlap-integration-20261025/coverage.json','data/accounting-master/retained-population-integration-20261025/coverage.json'),
 ('pages = [1, 392, 393, 394]','pages = [1, 407, 408, 409, 410]'),
 ('4.37','4.38'),
 ("advanced = {'MC01','MC04','MC06','MC09','MC20','MC24','MC28','MC35'}","advanced = {'MC13','MC15','MC16','MC24','MC28','MC32','MC35'}"),
 ('Retained population constraints integrated','Current-assessment timing integrated'),
 ('Conditional overlap and retained temporal source network composed in4.38.','Current-assessment interval and actual-turn state composed in4.38.'),
 ('6 focused tests,34 regressions,8 complete exchanges and2 full-system witnesses replay.','12 focused tests,49 regressions and8 complete exchanges replay.'),
 ('All114 source observations/38 relations survive; six regions/four equations form120/42.','Sale/assessment order preserves native interval refusal and valid prefixes.'),
 ('The complete256/143 source report, distinct populations and unresolved dash remain preserved.','Replacement updates one tax vintage; unknown facts and 32/64 action limits retain their meanings.'),
 ('Cover and PDF392–394','Cover and PDF407–410'),
 ('which substantive simulator dependency remains after completed source/history and overlap composition?','how can deferred measurement and fiscal carry retain exact state and period binding?'),
 ("['retained-population-overlap-20261025',HERE.name]","['assessment-timeline-20261025',HERE.name]"),
 ('Reassess broader simulator dependencies after completed source/history and overlap composition','Compose state-bound deferred assessment and terminal fiscal carry under a new audited plan'),
 ('Version4.34 plus accepted retained-network/history exchanges','Version4.37 plus accepted current-assessment timeline exchanges'),
 ('docs/plans/accounting-network-history-integration-20261025.md','docs/plans/accounting-assessment-timeline-20261025.md'),
 ('4.38;532 pages;not_ready','4.38;533 pages;not_ready')]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
compile(text,'finish.py','exec');(HERE/'finish.py').write_text(text)
print('Prepared4.38 control refresh')
