"""Prepare Version4.35 control refresh, preserving prior release records."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/statement-history-integration-20261025/finish.py').read_text()
changes=[
 ('accounting-retained-network-history-20261025.md','accounting-cash-population-reconciliation-20261025.md'),
 ('retained-history-integration-20261025/coverage.json','statement-history-integration-20261025/coverage.json'),
 ('pages = [1, 390, 391, 392]','pages = [1, 390, 391, 392, 393]'),
 ("'4.34'","'4.35'"),('Version 4.34','Version 4.35'),('in4.34','in4.35'),('4.34;530 pages','4.35;531 pages'),
 ('Joint statement histories integrated','Retained network histories integrated'),
 ('Selected cash and closing-balance history constraints integrated','Selected source-network and opening-history constraints integrated'),
 ('13 focused tests,62 regressions and14 complete exchanges replay.','10 focused tests,44 regressions and11 complete exchanges replay.'),
 ('Selected closing statements constrain the same history; actual openings and wider movements remain unresolved.','Reported openings reject prior constructed histories; population differences and source dash remain explicit.'),
 ('Cover and PDF390–392 were viewed; no new warnings, five inherited underfull notices.','Cover and PDF390–393 were viewed; no new warnings, five inherited underfull notices.'),
 ('which reported opening and movement constraints reject the current conditional histories?','what source evidence supports the different reported cash populations and their overlap?'),
 ("['retained-statement-history-20261025',HERE.name]","['retained-network-history-20261025',HERE.name]"),
 ('Attach reported openings and equity movements through the retained statement network','Resolve source cash populations and overlap before repairing history mappings'),
 ('accounting-statement-history-integration-20261025.md','accounting-network-history-integration-20261025.md'),
 ('Version4.33 plus accepted selected-statement/history exchanges','Version4.34 plus accepted retained-network/history exchanges')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared Version4.35 control refresh')
