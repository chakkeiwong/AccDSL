"""Prepare fiscal-candidate controls with the corrected unique page locator."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/insurance-loss-integration-20261025/finish.py').read_text()
changes=[('accounting-insurance-fiscal-boundary-20261025.md','accounting-insurance-statement-bridge-20261025.md'),
 ('group-indirect-integration-20261025/coverage.json','insurance-loss-integration-20261025/coverage.json'),
 ('pages = [1, 405, 406, 407, 408, 409]','pages = [1, 407, 408, 409, 410]'),
 ('4.28','4.29'),('4.27','4.28'),('525 pages','526 pages'),
 ('Exact insurer posting, loss-component memory and cumulative reports integrated in4.29.',
  'Explicit insurer calendar-year carry, unchanged native journals and annual reports integrated in4.29.'),
 ('Exact insurer posting explanation integrated','Explicit insurer fiscal carry integrated'),
 ('Sixteen focused tests, fifty-seven regressions and eight complete cases replay.',
  'Fourteen focused tests, seventy-one regressions and eight complete cases replay.'),
 ('Native journals, loss origins, unit alias and original dates remain preserved; admission stays provisional.',
  'Native journals, loss origins and original dates survive explicit annual carry; completeness stays unadmitted.'),
 ('Cover and PDF405–409 were viewed; no new warnings, five inherited underfull notices.',
  'Cover and PDF407–410 were viewed; no new warnings, five inherited underfull notices.'),
 ('can the exact insurer journals survive explicit fiscal carry without changing their native dates?',
  'can supplied classifications reconcile insurer annual profit to cash without a residual or unique-policy claim?'),
 ("['insurance-loss-book-20261025',HERE.name]","['insurance-fiscal-book-20261025',HERE.name]"),
 ('Compose retained insurer journals with explicit fiscal carry and unchanged native event dates',
  'Compose existing insurer fiscal reports and indirect explanations under two supplied classifications'),
 ('Version4.28 plus locked insurer journal and loss-memory evidence','Version4.28 plus locked exact insurer fiscal-carry evidence'),
 ('accounting-insurance-loss-integration-20261025.md','accounting-insurance-fiscal-integration-20261025.md'),
 ("HERE / 'integrate.py'","HERE / 'integrate_v2.py'"),
 ("'integrate.py','setup.py','prepare_finish.py','finish.py'",
  "'integrate.py','integrate_v2.py','setup.py','prepare_finish.py','finish.py','attempt-01-page-locator/reason.md','attempt-01-page-locator/integration-verification.json'"),
 ('integrate.py verify; finish.py','integrate_v2.py verify; finish.py')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared fiscal integration control refresh')
