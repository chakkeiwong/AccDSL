"""Verify ordered reading and advance live navigation from324 to336 once."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import fitz
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
D=ROOT/'data/accounting-master/release-pursuit-20261027/manuscript-review';start=time.monotonic()
I=D/'manuscript-release-prep-v552r2-20261027-inventory.json';j=json.loads(I.read_text());v=next(x for x in j['volumes'] if x['name']=='accounting-product-proposal')
assert sha256((ROOT/v['pdf']).read_bytes()).hexdigest()==v['pdf_sha256']
for row in j['source_files']:assert sha256((ROOT/j['candidate']/row['path']).read_bytes()).hexdigest()==row['sha256']
cursor=1;prior=None
for segment in [r for r in j['read_segments'] if r['volume']==v['name']]:
 assert segment['pages']==list(range(cursor,cursor+len(segment['pages']))) and len(segment['pages'])<=6
 if prior:assert segment['entry_state']==prior['exit_state']
 assert segment['pdf_sha256']==v['pdf_sha256'];cursor=segment['pages'][-1]+1;prior=segment
assert cursor==337
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,337))
doc=fitz.open(ROOT/v['pdf'])
for page in v['pages']:assert sha256(doc[page['physical_page']-1].get_text().encode()).hexdigest()==page['text_sha256']
checks=0
for a,b in [(325,330),(331,336)]:
 r=json.loads((D/f'arithmetic-{a:04}-{b:04}.json').read_text());assert all(c['passed'] for c in r['checks']);checks+=r['count']
 for page in json.loads((D/f'render-bindings-{a:04}-{b:04}.json').read_text())['pages']:
  assert sha256((D/'rendered-main'/f'{page["page"]:04}.png').read_bytes()).hexdigest()==page['sha256']
assert checks==43
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0336';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=336;d[key]['manuscript_review_frontier']['next_page']=337
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=336,next_page=337,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=336;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
for task in d['tasks']:
 if task['id']=='R04':task['next_action']='Actual ordered main reading reaches336/831 on protected5.52-R2; resume337. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
 if task['id']=='C04':task['next_action']=task['next_action'].replace('from325','from337')
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through336 — 28 October2026

Twelve further pages325–336 are individually read with43 exact checks.
Partition mappings, rounding, source clocks, corrections and literature
transfer limits remain distinct.279 source hashes,831 page texts, complete
ordered continuity and12 renders verify. Resume337;495 main pages remain.
Result: company-state-ordered-review-20261028/result.md under data/accounting-master.

Twenty-seven original failures reviewed;174 outside this pass. All original
criteria/dependencies/statuses and frozen releases persist. Independent/human,
hierarchy, simulation and successor-delta reviews remain open. E3 deferred.
Continue ready source/construction/failure work and ordered reading.

'''
for name in paths[4:]:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=H/'result.md';old=p.read_text();(H/'result-before-0336.md').write_text(old)
new='''# Ordered reading reaches physical page336

## Continuation through336 — 28 October2026

Twelve individually rendered pages325–336 are read in two ordered six-page
segments.30 and13 exact checks pass. The continuation265–336 now contains72
pages and453 local checks; these counts describe coverage, not acceptance.

Chapter29 distinguishes mapping partitions from populations, transcription
from an accepted interpretation, document coverage from economic completeness,
and public availability from possession and reviewed use. The revenue example
has two partitions summing260; adding both gives520. Two feasible joint tables
show that margins alone do not identify cross-cells. Nearest rounding gives
99.5–100.5 under a supplied assumption; positive truncation gives100–101 with
upper endpoint excluded. Neither rule follows from display precision alone.
The same-vintage half-year difference is260−110=150; using original120 mixes
vintages even though260−120=140 is arithmetically correct.

The treaty case preserves different initial measurements under different
contract order despite equal terminal cash. Later evidence changes a
conditional reconstruction without rewriting committed events. Candidate-set
membership, negative search results and full dependency ancestry affect reuse;
a correction still needs its accounting treatment before a journal can follow.

Chapter30 separates accounting identities, economic behavior and dated events.
The normalized identity S+N+O−C=0 is consistent with different financing choices.
An exact finite example shows that no row can be individually certain even
when every history contains some row. Database provenance, robust priors,
model averaging and intervention retain their source-specific assumptions;
no paper theorem is newly certified or transferred by this reading.

| Ledger | Verdict |
| --- | --- |
| Reader comprehension | Concrete cases explain why source meaning, date, measurement and posting are separate; independent reader pending |
| Mathematical integrity |43 conditional local checks pass; cited insurance and research derivations remain source-specific obligations |
| Source fidelity | Original versus interpretation and historical manuscript versus current survey status stay distinct; no new authority certification |
| Typography/rendering | All12 pages inspected individually; rounding display continuation, figure and short chapter end are readable |

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Record author reading325–336 | Individual images and exact entry/exit continuity |279 source/831 text hashes and12 renders match |495 unread main pages and other review layers | Continue337 | Independent/human acceptance |
| Retain local comparisons | Conditional arithmetic/finite examples agree | No local substantive defect confirmed | Actual source facts, method assumptions and runtime admission | Continue source/construction work | Complete company model or legal/accounting authority |

Post-run red team: successful normalized reconciliation cannot identify a
financing decision; unchanged cash cannot identify recognition timing; source
availability cannot prove system or investor knowledge. These distinctions
remain explicit. No frozen manuscript source changes were made. This is
whole-document diagnosis in progress, not a finished prose repair or release.

'''
p.write_text(new+old[old.index('## Continuation through 324'):])
result=dict(passed=True,frontier=336,next_page=337,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=12,new_arithmetic_checks=checks,total_continuation_checks=453,pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only document/hash/Fraction work',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0325-0330-20261028.md','docs/plans/company-state-ordered-review-0331-0336-20261028.md'],result=str(p.relative_to(ROOT)))
with (H/'verification-0336.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write(chr(10))
print(json.dumps({k:result[k] for k in ['passed','frontier','next_page','source_files','page_text_hashes','new_arithmetic_checks']}))

