"""Verify actual ordered reading and advance354/355 navigation once."""
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
assert cursor==355
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,355))
doc=fitz.open(ROOT/v['pdf'])
for page in v['pages']:assert sha256(doc[page['physical_page']-1].get_text().encode()).hexdigest()==page['text_sha256']
arith=json.loads((D/'arithmetic-0349-0354.json').read_text());assert all(c['passed'] for c in arith['checks']) and arith['count']==447
for page in json.loads((D/'render-bindings-0349-0354.json').read_text())['pages']:
 assert sha256((D/'rendered-main'/f'{page["page"]:04}.png').read_bytes()).hexdigest()==page['sha256']
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0354';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/p).read_text());d[key]['manuscript_review_frontier']['physical_pages_read']=354;d[key]['manuscript_review_frontier']['next_page']=355
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=354,next_page=355,result='data/accounting-master/company-state-ordered-review-20261028/result.md',scope='Actual author reading; independent/human acceptance pending');dump(ROOT/p,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=354;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
for task in d['tasks']:
 if task['id']=='R04':task['next_action']='Actual ordered main reading reaches354/831 on protected5.52-R2; resume355. Node/equation, simulation, successor-delta and independent reviews remain separate and incomplete.'
 if task['id']=='C04':task['next_action']=task['next_action'].replace('from349','from355')
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through354 — 28 October2026

Six further pages349–354 are individually read;447 exact local checks include
all206 rounded-display witnesses. Law families/mixtures, scoped construction,
half-open bounds, input quantization and unresolved mass remain distinct.
279 source hashes,831 page texts, continuity and six renders verify. Resume355;
477 main pages remain. Result: company-state-ordered-review-20261028/result.md
under data/accounting-master. Independent/human and other review layers remain open.

61 original failures reviewed;140 outside this pass. Original criteria/statuses
and frozen releases persist. E3 deferred. Continue source/construction work
and ordered reading. No global continuation veto.

'''
for name in paths[5:]:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=ROOT/paths[4];text=p.read_text().replace('Main reading348/831','Main reading354/831').replace('resume349','resume355').replace('from349','from355')
title,rest=text.split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=H/'result.md';old=p.read_text();(H/'result-before-0354.md').write_text(old)
new='''# Ordered reading reaches physical page354

## Continuation through354 — 28 October2026

Six individual pages349–354 continue from the exact prior reader state. The
continuation265–354 now covers90 pages with931 local arithmetic checks. The447
new checks include separate feasibility and equality checks for each of206
rounded-display witnesses; counts describe coverage, not acceptance quality.

The event architecture distinguishes policy information, event generation,
accounting and atomic state update. Date-limited measurement expectations and
probability-measure declarations remain explicit. A family of conditional laws
is different from a mixture under a supplied measure. Total variance requires
that measure; sample extrema and interval enclosures retain distinct meanings.

Rounded debt uses principal amounts rather than unknown-share products. The
interest image[4.975,7.035) has an attained lower endpoint and excluded upper
endpoint. Rounded displays4.98–7.03 cover206 cents, whereas cent-grid principal
has raw maximum7.0343. Equal displays do not identify the same latent domain.
All206 explicit witnesses and signed/tie/operation-order controls check exactly.

Construction remains scoped and preserves unfinished cells. Additive grouping
is conditional on transitions and reports under every admitted driver; changed
query scope requires renewed sufficiency. Identical terminal cash does not
erase treaty or bank-commitment memory. Posterior3/11,8/11 gives complete mean77
only when both branch equities are available; unresolved mass stays attached.
The effective-rate equation starts a new precision discussion to continue355.

| Ledger | Verdict |
| --- | --- |
| Reader comprehension | Concrete interval and treaty examples explain why query identity includes domain, memory and conditional mass; independent reading remains pending |
| Mathematical integrity |447 local finite/rational controls pass, including206 display witnesses; no imported theorem newly certified |
| Source fidelity | Hypothetical measures and supplied treaty values remain distinct from source admission and cross-referenced derivations |
| Typography/rendering | All six pages viewed individually; dense353 is legible, continued sentences and displays have no confirmed clipping |

No confirmed local defect is added. Policy notation containing full state is
explicitly subject to the permitted-information rule; law equality remains
relative to the declared policy/scenario question. Those are implementation
obligations, not permissions to expose hidden state or reuse altered queries.

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Record author reading349–354 | Actual ordered images, reader state and local arithmetic |279 source/831 text hashes, continuity and six renders match |477 unread main pages and other review layers | Resume355; continue construction/research independently | Whole-document or human acceptance |

Post-run red team: the local witness calculation does not establish a general
query solver, actual history coverage or admitted weights. Remaining review and
construction obligations persist. Frozen manuscripts are unchanged.

'''
p.write_text(new+old.split(chr(10),1)[1])
result=dict(passed=True,frontier=354,next_page=355,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=6,new_arithmetic_checks=447,total_continuation_checks=931,pdf_sha256=v['pdf_sha256'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only PDF/hash/rational reading checks',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0349-0354-20261028.md'],result=str(p.relative_to(ROOT)))
dump(H/'verification-0354.json',result);print(json.dumps(result))
