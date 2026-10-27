"""Protected manuscript addition; never reruns scientific evidence."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-vintage-carry-v518-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-decision-conversion-v519-20261026'
BASE='9a4946d45154eb4c17c67947d532a159438281a4e8701ab1402f4c4008c86e84'
STANDALONE='c00f30aa48e231e960b9852ed84a01c7fd95590d29d9e3855352a40d5d9ce654'
BS=chr(92)
NEW={n:'simulation/'+n for n in ('actor-decision.tex','conversion-book.tex','control-price.tex')}
APPENDS={'simulation/inference-vintage.tex':'actor-decision','simulation/financing-carry.tex':'conversion-book','simulation/14-refinancing-case.tex':'control-price'}
MARKERS=['A correction reaches different decision makers at different times','Conversion changes a claim and the people who control it','The price must anticipate who chooses after conversion']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):(HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def read(path):return json.loads(path.read_text())


def expected(name,source):
    if name=='accounting-product-proposal.tex':
        assert source.count('Version 5.18 (proposal candidate)')==1
        return source.replace('Version 5.18 (proposal candidate)','Version 5.19 (proposal candidate)')
    if name=='simulation-foundations.tex':
        assert source.count('Version 5.18 research companion')==1
        return source.replace('Version 5.18 research companion','Version 5.19 research companion')
    if name in APPENDS:return source+'\n'+BS+'input{simulation/'+APPENDS[name]+'}\n'
    return source


def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
    assert sha(ROOT/'docs/AccDSL-latest.pdf')==BASE and sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    evidence={}
    for unit in ('two-date-financing-control-20261026','conversion-rights-bridge-20261026','vintage-decision-20261026'):
        folder=HERE.parent/unit
        for path in folder.rglob('*'):
            if path.is_file() and path.suffix in ('.py','.md','.json'):
                evidence[str(path.relative_to(ROOT))]=sha(path)
    for name in sources:
        path=TARGET/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(expected(name,(SOURCE/name).read_text()))
    for name,dest in NEW.items():(TARGET/dest).write_bytes((HERE/name).read_bytes())
    save('source-preservation.json',dict(source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),sources=sources,evidence=evidence,
         added={dest:sha(HERE/name) for name,dest in NEW.items()},named_edits=['accounting-product-proposal.tex','simulation-foundations.tex',*APPENDS]))
    print(json.dumps(dict(prepared=True,protected_sources=len(sources),protected_evidence=len(evidence))))


def build(attempt):
    assert attempt in ('build-attempt-01','build-attempt-02')
    output=HERE/attempt;output.mkdir(exist_ok=False)
    env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    reports=[]
    for base in ('accounting-product-proposal','simulation-foundations'):
        command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',base+'.tex']
        start=time.monotonic()
        with (output/(base+'.stdout.log')).open('w') as log:
            result=subprocess.run(command,cwd=TARGET,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        for ext in ('.log','.pdf'):
            path=TARGET/(base+ext)
            if path.exists():(output/(base+ext)).write_bytes(path.read_bytes())
        reports.append(dict(document=base,command=command,returncode=result.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=sha(TARGET/(base+'.pdf')) if (TARGET/(base+'.pdf')).exists() else None))
        save(attempt+'/manifest.json',dict(results=reports,environment={k:env[k] for k in ('TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES')},cwd=str(TARGET),
             git_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
             plan='docs/plans/accounting-decision-conversion-integration-20261026.md',seed='N/A document build',data='source-preservation.json'))
        print(json.dumps(reports[-1]),flush=True)
        if result.returncode:raise SystemExit(result.returncode)


def verify():
    import fitz
    assert not (HERE/'verification.json').exists()
    lock=read(HERE/'source-preservation.json');checks=[]
    def ck(name,ok):
        checks.append(dict(id=name,passed=bool(ok)))
        if not ok:
            save('verification-failed.json',dict(checks=checks));raise AssertionError(name)
    ck('main_baseline',sha(SOURCE/'accounting-product-proposal.pdf')==BASE)
    ck('standalone_baseline',sha(SOURCE/'simulation-foundations.pdf')==STANDALONE)
    for name,digest in lock['sources'].items():
        ck('source.'+name,sha(SOURCE/name)==digest)
        ck('successor.'+name,(TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()))
    for name,digest in lock['evidence'].items():ck('evidence.'+name,sha(ROOT/name)==digest)
    for name,digest in lock['added'].items():ck('added.'+name,sha(TARGET/name)==digest)
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    ck('source_set',actual==set(lock['sources'])|set(lock['added']))
    bibkeys=set(re.findall(r'@\w+\{([^,]+),',(TARGET/'references.bib').read_text()))
    def warnings(path):return Counter(line for line in path.read_text(errors='replace').splitlines() if any(x in line for x in ('Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error')) or line.startswith('!'))
    documents=[]
    for base in ('accounting-product-proposal','simulation-foundations'):
        reachable=set()
        def visit(name):
            ck(base+'.unique_include.'+name,name not in reachable);reachable.add(name)
            for child in re.findall(re.escape(BS)+r'(?:input|include){([^}]+)}',(TARGET/name).read_text()):visit(child if child.endswith('.tex') else child+'.tex')
        visit(base+'.tex');text='\n'.join((TARGET/n).read_text() for n in reachable)
        labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
        refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref){([^}]+)}',text))
        cites=set()
        for group in re.findall(re.escape(BS)+r'citew**?(?:[[^]]*])*{([^}]+)}',text):cites.update(x.strip() for x in group.split(','))
        ck(base+'.labels',all(x==1 for x in labels.values()) and refs<=set(labels));ck(base+'.citations',cites<=bibkeys)
        new=warnings(TARGET/(base+'.log'))-warnings(SOURCE/(base+'.log'))
        doc=fitz.open(TARGET/(base+'.pdf'));texts=[' '.join(page.get_text().split()) for page in doc]
        ck(base+'.cover','Version 5.19' in texts[0])
        clipping=[i+1 for i,page in enumerate(doc) if any(min(b[0],b[1])<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1 for b in page.get_text('blocks'))]
        sections=[];pages={1}
        for marker in MARKERS:
            found=[i+1 for i,t in enumerate(texts) if marker in t and len(t)>1000]
            ck(base+'.marker.'+marker,bool(found))
            start=found[-1];end=min(len(doc),start+3);pages.update(range(max(1,start-1),end+1));sections.append(dict(title=marker,start=start,end=end))
        render=HERE/('render-'+base);render.mkdir(exist_ok=True)
        for page in sorted(pages):doc[page-1].get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(render/('page-'+str(page)+'.png'))
        documents.append(dict(document=base,pages=len(doc),pdf=str((TARGET/(base+'.pdf')).relative_to(ROOT)),sha256=sha(TARGET/(base+'.pdf')),
                              new_warnings=dict(new),out_of_page_text_blocks=clipping,sections=sections,rendered_pages=sorted(pages)))
        save('document-checks.json',documents)
        ck(base+'.warnings',not new);ck(base+'.clipping',not clipping)
    save('verification.json',dict(status='PASS',checks=checks,count=len(checks),documents=documents,protected_sources=len(lock['sources']),protected_evidence=len(lock['evidence']),readiness='independent_reader_pending'))
    print(json.dumps(dict(status='PASS',checks=len(checks),documents=documents)))


if __name__=='__main__':
    if sys.argv[1]=='build':build(sys.argv[2])
    else:{'prepare':prepare,'verify':verify}[sys.argv[1]]()
