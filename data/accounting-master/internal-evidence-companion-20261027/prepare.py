"""Merge checked component sets, refusing conflicts rather than choosing versions."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'data/accounting-master'
read=lambda p:json.loads(p.read_text())
digest=lambda p:sha256(p.read_bytes()).hexdigest()
components=[
    dict(id='source-reconstruction',unit='retained-source-reconstruction-20261027',
         preparation='preparation-01',manifest='source-manifest.json',attempt='attempt-01'),
    dict(id='source-to-report',unit='executable-evidence-closure-20261027',
         preparation='preparation-04',manifest='replay-manifest.json',attempt='attempt-04')]
files={}
for component in components:
    folder=BASE/component['unit']
    source=read(folder/component['preparation']/'bundle-manifest.json')
    assert read(folder/component['attempt']/'checks.json')['passed']
    component['driver']='data/accounting-master/'+component['unit']+'/replay.py'
    for name,row in source['entries'].items():
        assert digest(ROOT/name)==row['sha256'],name
        if name in files:
            assert files[name]['sha256']==row['sha256'],'component conflict: '+name
            files[name]['components'].append(component['id'])
        else:
            files[name]=dict(sha256=row['sha256'],bytes=row['bytes'],components=[component['id']])
    component['source_manifest_sha256']=digest(folder/component['preparation']/'bundle-manifest.json')
record=HERE/'preparation-01'
record.mkdir(exist_ok=False)
stage=Path(tempfile.mkdtemp(prefix='accdsl-internal-evidence-',dir='/tmp'))
for name,row in files.items():
    target=stage/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/name,target)
    assert digest(target)==row['sha256']
for component in components:
    folder=BASE/component['unit']
    # Exact component manifests, including original comparison scopes.
    dest=stage/component['manifest']
    shutil.copyfile(folder/component['preparation']/'bundle-manifest.json',dest)
    files[component['manifest']]=dict(sha256=digest(dest),bytes=dest.stat().st_size,
        components=[component['id']],purpose='unchanged child manifest')
    for name in ['README.md','result.md','environment-lock.json']:
        source=folder/name
        dest=stage/'component-notes'/component['id']/name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        files[str(dest.relative_to(stage))]=dict(sha256=digest(dest),bytes=dest.stat().st_size,
            components=[component['id']],purpose='scope and recorded environment')
for name in ['README.md','reproduce.py']:
    shutil.copyfile(HERE/name,stage/name)
    files[name]=dict(sha256=digest(stage/name),bytes=(stage/name).stat().st_size,
        components=['launcher'],purpose='single recipient command')
plan=Path('docs/plans/accounting-internal-evidence-companion-20261027.md')
(stage/plan).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/plan,stage/plan)
files[str(plan)]=dict(sha256=digest(stage/plan),bytes=(stage/plan).stat().st_size,
    components=['launcher'],purpose='reviewed assembly contract')
manifest=dict(profile='AccDSLInternalEvidenceCompanion/1',files=files,components=components,
    rights='internal only; source redistribution not established',full_release_closure=False)
for dest in [stage/'companion-manifest.json',record/'companion-manifest.json']:
    with dest.open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
summary=dict(stage=str(stage),files=len(files),shared_dependency_files=sum(len(r['components'])==2 for r in files.values()),
    bytes=sum(r['bytes'] for r in files.values()),manifest_sha256=digest(stage/'companion-manifest.json'))
with (record/'stage.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(summary))
