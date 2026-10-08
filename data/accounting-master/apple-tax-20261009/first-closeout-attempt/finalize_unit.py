"""Bind a completed, bounded documentary unit without changing old evidence."""
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

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT / 'docs/design/proposal/manuscript-tax-20261009'
if (OUT / 'completion.json').exists():
    raise SystemExit('Closed unit; preserve it')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
save = lambda n, d: (OUT / n).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
baseline = read(OUT / 'baseline.json')
candidate = read(OUT / 'candidate-checks.json')
evidence = read(OUT / 'evidence-checks.json')
assert candidate['failed'] == evidence['failed'] == 0
assert candidate['checker_sha256'] == sha(OUT / 'check_candidate.py')
assert evidence['checker_sha256'] == sha(OUT / 'prepare_evidence.py')
assert sha(ROOT / candidate['pdf']['path']) == candidate['pdf']['sha256']
for hashes in [candidate['inputs'], evidence['inputs'], evidence['output_hashes'], baseline['protected_hashes']]:
    assert all(sha(ROOT / n) == h for n, h in hashes.items())
rel = {r['historical_path']: r['preserved_path'] for r in baseline['pointer_relocations']}
previous = read(ROOT / baseline['prior_manifest'])
assert all(sha(ROOT / rel.get(n, n)) == h for n, h in previous['artifact_hashes'].items())
history = read(ROOT / 'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for k in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    assert all(sha(ROOT / n) == h for n, h in history[k].items())
p19 = read(ROOT / 'data/accounting-master/continuation-20261007/baseline-manifest.json')
p19rel = {r['historical_path']: r['preserved_path'] for r in p19['relocations']}
assert all(sha(ROOT / p19rel.get(n, n)) == h for n, h in p19['p19_historical_artifact_hashes'].items())
review = read(OUT / 'render-review.json')
assert review['author_review_sha256'] == sha(OUT / 'author-review.md')
assert review['render_manifest_sha256'] == sha(OUT / 'render-manifest.json')
assert review['human_acceptance'] == review['independent_reader'] == 'pending'
pointer_checks = []
for row in baseline['pointer_relocations']:
    assert sha(ROOT / row['preserved_path']) == row['sha256']
    p = ROOT / row['historical_path']
    t = p.read_text()
    assert 'Version 2.10' in t and 'E01' in t
    assert 'earnings' in t.lower() or 'tax' in t.lower()
    if 'requirements' not in p.name:
        assert 'not_ready' in t
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', t)
    bad = [s for s in links if not s.startswith(('http:', 'https:', '#')) and not (p.parent / s.split('#')[0]).exists()]
    assert not bad, (p, bad)
    pointer_checks.append(dict(path=row['historical_path'], sha256=sha(p), links_checked=len(links), broken_links=bad))
roadmap = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
gaps = re.findall(r'^\| (G\d+) —', roadmap, re.M)
assert len(gaps) == 18 and set(gaps) == {f'G{n}' for n in range(1, 19)}
assert '136 unverified publication dates' in roadmap
assert all(f'E{n}' in roadmap for n in ['01', '05', '07', '08', '14'])
acquisition = read(OUT / 'acquisition.json')
assert acquisition['network_requests'] == 0
prior_completion = read((ROOT / baseline['prior_manifest']).parent / 'completion.json')
assert prior_completion['manifest_sha256'] == sha(ROOT / baseline['prior_manifest'])
now = datetime.now(timezone.utc)
save('closeout-checks.json', dict(recorded_at=now.isoformat(), passed=True, pointer_checks=pointer_checks,
    gap_map='All G1–G18 retained once', previous_manifest_references=len(previous['artifact_hashes']),
    baseline_files=len(baseline['protected_hashes']), historical_preservation_counts=candidate['preservation_counts'],
    source_and_candidate_outputs_current=True, builds=1, full_readiness='not_ready'))
plan = ROOT / 'docs/plans/accounting-apple-tax-20261009.md'
artifacts = {str(p.relative_to(ROOT)): sha(p) for base in [OUT, NEW] for p in base.rglob('*')
             if p.is_file() and p.name not in {'run-manifest.json', 'completion.json'}}
artifacts[str(plan.relative_to(ROOT))] = sha(plan)
for row in pointer_checks:
    artifacts[row['path']] = row['sha256']
prefix = 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-tax-20261009/'
commands = [dict(command=prefix + name, exit_code=0) for name in
            ['build_candidate.py', 'render_sources.py', 'render_candidate.py']]
commands += [
    dict(command=prefix + 'prepare_evidence.py', exit_code=0, runs=1, wall_seconds=evidence['wall_seconds']),
    dict(command='latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex > /home/chakwong/python/AccDSL/data/accounting-master/apple-tax-20261009/build.log 2>&1',
         cwd=str(NEW), execution='trusted existing font cache', exit_code=0, builds=1),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-tax-20261009/sections/apple-tax-settlement.tex --pdf docs/design/proposal/manuscript-tax-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-tax-20261009/surface-audit.json --output-md data/accounting-master/apple-tax-20261009/surface-audit.md', exit_code=0),
    dict(command=prefix + 'check_candidate.py', exit_code=0, runs=1, wall_seconds=candidate['wall_seconds']),
    dict(command=prefix + 'finalize_unit.py', exit_code=0),
]
start = datetime.fromisoformat(baseline['recorded_at'])
manifest = dict(recorded_at=now.isoformat(), git_commit=baseline['git_commit'],
    git_worktree='Extensive pre-existing dirty state; artifact hashes supplement commit; no Git mutation',
    environment=dict(python=sys.executable, version=platform.python_version(),
        conda_env=os.environ.get('CONDA_DEFAULT_ENV'), platform=platform.platform(),
        beautifulsoup=bs4.__version__, pymupdf=fitz.VersionBind,
        latex='Existing LuaHBTeX; exact engine in retained log; trusted font cache',
        cpu_gpu_status='CPU document tools only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPUs in Python helpers; no ML or GPU detection'),
    random_seeds='N/A: deterministic documentary/arithmetic work', data_version=evidence['inputs'],
    plan=str(plan.relative_to(ROOT)), audit='Skeptical/default/evidence audit recorded before substantive work',
    result=str((OUT / 'result.md').relative_to(ROOT)), commands=commands,
    acquisition=acquisition, source_render_receipt=str((OUT / 'source-render-receipt.json').relative_to(ROOT)),
    auxiliary_operations='Baseline/pointer preservation, source extraction, original annual and derived interim PDF renders, baseline page inspection, contact sheets, author review and four current-pointer edits. Source and candidate checks passed on first runs; one successful PDF build, with no post-generation manuscript repair. No network, installs or new controller work.',
    wall_time=dict(started_at=start.isoformat(), finished_at=now.isoformat(), elapsed_seconds=(now-start).total_seconds(),
        basis='Baseline preservation through closeout, including carried-session work and reviews; not a performance measurement'),
    artifact_hashes=artifacts, preservation=dict(baseline_files=len(baseline['protected_hashes']),
        previous_manifest_references=len(previous['artifact_hashes']), historical_counts=candidate['preservation_counts'],
        pointers=baseline['pointer_relocations']),
    readiness='not_ready', independent_reader='pending', human_acceptance='pending',
    scope='Full bounded annual Note 7 with eighteen dependencies, tax recognition/payable/deferred bridges and conditional restricted-fund settlement; no full Apple semantics, actual cohort/payment reconstruction, operative authority, runtime or stochastic ranking')
save('run-manifest.json', manifest)
assert all(sha(ROOT / n) == h for n, h in artifacts.items())
completion = dict(recorded_at=now.isoformat(), status='bounded_unit_complete_with_wider_gaps',
    manifest_sha256=sha(OUT / 'run-manifest.json'), pdf=candidate['pdf'], source_checks=evidence['passed'],
    candidate_checks=candidate['passed'], artifacts_verified=len(artifacts), readiness='not_ready',
    next_work='E01/C03: earnings per share and share-count changes from annual A06/A16, interim I04/I08 and equity dependencies; plan and audit before execution')
save('completion.json', completion)
print(json.dumps(completion))
