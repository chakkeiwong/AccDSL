"""Refresh live controls only after saved reading evidence validates."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
subprocess.run([sys.executable, '-B', str(U / 'initialize.py'), 'validate'], check=True)
ledger = load(U / 'structure-ledger.json')
last = load(R / ledger['ordered_segments'][-1])['physical_pages'][1]
synthesis = load(U / 'synthesis-ledger.json')
for row in synthesis['chapter_regressions'] + synthesis['cumulative_prefixes']:
    binding = row['synthesis']
    assert sha(R / binding['path']) == binding['sha256']
    assert row['physical_pages'][1] <= last
segments = len(ledger['ordered_segments'])
chapters = len(synthesis['chapter_regressions'])
prefixes = len(synthesis['cumulative_prefixes'])
paragraph = f'''Next: resume exact Version3.46 argument review at physical page {last+1}.
Pages1–{last} are recorded in {segments} contiguous, hash-bound reading segments;
{chapters} chapter and {prefixes} cumulative-prefix syntheses are bound.
The new inventory binds144 sources,676 nodes and401 pages. No prior reading
credit transfers. Plan: docs/plans/accounting-346-argument-review-20261021.md.
Use at most six pages per segment and three images per call. Save each
completed segment before continuing; never rerun initialisation.
The reserve-originals inquiry is complete only at its bounded access layer:
19 receipts and58 bindings, no new technical paper, original/final comparisons
still open. City labels its deposit Accepted Version; corrected publisher APIs
require authentication; public publisher/SSRN/ETH routes returned403/403/429.
Do not repeat those failed routes without a new legitimate lead. Evidence:
data/accounting-master/r04-reserve-originals-20261021/; safe replay verify.py.
Recovery and transport evidence: session-recovery-20261021/recovery.md.
'''
names = ['docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md', 'data/accounting-master/next-plan.md']
edits = []
for name in names:
    p = R / name
    before = p.read_text()
    start = before.index('Next:')
    end = before.index('The source inquiries and open', start)
    after = before[:start] + paragraph + before[end:]
    if before != after:
        edits.append((p, before, after))
if edits:
    snapshot = U / f'controls-before-frontier-{last:03}'
    snapshot.mkdir(exist_ok=False)
    for p, before, after in edits:
        (snapshot / p.name).write_text(before)
        p.write_text(after)
    result = {'through': last, 'next': last+1,
        'controls': [{'path': name, 'sha256': sha(R / name)} for name in names]}
    (snapshot / 'result.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'controls_changed': len(edits), 'through': last, 'next': last+1}))
