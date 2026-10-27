from pathlib import Path
import subprocess,os,time,json,concurrent.futures,sys
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;T=R/'docs/design/proposal/manuscript-release-prep-v551r1-20261027'
cache=T/'.tex-cache';cache.mkdir(exist_ok=True);env=os.environ.copy();env.update(TEXMFVAR=str(cache.resolve()),TEXMFCACHE=str(cache.resolve()),CUDA_VISIBLE_DEVICES='-1')
def run(name):
 cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'];t=time.monotonic()
 with (H/(name+'-build-attempt-04.log')).open('w') as f:p=subprocess.run(cmd,cwd=T,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
 return {'command':cmd,'returncode':p.returncode,'seconds':time.monotonic()-t,'log':str(H/(name+'-build-attempt-04.log'))}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(run,['accounting-product-proposal','simulation-foundations']))
versions={k:subprocess.run(v,text=True,capture_output=True).stdout.splitlines()[:3] for k,v in {'latexmk':['latexmk','--version'],'lualatex':['lualatex','--version'],'bibtex':['bibtex','--version']}.items()};result={'builds':rs,'cwd':str(T),'environment':{k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},'versions':versions,'cpu_gpu':'CPU; GPU intentionally hidden','seed':'N/A deterministic document build','code_provenance':'Exact source hashes; unusable repository marker is not initialized','plan':'docs/plans/accounting-release-closure-20261027.md','result':'data/accounting-master/release-plan-execution-20261027/result.md'};(H/'build-manifest.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps(result,indent=2));sys.exit(any(x['returncode'] for x in rs))
