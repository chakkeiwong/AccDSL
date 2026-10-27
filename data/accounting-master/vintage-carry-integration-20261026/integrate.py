"""Protected dual-edition integration; source/build checks, no evidence reruns."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-financing-inference-v517-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-vintage-carry-v518-20261026'
BASE='04a0b857b0ba44b00297213d4a20403750b074192ef9be2dd0ba870103440547'
STANDALONE='bfb670b8cbe4d0750feff263891ce953c919447e695963696b4f99ccadcb13f2'
BS=chr(92)
NEW={n:'simulation/'+n for n in ['inference-vintage.tex','financing-carry.tex']}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,x):(HERE/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def expected(name,s):
    if name=='accounting-product-proposal.tex':
        assert s.count('Version 5.17 (proposal candidate)')==1
        return s.replace('Version 5.17 (proposal candidate)','Version 5.18 (proposal candidate)')
    if name=='simulation-foundations.tex':
        assert s.count('Version 5.17 research companion')==1
        return s.replace('Version 5.17 research companion','Version 5.18 research companion')
    appends={'simulation/inference-exchange.tex':'inference-vintage','simulation/remedy-freshness.tex':'financing-carry'}
    if name in appends:return s+chr(10)+BS+'input{simulation/'+appends[name]+'}'+chr(10)
    return s
def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
    assert sha(ROOT/'docs/AccDSL-latest.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    evidence={}
    for unit,attempt in [('inference-vintage-20261026','attempt-02'),('financing-carry-freshness-20261026','attempt-01')]:
        folder=HERE.parent/unit
        for p in list(folder.glob('*.py'))+list(folder.glob('*.md'))+list((folder/attempt).iterdir()):
            if p.is_file():evidence[str(p.relative_to(ROOT))]=sha(p)
    assert read(HERE.parent/'inference-vintage-20261026/attempt-02/checks.json')['assertions']==311
    assert read(HERE.parent/'financing-carry-freshness-20261026/attempt-01/checks.json')['assertions']==406
    for n in sources:
        p=TARGET/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(n,(SOURCE/n).read_text()))
    for n,dest in NEW.items():(TARGET/dest).write_bytes((HERE/n).read_bytes())
    save('source-preservation.json',dict(source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),source_pdf_sha256=BASE,standalone_pdf_sha256=STANDALONE,sources=sources,evidence=evidence,added={dest:sha(HERE/n) for n,dest in NEW.items()}))
    print(json.dumps(dict(prepared=True,source_files=len(sources),evidence_files=len(evidence))))
def build():
    attempt=HERE/'build-attempt-02';assert not attempt.exists();attempt.mkdir()
    env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    reports=[]
    for base in ['accounting-product-proposal','simulation-foundations']:
        command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',base+'.tex']
        start=time.monotonic()
        with (attempt/(base+'.log')).open('w') as f:r=subprocess.run(command,cwd=TARGET,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
        reports.append(dict(document=base,command=command,returncode=r.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=sha(TARGET/(base+'.pdf')) if (TARGET/(base+'.pdf')).exists() else None))
        save('build.json',dict(results=reports,environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},cwd=str(TARGET)))
        print(json.dumps(reports[-1]),flush=True)
        if r.returncode:raise SystemExit(r.returncode)
def verify():
    import fitz
    lock=read(HERE/'source-preservation.json');checks=[]
    def ck(n,ok):
        checks.append(dict(id=n,passed=bool(ok)));assert ok,n
    ck('main_baseline',sha(SOURCE/'accounting-product-proposal.pdf')==BASE)
    ck('standalone_baseline',sha(SOURCE/'simulation-foundations.pdf')==STANDALONE)
    for n,h in lock['sources'].items():
        ck('source.'+n,sha(SOURCE/n)==h)
        ck('successor.'+n,(TARGET/n).read_text()==expected(n,(SOURCE/n).read_text()))
    for n,h in lock['evidence'].items():ck('evidence.'+n,sha(ROOT/n)==h)
    for n,h in lock['added'].items():ck('added.'+n,sha(TARGET/n)==h)
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    ck('source_set',actual==set(lock['sources'])|set(lock['added']))
    bibkeys=set(re.findall(r'@\w+\{([^,]+),',(TARGET/'references.bib').read_text()))
    def warnings(p):return Counter(l for l in p.read_text(errors='replace').splitlines() if any(w in l for w in ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or l.startswith('!'))
    reports=[]
    for base in ['accounting-product-proposal','simulation-foundations']:
        reachable=set()
        def visit(n):
            ck(base+'.single_include.'+n,n not in reachable);reachable.add(n)
            for child in re.findall(re.escape(BS)+r'(?:input|include){([^}]+)}',(TARGET/n).read_text()):visit(child if child.endswith('.tex') else child+'.tex')
        visit(base+'.tex')
        text=chr(10).join((TARGET/n).read_text() for n in reachable)
        labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
        refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref){([^}]+)}',text))
        cites=set()
        for group in re.findall(re.escape(BS)+r'cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)}',text):cites.update(x.strip() for x in group.split(','))
        ck(base+'.labels',all(x==1 for x in labels.values()) and refs<=set(labels))
        ck(base+'.citations',cites<=bibkeys)
        new=warnings(TARGET/(base+'.log'))-warnings(SOURCE/(base+'.log'))
        doc=fitz.open(TARGET/(base+'.pdf'));texts=[' '.join(p.get_text().split()) for p in doc]
        ck(base+'.cover','Version 5.18' in texts[0])
        outside=[i+1 for i,p in enumerate(doc) if any(min(b[0],b[1])<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1 for b in p.get_text('blocks'))]
        pages={1};sections=[]
        for marker in ['Replaying a declared evidence vintage','Closing a year without erasing a missed payment']:
            found=[i+1 for i,t in enumerate(texts) if marker in t and len(t)>800];ck(base+'.found.'+marker,bool(found))
            start=found[-1];end=min(len(doc),start+5);pages.update(range(max(1,start-1),end+1));sections.append(dict(title=marker,start=start,end=end))
        out=HERE/('render-'+base);out.mkdir(exist_ok=True)
        for page in sorted(pages):doc[page-1].get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(out/('page-'+str(page)+'.png'))
        report=dict(document=base,pages=len(doc),pdf=str((TARGET/(base+'.pdf')).relative_to(ROOT)),sha256=sha(TARGET/(base+'.pdf')),new_warnings=dict(new),out_of_page_text_blocks=outside,sections=sections,rendered_pages=sorted(pages),citations=len(cites),labels=len(labels))
        reports.append(report);save('verification.json',dict(status='in_progress',checks=checks,documents=reports))
        ck(base+'.no_new_warnings',not new);ck(base+'.no_clipping',not outside)
    save('verification.json',dict(status='PASS',checks=checks,count=len(checks),documents=reports,protected_sources=len(lock['sources']),protected_evidence=len(lock['evidence']),readiness='not_ready'))
    print(json.dumps(dict(status='PASS',checks=len(checks),documents=[{k:r[k] for k in ['document','pages','sha256','sections']} for r in reports])))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
