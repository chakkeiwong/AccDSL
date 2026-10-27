"""Prepare successor scripts with exact checked insertion points."""
from pathlib import Path

OUT=Path(__file__).resolve().parent
PRIOR=OUT.parent/'instrument-reduction-20261016'
for name in ('integrate_manuscript.py','check_manuscript.py'):
    s=(PRIOR/name).read_text().replace('instrument-reduction','aligned-option-components').replace('manuscript-dependent-eps-20261016','manuscript-instrument-reduction-20261016')
    s=s.replace('Version 3.31','Version 3.32').replace('Version 3.30','Version 3.31').replace("version='3.31'","version='3.32'").replace('Version3.30','Version3.31')
    s=s.replace('len(files)==130','len(files)==131').replace('protected 130','protected 131').replace('sections/added-instruments.tex','sections/financing-components.tex')
    s=s.replace('instrument-only heterogeneous reductions','actual/aligned option components').replace('3.31 actual/aligned option components','3.32 actual/aligned option components')
    s=s.replace('Reducing an instrument preserves the purchase','The actual option and the hedged price need separate').replace('heterogeneous discontinued purchases require','sector integration retain their separate requirements')
    if name=='integrate_manuscript.py':
        lines=s.splitlines();i=next(i for i,line in enumerate(lines) if 'p.write_text(text+' in line)
        lines[i:i+1]=[r"    anchor=r'\hypertarget{forward-elements-and-currency-basis-spreads}'",'    assert text.count(anchor)==1',r"    p.write_text(text.replace(anchor, '\n'+r'\input{sections/aligned-option-components}'+'\n'+anchor))"]
        s='\n'.join(lines)+'\n'
    (OUT/name).write_text(s)
s=(PRIOR/'closeout.py').read_text().replace("PRIOR=ROOT/'data/accounting-master/dependent-eps-20261016'","PRIOR=ROOT/'data/accounting-master/instrument-reduction-20261016'")
s=s.replace("'3.31'","'3.32'").replace('accounting-instrument-reduction-20261016.md','accounting-aligned-option-components-20261016.md')
s=s.replace('instrument-only heterogeneous reductions','actual/aligned option components').replace('Instrument-only reduction with heterogeneous component histories and gross settlement','Actual/hypothetical option components and complete inventory/cash consequences')
a=s.index('    delta=');b=s.index('\n    for row',a)
s=s[:a]+"    delta='AlignedOptionComponents/1 binds separate actual/hypothetical strikes and component values through intrinsic/time reserves, mismatch profit and gross settlement/inventory basis. Six paths and18 observations preserve a balanced-but-wrong-target counterexample. Pricing, qualification and general signed-component methods remain distinct.'"+s[b:]
(OUT/'closeout.py').write_text(s)
print('Prepared integration, checker and closeout.')
