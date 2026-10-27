"""Protected coupon continuation integration; bounded build and document checks."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from datetime import datetime,timezone
import json,os,re,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2]
S=R/'docs/design/proposal/manuscript-coupon-continuation-v546-20261027'
T=R/'docs/design/proposal/manuscript-coupon-scope-v547-20261027'
PDFS={'accounting-product-proposal':'526c347b98545f7865211f5b510b0429b4d9761a097ac5bdfc5f02e139797e93','simulation-foundations':'5db0146d165d1e2124be8cf9fa091c4bf6fe7b08fd95db81e752c7f135864b89'}
ADDED={'simulation/coupon-scope.tex':'coupon-scope.tex'}
EDITED=['accounting-product-proposal.tex','simulation-foundations.tex','simulation/17-continuous-methods.tex']
def digest(p):return sha256(p.read_bytes()).hexdigest()
def save(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def transform(n,t):
    if n in ['accounting-product-proposal.tex','simulation-foundations.tex']:
        assert t.count('Version 5.46')==1;return t.replace('Version 5.46','Version 5.47')
    if n=='simulation/17-continuous-methods.tex':return t+'\n\\input{simulation/coupon-scope}\n'
    return t
def prepare():
    assert not T.exists() and not (H/'source-preservation.json').exists()
    cat=json.loads((R/'scripts/accounting_master_catalog.json').read_text())['active_execution_note']
    assert cat['current_candidate'].startswith('5.46;')
    for n,h in PDFS.items():assert digest(S/(n+'.pdf'))==h
    assert (R/'docs/AccDSL-latest.pdf').resolve()==S/'accounting-product-proposal.pdf'
    sources={p.relative_to(S).as_posix():digest(p) for p in S.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark']}
    evidence={str(p.relative_to(R)):digest(p) for folder in ['coupon-schedule-invariant-20261027','coupon-continuation-scope-20261027'] for p in (H.parent/folder).rglob('*') if p.is_file() and not {'inputs','__pycache__','control-before'}&set(p.parts) and p.suffix not in ['.png','.pyc']}
    for folder,attempt in [('coupon-schedule-invariant-20261027','attempt-01'),('coupon-continuation-scope-20261027','attempt-01')]:
        p=H.parent/folder/attempt;assert json.loads((p/'verification.json').read_text())['status']=='PASS'
        for n,d in json.loads((p/'source-lock.json').read_text()).items():assert digest(R/n)==d;evidence[n]=d
    for n in sources:
        p=T/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(transform(n,(S/n).read_text()))
    for n,f in ADDED.items():(T/n).write_bytes((H/f).read_bytes())
    save('source-preservation.json',dict(source=str(S.relative_to(R)),target=str(T.relative_to(R)),sources=sources,evidence=evidence,added={n:digest(H/f) for n,f in ADDED.items()},integration_inputs={n:digest(H/n) for n in ['coupon-scope.tex','reader-plan.md']},named_edits=EDITED))
    print(json.dumps(dict(prepared=True,sources=len(sources),evidence=len(evidence))))
def build():
    attempt=sys.argv[2];assert attempt in ['01','02','03'];out=H/('build-attempt-'+attempt);out.mkdir(exist_ok=False)
    env={**os.environ,'TEXMFVAR':'/tmp/accdsl-bank-profile-tex-cache','TEXMFCACHE':'/tmp/accdsl-bank-profile-tex-cache','CUDA_VISIBLE_DEVICES':'-1'};results=[]
    for name in PDFS:
        cmd=['latexmk','-lualatex','-silent','-g','-interaction=nonstopmode','-halt-on-error',name+'.tex'];clock=time.monotonic();started=datetime.now(timezone.utc).isoformat()
        with (out/(name+'.stdout.log')).open('w') as f:result=subprocess.run(cmd,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
        for ext in ['.log','.pdf']:
            if (T/(name+ext)).exists():(out/(name+ext)).write_bytes((T/(name+ext)).read_bytes())
        results.append(dict(document=name,command=cmd,returncode=result.returncode,started_utc=started,wall_seconds=time.monotonic()-clock,pdf_sha256=digest(T/(name+'.pdf')) if (T/(name+'.pdf')).exists() else None))
        save('build-attempt-'+attempt+'/manifest.json',dict(results=results,environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},cpu_gpu='CPU; GPU intentionally hidden',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),data_version='source-preservation.json',plan='docs/plans/accounting-coupon-scope-integration-20261027.md',result='result.md',random_seeds='N/A document build',cwd=str(T)))
        print(json.dumps(results[-1]),flush=True)
        if result.returncode:raise SystemExit(result.returncode)
def warnings(p):return Counter(re.sub(r' on input line \d+','',x) for x in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',x))
def verify():
    import fitz
    assert not (H/'verification.json').exists();lock=json.loads((H/'source-preservation.json').read_text());checks=[];docs=[]
    def ck(n,v):checks.append(dict(name=n,passed=bool(v)));assert v,n
    try:
        for n,d in lock['sources'].items():ck('predecessor:'+n,digest(S/n)==d);ck('retained:'+n,(T/n).read_text()==transform(n,(S/n).read_text()))
        for n,d in lock['evidence'].items():ck('evidence:'+n,digest(R/n)==d)
        for n,d in lock['added'].items():ck('added:'+n,digest(T/n)==d)
        for n,d in lock['integration_inputs'].items():ck('integration:'+n,digest(H/n)==d)
        keys=re.findall(r'@\w+\{([^,]+),',(T/'references.bib').read_text());ck('unique_bibliography',len(keys)==len(set(keys)))
        for name in PDFS:
            log=(T/(name+'.log')).read_text();ck(name+'/references',not re.search(r'undefined|multiply defined',log,re.I))
            new=warnings(T/(name+'.log'))-warnings(S/(name+'.log'));ck(name+'/warnings',not new)
            pdf=fitz.open(T/(name+'.pdf'));texts=[' '.join(p.get_text().split()) for p in pdf]
            ck(name+'/cover','Version 5.47' in texts[0])
            ranges=[]
            for label,opening,ending,words in [('coupon-scope','The residual claim is a property of the cash-only payment rule','discarding prior flows.',['induction','January','midperiod','identities','64','65'])]:
                starts=[i+1 for i,t in enumerate(texts) if opening in t];ends=[i+1 for i,t in enumerate(texts) if ending in t]
                ck(name+'/'+label+'/section',bool(starts) and bool(ends));first,last=starts[-1],ends[-1];ck(name+'/'+label+'/order',first<=last)
                text=' '.join(texts[first-1:last]);ck(name+'/'+label+'/complete_argument',all(x in text for x in words));ranges.append([first,last])
            clipped=[i+1 for i,p in enumerate(pdf) if any(min(b[0],b[1])<-1 or b[2]>p.rect.width+1 or b[3]>p.rect.height+1 for b in p.get_text('blocks'))];ck(name+'/clipping',not clipped)
            aux=(T/(name+'.aux')).read_text();body=int(re.search(r'\\newlabel\{sim:body-end\}\{\{[^}]*\}\{(\d+)\}',aux).group(1))-1 if name=='simulation-foundations' else None
            pages=[1]+sorted({i for first,last in ranges for i in range(first,last+1)});folder=H/('render-'+name);folder.mkdir(exist_ok=True)
            for i in pages:pdf[i-1].get_pixmap(matrix=fitz.Matrix(1,1)).save(folder/f'page-{i}.png')
            (H/(name+'-additions.txt')).write_text('\n\n'.join('PAGE '+str(i)+'\n'+pdf[i-1].get_text() for i in pages))
            docs.append(dict(document=name,pages=len(pdf),body_pages=body,sha256=digest(T/(name+'.pdf')),new_warnings=dict(new),clipped=clipped,addition_pages=ranges,rendered_pages=pages))
        save('document-checks.json',docs);save('verification.json',dict(status='PASS',checks=len(checks),results=checks,protected_sources=len(lock['sources']),protected_evidence=len(lock['evidence']),documents=docs,readiness='author_review_pending'))
        print(json.dumps(dict(status='PASS',checks=len(checks),documents=docs)))
    except Exception:
        save('verification-failure-'+sys.argv[2]+'.json',dict(status='FAIL',checks=checks,documents=docs));raise
if __name__=='__main__':{'prepare':prepare,'build':build,'verify':verify}[sys.argv[1]]()
