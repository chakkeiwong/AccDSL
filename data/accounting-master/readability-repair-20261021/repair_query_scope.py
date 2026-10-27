"""Preserve first build and resolve an ambiguous research-scope referent."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
from check_candidate import check

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/'docs/design/proposal/manuscript-reserve-risk-20261020'
C=R/'docs/design/proposal/manuscript-readability-20261021'
A=U/'attempt-01'
assert not A.exists()
checks=check()
A.mkdir()
shutil.copytree(C,A/'candidate')
for name in ('source-lock.json','source-delta.patch','source-checks.json','build-manifest.json','build-stdout.log'):
    shutil.copy2(U/name,A/name)
(A/'candidate-checks.json').write_text(json.dumps(checks,indent=2)+chr(10))
(A/'review.md').write_text('''# First-build local review

Physical pages385–387 were actually viewed in order. The initial-library count is now scoped correctly and the layout is legible. A new local ambiguity remains: inserting the later-search sentence before “This includes previously omitted discovery files” changes that pronoun's apparent referent. Those files belong to the initial population. Move the later-search statement after the initial-population and generation-script explanation, and name that initial scope explicitly. This is a wording repair, not new research or a change to the count. No other page-reading credit is claimed for this attempt.
''')
lock=json.loads((U/'source-lock.json').read_text())
change=next(x for x in lock['replacements'] if x['id']=='RR-003-query')
old_block='''Every one of the 179 unique candidates in the acquired forward-query files
has an individual title/metadata relevance decision. This includes
previously omitted discovery files associated with inaccessible seed papers.
The generation script requires an explicit decision and stops on an unseen
candidate.'''
new_block='''Each of the 179 unique candidates in the initial acquired forward-query
files has an individual title/metadata relevance decision. This initial
population includes previously omitted discovery files associated with
inaccessible seed papers. The initial generation script requires an explicit
decision and stops on an unseen candidate. Later searches retain their own
bounded populations and relevance decisions.'''
source=B/change['path'];dest=C/change['path']
assert source.read_text().count(old_block)==1
current=dest.read_text()
first_block=old_block.replace(change['old'],change['new'],1)
assert current.count(first_block)==1
dest.write_text(current.replace(first_block,new_block,1))
change.update(old=old_block,new=new_block)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in lock['files']:
    row['candidate_sha256']=sha(C/row['path'])
(U/'source-lock.json').write_text(json.dumps(lock,indent=2,ensure_ascii=False)+chr(10))
diff=[]
for row in lock['files']:
    if row['changed']:
        name=row['path']
        diff.extend(difflib.unified_diff((B/name).read_text().splitlines(True),(C/name).read_text().splitlines(True),fromfile='3.45/'+name,tofile='3.46/'+name))
(U/'source-delta.patch').write_text(''.join(diff))
print(json.dumps({'attempt1_preserved':True,'repair':'initial-query population referent clarified','source_check':check(source_only=True)}))
