"""Preserved Version 5.5 main and standalone finite-aggregation integration."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import json
import os
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-adopted-profiles-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-observation-quotient-20261026'
STANDALONE=ROOT/'docs/design/proposal/manuscript-bank-exact-profile-20261026'
BASE='508be1d4f142b72f87f397288b7cd6898a873176d65d330ae61e316f59b6e19c'
BS=chr(92)
STEMS=('accounting-product-proposal','simulation-foundations')
ADDED='simulation/08a-finite-quotient.tex'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,v):(HERE/name).write_text(json.dumps(v,indent=2)+'\n')

def expected(name,text):
    if name=='accounting-product-proposal.tex':
        old='Version 5.4 (proposal candidate)';assert text.count(old)==1
        return text.replace(old,'Version 5.5 (proposal candidate)')
    if name=='simulation-foundations.tex':
        old='Version 5.0 research companion; provisional candidate';assert text.count(old)==1
        return text.replace(old,'Version 5.5 research companion; provisional candidate')
    if name=='simulation/08-compression.tex':
        old='This is sufficient, not necessary, and is not an implemented general checker.'
        new='This condition is sufficient, not necessary. The finite helper described next checks explicitly supplied finite models; it is not a general checker for arbitrary company-state representations.'
        assert text.count(old)==1
        text=text.replace(old,new)
        marker=BS+'section{Unweighted families require relational memory}'
        assert text.count(marker)==1
        return text.replace(marker,BS+'input{simulation/08a-finite-quotient}'+chr(10)*2+marker)
    return text

def prepare():
    assert not TARGET.exists() and not (HERE/'source-preservation.json').exists()
    assert sha(SOURCE/(STEMS[0]+'.pdf'))==BASE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources)==215
    unit=HERE.parent/'observation-quotient-20261026'
    checks=json.loads((unit/'checks.json').read_text())
    assert checks['passed'] and checks['checks']==166 and checks['complete_path_comparisons']==12
    evidence={str((unit/n).relative_to(ROOT)):sha(unit/n) for n in ['result.md','design.md','quotient.py','paths.py','fixtures.py','verify.py','checks.json','run-manifest.json','source-lock.json','cases.json','path-comparisons.json','negative-path-comparisons.json','controls.json','persistent-counterexample.json']}
    for n in sources:
        p=TARGET/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(n,(SOURCE/n).read_text()))
    (TARGET/ADDED).write_bytes((HERE/'finite-quotient.tex').read_bytes())
    dump('source-preservation.json',dict(sources=sources,source_pdf_sha256=BASE,source=str(SOURCE.relative_to(ROOT)),target=str(TARGET.relative_to(ROOT)),evidence=evidence,added_source=ADDED,new_section_sha256=sha(HERE/'finite-quotient.tex'),standalone_baseline_pdf=str((STANDALONE/(STEMS[1]+'.pdf')).relative_to(ROOT)),standalone_baseline_sha256=sha(STANDALONE/(STEMS[1]+'.pdf'))))
    print(json.dumps({'protected_sources':len(sources),'candidate':'5.5'}))

def build():
    assert not (HERE/'build.json').exists()
    builds={}
    env={'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'}
    for stem in STEMS:
        start=time.monotonic()
        command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',stem+'.tex']
        with (HERE/(stem+'-build.log')).open('w') as log:
            result=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=300)
        pdf=TARGET/(stem+'.pdf')
        builds[stem]=dict(command=command,cwd=str(TARGET),environment=env,returncode=result.returncode,wall_seconds=time.monotonic()-start,pdf_sha256=sha(pdf) if pdf.exists() else None)
        dump('build.json',builds)
        print(json.dumps({'document':stem,'returncode':result.returncode}),flush=True)
        if result.returncode:raise SystemExit(result.returncode)

def verify():
    import fitz
    preservation=json.loads((HERE/'source-preservation.json').read_text())
    assert sha(SOURCE/(STEMS[0]+'.pdf'))==BASE
    assert sha(ROOT/preservation['standalone_baseline_pdf'])==preservation['standalone_baseline_sha256']
    for n,h in preservation['sources'].items():
        assert sha(SOURCE/n)==h,n
        assert (TARGET/n).read_text()==expected(n,(SOURCE/n).read_text()),n
    for n,h in preservation['evidence'].items(): assert sha(ROOT/n)==h,n
    assert sha(TARGET/ADDED)==preservation['new_section_sha256']
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert actual==set(preservation['sources'])|{ADDED}
    def warnings(path):
        return Counter(line for line in path.read_text(errors='replace').splitlines() if any(x in line for x in ['Warning','Overfull','Underfull','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    builds=json.loads((HERE/'build.json').read_text())
    results={}
    for stem in STEMS:
        reachable=set()
        def visit(n):
            assert n not in reachable
            reachable.add(n)
            for child in re.findall(re.escape(BS)+r'(?:input|include){([^}]+)}',(TARGET/n).read_text()):visit(child if child.endswith('.tex') else child+'.tex')
        visit(stem+'.tex')
        text='\n'.join((TARGET/n).read_text() for n in reachable)
        labels=Counter(re.findall(re.escape(BS+'label{')+r'([^}]+)}',text))
        refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref){([^}]+)}',text))
        assert all(x==1 for x in labels.values()) and refs<=set(labels)
        old=warnings((SOURCE if stem==STEMS[0] else STANDALONE)/(stem+'.log'))
        new=warnings(TARGET/(stem+'.log'))
        pdf=TARGET/(stem+'.pdf')
        assert builds[stem]['returncode']==0 and sha(pdf)==builds[stem]['pdf_sha256']
        doc=fitz.open(pdf);assert 'Version 5.5' in doc[0].get_text()
        texts=[' '.join(page.get_text().split()) for page in doc]
        start=next(i+1 for i,t in enumerate(texts) if 'A lending decision makes the joint-law requirement concrete.' in t)
        end=next(i+1 for i,t in enumerate(texts) if 'The next example shows why persistent contract type' in t)
        pages=sorted({1,*range(start-1,end+2)})
        for page in pages:
            doc[page-1].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE/f'{stem}-page-{page}.png')
            (HERE/f'{stem}-page-{page}.txt').write_text(doc[page-1].get_text())
        bounds=[i+1 for i,page in enumerate(doc) if any(min(b[0],b[1]) < -1 or b[2] > page.rect.width+1 or b[3] > page.rect.height+1 for b in page.get_text('blocks'))]
        results[stem]=dict(pages=len(doc),pdf=str(pdf.relative_to(ROOT)),pdf_sha256=sha(pdf),new_warnings=dict(new-old),inherited_warnings=dict(old),out_of_page_text_blocks=bounds,review_pages=pages)
        assert not (new-old) and not bounds,results[stem]
    body_aux=(TARGET/'simulation-foundations.aux').read_text()
    matches=[line for line in body_aux.splitlines() if line.startswith(BS+'newlabel{sim:body-end}{{')]
    assert len(matches)==1
    body_end_page=int(matches[0].split('}{')[2].split('}')[0])
    result=dict(passed_preservation=True,version='5.5',protected_source_files=len(preservation['sources']),changed_sources=[n for n,h in preservation['sources'].items() if sha(TARGET/n)!=h],inherited_simulation_chapters=26,unchanged_simulation_chapters=25,standalone_body_pages=body_end_page-1,documents=results,readiness='not_ready')
    dump('verification.json',result);print(json.dumps(result))

if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
