"""Freeze the completed current-candidate diagnosis once."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not (U / 'completion.json').exists()
d = load(U / 'structure-ledger.json')
s = load(U / 'synthesis-ledger.json')
assert d['diagnosis_status'] == 'in_progress'
assert len(d['ordered_segments']) == 67
assert all(n['reading_status'] == 'author_read' for n in d['nodes'])
assert all(p['reading_status'] == 'author_read' for p in d['pages'])
assert len(d['defects']) == 7
assert [x['chapter'] for x in s['chapter_regressions']] == list(range(1, 18))
assert [x['through_chapter'] for x in s['cumulative_prefixes']] == list(range(2, 17, 2))
for row in s['chapter_regressions'] + s['cumulative_prefixes']:
    assert sha(R / row['synthesis']['path']) == row['synthesis']['sha256']
for row in s['cumulative_prefixes']:
    assert row['physical_pages'] == [1, s['chapter_regressions'][row['through_chapter'] - 1]['physical_pages'][1]]
original = (U / 'structure-ledger.json').read_bytes()
with (U / 'structure-ledger-before-complete.json').open('xb') as f:
    f.write(original)
d['diagnosis_status'] = 'author_diagnosis_complete'
(U / 'structure-ledger.json').write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
try:
    subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
except BaseException:
    (U / 'structure-ledger.json').write_bytes(original)
    raise
with (U / 'synthesis-ledger-before-complete.json').open('xb') as f:
    f.write((U / 'synthesis-ledger.json').read_bytes())
s.update(status='author_diagnosis_complete_repairs_required',
         document_synthesis={'path': str((U / 'document-synthesis.md').relative_to(R)),
                             'sha256': sha(U / 'document-synthesis.md')})
(U / 'synthesis-ledger.json').write_text(json.dumps(s, indent=2) + '\n')
controls = [R / name for name in (
    'docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md',
    'data/accounting-master/next-plan.md')]
snapshot = U / 'controls-before-diagnosis-complete'
snapshot.mkdir(exist_ok=False)
replacement = '''The exact Version3.46 author diagnosis is complete:401 physical pages and
676 nodes in67 ordered segments,17 chapter/appendix syntheses and eight
cumulative prefixes. Seven confirmed defects require bounded repair:
RR346-001–003 project/retrieval history,RR346-004 compilation target,
RR346-005–006 source-file/copy history,and RR346-007 a false backward pointer.
Independent reader,implementability,domain and human acceptance remain pending.

Next: execute the audited protected Version3.47 repair under
docs/plans/accounting-readability-repair-20261022.md. Preserve the completed
diagnosis at readability-repair-20261021/regression/ and all source/math limits.
Then continue exact-candidate review; no prior reading credit transfers.
The reserve-originals inquiry remains bounded access evidence:19 receipts,
58 bindings,no new technical paper,and original/final comparisons still open.
Do not repeat rejected publisher/SSRN/ETH routes without a new legitimate lead.
Recovery evidence:session-recovery-20261021/recovery.md.
'''
for p in controls:
    before = p.read_text()
    start = before.index('Next: resume exact Version3.46 argument review at physical page ')
    end = before.index('The source inquiries and open', start)
    after = before[:start] + replacement + before[end:]
    after = after.replace('full exact-candidate review remains pending. No earlier\nreading credit transfers.',
                          'full exact-candidate author diagnosis is now complete below.\nIndependent acceptance remains pending.')
    (snapshot / p.name).write_text(before)
    p.write_text(after)
files = [p for p in U.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
result = {
    'status': 'author_diagnosis_complete_repairs_required',
    'candidate_pdf': s['candidate_pdf'], 'pdf_sha256': s['pdf_sha256'],
    'pages': 401, 'nodes': 676, 'segments': 67,
    'chapter_syntheses': 17, 'prefix_syntheses': 8,
    'defects': [x['id'] for x in d['defects']],
    'independent_reader': 'pending', 'human_acceptance': 'pending',
    'whole_rows_closed': 0, 'readiness': 'not_ready',
    'bindings': {str(p.relative_to(R)): sha(p) for p in sorted(files)},
    'live_controls_at_completion': {str(p.relative_to(R)): sha(p) for p in controls}}
with (U / 'completion.json').open('x') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps({k: v for k, v in result.items() if k not in ('bindings', 'live_controls_at_completion')}))
