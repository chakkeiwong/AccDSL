"""Assemble and reproduce a package revision of unchanged 5.54-R2 documents."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R/'docs/design/proposal/manuscript-financing-v554r2-20261027'
T = R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027'
E = R/'data/accounting-master/executable-evidence-closure-20261027'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def prepare():
    assert not T.exists() and not (D/'package-record.json').exists()
    baseline=read(D/'baseline.json')
    assert sha(B/'package-manifest.json')==baseline['baseline_manifest_sha256']
    for p,h in baseline['sources'].items():assert sha(R/p)==h
    assert (R/'docs/AccDSL-latest.pdf').resolve()==B/'accounting-product-proposal.pdf'
    T.mkdir()
    for row in baseline['baseline_files']:
        p=B/row['path'];assert sha(p)==row['sha256']
        q=T/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    for src,name in [('package-README.md','README.md'),('package-DEPENDENCIES.md','DEPENDENCIES.md')]:
        (T/name).write_bytes((D/src).read_bytes())
    component=T/'companions/source-history-replay';component.mkdir()
    mapping={'replay-bundle.tar.gz':'replay-bundle.tar.gz',
             'preparation-04/bundle-manifest.json':'bundle-manifest.json',
             'preservation.json':'preservation.json','environment-lock.json':'environment-lock.json',
             'execution-review.md':'execution-review.md','result.md':'upstream-result.md'}
    for source,name in mapping.items():(component/name).write_bytes((E/source).read_bytes())
    (component/'README.md').write_bytes((D/'component-README.md').read_bytes())
    (component/'unpack_replay.py').write_bytes((D/'unpack_replay.py').read_bytes())
    additions=[str(p.relative_to(T)) for p in component.iterdir()]
    edition={name:sha(T/name) for name in ['accounting-product-proposal.pdf','simulation-foundations.pdf',
                                         'accounting-product-proposal.tex','simulation-foundations.tex']}
    revision={'manuscript_edition':'5.54-R2','package_revision':2,'release_status':'not_ready',
        'predecessor_package':str(B.relative_to(R)),'predecessor_manifest_sha256':baseline['baseline_manifest_sha256'],
        'unchanged_manuscripts':edition,'changed_existing_files':['README.md','DEPENDENCIES.md'],
        'added_component':'companions/source-history-replay',
        'component_archive_sha256':sha(component/'replay-bundle.tar.gz'),
        'component_dependency_manifest_sha256':sha(component/'bundle-manifest.json'),
        'source_replay_result':str((E/'result.md').relative_to(R)),
        'document_reproduction':'data/accounting-master/release-pursuit-20261027/refinancing-domain/relocation-01/result.json',
        'document_rendering':'data/accounting-master/release-pursuit-20261027/refinancing-domain/rendered-review.json',
        'package_result':str((D/'result.md').relative_to(R)),
        'boundary':'Internal retained-input replay component; no manuscript argument change, full runtime closure or redistribution clearance.'}
    dump(T/'PACKAGE-REVISION.json',revision);additions.append('PACKAGE-REVISION.json')
    manifest=read(B/'package-manifest.json')
    manifest.update(candidate='5.54-R2;package_revision2;not_ready',
        manifest_self_hash=str((D/'package-record.json').relative_to(R)))
    for path in additions:manifest['files'].append({'path':path})
    for row in manifest['files']:
        p=T/row['path'];row.update(sha256=sha(p),bytes=p.stat().st_size)
    dump(T/'package-manifest.json',manifest)
    changed=[row['path'] for row in baseline['baseline_files'] if sha(T/row['path'])!=row['sha256']]
    assert set(changed)=={'README.md','DEPENDENCIES.md'}
    p=subprocess.run([sys.executable,'-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True,check=True)
    record={'passed':True,'candidate':'5.54-R2;package_revision2;not_ready',
        'manifest_sha256':sha(T/'package-manifest.json'),'files':len(manifest['files']),
        'verification':json.loads(p.stdout),'changed_files':changed,'added_files':sorted(additions),
        'unchanged_manuscripts':edition,'predecessor_manifest_sha256':baseline['baseline_manifest_sha256']}
    dump(D/'package-record.json',record)
    print(json.dumps({'prepared':True,'files':record['files'],'added':len(additions),'changed':changed}))

def stage():
    assert not (D/'stage.json').exists()
    assert sha(T/'package-manifest.json')==read(D/'package-record.json')['manifest_sha256']
    target=Path(tempfile.mkdtemp(prefix='accdsl-v554r2p2-package-',dir='/tmp'))
    for row in read(T/'package-manifest.json')['files']:
        p=T/row['path'];assert sha(p)==row['sha256']
        q=target/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    (target/'package-manifest.json').write_bytes((T/'package-manifest.json').read_bytes())
    extracted=target/'replay-extracted'
    command=[sys.executable,'-I','-B',str(target/'companions/source-history-replay/unpack_replay.py'),
             '--destination',str(extracted)]
    started=time.monotonic();p=subprocess.run(command,cwd='/tmp',capture_output=True,text=True,check=True)
    report={'package':str(target),'extracted':str(extracted),'command':command,'cwd':'/tmp',
        'extract_seconds':time.monotonic()-started,'extraction':json.loads(p.stdout),
        'timestamp_utc':datetime.now(timezone.utc).isoformat()}
    manifest=read(extracted/'replay-manifest.json')
    assert len(manifest['entries'])==234
    assert sha(extracted/'replay-manifest.json')==sha(T/'companions/source-history-replay/bundle-manifest.json')
    for path,row in manifest['entries'].items():assert sha(extracted/path)==row['sha256']
    dump(D/'stage.json',report);print(json.dumps(report))

def replay():
    assert not (D/'replay-command.json').exists() and not (D/'replay.stdout').exists()
    stage=read(D/'stage.json');root=Path(stage['extracted']);out=root/'output-01'
    cmd=[sys.executable,'-I','-B',str(root/'data/accounting-master/executable-evidence-closure-20261027/replay.py'),
         '--root',str(root),'--output',str(out)]
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
    start=time.monotonic()
    with (D/'replay.stdout').open('x') as log:
        p=subprocess.run(cmd,cwd='/tmp',env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    report={'command':cmd,'cwd':'/tmp','exit_code':p.returncode,'wall_seconds':time.monotonic()-start,
        'output':str(out),'environment':{'CUDA_VISIBLE_DEVICES':'-1','PYTHONDONTWRITEBYTECODE':'1'},
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'plan':'docs/plans/accounting-replay-package-inclusion-20261027.md'}
    dump(D/'replay-command.json',report);print(json.dumps(report))
    raise SystemExit(p.returncode)

def verify():
    assert not (D/'verification.json').exists()
    record=read(D/'replay-command.json');assert record['exit_code']==0
    out=Path(record['output']);checks=read(out/'checks.json');audit=read(out/'access-audit.json')
    assert checks['passed'] and checks['compatibility_exchanges']==26 and checks['selected_history_exchanges']==11
    assert checks['obligations']==180 and all(x['passed'] for x in checks['details'])
    assert audit['violations']==[] and audit['hook_before_project_imports']
    assert not [x for x in audit['reads_and_writes'] if x['path'].startswith(str(R)+'/')]
    target=Path(read(D/'stage.json')['package'])
    for base in [T,target]:
        p=subprocess.run([sys.executable,'-I','-B','verify_package.py'],cwd=base,capture_output=True,text=True,check=True)
        assert json.loads(p.stdout)['pass']
    for row in read(D/'baseline.json')['baseline_files']:assert sha(B/row['path'])==row['sha256']
    for name,h in read(D/'package-record.json')['unchanged_manuscripts'].items():assert sha(target/name)==h==sha(B/name)
    saved=D/'replay-result';saved.mkdir()
    outputs={}
    for source in sorted(out.iterdir()):
        assert source.is_file();dest=saved/source.name;dest.write_bytes(source.read_bytes())
        outputs[source.name]=sha(dest)
    result={'passed':True,'checks':checks['checks'],'exchanges':37,'preserved_issuer_obligations':180,
        'manuscripts_unchanged':True,'package_files':read(D/'package-record.json')['files'],
        'no_original_worktree_access':True,'access_audit':'replay-result/access-audit.json',
        'raw_outputs':outputs,'normalized_fields':checks['normalized_fields'],
        'certificate_comparisons':checks['certificate_comparisons'],
        'scope':'Copied internal package, validated archive and native retained-input replay; no new manuscript build or clean installation.'}
    dump(D/'verification.json',result)
    print(json.dumps({k:result[k] for k in ['passed','checks','exchanges','package_files','manuscripts_unchanged']}))

if __name__=='__main__':
    {'prepare':prepare,'stage':stage,'replay':replay,'verify':verify}[sys.argv[1]]()
