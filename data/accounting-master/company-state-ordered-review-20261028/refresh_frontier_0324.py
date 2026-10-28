"""Verify actual ordered reading and advance the live frontier to324 once."""
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
assert cursor==325
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,325))
doc=fitz.open(ROOT/v['pdf'])
for p in v['pages']:assert sha256(doc[p['physical_page']-1].get_text().encode()).hexdigest()==p['text_sha256']
checks=0
for a,b in [(313,318),(319,324)]:
 r=json.loads((D/f'arithmetic-{a:04}-{b:04}.json').read_text());assert all(c['passed'] for c in r['checks']);checks+=r['count']
 for p in json.loads((D/f'render-bindings-{a:04}-{b:04}.json').read_text())['pages']:
  assert sha256((D/'rendered-main'/f'{p["page"]:04}.png').read_bytes()).hexdigest()==p['sha256']
assert checks==50
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0324';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=324;d[key]['manuscript_review_frontier']['next_page']=325
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=324,next_page=325,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=324;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d);t=next(x for x in d['tasks'] if x['id']=='R04');t['next_action']='Actual ordered main reading reaches324/831 on protected5.52-R2; resume325. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through 324 — 28 October 2026

Twelve further pages313–324 are individually read in order, with50 exact
checks. Supply/product/service constraints, conditional asset/liability
histories, joint cash settlements and source/evidence-view distinctions remain
separate.279 source hashes,831 page texts, ordered continuity and12 new renders
verify. Resume325;507 main pages remain. Result:
company-state-ordered-review-20261028/result.md under data/accounting-master.

S09 is in_progress;25 original failures reviewed and176 outside this pass.
All original criteria, dependencies and releases persist. R04 remains
in_progress, independent/human and other review layers open. E3 deferred.
Continue ready source/construction/failure work and ordered reading.

'''
for n in paths[4:]:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=H/'result.md';old=p.read_text();(H/'result-before-0324.md').write_text(old)
new='''# Ordered reading reaches physical page 324

## Continuation through 324 — 28 October 2026

Twelve individual rendered pages313–324 are read in two ordered six-page
segments.23 and27 exact checks pass. The continuation265–324 now records
60 pages and410 local arithmetic checks; counts are navigation, not acceptance.

Product compatibility, supplier capacity, defective stock, purchase commitments
and service rights create different feasible responses despite equal balances.
Development, shipment, service delivery and cash dates remain distinct. Two
conditional asset histories preserve equal net property under different gross
transactions, and an independently assumed expense liability offsets the extra
capital payable/loss. Alpha allocates two indirect-cash-flow rows; their sum
is unchanged. Future settlement retains joint operating/investing pairs,
not independently selectable minima, and six paths preserve branch and date.
The exact paired total is-3082; mixed marginal minima fabricate-4082.

The text then moves from partial connected answers to immutable source
assertions, context/value/meaning/time/review fields, changing perimeters and
separate document/semantic/simulation coverage. A source reading can finish
while historical clocks or economic families remain unresolved. No substantive
manuscript defect is confirmed in this slice. Current legal/accounting authority
and cited technical papers were not newly certified. Chapter28's short final
page and the Chapter29 table continuation are readable, not missing text.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain author reading313–324 | Individual readable images and exact segment continuity |279 source/831 text hashes and12 renders verify |507 unread main pages plus separate review layers | Continue325 | Independent/human acceptance |
| Retain conditional arithmetic |50 exact checks; scope/premises explicit | No local arithmetic veto | Source-supported actual states and dates | Continue source and company-state construction | Exhaustive real-company history family |

Post-run red-team: balanced totals might conceal different liabilities or
settlement dates. The joint table and six timing paths expose that error;
context and information chapters preserve the remaining uncertainty. Success
of local calculations cannot close later chapters or source obligations.
Frozen manuscript and releases remain unchanged; independent/human review,
node/equation layer, simulation volume and successor changes remain open.

'''
p.write_text(new+old[old.index('## Continuation through312'):])
result=dict(passed=True,frontier=324,next_page=325,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=12,new_arithmetic_checks=checks,total_continuation_checks=410,pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only document/hash/Fraction work',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0313-0318-20261028.md','docs/plans/company-state-ordered-review-0319-0324-20261028.md'],result=str(p.relative_to(ROOT)))
with (H/'verification-0324.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write(chr(10))
print(json.dumps({k:result[k] for k in ['passed','frontier','next_page','source_files','page_text_hashes','new_arithmetic_checks']}))

