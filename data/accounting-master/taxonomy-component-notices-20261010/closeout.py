"""Freeze source-only component preparation with live-pointer relocation."""
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


def save(name,value):
    with (OUT/name).open('x') as f:f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def verify(mapping):
    bad=[p for p,h in mapping.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not bad,bad[:5]


def main():
    started,timer=datetime.now(timezone.utc).isoformat(),time.monotonic()
    base=read(OUT/'baseline.json');prior_path=ROOT/base['prior_manifest'];prior=read(prior_path)
    assert sha(prior_path)==base['prior_manifest_sha256']==read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    inherited={reloc.get(p,p):h for p,h in prior['artifact_hashes'].items()};verify(inherited)
    checks=read(OUT/'checks.json');assert checks['passed']==112 and checks['failed']==0
    assert checks['checker_sha256']==sha(OUT/'validate.py');verify(checks['inputs'])
    pdf=base['pdf'];assert sha(ROOT/pdf['path'])==pdf['sha256']
    pointers={p:sha(ROOT/p) for p in reloc}
    for p in pointers:
        text=(ROOT/p).read_text()
        for token in ['Version 2.25',pdf['sha256'],'not_ready','taxonomy-component-notices-20261010/result.md','112','Docling']:
            assert token in text,(p,token)
    current=(ROOT/'docs/plans/accounting-master-current.md').read_text()
    previous=(ROOT/reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps=lambda s:[x for x in s.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(current))==18 and gaps(current)==gaps(previous)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',ROOT/pdf['path'])]:
        line=next(x for x in current.splitlines() if x.startswith(label+': '))
        link=re.search(r'\]\(([^)]+)\)',line).group(1)
        assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    plan='docs/plans/accounting-taxonomy-component-notices-20261010.md'
    cmd=['git','diff','--check','--',*pointers,rel(OUT),plan]
    subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    assert head==base['git_commit']
    save('closeout-checks.json',dict(passed=True,documentary_checks=112,prior_references=len(inherited),
        current_pointer_hashes=pointers,all_eighteen_gap_rows_preserved=True,exact_current_links=True,
        scoped_diff_check='passed',manuscript_unchanged=True,distribution_admission=False))
    hashes=dict(inherited);hashes.update(checks['inputs']);hashes.update(pointers)
    hashes.update({rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                   and p.name not in {'run-manifest.json','completion.json'}})
    hashes[plan]=sha(ROOT/plan);hashes[base['prior_manifest']]=sha(prior_path)
    hashes[rel(prior_path.with_name('completion.json'))]=sha(prior_path.with_name('completion.json'))
    verify(hashes)
    runner='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '
    inventory=read(OUT/'notice-inventory.json')
    save('run-manifest.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Taxonomy component embedded-notice source audit E14/C07',git_commit=head,
        git_worktree='Extensive unrelated dirty work preserved; no commit or push',plan=plan,result=rel(OUT/'result.md'),
        pdf=pdf,manuscript_changed=False,artifact_hashes=hashes,
        prior_manifest=base['prior_manifest'],prior_manifest_sha256=base['prior_manifest_sha256'],
        pointer_relocations=base['pointer_relocations'],
        commands=[dict(command=runner+rel(OUT/'inventory.py'),exit_code=0,wall_seconds=inventory['wall_seconds'],
                       rejected_prior_inventory='attempt-01-context-incomplete'),
                  dict(command=runner+rel(OUT/'validate.py'),exit_code=0,wall_seconds=checks['wall_seconds']),
                  dict(command=' '.join(cmd),exit_code=0),
                  dict(command=runner+rel(Path(__file__)),exit_code=0,started_at=started)],
        environment=dict(python_executable=sys.executable,python_prefix=sys.prefix,python_version=sys.version,
                         platform=platform.platform(),conda_env='tfgpu executable selected directly',
                         CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden'),
        data_version='Hash-bound 27-node Apple FY2024 static taxonomy graph; retained XBRL/FASB notices, no new acquisitions',
        random_seeds='N/A deterministic documentary checks',
        wall_seconds=dict(inventory=inventory['wall_seconds'],validation=checks['wall_seconds'],
            closeout_through_manifest=time.monotonic()-timer,full_unit_elapsed=None,
            limitation='Full interactive author elapsed time not recorded'),
        full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',domain_acceptance='pending',
        distribution_admission=False,network_requests=0,new_pdf_review=False))
    verify(hashes)
    save('completion.json',dict(status='bounded_source_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),
        pdf=pdf,documentary_checks=112,manifest_bound_files=len(hashes),full_readiness='not_ready',
        next_work='Pinned Docling model/backend options and exact dependency preparation'))
    print(json.dumps(dict(manifest_bound_files=len(hashes),manifest_sha256=sha(OUT/'run-manifest.json'),
                          documentary_checks=112,pages=pdf['pages'])))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
