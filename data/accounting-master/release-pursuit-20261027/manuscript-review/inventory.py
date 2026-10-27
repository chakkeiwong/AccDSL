from pathlib import Path
from collections import Counter,defaultdict
import re,json,hashlib,sys,fitz
D=Path(__file__).resolve().parent;R=D.parents[3]
T=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else (R/'docs/AccDSL-latest.tex').resolve().parent
OUT=D/(T.name+'-inventory.json');bs=chr(92)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()[:18]
def group(s,i,left='{',right='}'):
 while i<len(s) and s[i].isspace():i+=1
 if i>=len(s) or s[i]!=left:raise ValueError(('missing group',s[i:i+80]))
 start=i;i+=1;depth=1
 while i<len(s):
  if s[i]==bs:i+=2;continue
  if s[i]==left:depth+=1
  elif s[i]==right:
   depth-=1
   if depth==0:return s[start+1:i],i+1
  i+=1
 raise ValueError('unclosed group')
def clean(s):
 lines=[]
 for line in s.splitlines(keepends=True):
  cut=None
  for i,c in enumerate(line):
   if c=='%':
    k=i-1
    while k>=0 and line[k]==bs:k-=1
    if (i-1-k)%2==0:cut=i;break
  lines.append(line if cut is None else line[:cut]+' '*(len(line.rstrip(chr(10)))-cut)+(chr(10) if line.endswith(chr(10)) else ''))
 return ''.join(lines)
