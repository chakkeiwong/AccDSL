"""Create a successor refresher; preserve frozen predecessors."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/insurance-statement-integration-20261025/finish.py').read_text()
changes=[
 ('accounting-credit-posting-representation-20261025.md','accounting-credit-host-boundary-20261025.md'),
 ('insurance-fiscal-integration-20261025/coverage.json','insurance-statement-integration-20261025/coverage.json'),
 ("HERE / 'integrate.py'","HERE / 'integrate_v2.py'"),
 ('pages = [1, 408, 409, 410]','pages = [1, 408, 409, 410, 411]'),
 ("'4.30'","'4.31'"),('Version 4.30','Version 4.31'),('in4.30','in4.31'),
 ('4.30;527 pages','4.31;528 pages'),
 ('Annual insurer statement explanation integrated','Shared exact credit measurements integrated'),
 ('Annual insurer operating-cash explanations under two supplied classifications integrated','Exact shared-factor credit measurements and bounded equality integrated'),
 ('Eight focused tests, twenty-six regressions and twenty-four complete exchanges replay.',
  '23 focused tests,44 regressions,9 schedules and53 native refusals replay.\n652 identities,80 authored targets and986 contained enclosures pass.'),
 ('Exact fiscal reports and gross postings survive alternative explicit classifications; admission stays provisional.',
  'Exact shared factors preserve57 stages and63 journals; host and accounting admission remain false.'),
 ('Cover and PDF408–410 were viewed; no new warnings, five inherited underfull notices.',
  'Cover and PDF408–411 were viewed; first overfull line repaired, no new warnings, five inherited underfull notices.'),
 ('how should linked interval-valued credit measurements reach an exact book without invented point values?',
  'how can exact credit expressions cross the company-book boundary with context and dependence intact?'),
 ('insurance-statement-bridge-20261025','credit-linked-measurements-20261025'),
 ('Audit linked credit measurements, exact cases and explicit representation choices before posting',
  'Audit exact credit amounts at the rational company-book boundary and specify the next supported integration'),
 ("'build.json'","'build-v2.json'"),("'build.log'","'build-v2.log'"),
 ('accounting-insurance-statement-integration-20261025.md','accounting-credit-linked-integration-20261025.md'),
 ('Version4.29 plus locked fiscal insurer statement exchanges','Version4.30 plus accepted exact shared-factor credit exchanges'),
 ('python3 -B integrate.py prepare/build; integrate.py verify; finish.py',
  'python3 -B integrate.py prepare/build; repair_layout.py; integrate_v2.py build/verify; finish.py')]
for old,new in changes:
    assert old in text,old;text=text.replace(old,new)
text=text.replace("'integrate.py','setup.py','prepare_finish.py','finish.py'",
    "'integrate.py','integrate_v2.py','setup.py','repair_layout.py','layout-repair-lock.json','prepare_finish.py','finish.py'")
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists()
(HERE/'finish.py').write_text(text)
print('Successor control refresher prepared')
