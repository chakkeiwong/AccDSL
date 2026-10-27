from collections import Counter
from hashlib import sha256
import json, os, re, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE=ROOT/'docs/design/proposal/manuscript-authoring-scope-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-profile-interfaces-20261026'
BASE='e463820a696aefed8acdd5b142178bbbaa01eab2f0185b32ef4e21a84e7591eb'
SECTION='sections/profile-interfaces.tex'
BS=chr(92);NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+NL)
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 4.40 (proposal candidate)')==1
        return text.replace('Version 4.40 (proposal candidate)','Version 4.41 (proposal candidate)')
    if name=='chapters/09-implementation.tex':
        anchor=BS+'input{sections/operations-storage}'
        assert text.count(anchor)==1
        return text.replace(anchor,anchor+NL+BS+'input{sections/profile-interfaces}')
    if name=='sections/portable-values.tex':
        anchor='unfinished. Domain scope and authoring syntax are therefore separate decisions.'
        assert text.count(anchor)==1
        return text.replace(anchor,anchor+NL+'Section~'+BS+'ref{sec:profile-effects-composition} adds a finite description of'+NL+'dependencies between retained native exchanges, preserving their distinct state'+NL+'and publication effects without supplying a general method dispatcher.')
    return text
def tokens(text):
    return {'labels':Counter(re.findall(r'\label	extbraceleft([^}]+)}'.replace('textbraceleft','{'),text)),
        'refs':Counter(re.findall(r'\(?:ref|eqref|autoref)	extbraceleft([^}]+)}'.replace('textbraceleft','{'),text)),
        'citations':Counter(re.findall(r'\cite[a-zA-Z]*	extbraceleft([^}]+)}'.replace('textbraceleft','{'),text)),
        'displays':Counter(re.findall(r'\	extlbrack(.*?)\	extrbrack'.replace('textlbrack','[').replace('textrbrack',']'),text,re.S))}
def warnings(text):
    return Counter(line for line in text.splitlines() if any(s in line for s in ['Warning','Overfull','Underfull','Undefined','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
def prepare():
    assert not TARGET.exists() and not (HERE/'baseline.json').exists()
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources)==174
    for name in sources:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
    (TARGET/SECTION).write_bytes((HERE/'profile-interfaces.tex').read_bytes())
    inputs={}
    for unit in ['component-identity-repair-20261026','profile-publication-effects-20261026','profile-composition-boundary-20261026']:
        for name in ['result.md','checks.json','run-manifest.json']:
            p=ROOT/'data/accounting-master'/unit/name;inputs[str(p.relative_to(ROOT))]=sha(p)
    dump(HERE/'baseline.json',{'source':str(SOURCE.relative_to(ROOT)),'sources':sources,'pdf_sha256':BASE,
        'added_section_sha256':sha(HERE/'profile-interfaces.tex'),'evidence':inputs})
    print(json.dumps({'prepared_sources':len(sources),'new_section':SECTION}))
def build():
    assert not (HERE/'build.json').exists(),'build already recorded'
    cache='/tmp/accdsl-profile-interfaces-20261026-tex-cache';Path(cache).mkdir(parents=True,exist_ok=True)
    env={'TEXMFVAR':cache,'TEXMFCACHE':cache,'CUDA_VISIBLE_DEVICES':'-1'}
    command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex']
    start=time.monotonic()
    with (HERE/'build.log').open('w') as log:
        r=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=240)
    pdf=TARGET/'accounting-product-proposal.pdf'
    dump(HERE/'build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,'returncode':r.returncode,'pdf_sha256':sha(pdf) if pdf.exists() else None})
    print(json.dumps({'returncode':r.returncode}));raise SystemExit(r.returncode)
def verify():
    import fitz
    baseline=json.loads((HERE/'baseline.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    for name,h in baseline['sources'].items():
        assert sha(SOURCE/name)==h,name
        assert (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),'unexpected delta:'+name
    for name,h in baseline['evidence'].items():assert sha(ROOT/name)==h,name
    assert sha(TARGET/SECTION)==baseline['added_section_sha256']
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert actual==set(baseline['sources'])|{SECTION}
    oldtext=NL.join((SOURCE/n).read_text() for n in baseline['sources'] if n.endswith('.tex'))
    newtext=NL.join((TARGET/n).read_text() for n in actual if n.endswith('.tex'))
    # Exact predecessor-file comparison above is stronger than counting equations.
    label_pattern=re.escape(BS+'label{')+r'([^}]+)}';ref_pattern=re.escape(BS)+r'(?:ref|eqref|autoref)	extbraceleft([^}]+)}'.replace('textbraceleft','{')
    labels=Counter(re.findall(label_pattern,newtext));refs=set(re.findall(ref_pattern,newtext))
    assert all(v==1 for v in labels.values()),'duplicate labels';assert refs<=set(labels),'missing references'
    oldwarn=warnings((SOURCE/'accounting-product-proposal.log').read_text(errors='replace'));newwarn=warnings((TARGET/'accounting-product-proposal.log').read_text(errors='replace'))
    delta=newwarn-oldwarn
    build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0
    pdf=TARGET/'accounting-product-proposal.pdf';assert sha(pdf)==build['pdf_sha256'];doc=fitz.open(pdf)
    assert 'Version 4.41' in doc[0].get_text()
    start=[i for i,p in enumerate(doc) if 'An insurer can publish a valuation assessment' in ' '.join(p.get_text().split())]
    end=[i for i,p in enumerate(doc) if 'adopt a checked distinction' in ' '.join(p.get_text().split())]
    assert len(start)==len(end)==1,(start,end)
    pages=sorted({1,*range(start[0],end[0]+3)})
    for n in pages:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'page-{n}.png')
    result={'passed_preservation':True,'version':'4.41','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
        'protected_source_files':len(baseline['sources']),'added_source_files':1,'new_warnings':dict(delta),'inherited_warnings':dict(oldwarn),
        'review_pages':pages,'readiness':'not_ready','acceptance_scope':'bounded interface section; independent and human acceptance pending'}
    dump(HERE/'verification.json',result);print(json.dumps(result))
    assert not delta,'new warning requires local inspection/repair'
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
