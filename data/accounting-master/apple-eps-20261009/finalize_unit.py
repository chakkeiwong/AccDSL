"""Bind the completed documentary unit after sequential pointer updates."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
import bs4
import fitz

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
NEW=ROOT/'docs/design/proposal/manuscript-eps-20261009'
if (OUT/'completion.json').exists():raise SystemExit('Closed unit; preserve it')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
baseline=read(OUT/'baseline.json');candidate=read(OUT/'candidate-checks.json');evidence=read(OUT/'evidence-checks.json')
assert candidate['failed']==evidence['failed']==0
assert candidate['checker_sha256']==sha(OUT/'check_candidate.py')
assert evidence['checker_sha256']==sha(OUT/'prepare_evidence.py')
assert sha(ROOT/candidate['pdf']['path'])==candidate['pdf']['sha256']
for hashes in [candidate['inputs'],evidence['inputs'],evidence['output_hashes'],baseline['protected_hashes']]:
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
rel={r['historical_path']:r['preserved_path'] for r in baseline['pointer_relocations']}
previous=read(ROOT/baseline['prior_manifest'])
assert all(sha(ROOT/rel.get(n,n))==h for n,h in previous['artifact_hashes'].items())
previous_completion=read((ROOT/baseline['prior_manifest']).parent/'completion.json')
assert previous_completion['manifest_sha256']==sha(ROOT/baseline['prior_manifest'])
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:
    assert all(sha(ROOT/n)==h for n,h in history[k].items())
p19=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json')
r={x['historical_path']:x['preserved_path'] for x in p19['relocations']}
assert all(sha(ROOT/r.get(n,n))==h for n,h in p19['p19_historical_artifact_hashes'].items())
review=read(OUT/'render-review.json')
assert review['author_review_sha256']==sha(OUT/'author-review.md')
assert review['render_manifest_sha256']==sha(OUT/'render-manifest.json')
assert review['human_acceptance']==review['independent_reader']=='pending'
pointers=[]
for row in baseline['pointer_relocations']:
    assert sha(ROOT/row['preserved_path'])==row['sha256']
    p=ROOT/row['historical_path'];t=p.read_text()
    assert 'Version 2.11' in t and 'E01' in t and 'debt' in t.lower()
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
assert read(OUT/'acquisition.json')['network_requests']==0
now=datetime.now(timezone.utc);start=datetime.fromisoformat(baseline['recorded_at'])
save('closeout-checks.json',dict(recorded_at=now.isoformat(),passed=True,pointer_checks=pointers,
    baseline_files=len(baseline['protected_hashes']),previous_manifest_references=len(previous['artifact_hashes']),
    historical_preservation_counts=candidate['preservation_counts'],all_eighteen_gaps_preserved=True,
    source_and_candidate_outputs_current=True,build_attempts=4,successful_builds=2,
    source_check_runs=3,source_render_runs=3,full_readiness='not_ready'))
plan=ROOT/'docs/plans/accounting-apple-eps-20261009.md'
artifacts={str(p.relative_to(ROOT)):sha(p) for base in [OUT,NEW] for p in base.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','completion.json'}}
artifacts[str(plan.relative_to(ROOT))]=sha(plan)
for row in pointers:artifacts[row['path']]=row['sha256']
prefix='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-eps-20261009/'
commands=[dict(command=prefix+'prepare_evidence.py',runs=3,final_exit_code=0,final_wall_seconds=evidence['wall_seconds'],
               first_failure='One full-text check rejected a PDF header-order difference; exact header permutation repair documented'),
          dict(command=prefix+'render_sources.py',runs=3,final_exit_code=0,
               repairs='Clipped labels and column alignment repaired; superseded views preserved'),
          dict(command=prefix+'render_candidate.py',exit_code=0,runs=1),
          dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-eps-20261009/sections/apple-eps-ownership.tex --pdf docs/design/proposal/manuscript-eps-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-eps-20261009/surface-audit.json --output-md data/accounting-master/apple-eps-20261009/surface-audit.md',exit_code=0),
          dict(command=prefix+'check_candidate.py',exit_code=0,runs=1,wall_seconds=candidate['wall_seconds']),
          dict(command=prefix+'finalize_unit.py',exit_code=0,runs=1)]
build=read(OUT/'build-receipt.json')
for i,attempt in enumerate(build['attempts']):
    commands.append(dict(command=build['command'].replace(' -g ', ' ') if i==0 else build['command'],cwd=build['cwd'],**attempt))
save('run-manifest.json',dict(recorded_at=now.isoformat(),git_commit=baseline['git_commit'],
    git_worktree='User-requested asset/tax checkpoint commit completed before this unit; unrelated dirty work preserved. This records the execution baseline, not a later commit of its outputs.',
    environment=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),pymupdf=fitz.VersionBind,beautifulsoup=bs4.__version__,cpu_gpu='CPU document/arithmetic helpers; GPU intentionally hidden with CUDA_VISIBLE_DEVICES=-1',cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),latex='LuaLaTeX via latexmk, trusted existing font cache'),
    data_version=evidence['inputs'],random_seeds='N/A: deterministic source/arithmetic work',
    plan=str(plan.relative_to(ROOT)),result=str((OUT/'result.md').relative_to(ROOT)),
    audit='Skeptical/default/evidence audit before execution; additional purchase/comparative/policy dependencies added before final integration',
    commands=commands,source_render_receipt=str((OUT/'source-render-receipt.json').relative_to(ROOT)),
    acquisition=read(OUT/'acquisition.json'),
    candidate_creation=dict(baseline='docs/design/proposal/manuscript-tax-20261009',candidate=str(NEW.relative_to(ROOT)),method='Copy prior TeX/bibliography and grammar source, add one section, one inclusion and version update',reader_delta='Source-backed EPS/ownership timing and separate award/equity/cash measures'),
    wall_time=dict(start_utc=start.isoformat(),end_utc=now.isoformat(),elapsed_seconds=(now-start).total_seconds(),scope='Unit wall interval includes interactive inspection and build approval; individual build seconds were not separately measured'),
    artifact_hashes=artifacts,preservation=dict(baseline_files=len(baseline['protected_hashes']),preceding_manifest_references=len(previous['artifact_hashes']),historical=candidate['preservation_counts'],pointers=baseline['pointer_relocations']),
    readiness='not_ready',independent_reader='pending',human_acceptance='pending',
    scope='Six full EPS/equity/compensation notes with fifteen dependencies; exact displayed-centre quantity examples only, not full histories, ASC methodology, implemented product or whole-package semantics'))
assert all(sha(ROOT/n)==h for n,h in artifacts.items())
completion=dict(recorded_at=now.isoformat(),status='bounded_unit_complete_with_wider_gaps',manifest_sha256=sha(OUT/'run-manifest.json'),pdf=candidate['pdf'],source_checks=evidence['passed'],candidate_checks=candidate['passed'],artifacts_verified=len(artifacts),readiness='not_ready',next_work='E01/C03: complete annual Note 9 and interim Note 6 debt reading with principal/carrying-value/maturity/cash/currency/hedge dependencies; audit population before execution')
save('completion.json',completion)
print(json.dumps(completion))
