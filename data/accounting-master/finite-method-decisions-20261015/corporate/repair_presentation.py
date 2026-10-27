"""Repair observed numeric run-ons in Markdown, before LaTeX conversion."""
from pathlib import Path
import re,shutil,subprocess,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
NEW=ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015'
archive=OUT/'initial-presentation';assert not archive.exists();archive.mkdir()
for p in [OUT/'manuscript-insert.md',NEW/'sections/corporate-residuals.tex',OUT/'build-run.json',OUT/'build-stdout.log']:
    shutil.copy2(p,archive/p.name)
p=OUT/'manuscript-insert.md';s=p.read_text()
s=re.sub(r'(?<=[A-Za-z])(?=[0-9])',' ',s)
s=re.sub(r'(?<=[0-9])(?=[A-Za-z])',' ',s)
s=re.sub(r'\s*([→×−])\s*',r' \1 ',s)
s=s.replace('Expected cost is 100 × (0+2+2)=400.',
 'The population estimate weights each possible repair cost and then sums across the covered products:\n\n'
 '$$100\\left(\\frac34\\,0+\\frac15\\,10+\\frac1{20}\\,40\\right)=400.$$\n\n'
 'A low claim probability for one product therefore does not eliminate the population obligation.')
s=s.replace('New total construction cost 100 makes cumulative progress 40%, so target construction revenue 56 yields catch-up 6.',
 'New total construction cost 100 makes cumulative progress 40%. The amended construction allocation therefore gives\n\n'
 '$$\\text{cumulative revenue}=140\\frac{40}{100}=56,\\qquad'
 '\\text{catch-up}=56-50=6.$$\n\n'
 'This corrects only the construction promise.')
s=s.replace('Material rate 10 plus variable 5 plus fixed 5 gives completed unit cost 20.',
 'The unfinished units have all their material but only half their conversion. Consequently,\n\n'
 '$$\\begin{aligned}\\text{material units}&=80+20=100,\\\\'
 '\\text{conversion equivalents}&=80+20\\left(\\frac12\\right)=90,\\\\'
 '\\text{completed unit cost}&=10+5+5=20.\\end{aligned}$$\n\n'
 'Separate denominators keep missing conversion work out of inventory cost.')
s=s.replace('give 42. Taxable profit 58 and tax base 58 give current 14.5 and DTL 5.5.',
 'give an expected deduction of\n\n'
 '$$\\frac15(100)+\\frac3{10}(40)+\\frac12(20)=42.$$\n\n'
 'Taxable profit and the remaining tax base are both 58. Current tax is '
 '$58(25\\%)=14.5$, while the taxable temporary difference is $80-58=22$, '
 'giving a deferred tax liability of $22(25\\%)=5.5$.')
s=s.replace('Operating cash movement − 770 is 350+105+0+40 − 62 profits, plus depreciation 60, less inventory increase 1375, plus supplier increase 110, plus noncash unwind 2.',
 'The same cash movement follows from the indirect reconciliation:\n\n'
 '$$433+60-1375+110+2=-770.$$\n\n'
 'Starting from pretax profit 433, add depreciation 60, deduct inventory growth '
 '1375, add the supplier liability increase 110 and add noncash restoration interest 2.')
p.write_text(s)
tex=subprocess.check_output(['pandoc','--from=markdown','--to=latex','--wrap=none'],input=s,text=True)
tex=tex.replace('IFRIC 1.2',r'IFRIC~1.2 \citep[IFRIC~1.1--8]{eu20231803}')
tex=tex.replace('AASB 137.14/24',r'AASB~137.14/24 \citep[paras.~14,24,36--62]{aasb137dated}')
tex=tex.replace('AASB 15.21(c)',r'AASB~15.21(c) \citep[paras.~18--21,39--45,73--90]{aasb15dated}')
tex=tex.replace('IAS 2 prescribes',r'IAS~2 \citep[IAS~2.12--18]{eu20231803} prescribes')
tex=tex.replace('EU IFRIC 23.6–14',r'EU IFRIC~23.6--14 \citep[IFRIC~23.6--14,A1--A5]{eu20231803}')
(NEW/'sections/corporate-residuals.tex').write_text(tex)
print(json.dumps({'preserved_initial_presentation':str(archive.relative_to(ROOT)),'displays':tex.count('\\[')}))
