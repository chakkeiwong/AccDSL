from pathlib import Path
import hashlib,json,re,fitz
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent/'v552r1';b=json.loads((H/'baseline.json').read_text());S=R/b['source'];T=R/b['target'];checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(k,v,d=None):checks.append({'check':k,'pass':bool(v),'detail':d})
changes=[]
for row in b['inputs']:
 p=S/row['path'];q=T/row['path'];ck('baseline:'+row['path'],sha(p)==row['sha256']);ck('present:'+row['path'],q.exists())
 if q.exists() and p.read_bytes()!=q.read_bytes():changes.append(row['path'])
 if p.suffix=='.tex':
  for token in ['cite','begin{equation}','begin{align}']:
   def tokens(t):return [x.split('}',1)[0] for x in t.split(chr(92)+token)[1:]]
   ck('tokens:'+token+':'+row['path'],tokens(p.read_text())==tokens(q.read_text()))
expected={'accounting-product-proposal.tex','simulation-foundations.tex','simulation/family-policies.tex','simulation/observation-binding.tex','chapters/10-validation.tex','spec/REFERENCE-ROOTS.md'}
ck('exact_changes',set(changes)==expected,changes)
ck('bibliography_unchanged',sha(S/'references.bib')==sha(T/'references.bib'))
for name,digest in b['pdfs'].items():ck('protected_pdf:'+name,sha(S/name)==digest)
volumes=[];rendered=[]
for name in ['accounting-product-proposal','simulation-foundations']:
 old=fitz.open(S/(name+'.pdf'));new=fitz.open(T/(name+'.pdf'));log=(T/(name+'.log')).read_text();diffs=[i+1 for i in range(min(len(old),len(new))) if old[i].get_text()!=new[i].get_text()]
 ck(name+':same_pages',len(old)==len(new),(len(old),len(new)))
 ck(name+':no_undefined',not any('undefined' in x.lower() for x in log.splitlines()))
 ck(name+':no_overfull','Overfull' not in log)
 for page in diffs:
  out=H/'rendered'/name/f'{page:04d}.png';out.parent.mkdir(parents=True,exist_ok=True);new[page-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out);rendered.append({'volume':name,'physical_page':page,'printed_page':new[page-1].get_label(),'path':str(out.relative_to(R)),'review':'pending'})
 volumes.append({'name':name,'pages':len(new),'sha256':sha(T/(name+'.pdf')),'changed_text_pages':diffs})
ck('simulation_page_target',150<=volumes[1]['pages']<=300)
components=[]
for component in json.loads((T/'component-index.json').read_text()):
 src=R/component['source'];dest=T/component['path'];rows=[]
 for p in sorted(src.rglob('*')):
  if p.is_file():rows.append({'file':str(p.relative_to(src)),'match':(dest/p.relative_to(src)).is_file() and sha(p)==sha(dest/p.relative_to(src))})
 ck('component:'+component['name'],all(x['match'] for x in rows));components.append({'name':component['name'],'files':len(rows),'all_match':all(x['match'] for x in rows)})
(T/'build-environment.json').write_bytes((H/'build-manifest.json').read_bytes())
result={'checks':checks,'passed':all(x['pass'] for x in checks),'volumes':volumes,'changed_sources':changes,'components':components,'rendered':rendered,'limits':'Exact intended source delta and byte/citation/build diagnostics. Rendered/technical/independent acceptance distinct.'};(H/'checks.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2));print('CHECKS',len(checks),'FAILED',[x for x in checks if not x['pass']])
