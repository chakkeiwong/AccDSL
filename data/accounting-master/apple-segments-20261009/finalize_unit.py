"""Freeze the completed segment unit only after four live records agree."""
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
NEW=ROOT/'docs/design/proposal/manuscript-segments-20261009'
PLAN=ROOT/'docs/plans/accounting-apple-segments-20261009.md'
for name in ['closeout-checks.json','run-manifest.json','completion.json']:
    if (OUT/name).exists():raise SystemExit('Preserve existing closeout: '+name)
assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())


def verify(hashes):
    bad=[n for n,h in hashes.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
    assert not bad,bad


def save(name,value):
    with (OUT/name).open('x') as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


baseline=read(OUT/'baseline.json')
candidate=read(OUT/'candidate-checks.json')
evidence=read(OUT/'evidence-checks.json')
tables=read(OUT/'table-checks.json')
for report,script,count in [(candidate,'check_candidate.py',37),(evidence,'prepare_evidence.py',83),(tables,'check_tables.py',107)]:
    assert report['passed']==count and report['failed']==0 and all(r['passed'] for r in report['checks'])
    assert report['checker_sha256']==sha(OUT/script)
for hashes in [candidate['inputs'],evidence['inputs'],evidence['output_hashes'],baseline['protected_hashes']]:verify(hashes)
pdf=NEW/'accounting-product-proposal.pdf';pdf_hash=sha(pdf)
assert candidate['pdf']==dict(path=str(pdf.relative_to(ROOT)),sha256=pdf_hash,pages=152)
assert len(fitz.open(pdf))==152
assert candidate['baseline_displays']==46 and candidate['candidate_displays']==48 and candidate['bibliography_keys']==66
assert len(baseline['protected_hashes'])==252 and baseline['prior_manifest_references']==249
prior_path=ROOT/baseline['prior_manifest']
assert sha(prior_path)==baseline['prior_manifest_sha256']==read(prior_path.parent/'completion.json')['manifest_sha256']
rel={r['historical_path']:r['preserved_path'] for r in baseline['pointer_relocations']}
assert len(rel)==4
verify({rel.get(n,n):h for n,h in read(prior_path)['artifact_hashes'].items()})
# The prior unit's preserved ancestor sets are immutable as well.
for name in ['apple-liquidity-20261009','apple-debt-20261009']:
    verify(read(ROOT/'data/accounting-master'/name/'baseline.json')['protected_hashes'])
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']:verify(history[k])
assert candidate['preservation_counts']=={k:len(history[k]) for k in ['protected_hashes','upstream_reference_hashes','controller_hashes']}
assert read(ROOT/'data/accounting-master/deliverables/P19/readiness.json')['status']=='not_ready'

render=read(OUT/'render-manifest.json');review=read(OUT/'render-review.json')
assert render['pdf_sha256_before']==render['pdf_sha256_after']==review['pdf_sha256']==pdf_hash
assert review['render_manifest_sha256']==sha(OUT/'render-manifest.json')
assert review['author_review_sha256']==sha(OUT/'author-review.md')
assert review['independent_reader']==review['human_acceptance']=='pending'
verify({r['path']:r['sha256'] for group in ['rendered_pages','contact_sheets'] for r in render[group].values()})
builds=[read(OUT/f'build-{i:02}/receipt.json') for i in range(1,4)]
assert all(r['exit_code']==0 for r in builds)
assert builds[-1]['pdf_sha256']==pdf_hash
for i,r in enumerate(builds,1):assert r['log_sha256']==sha(OUT/f'build-{i:02}/build.log')
assert not any(word in (NEW/'accounting-product-proposal.log').read_text() for word in ['Overfull','Underfull','LaTeX Warning','! '])

pointers=[]
for name in rel:
    text=(ROOT/name).read_text()
    assert 'Version 2.14' in text and pdf_hash in text,(name,'current version/hash missing')
    logical_text=' '.join(text.split())
    assert 'Exhibit 21.1' in logical_text and 'Note 1' in logical_text,(name,'next action missing')
    assert 'not_ready' in text,(name,'readiness missing')
    assert all(line.rstrip(' \t')==line for line in text.splitlines()),name
    pointers.append(dict(path=name,sha256=sha(ROOT/name)))
roadmap=(ROOT/'docs/plans/accounting-master-current.md').read_text()
oldroad=(ROOT/rel['docs/plans/accounting-master-current.md']).read_text()
gap_rows=lambda s:[line for line in s.splitlines() if re.match(r'^\| G\d+ ',line)]
assert len(gap_rows(roadmap))==18 and gap_rows(roadmap)==gap_rows(oldroad)
for label,target in [('Latest substantive result',OUT/'result.md'),('Current manuscript',pdf)]:
    lines=[line for line in roadmap.splitlines() if line.startswith(label+': ')]
    assert len(lines)==1
    match=re.search(r'\]\(([^)]+)\)',lines[0]);assert match
    resolved=(ROOT/'docs/plans'/match.group(1)).resolve()
    assert resolved==target.resolve(),(label,str(resolved))
first=' '.join(roadmap.split('## Remaining execution order\n',1)[1].split('\n2. ',1)[0].split())
assert first.startswith('1. Plan and audit E01/C03 Note 1 consolidated perimeter')
assert 'Exhibit 21.1' in first and '40-target' in first
assert pdf_hash in (OUT/'result.md').read_text()

now=datetime.now(timezone.utc)
save('closeout-checks.json',dict(recorded_at=now.isoformat(),passed=True,pointer_checks=pointers,
    baseline_files=252,prior_manifest_references=249,preservation_counts=candidate['preservation_counts'],
    all_eighteen_gap_rows_unchanged=True,current_pdf_and_result_links_resolved=True,
    source_checks=83,positional_witness_checks=107,candidate_checks=37,
    full_readiness='not_ready',next_work='E01/C03 Note 1 perimeter and retained annual Exhibit 21.1 subsidiaries, omission footnote and relevant Business/MD&A'))
artifacts={str(p.relative_to(ROOT)):sha(p) for base in [OUT,NEW] for p in base.rglob('*')
           if p.is_file() and p.name not in {'run-manifest.json','completion.json'} and '__pycache__' not in p.parts}
artifacts[str(PLAN.relative_to(ROOT))]=sha(PLAN)
artifacts.update({r['path']:r['sha256'] for r in pointers})
prefix='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-segments-20261009/'
commands=[
    dict(command=prefix+'prepare_baseline.py',runs=1,exit_codes=[0]),
    dict(command=prefix+'prepare_evidence.py',runs=3,exit_codes=[1,1,0],final_wall_seconds=evidence['wall_seconds'],
         repair='Correct Note 5 heading, then whitespace-normalise retrospective-adoption sentence; failed report preserved.'),
    dict(command=prefix+'check_tables.py',runs=3,exit_codes=[1,0,0],
         repair='Handle displaced PDF superscripts; add exact proportional full-matrix construction matching prose; prior reports preserved.'),
    dict(command=prefix+'render_sources.py',runs=1,exit_codes=[0]),
    dict(command=prefix+'prepare_candidate.py',runs=1,exit_codes=[0]),
    dict(command=prefix+'build_candidate.py',runs=3,exit_codes=[0,0,0],
         receipts=[str((OUT/f'build-{i:02}/receipt.json').relative_to(ROOT)) for i in range(1,4)]),
    dict(command=prefix+'render_candidate.py',runs=2,exit_codes=[0,0]),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-segments-20261009/sections/apple-segments.tex --pdf docs/design/proposal/manuscript-segments-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-segments-20261009/surface-audit.json --output-md data/accounting-master/apple-segments-20261009/surface-audit.md',runs=2,exit_codes=[0,0]),
    dict(command=prefix+'check_candidate.py',runs=1,exit_codes=[0],wall_seconds=candidate['wall_seconds']),
    dict(command='git diff --check -- docs/plans/accounting-master-checkpoint.md docs/plans/accounting-master-current.md docs/plans/accounting-continuation-requirements-20261007.md data/accounting-master/next-plan.md',exit_code=0),
    dict(command=prefix+'finalize_unit.py',runs=2,exit_codes=[1,0],
         repair='First pre-write check treated a line-wrapped Exhibit 21.1 as missing; normalise whitespace. No closeout outputs written on that attempt.')]
manifest=dict(schema_version='accdsl.bounded-unit-manifest.v1',recorded_at=now.isoformat(),
    unit='Apple segment/geographic E01/C03/C08',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    plan=str(PLAN.relative_to(ROOT)),result=str((OUT/'result.md').relative_to(ROOT)),
    environment=dict(python=sys.version,platform=platform.platform(),bs4=bs4.__version__,pymupdf=fitz.VersionBind,
                     CUDA_VISIBLE_DEVICES='-1',cpu_gpu_status='CPU only; GPU devices intentionally hidden',conda_env='N/A: system python3',
                     tex_cache='/tmp/accdsl-segments-tex-cache-20261009'),
    data_version='Pinned Apple FY2024 annual PDF and FY2025 Q1 SEC HTML; exact source/extraction hashes in evidence-checks.json',
    random_seeds='N/A: deterministic integer/Fraction arithmetic',commands=commands,
    wall_seconds=(now-datetime.fromisoformat(baseline['recorded_at'])).total_seconds(),
    build_wall_seconds=sum(r['wall_seconds'] for r in builds),network_requests=0,
    pdf=candidate['pdf'],full_readiness='not_ready',independent_reader='pending',human_acceptance='pending',
    artifact_hashes=artifacts,prior_manifest=baseline['prior_manifest'],prior_manifest_sha256=sha(prior_path),
    pointer_relocations=baseline['pointer_relocations'])
save('run-manifest.json',manifest)
verify(artifacts)
completion=dict(recorded_at=now.isoformat(),status='bounded_unit_complete',manifest_sha256=sha(OUT/'run-manifest.json'),
    pdf=candidate['pdf'],source_checks=83,positional_witness_checks=107,candidate_checks=37,
    manifest_bound_files=len(artifacts),full_readiness='not_ready',next_work='Note 1 perimeter / retained Exhibit 21.1')
save('completion.json',completion)
print(json.dumps(completion))
