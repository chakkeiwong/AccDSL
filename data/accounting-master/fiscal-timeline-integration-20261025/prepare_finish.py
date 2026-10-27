from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'finish.py').exists()
text=(ROOT/'data/accounting-master/assessment-timeline-integration-20261025/finish.py').read_text()
changes=[
 ('docs/plans/accounting-fiscal-timeline-20261025.md','docs/plans/accounting-post-fiscal-reassessment-20261025.md'),
 ('data/accounting-master/retained-population-integration-20261025/coverage.json','data/accounting-master/assessment-timeline-integration-20261025/coverage.json'),
 ('pages = [1, 407, 408, 409, 410]','pages = [1, 408, 409, 410, 411]'),
 ('4.38','4.39'),
 ('Current-assessment timing integrated','State-bound fiscal timeline integrated'),
 ('Current-assessment interval and actual-turn state composed in4.39.','State-bound deferred measurement and terminal carry composed in4.39.'),
 ('12 focused tests,49 regressions and8 complete exchanges replay.','13 focused tests,61 regressions and12 complete exchanges replay.'),
 ('Sale/assessment order preserves native interval refusal and valid prefixes.','Deferred measurement preserves exact state binding; stale evidence refuses with its valid prefix.'),
 ('Replacement updates one tax vintage; unknown facts and 32/64 action limits retain their meanings.','Terminal carry archives the old report; separately bound next-period decisions preserve vintages and stock reserve.'),
 ('Cover and PDF407–410','Cover and PDF408–411'),
 ('how can deferred measurement and fiscal carry retain exact state and period binding?','which substantive simulator dependency remains after completed fiscal composition?'),
 ("['assessment-timeline-20261025',HERE.name]","['fiscal-timeline-20261025',HERE.name]"),
 ('Compose state-bound deferred assessment and terminal fiscal carry under a new audited plan','Reassess source/reuse, authoring, real-source and numerical dependencies against completed fiscal design'),
 ('Version4.37 plus accepted current-assessment timeline exchanges','Version4.38 plus accepted fiscal timeline exchanges'),
 ('docs/plans/accounting-assessment-timeline-20261025.md','docs/plans/accounting-fiscal-timeline-20261025.md'),
 ('4.39;533 pages;not_ready','4.39;534 pages;not_ready'),
 ("'prepare_finish.py','finish.py']","'prepare_finish.py','finish.py','spacing-repair.json','repair_spacing.py']")]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
compile(text,'finish.py','exec');(HERE/'finish.py').write_text(text)
print('Prepared4.39 control refresh')
