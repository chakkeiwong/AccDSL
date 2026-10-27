"""Guarded additive refresh; preserve the live concurrent language route."""
from pathlib import Path
from hashlib import sha256
import json
import os

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PREFIX='data/accounting-master/gap-program-20261026/'
PLAN='docs/plans/accounting-gap-program-20261026.md'
FILES=['MISSION_CONTROL.md','docs/plans/accounting-master-program.md',
 'docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md',
 'scripts/accounting_master_catalog.json']
MARK='## Reviewed full gap program and execution — 26 October 2026'

def digest(data):return sha256(data).hexdigest()
snapshot={p:(ROOT/p).read_bytes() for p in FILES}
assert not (OUT/'master-refresh-manifest.json').exists(),'Already refreshed; do not repeat completed writes'
catalog=json.loads(snapshot['scripts/accounting_master_catalog.json'])
active=catalog['active_execution_note']
parallel_plan=active['active_work_plan']
assert parallel_plan!=PLAN and (ROOT/parallel_plan).is_file(),parallel_plan
assert '5.13' in active['current_candidate'],'New manuscript requires explicit rebase'
for field,hashfield in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:
 assert digest((ROOT/active[field]).read_bytes())==active[hashfield],field
for alias,field in [('docs/AccDSL-latest.pdf','current_pdf'),('docs/AccDSL-simulation-foundations.pdf','standalone_pdf')]:
 assert (ROOT/alias).resolve()==(ROOT/active[field]).resolve(),alias
for path in FILES:
 target=OUT/'controls-before-refresh'/path
 target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(snapshot[path])

block=f'''{MARK}

The full closure program reconciles all53 inherited obligations, six interactions,
46 operations, nine literature gaps,67 original simulation failures and48
literature extensions. Thirteen cross-interface challenges and18 dependency-
ordered packages state existing support, missing evidence and next actions.
Original audit records remain verbatim;13 successor deltas correct stale
Version4.40 next actions against the current5.13 candidate. This is trace
reconciliation, not a new independent audit of every native operation.

The plan and skeptical review are recorded before execution. E01 compares four
complete typed maturity/partial/late-settlement paths, with14 controls and179
checks. Equal ending balances retain different missed-payment histories. E02
adds28 exact extended-target exchange/revision-support checks and a scoped
primary SMC2/pinned-code reading. Both results retain their synthetic/finite
limits; all18 broad packages and all whole requirements remain open.

Full reviewed plan: {PLAN}.
Closure program: {PREFIX}closure-program.md.
Current trace: {PREFIX}audit-status.json.
Result: {PREFIX}result.md.
Remaining work: {PREFIX}remaining-work.md.
Concurrent language plan retained: {parallel_plan}.
Its live successor is recorded separately in the catalog's active_work_plan;
this full program does not overwrite that route or frozen phase bindings.

Governing main5.13 (741 pages) and standalone5.12 (183/165 body pages) remain
unchanged. E01/E02 are linked companion evidence pending protected manuscript
integration. S1–S5 partial, S6 held, E3 deferred; no whole requirement closure,
independent/human acceptance, paid engagement or background campaign inferred.

'''
pending={}
for path,data in snapshot.items():
 if path.endswith('.json'):continue
 source=data.decode();assert MARK not in source,path
 head,body=source.split('\n',1)
 pending[path]=(head+'\n\n'+block+body.lstrip('\n')).encode()
active.update(full_gap_plan=PLAN,full_gap_program=PREFIX+'closure-program.md',
 closure_packages=PREFIX+'closure-packages.json',failure_register=PREFIX+'failure-register.json',
 current_audit=PREFIX+'audit-status.json',remaining_work=PREFIX+'remaining-work.md',
 current_program=PLAN,latest_gap_program_result=PREFIX+'result.md',
 gap_program_review=PREFIX+'plan-review.md',
 active_work_plans=list(dict.fromkeys([parallel_plan,PLAN]+active.get('active_work_plans',[]))),
 gap_program_next=[
  'Continue the live language subplan without repeating completed projections/grouped queries',
  'Admit a material unresolved actual-source dependency into a bounded partial history',
  'Expose reusable E01 financing state invariants and dated funding decisions',
  'Audit SMC2 resampling/waste-free dependencies and immutable evidence-vintage inference',
  'Execute remaining W01-W17 closure evidence; retain S6 held and E3 deferred'],
 gap_program_execution={'E01':'checked bounded reference:4 programs,14 controls,179 comparisons',
                        'E02':'checked exact diagnostic:28 comparisons; static source audit only'})
pending['scripts/accounting_master_catalog.json']=(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n').encode()
before=json.loads(snapshot['scripts/accounting_master_catalog.json'])
assert {k:v for k,v in before.items() if k!='active_execution_note'}=={k:v for k,v in catalog.items() if k!='active_execution_note'}
for key in ['active_work_plan','latest_internal_result','latest_result','current_candidate','current_pdf','current_pdf_sha256','standalone_pdf','standalone_pdf_sha256','phase_status','next']:
 assert catalog['active_execution_note'][key]==before['active_execution_note'][key],key
# Verify the entire snapshot, then each immediate predecessor before replace.
for path,data in snapshot.items():assert (ROOT/path).read_bytes()==data,'Concurrent control change: '+path
changes=[]
for path,data in pending.items():
 assert (ROOT/path).read_bytes()==snapshot[path],'Concurrent control change: '+path
 target=ROOT/path;temp=target.with_name(target.name+'.gap-refresh-tmp')
 temp.write_bytes(data)
 assert target.read_bytes()==snapshot[path],'Concurrent control change before replace: '+path
 os.replace(temp,target)
 changes.append({'path':path,'before_sha256':digest(snapshot[path]),'after_sha256':digest(data)})
manifest={'date':'2026-10-26','status':'refreshed','concurrent_plan_preserved':parallel_plan,
 'main':active['current_pdf'],'main_sha256':active['current_pdf_sha256'],
 'standalone':active['standalone_pdf'],'standalone_sha256':active['standalone_pdf_sha256'],
 'changes':changes,'scope':'Additive live controls and active_execution_note only; legacy catalog and frozen publications preserved'}
(OUT/'master-refresh-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'refreshed','controls':len(changes),'concurrent_plan':parallel_plan}))
