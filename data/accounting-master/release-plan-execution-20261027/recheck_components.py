from pathlib import Path
import subprocess,tempfile,shutil,os,time,json,hashlib,concurrent.futures
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
names=['release-bundle-recovery-20261027','selected-term-bundle-20261027']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name):
 source=R/'data/accounting-master'/name/'attempt-02/bundle';manifest=json.loads((source/'bundle-manifest.json').read_text());tmp=Path(tempfile.mkdtemp(prefix='accdsl-release-check-'));target=tmp/'relocated';shutil.copytree(source,target);env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1','PYTHONDONTWRITEBYTECODE':'1'};cmd=['python3','-I','-B',str(target/'scripts/verify_relocated.py'),'audit-output-01'];clock=time.monotonic();proc=subprocess.run(cmd,cwd=tmp,env=env,text=True,capture_output=True,timeout=180);out=H/'component-checks'/name;out.mkdir(parents=True,exist_ok=False);(out/'stdout.txt').write_text(proc.stdout);(out/'stderr.txt').write_text(proc.stderr)
 if (target/'audit-output-01').exists():shutil.copytree(target/'audit-output-01',out/'output')
 result={'component':name,'source':str(source.relative_to(R)),'manifest_sha256':sha(source/'bundle-manifest.json'),'command':cmd,'cwd':str(tmp),'returncode':proc.returncode,'seconds':time.monotonic()-clock,'temporary_root':str(tmp),'seed':'N/A deterministic conformance','cpu_gpu':'CPU; GPU intentionally hidden','comparison':'Frozen whole-result identities and authored rejection cases; same financial engine, not independent accounting proof'};(out/'run-manifest.json').write_text(json.dumps(result,indent=2)+chr(10));return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as p:rs=list(p.map(run,names))
(H/'component-rechecks.json').write_text(json.dumps(rs,indent=2)+chr(10));print(json.dumps(rs,indent=2))
