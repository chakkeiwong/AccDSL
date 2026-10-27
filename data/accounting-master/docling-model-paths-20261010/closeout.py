"""Freeze this unit once, preserving prior live-pointer identities."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def save(name,data):
    with (OUT/name).open('x') as f:f.write(json.dumps(data,indent=2,ensure_ascii=False)+'\n')


def verify(mapping):
    bad=[p for p,h in mapping.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not bad,bad[:5]


def main():
    started,tick=datetime.now(timezone.utc).isoformat(),time.monotonic()
    base=read(OUT/'baseline.json');priorpath=ROOT/base['prior_manifest'];prior=read(priorpath)
    assert sha(priorpath)==base['prior_manifest_sha256']==read(priorpath.with_name('completion.json'))['manifest_sha256']
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in prior['artifact_hashes'].items()};verify(inherited)
    checks=read(OUT/'checks.json');assert checks['passed']==93 and checks['failed']==0
    assert checks['checker_sha256']==sha(OUT/'validate.py');verify(checks['inputs'])
    pdf=checks['pdf'];assert sha(ROOT/pdf['path'])==pdf['sha256']
    pointers={p:sha(ROOT/p) for p in reloc}
    for p in pointers:
        body=(ROOT/p).read_text()
        for token in ['Version 2.26',pdf['sha256'],'not_ready','docling-model-paths-20261010/result.md','93']:
            assert token in body,(p,token)
    current=(ROOT/'docs/plans/accounting-master-current.md').read_text()
    previous=(ROOT/reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps=lambda s:[x for x in s.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(current))==18 and gaps(current)==gaps(previous)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',ROOT/pdf['path'])]:
        line=next(x for x in current.splitlines() if x.startswith(label+': '));link=re.search(r'\]\(([^)]+)\)',line).group(1)
        assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    plan='docs/plans/accounting-docling-model-paths-20261010.md'
    cmd=['git','diff','--check','--',*pointers,rel(OUT),'docs/design/proposal/manuscript-model-paths-20261010',plan]
    subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert head==base['git_commit']
    save('closeout-checks.json',dict(passed=True,prior_references=len(inherited),documentary_candidate_checks=93,
        current_pointer_hashes=pointers,eighteen_gap_rows_unchanged=True,current_links_correct=True,scoped_diff_check='passed'))
    hashes=dict(inherited);hashes.update(checks['inputs']);hashes.update(pointers)
    for directory in [OUT,ROOT/'docs/design/proposal/manuscript-model-paths-20261010']:
        hashes.update({rel(p):sha(p) for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in {'run-manifest.json','completion.json'}})
    hashes[plan]=sha(ROOT/plan);hashes[base['prior_manifest']]=sha(priorpath);hashes[rel(priorpath.with_name('completion.json'))]=sha(priorpath.with_name('completion.json'));verify(hashes)
    build=read(OUT/'build-receipt.json');prep=read(OUT/'preparation-receipt.json')
    save('run-manifest.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),unit='Docling exact PDF model/backend source preparation E14/C07',
        git_commit=head,git_worktree='Unrelated dirty work preserved; no commit or push',plan=plan,result=rel(OUT/'result.md'),pdf=pdf,
        artifact_hashes=hashes,prior_manifest=base['prior_manifest'],prior_manifest_sha256=base['prior_manifest_sha256'],pointer_relocations=base['pointer_relocations'],
        commands=[dict(command='acquire.py with 25 exact source paths in bounded batches',receipts=rel(OUT/'acquisitions.json'),distinct_raw_urls=25,successful_raw=24,failed_raw=1),
                  dict(command='curl pinned Git tree and immutable blob metadata',receipts=rel(OUT/'metadata-receipts.json')),
                  dict(command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '+rel(OUT/'prepare.py'),receipt=rel(OUT/'preparation-receipt.json'),correction=rel(OUT/'preparation-correction.json')),
                  build,dict(command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '+rel(OUT/'validate.py'),exit_code=0,wall_seconds=checks['wall_seconds']),
                  dict(command=cmd,exit_code=0),dict(command='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '+rel(Path(__file__)),started_at=started,exit_code=0)],
        environment=dict(python_executable=sys.executable,python_prefix=sys.prefix,python_version=sys.version,platform=platform.platform(),conda_env='tfgpu executable selected directly',CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden; no model imports'),
        data_version='Docling commit eda5b5fc86d10b2b79a900ff3e69fc159d5f6014; no model weights acquired',random_seeds='N/A documentary audit',
        wall_seconds=dict(preparation=prep['wall_seconds'],build=build['wall_seconds'],validation=checks['wall_seconds'],closeout_through_manifest=time.monotonic()-tick,full_interactive_elapsed=None),
        network=dict(distinct_urls=27,attempts=28,successful_responses=26,sandbox_dns_failures=1,trusted_timeouts=1,weights_or_packages_downloaded=False),
        full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',domain_acceptance='pending',distribution_admission=False))
    verify(hashes)
    save('completion.json',dict(status='bounded_source_and_manuscript_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),manifest_bound_files=len(hashes),pdf=pdf,checks=93,full_readiness='not_ready',next_work='Heron/TableFormer repository metadata and model terms without weights'))
    print(json.dumps(dict(manifest_bound_files=len(hashes),manifest_sha256=sha(OUT/'run-manifest.json'),checks=93,pages=pdf['pages'])))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and not (OUT/'completion.json').exists()
    main()
