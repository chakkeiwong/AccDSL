"""Select the checked package revision without changing manuscript identity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

D=Path(__file__).resolve().parent
R=D.parents[3]
B=R/'docs/design/proposal/manuscript-financing-v554r2-20261027'
T=R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert not (D/'advancement.json').exists()
assert read(D/'verification.json')['passed']
assert read(D/'extract-existing-refusal.json')['passed']
assert sha(T/'package-manifest.json')==read(D/'package-record.json')['manifest_sha256']
for row in read(T/'package-manifest.json')['files']:assert sha(T/row['path'])==row['sha256']
for row in read(D/'baseline.json')['baseline_files']:assert sha(B/row['path'])==row['sha256']
for p,h in read(D/'baseline.json')['sources'].items():assert sha(R/p)==h
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
       'data/accounting-master/next-plan.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths};new={}
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf',
       'docs/AccDSL-latest.tex':'accounting-product-proposal.tex',
       'docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf',
       'docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,name in links.items():
    assert (R/p).resolve()==B/name and sha(B/name)==sha(T/name)
    link_before[p]=os.readlink(R/p)
preserved=read(D.parent/'refinancing-domain/advancement.json')['preserved_release_records']
assert all(sha(R/p)==h for p,h in preserved.items())
result=str((D/'result.md').relative_to(R));remaining=str((D/'remaining-work.md').relative_to(R))
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    data=json.loads(before[p]);a=data[key]
    assert a['current_candidate']=='5.54-R2;835 pages;not_ready'
    assert a['active_work_plan']=='docs/plans/accounting-release-eight-hour-20261027.md'
    assert a['current_pdf']==str((B/'accounting-product-proposal.pdf').relative_to(R))
    for field,name in [('current_pdf','accounting-product-proposal.pdf'),('standalone_pdf','simulation-foundations.pdf')]:
        assert a[field+'_sha256']==sha(T/name)
        a[field]=str((T/name).relative_to(R))
    a.update(package_revision=2,current_package_record=str((D/'package-record.json').relative_to(R)),
             latest_package_result=result,remaining_work=remaining,
             current_internal_status='5.54-R2 package revision2 selected; all manuscript bytes preserved and bundled source/history/opening/report replay checked. Whole-document and independent acceptance remain open.',
             next=['Continue ordered baseline reading at163 with successor delta checks',
                   'Trace remaining consequential executable dependencies and C2/C4 joins',
                   'Continue wider C3 source and accounting applicability work'])
    a['manuscript_review_frontier'].update(physical_pages_read=162,next_page=163)
    a.setdefault('completed_plan_evidence',{})['docs/plans/accounting-replay-package-inclusion-20261027.md']=result
    a.setdefault('latest_internal_results',[]).append(result)
    a['timed_release_pursuit'].update(selected_successor=str(T.relative_to(R)),package_result=result,
        integration_note='Package revision2 includes the exact 37-exchange replay component; manuscript edition and bytes unchanged.')
    new[p]=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
old_remaining='data/accounting-master/release-pursuit-20261027/refinancing-domain/remaining-work.md'
for p in paths[2:-1]:
    s=before[p].decode();head,tail=s.split('Historical assessments below are preserved.',1)
    assert 'Governing candidate **5.54-R2**' in head and 'The 414-file package verifies' in head
    head=head.replace('Four stable PDF/TeX links select it.','Four stable PDF/TeX links select internal package revision 2; manuscript bytes are unchanged.')
    head=head.replace(old_remaining,remaining)
    head=head.replace('The 414-file package verifies','The 423-file package verifies')
    head=head.replace('It is not yet included in this document\npackage.','It is now included by exact archive identity; the copied package reproduces\nall 37 exchanges under those same comparison rules.')
    head=head.replace('physical page150;\nresume at151.','physical page162;\nresume at163.')
    head=head.replace('Continue the executable inclusion, compatible joins, wider source questions and','Continue consequential executable dependencies, compatible joins, wider source questions and')
    head=head.replace('Current manuscript result:',f'Current package result: {result}.\nCurrent manuscript result:',1)
    new[p]=head+'Historical assessments below are preserved.'+tail
p=paths[-1];s=before[p].decode()
s=s.replace('dated 27 October 2026. Its','dated 27 October 2026, in internal package revision 2. Its',1)
s=s.replace('- [Current integration and checks](../data/accounting-master/release-pursuit-20261027/refinancing-domain/result.md).',
    '- [Current package and replay checks](../data/accounting-master/release-pursuit-20261027/replay-package/result.md).\n- [Current manuscript repair and checks](../data/accounting-master/release-pursuit-20261027/refinancing-domain/result.md).')
new[p]=s
backup=D/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(backup/'stable-links.json').write_text(json.dumps(link_before,indent=2)+'\n')
assert all((R/p).read_bytes()==b for p,b in before.items())
assert all(os.readlink(R/p)==s for p,s in link_before.items())
assert all(sha(R/p)==h for p,h in preserved.items())
for p,s in new.items():(R/p).write_text(s)
for p,name in links.items():
    link=R/p;temp=link.with_name(link.name+'.package2-next')
    assert not temp.exists() and not temp.is_symlink()
    temp.symlink_to(os.path.relpath(T/name,link.parent));os.replace(temp,link)
    assert link.resolve()==T/name
assert all(sha(R/p)==h for p,h in preserved.items())
report={'passed':True,'manuscript':'5.54-R2','package_revision':2,'release_status':'not_ready',
    'timestamp_utc':datetime.now(timezone.utc).isoformat(),
    'controls':[{'path':p,'before':hashlib.sha256(before[p]).hexdigest(),'after':sha(R/p)} for p in paths],
    'links':{p:{'before':link_before[p],'after':os.readlink(R/p)} for p in links},
    'preserved_release_records':preserved,
    'package_manifest_sha256':sha(T/'package-manifest.json'),
    'evidence':{n:sha(D/n) for n in ['package-record.json','verification.json','result.md','replay-command.json']}}
(D/'advancement.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'manuscript':'5.54-R2','package_revision':2,'controls':len(paths),'links':4}))
