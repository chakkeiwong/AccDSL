from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re

D=Path(__file__).resolve().parent;R=D.parents[3];M=D/'merged'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=read(M/'baseline.json');B=R/c['baseline'];T=R/c['candidate']
assert not (M/'advancement.json').exists()
for p in [M/'verification.json',M/'relocation/result.json',M/'package-record.json']:
    assert read(p)['passed']
assert len(read(M/'rendered-review.json')['pages'])==12
assert (D/'result.md').is_file() and (D/'author-review.md').is_file()
assert sha(T/'package-manifest.json')==read(M/'package-record.json')['manifest_sha256']
for row in read(T/'package-manifest.json')['files']:assert sha(T/row['path'])==row['sha256'],row['path']
for row in c['files']:assert sha(B/row['path'])==row['sha256'],row['path']
preserved=read(D.parent/'sector-integration/advancement.json')['preserved_release_records']
for p,h in preserved.items():assert sha(R/p)==h,p
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
       'data/accounting-master/next-plan.md','docs/README.md',
       'data/accounting-master/release-pursuit-20261027/state.json',
       'data/accounting-master/release-pursuit-20261027/reset-memo.md',
       'data/accounting-master/release-pursuit-20261027/progress.md']
before={p:(R/p).read_bytes() for p in paths};new={}
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf',
       'docs/AccDSL-latest.tex':'accounting-product-proposal.tex',
       'docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf',
       'docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,name in links.items():
    assert (R/p).is_symlink() and (R/p).resolve()==B/name,p
    link_before[p]=os.readlink(R/p)
now=datetime.now(timezone.utc).isoformat()
prefix=str(D.relative_to(R));result=prefix+'/result.md';remaining=prefix+'/remaining-work.md'
inventory=read(D.parent/'manuscript-review/manuscript-release-prep-v552r2-20261027-inventory.json')
segments=[r for r in inventory['read_segments'] if r['volume']=='accounting-product-proposal']
frontier=segments[-1]['pages'][-1];assert frontier>=192
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    obj=json.loads(before[p]);a=obj[key]
    assert a['current_candidate']=='5.55;836 pages;not_ready'
    assert a['current_pdf']==str((B/'accounting-product-proposal.pdf').relative_to(R))
    assert a['active_work_plan']=='docs/plans/accounting-release-eight-hour-20261027.md'
    a.update(updated=now,current_candidate='5.55-R1;837 pages;not_ready',package_revision=1,
        latest_internal_result=result,latest_manuscript_result=result,latest_package_result=result,
        current_package_record=prefix+'/merged/package-record.json',remaining_work=remaining,
        latest_reset_memo='data/accounting-master/release-pursuit-20261027/reset-memo.md',
        current_internal_status='5.55-R1 merges the exact midpoint threshold bound onto the dated sector successor; seven companions and both reproduced volumes retained. Whole-document and independent acceptance remain open.',
        next=['Reconcile original release conditions and current evidence before the15:19:56UTC deadline',
              f'Continue ordered baseline reading at{frontier+1} when compatible with final reconciliation',
              'Keep full source, company/sector composition, dependency and independent acceptance gaps explicit'])
    for field,name in [('current_pdf','accounting-product-proposal.pdf'),('standalone_pdf','simulation-foundations.pdf')]:
        a[field]=str((T/name).relative_to(R));a[field+'_sha256']=sha(T/name)
    a.setdefault('completed_plan_evidence',{})['docs/plans/accounting-midpoint-reference-20261027.md']=result
    a.setdefault('latest_internal_results',[]).append(result)
    a['manuscript_review_frontier'].update(physical_pages_read=frontier,next_page=frontier+1)
    a['timed_release_pursuit'].update(selected_successor=str(T.relative_to(R)),manuscript_result=result,
        package_result=result,status='active_supervised_local_work; final reconciliation pending',
        integration_note='5.55-R1 preserves all sector additions and six earlier companions, adding the exact midpoint-bound repair and seventh companion.')
    new[p]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
obj=json.loads(new[paths[1]]);h=hashlib.sha256(new[paths[0]].encode()).hexdigest();obj['catalog_sha256']=h
for value in obj.values():
    if isinstance(value,dict) and paths[0] in value:value[paths[0]]=h
new[paths[1]]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
for p in paths[2:9]:
    s=before[p].decode();head,tail=s.split('Historical assessments below are preserved.',1)
    assert 'Governing candidate **5.55**, 836 main pages and 264 total / 243 body' in head,p
    head=head.replace('Governing candidate **5.55**, 836 main pages and 264 total / 243 body',
                      'Governing candidate **5.55-R1**, 837 main pages and 265 total / 244 body',1)
    for name in ['accounting-product-proposal','simulation-foundations']:
        head=head.replace(sha(B/(name+'.pdf')),sha(T/(name+'.pdf')))
    head=head.replace('data/accounting-master/release-pursuit-20261027/sector-integration/result.md',result,1)
    head=head.replace('data/accounting-master/release-pursuit-20261027/sector-integration/remaining-work.md',remaining,1)
    marker='The dated premium-allocation example now explains'
    added='''The numerical reference chapter now proves the uniform midpoint threshold
error bound and explicitly shows that a finer grid can have greater error.
All169 retained arithmetic checks and6,552 rational boundary cases reproduce
from a copied companion. The452-file package retains all six predecessor
companions and adds that seventh component. All460 source/build checks pass;
12 rendered-page bindings cover the complete repaired chapter and affected
pages. Both merged volumes reproduce every normalized page text from a separate
copy without original-worktree TeX inputs. These remain bounded checks.

The preserved5.55 sector integration supplied the following evidence.
'''
    assert marker in head;head=head.replace(marker,added+marker,1)
    head=head.replace('The 447-file package includes six companions. Both new archives reproduce',
        'The preceding447-file package included six companions. Both sector archives reproduce',1)
    head=head.replace('All 437 source/build checks pass. Fifteen rendered-page',
        'Its437 source/build checks pass. Fifteen predecessor rendered-page',1)
    head=re.sub(r'reaches physical page [0-9]+;\nresume at [0-9]+\.',f'reaches physical page {frontier};'+chr(10)+f'resume at {frontier+1}.',head)
    new[p]=head+'Historical assessments below are preserved.'+tail
