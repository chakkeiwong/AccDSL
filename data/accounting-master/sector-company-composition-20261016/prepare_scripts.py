from pathlib import Path
import re
OUT=Path(__file__).resolve().parent
PRIOR=OUT.parent/'insurance-retrospective-measurement-20261016'
for name in ('integrate_manuscript.py','check_manuscript.py'):
    s=(PRIOR/name).read_text()
    s=s.replace('insurance-retrospective-measurement','sector-company-composition').replace('manuscript-insurance-service-finance-origins-20261016','manuscript-insurance-retrospective-measurement-20261016')
    s=s.replace('Version 3.35','Version 3.36').replace('Version 3.34','Version 3.35').replace('Version3.34','Version3.35').replace("version='3.35'","version='3.36'")
    s=s.replace('len(files)==134','len(files)==135').replace('protected 134','protected 135').replace('sections/insurance-methods.tex','sections/company-composition.tex')
    s=s.replace('insurance retrospective measurement','sector company composition').replace('3.35 sector company','3.36 sector company')
    s=s.replace('Reconstructing the margin from cash and service history','A bank and insurer share a group close').replace('without treating the unresolved methods as complete','nonlinear insurance valuation still require their own methods')
    if name=='integrate_manuscript.py':
        a=s.index('    anchor=');b=s.index('    shutil.copy2',a)
        s=s[:a]+"    p.write_text(text+'\\n'+r'\\input{sections/sector-company-composition}'+'\\n')\n"+s[b:]
    (OUT/name).write_text(s)
s=(PRIOR/'closeout.py').read_text().replace("PRIOR=ROOT/'data/accounting-master/insurance-service-finance-origins-20261016'","PRIOR=ROOT/'data/accounting-master/insurance-retrospective-measurement-20261016'")
s=s.replace("'3.35'","'3.36'").replace('accounting-insurance-retrospective-measurement-20261016.md','accounting-sector-company-composition-20261016.md').replace('insurance retrospective measurement','sector company composition')
s=s.replace('Full and modified transition measurements with acquisition and reinsurance origins','Shared bank, insurer and external guarantee legal/group close with tax, FX and changing ownership')
a=s.index('    affected=');b=s.index('\n    evidence=',a)
s=s[:a]+"    affected={'MC02','MC04','MC05','MC06','MC11','MC13','MC15','MC16','MC17','MC19','MC20','MC21','MC22','MC24','MC25','MC26','MC27','MC28','MC30','MC32','MC33','MC34','MC35','G2','G4','G5','G7','G12','G13','G17','G18'}"+s[b:]
a=s.index('    delta=');b=s.index('\n    for row',a)
s=s[:a]+"    delta='SectorCompany/1 joins unchanged bank/insurer component deltas to shared legal books, separate tax, external guarantee, matched deposit elimination, FX and retained-control ownership. Three cases,77 adverse inputs and20 protected-input challenges pass427 checks. Actual rights, prudential capital, wider tax and nonlinear valuations remain open.'"+s[b:]
(OUT/'closeout.py').write_text(s)
# Prose spacing is authored directly; never rewrite citation keys by regex.
print('Prepared Version3.36 integration/checker/closeout')
