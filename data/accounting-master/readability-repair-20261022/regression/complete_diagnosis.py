"""Freeze the additive 3.47 diagnosis once; default replay is read-only."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
EXPECTED = 'b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))


def exclusive(name, value):
    with (U / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def validate_syntheses(d, s):
    assert d['pdf_sha256'] == s['pdf_sha256'] == EXPECTED
    assert d['page_count'] == 401 and len(d['nodes']) == 676
    assert all(n['reading_status'] == 'author_read' for n in d['nodes'])
    assert all(p['reading_status'] == 'author_read' for p in d['pages'])
    assert [x['id'] for x in d['defects']] == ['R347-D01']
    assert [x['chapter'] for x in s['chapter_regressions']] == list(range(1, 18))
    assert [x['through_chapter'] for x in s['cumulative_prefixes']] == list(range(2, 17, 2))
    for row in s['chapter_regressions'] + s['cumulative_prefixes']:
        assert sha(R / row['synthesis']['path']) == row['synthesis']['sha256']
    for row in s['cumulative_prefixes']:
        assert row['physical_pages'] == [1, s['chapter_regressions'][row['through_chapter'] - 1]['physical_pages'][1]]
    assert (U / 'document-synthesis.md').stat().st_size > 1000


def complete():
    assert not (U / 'completion.json').exists(), 'Completed diagnosis is immutable'
    for name in ('structure-ledger-before-complete.json', 'synthesis-ledger-before-complete.json',
                 'controls-before-diagnosis-complete', 'completion-run-manifest.json'):
        assert not (U / name).exists(), name
    d, s = load(U / 'structure-ledger.json'), load(U / 'synthesis-ledger.json')
    assert d['diagnosis_status'] == s['status'] == 'in_progress'
    validate_syntheses(d, s)
    controls = [R / name for name in load(U.parent / 'protection.json')['controls']]
    edits = []
    replacement = f'''Full Version 3.47 author diagnosis is complete: 401 physical pages and
676 nodes in {len(d['ordered_segments'])} ordered segments, 17 chapter/appendix syntheses,
eight cumulative prefixes and a whole-document assessment. The sole confirmed
new defect is R347-D01: theta lacks its prerequisite definition at physical
page 88. No global continuation veto has fired. Independent reader,
implementability, domain and human acceptance remain pending.

Next: make the bounded theta-definition repair in a protected Version 3.48
successor after recording its audited plan. Preserve the complete diagnosis at
data/accounting-master/readability-repair-20261022/regression/ and the frozen
Version 3.47 source/PDF. Completion replay: regression/complete_diagnosis.py
without arguments. Never rerun completed initialization, recording, rendering,
frontier refresh or completion stages. Continue ready internal source/method
work after repair verification; this author diagnosis grants no new acceptance.

'''
    for path in controls:
        before = path.read_text()
        start = before.index('Full Version 3.47 ordered regression ')
        end = before.index('The reserve-originals inquiry remains bounded access evidence:', start)
        edits.append((path, before, before[:start] + replacement + before[end:]))
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
    s.update(status='author_diagnosis_complete_repairs_required',
             document_synthesis={'path': rel(U / 'document-synthesis.md'),
                                 'sha256': sha(U / 'document-synthesis.md')})
    (U / 'synthesis-ledger.json').write_text(json.dumps(s, indent=2) + '\n')
    snapshot = U / 'controls-before-diagnosis-complete'
    snapshot.mkdir(exist_ok=False)
    for path, before, after in edits:
        (snapshot / path.name).write_text(before)
        path.write_text(after)
    finish()


def finish():
    """Finish after the recorded manifest-name collision; never repeat completed mutations."""
    assert not (U / 'completion.json').exists()
    d, s = load(U / 'structure-ledger.json'), load(U / 'synthesis-ledger.json')
    validate_syntheses(d, s)
    assert d['diagnosis_status'] == 'author_diagnosis_complete'
    assert s['status'] == 'author_diagnosis_complete_repairs_required'
    assert sha(R / s['document_synthesis']['path']) == s['document_synthesis']['sha256']
    assert load(U / 'structure-ledger-before-complete.json')['diagnosis_status'] == 'in_progress'
    assert load(U / 'synthesis-ledger-before-complete.json')['status'] == 'in_progress'
    controls = [R / name for name in load(U.parent / 'protection.json')['controls']]
    for path in controls:
        assert 'Full Version 3.47 author diagnosis is complete:' in path.read_text()
        assert (U / 'controls-before-diagnosis-complete' / path.name).exists()
    subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
    protection = load(U.parent / 'protection.json')
    exclusive('completion-run-manifest.json', {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': protection['head'], 'branch': protection['branch'],
        'environment': sys.executable, 'python': platform.python_version(),
        'cpu_gpu': 'CPU only; GPU devices intentionally hidden',
        'data_version': 'Exact frozen Version3.47 source/PDF; no financial data changed',
        'seeds': 'N/A deterministic document reading and integrity checks',
        'wall_time': 'Not measured as one continuous run; author reading spans multiple sessions',
        'commands': ['initialize.py render FIRST LAST (at most six pages)',
                     'view_image (at most three images per call)',
                     'author_segment.py DRAFT', 'record_synthesis.py KIND NUMBER FIRST LAST FILE',
                     'initialize.py validate', 'refresh_frontier.py at saved frontiers',
                     '../verify.py (read-only)', 'complete_diagnosis.py complete (manifest collision retained)',
                     'complete_diagnosis.py finish',
                     'complete_diagnosis.py (read-only)'],
        'initial_manifest': {'path': rel(U / 'run-manifest.json'), 'sha256': sha(U / 'run-manifest.json')},
        'python_prefix': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B',
        'plan': 'docs/plans/accounting-readability-regression-20261022.md',
        'result': rel(U / 'document-synthesis.md'), 'output': rel(U)})
    files = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    result = {
        'status': 'author_diagnosis_complete_repairs_required',
        'candidate_pdf': s['candidate_pdf'], 'pdf_sha256': EXPECTED,
        'pages': 401, 'nodes': 676, 'segments': len(d['ordered_segments']),
        'chapter_syntheses': 17, 'prefix_syntheses': 8,
        'defects': [x['id'] for x in d['defects']],
        'independent_reader': 'pending', 'human_acceptance': 'pending',
        'whole_rows_closed': 0, 'readiness': 'not_ready',
        'bindings': {rel(p): sha(p) for p in sorted(files)},
        'live_controls_at_completion': {rel(p): sha(p) for p in controls}}
    exclusive('completion.json', result)


def verify():
    c = load(U / 'completion.json')
    assert c['pdf_sha256'] == EXPECTED and sha(R / c['candidate_pdf']) == EXPECTED
    for name, digest in c['bindings'].items():
        assert sha(R / name) == digest, name
    d, s = load(U / 'structure-ledger.json'), load(U / 'synthesis-ledger.json')
    validate_syntheses(d, s)
    assert d['diagnosis_status'] == 'author_diagnosis_complete'
    assert sha(R / s['document_synthesis']['path']) == s['document_synthesis']['sha256']
    subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
    print(json.dumps({k: v for k, v in c.items() if k not in ('bindings', 'live_controls_at_completion')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=['complete', 'finish', 'verify'], default='verify')
    action = parser.parse_args().action
    if action == 'complete':
        complete()
    elif action == 'finish':
        finish()
    verify()
