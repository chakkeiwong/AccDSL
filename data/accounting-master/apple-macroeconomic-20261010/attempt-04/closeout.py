"""Close out the annual-01 source unit without rerunning frozen generators."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, platform, re, subprocess, sys, time

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
    for name, digest in mapping.items():
        assert sha(ROOT / name) == digest, name


def main():
    started, timer = datetime.now(timezone.utc), time.monotonic()
    base = read(OUT / 'baseline.json')
    prior = read(ROOT / base['prior_manifest'])
    prior_path = ROOT / base['prior_manifest']
    assert sha(prior_path) == base['prior_manifest_sha256']
    assert sha(prior_path.with_name('completion.json')) == base['prior_completion_sha256']
    verify(prior['artifact_hashes'])
    checks = read(OUT / 'source-checks.json')
    supplement = read(OUT / 'source-claim-supplement.json')
    assert checks['checker_sha256'] == sha(OUT / 'prepare.py')
    assert checks['passed'] == 58 and checks['failed'] == 0
    assert all(x['passed'] for x in checks['checks'])
    verify(checks['inputs'])
    body = supplement['body']
    annual = (ROOT / body['source_path']).read_text()
    assert annual[body['heading']['start']:body['heading']['end']] == body['heading']['quote']
    assert annual[body['body_start']:body['semantic_end']] == ''.join(p['quote'] + '\n\n' for p in body['paragraphs']).rstrip()
    assert annual[body['semantic_end']:body['body_end']] == body['page_furniture']
    for p in body['paragraphs']:
        assert (ROOT / p['path']).read_text() == p['quote']
        assert sha(ROOT / p['path']) == p['file_sha256']
    for d in supplement['selected_dependencies']:
        source = ROOT / d['source_path']
        text = source.read_text()
        assert text[d['start']:d['end']] == d['quote'], d['id']
        assert hashlib.sha256(d['quote'].encode()).hexdigest() == d['quote_sha256'], d['id']
        assert sha(source) == d['source_sha256'], d['id']
        manifest = read(ROOT / d['manifest'])
        assert manifest['artifact_hashes'][d['supplement']] == d['supplement_sha256'], d['id']
        assert sha(ROOT / d['supplement']) == d['supplement_sha256'], d['id']
    context = supplement['interim_context']
    assert sha(ROOT / context['path']) == context['sha256']
    pointers = {x['historical_path']: sha(ROOT / x['historical_path']) for x in base['pointer_relocations']}
    for name in pointers:
        text = (ROOT / name).read_text()
        assert 'apple-macroeconomic-20261010/result.md' in text
        assert 'apple-macroeconomic-20261010/next-source-frontier.md' in text
        assert 'annual-02' in text or 'business-interruption' in text
        assert 'not_ready' in text
    roadmap = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
    previous = (ROOT / base['pointer_relocations'][-1]['preserved_path']).read_text()
    gap_rows = lambda text: [x for x in text.splitlines() if re.match(r'^\| G\d+ ', x)]
    assert len(gap_rows(roadmap)) == 18 and gap_rows(roadmap) == gap_rows(previous)
    subprocess.run(['git', 'diff', '--check', '--', *pointers, 'docs/plans/accounting-apple-macroeconomic-20261010.md'], check=True, capture_output=True, text=True)
    closeout = dict(passed=True, source_checks=58, selected_dependencies=12, annual_paragraphs=4,
        current_pointer_hashes=pointers, verified_prior_references=len(prior['artifact_hashes']),
        all_eighteen_gap_rows_preserved=True, manuscript='Version 2.19 retained; no candidate build',
        independent_reader='pending', human_acceptance='pending', domain_acceptance='pending', diff_check='passed')
    save('closeout-checks.json', closeout)
    hashes = {rel(p): sha(p) for p in OUT.rglob('*') if p.is_file() and p.name not in {'run-manifest.json', 'completion.json'} and '__pycache__' not in p.parts}
    hashes.update(prior['artifact_hashes']); hashes.update(checks['inputs']); hashes.update(pointers)
    verify(hashes)
    now = datetime.now(timezone.utc)
    commands = [json.loads(x) for x in (OUT / 'commands.jsonl').read_text().splitlines()]
    commands += [dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(OUT / 'closeout.py'), exit_code=0,
                      started_at=started.isoformat(), wall_seconds=time.monotonic()-timer),
                 dict(command='git diff --check', exit_code=0)]
    save('run-manifest.json', dict(recorded_at=now.isoformat(),
        unit='Apple annual-01 macroeconomic risk E01/C03/C08', git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        plan='docs/plans/accounting-apple-macroeconomic-20261010.md', result=rel(OUT / 'result.md'),
        pdf=prior['pdf'], artifact_hashes=hashes, prior_manifest=rel(prior_path),
        prior_manifest_sha256=sha(prior_path), pointer_relocations=base['pointer_relocations'],
        environment=dict(python=sys.version, platform=platform.platform(), CUDA_VISIBLE_DEVICES='-1',
            cpu_gpu_status='CPU only; GPU devices intentionally hidden', conda_env=os.environ.get('CONDA_DEFAULT_ENV', 'N/A')),
        data_version='Pinned FY2024 annual PDF/text and FY2025 Q1 interim HTML/text',
        random_seeds='N/A deterministic documentary work', commands=commands,
        wall_seconds=time.monotonic()-timer, full_readiness='not_ready', independent_reader='pending',
        human_acceptance='pending', domain_acceptance='pending', network_requests=0))
    verify(hashes)
    manifest_hash = sha(OUT / 'run-manifest.json')
    save('completion.json', dict(status='bounded_unit_complete', manifest_sha256=manifest_hash, pdf=prior['pdf'],
        source_checks=58, manifest_bound_files=len(hashes), full_readiness='not_ready',
        next_work='Annual-02 business-interruption risk body'))
    print(json.dumps(dict(source_checks=58, selected_dependencies=12, manifest_bound_files=len(hashes),
        manifest_sha256=manifest_hash, readiness='not_ready', next='annual-02 business interruption')))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists()
    main()
