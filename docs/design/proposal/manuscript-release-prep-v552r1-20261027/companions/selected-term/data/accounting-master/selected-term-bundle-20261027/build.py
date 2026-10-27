"""Bundle exact code dependencies without copying recursive audit history."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, os, platform, shutil, subprocess, sys, tempfile, time
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert len(sys.argv)==2
O=H/sys.argv[1];O.mkdir(exist_ok=False);start=time.monotonic()
P=B/'selected-term-program-20261027';prior=P/'attempt-01'
assert read(prior/'checks.json')['passed']
sys.path.insert(0,str(P));import program as p
root=O/'bundle';root.mkdir()
locks=read(prior/'source-lock.json');selected={n for n in locks if n.endswith('.py')}
loaded={str(Path(m.__file__).resolve().relative_to(R)) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).is_file() and Path(m.__file__).resolve().is_relative_to(R)}
selected|=loaded
selected|=set(p.source.full.p.base.binding.HELPERS)
selected|={str((P/'program.py').relative_to(R)),str((P/'contract.md').relative_to(R))}
source_lock={n:sha(R/n) for n in selected}
for n in sorted(selected):
    dest=root/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dest)
for chart in ['alpha','beta']:
    for suffix in ['program','selection']:
        path=prior/f'{chart}-{suffix}.json';source_lock[str(path.relative_to(R))]=sha(path)
        dest=root/'inputs'/path.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(path,dest)
    path=prior/f'{chart}-result.json';source_lock[str(path.relative_to(R))]=sha(path);result=read(path)
    dump(root/'inputs'/f'{chart}-oracle.json',dict(canonical_sha256=p.core.digest(result),order_sha256=p.source.full.p.order_digest(result),final_state=result['after'],source=str(path.relative_to(R)),source_sha256=sha(path)))
    del result
dest=root/'scripts/verify_relocated.py';shutil.copyfile(H/'verify_relocated.py',dest)
(root/'README.md').write_text('''# Selected term program component

This internal bundle contains the exact SelectedTermProgram/1 and its retained
semantic dependencies, two complete selected program inputs, independently
supplied selections and full-result hash commitments. Original full results
remain retained by path and digest in the source worktree; those large records
are not imported during execution. Each relocated result is fully recomputed
before its canonical and insertion-order hashes are compared.

Run from this directory in the recorded Python environment:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B scripts/verify_relocated.py output-01

Use a fresh output directory. Other copied verifier files are historical
reference dependencies; do not invoke their writer entrypoints. The script
disables native lifecycle/financial builder callbacks and audits project file
access before importing program code. Only the bundle and recorded Python
runtime may be read; writes are limited to the fresh output directory.

This is not the full modern AccDSL package, production software, independent
accounting acceptance or publication. No papers/standards are included, and
redistribution rights for project material remain unreviewed. The selected
profile's complete refusal, population and report limits remain in contract.md
under data/accounting-master/selected-term-program-20261027/.
''')
files=[dict(path=str(q.relative_to(root)),sha256=sha(q),bytes=q.stat().st_size,role='code_or_reference' if q.suffix=='.py' else 'selected_input_or_contract') for q in sorted(root.rglob('*')) if q.is_file()]
environment=dict(python=platform.python_version(),executable=sys.executable,platform=platform.platform(),external_packages='none imported by selected program; Python standard library')
dump(root/'bundle-manifest.json',dict(profile='SelectedTermBundle/1',files=files,environment=environment,full_release_bundle=False))
for q in [H/'build.py',H/'verify_relocated.py',R/'docs/plans/accounting-selected-term-bundle-20261027.md',prior/'checks.json']:source_lock[str(q.relative_to(R))]=sha(q)
dump(O/'source-lock.json',source_lock)
relocated=Path(tempfile.mkdtemp(prefix='accdsl-term-relocation-',dir='/tmp'))/'bundle';shutil.copytree(root,relocated)
cmd=[sys.executable,'-I','-B',str(relocated/'scripts/verify_relocated.py'),'output-01']
env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
try:proc=subprocess.run(cmd,cwd=relocated,env=env,capture_output=True,text=True,timeout=90)
except subprocess.TimeoutExpired as e:
    dump(O/'timeout.json',dict(timeout_seconds=90,command=cmd,relocated=str(relocated)));raise
(O/'stdout.txt').write_text(proc.stdout);(O/'stderr.txt').write_text(proc.stderr)
if (relocated/'output-01').exists():shutil.copytree(relocated/'output-01',O/'relocated-output')
assert all(sha(R/n)==d for n,d in source_lock.items())
git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
dump(O/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/selected-term-bundle-20261027/build.py '+sys.argv[1],child_command=cmd,child_cwd=str(relocated),git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',environment=environment,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(root/'bundle-manifest.json'),timestamp_utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/accounting-selected-term-bundle-20261027.md',result_file=str((H/'result.md').relative_to(R)),exit_code=proc.returncode))
assert proc.returncode==0,'relocation failed; inspect retained stderr'
v=read(O/'relocated-output/checks.json');assert v['passed']
summary=dict(passed=True,files=len(files),bytes=sum(f['bytes'] for f in files),checks=len(v['checks']),loaded_project_modules=len(v['loaded_project_modules']),protected_files=len(source_lock),full_release_bundle=False)
dump(O/'verification.json',summary);print(json.dumps(summary))
