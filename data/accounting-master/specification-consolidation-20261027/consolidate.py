"""Protected 5.52 bounded specification repair; no original writer is rerun."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from datetime import datetime,timezone
import json,os,re,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
S=R/'docs/design/proposal/manuscript-insurance-stage-v551-20261027'
T=R/'docs/design/proposal/manuscript-consolidated-v552-20261027'
NAMES=['accounting-product-proposal','simulation-foundations']
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)
def transform(name,text):
    if name in [n+'.tex' for n in NAMES]:return once(text,'Version 5.51','Version 5.52')
    if name=='chapters/01-purpose.tex':
        marker='The historical accounts are compatible with the whole interval $[5,7]$ of'
        explanation='''Here $\\alpha$ denotes the fixed share. In Chapter~\\ref{sim:observations}
the same letter denoted the floating share. These are complementary
coordinates: the fixed share here equals one minus the floating share there.
Substituting that relation in $7-2\\alpha$ gives the earlier $5+2\\alpha$
when its $\\alpha$ is read as the floating share. Both conventions describe
interest of 5 for wholly fixed debt and 7 for wholly floating debt; a numerical
share must be complemented when transferring it between these examples.

'''
        text=once(text,marker,explanation+marker)
        text=once(text,'The first release must answer the following complete workflow.',
          'The first software release must answer the following complete workflow.')
        marker='\\begin{longtable}{L{34mm}L{102mm}}'
        text=once(text,marker,'''Acceptance of this design document is a separate milestone. It requires an
implementable specification, adequate source and conformance evidence, and
independent reader, implementation and domain review. It does not establish
that the software workflow has been delivered or that forecasts are validated.
The implementation sequence is described in Chapter~\\ref{ch:validation}.

'''+marker)
    elif name=='chapters/06-language.tex':
        text=once(text,'collections and carry. This bounded synthetic continuation preserves the',
          '''collections and carry. Its selected ordered-program envelope now binds the
complete source and request sequence, retains each successful prefix, and
preserves the first refused request and all unexecuted commands. Two relocated
programs reproduce the complete retained results. This bounded synthetic
continuation preserves the''')
    elif name=='sections/selected-term-execution.tex':text=text+(H/'ordered-program.tex').read_text()
    elif name=='chapters/09-implementation.tex':
        marker='their older fields do not silently extend a new closed signature.'
        text=once(text,marker,marker+'''
The source package includes those two historical files beside
\\path{spec/core-0.lark}. Their fixture and executable dependencies retain
repository-relative paths; \\path{spec/REFERENCE-ROOTS.md} gives the exact
resolution and the independently relocated Core~0 component. The selected
term-program component has its own versioned source and dependency manifest.
Neither component supplies a migration between these distinct profiles or
completes the remaining language interfaces.''')
    return text
def prepare():
    assert not T.exists() and not (H/'source-preservation.json').exists()
    live=read(B/'next-plan.json')['active_execution'];assert live['current_candidate']=='5.51;828 pages;not_ready'
    sources={str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    pdfs={n:sha(S/(n+'.pdf')) for n in NAMES}
    assert pdfs['accounting-product-proposal']=='2663e860cdcd6afc27b0d62f0ca242b872fb854380c6db2addb5e90171b37530'
    evidence={}
    for folder,files in [
      ('selected-term-program-20261027',['program.py','contract.md','result.md','attempt-01/checks.json','attempt-01/source-lock.json']),
      ('selected-term-bundle-20261027',['result.md','attempt-02/verification.json','attempt-02/bundle/bundle-manifest.json']),
      ('release-bundle-recovery-20261027',['result.md','attempt-02/verification.json','attempt-02/bundle/bundle-manifest.json']),
      ('profile-compatibility-20261027',['compatibility.md','result.md','attempt-01/interfaces.json']),
      ('integrated-failure-dispositions-20261027',['result.md','attempt-01/checks.json','attempt-01/X09-assessment-continuity.json'])]:
        for f in files:p=B/folder/f;evidence[str(p.relative_to(R))]=sha(p)
    for n in sources:
        p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(transform(n,(S/n).read_text()))
    additions={}
    for n in ['core-contract.md','core-ir.schema.json']:
        src=R/'docs/design/spec'/n;dst=T/'spec'/n;dst.write_bytes(src.read_bytes());additions['spec/'+n]=dict(source=str(src.relative_to(R)),sha256=sha(dst))
    roots='''# Normative file roots for the 5.52 source package

core-contract.md, core-ir.schema.json and core-0.lark are the exact historical
Core 0 companions from docs/design/spec. They do not govern later portable or
company profiles. The repository is the root for scripts/ and docs/design/;
../fixtures/ in the historical contract resolves to docs/design/fixtures/ in
that repository, not an unrecorded sibling of this manuscript directory.

For a self-contained historical component use
data/accounting-master/release-bundle-recovery-20261027/attempt-02/bundle/.
It contains the exact normative files, 17-export registry, authored fixture,
pure semantic validator and a README with a fresh-output relocation command.
For the selected current term-program component use
data/accounting-master/selected-term-bundle-20261027/attempt-02/bundle/.

The full manuscript evidence dependency closure remains incomplete. Neither
component establishes general compiler, independent accounting acceptance,
production readiness or redistribution permission. No source path is to be
silently resolved through a private home directory or a mutable network URL.
'''
    (T/'spec/REFERENCE-ROOTS.md').write_text(roots);additions['spec/REFERENCE-ROOTS.md']=dict(source=None,sha256=sha(T/'spec/REFERENCE-ROOTS.md'))
    dump(H/'source-preservation.json',dict(source=str(S.relative_to(R)),target=str(T.relative_to(R)),sources=sources,pdfs=pdfs,evidence=evidence,additions=additions,inputs={n:sha(H/n) for n in ['ordered-program.tex','consolidate.py']},plan='docs/plans/accounting-specification-consolidation-20261027.md'))
    print(json.dumps(dict(prepared=True,sources=len(sources),evidence=len(evidence),additions=len(additions))))
def build():
    name=sys.argv[2];assert name in NAMES;attempt=sys.argv[3];out=H/('build-'+attempt+'-'+name);out.mkdir(exist_ok=False)
    env=dict(os.environ,TEXMFVAR='/tmp/accdsl-consolidation-tex-cache',TEXMFCACHE='/tmp/accdsl-consolidation-tex-cache',CUDA_VISIBLE_DEVICES='-1')
    cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',name+'.tex'];start=time.monotonic()
    with (out/'stdout.log').open('w') as stream:p=subprocess.run(cmd,cwd=T,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=150)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
    for ext in ['.pdf','.log']:
        q=T/(name+ext)
        if q.exists():(out/q.name).write_bytes(q.read_bytes())
    result=dict(command=cmd,cwd=str(T),exit_code=p.returncode,wall_seconds=time.monotonic()-start,environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',random_seeds='N/A document build',plan='docs/plans/accounting-specification-consolidation-20261027.md',source_lock=sha(H/'source-preservation.json'),timestamp_utc=datetime.now(timezone.utc).isoformat())
    dump(out/'run-manifest.json',result);print(json.dumps(dict(document=name,exit_code=p.returncode,seconds=result['wall_seconds'])),flush=True)
    raise SystemExit(p.returncode)
def verify():
    import fitz
    assert not (H/'verification.json').exists();lock=read(H/'source-preservation.json');checks=[];docs=[]
    def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
    for n,h in lock['sources'].items():
        check(sha(S/n)==h,'baseline:'+n);check((T/n).read_text()==transform(n,(S/n).read_text()),'exact_transform:'+n)
        if n.endswith('.tex'):
            pattern=r'\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}'
            check([m.group(0) for m in re.finditer(pattern,(S/n).read_text(),re.S)]==[m.group(0) for m in re.finditer(pattern,(T/n).read_text(),re.S)],'display_equations:'+n)
            cites=r'\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{[^}]*\}'
            check(re.findall(cites,(S/n).read_text())==re.findall(cites,(T/n).read_text()),'citations:'+n)
    for n,h in lock['evidence'].items():check(sha(R/n)==h,'evidence:'+n)
    for n,h in lock['pdfs'].items():check(sha(S/(n+'.pdf'))==h,'baseline_pdf:'+n)
    for n,h in lock['inputs'].items():check(sha(H/n)==h,'integration_input:'+n)
    for n,d in lock['additions'].items():check(sha(T/n)==d['sha256'],'normative_addition:'+n)
    warnings=lambda p:Counter(re.sub(r' on input line \d+','',s) for s in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',s))
    needles=['Here α denotes the fixed share','Acceptance of this design document is a separate milestone','Its selected ordered-program envelope now binds','Run the selected commands as one program','source package includes those two historical files']
    for name in NAMES:
        log=(T/(name+'.log')).read_text();check(not re.search(r'undefined|multiply defined',log,re.I),name+':references')
        new=warnings(T/(name+'.log'))-warnings(S/(name+'.log'));check(not new,name+':no_new_warnings:'+str(dict(new)))
        pdf=fitz.open(T/(name+'.pdf'));texts=[' '.join(pg.get_text().split()) for pg in pdf]
        check('Version 5.52' in texts[0],name+':cover')
        pages={1};found={}
        if name==NAMES[0]:
            for needle in needles:
                hits=[i+1 for i,t in enumerate(texts) if needle in t];check(bool(hits),name+':text:'+needle);found[needle]=hits
                for i in hits:pages.update(range(max(1,i-1),min(len(pdf),i+2)+1))
        clipped=[i+1 for i,pg in enumerate(pdf) if any(min(b[0],b[1])<-1 or b[2]>pg.rect.width+1 or b[3]>pg.rect.height+1 for b in pg.get_text('blocks'))]
        check(not clipped,name+':clipping')
        render=H/('render-'+name);render.mkdir(exist_ok=True)
        for i in sorted(pages):pdf[i-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(render/f'page-{i}.png')
        if name==NAMES[1]:
            oldpdf=fitz.open(S/(name+'.pdf'));check(len(oldpdf)==len(pdf),'simulation_page_count_preserved')
            check(all(' '.join(oldpdf[i].get_text().split())==texts[i] for i in range(1,len(pdf))),'simulation_body_text_preserved')
        body=None
        if name==NAMES[1]:body=int(re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',(T/(name+'.aux')).read_text()).group(1))-1
        docs.append(dict(document=name,pages=len(pdf),body_pages=body,sha256=sha(T/(name+'.pdf')),rendered_pages=sorted(pages),anchors=found))
    dump(H/'verification.json',dict(passed=True,checks=checks,documents=docs,independent_acceptance=False,author_review='pending'))
    print(json.dumps(dict(passed=True,checks=len(checks),documents=docs)))
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
