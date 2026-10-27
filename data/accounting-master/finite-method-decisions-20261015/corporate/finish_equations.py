from pathlib import Path
import shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
p=ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015/sections/corporate-residuals.tex'
s=p.read_text();archive=OUT/'second-presentation';assert not archive.exists();archive.mkdir()
for f in [p,OUT/'build-run.json',OUT/'build-stdout.log']:shutil.copy2(f,archive/f.name)
replacements=[
('New total construction cost 100 makes cumulative progress 40\%, so target construction revenue 56 yields catch-up 6.',r'''New total construction cost 100 makes cumulative progress 40\%. The amended construction allocation gives
\[\text{cumulative revenue}=140\frac{40}{100}=56,\qquad\text{catch-up}=56-50=6.\]
This corrects only the construction promise.'''),
('Material rate 10 plus variable 5 plus fixed 5 gives completed unit cost 20.',r'''The material denominator is 100 units, while conversion uses only 90 equivalent units:
\[80+20\left(\frac12\right)=90,\qquad\text{completed unit cost}=10+5+5=20.\]
Separate denominators keep missing conversion work out of inventory cost.'''),
('Operating cash movement − 770 is 350+105+0+40 − 62 profits, plus depreciation 60, less inventory increase 1375, plus supplier increase 110, plus noncash unwind 2.',r'''The same cash movement follows from the indirect reconciliation:
\[433+60-1375+110+2=-770.\]
Starting from pretax profit 433, add depreciation 60, deduct inventory growth 1375, add the supplier liability increase 110 and add noncash restoration interest 2.''')]
for old,new in replacements:
    assert s.count(old)==1,old
    s=s.replace(old,new)
p.write_text(s)
print('display_count',s.count('\\['))
