"""Read-only replay by default. Explicit completion recording is one-time."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from projection import run

U = Path(__file__).resolve().parent
R = U.parents[2]
PLAN = R / 'docs/plans/accounting-r06-native-duplicate-contract-20261023.md'
NOTE = R / 'docs/design/proposal/architecture/native-duplicate-consumer-boundary-proposed-v1.md'
REVIEW = R / 'data/accounting-master/readability-repair-20261022-theta'
SUPPLEMENT = REVIEW / 'r06-native-duplicate-contract-supplement.json'
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
    d = load(U / 'comparison-ledger.json')
    assert len(d['documents']) == 13 and len(d['design_anchors']) == 19 and len(d['rows']) == 12
    assert not d['independent_review'] and not d['new_literature_survey']
    for v in list(d['documents'].values()) + d['inputs'] + d['static_authored_checker_readings'] + [d['corrigendum']]:
        binding(v)
    anchors = {a['id']: a for a in d['design_anchors']}
    assert len(anchors) == len(d['design_anchors'])
    for a in anchors.values():
        doc = d['documents'][a['document']]
        lines = (R / doc['path']).read_text().splitlines()
        first, last = a['lines']
        assert len(lines) == doc['lines'] and any(lo <= first <= last <= hi for lo, hi in doc['read_spans'])
        assert a['quote'] == '\n'.join(lines[first - 1:last])
    source_ids = set()
    for ident, item in d['reused_source_inquiries'].items():
        for v in [item['completion'], item['source_ledger'], item['result']] + list(item['research_ledgers'].values()):
            binding(v)
        assert len(item['research_ledgers']) == 6
        original = load(R / item['source_ledger']['path'])
        originals = {a['id']: a for a in original['anchors']}
        for a in item['anchors']:
            assert a == originals[a['id']]
            source = original['sources'][a['source']]
            binding(source)
            text = ' '.join((R / source['path']).read_text().split())
            first, last = a['normalized_character_span']
            assert text[first:last] == a['quote']
            source_ids.add(ident + ':' + a['id'])
    assert len(source_ids) == 23
    for row in d['rows']:
        assert set(row['design_support']) <= set(anchors)
        assert set(row['source_support']) <= source_ids
    assert 'until an explicit alias decision' in anchors['D-wording']['quote']
    assert 'Source occurrences stay distinct after such\na decision.' in anchors['D-alias']['quote']
    projected = run()
    assert projected == load(U / 'examples-and-projection.json')
    assert len(projected['negative_controls']) == 8 and len(projected['examples']['cases']) == 7
    formula = load(R / 'data/accounting-master/r06-formula-binding-20261023/binding-example.json')
    case = next(c for c in projected['examples']['cases'] if c['id'] == 'formula-bindings')
    assert case['possible_data_set_counts'] == [v['distinct_possible_data_sets'] for v in formula['cases'][:3]]
    assert case['mandatory_processor_calls'] == formula['mandatory_processor_call_count']
    interval = load(R / 'data/accounting-master/r06-calc11-conformance-source-20261022/exact-examples.json')
    case = next(c for c in projected['examples']['cases'] if c['id'] == 'calculation-interval')
    assert case['finer'] == interval['finer_interval'] and case['intersection'] == interval['intersection']
    assert int(case['exact_witness']) == interval['authored_exact_total']
    a, o = load(REVIEW / 'assessment-successor.json'), load(REVIEW / 'operation-successor.json')
    assert (len(a['rows']), len(a['interactions']), len(o['rows'])) == (53, 6, 46)
    assert a['readiness'] == o['readiness'] == 'not_ready'
    for name in ('result.md', 'review.md', 'recovery.md'):
        assert (U / name).read_text().strip()
    checks = {'comparison_rows': 12, 'local_anchors': 19, 'reused_source_anchors': 23,
              'reused_inquiries': 3, 'research_ledger_bindings': 18,
              'selected_facts': 12, 'full_facts': 1127, 'full_records': 3788,
              'repeated_signature_groups': 69, 'repeated_group_members': 151,
              'negative_controls': 8, 'conditional_examples': 7,
              'additive_wording_repairs': 1, 'protected_files': len(p['protected']),
              'tracked_dirty_paths': len(rows), 'whole_rows_closed': 0,
              'readiness': 'not_ready', 'manuscript_changed': False, 'runtime_admitted': False}
    return p, checks


def record(p, checks):
    for path in (U / 'completion.json', U / 'checks.json', U / 'run-manifest.json', SUPPLEMENT):
        assert not path.exists() and path.parent.is_dir() and os.access(path.parent, os.W_OK), path
    assert not (U / 'controls-after').exists()
    replacement = '''The native occurrence/consumer audit is complete at
data/accounting-master/r06-native-duplicate-contract-20261023/: twelve boundary
comparisons, nineteen local anchors, twenty-three reused source anchors and
seven conditional examples. Both retained packets preserve every fact's own
occurrence/context links; the full file retains 1,127 facts and all 69 repeated
source-signature groups. Eight scoped corruptions are rejected. An additive
proposed note clarifies that assertion aliases preserve source occurrences
afterward; the older R4 “until” wording did not establish an actual deletion.
Formula stays disabled in the selected importer. No manuscript, schema or
runtime change and no whole-row closure follows. Read-only replay: verify.py
without flags; completed one-time stages are frozen.

Next: inspect distinct remaining method-source leads, beginning with the
zero-weight CGU reversal gap and its completed source attempts. Reuse retained
technical reading; execute a new inquiry only when it addresses the exact
all-zero non-goodwill boundary or another unresolved method counterexample.
Other ready internal work remains eligible; no global continuation veto fired.
Completed acquisitions and the full Version 3.48 diagnosis remain frozen.

'''
    marker = 'Next: audit the proposed native-XBRL occurrence, reduction and assertion'
    edits = []
    for name in p['controls']:
        target = R / name
        assert target.read_bytes() == (U / 'controls-before' / name).read_bytes(), name
        assert not target.is_symlink() and os.access(target, os.W_OK)
        text = target.read_text()
        assert text.count(marker) == 1
        first = text.index(marker)
        last = text.index('Completed review evidence:', first)
        edits.append((name, text[:first] + replacement + text[last:]))
    prefix = 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B '
    receipt = load(U / 'recording-receipt.json')
    write(U / 'checks.json', checks)
    write(U / 'run-manifest.json', {
        'git_commit': p['head'], 'branch': p['branch'], 'environment': sys.executable,
        'python': platform.python_version(), 'cpu_gpu': receipt['cpu_gpu'],
        'data_version': 'Pinned Apple instance, selected/full authored native packets, three frozen source inquiries; comparison-ledger.json',
        'seeds': 'N/A deterministic documentary checks; no stochastic comparison',
        'started_utc': p['started_utc'], 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'wall_time': {'measured_recording_seconds': receipt['wall_seconds'],
                      'total_session': 'Not measured across restarts; UTC brackets are not active execution time'},
        'commands': [prefix + rel(U / 'prepare.py'), prefix + rel(U / 'build_records.py'),
                     prefix + rel(U / 'verify.py'), prefix + rel(U / 'verify.py') + ' --record',
                     prefix + rel(U / 'verify.py')],
        'stage_provenance': 'Preparation recovered, never repeated; two projection debug calls (first failed nil-text assumption) are recorded in recovery.md; one record-generation call; read-only preflight before completion; final replay checked separately',
        'plan': rel(PLAN), 'result': rel(U / 'result.md'), 'output': rel(U), 'proposal_note': rel(NOTE)})
    write(SUPPLEMENT, {
        'scope': 'Native occurrence preservation and consumer-specific reduction boundaries',
        'candidate_version': '3.48', 'candidate_pdf': bind(R / 'docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf'),
        'protected_assessment': bind(REVIEW / 'assessment-successor.json'),
        'protected_operations': bind(REVIEW / 'operation-successor.json'),
        'completed_author_review': bind(REVIEW / 'regression/completion.json'),
        'all_original_obligations': 53, 'interactions': 6, 'operations': 46,
        'whole_rows_closed': 0, 'readiness': 'not_ready', 'plan': bind(PLAN),
        'result': bind(U / 'result.md'), 'review': bind(U / 'review.md'), 'checks': checks,
        'proposed_corrigendum': bind(NOTE), 'manuscript_changed': False,
        'runtime_admitted': False, 'independent_human_acceptance': 'pending'})
    for name, after in edits:
        snapshot = U / 'controls-after' / name
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open('x') as f:
            f.write(after)
        (R / name).write_text(after)
    assert check()[1] == checks
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    files += [PLAN, NOTE, SUPPLEMENT]
    write(U / 'completion.json', {
        'status': 'complete_documentary_audit_additive_wording_repair', 'checks': checks,
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
