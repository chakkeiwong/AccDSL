"""Verify completed documentary evidence read-only; recording is explicit and once."""
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

sys.dont_write_bytecode = True
U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r06-duplicates-guidance-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r06-duplicates-guidance-supplement.json'
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
    normalized = {}
    for key, value in d['sources'].items():
        binding(value)
        normalized[key] = ' '.join((R / value['path']).read_text().split())
    assert set(normalized) == {'note', 'calc11', 'oim', 'req11', 'req20'}
    binding(d['new_document']['body'])
    binding(d['figure']['original'])
    for ident, limit in [('01-note', 12582912), ('02-diagram', 2097152)]:
        receipt = load(U / 'sources' / (ident + '.receipt.json'))
        body = U / 'sources' / (ident + '.body')
        assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
        assert body.stat().st_size == receipt['metrics']['size_download'] <= limit
        assert receipt['metrics']['num_redirects'] <= 5
        assert receipt['metrics']['time_total'] <= 45
        assert (U / 'sources' / (ident + '.headers')).is_file()
        assert (U / 'sources' / (ident + '.stderr')).is_file()
    note = load(U / 'sources/01-note.receipt.json')
    diagram = load(U / 'sources/02-diagram.receipt.json')
    assert note['url'] == d['new_document']['requested_url']
    assert diagram['url'] == note['url'].rsplit('/', 1)[0] + '/images/duplicates-venn.png'
    assert (U / 'sources/02-diagram.body').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    assert len(list((U / 'sources').glob('*.receipt.json'))) == 2
    spec = importlib.util.spec_from_file_location('authored_note_parser', U / 'extract.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    parser = module.Text()
    parser.feed((U / 'sources/01-note.body').read_text())
    assert parser.images == [{'src': 'images/duplicates-venn.png'}]
    assert parser.table_count == 1
    assert '\n'.join(parser.parts) + '\n' == (U / 'sources/01-note.visible.txt').read_text()
    assert len(d['anchors']) == 32
    for a in d['anchors']:
        first, last = a['normalized_character_span']
        assert normalized[a['source']][first:last] == a['quote'], a['id']
    anchors = {a['id'] for a in d['anchors']}
    assert len(anchors) == 32
    claims = load(U / 'claim-support-ledger.json')['claims']
    comparisons = load(U / 'definition-comparison.json')['rows']
    assert len(claims) == len(comparisons) == 12
    for row in claims + comparisons:
        assert row['support'] and set(row['support']) <= anchors
    reading = load(U / 'reading-ledger.json')
    binding(reading['document'])
    binding(reading['figure']['binding'])
    assert reading['visible_lines'] == len(parser.parts) == 265
    covered = [n for a, b in reading['segments'] for n in range(a, b + 1)]
    assert covered == list(range(1, 266))
    assert reading['figure']['inspection'] == d['figure']['inspection'] == 'actually viewed'
    for name in ('source-support', 'citation-venue', 'backward-snowball', 'forward-snowball', 'claim-support', 'omission-risk'):
        assert load(U / (name + '-ledger.json'))
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('result.md', 'review.md', 'recovery-note.md'):
        prose = (U / name).read_text()
        assert ',+' not in prose
    assert 'not_ready' in (U / 'result.md').read_text()
    return p, {'new_documents': 1, 'figures_actually_viewed': 1,
               'successful_requests': 2, 'anchors': 32, 'claims': 12,
               'definition_comparisons': 12, 'protected_files': len(p['protected']),
               'tracked_dirty_paths': len(rows), 'whole_rows_closed': 0,
               'readiness': 'not_ready', 'manuscript_changed': False,
               'runtime_admitted': False}


def record(p, checks):
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists(), path
    replacement = '''The exact 2018 duplicate-facts guidance inquiry is complete at
data/accounting-master/r06-duplicates-guidance-20261023/: one official note,
one actually viewed diagram, 32 anchors and 12 definition comparisons.
Closed intervals require the same-accuracy safeguard. Historical multi-language
duplicates differ from OIM alternatives; highest-accuracy reduction differs
from final1.1 interval intersection. Sections5.1/5.4 remain unresolved;
processor claims remain attributed. No policy, manuscript or whole-row change.
Read-only replay: verify.py without flags; completed one-time stages are frozen.

Next: check retained sources for the exact2013 Inline XBRL Primer and
specification linked by the note. Independently inspect processor obligations
under a fresh bounded plan if not already retained/read. Keep source guidance,
normative requirements and archival provenance separate. Other ready R03–R06
work remains eligible; completed checks and manuscript reviews stay frozen.

'''
    edits = []
    marker = 'Next: inspect the exact linked 2018 duplicate-facts note under a separately'
    for name in p['controls']:
        assert (R / name).read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        before = (R / name).read_text()
        assert before.count(marker) == 1, name
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        edits.append((name, before[:start] + replacement + before[end:]))
    receipts = [load(U / 'sources' / (ident + '.receipt.json')) for ident in ('01-note', '02-diagram')]
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; authored standard-library source checks only',
        'data_version': 'Exact19April2018 note/figure and frozen OIM/1.1/requirements comparators; source-ledger.json',
        'seeds': 'N/A deterministic documentary inspection, no stochastic or numerical campaign',
        'inquiry_started_utc': p['started_utc'], 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': 'Continuous active work not measured; actual observation bounds and curl transfer durations retained in receipts',
        'request_seconds': [r['metrics']['time_total'] for r in receipts],
        'commands': [r['command'] for r in receipts] + [
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'prepare.py'),
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'extract.py') + ' 01-note',
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'build_records.py'),
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'write_ledgers.py'),
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'verify.py') + ' --record',
            'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(U / 'verify.py')],
        'views': ['view_image on sources/02-diagram.body; original PNG, no derivative'],
        'failed_authoring_checks': 'Two builder failures before any records were written; exact quotation spacing corrected; review.md',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Exact2018 duplicate guidance and OIM/final1.1 authority boundaries; internal source preparation',
        'candidate_version': '3.48',
        'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'manuscript_changed': False, 'runtime_admitted': False,
        'independent_human_acceptance': 'pending'})
    for name, after in edits:
        (R / name).write_text(after)
        target = U / 'controls-after' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x') as stream:
            stream.write(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    files += [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_source_inquiry_no_policy_promotion', 'checks': checks,
        'bindings': {rel(path): sha(path) for path in sorted(files)},
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