levels={'part':1,'chapter':2,'section':3,'subsection':4,'subsubsection':5,'paragraph':6,'subparagraph':7}
displays={'equation','equation*','align','align*','gather','gather*','multline','multline*','displaymath','eqnarray','eqnarray*'}
verbatim={'lstlisting','verbatim','Verbatim','comment'}
allnodes={};volumes=[];findings=[];sources={};edges=[]
for volume in ['accounting-product-proposal','simulation-foundations']:
 pdf=T/(volume+'.pdf');doc=fitz.open(pdf);dest=doc.resolve_names();aux=(T/(volume+'.aux')).read_text(errors='replace');bookmarks={};labels={}
 for line in aux.splitlines():
  if line.startswith(bs+'BKM@entry'):
   m=re.search(r'dest=[{]([0-9A-F]+)[}],srcline=[{]([0-9]+)[}],srcfile=[{]([0-9A-F]+)[}]',line)
   if m:
    anchor=bytes.fromhex(m[1]).decode();file=bytes.fromhex(m[3]).decode().removeprefix('./');bookmarks[(file,int(m[2]))]=anchor
  if line.startswith(bs+'newlabel{'):
   key,k=group(line,len(bs+'newlabel'));body,k=group(line,k);fields=[];j=0
   while j<len(body):
    if body[j].isspace():j+=1;continue
    v,j=group(body,j);fields.append(v)
   if len(fields)>3:labels[key]={'number':fields[0],'printed_page':fields[1],'anchor':fields[3],'physical_page':dest.get(fields[3],{}).get('page',-1)+1}
 root='document:'+volume;stack=[{'id':root,'level':0}];nodes=[{'id':root,'kind':'document','level':0,'title':volume,'parent':None,'argument_parent':None,'source_file':volume+'.tex','source_sha256':sha(T/(volume+'.tex')),'line_start':1,'review':{'structural':'inventoried','author_read':'not_read','independent_reader':'pending','human_acceptance':'pending'}}];active=[]
 def append_node(kind,title,path,line,endline,body='',equation_labels=None):
  level=levels.get(kind,8);rel=str(path.relative_to(T));ident=kind+':'+digest(rel+':'+str(line)+':'+title+':'+body)
  if kind!='equation':
   while stack[-1]['level']>=level:stack.pop()
  parent=stack[-1]['id'];argument=next((v['id'] for v in reversed(stack) if v['level']==3),None);chapter=next((v['id'] for v in reversed(stack) if v['level']==2),None);part=next((v['id'] for v in reversed(stack) if v['level']==1),None)
  anchor=bookmarks.get((rel,line));page=(dest.get(anchor,{}).get('page',-1)+1) if anchor else None
  eqanchors=[labels[x] for x in equation_labels or [] if x in labels];eqpages=sorted({x['physical_page'] for x in eqanchors if x['physical_page']>0})
  node={'id':ident,'kind':kind,'level':level,'title':title,'parent':parent,'argument_parent':argument,'chapter_parent':chapter,'part_parent':part,'source_file':rel,'source_sha256':sha(path),'line_start':line,'line_end':endline,'body_sha256':digest(body) if body else None,'anchor':anchor,'physical_start':page,'equation_labels':equation_labels or [],'equation_anchors':eqanchors,'equation_pages':eqpages,'location_status':'exact_heading_anchor' if page else ('exact_label_anchor' if eqpages else 'source_only_requires_rendered_location'),'review':{'structural':'inventoried','author_read':'not_read','independent_reader':'pending','human_acceptance':'pending'},'judgment':None}
  if kind=='equation':node.update({'classification':'not_checked','classification_reason':None,'exposition':None})
  nodes.append(node)
  if kind!='equation':stack.append({'id':ident,'level':level})
 def visit(path):
  if path in active:raise ValueError('recursive input '+str(path))
  if not path.is_file():raise ValueError('missing input '+str(path))
  active.append(path);raw=path.read_text();s=clean(raw);rel=str(path.relative_to(T));sources[rel]=sha(path);i=0
  while i<len(s):
   if s.startswith('$$',i):
    end=s.find('$$',i+2)
    if end<0:raise ValueError('unclosed dollar display')
    body=s[i:end+2];append_node('equation','$$ display',path,s.count(chr(10),0,i)+1,s.count(chr(10),0,end+2)+1,body,[]);i=end+2;continue
   if s[i]!=bs:i+=1;continue
   start=i
   if s.startswith(bs+'[',i):
    end=s.find(bs+']',i+2)
    if end<0:raise ValueError('unclosed bracket display')
    body=s[i:end+2];labs=re.findall(re.escape(bs+'label')+r'[{]([^}]+)[}]',body);append_node('equation','unnumbered display',path,s.count(chr(10),0,i)+1,s.count(chr(10),0,end+2)+1,body,labs);i=end+2;continue
   m=re.match(r'[A-Za-z@]+',s[i+1:])
   if not m:i+=2;continue
   cmd=m[0];i+=1+len(cmd)
   if cmd=='begin':
    env,i=group(s,i)
    if env in verbatim:
     finish=s.find(bs+'end{'+env+'}',i)
     if finish<0:raise ValueError('unclosed verbatim '+env)
     i=finish+len(bs+'end{'+env+'}');continue
    if env in displays:
     finish=s.find(bs+'end{'+env+'}',i)
     if finish<0:raise ValueError('unclosed display '+env)
     i=finish+len(bs+'end{'+env+'}');body=s[start:i];labs=re.findall(re.escape(bs+'label')+r'[{]([^}]+)[}]',body);append_node('equation',env,path,s.count(chr(10),0,start)+1,s.count(chr(10),0,i)+1,body,labs)
   elif cmd in ['input','include']:
    target,i=group(s,i);p=T/target
    if not p.suffix:p=p.with_suffix('.tex')
    if p.suffix!='.tex':continue
    edges.append({'volume':volume,'from':rel,'line':s.count(chr(10),0,start)+1,'to':str(p.relative_to(T))});visit(p)
   elif cmd in levels:
    if i<len(s) and s[i]=='*':i+=1
    while i<len(s) and s[i].isspace():i+=1
    if i<len(s) and s[i]=='[':short,i=group(s,i,'[',']')
    title,i=group(s,i);append_node(cmd,title,path,s.count(chr(10),0,start)+1,s.count(chr(10),0,i)+1)
  active.pop()
 visit(T/(volume+'.tex'))
 # Reconcile lower heading levels omitted from PDF bookmarks against the
 # exact ordered TOC stream. Starred headings remain source-only.
 toc_rows=[]
 for line in (T/(volume+'.toc')).read_text().splitlines():
  if not line.startswith(bs+'contentsline'):continue
  i=len(bs+'contentsline');kind,i=group(line,i);title,i=group(line,i);printed,i=group(line,i);anchor,i=group(line,i)
  title=title.strip()
  if title.startswith(bs+'numberline'):
   num,j=group(title,len(bs+'numberline'));title=title[j:].strip()
  toc_rows.append({'kind':kind,'title':title,'anchor':anchor,'printed_page':printed})
 cursor=0
 for node in nodes:
  if node['kind'] not in levels:continue
  for k in range(cursor,len(toc_rows)):
   tr=toc_rows[k]
   if tr['kind']==node['kind'] and tr['title']==node['title']:
    node['toc_anchor']=tr['anchor'];node['printed_page']=tr['printed_page'];page=dest.get(tr['anchor'],{}).get('page',-1)+1
    if page>0:node['physical_start']=page;node['location_status']='exact_toc_anchor'
    cursor=k+1;break
 for i,node in enumerate(nodes):
  if node['kind'] not in levels or not node.get('physical_start'):continue
  following=next((x for x in nodes[i+1:] if x['kind'] in levels and x['level']<=node['level'] and x.get('physical_start')),None)
  node['physical_end_inclusive']=following['physical_start'] if following else len(doc)
  node['range_scope']='Inclusive shared boundary page; exact section extent requires rendered reading'
 # A display without a label receives only its containing argument range.
 # Never upgrade this enclosure to an exact rendered equation location.
 lookup={x['id']:x for x in nodes}
 for node in nodes:
  if node['kind']=='equation' and not node['equation_pages']:
   parent=lookup.get(node['parent'])
   while parent and not parent.get('physical_start'):parent=lookup.get(parent['parent'])
   if parent:node['enclosing_page_range']=[parent['physical_start'],parent.get('physical_end_inclusive',len(doc))]
 ids={x['id'] for x in nodes};dup=[k for k,n in Counter(x['id'] for x in nodes).items() if n>1]
 if dup:findings.append({'volume':volume,'kind':'duplicate_node_ids','ids':dup})
 for x in nodes:
  if x['parent'] is not None and x['parent'] not in ids:findings.append({'volume':volume,'kind':'missing_parent','id':x['id']})
  if x.get('argument_parent') and next(y for y in nodes if y['id']==x['argument_parent'])['kind']!='section':findings.append({'volume':volume,'kind':'wrong_argument_ancestor','id':x['id']})
 pages=[];headingnodes=[x for x in nodes if x.get('physical_start')]
 for i,page in enumerate(doc):
  prior=[x for x in headingnodes if x['physical_start']<=i+1];current=prior[-1]['id'] if prior else root
  pages.append({'physical_page':i+1,'printed_label':page.get_label(),'text_sha256':hashlib.sha256(page.get_text().encode()).hexdigest(),'last_heading_at_start_or_within_page':current,'structural_inventory':True,'author_continuous_read':'not_read','independent_reader':'pending','human_acceptance':'pending','reading_segment':None})
 volumes.append({'name':volume,'pdf':str(pdf.relative_to(R)),'pdf_sha256':sha(pdf),'root_sha256':sha(T/(volume+'.tex')),'pages':pages,'nodes':nodes,'counts':dict(Counter(x['kind'] for x in nodes)),'unlocated_heading_nodes':[x['id'] for x in nodes if x['kind'] not in ['equation','document'] and not x['physical_start']],'unlocated_displays':[x['id'] for x in nodes if x['kind']=='equation' and not x['equation_pages']]})
result={'schema':'accdsl.manuscript_review_inventory.v1','candidate':str(T.relative_to(R)),'source_files':[{'path':p,'sha256':h} for p,h in sorted(sources.items())],'include_edges':edges,'volumes':volumes,'structural_findings':findings,'read_segments':[],'whole_document_status':'not_read','independent_reader_status':'pending','human_acceptance':'pending','limits':'Source-level hierarchy and physical-page identities only. Every null judgment and not_read field is an uncompleted review obligation. Approximate/unlocated displays require rendered inspection; this tool grants no scholarly or release acceptance.'}
OUT.write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({'output':str(OUT.relative_to(R)),'sources':len(sources),'volumes':[{'name':v['name'],'pages':len(v['pages']),'nodes':len(v['nodes']),'counts':v['counts'],'unlocated_headings':len(v['unlocated_heading_nodes']),'unlocated_displays':len(v['unlocated_displays'])} for v in volumes],'findings':findings}))
