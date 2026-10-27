"""Freeze the complete annual Item 1A source-retention unit."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, importlib.util, json, os, platform, re, subprocess, sys, time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    with (OUT / name).open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(mapping):
    bad = [n for n, h in mapping.items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
    assert not bad, bad[:8]


def main():
    started, timer = datetime.now(timezone.utc), time.monotonic()
    base = read(OUT / 'baseline.json')
    prior_path = ROOT / base['prior_manifest']
    prior = read(prior_path)
    assert sha(prior_path) == base['prior_manifest_sha256']
    assert sha(prior_path) == read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes = {reloc.get(n, n): h for n, h in prior['artifact_hashes'].items()}
    verify(prior_hashes)

    source = read(OUT / 'source-checks.json')
    meaning = read(OUT / 'meaning-checks.json')
    assert (source['passed'], meaning['passed']) == (90, 70)
    assert source['failed'] == meaning['failed'] == 0
    assert source['checker_sha256'] == sha(OUT / 'prepare.py')
    verify(source['inputs'])
    verify(meaning['inputs'])
    verify({x['path']: x['sha256'] for x in read(OUT / 'inspection/manifest.json')})

    coverage = read(OUT / 'coverage-update.json')
    assert coverage['not_semantic_completion']
    statuses = ['complete body retained', 'partial dependency only', 'no prior retained reading']
    assert [coverage['counts']['annual'][x] for x in statuses] == [28, 0, 0]
    assert [coverage['counts']['interim'][x] for x in statuses] == [2, 0, 0]
    for row in coverage['records']:
        if 'added_evidence' in row:
            assert sha(ROOT / row['added_evidence']['path']) == row['added_evidence']['sha256']

    pointers = {n: sha(ROOT / n) for n in reloc}
    required = ['Version 2.23', prior['pdf']['sha256'], 'not_ready',
                'apple-remaining-risks-20261010/result.md', '28 complete']
    for n in pointers:
        text = (ROOT / n).read_text()
        assert all(token.casefold() in text.casefold() for token in required), n

    current = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
    previous = (ROOT / reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps = lambda text: [line for line in text.splitlines() if re.match(r'^\| G\d+ ', line)]
    assert len(gaps(current)) == 18 and gaps(current) == gaps(previous)
    for label, target in [('Latest substantive result', OUT / 'result.md'),
                          ('Current manuscript', ROOT / prior['pdf']['path'])]:
        line = next(x for x in current.splitlines() if x.startswith(label + ': '))
        link = re.search(r'\]\(([^)]+)\)', line).group(1)
        assert (ROOT / 'docs/plans' / link).resolve() == target.resolve()

    diff_command = ['git', 'diff', '--check', '--', *pointers, rel(OUT),
                    'docs/plans/accounting-apple-remaining-risks-20261010.md']
    subprocess.run(diff_command, cwd=ROOT, check=True, capture_output=True, text=True)
    save('closeout-checks.json', dict(passed=True, source_checks=90, meaning_checks=70,
        candidate_checks=0, prior_references=len(prior_hashes), current_pointer_hashes=pointers,
        all_eighteen_gap_rows_preserved=True, coverage_counts=coverage['counts'],
        exact_current_pdf_and_result_links=True, diff_check='passed',
        candidate_decision='Current Version 2.23 retained; no new candidate in source-only closure'))

    hashes = {rel(path): sha(path) for path in OUT.rglob('*')
              if path.is_file() and '__pycache__' not in path.parts
              and path.name not in {'run-manifest.json', 'completion.json'}}
    hashes.update(prior_hashes)
    hashes.update(source['inputs'])
    hashes.update(meaning['inputs'])
    hashes.update(pointers)
    helper = ROOT / 'data/accounting-master/apple-legal-20261010/work_unit.py'
    hashes[rel(helper)] = sha(helper)
    hashes['docs/plans/accounting-mission-requirements.md'] = sha(ROOT / 'docs/plans/accounting-mission-requirements.md')
    verify(hashes)

    commands = [dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(OUT / 'prepare.py'),
                     exit_code=0, source_run=read(OUT / 'source-run-receipt.json')),
                dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(Path(__file__)),
                     exit_code=0, started_at=started.isoformat(), wall_seconds=time.monotonic() - timer),
                dict(command=' '.join(diff_command), exit_code=0)]
    save('run-manifest.json', dict(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Apple remaining annual Item 1A source-retention closure annual-09–28 E01/C03/C08',
        git_commit=base['git_commit'],
        git_worktree='Extensive unrelated dirty work preserved; no commit or push',
        plan='docs/plans/accounting-apple-remaining-risks-20261010.md',
        result=rel(OUT / 'result.md'), pdf=prior['pdf'], artifact_hashes=hashes,
        prior_manifest=rel(prior_path), prior_manifest_sha256=sha(prior_path),
        pointer_relocations=base['pointer_relocations'],
        environment=dict(python_executable=sys.executable, python_prefix=sys.prefix,
                         python_version=sys.version, platform=platform.platform(),
                         conda_env=os.environ.get('CONDA_DEFAULT_ENV'), CUDA_VISIBLE_DEVICES='-1',
                         cpu_gpu_status='CPU only; GPU devices intentionally hidden'),
        data_version='Pinned Apple FY2024 annual PDF/text and FY2025 Q1 interim HTML/text; exact hashes retained',
        random_seeds='N/A deterministic documentary work', commands=commands,
        wall_seconds=time.monotonic() - timer, full_readiness='not_ready',
        independent_reader='pending', human_acceptance='pending', domain_acceptance='pending', network_requests=0))
    verify(hashes)
    save('completion.json', dict(status='bounded_unit_complete', manifest_sha256=sha(OUT / 'run-manifest.json'),
        pdf=prior['pdf'], source_checks=90, meaning_checks=70, candidate_checks=0,
        manifest_bound_files=len(hashes), full_readiness='not_ready',
        next_work='Cumulative Chapter 2/source-support crosswalk'))
    print(json.dumps(dict(manifest_bound_files=len(hashes), manifest_sha256=sha(OUT / 'run-manifest.json'),
                          pages=prior['pdf']['pages'], next='cumulative Chapter 2/source-support crosswalk')))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists()
    main()