p=paths[9];s=before[p].decode();assert 'Version 5.55, 836 pages' in s
s=s.replace('Version 5.55, 836 pages','Version 5.55-R1, 837 pages',1).replace('**264 pages**','**265 pages**',1).replace('**243 body pages**','**244 body pages**',1)
s=s.replace('../data/accounting-master/release-pursuit-20261027/sector-integration/result.md','../'+result,2)
new[p]=s
state=json.loads(before[paths[10]])
assert state['ordered_read_pages']<=frontier
state['ordered_read_pages']=frontier
state.update(last_update_utc=now,selected_candidate=str(T.relative_to(R)),last_reconciled_parent='5.55',
    latest_package_result=result,candidate_checks='460 source/build checks;12 page bindings;452-file package; both copied documents and complete numerical companion reproduce',
    current_unit='Final timed release reconciliation against original conditions',
    next_check='Confirm stable package, original acceptance preservation and precise unfinished C0–C7 work')
assert not any(x['id']=='midpoint-reference' for x in state['completed_units'])
state['completed_units'].append({'id':'midpoint-reference','result':result,'status':'selected_5.55-R1_not_ready'})
new[paths[10]]=json.dumps(state,indent=2,ensure_ascii=False)+chr(10)
new[paths[11]]=f'''# Final reconciliation of the authorized release pursuit

Window:27 October2026 07:19:56–15:19:56UTC. The eight-hour plan remains active;
release remains not_ready. Selected5.55-R1 merges the midpoint bound/companion
onto5.55 without losing dated PAA or bank work. Main837 pages; simulation265
total/244 body. All460 source/build checks,12 page bindings and452 package
files pass. Both volumes and exact numerical companion reproduce from a copied
package. Six predecessor companions are byte-identical to their checked versions.

Current result: midpoint-reference/result.md. Guarded selection and copied
reproduction: midpoint-reference/merged/advancement.json and relocation/result.json.
Do not rerun completed prepare, merge, package, build, verification or advancement
writers. The earlier5.54-R3 branch is retained, unselected, with main-only copied
build evidence. Original baselines and pre-extension plan hashes stay historical.

Ordered reading of protected5.52-R2 reaches{frontier}. Resume{frontier+1} with the exit state
from manuscript-review/{segments[-1]['id']}.json. Local successor chapter reviews do
not establish whole-document coverage; all node/equation and independent
acceptance obligations remain. The consolidated inventory is not regenerated.

Continue final reconciliation through15:19:56UTC: exact stable-link identities,
full original acceptance wording, latest supplemental evidence, and remaining
internal/independent tasks. Preserve all concurrent work and frozen acceptance.
Read midpoint-reference/remaining-work.md and sector-integration/result.md.
Original 35 MC provisions,114 rows and156 clauses remain;53 obligations,
six interactions,46 operations and18 packages are open. S1–S5 partial,S6 held,
E3 deferred. No actual issuer history/opening, broad compliance, empirical
accuracy or accepted release has been established. No subagents,outreach,fees,
publication,installation,GPU work or legacy controller. Record the honest final
decision at the deadline rather than treating elapsed time as acceptance.
'''
new[paths[12]]=before[paths[12]].decode()+f'\n{now}: selected5.55-R1 after merging the exact midpoint repair into current5.55. All460 source/build checks,452-file package,12 rendered-page bindings and both copied-document reproductions pass. Six preceding companions retained exactly; seventh numerical companion reproduces169 original checks and6,552 rational cases. Original acceptance remains unchanged; final timed reconciliation continues.\n'
backup=M/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(backup/'stable-links.json').write_text(json.dumps(link_before,indent=2)+chr(10))
assert all((R/p).read_bytes()==b for p,b in before.items())
assert all(os.readlink(R/p)==s for p,s in link_before.items())
assert all(sha(R/p)==h for p,h in preserved.items())
for p,s in new.items():(R/p).write_text(s)
for p,name in links.items():
    q=R/p;tmp=q.with_name(q.name+'.midpoint-next');assert not tmp.exists() and not tmp.is_symlink()
    tmp.symlink_to(os.path.relpath(T/name,q.parent));os.replace(tmp,q)
assert all((R/p).read_text()==s for p,s in new.items())
assert all((R/p).resolve()==T/name for p,name in links.items())
assert all(sha(R/p)==h for p,h in preserved.items())
record={'passed':True,'timestamp_utc':now,'candidate':'5.55-R1','release_status':'not_ready',
    'controls':[{'path':p,'before':hashlib.sha256(before[p]).hexdigest(),'after':sha(R/p)} for p in paths],
    'links':{p:{'before':link_before[p],'after':os.readlink(R/p),'sha256':sha(R/p)} for p in links},
    'preserved_release_records':preserved,'package_manifest_sha256':sha(T/'package-manifest.json'),
    'evidence':{str(p.relative_to(R)):sha(p) for p in [M/'verification.json',M/'package-record.json',M/'relocation/result.json',M/'rendered-review.json',D/'result.md',D/'remaining-work.md']}}
(M/'advancement.json').write_text(json.dumps(record,indent=2)+chr(10))
print(json.dumps({'passed':True,'candidate':'5.55-R1','controls':len(paths),'links':len(links),'release_status':'not_ready'}))
