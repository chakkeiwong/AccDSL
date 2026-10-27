"""Update only the live review paragraph from validated reading segments."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
subprocess.run([sys.executable, '-B', str(OUT / 'initialize.py'), 'validate'], check=True)
ledger = json.loads((OUT / 'structure-ledger.json').read_text())
last = json.loads((ROOT / ledger['ordered_segments'][-1]).read_text())['physical_pages'][1]
count = len(ledger['ordered_segments'])
synthesis = json.loads((OUT / 'synthesis-ledger.json').read_text())
chapter_count = len(synthesis['chapter_regressions'])
prefix_count = len(synthesis['cumulative_prefixes'])
controls = [ROOT / p for p in ('docs/plans/accounting-master-current.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md', 'data/accounting-master/next-plan.md')]
replacement = (f'Next: resume the whole-document chain at physical page {last + 1}. Pages 1–{last}\n'
    f'are recorded in {count} contiguous, hash-bound author-reading segments.\n'
    f'{chapter_count} chapter syntheses and {prefix_count} cumulative prefix synthesis are bound.\n'
    'The exact 3.45 inventory contains\n'
    '676 nodes and 401 pages; independent and human acceptance remain pending. ')
edits = []
for path in controls:
    content = path.read_text()
    start = content.index('Next: resume the whole-document chain at physical page ')
    end = content.index('Record segments of at most six pages', start)
    updated = content[:start] + replacement + content[end:]
    if updated != content:
        edits.append((path, updated))
if edits:
    snapshot = OUT / f'controls-before-frontier-{last:03}'
    snapshot.mkdir(exist_ok=False)
    for path, updated in edits:
        shutil.copy2(path, snapshot / path.name)
        path.write_text(updated)
    record = {'continuous_pages': [1,last], 'next_page':last+1, 'segments':count,
        'controls':[{'path':str(p.relative_to(ROOT)),
          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in controls]}
    (snapshot / 'result.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps({'controls_changed':len(edits),'continuous_pages':last,'next_page':last+1}))
