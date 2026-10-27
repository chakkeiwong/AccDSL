"""Refresh only declared live controls from a validated saved reading frontier."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U=Path(__file__).resolve().parent
R=U.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
subprocess.run([sys.executable,'-B',str(U/'initialize.py'),'validate'],check=True)
d=load(U/'structure-ledger.json')
s=load(U/'synthesis-ledger.json')
last=load(R/d['ordered_segments'][-1])['physical_pages'][1]
for row in s['chapter_regressions']+s['cumulative_prefixes']:
    assert sha(R/row['synthesis']['path'])==row['synthesis']['sha256']
    assert row['physical_pages'][1]<=last
paragraph=f'''Full Version 3.47 ordered regression is in progress. Physical pages 1–{last}
are actually read and recorded in {len(d['ordered_segments'])} contiguous segments;
{sum(n['reading_status']=='author_read' for n in d['nodes'])} of 676 nodes have specific judgments. There are
{len(s['chapter_regressions'])} chapter/appendix and {len(s['cumulative_prefixes'])} cumulative-prefix syntheses. Confirmed new
defects: {len(d.get('defects',[]))}. No earlier reading credit transfers. Independent reader,
implementability, domain and human acceptance remain pending. No global
continuation veto has fired.

Next: resume physical page {last+1} under
docs/plans/accounting-readability-regression-20261022.md. Evidence is under
data/accounting-master/readability-repair-20261022/regression/. Read at most
six pages per segment and view at most three images per call; save authored
judgments before advancing. Never rerun initialization. Preserve the current
candidate until diagnosis is complete, then repair confirmed defects and
continue ready internal source/method work.

'''
names=load(U.parent/'protection.json')['controls']
edits=[]
for name in names:
    path=R/name
    before=path.read_text()
    start=before.index('Full Version 3.47 ordered regression ')
    end=before.index('The reserve-originals inquiry remains bounded access evidence:',start)
    after=before[:start]+paragraph+before[end:]
    if before!=after:edits.append((path,before,after))
if edits:
    out=U/f'controls-before-frontier-{last:03}'
    out.mkdir(exist_ok=False)
    for path,before,after in edits:
        (out/path.name).write_text(before)
        path.write_text(after)
    result={'through':last,'next':last+1,'controls':[{'path':name,'sha256':sha(R/name)} for name in names]}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'controls_changed':len(edits),'through':last,'next':last+1}))
