"""Freeze the source/interface preparation; preserve ancestor release hashes."""
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

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    with (OUT / name).open('x') as f: f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(mapping):
    bad = [p for p,h in mapping.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not bad,bad[:6]


def main():
    started,timer=datetime.now(timezone.utc).isoformat(),time.monotonic()
    base=read(OUT/'baseline.json');prior_path=ROOT/base['prior_manifest'];prior=read(prior_path)
    assert sha(prior_path)==base['prior_manifest_sha256']==read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes={reloc.get(p,p):h for p,h in prior['artifact_hashes'].items()};verify(prior_hashes)
    probe=read(OUT/'checks.json');candidate=read(OUT/'candidate-checks.json')
    assert probe['passed']==35 and probe['failed']==0 and probe['checker_sha256']==sha(OUT/'probe.py')
    assert candidate['passed']==23 and candidate['failed']==0 and candidate['checker_sha256']==sha(OUT/'check_candidate.py')
    verify(probe['inputs']);verify(candidate['inputs'])
    pdf=candidate['pdf'];pointers={p:sha(ROOT/p) for p in reloc}
    for p in pointers:
        text=(ROOT/p).read_text()
        for token in ['Version 2.25',pdf['sha256'],'not_ready','docling-page-failure-20261010/result.md','28 complete','XBRL']:
            assert token in text,(p,token)
    current=(ROOT/'docs/plans/accounting-master-current.md').read_text()
    previous=(ROOT/reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps=lambda s:[x for x in s.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(current))==18 and gaps(current)==gaps(previous)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',ROOT/pdf['path'])]:
        line=next(x for x in current.splitlines() if x.startswith(label+': '))
        link=re.search(r'\]\(([^)]+)\)',line).group(1)
        assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    plan='docs/plans/accounting-docling-page-failure-20261010.md'
    cmd=['git','diff','--check','--',*pointers,rel(OUT),str(Path(pdf['path']).parent),plan]
    subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True)
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,check=True,capture_output=True,text=True).stdout.strip()
    assert head==base['git_commit']
    save('closeout-checks.json',dict(passed=True,source_fragment_checks=35,candidate_checks=23,
        prior_references=len(prior_hashes),current_pointer_hashes=pointers,all_eighteen_gap_rows_preserved=True,
        exact_current_links=True,scoped_diff_check='passed'))
    hashes=dict(prior_hashes);hashes.update(probe['inputs']);hashes.update(candidate['inputs'])
    hashes.update({rel(p):sha(p) for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                   and p.name not in {'run-manifest.json','completion.json'}})
    hashes.update({rel(p):sha(p) for p in (ROOT/Path(pdf['path']).parent).rglob('*') if p.is_file()})
    hashes.update(pointers);hashes[plan]=sha(ROOT/plan)
    hashes[base['prior_manifest']]=sha(prior_path);hashes[rel(prior_path.with_name('completion.json'))]=sha(prior_path.with_name('completion.json'))
    verify(hashes)
    runner='CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '
    build=read(OUT/'build-receipt.json')
    commands=[dict(command=runner+rel(OUT/'probe.py'),exit_code=0,wall_seconds=probe['wall_seconds']),
        dict(command=build['command'],workdir=build['workdir'],environment=build['environment'],exit_code=0,
             wall_seconds=None,timing_limitation=build['timing_limitation']),
        dict(command=runner+rel(OUT/'check_candidate.py'),exit_code=0,wall_seconds=candidate['wall_seconds']),
        dict(command=' '.join(cmd),exit_code=0),dict(command=runner+rel(Path(__file__)),exit_code=0,started_at=started)]
    save('run-manifest.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Docling page outcomes and Version 2.25 author repair E14/C07/C08',
        git_commit=head,git_worktree='Extensive unrelated dirty work preserved; no commit or push',
        plan=plan,result=rel(OUT/'result.md'),pdf=pdf,artifact_hashes=hashes,
        prior_manifest=base['prior_manifest'],prior_manifest_sha256=base['prior_manifest_sha256'],
        pointer_relocations=base['pointer_relocations'],commands=commands,
        acquisition=read(OUT/'acquisition-receipt.json'),
        surface_command=runner+'/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py '
            +str(Path(pdf['path']).parent/'sections/adapter-methods.tex')+' --pdf '+pdf['path']
            +' --output-json '+rel(OUT/'surface-audit.json')+' --output-md '+rel(OUT/'surface-audit.md')+' --max-examples 2',
        environment=dict(python_executable=sys.executable,python_prefix=sys.prefix,python_version=sys.version,
            platform=platform.platform(),conda_env='tfgpu executable selected directly',CUDA_VISIBLE_DEVICES='-1',
            cpu_gpu_status='CPU only; GPU devices intentionally hidden',docling_imported=False),
        data_version='Official Docling source pin eda5b5fc86d10b2b79a900ff3e69fc159d5f6014; synthetic stage outcomes; frozen Version 2.24',
        random_seeds='N/A deterministic source and method-fragment checks',
        wall_seconds=dict(probe=probe['wall_seconds'],candidate_check=candidate['wall_seconds'],
            closeout_through_manifest=time.monotonic()-timer,build=None,full_unit_elapsed=None,
            limitation='No full interactive or build elapsed timing captured; component timings are not a total runtime'),
        author_reading=dict(body=list(range(137,142)),navigation=list(range(1,8)),bibliography=[164],dpi=120),
        full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',domain_acceptance='pending',
        network_requests=1,installation=False,product_runtime=False))
    verify(hashes)
    save('completion.json',dict(status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),
        pdf=pdf,source_fragment_checks=35,candidate_checks=23,manifest_bound_files=len(hashes),full_readiness='not_ready',
        next_work='Exact XBRL Software Notice/component source audit'))
    print(json.dumps(dict(manifest_bound_files=len(hashes),manifest_sha256=sha(OUT/'run-manifest.json'),
        source_fragment_checks=35,candidate_checks=23,pages=pdf['pages'])))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
