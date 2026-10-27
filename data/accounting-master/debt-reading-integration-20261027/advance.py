"""Select the checked candidate while preserving concurrent release records."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, os
import integrate as base
import layout_repair as layout

H,R,S,T=base.H,base.R,base.S,base.T
read,sha,dump=base.read,base.sha,base.dump
assert not (H/'advancement.json').exists()
v=read(H/'verification-03/verification.json')
assert v['passed'] and all(c['passed'] for c in v['checks'])
assert read(H/'relocation-01/result.json')['passed']
record=read(H/'package-record.json')
assert sha(T/'package-manifest.json')==record['manifest_sha256']
package=read(T/'package-manifest.json')
assert len(package['files'])==409
for row in package['files']:
    p=T/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
lock=read(H/'source-lock.json')
for n,h in lock['sources'].items():
    assert sha(S/n)==h
    if n=='README.md':assert sha(T/n)==read(H/'package-source-delta.json')['after_sha256']
    elif (S/n).suffix in ['.tex','.md']:assert (T/n).read_text()==layout.transform(n,(S/n).read_text())
    else:assert sha(T/n)==h
for k,root in [('pdfs',S),('evidence',R),('inputs',H)]:
    for n,h in lock[k].items():assert sha(root/n)==h
for d in v['documents']:assert sha(T/(d['document']+'.pdf'))==d['sha256']
for n in ['author-review.md','result.md','reset-memo.md']:assert (H/n).stat().st_size>500
plan='docs/plans/accounting-consequential-source-review-20261027.md'
old_plan='docs/plans/accounting-debt-reading-integration-20261027.md'
assert (R/plan).is_file()
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','MISSION_CONTROL.md',
       'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md',
       'docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
       'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md']
before={p:(R/p).read_bytes() for p in paths};new={}
evidence_paths=['release-acceptance.json','acceptance-clauses.json','current-claim-map.json','citation-source-index.json']
preserved={str((base.B/'release-plan-execution-20261027'/n).relative_to(R)):sha(base.B/'release-plan-execution-20261027'/n) for n in evidence_paths}
for p in paths[:2]:
    d=json.loads(before[p]);o=d['active_execution_note'] if p==paths[0] else d['active_execution']
    assert o['current_candidate']=='5.52-R1;830 pages;not_ready' and o['active_work_plan']==old_plan
    for key in ['current_pdf','standalone_pdf']:assert sha(R/o[key])==o[key+'_sha256']
    o.update(current_candidate='5.53;831 pages;not_ready',current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),
        current_pdf_sha256=v['documents'][0]['sha256'],standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),
        standalone_pdf_sha256=v['documents'][1]['sha256'],active_work_plan=plan,
        active_work_plans=[plan,o['financing_next_plan']],compression_next_plan=plan,full_gap_plan=plan,
        latest_internal_result=str((H/'result.md').relative_to(R)),debt_reading_integration_result=str((H/'result.md').relative_to(R)),
        current_package_record=str((H/'package-record.json').relative_to(R)),
        next=['Review the27 current consequential claims against retained technical sources and exact assumptions',
              'Complete remaining C2/C4 joins and release dependency closure',
              'Preserve whole-document and independent acceptance; S6 held and E3 deferred'])
    o.setdefault('completed_plan_evidence',{})[old_plan]=str((H/'result.md').relative_to(R))
    new[p]=json.dumps(d,indent=2,ensure_ascii=False)+'\n'
for p in paths[2:]:
    text=before[p].decode()
    head,tail=text.split('Historical assessments below are preserved.',1)
    head=base.once(head,'Governing candidate **5.52-R1**, 830 main pages','Governing candidate **5.53**, 831 main pages')
    head=base.once(head,'90f5db653e596471d467ca14e8195b0a1f0e3af6081690de840baf41c91bc037',v['documents'][0]['sha256'])
    head=base.once(head,'970e21636dd7047109829f564b39aa3640604c9cc9a9df1674de1d7abec6e896',v['documents'][1]['sha256'])
    head=base.once(head,'Active plan: '+old_plan+'.','Active plan: '+plan+'.')
    head=base.once(head,'Current result: data/accounting-master/release-plan-execution-20261027/result.md.',
        'Current result: data/accounting-master/debt-reading-integration-20261027/result.md.\nRelease-plan review: data/accounting-master/release-plan-execution-20261027/result.md.')
    head=base.once(head,'The\nsuccessor preserves 5.52, repairs stale profile descriptions, supplies exact',
        'The\nR1 predecessor preserved 5.52, repaired stale profile descriptions, supplied exact')
    head=base.once(head,'references and two scoped companions, and passes source/build/relocation checks.',
        'references and two scoped companions, and passed source/build/relocation checks.')
    head=base.once(head,'The declared 409-file package is verified. All 17 changed-text pages were viewed;',
        'The declared 409-file package is retained. R1\'s 17 changed-text pages were viewed;')
    head+='\n5.53 adds the separate source reading and complete conditional network result.\nAll 1,414 integration checks pass; twenty pages received bounded author review.\nBoth relocated volumes match all page text, with no hidden worktree inputs.\nThe 409-file package verifies; its full executable evidence closure remains open.\nContinue the current claim/source review; original broad acceptance is unchanged.\n'
    new[p]=head+'Historical assessments below are preserved.'+tail
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex',
       'docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,n in links.items():
    q=R/p;assert q.is_symlink() and q.resolve()==S/n
    link_before[p]=os.readlink(q)
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
dump(backup/'stable-links.json',link_before)
assert all((R/p).read_bytes()==b for p,b in before.items())
assert all(sha(R/p)==h for p,h in preserved.items())
for p,s in new.items():(R/p).write_text(s)
for p,n in links.items():
    q=R/p;tmp=q.with_name(q.name+'.v553-next')
    assert not tmp.exists() and not tmp.is_symlink()
    tmp.symlink_to(os.path.relpath(T/n,q.parent));os.replace(tmp,q)
    assert q.resolve()==T/n
for p in paths[:2]:
    d=read(R/p);o=d['active_execution_note'] if p==paths[0] else d['active_execution']
    assert o['current_candidate']=='5.53;831 pages;not_ready' and o['active_work_plan']==plan
assert all(sha(R/p)==h for p,h in preserved.items())
dump(H/'advancement.json',dict(passed=True,candidate='5.53;831 pages;not_ready',next_plan=plan,
     timestamp_utc=datetime.now(timezone.utc).isoformat(),
     controls=[dict(path=p,before=sha256(before[p]).hexdigest(),after=sha(R/p)) for p in paths],
     links={p:dict(before=link_before[p],after=os.readlink(R/p)) for p in links},
     preserved_release_records=preserved,evidence={n:sha(H/n) for n in ['verification-03/verification.json',
     'package-record.json','relocation-01/result.json','author-review.md','result.md','reset-memo.md']}))
print(json.dumps(dict(passed=True,controls=len(paths),links=len(links),candidate='5.53;831 pages;not_ready',next_plan=plan)))
