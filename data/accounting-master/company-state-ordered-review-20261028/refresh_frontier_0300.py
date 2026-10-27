"""Validate ordered reading and advance the live main frontier to300 once."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,fitz,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review'
I=D/'manuscript-release-prep-v552r2-20261027-inventory.json';j=json.loads(I.read_text());v=next(x for x in j['volumes'] if x['name']=='accounting-product-proposal')
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
for x in j['source_files']:assert sha256((ROOT/j['candidate']/x['path']).read_bytes()).hexdigest()==x['sha256']
cursor=1;prior=None
for s in [r for r in j['read_segments'] if r['volume']==v['name']]:
 assert s['pages']==list(range(cursor,cursor+len(s['pages']))) and len(s['pages'])<=6
 if prior:assert s['entry_state']==prior['exit_state']
 assert s['pdf_sha256']==v['pdf_sha256'];cursor=s['pages'][-1]+1;prior=s
assert cursor==301
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,301))
doc=fitz.open(ROOT/v['pdf'])
for p in v['pages']:assert sha256(doc[p['physical_page']-1].get_text().encode()).hexdigest()==p['text_sha256']
checks=0
for a,b in [(289,294),(295,300)]:
 x=json.loads((D/f'arithmetic-{a:04}-{b:04}.json').read_text());assert all(c['passed'] for c in x['checks']);checks+=x['count']
 for p in json.loads((D/f'render-bindings-{a:04}-{b:04}.json').read_text())['pages']:
  assert sha256((D/'rendered-main'/f'{p["page"]:04}.png').read_bytes()).hexdigest()==p['sha256']
assert checks==144
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json',
 'data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md']
backup=HERE/'controls-before-0300';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=300;d[key]['manuscript_review_frontier']['next_page']=301
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=300,next_page=301,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=300;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
t=next(x for x in d['tasks'] if x['id']=='R04');t['next_action']='Actual ordered main reading reaches300/831 on protected5.52-R2; resume301. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
for a,b in zip(old['tasks'],d['tasks']):
 for k in ['id','status','depends_on','completion_criterion','requirements']:assert a[k]==b[k]
dump(p,d)
entry='''
## Ordered main reading through300 — 28 October2026

Twelve further rendered pages289–300 are read in order with144 exact local
arithmetic checks. Annual/interim statement joins, deferred-revenue histories,
commitments, liquidity restrictions, customer overlap and segment allocation
retain their unresolved contracts and dates. Sources279, page texts831 and
entry/exit continuity verify. Result: company-state-ordered-review-20261028/result.md
under data/accounting-master. Resume physical301;531 main pages remain.

This is author reading only. Node/equation, simulation, successor-delta and
independent/human review remain incomplete. S06 is in_progress; original task
criteria and releases are unchanged. E3 remains deferred. Continue ready work.

'''
for n in paths[4:]:
 p=ROOT/n;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=HERE/'result.md';old=p.read_text();(HERE/'result-before-0300.md').write_text(old)
new='''# Ordered reading reaches physical page300

## Continuation through300 — 28 October2026

Twelve actual pages289–300 are now read in two six-page segments, each carrying
the exact previous exit.77 and67 exact checks pass,144 additional checks in
this continuation. Across265–300 the recorded reading covers36 pages with327
local arithmetic checks. Neither count substitutes for whole-document review.

Annual and interim statement bridges preserve stock/flow and population
boundaries. Deferred-revenue and commitment examples distinguish net movements
from gross additions, delivery, billing and cash. Cash restrictions, securities
valuation, customer overlap and geographic cost allocation retain different
meanings and unresolved histories. No new substantive defect was confirmed in
these twelve pages; external source authority was not newly inspected.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain pages289–300 as author-read | Actual ordered images and page-specific judgments |279 source hashes,831 page texts, continuity and12 renders pass |531 unread main pages and separate review layers | Continue301 | Independent or human acceptance |
| Retain local calculations |144 exact checks and explicit premises | No local arithmetic veto | Source applicability, actual contracts, later contradictions | Continue source and whole-document work | General simulator or accounting correctness |

Post-run red team: individually coherent note examples may not join into one
actual company history. The manuscript itself preserves this limit. A later
contradiction, changed source or unsupported premise would reopen the affected
judgment. Frozen manuscripts and release statuses remain unchanged.

'''
p.write_text(new+old[old.index('## Continuation through288'):])
verification=dict(passed=True,frontier=300,next_page=301,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=12,new_arithmetic_checks=checks,total_continuation_checks=327,
 pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 command=[sys.executable,*sys.argv],cpu_gpu='CPU-only document/hash/Fraction work; no GPU imports',seeds='N/A deterministic',
 plans=['docs/plans/company-state-ordered-review-0289-0294-20261028.md','docs/plans/company-state-ordered-review-0295-0300-20261028.md'],result=str((HERE/'result.md').relative_to(ROOT)))
with (HERE/'verification-0300.json').open('x') as f:json.dump(verification,f,indent=2);f.write(chr(10))
print(json.dumps({k:verification[k] for k in ['passed','frontier','next_page','source_files','page_text_hashes','new_arithmetic_checks']}))

