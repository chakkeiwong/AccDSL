from pathlib import Path
import json,hashlib,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
OLD=ROOT/'docs/design/proposal/manuscript-impairment-tax-20261015';NEW=ROOT/'docs/design/proposal/manuscript-financing-components-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not NEW.exists();assert json.loads((OUT/'cases.json').read_text())['passed']
assert sha(OLD/'accounting-product-proposal.pdf')=='a1910d7e5a6034b37529bf2bb0f795cb52f17f385b3beaeee09b3c621f901af9'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
(OUT/'manuscript-baseline.json').write_text(json.dumps({'baseline':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources]},indent=2)+'\n')
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.04')==1;p.write_text(s.replace('Version 3.04','Version 3.05'))
body=(ROOT/'docs/design/proposal/methods/financing-components-20261015.md').read_text()
body=body[:body.index('15 October 2026.')]+body[body.index('## The option'):]
tex=subprocess.check_output(['pandoc','-f','markdown','-t','latex','--wrap=none'],input=body,text=True)
tex=tex.replace('AASB9.6.5.15 separates',r'AASB~9.6.5.15 \citep[6.5.15 and B6.5.29--33]{aasb9dated} separates')
tex=tex.replace('Under B6.5.33(a)',r'Under B6.5.33(a) \citep[B6.5.32--33]{aasb9dated}')
tex=tex.replace('AASB9.6.5.16 permits',r'AASB~9.6.5.16 \citep[6.5.16 and B6.5.34--39]{aasb9dated} permits')
tex=tex.replace('Under 6.5.5--6.5.6 and B6.5.7--21,',r'Under 6.5.5--6.5.6 and B6.5.7--21 \citep[6.5.5--6.5.6 and B6.5.7--21]{aasb9dated},')
intro='The following conditional methods use the retained AASB~9 compilation for calendar-2024/2025 Australian for-profit Tier~1 illustrations, without optional later amendments. Actual authority admission and component valuation remain separate requirements.\n\n'
i=tex.index(r'\hypertarget{the-option');tex=tex[:i]+intro+tex[i:]
(NEW/'sections/financing-components.tex').write_text(tex)
p=NEW/'chapters/14-financing-groups.tex';s=p.read_text();anchor=r'\input{sections/financing-changes}';assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+'\n\n'+r'\input{sections/financing-components}'))
print(json.dumps({'version':'3.05','preserved_sources':len(sources),'new_words':len(body.split())}))
