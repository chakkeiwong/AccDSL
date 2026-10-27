from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
assert not (HERE/'refresh.py').exists()
text=(ROOT/'data/accounting-master/simulator-post-sector-reassessment-20261025/refresh.py').read_text()
for a,b in [
 ('docs/plans/accounting-retained-source-history-20261025.md','docs/plans/accounting-assessment-timeline-20261025.md'),
 ('Post-sector dependencies reassessed','Source/history dependencies reassessed'),
 ('Version 4.32 remains 528 pages','Version 4.37 remains 532 pages'),
 ('36 verified coverage files','41 verified coverage files'),
 ('Completed indirect reporting,\nsector composition and annual inventory recovery are retained.','Completed source/history, population overlap, sector composition and recovery are retained.'),
 ('Next: explicit retained-source binding to supplied conditional histories;','Next: explicit current-assessment clocks in the mixed decision timeline;'),
 ('data/accounting-master/simulator-post-sector-reassessment-20261025/result.md','data/accounting-master/source-history-reassessment-20261025/result.md'),
 ('how do retained source measurements constrain explicit histories without admitting unknown company facts?','how should native tax assessments be ordered with state-dependent decisions without guessing their clock?'),
 ('Post-sector reassessment:53/6/46 IDs through36 coverage files; retained-source/history binding selected','Source/history reassessment:53/6/46 IDs through41 coverage files; current-assessment timeline selected'),
 ('Bind retained source measurements to explicit conditional histories without actual-history admission','Add explicit current-assessment timeline clock using unchanged native annual kernel')]:
    assert a in text,a;text=text.replace(a,b)
(HERE/'refresh.py').write_text(text)
