"""Bind an explicitly authored chapter or cumulative-prefix synthesis."""
import argparse
import hashlib
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument('kind',choices=['chapter','prefix'])
p.add_argument('number',type=int)
p.add_argument('first',type=int)
p.add_argument('last',type=int)
p.add_argument('file')
a=p.parse_args()
ledger=json.loads((U/'structure-ledger.json').read_text())
s=json.loads((U/'synthesis-ledger.json').read_text())
last=json.loads((R/ledger['ordered_segments'][-1]).read_text())['physical_pages'][1]
assert 1<=a.first<=a.last<=last
path=(U/a.file).resolve()
assert path.is_relative_to(U) and path.stat().st_size>100
for row in s['chapter_regressions']+s['cumulative_prefixes']:
    assert sha(R/row['synthesis']['path'])==row['synthesis']['sha256']
if a.kind=='chapter':
    rows=s['chapter_regressions']
    assert a.number==len(rows)+1
    if rows:assert a.first==rows[-1]['physical_pages'][1]+1
    row={'chapter':a.number}
else:
    rows=s['cumulative_prefixes']
    assert a.number==2*(len(rows)+1) and a.number<=len(s['chapter_regressions'])
    assert a.first==1 and a.last==s['chapter_regressions'][a.number-1]['physical_pages'][1]
    row={'through_chapter':a.number}
row.update(physical_pages=[a.first,a.last],synthesis={'path':str(path.relative_to(R)),'sha256':sha(path)},
    status='author_synthesis_complete_independent_acceptance_pending')
rows.append(row)
(U/'synthesis-ledger.json').write_text(json.dumps(s,indent=2)+'\n')
print(json.dumps({'bound':a.kind,'number':a.number,'pages':[a.first,a.last]}))
