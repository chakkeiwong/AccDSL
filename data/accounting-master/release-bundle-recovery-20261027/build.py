"""Create a fresh, byte-preserving historical Core 0 bundle and relocate it."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast, importlib.metadata, json, os, platform, shutil, subprocess, sys, tempfile, time

H=Path(__file__).resolve().parent;R=H.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert len(sys.argv)==2, 'fresh attempt identifier required'
assert sys.argv[1].isalnum() or sys.argv[1].replace('-','').isalnum()
O=H/sys.argv[1];O.mkdir(exist_ok=False);start=time.monotonic()
live=read(R/'data/accounting-master/next-plan.json')['active_execution']
assert live['current_candidate']=='5.51;828 pages;not_ready'
candidate=R/live['current_pdf'];source=candidate.parent
inputs=['docs/design/spec/core-0.lark','docs/design/spec/core-contract.md','docs/design/spec/core-ir.schema.json',
 'docs/design/fixtures/core-ir-demo.json','docs/design/fixtures/core-demo-registry.json','docs/design/fixtures/demo-debt-package.json',
 'docs/design/fixtures/borrowings.json','docs/design/fixtures/borrowing.acc',
 'scripts/core_semantics.py','scripts/build_demo_registry.py','scripts/check_semantic_preparation.py','docs/design/research/tools.json']
locks={p:sha(R/p) for p in inputs}
for p in [candidate,R/live['standalone_pdf'],source/'chapters/09-implementation.tex',source/'chapters/11-contracts.tex',H/'build.py',H/'verify_relocated.py',R/'docs/plans/accounting-release-bundle-recovery-20261027.md']:
    locks[str(p.relative_to(R))]=sha(p)
dump(O/'source-lock.json',locks)
root=O/'bundle';root.mkdir()
for n in inputs:
    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
shutil.copyfile(H/'verify_relocated.py',root/'scripts/verify_relocated.py')
versions={n:importlib.metadata.version(n) for n in ['jsonschema','attrs','jsonschema-specifications','referencing','rpds-py']}
environment=dict(python=platform.python_version(),executable=sys.executable,distributions=versions,platform=platform.platform())
(root/'requirements-observed.txt').write_text('\n'.join(k+'=='+v for k,v in versions.items())+'\n')
registry=read(root/'docs/design/fixtures/core-demo-registry.json')
exports=[]
for r in registry['records']:
    if r['artifact'] is not None:
        p=(root/r['artifact']).resolve();assert p.is_relative_to(root.resolve()) and sha(p)==r['sha256']
    exports.append({k:r[k] for k in ['id','kind','artifact','sha256','pointer']})
assert len(exports)==17
imports={n:[ast.unparse(x) for x in ast.walk(ast.parse((root/n).read_text())) if isinstance(x,(ast.Import,ast.ImportFrom))] for n in inputs if n.endswith('.py')}
references=[dict(literal='spec/core-contract.md',resolved='docs/design/spec/core-contract.md',role='Historical Core 0 only; later portable profiles remain distinct'),
 dict(literal='spec/core-ir.schema.json',resolved='docs/design/spec/core-ir.schema.json',role='Historical structural schema; not a general semantic admission'),
 dict(literal='core-demo-registry.json',resolved='docs/design/fixtures/core-demo-registry.json',role='17 fixed exports'),
 dict(literal='research/tools.json',resolved='docs/design/research/tools.json',role='Historical software evidence index; external library files are not bundled')]
dump(root/'reference-map.json',dict(candidate='5.51',references=references,export_dependencies=exports,python_imports=imports))
(root/'README.md').write_text('''# Historical Core 0 specification component

This local bundle resolves the historical Core 0 contract/schema references in
AccDSL 5.51. It preserves the exact contract, schema, grammar, authored debt
fixture, 17-export registry and pure semantic validator. This component does
not contain all current portable/company/sector profiles or the full manuscript.

Run from this directory in the observed environment:

    env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 -I -B scripts/verify_relocated.py output-01

Use a fresh output directory for each invocation. No source writer is called.
The copied check_semantic_preparation.py and build_demo_registry.py main entry
points are retained reference material: do not run them to overwrite fixtures.
The new verifier calls only the pure validation and registry-construction APIs.
requirements-observed.txt records tested installed versions, not permission or
instructions to install software. Python version is in bundle-manifest.json.

Paths in reference-map.json are relative to this bundle. The normative files
retain their original wording and historical scope. No coercion to a later
profile or independent implementation acceptance is supplied. Source research
tools.json is a historical index, not evidence of current tool availability.

This is an internal reproducibility package. No retained papers or accounting
standards are copied. Redistribution rights for project material have not been
reviewed, so no public-distribution permission is asserted. Installed dependency
licence metadata is recorded separately; actual deployment notices require a
distribution-specific review.
''')
licences={}
for n in versions:
    meta=importlib.metadata.metadata(n)
    licences[n]={k:meta.get(k) for k in ['Name','Version','License','License-Expression','Home-page']}
dump(root/'dependency-metadata.json',dict(distributions=licences,redistribution='not reviewed; local verification only'))
files=[dict(path=str(p.relative_to(root)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(root.rglob('*')) if p.is_file()]
dump(root/'bundle-manifest.json',dict(profile='HistoricalCore0Bundle/1',environment=environment,files=files,source_pdfs={str(candidate.relative_to(R)):sha(candidate)},scope='Historical authored-debt specification/admission only',full_release_bundle=False))
relocated=Path(tempfile.mkdtemp(prefix='accdsl-core0-relocation-',dir='/tmp'))/'bundle'
shutil.copytree(root,relocated)
command=[sys.executable,'-I','-B',str(relocated/'scripts/verify_relocated.py'),'output-01']
env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
p=subprocess.run(command,cwd=relocated,env=env,capture_output=True,text=True,timeout=90)
(O/'stdout.txt').write_text(p.stdout);(O/'stderr.txt').write_text(p.stderr)
if (relocated/'output-01').exists():shutil.copytree(relocated/'output-01',O/'relocated-output')
for n,h in locks.items():assert sha(R/n)==h,n
git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
dump(O/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/release-bundle-recovery-20261027/build.py '+sys.argv[1],child_command=command,child_cwd=str(relocated),git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable; existing marker unusable',environment=environment,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',data_version=sha(root/'bundle-manifest.json'),plan_file='docs/plans/accounting-release-bundle-recovery-20261027.md',result_file=str((H/'result.md').relative_to(R)),wall_seconds=time.monotonic()-start,timestamp_utc=datetime.now(timezone.utc).isoformat(),exit_code=p.returncode))
assert p.returncode==0, 'relocation failed; inspect retained stderr and failure.json'
checks=read(O/'relocated-output/checks.json');assert checks['passed']
dump(O/'verification.json',dict(passed=True,files=len(files),frozen_exports=len(exports),checks=len(checks['checks']),protected_files=len(locks),relocated_root=str(relocated),source_preservation=True,full_release_bundle=False))
print(json.dumps(dict(passed=True,files=len(files),exports=len(exports),checks=len(checks['checks']),protected_files=len(locks),relocated=str(relocated))))
