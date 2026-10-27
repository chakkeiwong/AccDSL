from pathlib import Path
import json,hashlib,shutil,subprocess,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-corporate-events-20261015';NEW=ROOT/'docs/design/proposal/manuscript-impairment-tax-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='898396c21a3fd019304ba6c204de0a341b17eb6d629586e2d549fab5a810bbc2'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.03')==1;p.write_text(s.replace('Version 3.03','Version 3.04'))
md=(ROOT/'docs/design/proposal/methods/impairment-tax-repairs-20261015.md').read_text();body=md[md.index('The following methods'):].replace('## ','### ')
body='## Impairment across a group and the origin of tax\n\n'+body
body=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',body)
body=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',body)
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
for a,b in [('IAS 36.100--102 identifies',r'IAS~36.100--102 \citep[IAS~36.100--108]{eu20231803} identifies'),('IAS 36 AppendixC distinguishes',r'IAS~36 Appendix~C \citep[IAS~36.C1--C9]{eu20231803} distinguishes'),('IAS 36.60--64 treats',r'IAS~36.60--64 \citep[IAS~36.60--64,117--124; IAS~12.61A--65]{eu20231803} treats'),('IAS 12.66 requires',r'IAS~12.66 \citep[IAS~12.39--51,66--68]{eu20231803} requires'),('Commission Regulation(EU)2023/2468',r'Commission Regulation (EU) 2023/2468 \citep[arts.~2--3; annex~4A,88A--88D,98M]{eu20232468}')]:
 assert a in tex,a;tex=tex.replace(a,b)
(NEW/'sections/impairment-tax.tex').write_text(tex)
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor=r'\input{sections/corporate-events}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/impairment-tax}'))
p=NEW/'references.bib';p.write_text(p.read_text()+r'''
@misc{eu20232468,
 author={{European Commission}}, year={2023},
 title={{Commission Regulation (EU) 2023/2468 of 8 November 2023 amending Regulation (EU) 2023/1803 as regards International Accounting Standard 12}},
 url={https://eur-lex.europa.eu/eli/reg/2023/2468/oj},
 note={Official Journal 9 November 2023; all four pages including Articles 1--3 and the annex inspected; historical adoption and application provisions}
}
''')
(OUT/'manuscript-insert.md').write_text(body)
print(json.dumps({'version':'3.04','preserved_sources':len(sources),'words':len(body.split())}))
