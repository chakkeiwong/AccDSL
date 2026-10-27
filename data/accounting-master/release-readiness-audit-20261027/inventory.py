"""Read-only manuscript structure inventory; does not certify scholarly comprehension."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,fitz
H=Path(__file__).resolve().parent;R=H.parents[2];base=json.loads((H/'baseline.json').read_text());S=R/base['source']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n')
visited=[];unresolved=[];stream=[]
def walk(p,stack):
 if p in stack:raise ValueError('input_cycle:'+str(p))
 visited.append(p)
 for i,line in enumerate(p.read_text().splitlines(),1):
  clean=re.split(r'(?<!\\)%',line)[0]
  inc=re.search(r'\\(?:input|include)\{([^}]+)\}',clean)
  if inc:
   q=S/inc[1];q=q if q.suffix else q.with_suffix('.tex')
   if q.exists():walk(q,stack+[p])
   else:unresolved.append({'file':str(p.relative_to(S)),'line':i,'input':inc[1]})
  else:stream.append((str(p.relative_to(S)),i,clean))
walk(S/'accounting-product-proposal.tex',[])
levels={'part':0,'chapter':1,'section':2,'subsection':3,'subsubsection':4,'paragraph':5};parents={};units=[];equations=[];chapter=None
for filename,line,text in stream:
 m=re.match(r'.*?\\(part|chapter|section|subsection|subsubsection|paragraph)\*?(?:\[[^]]*\])?\{(.*?)\}(?:.*)?$',text)
 if m:
  kind,title=m.groups();level=levels[kind];uid=f'{filename}:{line}'
  unit={'id':uid,'kind':kind,'title':title,'parent':parents.get(level-1),'source':filename,'line':line,'structural_inventory':'located','continuous_read':'not_checked','independent_reader':'pending','human_acceptance':'pending'}
  units.append(unit);parents={k:v for k,v in parents.items() if k<level};parents[level]=uid
  if kind=='chapter':chapter=unit
 for m in re.finditer(r'\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath)\}|\\\[|\$\$',text):
  equations.append({'id':f'{filename}:{line}:display:{len(equations)+1}','kind':'display','parent':parents[max(parents)] if parents else None,'source':filename,'line':line,'classification':'not_checked','exposition_review':'not_checked','mathematical_check':'not_checked'})
unique=list(dict.fromkeys(visited));citation_use=[];labels=[]
for p in unique:
 for i,line in enumerate(p.read_text().splitlines(),1):
  for m in re.finditer(r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',line):
   for k in m[1].split(','):citation_use.append({'key':k.strip(),'source':str(p.relative_to(S)),'line':i})
  for m in re.finditer(r'\\label\{([^}]+)\}',line):labels.append({'label':m[1],'source':str(p.relative_to(S)),'line':i})
bib=(S/'references.bib').read_text();keys=re.findall(r'@\w+\{([^,]+),',bib);counts=Counter(keys);labs=Counter(x['label'] for x in labels)
pdfs=[];pages=[]
for key in ['current_pdf','standalone_pdf']:
 p=R/base['active_execution'][key];doc=fitz.open(p);toc=doc.get_toc();pdfs.append({'path':str(p.relative_to(R)),'sha256':sha(p),'pages':len(doc),'toc_entries':len(toc),'toc':toc})
 for i,page in enumerate(doc):pages.append({'pdf':str(p.relative_to(R)),'physical_page':i+1,'printed_page':page.get_label(),'text_sha256':hashlib.sha256(page.get_text().encode()).hexdigest(),'continuous_read':'not_checked','rendered_review':'not_checked'})
chapters=[u for u in units if u['kind']=='chapter'];out=[]
for i,c in enumerate(chapters):
 first=next(j for j,x in enumerate(stream) if x[0]==c['source'] and x[1]==c['line']);end=next((j for j in range(first+1,len(stream)) if re.match(r'\s*\\chapter(?:\*|\[|\{)',stream[j][2])),len(stream));lines=stream[first:end];text='\n'.join(x[2] for x in lines);headings=[x for x in units if any(x['id']==f'{y[0]}:{y[1]}' for y in lines)]
 out.append({'title':c['title'],'source':c['source'],'words':len(text.split()),'headings':len(headings),'opening':'\n'.join(x[2] for x in lines[:20]),'ending':'\n'.join(x[2] for x in lines[-16:]),'scope_flags':[{'source':f,'line':n,'text':s} for f,n,s in lines if re.search(r'not_ready|pending|first release|before release|unimplemented|held|future work|does not yet|unsupported|not implemented|release criteria',s,re.I)]})
dump('structure.json',{'units':units,'display_nodes':equations,'unresolved_inputs':unresolved,'parser_limit':'Literal include/heading/display inventory; TeX macros are not expanded. PDF bookmarks provide a separate compiled cross-check. No reading or mathematical acceptance inferred.'});dump('pages.json',pages);dump('chapters.json',out);dump('pdf-navigation.json',pdfs)
dump('inventory.json',{'candidate':base['candidate'],'included_files':{str(p.relative_to(S)):sha(p) for p in unique},'counts':{'included_tex':len(unique),'chapters':len(chapters),'structural_units':len(units),'display_nodes':len(equations),'bibliography_entries':len(keys),'distinct_cited_keys':len(set(x['key'] for x in citation_use)),'citation_occurrences':len(citation_use)},'missing_citation_keys':sorted(set(x['key'] for x in citation_use)-set(keys)),'duplicate_bib_keys':{k:v for k,v in counts.items() if v>1},'duplicate_labels':{k:v for k,v in labs.items() if v>1},'unresolved_inputs':unresolved,'citation_use':citation_use})
print(json.dumps({'counts':json.loads((H/'inventory.json').read_text())['counts'],'unresolved_inputs':unresolved,'chapters':[(x['title'],x['words']) for x in out]}))
