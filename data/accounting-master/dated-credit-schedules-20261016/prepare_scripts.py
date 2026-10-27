"""Adapt protected insertion and review utilities for B1 only."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;PRIOR=OUT.parent/'aligned-option-components-20261016'
for name in ('integrate_manuscript.py','check_manuscript.py'):
    s=(PRIOR/name).read_text().replace('aligned-option-components','dated-credit-schedules').replace('manuscript-instrument-reduction-20261016','manuscript-aligned-option-components-20261016')
    s=s.replace('Version 3.32','Version 3.33').replace('Version 3.31','Version 3.32').replace("version='3.32'","version='3.33'").replace('Version3.31','Version3.32')
    s=s.replace('len(files)==131','len(files)==132').replace('protected 131','protected 132').replace('sections/financing-components.tex','sections/bank-methods.tex')
    s=s.replace('actual/aligned option components','dated credit schedules').replace('3.32 dated credit schedules','3.33 dated credit schedules')
    s=s.replace('The actual option and the hedged price need separate','Receipts and write-offs between annual dates').replace('sector integration retain their separate requirements','wider bank-company joins remain open')
    if name=='integrate_manuscript.py':
        a=s.index('    anchor=');b=s.index('    shutil.copy2',a)
        s=s[:a]+r"    anchor=r'\input{sections/bank-poci-rollforward}'"+'\n'+"    assert text.count(anchor)==1\n"+r"    p.write_text(text.replace(anchor, anchor+'\n'+r'\input{sections/dated-credit-schedules}'+'\n'))"+'\n'+s[b:]
    (OUT/name).write_text(s)
s=(PRIOR/'closeout.py').read_text().replace("PRIOR=ROOT/'data/accounting-master/instrument-reduction-20261016'","PRIOR=ROOT/'data/accounting-master/aligned-option-components-20261016'")
s=s.replace("'3.32'","'3.33'").replace('accounting-aligned-option-components-20261016.md','accounting-dated-credit-schedules-20261016.md').replace('actual/aligned option components','dated credit schedules')
s=s.replace('Actual/hypothetical option components and complete inventory/cash consequences','Dated interest, cash, fees and earlier financial write-offs with explicit numerical bounds')
s=s.replace("'MC13','MC16'","'MC13','MC15','MC16'").replace("'MC19','MC24'","'MC19','MC21','MC24'")
a=s.index('    delta=');b=s.index('\n    for row',a)
s=s[:a]+"    delta='PerformingEIRSchedule/1 and POCIDatedSchedule/1 preserve dated expected/actual cash, integral fees, signed allowance, original-rate PV bounds and earlier full/partial write-offs. Nine paths,32 factor certificates and5 root brackets are checked. Exact initial-PV admission, supplied forecasts and remaining bank joins remain explicit.'"+s[b:]
(OUT/'closeout.py').write_text(s)
print('Prepared protected integration/checker/closeout for Version3.33')
