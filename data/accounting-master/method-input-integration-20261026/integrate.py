from collections import Counter
from hashlib import sha256
import json,os,re,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-credit-cash-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-method-input-20261026'
BASE='f09b83354c8384f3b75105a29c25bfc7db1ebd62193227dc478abd1424d0c1b7'
SECTION='sections/native-requirement-link.tex';BS=chr(92);NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+NL)
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 4.42 (proposal candidate)')==1
        return text.replace('Version 4.42 (proposal candidate)','Version 4.43 (proposal candidate)')
    if name=='sections/requirement-successors.tex':
        return text+NL+BS+'input{sections/native-requirement-link}'+NL
    return text
def prepare():
    import fitz
    assert not TARGET.exists() and not (HERE/'baseline.json').exists()
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources)==176
    for name in sources:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
    (TARGET/SECTION).write_bytes((HERE/'native-requirement-link.tex').read_bytes())
    evidence=ROOT/'data/accounting-master/common-method-input-boundary-20261026'
    dump(HERE/'baseline.json',{'source':str(SOURCE.relative_to(ROOT)),'sources':sources,'pdf_sha256':BASE,
        'added_section_sha256':sha(HERE/'native-requirement-link.tex'),'evidence':{str(p.relative_to(ROOT)):sha(p) for p in [evidence/'result.md',evidence/'checks.json',evidence/'run-manifest.json']}})
    doc=fitz.open(SOURCE/'accounting-product-proposal.pdf');pages=[i+1 for i,p in enumerate(doc) if 'Collection membership, identity order' in ' '.join(p.get_text().split())]
    for n in pages:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save(HERE/f'baseline-page-{n}.png')
    print(json.dumps({'prepared_sources':len(sources),'baseline_pages':pages}))
def build():
    assert not (HERE/'build.json').exists()
    cache='/tmp/accdsl-method-input-20261026-tex-cache';Path(cache).mkdir(parents=True,exist_ok=True)
    env={'TEXMFVAR':cache,'TEXMFCACHE':cache,'CUDA_VISIBLE_DEVICES':'-1'}
    command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex'];start=time.monotonic()
    with (HERE/'build.log').open('w') as log:r=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=240)
    pdf=TARGET/'accounting-product-proposal.pdf';dump(HERE/'build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,'returncode':r.returncode,'pdf_sha256':sha(pdf) if pdf.exists() else None})
    print(json.dumps({'returncode':r.returncode}));raise SystemExit(r.returncode)
def verify():
    import fitz
    baseline=json.loads((HERE/'baseline.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    for n,h in baseline['sources'].items():assert sha(SOURCE/n)==h and (TARGET/n).read_text()==expected(n,(SOURCE/n).read_text()),n
    for n,h in baseline['evidence'].items():assert sha(ROOT/n)==h,n
    assert sha(TARGET/SECTION)==baseline['added_section_sha256']
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert actual==set(baseline['sources'])|{SECTION}
    combined=NL.join((TARGET/n).read_text() for n in actual if n.endswith('.tex'))
    labels=Counter(re.findall(re.escape(BS+'label{')+'([^}]+)}',combined))
    refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)'+re.escape('{')+'([^}]+)}',combined))
    assert all(v==1 for v in labels.values()) and refs<=set(labels)
    def warnings(p):return Counter(line for line in p.read_text(errors='replace').splitlines() if any(s in line for s in ['Warning','Overfull','Underfull','Undefined','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    old=warnings(SOURCE/'accounting-product-proposal.log');new=warnings(TARGET/'accounting-product-proposal.log');delta=new-old
    build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0
    pdf=TARGET/'accounting-product-proposal.pdf';assert sha(pdf)==build['pdf_sha256'];doc=fitz.open(pdf);assert 'Version 4.43' in doc[0].get_text()
    starts=[i for i,p in enumerate(doc) if 'A passing requirement still needs the intended native request' in ' '.join(p.get_text().split())]
    ends=[i for i,p in enumerate(doc) if 'common-method-input-boundary-20261026/' in ''.join(p.get_text().split())]
    assert len(starts)==len(ends)==1,(starts,ends);pages=sorted({1,*range(starts[0],ends[0]+3)})
    for n in pages:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'page-{n}.png')
    result={'passed_preservation':True,'version':'4.43','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
        'protected_source_files':len(baseline['sources']),'added_source_files':1,'new_warnings':dict(delta),'inherited_warnings':dict(old),'review_pages':pages,'readiness':'not_ready'}
    dump(HERE/'verification.json',result);print(json.dumps(result));assert not delta,'new warning requires inspection'
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
