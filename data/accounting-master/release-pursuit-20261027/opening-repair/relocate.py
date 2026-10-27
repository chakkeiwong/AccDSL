from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json,os,re,subprocess,sys,tempfile,time,hashlib
D=Path(__file__).resolve().parent;R=D.parents[3];T=R/'docs/design/proposal/manuscript-release-v553r1-20261027';OUT=D/'relocation-01';NAMES=['accounting-product-proposal','simulation-foundations']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
def prepare():
 OUT.mkdir(exist_ok=False);record=read(D/'package-record.json');assert sha(T/'package-manifest.json')==record['manifest_sha256']
 target=Path(tempfile.mkdtemp(prefix='accdsl-v553r1-relocation-',dir='/tmp'));manifest=read(T/'package-manifest.json')
 for row in manifest['files']:
  source,dest=T/row['path'],target/row['path'];assert sha(source)==row['sha256'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
 (target/'package-manifest.json').write_bytes((T/'package-manifest.json').read_bytes());p=subprocess.run(['python3','-I','-B','verify_package.py'],cwd=target,capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stdout+p.stderr
 cache=target/'.tex-cache';cache.mkdir();dump(OUT/'location.json',{'target':str(target),'cache':str(cache),'copied_files':len(manifest['files']),'manifest_sha256':record['manifest_sha256'],'package_verification':json.loads(p.stdout)});print(json.dumps({'prepared':True,'target':str(target)}))
def build(name):
 assert name in NAMES;info=read(OUT/'location.json');target=Path(info['target']);result=OUT/(name+'-build.json');log=OUT/(name+'.stdout');assert not result.exists() and not log.exists()
 env=dict(os.environ,TEXMFVAR=info['cache'],TEXMFCACHE=info['cache'],CUDA_VISIBLE_DEVICES='-1');cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','-no-shell-escape',name+'.tex'];start=time.monotonic()
 with log.open('w') as f:p=subprocess.run(cmd,cwd=target,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 dump(result,{'command':cmd,'cwd':str(target),'exit_code':p.returncode,'wall_seconds':time.monotonic()-start,'environment':{k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},'timestamp_utc':datetime.now(timezone.utc).isoformat(),'git_commit':'unavailable; unusable repository marker','random_seeds':'N/A deterministic document build','plan':str((D/'plan.md').relative_to(R))});print(json.dumps({'document':name,'exit_code':p.returncode,'seconds':time.monotonic()-start}));raise SystemExit(p.returncode)
def verify():
 import fitz
 assert not (OUT/'result.json').exists();info=read(OUT/'location.json');target=Path(info['target']);reports=[]
 def warnings(p):return Counter(re.sub(r' on input line \d+','',s) for s in p.read_text().splitlines() if re.search(r'Warning:|Overfull|undefined references|undefined citations|multiply defined',s))
 for name in NAMES:
  assert read(OUT/(name+'-build.json'))['exit_code']==0
  a,b=fitz.open(T/(name+'.pdf')),fitz.open(target/(name+'.pdf'));assert len(a)==len(b)
  changed=[i+1 for i in range(len(a)) if ' '.join(a[i].get_text().split())!=' '.join(b[i].get_text().split())];assert not changed,(name,changed)
  log=target/(name+'.log');assert not re.search(r'undefined|multiply defined',log.read_text(),re.I);assert not warnings(log)-warnings(T/(name+'.log'))
  inputs=set()
  for line in (target/(name+'.fls')).read_text().splitlines():
   if line.startswith('INPUT '):
    p=Path(line[6:]);inputs.add(str((target/p).resolve() if not p.is_absolute() else p.resolve()))
  hidden=[p for p in inputs if p.startswith(str(R)+'/')];assert not hidden,hidden
  external=sorted(p for p in inputs if not p.startswith(str(target)+'/'));dump(OUT/(name+'-external-inputs.json'),external)
  reports.append({'document':name,'pages':len(a),'all_page_text_equal':True,'source_pdf_sha256':sha(T/(name+'.pdf')),'relocated_pdf_sha256':sha(target/(name+'.pdf')),'external_environment_files':len(external),'hidden_original_worktree_inputs':hidden})
 dump(OUT/'result.json',{'passed':True,'documents':reports,'manifest_sha256':info['manifest_sha256'],'scope':'Declared document-package relocation in the existing environment; not independent installation, full executable dependency closure or release acceptance.'});print(json.dumps({'passed':True,'documents':reports}))
if __name__=='__main__':
 if sys.argv[1]=='build':build(sys.argv[2])
 else:{'prepare':prepare,'verify':verify}[sys.argv[1]]()
