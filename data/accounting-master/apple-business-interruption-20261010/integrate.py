"""Bounded manuscript integration; all published unit artifacts stay immutable."""
from pathlib import Path
from datetime import datetime, timezone
import difflib, hashlib, importlib.util, json, os, re, shutil, sys, time
import fitz
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT/'docs/design/proposal/manuscript-regulation-20261010'
NEW = ROOT/'docs/design/proposal/manuscript-disruption-20261010'
TITLE = 'Demand, disruption and recovery follow different paths'
HELPER = ROOT/'data/accounting-master/apple-legal-20261010/work_unit.py'
spec = importlib.util.spec_from_file_location('document_helpers', HELPER)
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
w.OUT, w.OLD, w.NEW = OUT, OLD, NEW
sha, read, rel, save = w.sha, w.read, w.rel, w.save


def setup():
    base = read(OUT/'baseline.json'); m = read(ROOT/base['prior_manifest'])
    w.verify(m['artifact_hashes'])
    assert m['pdf']['path'] == rel(OLD/'accounting-product-proposal.pdf')
    assert sha(OLD/'accounting-product-proposal.pdf') == m['pdf']['sha256']
    protected = {rel(p):sha(p) for p in OLD.rglob('*') if p.is_file()}
    save('integration-baseline.json', dict(protected_hashes=protected,
        helper_sha256=sha(HELPER), baseline_pdf=m['pdf'],
        inspection_manifest=rel(OUT/'inspection/manifest.json'),
        inspection_sha256=sha(OUT/'inspection/manifest.json')))
    w.copy()


def render():
    pdf=NEW/'accounting-product-proposal.pdf'; doc=fitz.open(pdf)
    start=max(i+1 for i,p in enumerate(doc) if TITLE in ' '.join(p.get_text().split()))
    end=next(i+1 for i in range(start,len(doc)) if 'Representing a company’s historical record' in ' '.join(doc[i].get_text().split()))
    body=list(range(start-1,end+1)); assert len(body)<=6
    nav=list(range(1,8)); images=w.render(pdf,sorted(set(body+nav)),OUT/'render')
    sheet=Image.new('RGB',(1000,710),'white'); draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(nav):
        im=Image.open(OUT/'render'/f'page-{n:03}.png'); im.thumbnail((244,327))
        x=i%4*250; y=i//4*355; sheet.paste(im,(x,y+20)); draw.text((x+8,y+3),str(n),fill='black')
    p=OUT/'render/navigation.png'; sheet.save(p)
    save('render-manifest.json',dict(pdf=dict(path=rel(pdf),sha256=sha(pdf),pages=len(doc)),
        body_pages=body,navigation_pages=nav,images=images,navigation_sheet=dict(path=rel(p),sha256=sha(p))))
    print(json.dumps(dict(pages=len(doc),body_pages=body,pdf_sha256=sha(pdf))))


def check():
    checks=[]; inputs={}; ck=lambda n,ok:checks.append(dict(id=n,passed=bool(ok)))
    old={p.relative_to(OLD):p for p in OLD.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
    new={p.relative_to(NEW):p for p in NEW.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
    changed=[]; delta=[]
    for n,p in new.items():
        a=old[n].read_text() if n in old else ''; b=p.read_text(); inputs[rel(p)]=sha(p)
        if a!=b:
            changed.append(str(n)); delta.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n),tofile=str(NEW/n)))
    ck('all inherited sources retained',old.keys()<=new.keys())
    ck('bounded substantive delta',set(changed)=={'accounting-product-proposal.tex','chapters/13-reference-company.tex','sections/apple-disruption.tex'})
    ck('inherited chapter content intact',(NEW/'chapters/13-reference-company.tex').read_text()==(OLD/'chapters/13-reference-company.tex').read_text()+'\\input{sections/apple-disruption}\n')
    ck('version-only title change',(NEW/'accounting-product-proposal.tex').read_text().replace('Version 2.20','Version 2.19')==(OLD/'accounting-product-proposal.tex').read_text())
    a='\n'.join(p.read_text() for p in old.values() if p.suffix=='.tex')
    b='\n'.join(p.read_text() for p in new.values() if p.suffix=='.tex')
    displays=lambda s:re.findall(r'\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|displaymath)\}',s,re.S)
    ck('48 displays exactly preserved',len(displays(a))==48 and sorted(displays(a))==sorted(displays(b)))
    bib=(NEW/'references.bib').read_text();keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    ck('66 bibliography entries unchanged',bib==(OLD/'references.bib').read_text() and len(keys)==66)
    cites=lambda s:{k.strip() for q in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',s) for k in q.split(',')}
    ck('citations retained and resolved',cites(a)<=cites(b)<=set(keys))
    labels=re.findall(r'\\label\{([^}]+)\}',b); refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
    ck('unique labels resolved',len(labels)==len(set(labels)) and set(refs)<=set(labels))
    ck('clean final build log',not any(x in (NEW/'accounting-product-proposal.log').read_text() for x in ['Warning','Overfull','Underfull','! ']))
    ck('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
    r=read(OUT/'render-manifest.json'); ck('PDF hash bound',sha(NEW/'accounting-product-proposal.pdf')==r['pdf']['sha256'])
    w.verify({i['path']:i['sha256'] for i in r['images']+[r['navigation_sheet']]})
    s=read(OUT/'source-checks.json')
    reloc={x['historical_path']:x['preserved_path'] for x in read(OUT/'input-relocations.json')['relocations']}
    w.verify({reloc.get(x['path'],x['path']):x['sha256'] for x in s['inputs']})
    ck('source checker current and passing',s['failed']==0 and s['checker_sha256']==sha(OUT/'prepare.py'))
    evidence=read(OUT/'meaning-checks.json');ck('original text and meaning checks passing',evidence['failed']==0);w.verify(evidence['inputs'])
    w.verify(read(OUT/'integration-baseline.json')['protected_hashes'])
    w.ancestry()
    ck('baseline preserved',True)
    review=(OUT/'author-review.md').read_text();ck('review bound with independent pending',r['pdf']['sha256'] in review and 'independent_reader_pending' in review)
    ck('body and adjacent pages inspected',all(str(n) in review for n in r['body_pages']))
    for name in ['source-checks.json','source-claim-supplement.json','meaning-checks.json','claim-query-ledger.json','render-manifest.json','author-review.md','surface-audit.json','surface-body.json','surface-disposition.md','corrections-to-prior-notes.md']:
        inputs[rel(OUT/name)]=sha(OUT/name)
    (OUT/'manuscript-delta.diff').write_text(''.join(delta))
    save('candidate-checks.json',dict(checker_sha256=sha(Path(__file__)),inputs=inputs,checks=checks,passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks),pdf=r['pdf'],changed_sources=changed))
    print(json.dumps(dict(passed=sum(x['passed'] for x in checks),failed=sum(not x['passed'] for x in checks))))
    assert all(x['passed'] for x in checks),[x for x in checks if not x['passed']]


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    start=time.monotonic();started=datetime.now(timezone.utc);code=0;action=sys.argv[1]
    try: {'setup':setup,'build':w.build,'render':render,'check':check}[action]()
    except BaseException:code=1;raise
    finally:
        with (OUT/'commands.jsonl').open('a') as f:f.write(json.dumps(dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__))+' '+action,started_at=started.isoformat(),wall_seconds=time.monotonic()-start,exit_code=code))+'\n')
