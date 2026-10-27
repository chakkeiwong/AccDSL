"""Freeze the completed source and Version 2.20 evidence; no regeneration."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib, importlib.util, json, os, platform, re, subprocess, sys, time

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
NEW=ROOT/'docs/design/proposal/manuscript-disruption-20261010'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
rel=lambda p:str(p.relative_to(ROOT))


def verify(h):
    for n,v in h.items(): assert sha(ROOT/n)==v,n


def save(n,d):
    with (OUT/n).open('x') as f:f.write(json.dumps(d,indent=2,ensure_ascii=False)+'\n')


def main():
    start=time.monotonic();began=datetime.now(timezone.utc)
    base=read(OUT/'baseline.json');prior_path=ROOT/base['prior_manifest'];prior=read(prior_path)
    assert sha(prior_path)==base['prior_manifest_sha256']==read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc={x['historical_path']:x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes={reloc.get(n,n):v for n,v in prior['artifact_hashes'].items()};verify(prior_hashes)
    input_reloc={x['historical_path']:x['preserved_path'] for x in read(OUT/'input-relocations.json')['relocations']}
    assert sha(ROOT/input_reloc[base['requirements_path']])==base['requirements_sha256']
    for x in read(OUT/'input-relocations.json')['relocations']:
        assert sha(ROOT/x['historical_path'])==x['restored_sha256']
    source=read(OUT/'source-checks.json');meaning=read(OUT/'meaning-checks.json');candidate=read(OUT/'candidate-checks.json')
    assert (source['passed'],meaning['passed'],candidate['passed'])==(36,35,16)
    assert source['failed']==meaning['failed']==candidate['failed']==0
    assert source['checker_sha256']==sha(OUT/'prepare.py')
    assert candidate['checker_sha256']==sha(OUT/'integrate.py')
    resolved_inputs={input_reloc.get(x['path'],x['path']):x['sha256'] for x in source['inputs']}
    verify(resolved_inputs);verify(meaning['inputs']);verify(candidate['inputs'])
    integration=read(OUT/'integration-baseline.json');verify(integration['protected_hashes'])
    helper=ROOT/'data/accounting-master/apple-legal-20261010/work_unit.py'
    assert sha(helper)==integration['helper_sha256']
    spec=importlib.util.spec_from_file_location('preservation_helpers',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);ancestors=h.ancestry()
    rendering=read(OUT/'render-manifest.json');assert rendering['pdf']==candidate['pdf']
    assert sha(ROOT/candidate['pdf']['path'])==candidate['pdf']['sha256']
    verify({x['path']:x['sha256'] for x in rendering['images']+[rendering['navigation_sheet']]})
    verify({x['path']:x['sha256'] for x in read(OUT/'inspection/manifest.json')})
    coverage=read(OUT/'coverage-update.json');assert coverage['not_semantic_completion']
    assert list(coverage['counts']['annual'].values())==[7,2,19]
    assert list(coverage['counts']['interim'].values())==[2,0,0]
    for r in coverage['records']:
        if 'added_evidence' in r:assert sha(ROOT/r['added_evidence']['path'])==r['added_evidence']['sha256']
    pointers={n:sha(ROOT/n) for n in reloc}
    for n in pointers:
        t=(ROOT/n).read_text()
        assert all(x in t for x in ['Version 2.20',candidate['pdf']['sha256'],'not_ready','annual-03','apple-business-interruption-20261010/result.md']),n
    road=(ROOT/'docs/plans/accounting-master-current.md').read_text();old=(ROOT/reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps=lambda t:[x for x in t.splitlines() if re.match(r'^\| G\d+ ',x)]
    assert len(gaps(road))==18 and gaps(road)==gaps(old)
    for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',ROOT/candidate['pdf']['path'])]:
        line=next(x for x in road.splitlines() if x.startswith(label+': '));link=re.search(r'\]\(([^)]+)\)',line).group(1)
        assert (ROOT/'docs/plans'/link).resolve()==target.resolve()
    diff=['git','diff','--check','--',*pointers,rel(OUT),rel(NEW),'docs/plans/accounting-apple-business-interruption-20261010.md']
    subprocess.run(diff,check=True,capture_output=True,text=True)
    save('closeout-checks.json',dict(passed=True,source_checks=36,meaning_checks=35,candidate_checks=16,
        prior_references=len(prior_hashes),ancestor_counts=ancestors,pointers=pointers,
        requirements_restored=True,input_relocations_verified=True,all_eighteen_gap_rows_preserved=True,
        exact_current_pdf_and_result_links=True,diff_check='passed'))
    hashes={rel(p):sha(p) for directory in [OUT,NEW] for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['run-manifest.json','completion.json']}
    hashes.update(prior_hashes);hashes.update(resolved_inputs);hashes.update(meaning['inputs']);hashes.update(candidate['inputs']);hashes.update(pointers)
    hashes[rel(prior_path)]=sha(prior_path);hashes[rel(prior_path.with_name('completion.json'))]=sha(prior_path.with_name('completion.json'))
    hashes['docs/plans/accounting-mission-requirements.md']=sha(ROOT/'docs/plans/accounting-mission-requirements.md');verify(hashes)
    commands=[json.loads(x) for x in (OUT/'commands.jsonl').read_text().splitlines()]
    commands += [dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(OUT/'check_meaning.py'),exit_code=0),
                 dict(command='CUDA_VISIBLE_DEVICES=-1 python3 '+rel(Path(__file__)),exit_code=0,started_at=began.isoformat(),wall_seconds=time.monotonic()-start),
                 dict(command=' '.join(diff),exit_code=0)]
    save('run-manifest.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),unit='Apple macroeconomic/interruption risk and Version 2.20 E01/C03/C08',
        git_commit=base['git_commit'],git_worktree='Extensive unrelated dirty work preserved; no commit or push',
        plan='docs/plans/accounting-apple-business-interruption-20261010.md',result=rel(OUT/'result.md'),pdf=candidate['pdf'],
        artifact_hashes=hashes,prior_manifest=rel(prior_path),prior_manifest_sha256=sha(prior_path),pointer_relocations=base['pointer_relocations'],input_relocations=read(OUT/'input-relocations.json')['relocations'],
        environment=dict(python_executable=sys.executable,python_prefix=sys.prefix,python_version=sys.version,platform=platform.platform(),conda_env=os.environ.get('CONDA_DEFAULT_ENV'),CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden'),
        data_version='Pinned Apple FY2024 annual PDF/text and FY2025 Q1 interim HTML/text; exact hashes retained',random_seeds='N/A deterministic documentary work',
        commands=commands,wall_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(base['recorded_at'])).total_seconds(),timing_scope='Successful retained baseline to final closeout; earlier failed attempts retained separately',
        full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',domain_acceptance='pending',network_requests=0))
    verify(hashes)
    save('completion.json',dict(status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=candidate['pdf'],source_checks=36,meaning_checks=35,candidate_checks=16,manifest_bound_files=len(hashes),full_readiness='not_ready',next_work='Annual-03 competitive-market risk'))
    print(json.dumps(dict(manifest_bound_files=len(hashes),manifest_sha256=sha(OUT/'run-manifest.json'),pages=candidate['pdf']['pages'],next='annual-03')))


if __name__=='__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    assert not (OUT/'completion.json').exists()
    main()
