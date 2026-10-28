"""One-shot verify and refresh actual ordered reading366/367."""
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
assert cursor==367
assert [p['physical_page'] for p in v['pages'] if p['author_continuous_read']=='author_read']==list(range(1,367))
doc=fitz.open(ROOT/v['pdf'])
for page in v['pages']:assert sha256(doc[page['physical_page']-1].get_text().encode()).hexdigest()==page['text_sha256']
arith=json.loads((D/'arithmetic-0361-0366.json').read_text());assert arith['count']==42 and all(x['passed'] for x in arith['checks'])
for page in json.loads((D/'render-bindings-0361-0366.json').read_text())['pages']:
 assert sha256((D/'rendered-main'/f'{page["page"]:04}.png').read_bytes()).hexdigest()==page['sha256']
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','data/accounting-master/release-pursuit-20261027/state.json','data/accounting-master/unified-program-20261028/program.json','data/accounting-master/construction-continuation-20261028/checkpoint.md','data/accounting-master/next-plan.md','docs/plans/company-state-research-release-program-20261028.md','docs/plans/accounting-master-checkpoint.md','MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md']
backup=H/'controls-before-0366';backup.mkdir(exist_ok=False)
for i,p in enumerate(paths):(backup/(str(i)+'-'+Path(p).name)).write_bytes((ROOT/p).read_bytes())
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
for name,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
 d=json.loads((ROOT/name).read_text());d[key]['manuscript_review_frontier'].update(physical_pages_read=366,next_page=367)
 d[key]['ordered_review_continuation_20261028']=dict(physical_pages_read=366,next_page=367,result='data/accounting-master/company-state-ordered-review-20261028/result.md',unresolved_local_finding='READ-0358-0360-01',scope='Author diagnosis; successor navigation repair and independent/human acceptance pending');dump(ROOT/name,d)
d=json.loads((ROOT/paths[2]).read_text());d['ordered_read_pages']=366;dump(ROOT/paths[2],d)
p=ROOT/paths[3];d=json.loads(p.read_text());old=deepcopy(d)
for task in d['tasks']:
 if task['id']=='R04':
  task['next_action']='Actual ordered main reading reaches366/831 on protected5.52-R2; resume367. READ-0358-0360-01 records appendix-reference navigation burden for post-diagnosis successor repair. Node/equation, simulation, successor-delta and independent reviews remain incomplete.'
  evidence='data/accounting-master/company-state-ordered-review-20261028/finding-0358-0360.json'
  if evidence not in task['evidence']:task['evidence'].append(evidence)
 if task['id']=='C04':task['next_action']=task['next_action'].replace('reading361','reading367')
for a,b in zip(old['tasks'],d['tasks']):
 for key in ['id','status','depends_on','completion_criterion','requirements']:assert a[key]==b[key]
dump(p,d)
entry='\n## Ordered main reading through366 — 28 October2026\n\nPages361–366 are individually read;42 local exact checks cover the shared debt\nfraction, decimal identity and balanced posting illustrations. The language\nchapter states its authoring/compiler limits and distinguishes source identity,\nmeaning and admission. Prior navigation finding READ-0358-0360-01 stays open.\n279 source hashes,831 page texts, continuity and six renders verify. Resume367;\n465 main pages remain. Independent/human and other review layers stay open.\n\n79 original failures reviewed;122 outside this pass. Original criteria/statuses\nand releases persist;E3 deferred. Continue original literature/source work.\n\n'
for name in paths[5:]:
 p=ROOT/name;title,rest=p.read_text().split(chr(10),1);p.write_text(title+chr(10)+entry+rest)
p=ROOT/paths[4]
p.write_text('# Construction continuation checkpoint'+chr(10)+entry+'''Live program: data/accounting-master/unified-program-20261028/program.json.
40 tasks,114 acceptance rows,156 clauses,18 packages,201 original failures.
T01 definition complete; construction/research/acceptance remain incomplete.
S1–S5 partial,S6 held,E3 deferred. Selected5.55-R1/provisional5.56-D1 not_ready.
No global continuation veto. Main review366/831; next367.

Next: inspect LIT-F010–015: sufficient state, uninformative/zero likelihood,
resampling type coverage, source correction and future evidence access. Reuse
retained complete evidence only where it answers the exact original treatment.
Continue source research and reading367. READ-0358-0360-01 stays open.
Do not rerun one-shot scripts; concurrent edits stay separate.
''')
p=H/'result.md';old=p.read_text();(H/'result-before-0366.md').write_text(old)
new='# Ordered reading reaches physical page366\n\n## Continuation through366 — 28 October2026\n\nSix pages361–366 are read individually and in order. The continuation265–366\ncovers102 pages and1014 local exact checks. The42 new checks reproduce the\nshared debt partition, fixed/floating-share substitution, rate endpoints,\nexact decimal and simple-interest posting illustrations. They are local\nchecks, not portable-codec conformance or a complete compiler test.\n\nThe type table distinguishes unweighted choices, shared symbols and explicit\nmeasures; missingness and NotApplicable stay separate from zero. Portable\nrecord identity is motivated by cross-frontend exchange, with rational,\nUnicode and dependency rules defined before the digest. Source-byte identity\nand financial admission remain separate. The profile explicitly admits that\nwhole-company authoring is broader than the matched debt frontend.\n\nThe worked debt listing makes one shared alpha concrete. It preserves the\ncontinuous family rather than only the named endpoints; a probability measure\nrequires another premise. The InterestPaid example makes same-date settlement,\nrounding and negative-interest limits explicit before explaining override\nconflicts and unresolved applicability. Package and IR migration rules close\nthe chapter without treating syntax as recognition authority.\n\nThe later examples improve the reader route but do not repair the earlier\nappendix-reference overview. READ-0358-0360-01 remains unresolved successor\nwork after diagnosis. No frozen manuscript was changed.\n\n| Ledger | Verdict |\n| --- | --- |\n| Reader comprehension | Shared debt and posting examples become locally reconstructable; prior overview repair and independent/human reading remain open |\n| Mathematical integrity |42 local exact checks pass; schema digest read as a definition, not a cryptographic or compiler proof |\n| Source fidelity | Historical grammar, supplied demo assumptions and present authoring limits stay explicit; no new external theorem certification |\n| Typography/rendering | Six full pages individually inspected; code boxes and type table fit; no clipping confirmed |\n\n| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |\n| --- | --- | --- | --- | --- | --- |\n| Record author reading361–366 | Actual images and specific continuous reader judgments |279 source/831 text hashes and six renders match |465 unread main pages and pending repair/independent layers | Continue367 plus source/construction work | Complete design, compiler or human acceptance |\n\nPost-run red team: clear local examples are narrower than an implementable\nwhole-company language. The manuscript itself retains that distinction.\n\n'
p.write_text(new+old.split(chr(10),1)[1])
result=dict(passed=True,frontier=366,next_page=367,source_files=len(j['source_files']),page_text_hashes=len(v['pages']),new_rendered_pages=6,new_arithmetic_checks=42,total_continuation_checks=1014,pdf_sha256=v['pdf_sha256'],unresolved_findings=['READ-0358-0360-01'],independent_reader='pending',human_acceptance='pending',hierarchy='separate incomplete obligation',git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cpu_gpu='CPU-only PDF/hash/rational reading checks',seeds='N/A deterministic',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plans=['docs/plans/company-state-ordered-review-0361-0366-20261028.md'],result=str(p.relative_to(ROOT)))
dump(H/'verification-0366.json',result);print(json.dumps(result))
