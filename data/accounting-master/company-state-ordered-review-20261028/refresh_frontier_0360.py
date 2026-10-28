"""One-shot verify and refresh actual ordered reading360/361."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys,time
from pathlib import Path
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
assert cursor==361
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,361))
doc=fitz.open(ROOT/v['pdf'])
for page in v['pages']:assert sha256(doc[page['physical_page']-1].get_text().encode()).hexdigest()==page['text_sha256']
arith=json.loads((D/'arithmetic-0355-0360.json').read_text());assert arith['count']==41 and all(x['passed'] for x in arith['checks'])
for page in json.loads((D/'render-bindings-0355-0360.json').read_text())['pages']:
 assert sha256((D/'rendered-main'/f'{page["page"]:04}.png').read_bytes()).hexdigest()==page['sha256']
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0360';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for name,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/name).read_text());d[key]['manuscript_review_frontier'].update(physical_pages_read=360,next_page=361)
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=360,next_page=361,result='data/accounting-master/company-state-ordered-review-20261028/result.md',unresolved_local_finding='READ-0358-0360-01',scope='Author diagnosis; successor navigation repair and independent/human acceptance pending');dump(ROOT/name,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=360;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
for task in d['tasks']:
 if task['id']=='R04':
  task['next_action']='Actual ordered main reading reaches360/831 on protected5.52-R2; resume361. READ-0358-0360-01 records appendix-reference navigation burden for post-diagnosis successor repair. Node/equation, simulation, successor-delta and independent reviews remain incomplete.'
  evidence='data/accounting-master/company-state-ordered-review-20261028/finding-0358-0360.json'
  if evidence not in task['evidence']:task['evidence'].append(evidence)
 if task['id']=='C04':task['next_action']=task['next_action'].replace('from355','from361')
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='''
## Ordered main reading through360 — 28 October2026

Pages355–360 are individually read;41 rational checks cover rates, Bayesian
updates, Gaussian moments and the supplied intervention example. One concrete
language-chapter navigation issue is recorded as READ-0358-0360-01 for successor
repair after diagnosis. Frozen manuscripts remain unchanged. Result:
company-state-ordered-review-20261028/result.md under data/accounting-master.
279 source hashes,831 page texts, continuity and six renders verify. Resume361;
471 main pages remain. Independent/human and other review layers stay open.

68 original failures reviewed;133 outside this pass. Original criteria/statuses
and releases persist;E3 deferred. Continue information/causal cases and sources.

'''
for name in paths[5:]:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=ROOT/paths[4]
p.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review360/831; next361.

Next: inspect original SIM-F013/017/020 and existing information/causal evidence
before implementing new discriminators. Continue source research and reading361.
Preserve finding READ-0358-0360-01 for successor prose repair after diagnosis.
Do not rerun one-shot scripts; concurrent edits stay separate.
''')
p=H/'result.md';old=p.read_text();(H/'result-before-0360.md').write_text(old)
new='''# Ordered reading reaches physical page360

## Continuation through360 — 28 October2026

Six pages355–360 are read as individual images in order. The continuation265–360
now covers96 pages and972 local arithmetic checks. The41 new controls reproduce
the positive-payment rate examples, a mixed-sign two-root counterexample,
rounding-boundary uncertainty, Bayes normalization, Gaussian square completion
and the supplied conditioning/intervention distinction. These are exact local
checks, not certification of imported source claims or an inference service.

Pages355–357 state assumptions before the key displays and distinguish numerical
precision, information reuse and causal mechanisms. Page358 opens the accounting
language chapter with clear distinctions, but its overview then becomes a long
sequence of appendix extensions across358–360. The reader must leave the local
argument to reconstruct how to express a company model. READ-0358-0360-01 in
finding-0358-0360.json records this specific navigation issue and a repair that
organizes the overview around a sourced balance, an unresolved contract and a
conditional operation, retaining exact references in a separate reference layer.

The finding is unresolved successor work. No frozen manuscript has been edited,
and this diagnosis is not a completed prose repair. The whole-document plan
requires diagnosis before successor reconstruction. Current language limitations,
common-book compatibility and source/semantic identity distinctions must survive
that repair. The Money<C> table begins on360 and continues beyond this slice.

| Ledger | Verdict |
| --- | --- |
| Reader comprehension | Precision/update/causal examples are locally interpretable;33.1 needs the recorded navigation repair; independent and human reading pending |
| Mathematical integrity |41 exact controls pass; displayed scalar targets and domain distinctions checked; imported source results not newly certified |
| Source fidelity | Stuart, Giacomini–Kitagawa and Pearl remain source anchors with explicit transfer limits; this review makes no new external authority claim |
| Typography/rendering | Six full pages individually inspected; no clipping confirmed;360 begins a continuing type table |

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Record author reading355–360 | Actual images, carried reader state and specific local judgments |279 source/831 text hashes and six renders match |471 unread main pages, navigation repair and other review layers | Continue361, source and construction work | Complete manuscript or human acceptance |

Post-run red-team: correct scalar mathematics does not establish a usable
whole-company language. The confirmed appendix-navigation burden remains open
rather than being concealed by successful arithmetic or hash checks.

'''
p.write_text(new+old.split(chr(10),1)[1])
result=dict(passed=True,frontier=360,next_page=361,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=6,new_arithmetic_checks=41,total_continuation_checks=972,pdf_sha256=v['pdf_sha256'],unresolved_findings=['READ-0358-0360-01'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only PDF/hash/rational reading checks',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0355-0360-20261028.md'],result=str(p.relative_to(ROOT)))
dump(H/'verification-0360.json',result);print(json.dumps(result))
