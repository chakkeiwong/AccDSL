"""Create Version3.00 from the protected2.99 source tree, once."""
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
OLD=ROOT/'docs/design/proposal/manuscript-group-bindings-20261015'
NEW=ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'accounting-product-proposal.pdf')=='393f4cf191a44ac8e671248a6c10562674d5c5a03a3a42e4f60c30b8c10e70e8'
assert json.loads((OUT/'independent-checks.json').read_text())['passed']
assert json.loads((OUT/'uncertain-tax-cases.json').read_text())['passed']
assert not NEW.exists()
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
    dest=NEW/p.relative_to(OLD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),
 'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),
 'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.99','Version 3.00'))
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor='\\input{sections/production-cost}\n';assert s.count(anchor)==1
addition='\n\\input{sections/corporate-residuals}\n'
p.write_text(s.replace(anchor,anchor+addition))
md=(ROOT/'docs/design/proposal/methods/corporate-residuals-20261015.md').read_text()
body='## Changed obligations and unfinished production {#sec:corporate-residuals}\n\n'
body+='A company can change its restoration estimate before a machine wears out, promise to repair sold products, or end a period with unfinished goods. Each condition changes a different part of its accounts. The following cases extend the preceding operating methods through those transitions. They retain exact illustrative amounts and separate economic evidence from bookkeeping.\n\n'
body+='Restoration, production and uncertain-tax methods use the retained historical EU text; assurance and mixed contracts use the inspected AASB compilations for synthetic 2024/2025 Australian for-profit reporters. The AASB 137 PDF covers annual periods beginning from 1 January 2023 to before 1 July 2026; its website gives a different end-period summary. Both admit these particular historical calendar years. A real application still needs its own source and period admission. Amounts are pretax unless an explicit tax calculation follows.\n\n'
body+=md[md.index('## Restoration estimates'):md.index('## Combined closing')]
body+='## Combining the new operating contributions\n\n'+md[md.index('Combine only the five'):md.index('The residual disposition file')]
body=body.replace('## ','### ')
body=body.replace('### Changed obligations','## Changed obligations',1)
for a,b in [('RestorationState','The restoration record'),('AssuranceState','The assurance record'),('ModificationState','The modification record'),('ProductionState','The production record'),('JointProductionState','The joint-production record'),('SupplierFinanceState','The supplier record'),('UncertainTaxState','The uncertain-tax record')]:body=body.replace(a,b)
tex=subprocess.check_output(['pandoc','--from=markdown','--to=latex','--wrap=none'],input=body,text=True)
tex=tex.replace('IFRIC1.2',r'IFRIC~1.2 \citep[IFRIC~1.1--8]{eu20231803}')
tex=tex.replace('AASB137.14/24',r'AASB~137.14/24 \citep[paras.~14,24,36--62]{aasb137dated}')
tex=tex.replace('AASB15.21(c)',r'AASB~15.21(c) \citep[paras.~18--21,39--45,73--90]{aasb15dated}')
tex=tex.replace('IAS2 prescribes',r'IAS~2 \citep[IAS~2.12--18]{eu20231803} prescribes')
tex=tex.replace('EU IFRIC23.6–14',r'EU IFRIC~23.6--14 \citep[IFRIC~23.6--14,A1--A5]{eu20231803}')
(NEW/'sections/corporate-residuals.tex').write_text(tex)
bib=NEW/'references.bib'
bib.write_text(bib.read_text()+r'''
@misc{aasb137dated,
 author={{Australian Accounting Standards Board}}, year={2022},
 title={{AASB 137 Provisions, Contingent Liabilities and Contingent Assets, compilation 5, 31 December 2022}},
 url={https://www.aasb.gov.au/admin/file/content105/c9/AASB137_08-15_COMPdec22_01-23.pdf},
 note={Registration F2023C00419, 8 May 2023; selected recognition, measurement, reimbursement and remeasurement provisions; historical source}
}
''')
(OUT/'manuscript-insert.md').write_text(body)
print(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'protected_source_files':len(sources),'new_section_words':len(body.split())}))
