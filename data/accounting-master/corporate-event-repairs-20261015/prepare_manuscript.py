from pathlib import Path
import hashlib,json,subprocess,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-selected-reuse-20261015';NEW=ROOT/'docs/design/proposal/manuscript-corporate-events-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='44e8f20419cb8e4089cf3416ed9ea54a693dcb24a0d58b8b4e57efc1065fd559'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.02')==1;p.write_text(s.replace('Version 3.02','Version 3.03'))
md=(ROOT/'docs/design/proposal/methods/corporate-event-repairs-20261015.md').read_text();body=md[md.index('## Replacing'):].replace('## ','### ')
intro='## Inspections, surrendered rights and changed employee benefits\n\nA replacement inspection, a smaller leased area and a pension curtailment all remove something from an existing arrangement, but they remove different economic rights or obligations. The accounting must identify what survives before measuring the new arrangement. The following methods use the retained historical EU text and synthetic pretax amounts. Actual authority, contract and actuarial facts remain necessary for application.\n\n'
body=intro+body
reps={'IAS16.14':r'IAS 16.14','IAS16.43–55':'IAS 16.43–55','IFRS16.44':'IFRS 16.44','IAS19.99':'IAS 19.99','IAS19.32–36':'IAS 19.32–36','IFRS16.38(b)':'IFRS 16.38(b)','IAS16.12':'IAS 16.12','IAS16':'IAS 16','IFRS16':'IFRS 16','IAS19':'IAS 19','IAS37':'IAS 37','IFRIC14':'IFRIC 14'}
for a,b in reps.items():body=body.replace(a,b)
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
for a,b in [(r'IAS 16.14 distinguishes',r'IAS~16.14 \citep[IAS~16.12--14,43--55]{eu20231803} distinguishes'),(r'IFRS 16.44 first',r'IFRS~16.44 \citep[IFRS~16.38--46]{eu20231803} first'),(r'IAS 19.99 requires',r'IAS~19.99 \citep[IAS~19.99--112,120--126]{eu20231803} requires'),(r'IAS 19.32--36 requires',r'IAS~19.32--36 \citep[IAS~19.32--41]{eu20231803} requires')]:
 assert a in tex,a;tex=tex.replace(a,b)
(NEW/'sections/corporate-events.tex').write_text(tex)
p=NEW/'sections/corporate-methods.tex';s=p.read_text();anchor=r'\input{sections/corporate-residuals}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/corporate-events}'))
(OUT/'manuscript-insert.md').write_text(body)
print(json.dumps({'version':'3.03','source_files_preserved':len(sources),'new_words':len(body.split())}))
