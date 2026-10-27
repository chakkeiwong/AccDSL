from pathlib import Path
import json,hashlib,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-financing-components-20261015';NEW=ROOT/'docs/design/proposal/manuscript-awards-participation-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='4fe5f9c2d878aad0f848d63e31cdba799fcea111717dac6e21dad0d0c062153e'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.05')==1;p.write_text(s.replace('Version 3.05','Version 3.06'))
body=(ROOT/'docs/design/proposal/methods/awards-participation-20261015.md').read_text()
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
for a,b in [('IFRS 2.10--21 measures',r'IFRS~2.10--21 \citep[IFRS~2.10--23]{eu20231803} measures'),('Paragraphs 27--28 preserve',r'Paragraphs 27--28 \citep[IFRS~2.27--28A]{eu20231803} preserve'),('IFRS 2.30--33D requires',r'IFRS~2.30--33D \citep[IFRS~2.30--33D]{eu20231803} requires'),('paragraphs 35--40 treat',r'paragraphs 35--40 \citep[IFRS~2.35--43]{eu20231803} treat'),('IAS 33.A13--A14 allocates',r'IAS~33.A13--A14 \citep[IAS~33.A13--A16]{eu20231803} allocates'),('Under paragraphs 47A--48,',r'Under paragraphs 47A--48 \citep[IAS~33.47A--60]{eu20231803},')]:
 assert a in tex,a;tex=tex.replace(a,b)
(NEW/'sections/awards-participation.tex').write_text(tex)
p=NEW/'chapters/14-financing-groups.tex';s=p.read_text();anchor=r'\input{sections/financing-components}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/awards-participation}'))
print(json.dumps({'version':'3.06','preserved_sources':len(sources),'new_words':len(body.split())}))
