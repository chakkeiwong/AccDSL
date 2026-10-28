"""Verify continuous reading and advance current frontier to312 once."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
start=time.monotonic();I=D/'manuscript-release-prep-v552r2-20261027-inventory.json';j=json.loads(I.read_text());v=next(x for x in j['volumes'] if x['name']=='accounting-product-proposal')
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
for row in j['source_files']:assert sha256((ROOT/j['candidate']/row['path']).read_bytes()).hexdigest()==row['sha256']
cursor=1;prior=None
for s in [r for r in j['read_segments'] if r['volume']==v['name']]:
 assert s['pages']==list(range(cursor,cursor+len(s['pages']))) and len(s['pages'])<=6
 if prior:assert s['entry_state']==prior['exit_state']
 assert s['pdf_sha256']==v['pdf_sha256'];cursor=s['pages'][-1]+1;prior=s
assert cursor==313
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,313))
doc=fitz.open(ROOT/v['pdf'])
for p in v['pages']:assert sha256(doc[p['physical_page']-1].get_text().encode()).hexdigest()==p['text_sha256']
checks=0
for a,b in [(301,306),(307,312)]:
 record=json.loads((D/f'arithmetic-{a:04}-{b:04}.json').read_text());assert all(c['passed'] for c in record['checks']);checks+=record['count']
 for p in json.loads((D/f'render-bindings-{a:04}-{b:04}.json').read_text())['pages']:
  assert sha256((D/'rendered-main'/f'{p["page"]:04}.png').read_bytes()).hexdigest()==p['sha256']
assert checks==33
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0312';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=312;d[key]['manuscript_review_frontier']['next_page']=313
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=312,next_page=313,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=312;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d);t=next(x for x in d['tasks'] if x['id']=='R04');t['next_action']='Actual ordered main reading reaches312/831 on protected5.52-R2; resume313. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through312 — 28 October2026

Twelve further pages301–312 are individually read in order, with33 exact local
checks. Product/region margins, legal entities, litigation, later disclosure,
indemnities, insurance and operating restrictions retain their separate source,
date and population meanings.279 source hashes,831 page texts, complete segment
continuity and12 new renders verify. Resume313;519 main pages remain.
Result: company-state-ordered-review-20261028/result.md under data/accounting-master.

Twenty-two original failure rows are individually reviewed;179 remain outside
this pass. All original task criteria/releases persist. R04 stays in_progress;
independent/human review and other layers remain open. E3 deferred. Continue.

'''
for n in paths[4:]:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=H/'result.md';old=p.read_text();(H/'result-before-0312.md').write_text(old)
new='''# Ordered reading reaches physical page312

## Continuation through312 — 28 October2026

Twelve individual rendered pages301–312 are read in two ordered six-page
segments.27 and6 exact local checks pass; the continuation265–312 now records
48 pages and360 arithmetic checks. Counts support navigation, not acceptance.

Country/segment/product margins do not locate legal sellers or identify the
joint exposure table. The two product-region witnesses preserve all margins.
Ownership, incorporation, functional currency and tax residence require separate
facts. Legal proceedings, contractual indemnities, defense, settlements and
insurance are distinct channels. Later comparative expense disclosures add
historical information without proving past availability or new transactions.
Regulation can restrict the feasible operating plan; disclosed risks do not
supply the joint demand/supply law. No substantive manuscript defect is
confirmed in this slice. Source authority/current law was not newly inspected.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain author reading301–312 | Individual readable images and exact segment continuity |279 source/831 text hashes and12 renders verify |519 unread main pages plus separate review layers | Continue313 | Independent or human acceptance |
| Retain local math |33 exact checks and explicit assumptions | No local arithmetic veto | Source scope and connected whole-company construction | Continue source and full-document work | Actual contract identification or forecasting |

Post-run red-team: later detail could look like data available at an earlier
forecast cutoff. The text explicitly rejects that inference. The substantial
remaining uncertainty is whether all later chapters and source obligations
preserve the same distinctions; this bounded read cannot establish it. Frozen
manuscript/release files remain unchanged.

'''
p.write_text(new+old[old.index('## Continuation through300'):])
result=dict(passed=True,frontier=312,next_page=313,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=12,new_arithmetic_checks=checks,total_continuation_checks=360,pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only document/hash/Fraction work',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0301-0306-20261028.md','docs/plans/company-state-ordered-review-0307-0312-20261028.md'],result=str(p.relative_to(ROOT)))
with (H/'verification-0312.json').open('x') as f:json.dump(result,f,indent=2);f.write(chr(10))
print(json.dumps({k:result[k] for k in ['passed','frontier','next_page','source_files','page_text_hashes','new_arithmetic_checks']}))

