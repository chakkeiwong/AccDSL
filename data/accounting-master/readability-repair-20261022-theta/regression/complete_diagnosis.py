"""Bind the complete 3.48 author diagnosis once; default replay is read-only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
EXPECTED = '6a2acd8e3e01e6127eb89112a168216ee12b3244b3e56c814f1d2d1c56b90f0e'
STATUS = 'author_diagnosis_complete_no_new_defects_acceptance_pending'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))


def exclusive(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def protection_check():
    p = load(U / 'protection.json')
    for name, digest in p['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == p['head']
    assert sha(R / '.git/index') == p['index_sha256']
    rows = [x for x in subprocess.check_output(
        ['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'],
        cwd=R, text=True).split('\0') if x]
    assert {x[3:] for x in rows} == set(p['tracked_dirty'])
    assert all(x[:2] == ' M' for x in rows)
    for name, digest in p['tracked_dirty'].items():
        if name not in p['controls']:
            assert sha(R / name) == digest, name
    return p


def validate_syntheses(d, s):
    assert d['pdf_sha256'] == s['pdf_sha256'] == EXPECTED
    assert d['page_count'] == 401 and len(d['nodes']) == 676
    assert len(d['sources']) == 144 and not d['defects']
    assert all(n['reading_status'] == 'author_read' for n in d['nodes'])
    assert all(p['reading_status'] == 'author_read' for p in d['pages'])
    assert [x['chapter'] for x in s['chapter_regressions']] == list(range(1, 18))
    assert [x['through_chapter'] for x in s['cumulative_prefixes']] == list(range(2, 17, 2))
    previous = 0
    for row in s['chapter_regressions']:
        first, last = row['physical_pages']
        assert first == previous + 1 and first <= last
        previous = last
    assert previous == 401
    for row in s['chapter_regressions'] + s['cumulative_prefixes']:
        assert sha(R / row['synthesis']['path']) == row['synthesis']['sha256']
        assert row['status'] == 'author_synthesis_complete_independent_acceptance_pending'
    for row in s['cumulative_prefixes']:
        assert row['physical_pages'] == [1, s['chapter_regressions'][row['through_chapter'] - 1]['physical_pages'][1]]
    assert s['independent_reader'] == s['human_acceptance'] == 'pending'
    assert (U / 'document-synthesis.md').stat().st_size > 1000


def complete():
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    names = ('completion.json', 'completion-run-manifest.json',
             'structure-ledger-before-complete.json', 'synthesis-ledger-before-complete.json',
             'controls-before-diagnosis-complete')
    assert all(not (U / name).exists() for name in names), 'Never repeat completed mutations'
    d, s = load(U / 'structure-ledger.json'), load(U / 'synthesis-ledger.json')
    assert d['diagnosis_status'] == s['status'] == 'in_progress'
    assert s['document_synthesis'] is None
    validate_syntheses(d, s)
    p = protection_check()
    replacement = f'''Full Version 3.48 author diagnosis is complete: all 401 physical pages,
676 nodes and 144 source files are bound in {len(d['ordered_segments'])} ordered reading segments,
17 chapter/appendix syntheses, eight cumulative prefixes and a document synthesis.
No confirmed new manuscript defect was found. The theta prerequisite repair
passes the complete author regression; no further manuscript revision is
justified by this diagnosis. No global continuation veto has fired.
Independent reader, implementability, domain and human acceptance remain pending.

Next: continue the ready internal R03–R06 source/method preparation after a
fresh dependency audit of the live queue. Choose a new discriminating inquiry,
preserve completed source failures and finite checks, and retain the exact
unresolved financial method boundaries. This instruction supersedes older
dated next-step paragraphs below; the completed manuscript review is not a
reason to restart reading or request acceptance before internal work continues.

Completed review evidence:
data/accounting-master/readability-repair-20261022-theta/regression/.
Safe replay: complete_diagnosis.py without arguments. Never rerun completed
initialization, rendering, segment/synthesis recording, frontier refresh or
completion. Frozen candidate and predecessor evidence are preserved. All
53 obligations, six interactions and 46 operations remain, zero whole rows
close, and not_ready persists. This author diagnosis grants no source authority,
runtime, empirical, independent-reader or human acceptance.

'''
    stale = 'Full successor chapter/cumulative/document regression remains pending.'
    reconciled = ('Full successor chapter/cumulative/document author regression is recorded\n'
                  'below; independent acceptance remains pending.')
    edits = []
    for name in p['controls']:
        before = (R / name).read_text()
        assert before.count(stale) == 1, name
        start = before.index('Full Version 3.48 ordered regression is in progress.')
        end = before.index('General hedge\nattribution,', start)
        after = (before[:start] + replacement + before[end:]).replace(stale, reconciled)
        assert 'resume physical page 402' not in after
        edits.append((name, before, after))
    original = (U / 'structure-ledger.json').read_bytes()
    with (U / 'structure-ledger-before-complete.json').open('xb') as stream:
        stream.write(original)
    d['diagnosis_status'] = 'author_diagnosis_complete'
    (U / 'structure-ledger.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
    try:
        subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
    except BaseException:
        (U / 'structure-ledger.json').write_bytes(original)
        raise
    with (U / 'synthesis-ledger-before-complete.json').open('xb') as stream:
        stream.write((U / 'synthesis-ledger.json').read_bytes())
    s.update(status=STATUS, document_synthesis={
        'path': rel(U / 'document-synthesis.md'), 'sha256': sha(U / 'document-synthesis.md')})
    (U / 'synthesis-ledger.json').write_text(json.dumps(s, indent=2) + '\n')
    snapshot = U / 'controls-before-diagnosis-complete'
    snapshot.mkdir(exist_ok=False)
    for name, before, after in edits:
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(before)
        (R / name).write_text(after)
    protection_check()
    exclusive('completion-run-manifest.json', {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': p['head'], 'branch': p['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden',
        'data_version': 'Exact frozen Version 3.48 source/PDF; no financial data changed',
        'seeds': 'N/A deterministic document review and integrity checks',
        'wall_time': 'Reading spans multiple sessions; not measured as a continuous run',
        'commands': ['initialize.py render FIRST LAST (at most six new pages)',
                     'view_image (at most three images per call)', 'author_segment.py DRAFT',
                     'record_synthesis.py KIND NUMBER FIRST LAST FILE',
                     'refresh_frontier.py at previously saved frontiers',
                     'initialize.py render --pages 386 391 (rejected by argument parser; no render)',
                     'initialize.py render 386 391 (correct positional syntax)',
                     'complete_diagnosis.py complete (includes strict initialize.py validate)',
                     'complete_diagnosis.py (read-only replay)'],
        'python_prefix': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B',
        'initial_manifest': {'path': rel(U / 'run-manifest.json'), 'sha256': sha(U / 'run-manifest.json')},
        'plan': 'docs/plans/accounting-readability-regression-20261022-theta.md',
        'result': rel(U / 'document-synthesis.md'), 'output': rel(U)})
    files = [path for path in U.rglob('*') if path.is_file() and '__pycache__' not in path.parts]
    exclusive('completion.json', {
        'status': STATUS, 'candidate_pdf': s['candidate_pdf'], 'pdf_sha256': EXPECTED,
        'pages': 401, 'nodes': 676, 'sources': 144, 'segments': len(d['ordered_segments']),
        'chapter_syntheses': 17, 'prefix_syntheses': 8, 'defects': [],
        'protected_files_preserved': len(p['protected']), 'tracked_dirty_paths_preserved': len(p['tracked_dirty']),
        'head_and_index_preserved': True, 'independent_reader': 'pending', 'human_acceptance': 'pending',
        'obligations': 53, 'interactions': 6, 'operations': 46, 'whole_rows_closed': 0,
        'readiness': 'not_ready', 'bindings': {rel(path): sha(path) for path in sorted(files)},
        'live_controls_at_completion': {name: sha(R / name) for name in p['controls']}})


def verify():
    c = load(U / 'completion.json')
    assert c['status'] == STATUS and c['pdf_sha256'] == EXPECTED
    assert sha(R / c['candidate_pdf']) == EXPECTED
    for name, digest in c['bindings'].items():
        assert sha(R / name) == digest, name
    d, s = load(U / 'structure-ledger.json'), load(U / 'synthesis-ledger.json')
    validate_syntheses(d, s)
    assert d['diagnosis_status'] == 'author_diagnosis_complete' and s['status'] == STATUS
    assert sha(R / s['document_synthesis']['path']) == s['document_synthesis']['sha256']
    subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
    print(json.dumps({k: v for k, v in c.items() if k not in ('bindings', 'live_controls_at_completion')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=['complete', 'verify'], default='verify')
    if parser.parse_args().action == 'complete':
        complete()
    verify()
