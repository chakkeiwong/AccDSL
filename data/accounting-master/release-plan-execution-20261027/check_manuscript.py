from pathlib import Path
import hashlib,json,re,fitz
from fractions import Fraction
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;b=json.loads((H/'baseline.json').read_text());S=R/b['source'];T=R/'docs/design/proposal/manuscript-release-prep-v551r1-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cites(t):
 return [v.split('}',1)[0] for v in t.split(chr(92)+'cite')[1:]]
checks=[]
def chk(k,v,detail=None):checks.append({'check':k,'pass':bool(v),'detail':detail})
base_sources=[p for p in S.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']]
changed=[]
for p in base_sources:
 q=T/p.relative_to(S);chk('preserved_file:'+str(p.relative_to(S)),q.exists())
 if q.exists() and p.read_bytes()!=q.read_bytes():changed.append(str(p.relative_to(S)))
 if p.suffix=='.tex':chk('citation_tokens:'+str(p.relative_to(S)),cites(p.read_text())==cites(q.read_text()))
chk('baseline_source_hashes',all(sha(R/p)==h for p,h in b['source_hashes'].items()))
chk('expected_changed_sources',set(changed)==set(['accounting-product-proposal.tex','simulation-foundations.tex','chapters/01-purpose.tex','simulation/family-policies.tex','simulation/observation-binding.tex','simulation/temporal-frontier.tex','chapters/10-validation.tex']),changed)
# Exact affine identity, not merely sample equality: old fixed share f=1-alpha.
old_intercept=7-2;old_slope=2;new_intercept=5;new_slope=2
chk('affine_change_of_variable',old_intercept==new_intercept and old_slope==new_slope)
for a in [Fraction(0),Fraction(1,5),Fraction(2,5),Fraction(1)]:chk('interest_case:'+str(a),7-2*(1-a)==5+2*a)
labels=[];refs=[]
for p in base_sources:
 if p.suffix!='.tex':continue
 new=(T/p.relative_to(S)).read_text()
 labels += [v.split('}',1)[0] for v in new.split(chr(92)+'label{')[1:]]
 for op in ['ref','eqref','pageref']:
  refs += [v.split('}',1)[0] for v in new.split(chr(92)+op+'{')[1:]]
duplicates={x:labels.count(x) for x in set(labels) if labels.count(x)>1}
chk('no_unexpected_cross_root_duplicate_labels',duplicates=={'sim:body-end':2},duplicates)
chk('all_reference_labels_exist',set(refs)<=set(labels),sorted(set(refs)-set(labels)))
volumes=[];renders=[]
for name in ['accounting-product-proposal','simulation-foundations']:
 pdf=T/(name+'.pdf');doc=fitz.open(pdf);old=fitz.open(S/(name+'.pdf'));log=(T/(name+'.log')).read_text();oldlog=(S/(name+'.log')).read_text()
 chk(name+':no_undefined',not re.search(r'(Citation .* undefined|Reference .* undefined|There were undefined)',log))
 def warnings(x):return [z for z in x.splitlines() if 'Overfull' in z or 'Underfull' in z]
 chk(name+':overfull_not_increased',sum('Overfull' in x for x in warnings(log))<=sum('Overfull' in x for x in warnings(oldlog)))
 pages={0}
 needles=['floating-rate fraction','saved partial-frontier extension','For this observation-binding profile','Stopped' if False else 'Stopping a search','Adapters exchange typed records','Core grammar, records','The parser/API comparison in P2 originally']
 for needle in needles:
  matched=[i for i,p in enumerate(doc) if needle in p.get_text()]
  pages.update(matched[-1:])
 for i in sorted(pages):
  out=H/'rendered'/name/f'{i+1:04d}.png';out.parent.mkdir(parents=True,exist_ok=True);doc[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out);renders.append({'volume':name,'physical_page':i+1,'printed_page':doc[i].get_label(),'image':str(out.relative_to(R)),'visual_review':'pending'})
 volumes.append({'name':name,'pages':len(doc),'previous_pages':len(old),'sha256':sha(pdf),'overfull':sum('Overfull' in x for x in warnings(log)),'underfull':sum('Underfull' in x for x in warnings(log))})
chk('simulation_requested_page_range',150<=volumes[1]['pages']<=300)
for rec in json.loads((T/'reference-map.json').read_text()):chk('reference_copy:'+rec['reference'],sha(T/rec['reference'])==rec['sha256'])
result={'checks':checks,'passed':all(c['pass'] for c in checks),'volumes':volumes,'changed_sources':changed,'rendered':renders,'limits':'Source/citation/affine/build diagnostics only; no whole-document comprehension or authority acceptance.'};(H/'manuscript-checks.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({'passed':result['passed'],'count':len(checks),'failed':[c for c in checks if not c['pass']],'volumes':volumes,'rendered':renders},indent=2))
