"""Create protected Version 3.01, with no changes to prior candidates."""
from pathlib import Path
import json,hashlib,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
base=json.loads((OUT/'baseline.json').read_text());OLD=ROOT/base['candidate']
NEW=ROOT/'docs/design/proposal/manuscript-future-validation-20261015'
assert not NEW.exists()
assert json.loads((OUT/'protocol-checks.json').read_text())['passed']
assert hashlib.sha256((OLD/'accounting-product-proposal.pdf').read_bytes()).hexdigest()==base['pdf_sha256']
for x in base['source_files']:
 p=OLD/x['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 q=NEW/x['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
p=NEW/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.00')==1;p.write_text(s.replace('Version 3.00','Version 3.01'))
md=(ROOT/'docs/design/proposal/methods/future-validation-20261015.md').read_text()
body=md[md.index('These protocols'):].replace('## ','### ')
body=body.replace('These protocols extend Q5 without selecting a trained model, implementation or\nforecasting default.','The following protocols specify the comparisons needed before selecting a forecasting method.')
body=body.replace('Q3:', 'the normal model in the conditional-inference discussion:').replace('The Q4 causal example','The earlier causal example')
tex=subprocess.check_output(['pandoc','--from=markdown','--to=latex','--wrap=none'],input=body,text=True)
tex=tex.replace('Gneiting and Raftery (2007),',r'Gneiting and Raftery \citep[sec.~4.2, eqs.~20--21]{gneiting2007proper},')
tex=tex.replace('The first question is what a successful prediction would\nmean.', 'The first question is what a successful prediction would mean.')
tex=r'\section{Fixing the target before evaluating a method}'+'\n'+r'\label{sec:future-validation-targets}'+'\n\n'+tex
(NEW/'sections/future-validation.tex').write_text(tex)
p=NEW/'chapters/10-validation.tex';s=p.read_text();anchor=r'\section{Capability contracts for sector packages}';assert s.count(anchor)==1
p.write_text(s.replace(anchor,r'\input{sections/future-validation}'+'\n\n'+anchor))
p=NEW/'references.bib';p.write_text(p.read_text()+r'''
@article{gneiting2007proper,
 author={Gneiting, Tilmann and Raftery, Adrian E.},
 title={Strictly Proper Scoring Rules, Prediction, and Estimation},
 journal={Journal of the American Statistical Association},
 year={2007}, volume={102}, number={477}, pages={359--378},
 doi={10.1198/016214506000001437},
 note={Selected definitions, moment conditions, kernel argument and evaluation examples inspected; external theorem dependencies not independently re-proved}
}
''')
(OUT/'manuscript-preparation.json').write_text(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'baseline':base['candidate'],'preserved_sources':len(base['source_files']),'intended_changed':['accounting-product-proposal.tex','chapters/10-validation.tex','references.bib'],'intended_added':['sections/future-validation.tex'],'body_words':len(body.split())},indent=2)+'\n')
print(json.dumps({'candidate':str(NEW.relative_to(ROOT)),'body_words':len(body.split())}))
