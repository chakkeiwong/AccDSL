"""Read-only replay by default; completion/control recording is explicit and once."""
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
PLAN = R / 'docs/plans/accounting-r06-formula-binding-20261023.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r06-formula-binding-supplement.json'
IDS = ('01-variables', '02-formula', '03-valueassertions', '04-variablehistory',
       '05-formulahistory', '06-assertionhistory', '07-implicitfilters',
       '08-validation', '09-implicithistory', '10-validationhistory', '11-xdm',
       '12-xdm20', '13-xdmerrata')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}
norm = lambda text: ' '.join(text.split())


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def binding(value):
    assert sha(R / value['path']) == value['sha256'], value['path']


def check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    raw = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
    rows = [row for row in raw.split('\0') if row]
    assert {row[3:] for row in rows} == set(p['tracked_dirty'])
    assert all(row[:2] == ' M' for row in rows)
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    for name in p['controls']:
        assert sha(U / 'controls-before' / name) == p['tracked_dirty'][name]
    d = load(U / 'source-ledger.json')
    assert set(d['sources']) == set(IDS) | {'note2018'}
    assert set(d['new_documents']) == set(IDS)
    binding(d['discovery_index'])
    binding(d['earlier_note_inquiry'])
    lines = {}
    for ident, value in d['sources'].items():
        binding(value)
        lines[ident] = (R / value['path']).read_text().splitlines()
    parser_path = R / 'data/accounting-master/r06-duplicates-guidance-20261023/extract.py'
    spec = importlib.util.spec_from_file_location('authored_source_text_parser', parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(list((U / 'sources').glob('*.receipt.json'))) == 13
    image_count = 0
    for ident in IDS:
        receipt = load(U / 'sources' / (ident + '.receipt.json'))
        body = U / 'sources' / (ident + '.body')
        meta = load(U / 'sources' / (ident + '.structure.json'))
        binding(d['new_documents'][ident])
        assert receipt['id'] == ident and receipt['url'] in PLAN.read_text()
        assert receipt['exit_code'] == 0 and receipt['metrics']['http_code'] == 200
        assert receipt.get('started_utc') and receipt.get('finished_utc')
        assert receipt['started_utc'] <= receipt['finished_utc']
        assert body.stat().st_size == receipt['metrics']['size_download'] <= 12582912
        assert 0 <= receipt['metrics']['num_redirects'] <= 5
        assert 0 <= receipt['metrics']['time_total'] <= 45
        assert all(x in receipt['command'] for x in ('--connect-timeout 15', '--max-time 45', '--max-redirs 5', '--max-filesize 12582912'))
        assert '--retry' not in receipt['command']
        assert all((U / 'sources' / (ident + s)).is_file() for s in ('.headers', '.stderr'))
        assert sha(body) == meta['body_sha256']
        assert sha(U / 'sources' / (ident + '.visible.txt')) == meta['visible_sha256']
        assert sha(parser_path) == meta['parser_sha256']
        parser = module.Text()
        parser.feed(body.read_text())
        assert parser.parts == lines[ident]
        assert parser.links == meta['links'] and parser.images == meta['images']
        assert parser.headings == meta['headings'] and parser.table_count == meta['table_count']
        image_count += len(meta['images'])
    anchors = {a['id']: a for a in d['anchors']}
    assert len(anchors) == len(d['anchors']) == 44
    reading = load(U / 'reading-ledger.json')
    assert reading['whole_specification_read'] is reading['whole_formula_family_read'] is False
    assert {r['source'] for r in reading['sources']} == set(d['sources'])
    assert len(reading['images']) == image_count
    assert all(row['actually_viewed_in_this_unit'] is False for row in reading['images'])
    for row in reading['sources']:
        binding(row['binding'])
        n = len(lines[row['source']])
        assert row['visible_lines'] == n
        spans = row['actually_read_spans']
        assert all(1 <= a <= b <= n for a, b in spans)
        assert all(spans[i][1] < spans[i + 1][0] for i in range(len(spans) - 1))
        for a in [a for a in anchors.values() if a['source'] == row['source']]:
            first, last = a['visible_lines']
            assert any(lo <= first <= last <= hi for lo, hi in spans), a['id']
            assert norm('\n'.join(lines[row['source']][first - 1:last])) == a['quote']
            lo, hi = a['normalized_character_span']
            assert norm((R / row['binding']['path']).read_text())[lo:hi] == a['quote']
    assert 'identical variable-set evaluations' in anchors['V-identical']['quote']
    assert 'No fact occurs more than once' in anchors['V-sequence']['quote']
    assert '09 December 2010' in anchors['V-errata']['quote'] and '20 June 2013' in anchors['V-errata']['quote']
    assert 'MAY be evaluated once for each' in anchors['T-may']['quote']
    assert 'revised 7 September 2015' in anchors['X20-edition']['quote']
    assert 'place-holder' in anchors['X20-errata']['quote']
    claims = load(U / 'claim-support-ledger.json')['claims']
    rules = load(U / 'rule-comparison.json')['rows']
    assert len(claims) == len(rules) == 18
    assert {c['id'] for c in claims} == {c['id'] for c in rules}
    assert all(c['support'] and set(c['support']) <= set(anchors) for c in claims + rules)
    example = load(U / 'binding-example.json')
    assert len(example['cases']) == 5
    assert [c['distinct_possible_data_sets'] for c in example['cases']] == [4, 1, 4, 0, 0]
    assert example['mandatory_processor_call_count'] == 'not established'
    assert len(load(U / 'assumption-audit.json')['rows']) == 6
    html = load(U / 'html-inspection.json')['rows']
    assert [len(row['captures']) for row in html] == [3, 1, 1, 2]
    for row in html:
        binding(row['body'])
        assert {c['needle'] for c in row['captures']} == set(row['needles'])
    assert sha(U / 'source-ledger.json') == load(U / 'anchor-repair.json')['after_sha256']
    for name in ('source-support', 'citation-venue', 'backward-snowball', 'forward-snowball', 'claim-support', 'omission-risk'):
        assert load(U / (name + '-ledger.json'))
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('result.md', 'review.md', 'recovery.md'):
        assert (U / name).read_text().strip()
    return p, {'documents': 13, 'anchors': 44, 'claims': 18, 'rule_rows': 18,
               'symbolic_cases': 5, 'html_captures': 7, 'research_ledgers': 6,
               'whole_specification_read': False, 'protected_files': len(p['protected']),
               'tracked_dirty_paths': len(rows), 'whole_rows_closed': 0,
               'readiness': 'not_ready', 'manuscript_changed': False, 'runtime_admitted': False}


def record(p, checks):
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    outputs = (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT)
    for path in outputs:
        assert not path.exists(), path
        assert path.parent.is_dir() and os.access(path.parent, os.W_OK), path.parent
    assert not (U / 'controls-after').exists()
    replacement = '''The Formula duplicate-binding inquiry is complete at
data/accounting-master/r06-formula-binding-20261023/: thirteen documents,
44 anchors, 18 claim/rule rows and five symbolic cases. Four possible singleton
data sets follow under explicit assumptions; Validation's MAY does not establish
mandatory processor calls. Conditional sequence/matches, filters, preconditions
and identity rules remain distinct. No installed, policy, manuscript or whole-row
promotion follows. Read-only replay: verify.py without flags; one-time stages
are frozen.

Next: audit the proposed native-XBRL occurrence, reduction and assertion
boundaries against the frozen 2018 guidance, Inline and Formula findings.
Repair only concrete confirmed defects under a fresh bounded audited plan.
Other ready internal work remains eligible; completed source acquisitions and
the full Version 3.48 manuscript diagnosis stay frozen.

'''
    marker = 'Next: inspect retained sources for the exact Formula1.0 references behind the'
    edits = []
    for name in p['controls']:
        target = R / name
        assert target.read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        assert target.is_file() and not target.is_symlink() and os.access(target, os.W_OK), name
        before = target.read_text()
        assert before.count(marker) == 1, name
        start = before.index(marker)
        end = before.index('Completed review evidence:', start)
        edits.append((name, before[:start] + replacement + before[end:]))
    receipts = [load(U / 'sources' / (ident + '.receipt.json')) for ident in IDS]
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    recovered = [prefix + rel(U / 'prepare.py')]
    recovered += [prefix + rel(U / 'extract.py') + ' ' + ident for ident in IDS[:11]]
    resumed = [prefix + rel(U / 'recover_check.py')]
    resumed += [prefix + rel(U / 'extract.py') + ' ' + ident for ident in IDS[11:]]
    resumed += [prefix + rel(U / name) for name in
                ('build_records.py', 'repair_anchor_bounds.py', 'write_ledgers.py')]
    resumed += [prefix + rel(U / 'verify.py'), prefix + rel(U / 'verify.py') + ' --record',
                prefix + rel(U / 'verify.py')]
    # All destination and replacement checks precede the first completion write.
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden; authored standard-library tools only',
        'data_version': 'Exact retained XBRL editions/histories, XDM editions and errata placeholder; source-ledger.json',
        'seeds': 'N/A deterministic documentary inquiry; no stochastic comparison',
        'inquiry_started_utc': p['started_utc'], 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': 'Continuous active work not measured across restart; observed UTC receipt brackets are not process durations',
        'request_seconds': {ident: row['metrics']['time_total'] for ident, row in zip(IDS, receipts)},
        'commands': [row['command'] for row in receipts] + recovered + resumed,
        'stage_provenance': {
            'recovered_before_restart': recovered,
            'post_restart_authored_stages': resumed,
            'acquisitions': '01–11 recovered; 12–13 executed after restart; each once',
            'recording_commands': 'Preflight passed before this recording; final replay is checked separately'},
        'reading': rel(U / 'reading-ledger.json'), 'recovery': rel(U / 'recovery.md'),
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U)})
    write(SUPPLEMENT, {
        'scope': 'Conditional Formula duplicate binding and evaluation; internal source preparation',
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
        target = U / 'controls-after' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x') as stream:
            stream.write(after)
        (R / name).write_text(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    files += [PLAN, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_source_comparison_no_policy_promotion', 'checks': checks,
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
        completion = load(U / 'completion.json')
        for name, digest in completion['bindings'].items():
            assert sha(R / name) == digest, name
        assert load(U / 'checks.json') == completion['checks'] == checks
        status = 'recorded and verified' if args.record else 'read-only replay passed'
    else:
        status = 'read-only preflight passed; not yet recorded'
    print(json.dumps({'status': status, **checks}))


if __name__ == '__main__':
    main()
