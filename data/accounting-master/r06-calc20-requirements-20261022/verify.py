"""One-time source-result recording; default replay never writes."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r06-calc20-requirements-20261022.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r06-calc20-requirements-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def binding(value):
    assert sha(R / value['path']) == value['sha256'], value['path']


def check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [x for x in raw.split('\0') if x]
    assert {x[3:] for x in rows} == set(p['tracked_dirty'])
    assert all(x[:2] == ' M' for x in rows)
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    d = load(U / 'source-ledger.json')
    assert (len(d['sources']), len(d['figures']), len(d['anchors'])) == (3, 20, 36)
    normalized = {}
    for s in d['sources']:
        binding(s['body'])
        binding(s['visible'])
        rec = load(R / s['receipt'])
        assert rec['url'] == s['url']
        assert rec['exit_code'] == 0 and rec['metrics']['http_code'] == 200
        assert (R / s['body']['path']).stat().st_size == rec['metrics']['size_download']
        normalized[s['id']] = ' '.join((R / s['visible']['path']).read_text().split())
    for key, label in [('prior_11_requirements', 'prior-11-requirements'), ('prior_recommendation', 'prior-recommendation')]:
        binding(d[key])
        normalized[label] = ' '.join((R / d[key]['path']).read_text().split())
    for a in d['anchors']:
        first, last = a['normalized_character_span']
        assert normalized[a['source']][first:last] == a['quote'], a['id']
    index = load(U / 'image-index.json')
    spec = importlib.util.spec_from_file_location('authored_source_parser', U / 'build_records.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parser = module.Text()
    parser.feed((U / 'sources/02-requirements.body').read_text())
    assert len(parser.images) == 20
    for image, f, actual in zip(index, d['figures'], parser.images):
        assert image['index'] == f['index'] and image['src'] == f['src'] == actual['src']
        assert image['url'] == f['url'] and not actual.get('alt', '').strip()
        binding(f['original'])
        rec = load(R / f['receipt'])
        assert rec['url'] == image['url'] and rec['exit_code'] == 0
        assert rec['metrics']['http_code'] == 200
        assert (R / f['original']['path']).stat().st_size == rec['metrics']['size_download'] <= 2097152
        if image['index'] >= 3:
            binding(f['view'])
            binding(f['view_provenance'])
            meta = load(R / f['view_provenance']['path'])
            assert meta['original_sha256'] == f['original']['sha256']
            assert meta['view_sha256'] == f['view']['sha256']
    assert len(list((U / 'sources').glob('*.receipt.json'))) == 23
    anchors = {a['id'] for a in d['anchors']}
    claims = load(U / 'claim-support-ledger.json')['claims']
    mappings = load(U / 'scope-prerequisites.json')['relationships']
    assert len(claims) == 12 and len(mappings) == 10
    for row in claims + mappings:
        assert row['support'] and set(row['support']) <= anchors
    reading = load(U / 'reading-ledger.json')
    assert [i['figure'] for i in reading['image_reading']] == list(range(1, 21))
    assert all(i['inspection'] == 'actually viewed' for i in reading['image_reading'])
    for s in reading['text']:
        binding(s['binding'])
    for name in ('source-support', 'citation-venue', 'backward-snowball', 'forward-snowball', 'claim-support', 'omission-risk'):
        assert load(U / (name + '-ledger.json'))
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('result.md', 'review.md', 'recovery-note.md'):
        text = (U / name).read_text()
        assert ',+' not in text
        if name == 'result.md':
            assert 'not_ready' in text
    return p, {'documents': 3, 'figures_actually_read': 20, 'anchors': 36,
               'claims': 12, 'prerequisite_mappings': 10, 'successful_requests': 23,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'runtime_admitted': False}


def record(p, checks):
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    assert not (U / 'completion.json').exists() and not SUPPLEMENT.exists()
    assert not (U / 'checks.json').exists() and not (U / 'run-manifest.json').exists()
    replacement = '''The bounded Calculations 2.0 requirements inquiry is complete at
data/accounting-master/r06-calc20-requirements-20261022/: three official
documents, 20 actually viewed examples, 36 anchors and ten prerequisite
mappings. The 2019 text proposes dimensional/period relations, completeness
sections and inferred subtotals; it supplies no adopted algorithm or economic-
history identification. Its early duplicate rule differs from final 1.1.
Underlying example filings remain unverified. No policy or manuscript change
and no whole-row closure. Read-only replay: verify.py without flags.

Next: inspect the exact linked 2018 duplicate-facts note under a separately
bounded source plan, after checking existing local sources and exhausted routes.
Keep note guidance, final 1.1 rules and company rounding policy distinct.
Other ready R03–R06 work remains eligible; no completed finite check or
manuscript review is to be restarted.

'''
    edits = []
    marker = 'Next: inspect the newly linked public Calculations 2.0 requirements for the'
    for name in p['controls']:
        assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        before = (R / name).read_text()
        assert before.count(marker) == 1, name
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        edits.append((name, before[:start] + replacement + before[end:]))
    receipts = [load(U / 'sources' / (i + '.receipt.json'))
                for i in ('01-product', '02-requirements', '03-history')]
    receipts += [load(U / 'sources' / f'image-{n:02d}.receipt.json') for n in range(1, 21)]
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; authored standard-library records; Pillow display preparation only',
        'data_version': '23 exact official responses; retained 1.1 comparators; see source-ledger.json',
        'seeds': 'N/A deterministic source inspection; no numeric or stochastic campaign',
        'inquiry_started_utc': p['started_utc'],
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': 'Not measured as continuous active work; request durations retained separately',
        'request_seconds': [r['metrics']['time_total'] for r in receipts],
        'commands': [r['command'] for r in receipts] + [
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'prepare.py')],
        'view_commands': ['env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'prepare_views.py') + ' ' + span
                          for span in ('3 3', '4 6', '7 9', '10 12', '13 15', '16 18', '19 20')],
        'record_commands': ['env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'build_records.py'),
                            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'verify.py') + ' --record',
                            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'verify.py')],
        'view_initialisation_note': 'Image 3 white view was created before prepare_views.py bound its existing bytes; see recovery-note.md',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': '2019 Calculations 2.0 requirements, reproduced examples and missing company premises; source preparation only',
        'candidate_version': '3.48',
        'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'),
        'checks': checks, 'manuscript_changed': False, 'runtime_admitted': False,
        'independent_human_acceptance': 'pending'})
    for name, after in edits:
        (R / name).write_text(after)
        target = U / 'controls-after' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x') as stream:
            stream.write(after)
    assert check()[1] == checks
    files = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files += [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_source_inquiry_no_policy_promotion', 'checks': checks,
        'bindings': {rel(p): sha(p) for p in sorted(files)},
        'control_replay_policy': 'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    p, checks = check()
    if args.record:
        record(p, checks)
    completion = load(U / 'completion.json')
    for name, digest in completion['bindings'].items():
        assert sha(R / name) == digest, name
    assert load(U / 'checks.json') == completion['checks'] == checks
    print(json.dumps({'status': 'recorded and verified' if args.record else 'read-only replay passed', **checks}))


if __name__ == '__main__':
    main()
