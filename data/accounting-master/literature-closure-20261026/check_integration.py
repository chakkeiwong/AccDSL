from pathlib import Path
import hashlib,json,re,fitz
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
j=json.loads((B/'manuscript-integration.json').read_text());old=R/j['baseline'];new=R/j['successor']
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):
 checks.append(dict(id=name,passed=bool(ok)));assert ok,name
edits={e['path']:e for e in j['edits']}
for row in j['protected_sources']:
 rel=row['path'];f=old/rel;g=new/rel;ck('baseline_'+rel,sha(f)==row['sha256'])
 a=f.read_bytes();b=g.read_bytes()
 for edit in j.get('presentation_insertions',[]):
  if edit['path']==rel:b=b.replace(edit['insertion'].encode(),b'')
 if rel in edits:
  for edit in j['edits']:
   if edit['path']==rel:b=b.replace(edit['insertion'].encode(),b'')
 elif rel=='references.bib':b=b[:len(a)]
 elif rel in ['accounting-product-proposal.tex','simulation-foundations.tex']:
  b=b.replace(('Version '+j['successor_version']+' (proposal candidate)').encode(),('Version '+j['baseline_version']+' (proposal candidate)').encode()).replace(('Version '+j['successor_version']+' research companion').encode(),b'Version 5.5 research companion')
  b=b.replace(b'amsmath,amssymb,amsthm,',b'amsmath,amssymb,')
  b=b.replace(b'\\newtheorem{proposition}{Proposition}[chapter]\n',b'').replace(b'\\newcommand{\\ind}{\\mathbf 1}\n',b'')
 ck('preserved_'+rel,a==b)
warn=lambda p:[x for x in p.read_text().splitlines() if re.search(r'Warning|Overfull|Underfull|undefined|^!',x)]
ck('main_no_new_warnings',warn(new/'accounting-product-proposal.log')==warn(old/'accounting-product-proposal.log'))
ck('standalone_no_warnings',not warn(new/'simulation-foundations.log'))
alltex='\n'.join(f.read_text() for f in new.rglob('*.tex') if f.name not in ['simulation-foundations.tex'])
keys=set(re.findall(r'@\w+\{([^,]+)',(new/'references.bib').read_text()))
cites={key for group in re.findall(r'\\cite\w*\*?(?:\[[^]]*\]){0,2}\{([^}]+)\}',alltex) for key in group.split(',')}
ck('all_citations_resolve',cites<=keys)
aux=(new/'simulation-foundations.aux').read_text();body_end=int(re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1));body=body_end-1
ck('requested_body_range',150<=body<=300)
# Locate sections by PDF outlines, avoiding guessed PDF/printed-page offsets.
headings=[]
for e in j['edits']:headings+=re.findall(r'\\section\{([^}]+)\}',(new/e['fragment']).read_text())
render=B/'rendered-integration';render.mkdir(exist_ok=True)
from PIL import Image,ImageDraw
rendered={}
for stem in ['simulation-foundations','accounting-product-proposal']:
 pdf=fitz.open(new/(stem+'.pdf'));toc=pdf.get_toc();pages={0};entries=[]
 for n,t in enumerate(toc):
  if re.sub(r'^\d+(?:\.\d+)*\s+', '', t[1]) in headings:
   end=next((v[2]-1 for v in toc[n+1:] if v[0]<=t[0]),t[2])
   selected=list(range(max(0,t[2]-2),min(len(pdf),end+1)))
   pages.update(selected);entries.append(dict(title=t[1],physical_start=t[2],physical_end=max(t[2],end)))
 # Bibliography and contents review includes affected entries and author names.
 firstbody=next(x[2] for x in toc if x[1].startswith('1 ')) if any(x[1].startswith('1 ') for x in toc) else 0
 pages.update(range(min(firstbody-1 if firstbody else 4,len(pdf))))
 bibstart=next((i+1 for i,page in enumerate(pdf) if 'Bibliography' in [line.strip() for line in page.get_text().splitlines()[:6]]),len(pdf)-5)
 pages.update(range(bibstart-1,len(pdf)))
 rendered[stem]=dict(pages=sorted(x+1 for x in pages),section_ranges=entries,total_pages=len(pdf),sha256=sha(new/(stem+'.pdf')))
 selected=sorted(pages)
 for n in range(0,len(selected),2):
  canvas=Image.new('RGB',(1600,1160),'#d9d9d9');draw=ImageDraw.Draw(canvas)
  for col,idx in enumerate(selected[n:n+2]):
   pix=pdf[idx].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((785,1115))
   canvas.paste(im,(col*800+(800-im.width)//2,30));draw.text((col*800+12,8),stem+' physical page '+str(idx+1),fill='black')
  canvas.save(render/(stem+'-'+str(n//2+1).zfill(2)+'.png'))
# Supplement: render every page, not only changes.
pdfpath=R/'docs/design/research/simulation-literature-closure-20261026/supplement.pdf';pdf=fitz.open(pdfpath);folder=B/'rendered-current';folder.mkdir(exist_ok=True)
for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(folder/f'page-{i+1:02d}.png')
for i in range(0,len(pdf),2):
 canvas=Image.new('RGB',(1600,1160),'#d9d9d9');draw=ImageDraw.Draw(canvas)
 for col,idx in enumerate(range(i,min(i+2,len(pdf)))):
  im=Image.open(folder/f'page-{idx+1:02d}.png');im.thumbnail((785,1115));canvas.paste(im,(col*800+(800-im.width)//2,30));draw.text((col*800+12,8),'Supplement page '+str(idx+1),fill='black')
 canvas.save(folder/f'spread-{i//2+1:02d}.png')
result=dict(status='PASS',checks=checks,protected_sources=len(j['protected_sources']),simulation_body_pages=body,simulation_chapters=26,source_additions=len(j['edits']),new_bibliography_entries=len(j['new_bibliography_keys']),rendered=rendered,supplement_pages=len(pdf),supplement_sha256=sha(pdfpath),review='Rendering generated; actual visual inspection recorded separately')
(B/'integration-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['checks','rendered']}));print(json.dumps({k:len(v['pages']) for k,v in rendered.items()}))
