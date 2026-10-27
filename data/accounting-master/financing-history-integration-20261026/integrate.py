"""Protected Version 5.16 integration; bounded deterministic build and checks."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-term-execution-v515-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-financing-history-v516-20261026'
BASE='6975385b9bbf994bbc5f171d8f9095c47b493cef81d68e4bcb901bd072fd57ec'
STANDALONE='63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'
NEW='sections/selected-financing-history.tex';BS=chr(92)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(n,x):(HERE/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        old='Version 5.15 (proposal candidate)';assert text.count(old)==1
        return text.replace(old,'Version 5.16 (proposal candidate)',1)
    if name=='sections/common-program-authoring.tex':
        old=BS+'input{sections/selected-term-execution}';assert text.count(old)==1
        return text.replace(old,old+chr(10)*2+BS+'input{sections/selected-financing-history}',1)
    if name=='chapters/06-language.tex':
        old='separate requirements for actual-source and accounting admission.';assert text.count(old)==1
        added='Financing requires the same distinction between a consistent snapshot and a'+chr(10)+'''faithful history. Section~'''+BS+'''ref{sec:selected-financing-history} preserves
missed-payment and share memory through settlement, separates conditional
remedies from economic effects, and rejects clause findings made stale by a
same-day payment.'''
        return text.replace(old,old+chr(10)+added,1)
    return text
def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists(),'already_prepared'
    assert sha(SOURCE/'accounting-product-proposal.pdf')==sha(ROOT/'docs/AccDSL-latest.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    assert len(sources)==236
    evidence={}
    units=[('financing-opening-invariants-20261026','attempt-02',283),
           ('financing-remedy-binding-20261026','attempt-01',310),
           ('financing-remedy-state-binding-20261026','attempt-01',332)]
    for name,attempt,count in units:
        unit=HERE.parent/name;checks=read(unit/attempt/'checks.json')
        assert checks['passed'] and checks['assertions']==count
        for n,h in read(unit/attempt/'source-lock.json').items():
            assert sha(ROOT/n)==h,n
            if n in evidence:assert evidence[n]==h,n
            evidence[n]=h
        for folder in [unit,unit/attempt]:
            for p in folder.iterdir():
                if p.is_file() and p.suffix in ('.py','.md','.json'):
                    evidence[str(p.relative_to(ROOT))]=sha(p)
    assert read(HERE.parent/'financing-remedy-binding-20261026/same-day-discriminator.json')['discriminator_confirmed']
    for name in sources:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
    (TARGET/NEW).write_bytes((HERE/Path(NEW).name).read_bytes())
    controls=list(read(HERE.parent/'term-execution-integration-20261026/control-input-hashes.json'))
    dump('control-input-hashes.json',{n:sha(ROOT/n) for n in controls})
    dump('source-preservation.json',dict(source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),
      source_pdf_sha256=BASE,standalone_pdf_sha256=STANDALONE,sources=sources,evidence=evidence,
      added_source=NEW,added_source_sha256=sha(HERE/Path(NEW).name)))
    print(json.dumps(dict(protected_sources=len(sources),protected_evidence=len(evidence),candidate='5.16')))
def build():
    assert not (HERE/'build.json').exists(),'build_already_recorded'
    started=time.monotonic();env=dict(TEXMFVAR='/tmp/accdsl-bank-profile-tex-cache',TEXMFCACHE='/tmp/accdsl-bank-profile-tex-cache',CUDA_VISIBLE_DEVICES='-1')
    cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    with (HERE/'build.log').open('w') as log:
        r=subprocess.run(cmd,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
    pdf=TARGET/'accounting-product-proposal.pdf'
    dump('build.json',dict(command=cmd,cwd=str(TARGET),environment=env,returncode=r.returncode,wall_seconds=time.monotonic()-started,
                         pdf_sha256=sha(pdf) if pdf.exists() else None))
    print(json.dumps(dict(returncode=r.returncode)));raise SystemExit(r.returncode)
def verify():
    import fitz
    assert not (HERE/'verification.json').exists(),'verification_already_recorded'
    p=read(HERE/'source-preservation.json')
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    for n,h in p['sources'].items():
        assert sha(SOURCE/n)==h,n
        assert (TARGET/n).read_text()==expected(n,(SOURCE/n).read_text()),n
    assert sha(TARGET/NEW)==p['added_source_sha256']
    for n,h in p['evidence'].items():assert sha(ROOT/n)==h,n
    actual={f.relative_to(TARGET).as_posix() for f in TARGET.rglob('*') if f.is_file() and f.suffix in ('.tex','.bib','.lark')}
    assert actual==set(p['sources'])|{NEW}
    reachable=set()
    def visit(n):
        assert n not in reachable,n;reachable.add(n)
        for child in re.findall(re.escape(BS)+r'(?:input|include)\{([^}]+)}',(TARGET/n).read_text()):
            visit(child if child.endswith('.tex') else child+'.tex')
    visit('accounting-product-proposal.tex')
    text=chr(10).join((TARGET/n).read_text() for n in reachable)
    labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
    refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)\{([^}]+)}',text))
    assert all(n==1 for n in labels.values()) and refs<=set(labels)
    def warnings(path):
        return Counter(line for line in path.read_text(errors='replace').splitlines() if any(x in line for x in
         ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    old=warnings(SOURCE/'accounting-product-proposal.log');new=warnings(TARGET/'accounting-product-proposal.log')
    pdf=TARGET/'accounting-product-proposal.pdf';build_result=read(HERE/'build.json')
    assert build_result['returncode']==0 and sha(pdf)==build_result['pdf_sha256']
    doc=fitz.open(pdf);assert 'Version 5.16' in doc[0].get_text();texts=[' '.join(page.get_text().split()) for page in doc]
    chapter=next(i+1 for i,s in enumerate(texts) if 'Financing requires the same distinction' in s)
    start=next(i+1 for i,s in enumerate(texts) if 'Preserve payment history when financing and remedies change' in s)
    end=next(i+1 for i,s in enumerate(texts) if 'financing-remedy-state-binding-20261026/' in s)
    pages=sorted({1,chapter,*range(max(1,start-1),min(len(doc),end+1)+1)})
    for number in pages:
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'page-{number}.png')
        (HERE/f'page-{number}.txt').write_text(doc[number-1].get_text())
    bounds=[i+1 for i,page in enumerate(doc) if any(min(b[0],b[1]) < -1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1 for b in page.get_text('blocks'))]
    result=dict(passed_preservation=True,version='5.16',pages=len(doc),pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),
      protected_source_files=len(p['sources']),changed_sources=[n for n,h in p['sources'].items() if sha(TARGET/n)!=h],added_source=NEW,
      protected_evidence_files=len(p['evidence']),new_warnings=dict(new-old),inherited_warnings=dict(old),out_of_page_text_blocks=bounds,
      review_pages=pages,new_section_pages=[start,end],language_chapter_page=chapter,standalone_pdf_unchanged=True,readiness='not_ready')
    dump('verification.json',result);print(json.dumps(result));assert not (new-old) and not bounds
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
