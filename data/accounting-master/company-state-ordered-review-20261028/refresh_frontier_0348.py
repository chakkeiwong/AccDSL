"""Verify actual ordered reading and update348/349 navigation once."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess,sys,time
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
assert cursor==349
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,349))
doc=fitz.open(ROOT/v['pdf'])
for page in v['pages']:assert sha256(doc[page['physical_page']-1].get_text().encode()).hexdigest()==page['text_sha256']
checks=0
for a,b in [(337,342),(343,348)]:
 r=json.loads((D/f'arithmetic-{a:04}-{b:04}.json').read_text());assert all(c['passed'] for c in r['checks']);checks+=r['count']
 for page in json.loads((D/f'render-bindings-{a:04}-{b:04}.json').read_text())['pages']:
  assert sha256((D/'rendered-main'/f'{page["page"]:04}.png').read_bytes()).hexdigest()==page['sha256']
assert checks==31
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0348';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=348;d[key]['manuscript_review_frontier']['next_page']=349
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=348,next_page=349,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=348;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
for task in d['tasks']:
 if task['id']=='R04':task['next_action']='Actual ordered main reading reaches348/831 on protected5.52-R2; resume349. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
 if task['id']=='C04':task['next_action']=task['next_action'].replace('from337','from349')
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through348 — 28 October2026

Twelve further pages337–348 are individually read;31 exact local checks pass.
Language/extraction/contract boundaries, typed-library baseline, scoped history
families, certain liabilities and signed-book invariants remain distinct.
279 source hashes,831 page texts, continuity and12 renders verify. Resume349;
483 main pages remain. Result: company-state-ordered-review-20261028/result.md
under data/accounting-master. Independent/human and other review layers remain open.

43 original failures reviewed;158 outside this pass. Original criteria/statuses
and frozen releases persist. E3 deferred. Continue source/construction work
and ordered reading. No global continuation veto.

'''
for name in paths[5:]:
 p=ROOT/name;title,rest=p.read_text().split('\n',1);p.write_text(title+'\n'+entry+rest)
p=ROOT/paths[4];text=p.read_text().replace('Main reading336/831','Main reading348/831').replace('resume337','resume349').replace('from337','from349')
title,rest=text.split('\n',1);p.write_text(title+'\n'+entry+rest)
p=H/'result.md';old=p.read_text();(H/'result-before-0348.md').write_text(old)
new='''# Ordered reading reaches physical page348

## Continuation through348 — 28 October2026

Twelve individually rendered pages337–348 are read in two ordered six-page
segments, with7 and24 exact local checks. The continuation265–348 now has84
pages and484 local checks. These are coverage counts, not acceptance scores.

Chapter30 separates DSL/compiler semantics, contract events and extraction
metrics from accounting admission. The46-hour example gives one complete
elapsed day versus two calendar days; its simple-interest factor differs by2.
No ACTUS version, paper result or current licence is newly certified here.
Chapter31 retains a serious typed-schema/SQL/Python baseline and a shared IR.
Reported borrowing100 does not turn assumed loans60/40 into disclosed facts;
70/30 fits the same aggregate. Adapter outputs remain subject to accounting
and source checks.

Chapter32 introduces scoped compatible histories and explicit rounding before
querying them. A payable100 owed to A or B has a certain total and existence,
but no certain creditor row. Intersection loses that existence; union produces
a false total200. Empty histories change the result. Imported incomplete-
database theorems retain their information-order, genericity and representation
conditions. An undecided evaluator need not imply opposite feasible answers.
The null-space derivation and receivables bridge preserve alternative movements;
bookkeeping induction preserves balance without establishing economic meaning.
Reporting additionally needs classified movements, context and economic state.

| Ledger | Verdict |
| --- | --- |
| Reader comprehension | Concrete examples explain context, answer-family and adapter distinctions; independent reader remains pending |
| Mathematical integrity |31 local timing, set and rational checks pass; imported theorems are not newly certified |
| Source fidelity | Historical source/code/licence inspections remain scoped and distinct from present admission or integration |
| Typography/rendering | All12 pages viewed individually; continuing tables, diagrams, short chapter ends and displayed equations are legible |

No confirmed local manuscript defect is added by this slice. Frozen texts and
release hashes remain unchanged. The7/24 check counts do not replace the
actual per-page judgments in main-0337-0342.json and main-0343-0348.json.

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Record author reading337–348 | Actual ordered images, reader state and local checks |279 source/831 text hashes, continuity and12 renders match |483 unread main pages; independent/hierarchy/simulation/successor reviews | Resume349 and continue source/construction work | Whole-document or human acceptance |

Post-run red team: correct local definitions do not establish a complete
company-history implementation, and cited source boundaries are not substitutes
for technical primary-source review. Those acceptance obligations remain open.

'''
p.write_text(new+old.split('\n',1)[1])
result=dict(passed=True,frontier=348,next_page=349,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=12,new_arithmetic_checks=checks,total_continuation_checks=484,pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only PDF/hash/rational reading checks',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0337-0342-20261028.md','docs/plans/company-state-ordered-review-0343-0348-20261028.md'],result=str(p.relative_to(ROOT)))
dump(H/'verification-0348.json',result);print(json.dumps(result))
