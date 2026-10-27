"""Save a validated frontier in the four live controls; never rerun a frontier."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
subprocess.run([sys.executable,'-B',str(U/'initialize.py'),'validate'],check=True)
p, d, s = [load(U/name) for name in ('protection.json','structure-ledger.json','synthesis-ledger.json')]
for name, digest in p['protected'].items():
    assert sha(R/name) == digest, name
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == p['head']
assert sha(R/'.git/index') == p['index_sha256']
rows = [x for x in subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True).split('\0') if x]
assert {x[3:] for x in rows} == set(p['tracked_dirty']) and all(x[:2]==' M' for x in rows)
for name, digest in p['tracked_dirty'].items():
    if name not in p['controls']:
        assert sha(R/name) == digest, name
last = load(R/d['ordered_segments'][-1])['physical_pages'][1]
for row in s['chapter_regressions'] + s['cumulative_prefixes']:
    assert sha(R/row['synthesis']['path']) == row['synthesis']['sha256']
    assert row['physical_pages'][1] <= last
paragraph = f'''Full Version 3.48 ordered regression is in progress. Physical pages 1–{last}
are actually read in {len(d['ordered_segments'])} contiguous segments; {sum(n['reading_status']=='author_read' for n in d['nodes'])} of 676 nodes
have specific judgments. There are {len(s['chapter_regressions'])} chapter/appendix and {len(s['cumulative_prefixes'])} cumulative-prefix
syntheses; {len(d.get('defects',[]))} confirmed new defects. No earlier reading credit transfers.
Independent reader, implementability, domain and human acceptance remain pending.

Next: resume physical page {last+1} under
docs/plans/accounting-readability-regression-20261022-theta.md. Evidence is at
data/accounting-master/readability-repair-20261022-theta/regression/.
Read at most six pages per segment and view at most three images per call.
Save authored judgments before advancing; never rerun completed initialization,
rendering, segment recording or frontier refresh. Complete diagnosis before
any successor manuscript edit. All 53/6/46 obligations/interactions/operations
remain, zero whole rows close, and no global continuation veto has fired.

'''
first_marker = 'Next: perform a fresh ordered Version 3.48 chapter/cumulative/document'
edits = []
for name in p['controls']:
    path = R/name
    before = path.read_text()
    marker = 'Full Version 3.48 ordered regression is in progress.'
    start = before.index(marker if marker in before else first_marker)
    end = before.index('General hedge\nattribution,',start)
    edits.append((name,before,before[:start]+paragraph+before[end:]))
out = U/f'controls-before-frontier-{last:03}'
out.mkdir(exist_ok=False)
for name,before,after in edits:
    target = out/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(before)
    (R/name).write_text(after)
with (out/'result.json').open('x') as f:
    json.dump(dict(through=last,next_page=last+1,controls=[dict(path=name,sha256=sha(R/name)) for name in p['controls']]),f,indent=2)
    f.write('\n')
print(json.dumps(dict(through=last,next_page=last+1,protected_files=len(p['protected']),controls_changed=4)))
