"""One-time protected manuscript successor; each phase is invoked separately."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,os,re,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10);BS=chr(92)
SOURCE=ROOT/'docs/design/proposal/manuscript-state-invariants-20261026'
TARGET=ROOT/'docs/design/proposal/manuscript-event-contract-20261026'
BASE='ccc3ffbb83303dcbeb892decd3bd9f36cd112d54148ab15fe24167f9bd34c38e'
ADDED=['authored-event-contract']
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+NL)
def expected(name,text):
    if name=='accounting-product-proposal.tex':
        assert text.count('Version 4.47 (proposal candidate)')==1
        return text.replace('Version 4.47 (proposal candidate)','Version 4.48 (proposal candidate)')
    if name=='sections/authored-state-invariants.tex':
        return text+NL+NL.join(BS+'input{sections/'+name+'}' for name in ADDED)+NL
    return text
def prepare():
    assert not TARGET.exists() and not (HERE/'baseline.json').exists()
    assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    sources={p.relative_to(SOURCE).as_posix():sha(p) for p in SOURCE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert len(sources)==182
    evidence={}
    for unit in ['authored-event-prerequisite-audit-20261026','authored-event-contract-20261026']:
        folder=HERE.parent/unit
        assert json.loads((folder/'checks.json').read_text())['passed']
        for name in (['result.md','checks.json','run-manifest.json','probe.py'] if unit.endswith('audit-20261026') else ['result.md','checks.json','run-manifest.json','verify.py','contract.py','contract_runner.py']):
            p=folder/name;evidence[str(p.relative_to(ROOT))]=sha(p)
    for name in sources:
        p=TARGET/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(expected(name,(SOURCE/name).read_text()))
    for name in ADDED:(TARGET/'sections'/(name+'.tex')).write_bytes((HERE/(name+'.tex')).read_bytes())
    dump(HERE/'baseline.json',{'source':str(SOURCE.relative_to(ROOT)),'sources':sources,'pdf_sha256':BASE,
        'added':{name:sha(HERE/(name+'.tex')) for name in ADDED},'evidence':evidence})
    print(json.dumps({'prepared_sources':len(sources),'added':ADDED,'preserved_pdf':BASE}))
def build():
    assert not (HERE/'build.json').exists()
    cache='/tmp/accdsl-event-contract-20261026-tex-cache';Path(cache).mkdir(parents=True,exist_ok=True)
    env={'TEXMFVAR':cache,'TEXMFCACHE':cache,'CUDA_VISIBLE_DEVICES':'-1'}
    command=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error','accounting-product-proposal.tex'];start=time.monotonic()
    with (HERE/'build.log').open('w') as log:
        r=subprocess.run(command,cwd=TARGET,env={**os.environ,**env},stdout=log,stderr=subprocess.STDOUT,timeout=240)
    pdf=TARGET/'accounting-product-proposal.pdf'
    dump(HERE/'build.json',{'command':command,'cwd':str(TARGET),'environment':env,'wall_seconds':time.monotonic()-start,
        'returncode':r.returncode,'pdf_sha256':sha(pdf) if pdf.exists() else None})
    print(json.dumps({'returncode':r.returncode}));raise SystemExit(r.returncode)
def verify():
    import fitz
    baseline=json.loads((HERE/'baseline.json').read_text());assert sha(SOURCE/'accounting-product-proposal.pdf')==BASE
    for name,h in baseline['sources'].items():
        assert sha(SOURCE/name)==h and (TARGET/name).read_text()==expected(name,(SOURCE/name).read_text()),name
    for name,h in baseline['evidence'].items():assert sha(ROOT/name)==h,name
    for name,h in baseline['added'].items():assert sha(TARGET/'sections'/(name+'.tex'))==h
    actual={p.relative_to(TARGET).as_posix() for p in TARGET.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}}
    assert actual==set(baseline['sources'])|{'sections/'+n+'.tex' for n in ADDED}
    combined=NL.join((TARGET/n).read_text() for n in actual if n.endswith('.tex'))
    labels=Counter(re.findall(re.escape(BS+'label{')+'([^}]+)}',combined))
    refs=set(re.findall(re.escape(BS)+r'(?:ref|eqref|autoref)'+re.escape('{')+'([^}]+)}',combined))
    assert all(v==1 for v in labels.values()) and refs<=set(labels)
    def warnings(p):
        return Counter(line for line in p.read_text(errors='replace').splitlines() if any(s in line for s in
            ['Warning','Overfull','Underfull','Undefined','undefined','Missing character:','LaTeX Error']) or line.startswith('!'))
    old=warnings(SOURCE/'accounting-product-proposal.log');new=warnings(TARGET/'accounting-product-proposal.log');delta=new-old
    build=json.loads((HERE/'build.json').read_text());assert build['returncode']==0
    pdf=TARGET/'accounting-product-proposal.pdf';assert sha(pdf)==build['pdf_sha256'];doc=fitz.open(pdf)
    assert 'Version 4.48' in doc[0].get_text()
    starts=[i for i,p in enumerate(doc) if 'Keep the event’s intent when a method is specialized' in ' '.join(p.get_text().split())]
    ends=[i for i,p in enumerate(doc) if 'These comparisons extend the checked refusal scope' in ' '.join(p.get_text().split())]
    assert len(starts)==len(ends)==1,(starts,ends)
    pages=sorted({1,*range(starts[0],ends[0]+3)})
    for n in pages:
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(HERE/f'page-{n}.png')
        (HERE/f'page-{n}.txt').write_text(doc[n-1].get_text())
    result={'passed_preservation':True,'version':'4.48','pages':len(doc),'pdf':str(pdf.relative_to(ROOT)),'pdf_sha256':sha(pdf),
        'protected_source_files':len(baseline['sources']),'added_source_files':len(ADDED),'new_warnings':dict(delta),
        'inherited_warnings':dict(old),'review_pages':pages,'readiness':'not_ready'}
    dump(HERE/'verification.json',result);print(json.dumps(result));assert not delta,'new warning requires inspection'
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
