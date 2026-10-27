"""Freeze this unit after the current four records agree and baseline verifies."""
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

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
NEW=ROOT/'docs/design/proposal/manuscript-perimeter-20261009'
PLAN=ROOT/'docs/plans/accounting-apple-perimeter-20261009.md'
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
for name in ['closeout-checks.json','run-manifest.json','completion.json']:
    assert not (OUT/name).exists(),'Preserve completed outputs'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
norm=lambda s:' '.join(s.split())
def verify(hashes):
    bad=[p for p,h in hashes.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not bad,bad
def save(name,value):
    with (OUT/name).open('x') as f:f.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

base=read(OUT/'baseline.json');candidate=read(OUT/'candidate-checks.json');source=read(OUT/'source-checks.json')
assert candidate['passed']==40 and candidate['failed']==0 and all(r['passed'] for r in candidate['checks'])
assert source['passed']==79 and source['failed']==0 and all(r['passed'] for r in source['checks'])
assert candidate['checker_sha256']==sha(OUT/'check_candidate.py')
assert source['checker_sha256']==sha(OUT/'work_unit.py')
verify(candidate['inputs']);verify(source['inputs']);verify(base['protected_hashes'])
pdf=NEW/'accounting-product-proposal.pdf';pdfhash=sha(pdf)
assert candidate['pdf']==dict(path=str(pdf.relative_to(ROOT)),sha256=pdfhash,pages=155)
assert len(fitz.open(pdf))==155
assert candidate['baseline_displays']==candidate['candidate_displays']==48 and candidate['bibliography_keys']==66
assert len(base['protected_hashes'])==178 and base['prior_manifest_references']==176
prior=ROOT/base['prior_manifest'];rel={r['historical_path']:r['preserved_path'] for r in base['pointer_relocations']}
assert sha(prior)==base['prior_manifest_sha256']==read(prior.parent/'completion.json')['manifest_sha256']
verify({rel.get(n,n):h for n,h in read(prior)['artifact_hashes'].items()})
for name in base['ancestor_counts']:verify(read(ROOT/'data/accounting-master'/name/'baseline.json')['protected_hashes'])
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for key,count in base['history_counts'].items():assert len(history[key])==count;verify(history[key])
render=read(OUT/'render-manifest.json');review=read(OUT/'render-review.json')
assert render['pdf_sha256']==review['pdf_sha256']==pdfhash
assert review['render_manifest_sha256']==sha(OUT/'render-manifest.json') and review['author_review_sha256']==sha(OUT/'author-review.md')
assert review['independent_reader']==review['human_acceptance']=='pending'
verify({r['path']:r['sha256'] for r in render['rendered_images']+[render['navigation_sheet']]})
build=read(OUT/'build-01/receipt.json');assert build['exit_code']==0 and build['pdf_sha256']==pdfhash
assert build['log_sha256']==sha(OUT/'build-01/build.log')
assert not any(s in (NEW/'accounting-product-proposal.log').read_text() for s in ['Warning','Overfull','Underfull','! '])
assert read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')['status']=='not_ready'
pointers=[]
for name in rel:
    s=(ROOT/name).read_text();logical=norm(s)
    assert 'Version 2.15' in s and pdfhash in s and 'not_ready' in s,name
    assert 'annual Item 3' in logical and 'legal proceedings' in logical,name
    assert all(line==line.rstrip(' \t') for line in s.splitlines()),name
    pointers.append(dict(path=name,sha256=sha(ROOT/name)))
road=(ROOT/'docs/plans/accounting-master-current.md').read_text()
oldroad=(ROOT/rel['docs/plans/accounting-master-current.md']).read_text()
gaprows=lambda s:[line for line in s.splitlines() if re.match(r'^\| G\d+ ',line)]
assert len(gaprows(road))==18 and gaprows(road)==gaprows(oldroad)
for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',pdf)]:
    lines=[line for line in road.splitlines() if line.startswith(label+': ')]
    assert len(lines)==1
    m=re.search(r'\]\(([^)]+)\)',lines[0]);assert m
    assert (ROOT/'docs/plans'/m.group(1)).resolve()==target.resolve()
first=norm(road.split('## Remaining execution order\n',1)[1].split('\n2. ',1)[0])
assert first.startswith('1. Plan and audit E01/C03 annual Item 3') and '40-target' in first
frontier=read(ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json')
assert len(frontier['reference_frontier'])==70
assert next(r for r in frontier['reference_frontier'] if r['id']=='annual.exhibit.21.1')['semantic_status']=='target_identity_inspected; substantive_translation_pending'
assert pdfhash in (OUT/'result.md').read_text()
for k,a,b,h in [('annual',103510,107860,'43d42cd8fbd565628fbacee844cec184f767634f8c309004a527347e54a3cbfe'),
              ('interim',53800,58229,'fc40f30a6ce71df57f4c8f2ac58fd595f80054d6f716565b51f68b0977118cae')]:
    path=ROOT/frontier['sources'][k]['extraction_path'];s=path.read_text()
    assert hashlib.sha256(s[a:b].encode()).hexdigest()==h and h in (OUT/'next-source-frontier.md').read_text()

now=datetime.now(timezone.utc)
save('closeout-checks.json',dict(recorded_at=now.isoformat(),passed=True,pointer_checks=pointers,
    baseline_files=178,prior_manifest_references=176,history_counts=base['history_counts'],all_eighteen_gap_rows_unchanged=True,
    current_pdf_and_result_links_resolved=True,source_checks=79,candidate_checks=40,
    full_readiness='not_ready',next_work='E01/C03 annual Item 3/interim Part II Item 1 legal proceedings and contingency/risk/MD&A dependencies'))
artifacts={str(p.relative_to(ROOT)):sha(p) for directory in [OUT,NEW] for p in directory.rglob('*')
           if p.is_file() and p.name not in {'run-manifest.json','completion.json'} and '__pycache__' not in p.parts}
artifacts[str(PLAN.relative_to(ROOT))]=sha(PLAN)
artifacts.update({r['path']:r['sha256'] for r in pointers})
commands=[json.loads(line) for line in (OUT/'commands.jsonl').read_text().splitlines()]
commands.extend([
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-perimeter-20261009/check_candidate.py',exit_code=0,wall_seconds=candidate['wall_seconds']),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-perimeter-20261009/sections/apple-perimeter.tex --pdf docs/design/proposal/manuscript-perimeter-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-perimeter-20261009/surface-audit.json --output-md data/accounting-master/apple-perimeter-20261009/surface-audit.md',exit_code=0),
    dict(command='git diff --check -- docs/plans/accounting-master-checkpoint.md docs/plans/accounting-master-current.md docs/plans/accounting-continuation-requirements-20261007.md data/accounting-master/next-plan.md',exit_code=0),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-perimeter-20261009/finalize_unit.py',exit_code=0)])
manifest=dict(schema_version='accdsl.bounded-unit-manifest.v1',recorded_at=now.isoformat(),
    unit='Apple Note 1 / Exhibit 21.1 perimeter E01/C03/C08',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    git_branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
    plan=str(PLAN.relative_to(ROOT)),result=str((OUT/'result.md').relative_to(ROOT)),
    environment=dict(python=sys.version,platform=platform.platform(),bs4=bs4.__version__,pymupdf=fitz.VersionBind,
        CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',conda_env='N/A: system python3',
        tex_cache='/tmp/accdsl-perimeter-tex-cache-20261009'),
    data_version='Pinned Apple FY2024 annual PDF / FY2025 Q1 SEC HTML; hashes and exact spans in source-claim-supplement.json',
    random_seeds='N/A: deterministic documentary/positional checks, no stochastic run',commands=commands,
    command_attempt_status=dict(baseline=[0],sources=[1,0,0],copy=[0],build=[0],render=[0],candidate_check=[0]),
    wall_seconds=(now-datetime.fromisoformat(base['recorded_at'])).total_seconds(),build_wall_seconds=build['wall_seconds'],
    network_requests=0,pdf=candidate['pdf'],full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',
    artifact_hashes=artifacts,prior_manifest=base['prior_manifest'],prior_manifest_sha256=sha(prior),pointer_relocations=base['pointer_relocations'])
save('run-manifest.json',manifest);verify(artifacts)
completion=dict(recorded_at=now.isoformat(),status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),
    pdf=candidate['pdf'],source_checks=79,candidate_checks=40,manifest_bound_files=len(artifacts),full_readiness='not_ready',
    next_work='E01/C03 annual/interim legal proceedings')
save('completion.json',completion)
print(json.dumps(completion))
