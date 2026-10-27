"""Preserve Version 5.14 while integrating the selected term-state and event design."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-nested-invariants-v514-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-term-execution-v515-20261026'
BASE='233f22f891ae2d0ded9c3aa7ef046b8f70c5f5cb6a8d9b3cd43c2a64b1424839'
STANDALONE='63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'
NEW='sections/selected-term-execution.tex';BS=chr(92)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+chr(10))
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        old='Version 5.14 (proposal candidate)';assert text.count(old)==1
        return text.replace(old,'Version 5.15 (proposal candidate)')
    if name=='sections/common-program-authoring.tex':
        old=BS+'input{sections/nested-term-invariants}';assert text.count(old)==1
        return text.replace(old,old+chr(10)+chr(10)+BS+'input{sections/selected-term-execution}')
    if name=='chapters/06-language.tex':
        old='Those checks preserve the separate need for structural admission and do not'+chr(10)+'yet replace the complete native opening or execution contract.'
        assert text.count(old)==1
        return text.replace(old,'Section~'+BS+'ref{sec:selected-term-execution} binds them to an explicit selected'+chr(10)+'state contract and direct source for prospective amendments, assessments,'+chr(10)+'collections and carry. This bounded synthetic continuation preserves the'+chr(10)+'separate requirements for actual-source and accounting admission.')
    if name=='sections/nested-term-invariants.tex':
        old='This difference identifies the remaining boundary rather than an alternative'+chr(10)+'''form of opening admission. Exact native structural schemas, role and cost
selection, and migration premises still need their own selected contract.
The bundle grants no execution or accounting admission and is not yet bound
into the opening-to-program execution path. Direct source authoring for these
nested profiles also remains to be supplied.'''
        assert text.count(old)==1
        return text.replace(old,'This difference identifies a separate structural condition rather than an'+chr(10)+'''alternative form of opening admission. The semantic bundle by itself grants
no execution or accounting admission. Section~'''+BS+'''ref{sec:selected-term-execution}
supplies the selected structural contract, direct nested source and bounded
event/carry composition while retaining actual-source and accounting limits.''')
    return text
def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists(),'already_prepared'
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-latest.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    assert len(sources)==235
    units={
      'term-structural-admission-20261026':('',61,681),
      'nested-contract-source-20261026':('attempt-01',16,4573),
      'nested-assessment-construction-20261026':('attempt-02',14,381),
      'term-event-carry-binding-20261026':('attempt-01',12,439),
      'term-full-event-binding-20261026':('attempt-01',19,548),
      'term-event-source-20261026':('attempt-01',9,1018)}
    evidence={}
    for unit_name,(attempt,controls,assertions) in units.items():
        unit=HERE.parent/unit_name;data=unit/attempt;checks=read(data/'checks.json')
        assert checks['passed'] and checks.get('controls',checks.get('source_controls'))==controls and checks['assertions']==assertions
        for n,h in read(data/'source-lock.json').items():
            assert sha(ROOT/n)==h,n
            if n in evidence:assert evidence[n]==h,n
            evidence[n]=h
        for path in list(unit.iterdir())+list(data.iterdir()):
            if path.is_file():evidence[str(path.relative_to(ROOT))]=sha(path)
    assert read(HERE.parent/'term-full-event-binding-20261026/date-boundary.json')['passed']
    for name in sources:
        path=TARGET/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(expected(name,(SOURCE/name).read_text()))
    (TARGET/NEW).write_bytes((HERE/'selected-term-execution.tex').read_bytes())
    controls=list(read(HERE.parent/'nested-invariant-integration-20261026/control-input-hashes.json'))
    dump('control-input-hashes.json',{n:sha(ROOT/n) for n in controls})
    dump('source-preservation.json',dict(source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),
      source_pdf_sha256=BASE,standalone_pdf_sha256=STANDALONE,sources=sources,evidence=evidence,
      added_source=NEW,added_source_sha256=sha(HERE/'selected-term-execution.tex')))
    print(json.dumps(dict(protected_sources=len(sources),protected_evidence=len(evidence),candidate='5.15')))
def build():
    assert not (HERE/'build.json').exists(),'build_already_recorded'
    started=time.monotonic();env={'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    with (HERE/'build.log').open('w') as log:
        result=subprocess.run(cmd,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
    pdf=TARGET/'accounting-product-proposal.pdf'
    dump('build.json',dict(command=cmd,cwd=str(TARGET),environment=env,returncode=result.returncode,
         wall_seconds=time.monotonic()-started,pdf_sha256=sha(pdf) if pdf.exists() else None))
    print(json.dumps(dict(returncode=result.returncode)));raise SystemExit(result.returncode)
def verify():
    import fitz
    preservation=read(HERE/'source-preservation.json')
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    for name,h in preservation['sources'].items():
        assert sha(SOURCE/name)==h,name
        assert (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),name
    assert sha(TARGET/NEW)==preservation['added_source_sha256']==sha(HERE/'selected-term-execution.tex')
    for name,h in preservation['evidence'].items():assert sha(ROOT/name)==h,name
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    assert actual==set(preservation['sources'])|{NEW}
    reachable=set()
    def visit(name):
        assert name not in reachable,name
        reachable.add(name)
        for child in re.findall(re.escape(BS)+r'(?:input|include)\{([^}]+)}',(TARGET/name).read_text()):
            visit(child if child.endswith('.tex') else child+'.tex')
    visit('accounting-product-proposal.tex')
    text=chr(10).join((TARGET/name).read_text() for name in reachable)
    labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
    refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)\{([^}]+)}',text))
    assert all(n==1 for n in labels.values()) and refs<=set(labels)
    def warnings(path):
        return Counter(line for line in path.read_text(errors='replace').splitlines() if any(x in line for x in
          ('Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error')) or line.startswith('!'))
    old=warnings(SOURCE/'accounting-product-proposal.log');new=warnings(TARGET/'accounting-product-proposal.log')
    pdf=TARGET/'accounting-product-proposal.pdf';build_result=read(HERE/'build.json')
    assert build_result['returncode']==0 and sha(pdf)==build_result['pdf_sha256']
    doc=fitz.open(pdf);assert 'Version 5.15' in doc[0].get_text()
    texts=[' '.join(page.get_text().split()) for page in doc]
    chapter=next(i+1 for i,s in enumerate(texts) if 'Nested term histories require a further distinction:' in s)
    start=next(i+1 for i,s in enumerate(texts) if 'Carry the historical terms through a complete command' in s)
    end=next(i+1 for i,s in enumerate(texts) if 'term-event-source-20261026/' in s)
    pages=sorted({1,chapter,*range(max(1,start-1),min(len(doc),end+1)+1)})
    for number in pages:
        doc[number-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'page-{number}.png')
        (HERE/f'page-{number}.txt').write_text(doc[number-1].get_text())
    bounds=[i+1 for i,page in enumerate(doc) if any(min(block[0],block[1]) < -1 or block[2] > page.rect.width+1 or block[3] > page.rect.height+1 for block in page.get_text('blocks'))]
    result=dict(passed_preservation=True,version='5.15',pages=len(doc),pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),
      protected_source_files=len(preservation['sources']),changed_sources=[n for n,h in preservation['sources'].items() if sha(TARGET/n)!=h],
      added_source=NEW,protected_evidence_files=len(preservation['evidence']),new_warnings=dict(new-old),inherited_warnings=dict(old),
      out_of_page_text_blocks=bounds,review_pages=pages,new_section_pages=[start,end],language_chapter_page=chapter,
      standalone_pdf_unchanged=True,readiness='not_ready')
    dump('verification.json',result);print(json.dumps(result))
    assert not (new-old) and not bounds
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
