"""Version-specific clause records and bounded source views."""
import hashlib,html,json,re
from pathlib import Path
import fitz
from bs4 import BeautifulSoup
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'source-views.json').exists():raise SystemExit('Existing views; inspect.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
targets=json.loads((U/'targets.json').read_text());records=[]
for x in targets:
    raw=(U/'sources'/f'{x["number"]}-span.txt').read_text();t=' '.join(raw.split())
    anchors={}
    for n,label,nextlabel in [(3,'3. Vesting','4. Continuance'),(4,'4. Continuance','5. Dividend'),
      (5,'5. Dividend','6. Restrictions'),(7,'7. Timing','8. Effect'),(8,'8. Effect','9. Recoupment')]:
        a=t.index(label);z=t.index(nextlabel,a+len(label));anchors[str(n)]={'start':a,'end':z,'text':t[a:z]}
    a=t.index('PERFORMANCE VESTING REQUIREMENTS');anchors['A']={'start':a,'end':len(t),'text':t[a:]}
    records.append({'id':x['id'],'description':x['description'],'source_span':x['target_span'],
        'normalized_span_sha256':hashlib.sha256(t.encode()).hexdigest(),'clauses':anchors})
pdf=R/'docs/design/cases/apple/annual-2024.pdf';d=fitz.open(pdf);pages=[]
for n in [82,83,84,85,89,90,99,100,101,102,106,107]:
    p=U/'sources'/f'annual-p{n}.png';d[n-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(p)
    pages.append({'pdf_page':n,'path':str(p.relative_to(R)),'sha256':sha(p)})
# Retain the actual HTML exhibit, then render exact normalized selected clauses.
src=R/targets[0]['target_span']['original_path'];soup=BeautifulSoup(src.read_text(),'html.parser')
exhibits=[e for e in soup.find_all('efx_exhibit_10') if 'Exhibit 10.2' in ' '.join(e.get_text(' ',strip=True).split())[:200]]
assert len(exhibits)==1,len(exhibits)
ex=exhibits[0];fragment=U/'sources/ceo2022-exhibit.html';fragment.write_text(str(ex))
htmltext=' '.join(ex.get_text(' ',strip=True).split())
for key in ['7','8']:
    # HTML extraction can add spacing around punctuation; preserve both forms.
    assert re.sub(r'\s','',records[0]['clauses'][key]['text']) in re.sub(r'\s','',htmltext)
body='<h1>Derived September2022 CEO form: Sections7 and8</h1>'
body+='<p>From retained fiscal2023Q1 HTML; selected normalized text, not a browser screenshot.</p>'
for key in ['7','8']:body+='<p>'+html.escape(records[0]['clauses'][key]['text'])+'</p>'
view=U/'sources/ceo2022-view.html';view.write_text(body);out=U/'sources/ceo2022-view.pdf'
story=fitz.Story(html=body,user_css='body {font-family:sans-serif; font-size:10pt;} h1 {font-size:14pt;}')
w=fitz.DocumentWriter(out);rect=fitz.paper_rect('a4');where=rect+(36,36,-36,-36);more=1
while more:
    dev=w.begin_page(rect);more,_=story.place(where);story.draw(dev);w.end_page()
w.close();v=fitz.open(out);images=[]
for i,p in enumerate(v):
    im=U/'sources'/f'ceo2022-view-{i+1}.png';p.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(im);images.append({'path':str(im.relative_to(R)),'sha256':sha(im)})
(U/'clauses.json').write_text(json.dumps(records,indent=2)+'\n')
(U/'source-views.json').write_text(json.dumps({'annual':str(pdf.relative_to(R)),'annual_sha256':sha(pdf),'pages':pages,
 'ceo2022':{'original':str(src.relative_to(R)),'sha256':sha(src),'fragment':str(fragment.relative_to(R)),'fragment_sha256':sha(fragment),'view':str(view.relative_to(R)),'images':images},
 'page_boundary_note':'The prior span page locator names91/108 as ending pages; exact text spans stop before next exhibits. Operative performance forms end on90/107. Frozen spans and labels preserved.'},indent=2)+'\n')
print(json.dumps({'annual_images':len(pages),'ceo2022_images':len(images),'clause_records':len(records)}))
