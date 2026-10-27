from pathlib import Path
from collections import Counter
import re,json,hashlib,fitz,sys,time,platform,difflib
D=Path(__file__).resolve().parent;R=D.parents[3];base=json.loads((D/'baseline.json').read_text());B=R/base['baseline'];T=R/base['candidate'];checks=[];changes=[];start=time.monotonic()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,x,d=None):checks.append({'check':n,'pass':bool(x),'detail':d})
allowed={'README.md','accounting-product-proposal.tex','simulation-foundations.tex','references.bib','simulation/01-observations.tex','simulation/03-learning.tex','simulation/04-scenarios.tex','simulation/06-equity.tex','simulation/lit-09-approximation-4.tex'}
for row in base['files']:
 p=B/row['path'];ck('baseline:'+row['path'],sha(p)==row['sha256'])
 if p.suffix!='.pdf' and sha(T/row['path'])!=row['sha256']:changes.append(row['path'])
ck('intended_changes',set(changes)==allowed,changes)
bs=chr(92);pat=re.compile(re.escape(bs)+'cite[a-zA-Z]*[*]?(?:'+re.escape('[')+'[^]]*'+re.escape(']')+')*'+re.escape('{')+'([^}]+)'+re.escape('}'));before=Counter();after=Counter();beforelabels=Counter();afterlabels=Counter()
for row in base['files']:
 if Path(row['path']).suffix=='.tex':
  x=(B/row['path']).read_text();y=(T/row['path']).read_text();before.update(pat.findall(x));after.update(pat.findall(y));beforelabels.update(re.findall(r'\\label\{([^}]+)\}',x));afterlabels.update(re.findall(r'\\label\{([^}]+)\}',y))
ck('all_citation_tokens_preserved',before==after,{'before':sum(before.values()),'after':sum(after.values())});ck('nonempty_citation_inventory',sum(before.values())>500)
ck('all_existing_labels_preserved',not(beforelabels-afterlabels));ck('new_coupling_labels',set(afterlabels-beforelabels)=={'sim:lit-initial-coupling','sim:lit-matched-loss'})
cp='simulation/lit-09-approximation-4.tex';ck('exact_reviewed_coupling_import',sha(T/cp)==base['coupling_sha256'])
for name in ['01-observations','03-learning','06-equity']:
 x=(B/f'simulation/{name}.tex').read_text();y=(T/f'simulation/{name}.tex').read_text();pattern=r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
 ck('display_equations_unchanged:'+name,re.findall(pattern,x,re.S)==re.findall(pattern,y,re.S) and [m.group() for m in re.finditer(pattern,x,re.S)]==[m.group() for m in re.finditer(pattern,y,re.S)])
x=(B/'references.bib').read_text();y=(T/'references.bib').read_text();pattern=r'@misc\{litcloseestimation,.*?\n\}\n';ck('only_inspected_bibliography_entry_changes',re.sub(pattern,'ENTRY',x,flags=re.S)==re.sub(pattern,'ENTRY',y,flags=re.S));ck('version_pinned','eprint={2002.07261v2}' in y)
ck('admissible_domain','(h,s,\\pi)\\in\\mathcal A' in (T/'simulation/04-scenarios.tex').read_text());ck('distress_retained','Admissibility does not mean' in (T/'simulation/04-scenarios.tex').read_text())
for f in ['domain-check.json','eps-sign-check.json']:ck(f,json.loads((D/f).read_text())['passed'])
vol=[];render=[];out=D/'rendered';out.mkdir(exist_ok=True)
needles={'accounting-product-proposal':['Reading this proposal','only cash movement','Five dates attached','jointly admitted triples','For positive earnings','couple the initial states','Initial and within-pair approximation','2002.07261v2'],'simulation-foundations':['couple the initial states','Initial and within-pair approximation','2002.07261v2']}
for name in ['accounting-product-proposal','simulation-foundations']:
 doc=fitz.open(T/(name+'.pdf'));log=(T/(name+'.log')).read_text(errors='replace');ck('build_log:'+name,not re.search(r'undefined|Overfull|multiply defined',log,re.I));ck('version:'+name,'5.53-R1' in doc[0].get_text());vol.append({'name':name,'pages':len(doc),'sha256':sha(T/(name+'.pdf'))});pages={1}
 for needle in needles[name]:
  hits=[i+1 for i,p in enumerate(doc) if needle in ' '.join(p.get_text().split())];ck('render_anchor:'+name+':'+needle,bool(hits),hits);pages.update(hits)
 for n in sorted(pages):
  path=out/f'{name}-{n:04}.png';doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(path);render.append({'volume':name,'page':n,'path':str(path.relative_to(R)),'pdf_sha256':sha(T/(name+'.pdf')),'review':'not_yet_viewed'})
 clipping=[]
 for i,page in enumerate(doc):
  for word in page.get_text('words'):
   if word[0]<-1 or word[1]<-1 or word[2]>page.rect.width+1 or word[3]>page.rect.height+1:clipping.append({'page':i+1,'word':word[4]})
 ck('page_rectangle_text_bounds:'+name,not clipping,clipping[:10])
(D/'rendered-pages.json').write_text(json.dumps(render,indent=2)+'\n')
delta=[]
for name in changes:delta.extend(difflib.unified_diff((B/name).read_text().splitlines(True),(T/name).read_text().splitlines(True),fromfile='5.53/'+name,tofile='5.53-R1/'+name))
(D/'final-source-delta.patch').write_text(''.join(delta))
result={'pass':all(c['pass'] for c in checks),'checks':checks,'changed_files':changes,'new_files':['reading-guide.tex'],'volumes':vol,'command':[sys.executable,str(Path(__file__).resolve())],'wall_seconds':time.monotonic()-start,'environment':sys.version,'plan':str((D/'plan.md').relative_to(R)),'scope':'source,build,layout-bound checks; rendered author review and independent acceptance separate'};(D/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'checks':len(checks),'failures':[c for c in checks if not c['pass']],'volumes':vol,'render_pages':[{'volume':x['volume'],'page':x['page']} for x in render]}));raise SystemExit(0 if result['pass'] else 1)
