from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
base=json.loads((OUT/'baseline.json').read_text());OLD=ROOT/base['candidate'];NEW=ROOT/'docs/design/proposal/manuscript-selected-reuse-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert sha(OLD/'accounting-product-proposal.pdf')==base['pdf_sha256'];assert json.loads((OUT/'checks.json').read_text())['passed']
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':base['pdf_sha256'],'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.01')==1;p.write_text(s.replace('Version 3.01','Version 3.02'))
md=(OUT/'manuscript-insert.md').read_text();tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=md,text=True)
tex=tex.replace('The first optional importer uses the retained Arelle source',r'The first optional importer uses the retained Arelle source \citep{arellepinned2026}')
(NEW/'sections/selected-reuse.tex').write_text(tex)
p=NEW/'sections/adapter-methods.tex';p.write_text(p.read_text()+'\n'+r'\input{sections/selected-reuse}'+'\n')
print(json.dumps({'version':'3.02','protected_sources':len(sources),'new_words':len(md.split())}))
