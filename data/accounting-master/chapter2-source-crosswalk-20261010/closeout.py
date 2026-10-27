"""Bind this author-preparation result without rewriting historical releases."""
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
    with (OUT / name).open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(mapping):
    bad = [p for p, h in mapping.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
    assert not bad, bad[:6]


def main():
    started, timer = datetime.now(timezone.utc).isoformat(), time.monotonic()
    base = read(OUT / 'baseline.json')
    prior_path = ROOT / base['prior_manifest']; prior = read(prior_path)
    assert sha(prior_path) == base['prior_manifest_sha256']
    assert sha(prior_path) == read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes = {reloc.get(p, p): h for p, h in prior['artifact_hashes'].items()}
    verify(prior_hashes)
    checks = read(OUT / 'candidate-checks.json')
    assert checks['failed'] == 0 and checks['passed'] == 33
    assert checks['checker_sha256'] == sha(OUT / 'check_candidate.py')
    verify(checks['inputs'])
    pdf = checks['pdf']
    pointers = {p: sha(ROOT / p) for p in reloc}
    for p in pointers:
        text = (ROOT / p).read_text()
        for token in ['Version 2.24', pdf['sha256'], 'not_ready',
                      'chapter2-source-crosswalk-20261010/result.md', 'E14', '28 complete']:
            assert token in text, (p, token)
    current = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
    previous = (ROOT / reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps = lambda s: [line for line in s.splitlines() if re.match(r'^\| G\d+ ', line)]
    assert len(gaps(current)) == 18 and gaps(current) == gaps(previous)
    for label, target in [('Latest substantive result', OUT / 'result.md'),
                          ('Current manuscript', ROOT / pdf['path'])]:
        line = next(x for x in current.splitlines() if x.startswith(label + ': '))
        link = re.search(r'\]\(([^)]+)\)', line).group(1)
        assert (ROOT / 'docs/plans' / link).resolve() == target.resolve()
    diff_command = ['git', 'diff', '--check', '--', *pointers, rel(OUT),
                    str(Path(pdf['path']).parent), 'docs/plans/accounting-chapter2-source-crosswalk-20261010.md']
    subprocess.run(diff_command, cwd=ROOT, check=True, capture_output=True, text=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout.strip()
    assert head == '891a80316c3291d701b30723df687e517e11a06e'

    # The rejected provisional inventory is preserved separately, not promoted.
    provisional = OUT / 'manifest.json'
    assert sha(provisional) == sha(OUT / 'attempt-01-rejected/manifest.json')
    replacement = dict(status='corrected author crosswalk inventory; no semantic certification',
        supersedes='attempt-01-rejected/manifest.json', input_count=25, record_count=502,
        counts_by_kind=checks['counts_by_kind'], author_groups=82, pending=0,
        input_inventory_sha256=sha(OUT / 'ledger-inventory.json'),
        crosswalk_sha256=sha(OUT / 'claim-query-crosswalk.json'),
        candidate_resolution_sha256=sha(OUT / 'candidate-resolution.json'), pdf=pdf,
        source_boundary=rel(OUT / 'source-boundary.md'), readiness='not_ready',
        independent_reader='pending', factual_queries_closed=0)
    provisional.write_text(json.dumps(replacement, indent=2) + '\n')
    save('closeout-checks.json', dict(passed=True, candidate_checks=33,
        prior_references=len(prior_hashes), current_pointer_hashes=pointers,
        all_eighteen_gap_rows_preserved=True, exact_current_links=True,
        scoped_diff_check='passed', rejected_inventory_superseded=True))

    hashes = dict(prior_hashes)
    hashes.update(checks['inputs'])
    hashes.update({rel(p): sha(p) for p in (ROOT / Path(pdf['path']).parent).rglob('*') if p.is_file()})
    hashes.update({rel(p): sha(p) for p in OUT.rglob('*') if p.is_file()
                   and '__pycache__' not in p.parts and p.name not in {'run-manifest.json', 'completion.json'}})
    hashes.update(pointers)
    plan = 'docs/plans/accounting-chapter2-source-crosswalk-20261010.md'
    hashes[plan] = sha(ROOT / plan)
    hashes[base['prior_manifest']] = sha(prior_path)
    hashes[rel(prior_path.with_name('completion.json'))] = sha(prior_path.with_name('completion.json'))
    verify(hashes)
    finish(started, timer, head, pdf, base, hashes, diff_command, plan, checks)


def finish(started, timer, head, pdf, base, hashes, diff_command, plan, checks):
    runner = 'CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 '
    builds = [dict(receipt=rel(OUT / f'build-0{i}/receipt.json'),
                   **read(OUT / f'build-0{i}/receipt.json')) for i in (1, 2)]
    commands = [dict(command=runner + rel(OUT / name), exit_code=0)
                for name in ['author_map.py', 'crosswalk.py']]
    commands += [dict(command=b['command'], workdir=str(Path(pdf['path']).parent),
                      environment=b['environment'], exit_code=b['exit_code'],
                      wall_seconds=b['wall_seconds'], receipt=b['receipt']) for b in builds]
    commands += [dict(command=runner + '/home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py '
                     + str(Path(pdf['path']).parent / 'sections/apple-quality-inventory.tex')
                     + ' --pdf ' + pdf['path'] + ' --output-json ' + rel(OUT / 'surface-audit.json')
                     + ' --output-md ' + rel(OUT / 'surface-audit.md') + ' --max-examples 2', exit_code=0),
                 dict(command=runner + rel(OUT / 'check_candidate.py'), exit_code=0,
                      wall_seconds=checks['wall_seconds'], earlier_failed_attempt='validation-attempt-01'),
                 dict(command=' '.join(diff_command), exit_code=0),
                 dict(command=runner + rel(Path(__file__)), exit_code=0,
                      started_at=started, measured_through_manifest_seconds=time.monotonic() - timer)]
    save('run-manifest.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Chapter 2 source crosswalk and Version 2.24 service-access author repair',
        git_commit=head, git_worktree='Extensive unrelated dirty work preserved; no commit or push',
        plan=plan, result=rel(OUT / 'result.md'), pdf=pdf, artifact_hashes=hashes,
        prior_manifest=base['prior_manifest'], prior_manifest_sha256=base['prior_manifest_sha256'],
        pointer_relocations=base['pointer_relocations'], commands=commands,
        environment=dict(python_executable=sys.executable, python_prefix=sys.prefix,
                         python_version=sys.version, platform=platform.platform(),
                         conda_env='tfgpu executable selected directly; no shell activation',
                         CUDA_VISIBLE_DEVICES='-1', cpu_gpu_status='CPU only; GPU devices intentionally hidden'),
        data_version='25 hash-bound ledgers in 19 Apple units; pinned FY2024 annual and FY2025 Q1 sources; frozen Version 2.23 comparator',
        random_seeds='N/A deterministic documentary work',
        wall_seconds=dict(builds=[b['wall_seconds'] for b in builds], candidate_check=checks['wall_seconds'],
                          closeout_through_manifest=time.monotonic() - timer,
                          full_unit_elapsed=None, limitation='Full interactive author/review elapsed time was not recorded; component timings are not an end-to-end runtime'),
        author_reading=dict(chapter2=list(range(11, 43)), unchanged_final_pixels_reused=list(range(11, 41)),
                            final_pages_reread=[41, 42], navigation=list(range(1, 8)), boundary=43, dpi=120),
        full_readiness='not_ready', independent_reader='pending', human_acceptance='pending',
        domain_acceptance='pending', network_requests=0))
    verify(hashes)
    save('completion.json', dict(status='bounded_unit_complete',
        manifest_sha256=sha(OUT / 'run-manifest.json'), pdf=pdf, candidate_checks=33,
        manifest_bound_files=len(hashes), full_readiness='not_ready',
        next_work='E14/C07 bounded typed-exchange/failure source audit'))
    print(json.dumps(dict(manifest_bound_files=len(hashes), manifest_sha256=sha(OUT / 'run-manifest.json'),
                          candidate_checks=33, pages=pdf['pages'], readiness='not_ready')))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists(), 'Do not rerun closed units.'
    main()
