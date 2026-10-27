"""Read-only verification by default; completion and four controls record once."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from calculate import calculate

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r03-zero-weight-limit-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r03-zero-weight-limit-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def binding(value):
    assert sha(R / value['path']) == value['sha256'], value['path']


def check():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [row for row in raw.split('\0') if row]
    assert all(row[:2] == ' M' for row in rows)
    assert {row[3:] for row in rows} == set(p['tracked_dirty'])
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    for name in p['controls']:
        assert sha(U / 'controls-before' / name) == p['tracked_dirty'][name]
    calculated = calculate()
    assert calculated == load(U / 'calculation.json')
    assert calculated['counts'] == {'positive_cases': 14, 'refused_inputs': 8, 'constructive_path_points': 6}
    manifest = load(U / 'calculation-manifest.json')
    for name, digest in manifest['bindings'].items():
        assert sha(R / name) == digest, name
    s = load(U / 'source-boundary.json')
    for value in [s['derivation'], s['baseline_method'], s['historical_primary_pdf']] + s['reused_notes'] + s['previous_source_manifests']:
        binding(value)
    assert not s['new_acquisition'] and not s['new_literature_survey']
    assert s['support_class'] == 'PROJECT_DERIVATION' and len(s['claims']) == 5
    for a in s['anchors']:
        binding(a['binding'])
        text = (R / a['binding']['path']).read_text()
        first, last = a['character_span']
        assert text[first:last] == a['quote']
        assert a['lines_by_newline'] == [text[:first].count('\n') + 1, text[:last].count('\n') + 1]
    assert len(s['anchors']) == 5
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('derivation.md', 'result.md', 'review.md'):
        assert (U / name).read_text().strip()
    return p, {**calculated['counts'], 'source_anchors': 5, 'scoped_claims': 5,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'accounting_fallback_admitted': False,
               'runtime_admitted': False}


def record(p, checks):
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent, os.W_OK), path
    assert not (U / 'controls-after').exists()
    replacement = '''The zero-weight CGU limiting argument is complete at
data/accounting-master/r03-zero-weight-limit-20261023/: the positive-weight
capped allocator can approach every cap-and-total feasible vector as starting
balances approach zero, under fixed ceilings and final total. With at least
two eligible assets and a strict interior total there is no unique continuous
extension. Fourteen rational fixtures, six constructive path points and eight
outside-domain refusals pass. This rejects a limit-only fallback; accounting
authority at zero remains unresolved. No manuscript/default/runtime change
or whole-row closure follows. Read-only replay: verify.py without flags.

The user has now selected E3 expected performance at future dates for the same
named companies (repeated_origins). This direction supersedes the earlier
unanswered target question. It does not choose the origin law, issuer weights,
improvement margin, confidence, sample size or inference procedure, and does
not authorise empirical execution. A successor decision record is next.

Next: bind the user's repeated-origins choice in an additive E3 target record,
then audit the matching forecast-origin, dependence, vintage and inference
prerequisites. Preserve the historical unselected target sheets, completed
source inquiries and full Version 3.48 diagnosis. Continue ready internal work.

'''
    marker = 'Next: inspect distinct remaining method-source leads, beginning with the'
    edits = []
    for name in p['controls']:
        target = R / name
        assert target.read_bytes() == (U / 'controls-before' / name).read_bytes()
        assert not target.is_symlink() and os.access(target, os.W_OK)
        text = target.read_text()
        assert text.count(marker) == 1
        first = text.index(marker)
        last = text.index('Completed review evidence:', first)
        after = text[:first] + replacement + text[last:]
        old = 'The E3 target and six scientific choices remain unselected; all 192 vintage\nadmissions remain false.'
        assert after.count(old) == 1
        after = after.replace(old, 'E3 now targets repeated future origins for the named companies; six scientific\nchoices remain unselected and all 192 vintage admissions remain false.', 1)
        edits.append((name, after))
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': 'Fixed-ceiling/total hypothetical model, hand-authored rational fixtures; source-boundary.json',
        'seeds': 'N/A deterministic algebra', 'started_utc': p['started_utc'],
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': {'calculation_seconds': load(U / 'calculation-manifest.json')['wall_seconds'],
                      'whole_session': 'Not measured; reading/editing time not inferred from UTC brackets'},
        'commands': [prefix + rel(U / 'prepare.py'), prefix + rel(U / 'calculate.py') + ' --record',
                     prefix + rel(U / 'record_context.py'), prefix + rel(U / 'verify.py'),
                     prefix + rel(U / 'verify.py') + ' --record', prefix + rel(U / 'verify.py')],
        'stage_provenance': 'Preparation, calculation and context records each once; preflight before completion; final replay verified separately',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Mathematical limit set of existing positive-weight capped reversal allocator',
        'candidate_version': '3.48', 'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'manuscript_changed': False, 'runtime_admitted': False,
        'accounting_fallback_admitted': False, 'independent_human_acceptance': 'pending'})
    for name, after in edits:
        snapshot = U / 'controls-after' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / name).write_text(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_local_derivation_no_accounting_promotion', 'checks': checks,
        'bindings': {rel(path): sha(path) for path in sorted(files)},
        'control_replay_policy': 'Immutable before/after snapshots; live controls may advance in successor units'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    p, checks = check()
    if args.record:
        record(p, checks)
    if (U / 'completion.json').exists():
        c = load(U / 'completion.json')
        for name, digest in c['bindings'].items():
            assert sha(R / name) == digest, name
        assert c['checks'] == checks == load(U / 'checks.json')
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        status = 'read-only preflight passed; not yet recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
