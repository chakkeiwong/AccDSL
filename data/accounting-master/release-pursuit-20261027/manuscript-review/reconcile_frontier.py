"""Update only live reading navigation from a continuous checked segment chain."""
from datetime import datetime,timezone
from hashlib import sha256
import json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[3]
read=lambda p:json.loads(p.read_text())
j=read(D/'manuscript-release-prep-v552r2-20261027-inventory.json')
v=next(x for x in j['volumes'] if x['name']=='accounting-product-proposal')
assert sha256((R/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
segments=[s for s in j['read_segments'] if s['volume']==v['name']]
prior=0;exit_state=None
for s in segments:
    assert s['pages']==list(range(prior+1,s['pages'][-1]+1)) and 1<=len(s['pages'])<=6
    if exit_state is not None:assert s['entry_state']==exit_state
    prior=s['pages'][-1];exit_state=s['exit_state']
assert all(p['author_continuous_read']=='author_read' for p in v['pages'][:prior])
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'data/accounting-master/release-pursuit-20261027/state.json',
       'data/accounting-master/release-pursuit-20261027/progress.md']
before={p:(R/p).read_bytes() for p in paths};new={}
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    obj=json.loads(before[p]);a=obj[key]
    assert a['manuscript_review_frontier']['baseline']=='5.52-R2'
    a['manuscript_review_frontier'].update(physical_pages_read=prior,next_page=prior+1)
    new[p]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
obj=json.loads(new[paths[1]]);h=sha256(new[paths[0]].encode()).hexdigest();obj['catalog_sha256']=h
for value in obj.values():
    if isinstance(value,dict) and paths[0] in value:value[paths[0]]=h
new[paths[1]]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
obj=json.loads(before[paths[2]]);obj['ordered_read_pages']=prior
new[paths[2]]=json.dumps(obj,indent=2)+chr(10)
now=datetime.now(timezone.utc).isoformat()
new[paths[3]]=before[paths[3]].decode()+chr(10)+f'{now}: ordered author reading of protected 5.52-R2 reaches physical page {prior}; resume at {prior+1}. Segment continuity and PDF identity checked; no independent or whole-document acceptance inferred. Selected candidate and active work unit preserved.'+chr(10)
backup=D/f'frontier-{prior:04}-before';backup.mkdir(exist_ok=False)
for p,b in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
assert all((R/p).read_bytes()==b for p,b in before.items())
for p,s in new.items():(R/p).write_text(s)
report=dict(timestamp_utc=now,frontier=prior,next_page=prior+1,pdf_sha256=v['pdf_sha256'],
    controls={p:dict(before=sha256(before[p]).hexdigest(),after=sha256((R/p).read_bytes()).hexdigest()) for p in paths})
with (D/f'frontier-{prior:04}.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,frontier=prior,controls=len(paths))))
