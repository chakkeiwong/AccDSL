"""Preserved dual-edition integration of checked settlement/inference arguments."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json, re, os, subprocess, sys, time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-financing-history-v516-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-financing-inference-v517-20261026'
BASE='e963959f28aaed8deb5c6894b480e97ccbaf04eccca92b5dea10098fb44cd966'
STANDALONE='63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'
BS=chr(92)
NEW={n:'simulation/'+n for n in ['settlement-remedies.tex','remedy-freshness.tex','inference-exchange.tex']}
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,obj):(HERE/n).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+chr(10))
def expected(name,s):
    if name=='accounting-product-proposal.tex':
        assert s.count('Version 5.16 (proposal candidate)')==1
        return s.replace('Version 5.16 (proposal candidate)','Version 5.17 (proposal candidate)')
    if name=='simulation-foundations.tex':
        assert s.count('Version 5.12 research companion')==1
        return s.replace('Version 5.12 research companion','Version 5.17 research companion')
    inserts={'simulation/03-learning.tex':('A proposed information service','inference-exchange'),
             'simulation/05-debt.tex':('Implementation proposal','settlement-remedies'),
             'simulation/07-events.tex':('Reporting frequency and event frequency','remedy-freshness')}
    if name in inserts:
        heading,leaf=inserts[name];anchor=BS+'section{'+heading+'}'
        assert s.count(anchor)==1
        return s.replace(anchor,BS+'input{simulation/'+leaf+'}'+chr(10)*2+anchor)
    if name=='references.bib':
        assert 'particlesgap2026' not in s
        return s+chr(10)+'''@misc{particlesgap2026,
 author={Chopin, Nicolas and contributors},
 title={particles: Sequential Monte Carlo in Python, pinned source},
 year={2026},
 howpublished={Author-linked source repository},
 url={https://github.com/nchopin/particles/blob/3388c4bd30ab9acc5a27c970089230f93610b627/particles/smc_samplers.py},
 note={Commit 3388c4bd30ab9acc5a27c970089230f93610b627; inspected SMC2 exchange, ArrayMetropolis, ThetaParticles and FancyList; static audit only}
}
'''
    return s
def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-latest.pdf')==BASE
    assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==STANDALONE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*')
             if p.is_file() and p.suffix in ('.tex','.bib','.lark')}
    evidence={}
    for rel in ['gap-program-20261026','financing-opening-invariants-20261026/attempt-02',
                'financing-remedy-binding-20261026','financing-remedy-freshness-20261026']:
        folder=HERE.parent/rel
        # Only evidence in these explicit units; retain complete result hashes.
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ('.json','.md','.py'):
                evidence[str(p.relative_to(ROOT))]=sha(p)
    for rel in ['financing-opening-invariants-20261026/attempt-02/source-lock.json',
                'financing-remedy-freshness-20261026/attempt-02/source-lock.json']:
        for n,h in read(HERE.parent/rel).items():
            assert sha(ROOT/n)==h,n
            evidence[n]=h
    for p in (HERE.parent/'financing-remedy-freshness-20261026/attempt-02').iterdir():
        if p.is_file():evidence[str(p.relative_to(ROOT))]=sha(p)
    for n,h in read(HERE.parent/'gap-program-20261026/smc2-run-manifest.json')['source_sha256'].items():
        assert sha(ROOT/n)==h,n;evidence[n]=h
    contract=read(HERE.parent/'gap-program-20261026/contract-run-manifest.json')
    for n,h in contract['source_sha256'].items():
        assert sha(ROOT/n)==h,n;evidence[n]=h
    assert read(HERE.parent/'financing-remedy-freshness-20261026/attempt-02/checks.json')['assertions']==357
    for name in sources:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(expected(name,(SOURCE/name).read_text()))
    for n,dst in NEW.items():(TARGET/dst).write_bytes((HERE/n).read_bytes())
    save('source-preservation.json',dict(source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),
      source_pdf_sha256=BASE,standalone_pdf_sha256=STANDALONE,sources=sources,evidence=evidence,
      added={dst:sha(HERE/n) for n,dst in NEW.items()}))
    print(json.dumps(dict(prepared=True,source_files=len(sources),evidence_files=len(evidence))))
def build():
    out=HERE/'build-attempt-01';assert not out.exists();out.mkdir()
    env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache',
         'TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    results=[]
    for base in ['accounting-product-proposal','simulation-foundations']:
        cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',base+'.tex']
        start=time.monotonic()
        with (out/(base+'.build.log')).open('w') as log:
            r=subprocess.run(cmd,cwd=TARGET,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        results.append(dict(document=base,command=cmd,returncode=r.returncode,wall_seconds=time.monotonic()-start,
          pdf_sha256=sha(TARGET/(base+'.pdf')) if (TARGET/(base+'.pdf')).exists() else None))
        save('build.json',dict(attempt='build-attempt-01',results=results,cpu_gpu='CPU; GPU intentionally hidden',
          cwd=str(TARGET),environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']}))
        print(json.dumps(results[-1]),flush=True)
        if r.returncode:raise SystemExit(r.returncode)
def verify():
    import fitz
    p=read(HERE/'source-preservation.json');checks=[]
    def ck(n,ok):
        checks.append(dict(id=n,passed=bool(ok)))
        assert ok,n
    ck('main_baseline',sha(SOURCE/'accounting-product-proposal.pdf')==BASE)
    old_sim=ROOT/'docs/design/proposal/manuscript-literature-methods-v512-20261026/simulation-foundations.pdf'
    ck('standalone_baseline',sha(old_sim)==STANDALONE)
    for n,h in p['sources'].items():
        ck('source.'+n,sha(SOURCE/n)==h)
        ck('successor.'+n,(TARGET/n).read_text()==expected(n,(SOURCE/n).read_text()))
    for n,h in p['evidence'].items():ck('evidence.'+n,sha(ROOT/n)==h)
    for n,h in p['added'].items():ck('addition.'+n,sha(TARGET/n)==h==sha(HERE/Path(n).name))
    actual={f.relative_to(TARGET).as_posix() for f in TARGET.rglob('*') if f.is_file() and f.suffix in ('.tex','.bib','.lark')}
    ck('exact_source_set',actual==set(p['sources'])|set(p['added']))
    bibkeys=set(re.findall(r'@\w+\{([^,]+),',(TARGET/'references.bib').read_text()))
    def warnings(file):
        return Counter(line for line in file.read_text(errors='replace').splitlines()
          if any(x in line for x in ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    reports=[]
    for base in ['accounting-product-proposal','simulation-foundations']:
        reachable=set()
        def visit(name):
            ck(base+'.single_include.'+name,name not in reachable);reachable.add(name)
            for child in re.findall(re.escape(BS)+r'(?:input|include)\{([^}]+)}',(TARGET/name).read_text()):
                visit(child if child.endswith('.tex') else child+'.tex')
        visit(base+'.tex')
        content=chr(10).join((TARGET/n).read_text() for n in reachable)
        labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',content))
        refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)\{([^}]+)}',content))
        cited=set()
        for group in re.findall(re.escape(BS)+r'cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)}',content):cited.update(x.strip() for x in group.split(','))
        ck(base+'.labels',all(x==1 for x in labels.values()) and refs<=set(labels))
        ck(base+'.citations',cited<=bibkeys)
        oldlog=SOURCE/(base+'.log') if base=='accounting-product-proposal' else old_sim.with_suffix('.log')
        old=warnings(oldlog);new=warnings(TARGET/(base+'.log'))
        delta=new-old
        pdf=TARGET/(base+'.pdf');doc=fitz.open(pdf)
        texts=[' '.join(page.get_text().split()) for page in doc]
        ck(base+'.cover','Version 5.17' in texts[0])
        bounds=[i+1 for i,page in enumerate(doc) if any(min(b[0],b[1])<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1 for b in page.get_text('blocks'))]
        markers=['Changing particles without changing the target','Equal balances after unequal payment histories','A finding can become stale within one day']
        sections=[];pages={1}
        for marker in markers:
            found=[i+1 for i,t in enumerate(texts) if marker in t and len(t)>800]
            ck(base+'.found.'+marker,bool(found));start=found[-1]
            # Capture the full bounded additions plus the immediate continuation.
            end=min(len(doc),start+(6 if marker.startswith('Equal') else 4))
            sections.append(dict(title=marker,start=start,end=end));pages.update(range(max(1,start-1),end+1))
        output=HERE/('render-'+base);output.mkdir(exist_ok=True)
        for n in sorted(pages):
            doc[n-1].get_pixmap(matrix=fitz.Matrix(1.05,1.05)).save(output/('page-'+str(n)+'.png'))
            (output/('page-'+str(n)+'.txt')).write_text(doc[n-1].get_text())
        report=dict(document=base,pages=len(doc),pdf=str(pdf.relative_to(ROOT)),sha256=sha(pdf),
          new_warnings=dict(delta),inherited_warnings=dict(old),out_of_page_text_blocks=bounds,
          sections=sections,rendered_pages=sorted(pages),citations=len(cited),labels=len(labels))
        reports.append(report)
        save('verification.json',dict(status='in_progress',checks=checks,documents=reports))
        ck(base+'.no_new_warnings',not delta);ck(base+'.no_clipped_text',not bounds)
    save('verification.json',dict(status='PASS',checks=checks,count=len(checks),documents=reports,
      protected_sources=len(p['sources']),protected_evidence=len(p['evidence']),
      changed_sources=[n for n in p['sources'] if sha(TARGET/n)!=p['sources'][n]],
      readiness='not_ready; rendered human reading remains separate'))
    print(json.dumps(dict(status='PASS',checks=len(checks),documents=[{k:r[k] for k in ['document','pages','sha256','sections']} for r in reports])))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
