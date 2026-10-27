"""Adapt the prior explicit control refresh to the accepted group passage."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/indirect-cash-integration-20261025/finish.py').read_text()
replacements=[
 ('accounting-group-indirect-cash-20261025.md','accounting-sector-posting-boundary-20261025.md'),
 ('term-authoring-integration-20261025/coverage.json','indirect-cash-integration-20261025/coverage.json'),
 ('integrate_v2.py','integrate.py'),
 ('pages = [1, 396, 397, 398, 399, 400]','pages = [1, 409, 410, 411]'),
 ("'4.26'","'4.27'"),('Version 4.26','Version 4.27'),('4.26;523','4.27;524'),('in4.26','in4.27'),
 ('Conditional indirect cash explanation, exact cases and derivation integrated','Legal-trace group cash explanation and exact internal-flow correction integrated'),
 ('Conditional indirect cash explanation integrated','Group indirect cash explanation integrated'),
 ('Eleven focused tests, fifteen regressions and twenty complete cases replay.','Fourteen focused tests, fifty-six regressions and eight complete cases replay.'),
 ('Sixteen prior common projections remain equal; classifications stay provisional.','Legal reports and prior group financial results remain preserved; admission stays provisional.'),
 ('Cover and PDF396–400 were viewed; no new warnings, five inherited underfull notices.','Cover and PDF409–411 were viewed; no new warnings, five inherited underfull notices.'),
 ('how do verified legal-book cash bridges compose with explicit internal-flow removal?',
  'which retained sector measurement can supply an explicit, faithful common-book posting contract?'),
 ("['declared-indirect-profit-components-20261025',HERE.name]","['group-indirect-cash-20261025',HERE.name]"),
 ('Bind verified legal-book indirect bridges to the conditional group period report','Audit retained sector measurements, state, units and posting boundaries'),
 ("'integrate.py','verification-repair.md','repair_anchor.py','finish.py'","'integrate.py','setup.py','prepare_finish.py','finish.py'"),
 ('Version4.25 plus locked conditional indirect-cash evidence','Version4.26 plus locked group indirect-cash evidence'),
 ('accounting-indirect-cash-integration-20261025.md','accounting-group-indirect-integration-20261025.md')]
for old,new in replacements:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared explicit group integration control refresh.')
