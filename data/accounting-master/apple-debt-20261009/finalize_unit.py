"""Freeze the completed debt unit after checking all four current records."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import bs4
import fitz

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
NEW=ROOT/'docs/design/proposal/manuscript-debt-20261009'
if (OUT/'completion.json').exists():raise SystemExit('Closed unit; preserve it')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def save(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def verify(hashes):
    bad=[n for n,h in hashes.items() if not (ROOT/n).exists() or sha(ROOT/n)!=h]
    assert not bad,bad

baseline=read(OUT/'baseline.json');candidate=read(OUT/'candidate-checks.json');evidence=read(OUT/'evidence-checks.json')
assert candidate['failed']==evidence['failed']==0
assert candidate['passed']==33 and evidence['passed']==162
assert candidate['checker_sha256']==sha(OUT/'check_candidate.py')
assert evidence['checker_sha256']==sha(OUT/'prepare_evidence.py')
assert sha(ROOT/candidate['pdf']['path'])==candidate['pdf']['sha256']
for hashes in [candidate['inputs'],evidence['inputs'],evidence['output_hashes'],baseline['protected_hashes']]:verify(hashes)
rel={r['historical_path']:r['preserved_path'] for r in baseline['pointer_relocations']}
previous=read(ROOT/baseline['prior_manifest'])
verify({rel.get(n,n):h for n,h in previous['artifact_hashes'].items()})
previous_completion=read((ROOT/baseline['prior_manifest']).parent/'completion.json')
assert previous_completion['manifest_sha256']==sha(ROOT/baseline['prior_manifest'])
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:verify(history[k])
p19=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json')
oldrel={r['historical_path']:r['preserved_path'] for r in p19['relocations']}
verify({oldrel.get(n,n):h for n,h in p19['p19_historical_artifact_hashes'].items()})
review=read(OUT/'render-review.json')
assert review['author_review_sha256']==sha(OUT/'author-review.md')
assert review['render_manifest_sha256']==sha(OUT/'render-manifest.json')
assert review['human_acceptance']==review['independent_reader']=='pending'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==baseline['git_commit']

pointers=[]
for row in baseline['pointer_relocations']:
    assert sha(ROOT/row['preserved_path'])==row['sha256']
    p=ROOT/row['historical_path'];t=p.read_text()
    assert 'Version 2.12' in t and 'E01' in t and 'Note 4' in t,(p,'current unit/next query')
    if 'requirements' not in p.name:assert 'not_ready' in t
    links=re.findall(r'\[[^\]]+\]\(([^)]+)\)',t)
    bad=[s for s in links if not s.startswith(('http:','https:','#')) and not (p.parent/s.split('#')[0]).exists()]
    assert not bad,(p,bad)
    pointers.append(dict(path=row['historical_path'],sha256=sha(p),links_checked=len(links),broken_links=bad))
roadmap=(ROOT/'docs/plans/accounting-master-current.md').read_text()
gaps=re.findall(r'^\| (G\d+) —',roadmap,re.M)
assert len(gaps)==18 and set(gaps)=={f'G{n}' for n in range(1,19)}
assert '136 unverified publication dates' in roadmap
assert all(f'E{n}' in roadmap for n in ['01','05','07','08','14'])
assert '40 outstanding exhibit targets' in roadmap
expected_links={
    'Latest substantive result':('Apple debt unit','../../data/accounting-master/apple-debt-20261009/result.md'),
    'Current manuscript':('Version 2.12 PDF','../design/proposal/manuscript-debt-20261009/accounting-product-proposal.pdf'),
}
for label,(title,target) in expected_links.items():
    matches=re.findall(r'^'+re.escape(label)+r': \[([^\]]+)\]\(([^)]+)\)\.',roadmap,re.M)
    assert matches==[(title,target)],(label,matches)
assert '146-page Version 2.12' in roadmap
assert 'Next: complete annual/interim Note 4' in roadmap
assert 'Plan and audit E01/C03 full annual Note 9' not in roadmap
result=(OUT/'result.md').read_text()
assert candidate['pdf']['sha256'] in result and '162 source/arithmetic and 33 candidate/preservation' in result
assert read(OUT/'acquisition.json')['network_requests']==0

now=datetime.now(timezone.utc);start=datetime.fromisoformat(baseline['recorded_at'])
save('closeout-checks.json',dict(recorded_at=now.isoformat(),passed=True,pointer_checks=pointers,
    semantic_current_links=expected_links,baseline_files=len(baseline['protected_hashes']),
    previous_manifest_references=len(previous['artifact_hashes']),historical_preservation_counts=candidate['preservation_counts'],
    all_eighteen_gaps_preserved=True,source_and_candidate_outputs_current=True,
    source_check_runs=3,source_render_runs=3,candidate_check_runs=2,build_attempts=1,successful_builds=1,
    full_readiness='not_ready',next_work='Audit complete annual/interim Note 4 cash, securities, restrictions, liquidity and receivable concentrations with declared dependencies.'))
plan=ROOT/'docs/plans/accounting-apple-debt-20261009.md'
artifacts={str(p.relative_to(ROOT)):sha(p) for base in [OUT,NEW] for p in base.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','completion.json'}}
artifacts[str(plan.relative_to(ROOT))]=sha(plan)
for row in pointers:artifacts[row['path']]=row['sha256']
prefix='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-debt-20261009/'
commands=[
    dict(command=prefix+'prepare_evidence.py',runs=3,exit_codes=[1,0,0],final_wall_seconds=evidence['wall_seconds'],
         repairs='Narrow original-PDF displaced superscript normalization; later ownership of output hashes corrected. Prior scripts/reports preserved.'),
    dict(command=prefix+'render_sources.py',runs=3,exit_codes=[0,0,0],
         repairs='Rebind after evidence repair; then restore par-value unit exception in derived heading. Prior views retained.'),
    dict(command=prefix+'build_candidate.py',runs=1,exit_code=0,receipt='data/accounting-master/apple-debt-20261009/build-receipt.json'),
    dict(command=prefix+'render_candidate.py',runs=1,exit_code=0),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-debt-20261009/sections/apple-debt.tex --pdf docs/design/proposal/manuscript-debt-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-debt-20261009/surface-audit.json --output-md data/accounting-master/apple-debt-20261009/surface-audit.md',exit_code=0),
    dict(command=prefix+'check_candidate.py',runs=2,exit_codes=[1,0],final_wall_seconds=candidate['wall_seconds'],
         repair='Header row initially parsed as numbers; require all three data cells numeric. Manuscript unchanged.'),
    dict(command='git diff --check -- docs/plans/accounting-master-checkpoint.md docs/plans/accounting-master-current.md docs/plans/accounting-continuation-requirements-20261007.md data/accounting-master/next-plan.md',exit_code=0),
    dict(command=prefix+'finalize_unit.py',runs=1,exit_code=0),
]
build=read(OUT/'build-receipt.json')
commands.append(dict(command=build['command'],cwd=build['cwd'],environment=build['environment'],exit_code=build['exit_code'],wall_seconds=build['wall_seconds']))
save('run-manifest.json',dict(recorded_at=now.isoformat(),git_commit=head,
    git_worktree='Execution baseline is the checked EPS Version 2.11 commit. This unit is not yet committed; unrelated dirty work preserved.',
    environment=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),pymupdf=fitz.VersionBind,beautifulsoup=bs4.__version__,
        cpu_gpu='CPU document/arithmetic helpers; GPU intentionally hidden with CUDA_VISIBLE_DEVICES=-1',cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        latex='LuaLaTeX via latexmk; explicit writable /tmp TEXMFVAR and TEXMFCACHE, no install'),
    data_version=evidence['inputs'],random_seeds='N/A: deterministic documentary/arithmetic work; issuer Monte Carlo assertion not replicated',
    plan=str(plan.relative_to(ROOT)),result=str((OUT/'result.md').relative_to(ROOT)),
    audit='Pre-execution skeptical/default/evidence audit passed; full declared notes and dependencies checked before integration, meaning limits retained.',
    commands=commands,source_render_receipt=str((OUT/'source-render-receipt.json').relative_to(ROOT)),acquisition=read(OUT/'acquisition.json'),
    candidate_creation=dict(baseline='docs/design/proposal/manuscript-eps-20261009',candidate=str(NEW.relative_to(ROOT)),
        method='Copy all TeX/bibliography/grammar sources, add one source-backed debt section, one inclusion and version update; no old display or reference deletion',
        reader_delta='Annual debt measurement/cash distinction, net/gross refinancing and dated rate/FX-risk targets'),
    wall_time=dict(start_utc=start.isoformat(),end_utc=now.isoformat(),elapsed_seconds=(now-start).total_seconds(),
        scope='Whole unit interval includes session resumption, source/PDF inspection and documentation; individual build and checker seconds recorded separately'),
    artifact_hashes=artifacts,preservation=dict(baseline_files=len(baseline['protected_hashes']),preceding_manifest_references=len(previous['artifact_hashes']),
        prior_manifest=baseline['prior_manifest'],historical=candidate['preservation_counts'],pointers=baseline['pointer_relocations']),
    readiness='not_ready',independent_reader='pending',human_acceptance='pending',
    scope='Two full debt notes with thirteen source dependencies and one retained prior query; exact displayed-centre consequences and a scoped hypothetical principal round trip, not full histories, operative accounting compliance, a replicated risk model or product implementation.'))
verify(artifacts)
completion=dict(recorded_at=now.isoformat(),status='bounded_unit_complete_with_wider_gaps',manifest_sha256=sha(OUT/'run-manifest.json'),
    pdf=candidate['pdf'],source_checks=evidence['passed'],candidate_checks=candidate['passed'],artifacts_verified=len(artifacts),readiness='not_ready',
    next_work='E01/C03: audit complete annual/interim Note 4 cash, marketable securities, restrictions, liquidity and receivable concentrations with policy/statement/MD&A dependencies; preserve completed hedge/escrow results.')
save('completion.json',completion)
print(json.dumps(completion))
