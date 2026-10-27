"""Prepare protected manuscript and source reading."""
from pathlib import Path
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
OLD=ROOT/'docs/design/proposal/manuscript-bank-commitment-draw-20261014'
NEW=ROOT/'docs/design/proposal/manuscript-insurance-connected-groups-20261014'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d): (OUT/n).write_text(json.dumps(d,indent=2)+'\n')
assert not NEW.exists()
sources=[p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']]
for p in sources:
 q=NEW/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
put('manuscript-baseline.json',{'baseline_pdf':str((OLD/'accounting-product-proposal.pdf').relative_to(ROOT)),'baseline_pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'candidate':str(NEW.relative_to(ROOT)),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sorted(sources)]})
p=NEW/'accounting-product-proposal.tex';p.write_text(p.read_text().replace('Version 2.82','Version 2.83'))
source=ROOT/'docs/design/research/standards/aasb17.pdf';txt=source.with_suffix('.txt')
pages=txt.read_text().split('\f'); starts=['14      ','16      ','22      ','25      ','32      ','38      ','40      ','44      ','47      ','50      ','52      ','60      ','65      ','66      ','78      ','81      ','86      ','88      ','B72     ','B119    ','B119C   ','B119F   ','B124    ']
selected=sorted({i+1 for i,t in enumerate(pages) if any(x in t for x in starts)}|{1})
(OUT/'selected-source-pages.txt').write_text('\n\n'.join('PHYSICAL PAGE '+str(i)+'\n'+pages[i-1] for i in selected))
put('source-manifest.json',{'source':str(source.relative_to(ROOT)),'sha256':sha(source),'text_sha256':sha(txt),'registration':'F2023C00382','version':'December 2022 compilation; private-sector annual starts [2023-01-01,2026-07-01)','url':'https://www.aasb.gov.au/admin/file/content105/c9/AASB17_07-17_COMPdec22_01-23.pdf','physical_pages_retained':selected,'inspected_anchors':['14–28','32–44','47–52','60–68','78–88','B72','B119–B125'],'scope':'Historical synthetic calendar 2024–2025 case, not current accounting advice. Retained primary source; online lookup returned no additional usable text.'})
print(json.dumps({'protected_sources':len(sources),'selected_source_pages':selected,'candidate':str(NEW.relative_to(ROOT))}))
