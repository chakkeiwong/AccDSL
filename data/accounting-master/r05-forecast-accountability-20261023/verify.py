"""Read-only verification; --record freezes this documentary unit once."""
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
PLAN = R / 'docs/plans/accounting-r05-forecast-accountability-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-forecast-accountability-supplement.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}
INPUTS = [
    ('data/accounting-master/r05-repeated-origins-20261023/choice.json', 'Explicit user direction; pending preferences and six scientific choices'),
    ('data/accounting-master/r05-repeated-origins-20261023/design.md', 'Fixed-panel target and common failure/lock requirements'),
    ('data/accounting-master/r05-repeated-origins-20261023/prerequisites.json', 'E3-R05 eligibility/failure/refit and E3-R06 source prerequisites'),
    ('data/accounting-master/r05-target-overlap-20261018/specification.md', 'Proposed observation records, denominators, first releases and exposure'),
    ('data/accounting-master/r05-target-overlap-20261018/target-sheets.json', 'Frozen E3 score/baseline/economics and historical unselected state'),
    ('docs/design/proposal/methods/future-validation-20261015.md', 'E3 section: point-law CRPS, scale, first release and service denominator'),
    ('docs/design/proposal/methods/forecasting-methods-v1.md', 'Lines150-178: historic forecast-validation proposal and limits'),
    ('data/accounting-master/r05-vintage-admission-20261018/reconciliation.json', 'All192 selected-byte admissions remain false')]


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


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
    c = load(R / INPUTS[0][0])
    assert c['selected_design'] == 'repeated_origins' and len(c['named_companies']) == 9
    assert c['issuer_weights']['values'] is None
    assert all(c['forecast_task'][k] is None for k in ('interval', 'cutoff', 'origin_grouping'))
    sheets = load(R / INPUTS[4][0])
    assert c['frozen_e3'] == sheets['frozen_e3'] and sheets['selected_design'] is None
    assert c['unselected'] == sheets['unselected'] and c['empirical_execution'] is False
    v = load(R / INPUTS[-1][0])
    assert len(v['rows']) == 192
    assert all(x['selected_byte_available_at'] is None and x['as_of_admission'] is False for x in v['rows'])
    result = calculate()
    assert result == load(U / 'calculation.json')
    assert result['actual_empirical_admission'] is False and result['weights_selected'] is False
    for name, digest in load(U / 'calculation-manifest.json')['bindings'].items():
        assert sha(R / name) == digest, name
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('contract.md', 'result.md', 'review.md'):
        assert (U / name).read_text().strip()
    return p, {**result['counts'], 'input_bindings': len(INPUTS), 'vintage_admissions': 0,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'empirical_execution': False, 'runtime_admitted': False}


def record(p, checks):
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', U / 'input-bindings.json', SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent, os.W_OK), path
    assert not (U / 'controls-after').exists()
    replacement = '''The E3 forecast-accountability proposal is complete at
data/accounting-master/r05-forecast-accountability-20261023/: separate timing,
exposure, attempt, outcome and scale statuses; first-release/retry rules; and
exact original-weight denominators. Twelve time cases, four invalid-bound
refusals, six fictional cells, ten corruptions and two aggregation boundaries
pass. A score on a late forecast remains retrospective; an observed contribution
cannot replace a full-service effect. No weights, fallback or empirical design
are selected. Safe replay: verify.py without flags; one-time stages are frozen.

Next: use the pending forecast-period and company-weight answers to finalise
the first E3 task. Meanwhile audit remaining internal source and design work
against the open obligation records; do not repeat completed readings or
known rejected access routes. Future-origin law, quantitative decisions,
source admission and matched inference remain unresolved. No global
continuation veto has fired.

'''
    marker = 'Next: resolve the pending forecast-period and company-weight objectives when'
    edits = []
    for name in p['controls']:
        target = R / name
        assert target.read_bytes() == (U / 'controls-before' / name).read_bytes()
        assert not target.is_symlink() and os.access(target, os.W_OK)
        text = target.read_text()
        assert text.count(marker) == 1
        first = text.index(marker)
        last = text.index('Completed review evidence:', first)
        edits.append((name, text[:first] + replacement + text[last:]))
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'checks.json', checks)
    write(U / 'input-bindings.json', {'bindings': [{**bind(R / name), 'scope': scope} for name, scope in INPUTS],
        'source_use': 'Existing project source/technical notes reused; no new literature acquisition, theorem inspection or survey'})
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': 'Frozen E3 records; six fictional point-law cells and finite supplied timing/status examples',
        'seeds': 'N/A deterministic authored examples', 'started_utc': p['started_utc'],
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': {'calculation_seconds': load(U / 'calculation-manifest.json')['wall_seconds'],
                      'whole_session': 'Not measured; reading/editing time not inferred from UTC brackets'},
        'commands': [prefix + rel(U / 'prepare.py'), prefix + rel(U / 'calculate.py'),
                     prefix + rel(U / 'calculate.py') + ' --record', prefix + rel(U / 'verify.py'),
                     prefix + rel(U / 'verify.py') + ' --record', prefix + rel(U / 'verify.py')],
        'stage_provenance': 'Preparation once; calculation preflight then one record; completion preflight then one record; final replay separately',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Proposed E3 orthogonal status, chronology, first-release/retry and failure-denominator decisions',
        'candidate_version': '3.48', 'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'manuscript_changed': False, 'runtime_admitted': False,
        'empirical_execution': False, 'independent_human_acceptance': 'pending'})
    for name, after in edits:
        snapshot = U / 'controls-after' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / name).write_text(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts] + [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_proposed_contract_and_finite_examples_no_empirical_admission', 'checks': checks,
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
