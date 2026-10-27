"""Prepare the successor control refresh without rerunning frozen refreshers."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/group-indirect-integration-20261025/finish.py').read_text()
changes=[('accounting-sector-posting-boundary-20261025.md','accounting-insurance-fiscal-boundary-20261025.md'),
 ('indirect-cash-integration-20261025/coverage.json','group-indirect-integration-20261025/coverage.json'),
 ('pages = [1, 409, 410, 411]','pages = [1, 405, 406, 407, 408, 409]'),
 ('4.27','4.28'),('4.26','4.27'),('524 pages','525 pages'),
 ('Legal-trace group cash explanation and exact internal-flow correction integrated in4.28.',
  'Exact insurer posting, loss-component memory and cumulative reports integrated in4.28.'),
 ('Group indirect cash explanation integrated','Exact insurer posting explanation integrated'),
 ('Fourteen focused tests, fifty-six regressions and eight complete cases replay.',
  'Sixteen focused tests, fifty-seven regressions and eight complete cases replay.'),
 ('Legal reports and prior group financial results remain preserved; admission stays provisional.',
  'Native journals, loss origins, unit alias and original dates remain preserved; admission stays provisional.'),
 ('Cover and PDF409–411 were viewed; no new warnings, five inherited underfull notices.',
  'Cover and PDF405–409 were viewed; no new warnings, five inherited underfull notices.'),
 ('which retained sector measurement can supply an explicit, faithful common-book posting contract?',
  'can the exact insurer journals survive explicit fiscal carry without changing their native dates?'),
 ("['group-indirect-cash-20261025',HERE.name]","['insurance-loss-book-20261025',HERE.name]"),
 ('Audit retained sector measurements, state, units and posting boundaries',
  'Compose retained insurer journals with explicit fiscal carry and unchanged native event dates'),
 ('Version4.27 plus locked group indirect-cash evidence','Version4.27 plus locked insurer journal and loss-memory evidence'),
 ('accounting-group-indirect-integration-20261025.md','accounting-insurance-loss-integration-20261025.md')]
for old,new in changes:
    assert old in text,old
    text=text.replace(old,new)
assert not (HERE/'finish.py').exists();compile(text,'finish.py','exec');(HERE/'finish.py').write_text(text)
print('Prepared integration control refresh')
