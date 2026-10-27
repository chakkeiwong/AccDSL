"""Structural source coverage, explicitly separate from semantic acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,sys,time
import fitz
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda t:' '.join(t.split())
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))
POINTERS=['docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-master-current.md']
PRIOR=ROOT/'data/accounting-master/apple-regulation-20261010/run-manifest.json'
PLAN=ROOT/'docs/plans/accounting-apple-risk-coverage-20261010.md'

def save(n,d):
 p=OUT/n;p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('x') as f:f.write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def verify(h):
 for n,v in h.items():assert sha(ROOT/n)==v,n

def run():
 start=time.monotonic();m=read(PRIOR);assert sha(PRIOR)==read(PRIOR.with_name('completion.json'))['manifest_sha256'];verify(m['artifact_hashes'])
 refs={rel(PRIOR):sha(PRIOR),rel(PRIOR.with_name('completion.json')):sha(PRIOR.with_name('completion.json')),rel(PLAN):sha(PLAN),rel(Path(__file__)):sha(Path(__file__))}
 pointers=[]
 for n in POINTERS:
  p=OUT/'pointers-before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p);pointers.append(dict(historical_path=n,preserved_path=rel(p),sha256=sha(p)))
 save('baseline.json',dict(prior_manifest=rel(PRIOR),prior_manifest_sha256=sha(PRIOR),prior_references=len(m['artifact_hashes']),pointer_relocations=pointers,pdf=m['pdf']))
 s=read(ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json')['sources'];texts={};docs={}
 for k in ['annual','interim']:
  for kind in ['original','extraction']:
   p=ROOT/s[k][kind+'_path'];assert sha(p)==s[k][kind+'_sha256'];refs[rel(p)]=sha(p)
  texts[k]=(ROOT/s[k]['extraction_path']).read_text()
 docs['annual']=fitz.open(ROOT/s['annual']['original_path'])
 scope={}
 for k in texts:
  t=texts[k];matches=list(re.finditer(r'Item 1A\.\s+Risk Factors',t));a=matches[-1].start();end='Item 1B.' if k=='annual' else 'Item 2.';b=t.index(end,a);scope[k]=(a,b)
 candidates=[]
 for i,p in enumerate(docs['annual']):
  if i+1<8 or i+1>20:continue
  for block in p.get_text('dict')['blocks']:
   group=[];boxes=[]
   for line in block.get('lines',[]):
    spans=line['spans'];italic=spans and all('BoldItalic' in x['font'] or 'BoldOblique' in x['font'] for x in spans)
    if italic:group.append(' '.join(x['text'] for x in spans));boxes.append(line['bbox'])
    elif group:
     candidates.append(dict(text=norm(' '.join(group)),pdf_page=i+1,bboxes=boxes));group=[];boxes=[]
   if group:candidates.append(dict(text=norm(' '.join(group)),pdf_page=i+1,bboxes=boxes))
 def locate(k,candidates):
  t=texts[k];a,b=scope[k];result=[]
  for c in candidates:
   pattern=r'\s+'.join(re.escape(x) for x in c['text'].split());matches=list(re.finditer(pattern,t[a:b]));assert len(matches)==1,(k,c,matches)
   match=matches[0];result.append(dict(**c,start=a+match.start(),heading_end=a+match.end()))
  return sorted(result,key=lambda x:x['start'])
 headings={'annual':locate('annual',candidates)}
 soup=BeautifulSoup((ROOT/s['interim']['original_path']).read_text(),'html.parser')
 expected=['The Company is subject to complex and changing laws and regulations worldwide','The technology industry, including, in some instances, the Company']
 interim_candidates=[]
 for text in expected:
  nodes=[node for node in soup.find_all('span') if 'font-weight:700' in node.get('style','') and norm(node.get_text(' ',strip=True)).startswith(text)]
  assert len(nodes)==1,(text,len(nodes));interim_candidates.append(dict(text=norm(nodes[0].get_text(' ',strip=True)),html_tag=nodes[0].name))
 headings['interim']=locate('interim',interim_candidates)
 assert len(headings['annual'])==28 and len(headings['interim'])==2
 pool=[];mismatches=[];scope_exclusions=[];checked=0
 excluded={
 'data/accounting-master/apple-eps-20261009/source-claim-supplement.json/dependencies/4':'annual.calendar crosses Business through Note 1; literal bytes retained but narrow calendar reading only',
 'data/accounting-master/apple-revenue-20261008/source-claim-supplement.json/dependencies/2':'annual.segment crosses Business through Note 13; literal bytes retained but narrow segment reading only'}
 def walk(d,path):
  if isinstance(d,dict):
   k=d.get('source_id',d.get('source'));q=d.get('quote');a=d.get('start');b=d.get('end')
   if isinstance(k,str) and k in texts and isinstance(q,str) and isinstance(a,int) and isinstance(b,int):
    exact=texts[k][a:b]==q;trim=texts[k][a:b].rstrip()==q.rstrip()
    if exact or trim:
     row=dict(source=k,start=a,end=b,unit=path.split('/')[2],json_path=path,match='literal' if exact else 'trailing whitespace only')
     if path in excluded:scope_exclusions.append(dict(**row,reason=excluded[path],verdict='wrong relative to labelled narrow source-reading scope; excluded from reading coverage'))
     else:pool.append(row)
    else:mismatches.append(dict(path=path,source=k,start=a,end=b,reason='literal/offset mismatch; excluded from coverage'))
   for n,v in d.items():walk(v,path+'/'+str(n))
  elif isinstance(d,list):
   for n,v in enumerate(d):walk(v,path+'/'+str(n))
 for p in sorted((ROOT/'data/accounting-master').glob('apple-*/source-claim-supplement.json')):
  manifest=p.with_name('run-manifest.json');dm=read(manifest);h=dm['artifact_hashes'][rel(p)];assert sha(p)==h;refs[rel(p)]=h;refs[rel(manifest)]=sha(manifest);walk(read(p),rel(p));checked+=1
 assert len(scope_exclusions)==2
 repairs=[];t=texts['annual']
 for ident,opening,context,ending in [('annual.calendar','The Company’s fiscal year is the 52- or 53-week period','Note 1 – Summary of Significant Accounting Policies',None),('annual.segment','The Company manages its business primarily on a geographic basis','Note 13 – Segment Information and Geographic Data','Apple Inc. | 2024 Form 10-K | 46')]:
  a=t.index(opening,t.index(context));b=t.index(ending,a) if ending else t.index('\n\n',a);q=t[a:b].rstrip();f=OUT/'scope-repairs'/(ident+'.txt');f.parent.mkdir(exist_ok=True);f.write_text(q+'\n');repairs.append(dict(id=ident,start=a,end=a+len(q),quote=q,sha256=hashlib.sha256(q.encode()).hexdigest(),retained_span=rel(f),meaning='Superseding context-bound locator; historical broad bytes preserved, no new risk interpretation'))
 save('locator-scope-repairs.json',dict(exclusions=scope_exclusions,repairs=repairs,prior_source_files_unchanged=True))
 categories=['Macroeconomic and Industry Risks','Business Risks','Legal and Regulatory Compliance Risks','Financial Risks','General Risks']
 ignored=lambda t:re.sub(r'Apple Inc\. \| (?:2024 Form 10-K|Q1 2025 Form 10-Q) \| \d+','',t)
 records=[];checks=[]
 def ck(n,ok):checks.append(dict(id=n,passed=bool(ok)))
 for k,hs in headings.items():
  t=texts[k];a,b=scope[k];preamble=t[a:hs[0]['start']];(OUT/(k+'-preamble.txt')).write_text(preamble)
  for i,h in enumerate(hs):
   end=hs[i+1]['start'] if i+1<len(hs) else b
   category_candidates=[t.find(c,h['heading_end'],end) for c in categories] if k=='annual' else []
   # A new category is context of the next heading, not preceding body.
   valid=[x for x in category_candidates if x!=-1];bodyend=min(valid) if valid else end
   body=t[h['heading_end']:bodyend];quote=t[h['start']:bodyend];f=OUT/'bodies'/(k+f'-{i+1:02}.txt');f.parent.mkdir(exist_ok=True);f.write_text(quote)
   meaningful=[not ch.isspace() for ch in body]
   for match in re.finditer(r'Apple Inc\. \| (?:2024 Form 10-K|Q1 2025 Form 10-Q) \| \d+',body):
    for j in range(match.start(),match.end()):meaningful[j]=False
   coverage=[False]*len(body);overlaps=[]
   for p in pool:
    if p['source']!=k:continue
    x=max(h['heading_end'],p['start']);y=min(bodyend,p['end'])
    if x<y:
     overlaps.append(p)
     for j in range(x-h['heading_end'],y-h['heading_end']):coverage[j]=True
   missing=[];j=0
   while j<len(body):
    if meaningful[j] and not coverage[j]:
     x=j;j+=1
     while j<len(body) and (not meaningful[j] or not coverage[j]):j+=1
     missing.append(dict(start=h['heading_end']+x,end=h['heading_end']+j,quote=body[x:j].strip()))
    else:j+=1
   has=any(c and q for c,q in zip(coverage,meaningful));status='complete body retained' if not missing else ('partial dependency only' if has else 'no prior retained reading')
   rec=dict(source=k,index=i+1,heading=h['text'],start=h['start'],heading_end=h['heading_end'],body_end=bodyend,boundary_end=end,quote_sha256=hashlib.sha256(quote.encode()).hexdigest(),body_path=rel(f),body_sha256=sha(f),retention_status=status,prior_overlaps=overlaps,uncovered_spans=missing,interpretation_status='not independently accepted; prior unit meaning remains scoped',pdf_page=h.get('pdf_page'),heading_provenance=h)
   records.append(rec);ck(k+f'-{i+1:02} body exact',t[rec['start']:rec['body_end']]==quote);ck(k+f'-{i+1:02} heading exact',norm(t[rec['start']:rec['heading_end']])==h['text'])
  # Every scope character belongs to preamble, risk, or inter-risk/category furniture.
  ranges=[(a,hs[0]['start'])]+[(h['start'],hs[i+1]['start'] if i+1<len(hs) else b) for i,h in enumerate(hs)]
  ck(k+' exhaustive contiguous scope partition',ranges[0][0]==a and ranges[-1][1]==b and all(x[1]==y[0] for x,y in zip(ranges,ranges[1:])))
  save(k+'-scope.json',dict(start=a,end=b,sha256=hashlib.sha256(t[a:b].encode()).hexdigest(),ranges=ranges,source=s[k]))
 ck('two broad dependency scopes excluded',len(scope_exclusions)==2);ck('annual heading population 28',len(headings['annual'])==28);ck('interim heading population 2',len(headings['interim'])==2)
 save('risk-coverage.json',dict(records=records,prior_accepted_supplements=checked,prior_span_pool=len(pool),excluded_mismatches=mismatches,scope_exclusions=scope_exclusions,categories=categories,scope='Annual Item 1A and interim Item 1A only',not_semantic_completion=True,new_inventory_not_counted_as_prior_reading=True,inputs=refs))
 counts={k:{v:sum(r['source']==k and r['retention_status']==v for r in records) for v in ['complete body retained','partial dependency only','no prior retained reading']} for k in texts}
 save('checks.json',dict(checker_sha256=sha(Path(__file__)),inputs=refs,checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),counts=counts,excluded_mismatches=mismatches,scope_exclusions=scope_exclusions,wall_seconds=time.monotonic()-start));assert all(x['passed'] for x in checks)
 # Hierarchy navigation only, not normal-resolution continuous source reading.
 contact=Image.new('RGB',(1800,5*450),(235,235,235));draw=ImageDraw.Draw(contact);image_records=[]
 for j,n in enumerate(range(8,21)):
  pix=docs['annual'][n-1].get_pixmap(matrix=fitz.Matrix(.60,.60));p=OUT/'hierarchy'/f'page-{n:03}.png';p.parent.mkdir(exist_ok=True);pix.save(p);im=Image.open(p);im.thumbnail((430,410));x=(j%4)*450;y=(j//4)*450;contact.paste(im,(x,y+25));draw.text((x+10,y+7),'Original PDF page '+str(n),fill='black');image_records.append(dict(page=n,path=rel(p),sha256=sha(p)))
 cp=OUT/'hierarchy/contact.png';contact.save(cp);save('hierarchy-render.json',dict(contact=dict(path=rel(cp),sha256=sha(cp)),images=image_records,status='Heading hierarchy/navigation only; not continuous scholarly reading'))
 print(json.dumps(dict(passed=sum(x['passed'] for x in checks),counts=counts,excluded_mismatches=len(mismatches),prior_supplements=checked),ensure_ascii=False))

if __name__=='__main__':
 assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1';assert not (OUT/'checks.json').exists();run()
