from pathlib import Path
import json,hashlib,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-awards-participation-20261015';NEW=ROOT/'docs/design/proposal/manuscript-bank-transfer-fees-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='2fec624bc40c3ffcdeb41e62d451a5c171fd5e9715aa585b19b73141cc28294e'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.06')==1;p.write_text(s.replace('Version 3.06','Version 3.07'))
body=(ROOT/'docs/design/proposal/methods/bank-transfer-fees-20261015.md').read_text()
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
for a,b in [('AASB9.5.5.6 and B5.5.47',r'AASB~9.5.5.6 and B5.5.47 \citep[5.5.6 and B5.5.47]{aasb9dated}'),('AASB7.B8E presents',r'AASB~7.B8E \citep[B8E]{aasb7dated} presents'),('Under AASB9.5.5.20 and B5.5.39--40,',r'Under AASB~9.5.5.20 and B5.5.39--40 \citep[5.5.20 and B5.5.39--40]{aasb9dated},'),('Under AASB9.B5.4.1--4,',r'Under AASB~9.B5.4.1--4 \citep[B5.4.1--4]{aasb9dated},'),('AASB9.3.2.2 first decides',r'AASB~9.3.2.2 \citep[3.2.2--3.2.23]{aasb9dated} first decides'),('B3.2.13(a):',r'B3.2.13(a) \citep[B3.2.13(a)]{aasb9dated}:')]:
 assert a in tex,a;tex=tex.replace(a,b)
(NEW/'sections/bank-transfer-fees.tex').write_text(tex)
p=NEW/'sections/bank-methods.tex';s=p.read_text();anchor=r'\input{sections/bank-restructuring}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/bank-transfer-fees}'))
print(json.dumps({'version':'3.07','preserved_sources':len(sources),'new_words':len(body.split())}))
