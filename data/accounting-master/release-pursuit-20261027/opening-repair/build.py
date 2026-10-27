from pathlib import Path
import os,subprocess,json,time,sys,platform
D=Path(__file__).resolve().parent;R=D.parents[3];T=R/'docs/design/proposal/manuscript-release-v553r1-20261027';cache=T/'.tex-cache';cache.mkdir(exist_ok=True);env={**os.environ,'TEXMFVAR':str(cache),'TEXMFCACHE':str(cache),'CUDA_VISIBLE_DEVICES':'-1'};results=[]
for volume in ['accounting-product-proposal','simulation-foundations']:
 cmd=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','-no-shell-escape',volume+'.tex'];start=time.monotonic()
 with (D/(volume+'-build.log')).open('w') as log:p=subprocess.run(cmd,cwd=T,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
 results.append({'volume':volume,'command':cmd,'returncode':p.returncode,'seconds':time.monotonic()-start,'log':str((D/(volume+'-build.log')).relative_to(R))});(D/'build-manifest.json').write_text(json.dumps({'cwd':str(T),'environment':{k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},'python':sys.version,'platform':platform.platform(),'builds':results,'seed':'N/A deterministic document build','plan':str((D/'plan.md').relative_to(R))},indent=2)+chr(10))
 if p.returncode:break
print(json.dumps(results));raise SystemExit(0 if len(results)==2 and all(x['returncode']==0 for x in results) else 1)
