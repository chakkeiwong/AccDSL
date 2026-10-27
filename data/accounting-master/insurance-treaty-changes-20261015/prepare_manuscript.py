from pathlib import Path
import json,hashlib,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-bank-transfer-fees-20261015';NEW=ROOT/'docs/design/proposal/manuscript-insurance-treaty-changes-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='826f40c2499ee46525aae65f2502189c3c043a8640b75e6cde5c0e591dec2208'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.07')==1;p.write_text(s.replace('Version 3.07','Version 3.08'))
body=(ROOT/'docs/design/proposal/methods/insurance-treaty-changes-20261015.md').read_text()
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
for a,b in [('IFRS 17.62--66B keeps',r'IFRS~17.62--66B \citep[IFRS~17.62--68 and B119C--F]{eu20231803} keeps'),('Under paragraph 66(c)(i),',r'Under paragraph 66(c)(i) \citep[IFRS~17.66(c),66(bb),B119F]{eu20231803},'),("paragraph 72's tests",r"paragraph 72's tests \citep[IFRS~17.72--77]{eu20231803}"),('paragraph 44 and B96--B97',r'paragraph 44 and B96--B97 \citep[IFRS~17.44,48--52,B72,B96--97]{eu20231803}'),('paragraphs 87--90,',r'paragraphs 87--90 \citep[IFRS~17.87--91 and B128--132]{eu20231803},')]:
 assert a in tex,a;tex=tex.replace(a,b)
(NEW/'sections/insurance-treaty-changes.tex').write_text(tex)
p=NEW/'sections/insurance-methods.tex';s=p.read_text();anchor=r'\input{sections/insurance-priced-guarantee}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/insurance-treaty-changes}'))
print(json.dumps({'version':'3.08','preserved_sources':len(sources),'new_words':len(body.split())}))
