from pathlib import Path
from collections import Counter
import re,json,hashlib,fitz,sys,time,platform
D=Path(__file__).resolve().parent;R=D.parents[3];baseline=json.loads((D/'baseline.json').read_text());B=R/baseline['source'];T=R/baseline['candidate'];checks=[];changes=[];clock=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,x,d=None):checks.append({'check':n,'pass':bool(x),'detail':d})
for row in baseline['inputs']:
 p=B/row['path'];ck('baseline:'+row['path'],sha(p)==row['sha256'])
 if p.suffix!='.pdf' and sha(T/row['path'])!=row['sha256']:changes.append(row['path'])
ck('intended_changes',set(changes)=={'README.md','accounting-product-proposal.tex','simulation-foundations.tex','simulation/lit-09-approximation-4.tex'},changes)
bs=chr(92);pat=re.compile(re.escape(bs)+'cite[a-zA-Z]*[*]?'+'(?:'+re.escape('[')+'[^]]*'+re.escape(']')+')*'+re.escape('{')+'([^}]+)'+re.escape('}'));before=Counter();after=Counter()
for row in baseline['inputs']:
 if Path(row['path']).suffix=='.tex':before.update(pat.findall((B/row['path']).read_text()));after.update(pat.findall((T/row['path']).read_text()))
ck('citation_tokens_preserved',before==after,{'before':sum(before.values()),'after':sum(after.values())});ck('nonempty_complete_citation_inventory',sum(before.values())>500);ck('bibliography_preserved',sha(B/'references.bib')==sha(T/'references.bib'))
p='simulation/lit-09-approximation-4.tex';old=(B/p).read_text();new=(T/p).read_text()
for label in ['sim:lit-threshold','sim:lit-finite-coupling','sim:lit-finite-cost']:
 ck('old_equation_label:'+label,new.count(bs+'label{'+label+'}')==1)
for text in ['12'+bs+'{1-(19/20)^3'+bs+'}=3423/2000','4433/8000','all 64 policies']:
 ck('original_numeric_example:'+text,text in old and text in new)
ck('original_prefix_unchanged',new[:new.index('A stronger but')]==old[:old.index('A stronger but')])
ck('original_suffix_unchanged',new[new.index('For finite kernels with common outcome labels'):]==old[old.index('For finite kernels with common outcome labels'):])
vol=[]
for name in ['accounting-product-proposal','simulation-foundations']:
 doc=fitz.open(T/(name+'.pdf'));log=(T/(name+'.log')).read_text(errors='replace');ck('build_log:'+name,'undefined' not in log and 'Overfull' not in log);ck('version:'+name,'5.52-R2' in doc[0].get_text());vol.append({'name':name,'pages':len(doc),'sha256':sha(T/(name+'.pdf'))})
render=json.loads((D/'after-pages.json').read_text());reviews=[]
for x in render:reviews.append({'volume':x['volume'],'physical_page':x['physical_page'],'pdf_sha256':sha(T/(x['volume']+'.pdf')),'path':x['path'],'status':'bounded_author_visual_inspection_pass','finding':'Conditions, recurrence, new loss bounds, original example and following limitations are readable; no clipping or broken equation/reference observed.'})
(D/'rendered-review.json').write_text(json.dumps({'before_pages':[79,80,81,82],'before_pdf_sha256':sha(B/'simulation-foundations.pdf'),'after_pages':reviews,'scope':'Four original standalone pages and six resulting main/standalone pages actually viewed; no whole-document or independent-reader acceptance.'},indent=2)+chr(10))
result={'pass':all(x['pass'] for x in checks),'checks':checks,'changed_files':changes,'volumes':vol,'command':[sys.executable,str(Path(__file__).resolve())],'seconds':time.monotonic()-clock,'environment':sys.version,'plan':str((D/'plan.md').relative_to(R)),'limits':'Bounded source and local mathematical correction; full release acceptance remains open.'};(D/'verification.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({'pass':result['pass'],'checks':len(checks),'failures':[x for x in checks if not x['pass']],'volumes':vol}));raise SystemExit(0 if result['pass'] else 1)
