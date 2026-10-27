from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'refresh.py').exists()
text=(ROOT/'data/accounting-master/source-history-reassessment-20261025/refresh.py').read_text()
changes=[('accounting-assessment-timeline-20261025.md','accounting-gentry-excluded-leaves-20261025.md'),
 ('Source/history dependencies reassessed','Post-fiscal dependencies reassessed'),
 ('Version 4.37 remains 532 pages','Version 4.39 remains 534 pages'),
 ('41 verified coverage files','43 verified coverage files'),
 ('Completed source/history, population overlap, sector composition and recovery are retained.','Completed source/history, population, sector, fiscal and recovery compositions are retained.'),
 ('Next: explicit current-assessment clocks in the mixed decision timeline;','Next: inspect four excluded Gentry scan leaves using the retained archive identity;'),
 ('data/accounting-master/source-history-reassessment-20261025/result.md','data/accounting-master/post-fiscal-reassessment-20261025/result.md'),
 ('how should native tax assessments be ordered with state-dependent decisions without guessing their clock?','do excluded source-scan leaves contain the missing Gentry derivation?'),
 ('Source/history reassessment:53/6/46 IDs through41 coverage files; current-assessment timeline selected','Post-fiscal reassessment:53/6/46 IDs through43 coverage files; excluded-source scan selected'),
 ('Add explicit current-assessment timeline clock using unchanged native annual kernel','Inspect the four excluded Gentry scan leaves before current-design reconciliation')]
for a,b in changes:
    assert a in text,a
    text=text.replace(a,b)
compile(text,'refresh.py','exec');(HERE/'refresh.py').write_text(text)
