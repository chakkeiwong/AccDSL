"""Bind the completed annual-03/04 unit without regenerating frozen evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NEW = ROOT / 'docs/design/proposal/manuscript-competition-transition-20261010'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, value):
    p = OUT / name
    with p.open('x') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(mapping):
    bad = [name for name, digest in mapping.items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    assert not bad, bad[:8]


def main():
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    base = read(OUT / 'baseline.json')
    prior_path = ROOT / base['prior_manifest']
    prior = read(prior_path)
    assert sha(prior_path) == base['prior_manifest_sha256']
    assert sha(prior_path) == read(prior_path.with_name('completion.json'))['manifest_sha256']

    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes = {reloc.get(name, name): digest
                    for name, digest in prior['artifact_hashes'].items()}
    verify(prior_hashes)

    source = read(OUT / 'source-checks.json')
    meaning = read(OUT / 'meaning-checks.json')
    candidate = read(OUT / 'candidate-checks.json')
    assert (source['passed'], meaning['passed'], candidate['passed']) == (28, 28, 16)
    assert source['failed'] == meaning['failed'] == candidate['failed'] == 0
    assert source['checker_sha256'] == sha(OUT / 'prepare.py')
    assert candidate['checker_sha256'] == sha(OUT / 'integrate.py')
    verify({x['path']: x['sha256'] for x in source['inputs']})
    verify(meaning['inputs'])
    verify(candidate['inputs'])

    integration = read(OUT / 'integration-baseline.json')
    verify(integration['protected_hashes'])
    helper = ROOT / 'data/accounting-master/apple-legal-20261010/work_unit.py'
    assert sha(helper) == integration['helper_sha256']
    spec = importlib.util.spec_from_file_location('preservation_helpers', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ancestor_counts = module.ancestry()

    rendering = read(OUT / 'render-manifest.json')
    assert rendering['pdf']['sha256'] == sha(ROOT / rendering['pdf']['path'])
    verify({x['path']: x['sha256'] for x in rendering['images'] + [rendering['navigation_sheet']]})
    verify({x['path']: x['sha256'] for x in read(OUT / 'inspection/manifest.json')})

    coverage = read(OUT / 'coverage-update.json')
    assert coverage['not_semantic_completion']
    assert [coverage['counts']['annual'][x] for x in
            ['complete body retained', 'partial dependency only', 'no prior retained reading']] == [9, 2, 17]
    assert [coverage['counts']['interim'][x] for x in
            ['complete body retained', 'partial dependency only', 'no prior retained reading']] == [2, 0, 0]
    for record in coverage['records']:
        if 'added_evidence' in record:
            assert sha(ROOT / record['added_evidence']['path']) == record['added_evidence']['sha256']

    pointers = {name: sha(ROOT / name) for name in reloc}
    required = ['Version 2.21', rendering['pdf']['sha256'], 'not_ready', 'annual-03',
                'apple-competition-transition-20261010/result.md', 'annual-06']
    for name in pointers:
        text = (ROOT / name).read_text()
        assert all(token in text for token in required), name

    current = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
    previous = (ROOT / reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps = lambda text: [line for line in text.splitlines() if re.match(r'^\| G\d+ ', line)]
    assert len(gaps(current)) == 18 and gaps(current) == gaps(previous)
    for label, target in [('Latest substantive result', OUT / 'result.md'),
                          ('Current manuscript', ROOT / rendering['pdf']['path'])]:
        line = next(line for line in current.splitlines() if line.startswith(label + ': '))
        link = re.search(r'\]\(([^)]+)\)', line).group(1)
        assert (ROOT / 'docs/plans' / link).resolve() == target.resolve()

    diff_command = ['git', 'diff', '--check', '--', *pointers, rel(OUT), rel(NEW),
                    'docs/plans/accounting-apple-competition-transition-20261010.md']
    subprocess.run(diff_command, cwd=ROOT, check=True, capture_output=True, text=True)
    save('closeout-checks.json', dict(
        passed=True, source_checks=28, meaning_checks=28, candidate_checks=16,
        prior_references=len(prior_hashes), ancestor_counts=ancestor_counts,
        current_pointer_hashes=pointers, all_eighteen_gap_rows_preserved=True,
        coverage_counts=coverage['counts'], exact_current_pdf_and_result_links=True,
        diff_check='passed'))

    hashes = {rel(path): sha(path)
              for directory in [OUT, NEW]
              for path in directory.rglob('*')
              if path.is_file() and '__pycache__' not in path.parts
              and path.name not in {'run-manifest.json', 'completion.json'}}
    hashes.update(prior_hashes)
    hashes.update({x['path']: x['sha256'] for x in source['inputs']})
    hashes.update(meaning['inputs'])
    hashes.update(candidate['inputs'])
    hashes.update(pointers)
    hashes[rel(helper)] = sha(helper)
    hashes['docs/plans/accounting-mission-requirements.md'] = sha(ROOT / 'docs/plans/accounting-mission-requirements.md')
    verify(hashes)

    commands = [json.loads(line) for line in (OUT / 'commands.jsonl').read_text().splitlines()]
    commands += [
        dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(Path(__file__)),
             exit_code=0, started_at=started.isoformat(), wall_seconds=time.monotonic() - timer),
        dict(command=' '.join(diff_command), exit_code=0),
    ]
    save('run-manifest.json', dict(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Apple competition and product-transition risk annual-03/04 E01/C03/C08',
        git_commit=base['git_commit'],
        git_worktree='Extensive unrelated dirty work preserved; no commit or push',
        plan='docs/plans/accounting-apple-competition-transition-20261010.md',
        result=rel(OUT / 'result.md'), pdf=rendering['pdf'], artifact_hashes=hashes,
        prior_manifest=rel(prior_path), prior_manifest_sha256=sha(prior_path),
        pointer_relocations=base['pointer_relocations'],
        environment=dict(python_executable=sys.executable, python_prefix=sys.prefix,
                         python_version=sys.version, platform=platform.platform(),
                         conda_env=os.environ.get('CONDA_DEFAULT_ENV'),
                         CUDA_VISIBLE_DEVICES='-1',
                         cpu_gpu_status='CPU only; GPU devices intentionally hidden'),
        data_version='Pinned Apple FY2024 annual PDF/text and FY2025 Q1 interim HTML/text; exact hashes retained',
        random_seeds='N/A deterministic documentary work', commands=commands,
        wall_seconds=time.monotonic() - timer,
        full_readiness='not_ready', independent_reader='pending',
        human_acceptance='pending', domain_acceptance='pending', network_requests=0))
    verify(hashes)
    save('completion.json', dict(status='bounded_unit_complete',
        manifest_sha256=sha(OUT / 'run-manifest.json'), pdf=rendering['pdf'],
        source_checks=28, meaning_checks=28, candidate_checks=16,
        manifest_bound_files=len(hashes), full_readiness='not_ready',
        next_work='Annual-06 component-availability risk'))
    print(json.dumps(dict(manifest_bound_files=len(hashes),
                          manifest_sha256=sha(OUT / 'run-manifest.json'),
                          pages=rendering['pdf']['pages'], next='annual-06')))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists()
    main()
