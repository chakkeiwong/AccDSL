"""Guardedly select the checked 5.55 package and reconcile live controls once."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

D=Path(__file__).resolve().parent; R=D.parents[3]
B=R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027'
T=R/'docs/design/proposal/manuscript-sector-v555-20261027'
read=lambda p:json.loads(p.read_text())
digest=lambda p:sha256(p.read_bytes()).hexdigest()
prefix=str(D.relative_to(R)); result=prefix+'/result.md'; remaining=prefix+'/remaining-work.md'
assert not (D/'advancement.json').exists()
assert read(D/'verification-02.json')['passed']
assert read(D/'relocation-01/result.json')['passed']
assert (D/'author-review.md').is_file() and (D/'result.md').is_file()
assert digest(T/'package-manifest.json')==read(D/'package-record.json')['manifest_sha256']
for row in read(T/'package-manifest.json')['files']:assert digest(T/row['path'])==row['sha256'],row['path']
for row in read(D/'baseline.json')['files']:assert digest(B/row['path'])==row['sha256'],row['path']
preserved=read(D.parent/'replay-package/advancement.json')['preserved_release_records']
for p,h in preserved.items():assert digest(R/p)==h,p
for unit in ['insurance-paa-dated-book-20261027','bank-interface-consolidation-20261027']:
    supplement=read(R/'data/accounting-master'/unit/'acceptance-supplement.json')
    for p,h in {**supplement['baseline_records'],**supplement['evidence']}.items():assert digest(R/p)==h,p
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
       'data/accounting-master/next-plan.md','docs/README.md',
       'data/accounting-master/release-pursuit-20261027/state.json',
       'data/accounting-master/release-pursuit-20261027/reset-memo.md',
       'data/accounting-master/release-pursuit-20261027/progress.md']
before={p:(R/p).read_bytes() for p in paths}; new={}
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf',
       'docs/AccDSL-latest.tex':'accounting-product-proposal.tex',
       'docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf',
       'docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,name in links.items():
    assert (R/p).is_symlink() and (R/p).resolve()==B/name,p
    link_before[p]=os.readlink(R/p)
now=datetime.now(timezone.utc).isoformat()
state=json.loads(before[paths[10]])
inventory=read(D.parent/'manuscript-review/manuscript-release-prep-v552r2-20261027-inventory.json')
segments=[s for s in inventory['read_segments'] if s['volume']=='accounting-product-proposal']
frontier=segments[-1]['pages'][-1]
assert state['ordered_read_pages']==frontier
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    obj=json.loads(before[p]); a=obj[key]
    assert a['current_candidate']=='5.54-R2;835 pages;not_ready'
    assert a['active_work_plan']=='docs/plans/accounting-release-eight-hour-20261027.md'
    assert a['current_pdf']==str((B/'accounting-product-proposal.pdf').relative_to(R))
    a.update(updated=now,current_candidate='5.55;836 pages;not_ready',package_revision=1,
        latest_internal_result=result,latest_manuscript_result=result,latest_package_result=result,
        current_package_record=prefix+'/package-record.json',remaining_work=remaining,
        latest_reset_memo=prefix+'/reset-memo.md',
        current_internal_status='5.55 integrates dated PAA and bank profile boundaries; complete new companion outputs and both copied volumes reproduce. Whole-document and independent acceptance remain open.',
        next=['Reconcile the independently staged midpoint repair against the selected sector successor',
              f'Continue ordered protected 5.52-R2 reading at{frontier+1} with successor delta checks',
              'Trace remaining consequential executable dependencies and compatible accounting joins',
              'Continue wider source/applicability work and reconcile at the deadline'])
    for field,name in [('current_pdf','accounting-product-proposal.pdf'),('standalone_pdf','simulation-foundations.pdf')]:
        a[field]=str((T/name).relative_to(R));a[field+'_sha256']=digest(T/name)
    a.setdefault('completed_plan_evidence',{})['docs/plans/accounting-sector-interface-integration-20261027.md']=result
    a.setdefault('latest_internal_results',[]).append(result)
    for field in ['insurance_paa_dated_book','bank_interface_consolidation']:
        a[field].update(included_in_selected_manuscript_package=True,integration_result=result)
    a['manuscript_review_frontier'].update(physical_pages_read=frontier,next_page=frontier+1)
    a['timed_release_pursuit'].update(selected_successor=str(T.relative_to(R)),
        manuscript_result=result,package_result=result,
        status='active_supervised_local_work; goal tool has no entry',
        integration_note='5.55 includes the dated PAA narrative/interface and bank compatibility boundaries plus their exact internal archives.')
    new[p]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
obj=json.loads(new[paths[1]]); h=sha256(new[paths[0]].encode()).hexdigest();obj['catalog_sha256']=h
for value in obj.values():
    if isinstance(value,dict) and paths[0] in value:value[paths[0]]=h
new[paths[1]]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
summary=f'''## Current execution — 27 October 2026

Governing candidate **5.55**, 836 main pages and 264 total / 243 body
simulation pages, remains **not_ready**. Four stable PDF/TeX links select
internal package revision 1.
Main SHA256: {digest(T/'accounting-product-proposal.pdf')}.
Simulation SHA256: {digest(T/'simulation-foundations.pdf')}.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Active plan: docs/plans/accounting-release-eight-hour-20261027.md.
Current manuscript and package result: {result}.
Remaining work: {remaining}.
Acceptance index: data/accounting-master/release-plan-execution-20261027/release-acceptance.md.

The dated premium-allocation example now explains its synthetic calendar and
eight-event sequence and reaches the common book/interim-report interface.
Bank compatibility distinguishes the separate AU accounting profiles from the
existing US book-to-capital case and preserves exact-time query boundaries.
The 447-file package includes six companions. Both new archives reproduce
complete saved outputs from a fresh copy; both copied volumes reproduce all
normalized page text. All 437 source/build checks pass. Fifteen rendered-page
bindings cover the additions and adjacent transitions. The first overflow
failure and its repair are retained. These are local integration checks.

Dated PAA evidence: data/accounting-master/insurance-paa-dated-book-20261027/result.md.
Seven cases, 21 controls and 732 checks preserve complete states and reports;
70 separate identity/prefix checks remain retained evidence. Actual source,
group, chronology, accounting and posting admission remain open.
Bank evidence: data/accounting-master/bank-interface-consolidation-20261027/result.md.
Four profiles reproduce 1,659 original exchanges and 63 exact-time cases;
20,339 original checks, 42 retries and 12 added controls pass. Historical
Git/index checks remain historical workspace evidence, distinct from recipient
copied-input preservation. All four original MC21 clauses retain their scope.

Separate internal evidence remains available outside this manuscript package:
data/accounting-master/internal-evidence-companion-20261027/acceptance-supplement.md
and data/accounting-master/intragroup-evidence-replay-20261027/acceptance-supplement.md.
The former reproduces source construction and 37 downstream exchanges with
2,981 checks from 262 inputs; the latter reproduces 351 complete intragroup
exchanges from 166 inputs, preserving 28 unresolved-tax cases.

Earlier source/history, coupling, opening, EPS, edition, particle-weight and
financing repairs remain preserved. The continuous borrowing derivation and
1,428 rational financing checks still distinguish feasibility, liquidity
optimality and settlement-order shortfall. The source/history companion
retains its 37 exchanges and explicit comparison rules. All 27 mapped
literature claims have bounded dispositions. The 236 observations, 101
equations and 180 unresolved issuer obligations remain; no actual issuer
history or opening has been inferred.

The current ordered ledger for protected 5.52-R2 reaches physical page {frontier};
resume at {frontier+1}. This incorporates separately saved reading evidence.
Local successor reviews do not advance that whole-manuscript frontier.
Continue consequential dependencies, compatible joins, wider source questions
and ordered reading. The authorized pursuit ends at 15:19:56 UTC.

All 35 original MC provisions, 114 acceptance rows and 156 authored clauses
remain. The 201 failure rows are targets/evidence, not 201 executed tests.
All 53 obligations, six interactions, 46 operations and 18 packages remain
open. S1–S5 partial; S6 held; E3 deferred. Independent reader, domain and
implementation acceptance remain open. Complete feasible internal work before
focused referral; no publication, outreach or paid engagement is authorized.
Prior live control bytes are retained in this result's control-before directory.

'''
for p in paths[2:9]:
    text=before[p].decode();head,tail=text.split('Historical assessments below are preserved.',1)
    assert 'Governing candidate **5.54-R2**' in head,p
    new[p]=head.split('## Current execution',1)[0]+summary+'Historical assessments below are preserved.'+tail
p=paths[9];text=before[p].decode()
assert 'Version 5.54-R2, 835 pages' in text
text=text.replace('Version 5.54-R2, 835 pages','Version 5.55, 836 pages',1).replace('internal package revision 2','internal package revision 1',1)
text=text.replace('../data/accounting-master/release-pursuit-20261027/replay-package/result.md','../'+result,1)
text=text.replace('../data/accounting-master/release-pursuit-20261027/refinancing-domain/result.md','../'+result,1)
new[p]=text
state.update(last_update_utc=now,selected_candidate=str(T.relative_to(R)),last_reconciled_parent='5.55',
    latest_package_result=result,
    candidate_checks='437 source/build checks; 15 page bindings; 447-file package; both copied volumes and complete new sector outputs reproduce')
state['completed_units'].append(dict(id='sector-integration',result=result,status='selected_5.55_not_ready'))
for row in state['completed_units']:
    if row['id'] in ['insurance-paa-dated-book-20261027','bank-interface-consolidation-20261027']:
        row['status']='included_in_selected_5.55_package'
new[paths[10]]=json.dumps(state,indent=2)+chr(10)
new[paths[11]]=(D/'reset-memo.md').read_text()+chr(10)+f'Live reconciliation: the separately updated ordered ledger reaches physical page {frontier}. Resume at {frontier+1}. Preserve and reconcile the staged midpoint-reference repair before its selection; it was prepared against 5.54-R2 and must retain this checked sector integration. The pre-selection reset memo is preserved in control-before.'+chr(10)
new[paths[12]]=before[paths[12]].decode()+chr(10)+f'{now}: selected 5.55 after all 437 source/build checks, 15 page inspections, 447-file verification, exact copied sector replay and full copied-volume text comparisons. Separately saved ordered reading reaches {frontier}; the existing current work unit is preserved for reconciliation. Release remains not_ready.'+chr(10)
backup=D/'control-before';backup.mkdir(exist_ok=False)
for p,content in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(content)
(backup/'stable-links.json').write_text(json.dumps(link_before,indent=2)+chr(10))
assert all((R/p).read_bytes()==b for p,b in before.items())
assert all(os.readlink(R/p)==v for p,v in link_before.items())
for p,h in preserved.items():assert digest(R/p)==h
for p,text in new.items():(R/p).write_text(text)
for p,name in links.items():
    link=R/p;temp=link.with_name(link.name+'.v555-next')
    assert not temp.exists() and not temp.is_symlink()
    temp.symlink_to(os.path.relpath(T/name,link.parent));os.replace(temp,link)
    assert link.resolve()==T/name
for p,h in preserved.items():assert digest(R/p)==h
record=dict(passed=True,timestamp_utc=now,candidate='5.55',release_status='not_ready',
    controls={p:dict(before=sha256(before[p]).hexdigest(),after=digest(R/p)) for p in paths},
    links={p:dict(before=link_before[p],after=os.readlink(R/p)) for p in links},
    preserved_release_records=preserved,package_manifest_sha256=digest(T/'package-manifest.json'),
    evidence={n:digest(D/n) for n in ['verification-02.json','package-record.json','relocation-01/result.json','author-review.md','result.md']})
with (D/'advancement.json').open('x') as f:json.dump(record,f,indent=2);f.write(chr(10))
print(json.dumps(dict(passed=True,candidate='5.55',controls=len(paths),links=len(links))))
