"""Verify retained evidence without rerunning the frozen reconciler."""
from pathlib import Path
from datetime import datetime, timezone
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
    for name, digest in mapping.items():
        assert sha(ROOT / name) == digest, name


def main():
    start = time.monotonic()
    started = datetime.now(timezone.utc)
    base = read(OUT / 'baseline.json')
    prior_path = ROOT / base['prior_manifest']
    prior = read(prior_path)
    assert sha(prior_path) == base['prior_manifest_sha256']
    assert sha(prior_path) == read(prior_path.with_name('completion.json'))['manifest_sha256']
    reloc = {x['historical_path']: x['preserved_path'] for x in base['pointer_relocations']}
    prior_hashes = {reloc.get(n, n): h for n, h in prior['artifact_hashes'].items()}
    verify(prior_hashes)
    verify(read(prior_path.with_name('baseline.json'))['protected_hashes'])
    helper = ROOT / 'data/accounting-master/apple-legal-20261010/work_unit.py'
    spec = importlib.util.spec_from_file_location('preservation_helpers', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ancestor_counts = module.ancestry()
    checks = read(OUT / 'checks.json')
    coverage = read(OUT / 'risk-coverage.json')
    verify(checks['inputs'])
    assert checks['inputs'] == coverage['inputs']
    assert sha(OUT / 'reconcile.py') == checks['checker_sha256']
    assert checks['passed'] == 65 and checks['failed'] == 0
    assert all(x['passed'] for x in checks['checks'])
    assert coverage['new_inventory_not_counted_as_prior_reading']
    assert coverage['not_semantic_completion'] and not coverage['excluded_mismatches']
    assert coverage['prior_accepted_supplements'] == 13
    expected = {'annual': (5, 3, 20), 'interim': (2, 0, 0)}
    statuses = ['complete body retained', 'partial dependency only', 'no prior retained reading']
    source_text = {}
    for source in expected:
        scope = read(OUT / (source + '-scope.json'))
        source_text[source] = (ROOT / scope['source']['extraction_path']).read_text()
        t = source_text[source]
        assert hashlib.sha256(t[scope['start']:scope['end']].encode()).hexdigest() == scope['sha256']
        ranges = scope['ranges']
        assert ranges[0][0] == scope['start'] and ranges[-1][1] == scope['end']
        assert all(a[1] == b[0] for a, b in zip(ranges, ranges[1:]))
        rows = [r for r in coverage['records'] if r['source'] == source]
        assert tuple(sum(r['retention_status'] == s for r in rows) for s in statuses) == expected[source]
        for r in rows:
            q = t[r['start']:r['body_end']]
            assert (ROOT / r['body_path']).read_text() == q
            assert sha(ROOT / r['body_path']) == r['body_sha256'] == r['quote_sha256']
            assert ' '.join(t[r['start']:r['heading_end']].split()) == r['heading']
            assert all('/apple-risk-coverage-' not in x['json_path'] for x in r['prior_overlaps'])
    repairs = read(OUT / 'locator-scope-repairs.json')
    assert repairs['exclusions'] == coverage['scope_exclusions'] and len(repairs['exclusions']) == 2
    for r in repairs['repairs']:
        assert source_text['annual'][r['start']:r['end']] == r['quote']
        assert (ROOT / r['retained_span']).read_text() == r['quote'] + '\n'
        assert hashlib.sha256(r['quote'].encode()).hexdigest() == r['sha256']
    renders = read(OUT / 'hierarchy-render.json')
    verify({r['path']: r['sha256'] for r in renders['images'] + [renders['contact']]})
    pointers = {n: sha(ROOT / n) for n in reloc}
    for n in pointers:
        text = (ROOT / n).read_text()
        assert all(s in text for s in ['Version 2.19', prior['pdf']['sha256'], 'not_ready', 'macroeconomic']), n
        assert 'apple-risk-coverage-20261010/result.md' in text, n
    road = (ROOT / 'docs/plans/accounting-master-current.md').read_text()
    previous = (ROOT / reloc['docs/plans/accounting-master-current.md']).read_text()
    gaps = lambda text: [x for x in text.splitlines() if re.match(r'^\| G\d+ ', x)]
    assert len(gaps(road)) == 18 and gaps(road) == gaps(previous)
    for label, target in [('Latest substantive result', OUT / 'result.md'), ('Current manuscript', ROOT / prior['pdf']['path'])]:
        row = next(x for x in road.splitlines() if x.startswith(label + ': '))
        link = re.search(r'\]\(([^)]+)\)', row).group(1)
        assert (ROOT / 'docs/plans' / link).resolve() == target.resolve()
    diff_command = ['git', 'diff', '--check', '--', *pointers, 'docs/plans/accounting-apple-risk-coverage-20261010.md']
    subprocess.run(diff_command, check=True, capture_output=True, text=True)
    save('closeout-checks.json', dict(passed=True, source_checks=65, current_pointer_hashes=pointers,
        verified_prior_references=len(prior_hashes), ancestor_counts=ancestor_counts,
        all_eighteen_gap_rows_preserved=True, hierarchy_review='Original annual pages 8–20, navigation only',
        scope_repairs_verified=True, diff_check='passed'))
    hashes = {rel(p): sha(p) for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    hashes.update(prior_hashes)
    hashes.update(checks['inputs'])
    hashes.update(pointers)
    hashes[rel(helper)] = sha(helper)
    verify(hashes)
    save('run-manifest.json', dict(recorded_at=datetime.now(timezone.utc).isoformat(),
        unit='Apple Item 1A risk-coverage reconciliation E01/C03/C08',
        git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        plan='docs/plans/accounting-apple-risk-coverage-20261010.md', result=rel(OUT / 'result.md'),
        pdf=prior['pdf'], artifact_hashes=hashes, prior_manifest=rel(prior_path),
        prior_manifest_sha256=sha(prior_path), pointer_relocations=base['pointer_relocations'],
        environment=dict(python=sys.version, platform=platform.platform(), CUDA_VISIBLE_DEVICES='-1',
            cpu_gpu_status='CPU only; GPU devices intentionally hidden', conda_env='N/A system python3'),
        data_version='Pinned FY2024 annual PDF/text and FY2025 Q1 interim HTML/text',
        random_seeds='N/A deterministic documentary diagnostic',
        commands=[dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(OUT / 'reconcile.py'),
                       exit_code=0, wall_seconds=checks['wall_seconds'], timing_scope='Diagnostic stage only; earlier total not recorded'),
                  dict(command='CUDA_VISIBLE_DEVICES=-1 python3 ' + rel(Path(__file__)),
                       exit_code=0, started_at=started.isoformat(), wall_seconds=time.monotonic()-start),
                  dict(command=' '.join(diff_command), exit_code=0)],
        resumed_closeout_wall_seconds=time.monotonic()-start, full_readiness='not_ready',
        independent_reader='pending', human_acceptance='pending', domain_acceptance='pending', network_requests=0))
    save('completion.json', dict(status='bounded_unit_complete', manifest_sha256=sha(OUT / 'run-manifest.json'),
        pdf=prior['pdf'], source_checks=65, manifest_bound_files=len(hashes), full_readiness='not_ready',
        next_work='Complete annual-01 macroeconomic risk body and query-relevant dependencies'))
    print(json.dumps(dict(source_checks=65, manifest_bound_files=len(hashes),
        manifest_sha256=sha(OUT / 'run-manifest.json'), readiness='not_ready', next='annual-01 macroeconomic risk')))


if __name__ == '__main__':
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (OUT / 'completion.json').exists()
    main()
