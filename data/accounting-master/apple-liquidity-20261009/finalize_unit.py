"""Freeze the completed liquidity unit after checking all four current records."""
from datetime import datetime, timezone
import difflib
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


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-debt-20261009'
NEW = ROOT / 'docs/design/proposal/manuscript-liquidity-20261009'
PLAN = ROOT / 'docs/plans/accounting-apple-liquidity-20261009.md'
OUTPUTS = ['closeout-checks.json', 'run-manifest.json', 'completion.json']
existing = [name for name in OUTPUTS if (OUT / name).exists()]
if existing:
    raise SystemExit(f'Preserve existing closeout evidence; refusing overwrite: {existing}')
assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(name, data):
    with (OUT / name).open('x') as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def verify(hashes):
    bad = [name for name, digest in hashes.items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    assert not bad, bad


baseline = read(OUT / 'baseline.json')
candidate = read(OUT / 'candidate-checks.json')
evidence = read(OUT / 'evidence-checks.json')
assert candidate['failed'] == evidence['failed'] == 0
assert candidate['passed'] == 35 and evidence['passed'] == 339
assert all(row['passed'] for report in [candidate, evidence] for row in report['checks'])
assert candidate['checker_sha256'] == sha(OUT / 'check_candidate.py')
assert evidence['checker_sha256'] == sha(OUT / 'prepare_evidence.py')
pdf = NEW / 'accounting-product-proposal.pdf'
pdf_hash = sha(pdf)
assert candidate['pdf']['path'] == str(pdf.relative_to(ROOT))
assert candidate['pdf']['sha256'] == pdf_hash
assert candidate['pdf']['pages'] == 149
with fitz.open(pdf) as document:
    assert len(document) == 149
for hashes in [candidate['inputs'], evidence['inputs'], evidence['output_hashes'],
               baseline['protected_hashes']]:
    verify(hashes)

relocations = {row['historical_path']: row['preserved_path']
               for row in baseline['pointer_relocations']}
assert len(relocations) == 4
prior_path = ROOT / baseline['prior_manifest']
assert sha(prior_path) == baseline['prior_manifest_sha256']
previous = read(prior_path)
assert len(previous['artifact_hashes']) == baseline['prior_manifest_references'] == 152
assert len(baseline['protected_hashes']) == 154
verify({relocations.get(name, name): digest
        for name, digest in previous['artifact_hashes'].items()})
previous_completion = read(prior_path.parent / 'completion.json')
assert previous_completion['manifest_sha256'] == sha(prior_path)
assert previous_completion['pdf']['pages'] == 146
history = read(ROOT / 'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json')
counts = {}
for key in ['protected_hashes', 'upstream_reference_hashes', 'controller_hashes']:
    verify(history[key])
    counts[key] = len(history[key])
assert counts == candidate['preservation_counts'] == dict(
    protected_hashes=1266, upstream_reference_hashes=518, controller_hashes=6)
p19 = read(ROOT / 'data/accounting-master/continuation-20261007/baseline-manifest.json')
old_relocations = {row['historical_path']: row['preserved_path'] for row in p19['relocations']}
verify({old_relocations.get(name, name): digest
        for name, digest in p19['p19_historical_artifact_hashes'].items()})
readiness = read(ROOT / 'data/accounting-master/deliverables/P19/readiness.json')
assert readiness['status'] == 'not_ready' and not readiness['ready']
assert set(readiness['remaining_blockers']) == {
    'P15-' + name for name in ['E01', 'E05', 'E07', 'E08', 'E14']}

# Bind the saved source delta, since a PDF hash alone does not bind its inputs.
sources = lambda base: {path.relative_to(base): path for path in base.rglob('*')
                        if path.is_file() and path.suffix in {'.tex', '.bib', '.lark'}}
old_sources, new_sources = sources(OLD), sources(NEW)
assert old_sources.keys() <= new_sources.keys()
changed, delta = [], []
for name in sorted(new_sources):
    before = old_sources[name].read_text() if name in old_sources else ''
    after = new_sources[name].read_text()
    if before != after:
        changed.append(str(name))
        delta.extend(difflib.unified_diff(
            before.splitlines(True), after.splitlines(True),
            fromfile=str(OLD / name) if name in old_sources else '/dev/null',
            tofile=str(NEW / name)))
assert changed == candidate['changed_sources']
assert set(changed) == {'accounting-product-proposal.tex',
                        'chapters/13-reference-company.tex', 'sections/apple-liquidity.tex'}
assert ''.join(delta) == (OUT / 'manuscript-delta.diff').read_text()
assert (NEW / 'accounting-product-proposal.tex').read_text().replace(
    'Version 2.13', 'Version 2.12') == (OLD / 'accounting-product-proposal.tex').read_text()
chapter = 'chapters/13-reference-company.tex'
assert (NEW / chapter).read_text() == (OLD / chapter).read_text() + '\n\\input{sections/apple-liquidity}\n'
assert candidate['baseline_displays'] == 44 and candidate['candidate_displays'] == 46
assert candidate['bibliography_keys'] == 66

render = read(OUT / 'render-manifest.json')
review = read(OUT / 'render-review.json')
assert render['pdf_sha256_before'] == render['pdf_sha256_after'] == pdf_hash
assert render['script_sha256'] == sha(OUT / 'render_candidate.py')
verify({row['path']: row['sha256'] for group in ['rendered_pages', 'contact_sheets']
        for row in render[group].values()})
assert review['author_review_sha256'] == sha(OUT / 'author-review.md')
assert review['render_manifest_sha256'] == sha(OUT / 'render-manifest.json')
assert review['page_numbers'] == render['page_numbers'] == list(range(1, 8)) + list(range(20, 26))
assert review['continuous_read_pages'] == render['continuous_read_pages'] == list(range(20, 26))
assert review['navigation_inspection_pages'] == list(range(1, 8))
assert review['human_acceptance'] == review['independent_reader'] == 'pending'
first_render_path = OUT / 'candidate-attempt-01/render-manifest.json'
assert review['prior_render_manifest_sha256'] == sha(first_render_path)
first_render = read(first_render_path)
unchanged = [page for page in render['page_numbers'] if
             render['rendered_pages'][str(page)]['sha256'] ==
             first_render['rendered_pages'][str(page)]['sha256']]
assert unchanged == review['prior_inspected_unchanged_images'] == [
    1, 2, 3, 4, 5, 6, 7, 20, 21, 22, 24, 25]
assert review['repaired_page_reread'] == [23]
attempt = read(OUT / 'candidate-attempt-01/preservation.json')
verify({row['preserved_path']: row['sha256'] for row in attempt['relocations']})
source_render = read(OUT / 'source-render-receipt.json')
assert source_render['source_supplement_sha256'] == sha(OUT / 'source-claim-supplement.json')
assert source_render['script_sha256'] == sha(OUT / 'render_sources.py')
verify({row['path']: row['sha256'] for row in source_render['rendered_images']})
assert source_render['derived_html_sha256'] == sha(ROOT / source_render['derived_html'])
assert source_render['derived_pdf_sha256'] == sha(ROOT / source_render['derived_pdf'])
assert source_render['annual_sha256'] == sha(ROOT / source_render['annual_source'])
build = read(OUT / 'build-receipt.json')
first_build = read(OUT / 'candidate-attempt-01/build-receipt.json')
assert build['exit_code'] == first_build['exit_code'] == 0
assert build['pdf_sha256'] == pdf_hash and build['log_sha256'] == sha(OUT / 'build.log')
assert build['script_sha256'] == sha(OUT / 'build_candidate.py')
assert first_build['pdf_sha256'] == sha(OUT / 'candidate-attempt-01/manuscript/accounting-product-proposal.pdf')
assert first_build['log_sha256'] == sha(OUT / 'candidate-attempt-01/build.log')

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == baseline['git_commit']
pointers = []
for row in baseline['pointer_relocations']:
    assert sha(ROOT / row['preserved_path']) == row['sha256']
    path = ROOT / row['historical_path']
    text = path.read_text()
    flat = ' '.join(text.split())
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', text)
    linked_pdf = any((path.parent / target.split('#')[0]).resolve() == pdf
                     for target in links if not target.startswith(('http:', 'https:', '#')))
    assert 'Version 2.13' in text and (str(pdf.relative_to(ROOT)) in text or linked_pdf)
    assert pdf_hash in text and 'not_ready' in text
    assert 'E01' in text and 'Note 13' in text and 'Note 10' in text
    assert all(term in flat for term in ['Note 1', 'Note 2', 'MD&A', 'A21/I11'])
    assert '339 source/arithmetic and 35 candidate/preservation' in flat
    broken = [target for target in links if
              not target.startswith(('http:', 'https:', '#')) and
              not (path.parent / target.split('#')[0]).exists()]
    assert not broken, (path, broken)
    pointers.append(dict(path=row['historical_path'], sha256=sha(path),
                         links_checked=len(links), broken_links=broken))

roadmap_path = ROOT / 'docs/plans/accounting-master-current.md'
roadmap = roadmap_path.read_text()
prior_roadmap = (ROOT / relocations[str(roadmap_path.relative_to(ROOT))]).read_text()
gap_rows = lambda text: re.findall(r'^\| (G\d+ —[^\n]+)', text, re.M)
assert gap_rows(roadmap) == gap_rows(prior_roadmap)
assert len(gap_rows(roadmap)) == 18
assert set(re.findall(r'^\| (G\d+) —', roadmap, re.M)) == {f'G{n}' for n in range(1, 19)}
requirements = (ROOT / 'docs/plans/accounting-mission-requirements.md').read_text()
assert set(re.findall(r'^\| (MC\d+) \|', requirements, re.M)) == {f'MC{n:02d}' for n in range(1, 36)}
assert (ROOT / 'docs/plans/accounting-mission-requirements.md').read_bytes() == subprocess.check_output(
    ['git', 'show', head + ':docs/plans/accounting-mission-requirements.md'], cwd=ROOT)
assert '136 unverified publication dates' in roadmap
assert '40 outstanding exhibit targets' in roadmap
assert all(f'E{name}' in roadmap for name in ['01', '05', '07', '08', '14'])
expected_links = {
    'Latest substantive result': ('Apple liquidity unit', '../../data/accounting-master/apple-liquidity-20261009/result.md'),
    'Current manuscript': ('Version 2.13 PDF', '../design/proposal/manuscript-liquidity-20261009/accounting-product-proposal.pdf'),
}
for label, expected in expected_links.items():
    matches = re.findall(r'^' + re.escape(label) + r': \[([^\]]+)\]\(([^)]+)\)\.', roadmap, re.M)
    assert matches == [expected], (label, matches)
assert '149-page Version 2.13' in roadmap
assert 'Next: complete annual Note 13/interim Note 10' in roadmap
assert 'Next: complete annual/interim Note 4' not in roadmap
execution_order = roadmap.split('## Remaining execution order\n', 1)[1].split('\n## ', 1)[0]
first_action = ' '.join(execution_order.split('\n2. ', 1)[0].split())
assert first_action.startswith('1. Plan and audit E01/C03 complete annual Note 13/interim Note 10')
assert all(term in first_action for term in ['Note 1', 'Note 2', 'consolidated operations',
                                           'MD&A', 'reporting-change', 'A21/I11', 'liquidity'])
assert 'Note 4' not in first_action
assert all(line in roadmap.splitlines()[-2:]
           for line in ['Latest substantive result: [' + expected_links['Latest substantive result'][0] + '](' + expected_links['Latest substantive result'][1] + ').',
                        'Current manuscript: [' + expected_links['Current manuscript'][0] + '](' + expected_links['Current manuscript'][1] + ').'])
result = (OUT / 'result.md').read_text()
assert pdf_hash in result and '339 source/arithmetic and 35 candidate/preservation' in result
assert read(OUT / 'acquisition.json')['network_requests'] == 0
assert 'The audit passes' in (OUT / 'closeout-note.md').read_text()

whitespace_paths = [ROOT / row['path'] for row in pointers] + [OUT / 'closeout-note.md', Path(__file__)]
whitespace_errors = [(str(path.relative_to(ROOT)), number)
                     for path in whitespace_paths
                     for number, line in enumerate(path.read_text().splitlines(), 1)
                     if line.rstrip(' \t') != line]
assert not whitespace_errors, whitespace_errors

now = datetime.now(timezone.utc)
start = datetime.fromisoformat(baseline['recorded_at'])
next_work = ('E01/C03: audit complete annual Note 13/interim Note 10 segment and geographic information; '
             'declare Note 1, Note 2, consolidated operations, MD&A segment-performance and reporting-change dependencies; '
             'extend geographic/profit/asset and unknown-allocation meaning, preserving A21/I11 and existing income/sales sums.')
save('closeout-checks.json', dict(
    recorded_at=now.isoformat(), passed=True, pointer_checks=pointers,
    semantic_current_links=expected_links, baseline_files=154, previous_manifest_references=152,
    historical_preservation_counts=counts, historical_p19_hashes_resolved=True,
    all_eighteen_gap_rows_unchanged=True, original_mc01_mc35_requirements_preserved=True,
    roadmap_execution_order_current=True, whitespace_files_checked=len(whitespace_paths),
    source_and_candidate_outputs_current=True, reviewed_images_current=True,
    source_check_runs=3, source_render_runs=1, candidate_check_runs=1,
    build_attempts=2, successful_builds=2, final_render_runs=2,
    full_readiness='not_ready', next_work=next_work))

artifacts = {str(path.relative_to(ROOT)): sha(path) for base in [OUT, NEW]
             for path in base.rglob('*') if path.is_file() and
             path.name not in {'run-manifest.json', 'completion.json'} and
             '__pycache__' not in path.parts}
artifacts[str(PLAN.relative_to(ROOT))] = sha(PLAN)
for row in pointers:
    artifacts[row['path']] = row['sha256']
prefix = 'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/apple-liquidity-20261009/'
commands = [
    dict(command=prefix + 'prepare_baseline.py', runs=1, exit_code=0),
    dict(command=prefix + 'prepare_evidence.py', runs=3, exit_codes=[1, 1, 0],
         final_wall_seconds=evidence['wall_seconds'],
         repairs='Correct tax dependency filename, then account for displaced original-PDF superscript markers; earlier attempts retained.'),
    dict(command=prefix + 'render_sources.py', runs=1, exit_code=0),
    dict(command=prefix + 'prepare_candidate.py', runs=1, exit_code=0),
    dict(command=prefix + 'build_candidate.py', runs=2, exit_codes=[0, 0],
         receipts=['data/accounting-master/apple-liquidity-20261009/candidate-attempt-01/build-receipt.json',
                   'data/accounting-master/apple-liquidity-20261009/build-receipt.json'],
         repairs='Correct annual comprehensive-income page anchor and add direct disposal-policy citation; first candidate/build preserved.'),
    dict(command=prefix + 'render_candidate.py', runs=2, exit_codes=[0, 0],
         repair='Final corrected page 23 reread; twelve other inspected images unchanged.'),
    dict(command='CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-liquidity-20261009/sections/apple-liquidity.tex --pdf docs/design/proposal/manuscript-liquidity-20261009/accounting-product-proposal.pdf --output-json data/accounting-master/apple-liquidity-20261009/surface-audit.json --output-md data/accounting-master/apple-liquidity-20261009/surface-audit.md',
         runs=2, exit_codes=[0, 0]),
    dict(command=prefix + 'record_review.py', runs=1, exit_code=0),
    dict(command=prefix + 'check_candidate.py', runs=1, exit_code=0,
         wall_seconds=candidate['wall_seconds']),
    dict(command='git diff --check -- docs/plans/accounting-master-checkpoint.md docs/plans/accounting-master-current.md docs/plans/accounting-continuation-requirements-20261007.md data/accounting-master/next-plan.md', exit_code=0),
    dict(command=prefix + 'finalize_unit.py', runs=3, exit_codes=[1, 1, 0],
         repairs='First pre-write attempt rejected the roadmap valid relative PDF link; resolve local Markdown link targets. Second expected unpadded MC1-MC9 rather than original MC01-MC09; correct expected identifiers. Neither failed attempt created partial output files.'),
]
for receipt in [first_build, build]:
    commands.append(dict(command=receipt['command'], cwd=receipt['cwd'],
                         environment=receipt['environment'], exit_code=receipt['exit_code'],
                         wall_seconds=receipt['wall_seconds']))
save('run-manifest.json', dict(
    recorded_at=now.isoformat(), git_commit=head,
    git_worktree='Execution baseline is the checked EPS Version 2.11 commit. Debt/liquidity remain uncommitted; unrelated dirty work preserved; no commit or push.',
    environment=dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
                     pymupdf=fitz.VersionBind, beautifulsoup=bs4.__version__,
                     cpu_gpu='CPU document/arithmetic helpers; GPU intentionally hidden with CUDA_VISIBLE_DEVICES=-1',
                     cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
                     latex='LuaLaTeX via latexmk; explicit writable /tmp TEXMFVAR and TEXMFCACHE, no install'),
    data_version=evidence['inputs'],
    random_seeds='N/A: deterministic documentary/arithmetic work; issuer risk scenario not locally replicated',
    plan=str(PLAN.relative_to(ROOT)), result=str((OUT / 'result.md').relative_to(ROOT)),
    audit='Saved skeptical/default/evidence audit passed; resumed closeout audit in closeout-note.md; complete declared notes/dependencies and final source/render bindings checked.',
    commands=commands, source_render_receipt=str((OUT / 'source-render-receipt.json').relative_to(ROOT)),
    acquisition=read(OUT / 'acquisition.json'),
    candidate_creation=dict(
        baseline=str(OLD.relative_to(ROOT)), candidate=str(NEW.relative_to(ROOT)),
        method='Copy all TeX/bibliography/grammar sources, add one source-backed liquidity section, one inclusion and version update; preserve 44 prior displays and 66 bibliography entries, add two displays',
        reader_delta='Payment resources, restricted/current distinctions, security cash/valuation populations and whole-customer concentration alternatives'),
    wall_time=dict(start_utc=start.isoformat(), end_utc=now.isoformat(),
                   elapsed_seconds=(now - start).total_seconds(),
                   scope='Whole unit interval includes session resumption, source/PDF inspection and documentation; individual build/checker seconds recorded separately'),
    artifact_hashes=artifacts,
    preservation=dict(baseline_files=154, preceding_manifest_references=152,
                      prior_manifest=baseline['prior_manifest'], prior_manifest_sha256=baseline['prior_manifest_sha256'],
                      historical=counts, pointers=baseline['pointer_relocations']),
    readiness='not_ready', independent_reader='pending', human_acceptance='pending',
    scope='Two complete financial-instruments notes, fourteen material units, thirteen dependencies and eleven queries; displayed-centre identities and conditional whole-customer examples, not full histories, operative compliance, security/loss forecasts, an independently accepted proposal or product implementation.'))
verify(artifacts)
completion = dict(recorded_at=now.isoformat(), status='bounded_unit_complete_with_wider_gaps',
                  manifest_sha256=sha(OUT / 'run-manifest.json'), pdf=candidate['pdf'],
                  source_checks=339, candidate_checks=35, artifacts_verified=len(artifacts),
                  readiness='not_ready', next_work=next_work)
save('completion.json', completion)
print(json.dumps(completion))
