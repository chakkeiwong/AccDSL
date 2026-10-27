"""Prepare master refresh after the checked statement explanation."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/insurance-loss-integration-20261025/finish.py').read_text()
changes=[('accounting-insurance-fiscal-boundary-20261025.md','accounting-credit-posting-representation-20261025.md'),
 ('group-indirect-integration-20261025/coverage.json','insurance-fiscal-integration-20261025/coverage.json'),
 ('pages = [1, 405, 406, 407, 408, 409]','pages = [1, 408, 409, 410]'),
 ('4.28','4.30'),('4.27','4.29'),('525 pages','527 pages'),
 ('Exact insurer posting, loss-component memory and cumulative reports integrated in4.30.',
  'Annual insurer operating-cash explanations under two supplied classifications integrated in4.30.'),
 ('Exact insurer posting explanation integrated','Annual insurer statement explanation integrated'),
 ('Sixteen focused tests, fifty-seven regressions and eight complete cases replay.',
  'Eight focused tests, twenty-six regressions and twenty-four complete exchanges replay.'),
 ('Native journals, loss origins, unit alias and original dates remain preserved; admission stays provisional.',
  'Exact fiscal reports and gross postings survive alternative explicit classifications; admission stays provisional.'),
 ('Cover and PDF405–409 were viewed; no new warnings, five inherited underfull notices.',
  'Cover and PDF408–410 were viewed; no new warnings, five inherited underfull notices.'),
 ('can the exact insurer journals survive explicit fiscal carry without changing their native dates?',
  'how should linked interval-valued credit measurements reach an exact book without invented point values?'),
 ("['insurance-loss-book-20261025',HERE.name]","['insurance-statement-bridge-20261025',HERE.name]"),
 ('Compose retained insurer journals with explicit fiscal carry and unchanged native event dates',
  'Audit linked credit measurements, exact cases and explicit representation choices before posting'),
 ('Version4.29 plus locked insurer journal and loss-memory evidence','Version4.29 plus locked fiscal insurer statement exchanges'),
 ('accounting-insurance-loss-integration-20261025.md','accounting-insurance-statement-integration-20261025.md')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared statement integration control refresh')
