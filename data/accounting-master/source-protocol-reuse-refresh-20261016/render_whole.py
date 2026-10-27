"""All-page layout overviews; these do not certify text comprehension."""
from pathlib import Path
import hashlib,json
import fitz
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
pdf=ROOT/'docs/design/proposal/manuscript-source-protocol-reuse-refresh-20261016/accounting-product-proposal.pdf'
dest=OUT/'whole-render';dest.mkdir(exist_ok=False)
doc=fitz.open(pdf);records=[];sheets=[]
for start in range(0,len(doc),25):
    sheet=Image.new('RGB',(1800,2650),'#dddddd');draw=ImageDraw.Draw(sheet)
    for j in range(25):
        idx=start+j
        if idx>=len(doc):break
        pix=doc[idx].get_pixmap(matrix=fitz.Matrix(.65,.65),alpha=False)
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((350,500))
        x,y=(j%5)*360,(j//5)*530
        sheet.paste(im,(x+5,y+23));draw.text((x+6,y+5),f'Physical page {idx+1}',fill='black')
        records.append(dict(page=idx+1,sheet=f'overview-{start//25+1:02d}.png',box=[x+5,y+23,x+5+im.width,y+23+im.height],text_characters=len(doc[idx].get_text())))
    p=dest/f'overview-{start//25+1:02d}.png';sheet.save(p)
    sheets.append(dict(path=str(p.relative_to(ROOT)),first=start+1,last=min(start+25,len(doc)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert [x['page'] for x in records]==list(range(1,len(doc)+1))
(OUT/'whole-render-manifest.json').write_text(json.dumps(dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),page_count=len(doc),sheets=sheets,pages=records,inspection='pending',scope='layout overview at350x500 maximum per page; not full-resolution text reading'),indent=2)+'\n')
print(json.dumps(dict(pages=len(doc),sheets=len(sheets))))
