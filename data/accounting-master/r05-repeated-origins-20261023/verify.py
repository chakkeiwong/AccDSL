"""Read-only replay by default; completion and control refresh record once."""
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
PLAN = R / 'docs/plans/accounting-r05-repeated-origins-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r05-repeated-origins-supplement.json'
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

    c = load(U / 'choice.json')
    assert c['selected_design'] == 'repeated_origins'
    assert c['user_answer_verbatim'] == 'Expected performance at future dates for the same named companies (recommended)'
    for b in (c['predecessor_target_sheets'], c['active_panel']):
        binding(b)
    sheets = load(R / c['predecessor_target_sheets']['path'])
    panel = load(R / c['active_panel']['path'])
    assert sheets['selected_design'] is None
    assert c['selected_target_sheet'] == next(s for s in sheets['sheets'] if s['id'] == 'repeated_origins')
    assert c['frozen_e3'] == sheets['frozen_e3']
    assert c['unselected'] == sheets['unselected']
    fields = {'deployment_population', 'weights', 'improvement_margin',
              'confidence_level', 'inference_procedure', 'sample_size'}
    assert set(c['unselected']) == fields | {'empirical_execution'}
    assert all(c['unselected'][k] is None for k in fields)
    assert c['unselected']['empirical_execution'] is False
    companies = [{'issuer_id': row['issuer_id'], 'legal_name': row['legal_name'],
                  'source_panel_family_label': row['standard_family'], 'financial_mapping_admitted': False}
                 for row in panel['issuers']]
    assert c['named_companies'] == companies
    assert {i['issuer_id'] for i in companies} == {
        'apple', 'caterpillar', 'jpmorgan', 'henkel', 'hsbc',
        'munich_re', 'saic_motor', 'ping_an', 'midea'}
    assert c['population_status'] == {'issuer_membership': 'selected fixed panel',
        'future_origin_law': None, 'regime_or_stability': None, 'deployment_population_admitted': False}
    assert all(c['forecast_task'][k] is None for k in ('interval', 'cutoff', 'origin_grouping'))
    assert c['issuer_weights']['values'] is None
    assert c['historical_vintage_admissions'] == 0
    assert c['empirical_execution'] is False and c['future_issuer_generalization_selected'] is False

    v = load(R / 'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json')
    assert len(v['rows']) == 192 and len(v['families']) == 9
    assert {f['issuer_id'] for f in v['families']} == {i['issuer_id'] for i in companies}
    assert all(row['selected_byte_available_at'] is None and row['as_of_admission'] is False for row in v['rows'])
    tasks = load(U / 'prerequisites.json')
    assert tasks['choice_is_not_empirical_admission'] is True and tasks['global_continuation_veto'] is False
    assert [t['id'] for t in tasks['rows']] == [f'E3-R{i:02}' for i in range(1, 12)]
    assert [t['status'] for t in tasks['rows']] == [
        'selected', 'pending_user_preference', 'pending_user_preference', 'unresolved', 'unresolved',
        'unadmitted', 'existing_obligations_preserved', 'unselected', 'unselected', 'unselected', 'held']
    seen = set()
    for t in tasks['rows']:
        assert set(t['depends_on']) <= seen and t['owner'] and t['next_action']
        seen.add(t['id'])

    inputs = load(U / 'input-bindings.json')
    assert len(inputs['bindings']) == 10
    for b in inputs['bindings'] + [inputs['new_mathematics']]:
        binding(b)
    calculated = calculate()
    assert calculated == load(U / 'calculation.json')
    assert len(calculated['fixed_panel']) == 2
    assert all(row['worlds'] == 64 for row in calculated['fixed_panel'])
    assert calculated['serial_overlap']['worlds'] == 8
    assert calculated['nine_by_eight_illustration']['company_data'] is False
    manifest = load(U / 'calculation-manifest.json')
    for name, digest in manifest['bindings'].items():
        assert sha(R / name) == digest, name
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('design.md', 'derivation.md', 'result.md', 'review.md'):
        assert (U / name).read_text().strip()
    return p, {'selected_design': 'repeated_origins', 'named_companies': 9,
               'prerequisites': 11, 'input_bindings': 10, 'vintage_admissions': 0,
               'fixed_panel_cases': 2, 'worlds_per_case': 64, 'serial_worlds': 8,
               'protected_files': len(p['protected']), 'tracked_dirty_paths': len(rows),
               'whole_rows_closed': 0, 'readiness': 'not_ready',
               'manuscript_changed': False, 'empirical_execution': False, 'runtime_admitted': False}


def record(p, checks):
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent, os.W_OK), path
    assert not (U / 'controls-after').exists()
    replacement = '''The E3 repeated-origins decision is recorded at
data/accounting-master/r05-repeated-origins-20261023/: the user's exact answer,
the nine named companies, unchanged E3 scores/comparators and eleven ordered
prerequisites. Fixed company identities retain future common and serial shocks;
two complete 64-world examples and an eight-world overlap example check the
conditional covariance derivation. They provide no inference procedure or
sample-size estimate. Forecast-period and company-weight objectives are pending;
no answer is inferred. All192 vintage admissions stay false. Read-only replay:
verify.py without flags; completed one-time stages are frozen.

Next: resolve the pending forecast-period and company-weight objectives when
the user answers. Meanwhile prepare the eligibility, failure and forecast-lock
contract common to these choices, after auditing existing coverage obligations.
Do not select an origin law, numerical weights or empirical defaults from
silence. Preserve the historical target sheets and full Version3.48 diagnosis.

'''
    marker = "Next: bind the user's repeated-origins choice in an additive E3 target record,"
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
        old = 'not authorise empirical execution. A successor decision record is next.'
        assert after.count(old) == 1
        after = after.replace(old, 'not authorise empirical execution. The successor record is described below.', 1)
        edits.append((name, after))
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
        'data_version': 'Frozen panel/target/vintage records and explicit finite synthetic laws; input-bindings.json',
        'seeds': 'N/A complete deterministic enumeration', 'started_utc': p['started_utc'],
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': {'calculation_seconds': load(U / 'calculation-manifest.json')['wall_seconds'],
                      'whole_session': 'Not measured; reading/editing time not inferred from UTC brackets'},
        'commands': [prefix + rel(U / 'prepare.py'), prefix + rel(U / 'calculate.py') + ' --record',
                     prefix + rel(U / 'record_choice.py'), prefix + rel(U / 'verify.py'),
                     prefix + rel(U / 'verify.py') + ' --record', prefix + rel(U / 'verify.py')],
        'stage_provenance': 'Preparation, calculation and choice each once; first preflight schema-count assertion failed and verifier was repaired as recorded in recovery.md; subsequent preflight before completion; final replay verified separately',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Explicit user selection of E3 repeated future origins for the fixed named panel; conditional covariance boundary',
        'candidate_version': '3.48', 'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'),
        'choice': bind(U / 'choice.json'), 'checks': checks,
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
        'status': 'complete_direction_and_mathematical_boundary_no_empirical_admission', 'checks': checks,
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
