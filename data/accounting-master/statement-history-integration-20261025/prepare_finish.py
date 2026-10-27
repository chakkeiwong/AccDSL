"""Prepare the bounded statement integration control refresh."""
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
text=(ROOT/'data/accounting-master/retained-history-integration-20261025/finish.py').read_text()
changes=[
 ('accounting-retained-statement-history-20261025.md','accounting-retained-network-history-20261025.md'),
 ('credit-linked-book-integration-20261025/coverage.json','retained-history-integration-20261025/coverage.json'),
 ('pages = [1, 389, 390, 391]','pages = [1, 390, 391, 392]'),
 ("'4.33'","'4.34'"),('Version 4.33','Version 4.34'),('in4.33','in4.34'),('4.33;529 pages','4.34;530 pages'),
 ('Retained source histories integrated','Joint statement histories integrated'),
 ('Selected source-bound conditional history composition integrated','Selected cash and closing-balance history constraints integrated'),
 ('15 focused tests,65 regressions and11 complete exchanges replay.','13 focused tests,62 regressions and14 complete exchanges replay.'),
 ('Separate source bases and unresolved actual-company facts remain explicit; admission stays false.','Selected closing statements constrain the same history; actual openings and wider movements remain unresolved.'),
 ('Cover and PDF389–391 were viewed; no new warnings, five inherited underfull notices.','Cover and PDF390–392 were viewed; no new warnings, five inherited underfull notices.'),
 ('can selected cash histories also satisfy retained balance-sheet constraints?','which reported opening and movement constraints reject the current conditional histories?'),
 ("['retained-source-history-20261025',HERE.name]","['retained-statement-history-20261025',HERE.name]"),
 ('Constrain selected cash histories with explicit retained balance-sheet evidence','Attach reported openings and equity movements through the retained statement network'),
 ('accounting-retained-history-integration-20261025.md','accounting-statement-history-integration-20261025.md'),
 ('Version4.32 plus accepted retained-source/history exchanges','Version4.33 plus accepted selected-statement/history exchanges')]
for old,new in changes:assert old in text,old;text=text.replace(old,new)
compile(text,'finish.py','exec');assert not (HERE/'finish.py').exists();(HERE/'finish.py').write_text(text)
print('Prepared Version4.34 control refresh')
