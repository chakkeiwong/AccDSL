"""Guardedly select the verified document, preserving concurrent evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R / 'docs/design/proposal/manuscript-filter-v554r1-20261027'
T = R / 'docs/design/proposal/manuscript-financing-v554r2-20261027'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

assert not (D/'advancement.json').exists()
v = read(D/'candidate-verification-02.json')
assert v['passed'] and all(x['passed'] for x in v['checks'])
for name in ['checks.json','companion-reproduction.json','relocation-01/result.json']:
    assert read(D/name)['passed']
assert sha(T/'package-manifest.json') == read(D/'package-record.json')['manifest_sha256']
for row in read(T/'package-manifest.json')['files']:
    p=T/row['path']; assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
for row in read(D/'candidate-baseline.json')['files']:
    assert sha(B/row['path'])==row['sha256']
for row in read(D/'rendered-review.json')['pages']:
    assert row['review']=='author_viewed'
    assert sha(T/(row['volume']+'.pdf'))==row['pdf_sha256']
    assert sha(R/row['path'])==row['image_sha256']
for name in ['result.md','author-review.md','remaining-work.md','integration-manifest.json']:
    assert (D/name).stat().st_size>500

paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
       'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
       'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
       'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-current.md',
       'data/accounting-master/next-plan.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths}
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf',
       'docs/AccDSL-latest.tex':'accounting-product-proposal.tex',
       'docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf',
       'docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
link_before={}
for p,name in links.items():
    assert (R/p).is_symlink() and (R/p).resolve()==B/name
    link_before[p]=os.readlink(R/p)
preserve=['data/accounting-master/state.json',
          'data/accounting-master/release-plan-execution-20261027/release-acceptance.json',
          'data/accounting-master/release-plan-execution-20261027/acceptance-clauses.json',
          'data/accounting-master/release-plan-execution-20261027/current-claim-map.json',
          'data/accounting-master/release-plan-execution-20261027/citation-source-index.json',
          'data/accounting-master/remaining-claim-review-20261027/current-claim-ledger.json',
          'data/accounting-master/executable-evidence-closure-20261027/result.md',
          'data/accounting-master/executable-evidence-closure-20261027/preparation-04/bundle-manifest.json']
preserved={p:sha(R/p) for p in preserve}
new={}; plan='docs/plans/accounting-release-eight-hour-20261027.md'
unit='docs/plans/accounting-refinancing-action-domain-20261027.md'
result=str((D/'result.md').relative_to(R)); remaining=str((D/'remaining-work.md').relative_to(R))
technical=[]
for p,key in [(paths[0],'active_execution_note'),(paths[1],'active_execution')]:
    data=json.loads(before[p]);active=data[key]
    assert active['current_candidate']=='5.54-R1;834 pages;not_ready'
    assert active['active_work_plan']==unit
    for field in ['current_pdf','standalone_pdf']:
        assert sha(R/active[field])==active[field+'_sha256']
    technical.append(active['latest_internal_result'])
    active.update(current_candidate='5.54-R2;835 pages;not_ready',
        current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),
        current_pdf_sha256=v['volumes'][0]['sha256'],
        standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),
        standalone_pdf_sha256=v['volumes'][1]['sha256'],
        current_package_record=str((D/'package-record.json').relative_to(R)),
        latest_manuscript_result=result,refinancing_domain_result=result,
        current_internal_status='5.54-R2 selected provisionally; financing domain, local chapter regression, portable example and document reproduction checked. Whole-document and independent acceptance remain open.',
        manuscript_review_frontier={'baseline':'5.52-R2','physical_pages_read':150,'next_page':151,
            'status':'partial_author_read; node and independent acceptance open'},
        active_work_plan=plan,full_gap_plan=plan,remaining_work=remaining,
        next=['Continue ordered baseline reading at151 with current-candidate delta checks',
              'Include the retained executable replay component in a protected package',
              'Continue C2/C4 source/history/accounting and wider C3 residuals'])
    active.setdefault('completed_plan_evidence',{})[unit]=result
    if unit in active.get('active_work_plans',[]):active['active_work_plans'].remove(unit)
    if plan not in active.setdefault('active_work_plans',[]):active['active_work_plans'].append(plan)
    pursuit=active.get('timed_release_pursuit',{})
    pursuit.update(selected_successor=str(T.relative_to(R)),manuscript_result=result,
        status='active_supervised_local_work; earlier goal tool remains blocked',
        integration_note='Financing action domain and portable example selected; latest source and executable replay results preserved.')
    active['timed_release_pursuit']=pursuit
    active.setdefault('latest_internal_results',[]).append(result)
    new[p]=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
assert len(set(technical))==1
body=f'''## Current execution — 27 October 2026

Governing candidate **5.54-R2**, 835 main pages and 264 total / 243 body
simulation pages, remains **not_ready**. Four stable PDF/TeX links select it.
Main SHA256: {v['volumes'][0]['sha256']}.
Simulation SHA256: {v['volumes'][1]['sha256']}.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Active plan: {plan}.
Current manuscript result: {result}.
Latest technical result: {technical[0]}.
Remaining work: {remaining}.
Acceptance index: data/accounting-master/release-plan-execution-20261027/release-acceptance.md.

Section 14.13 now retains continuous borrowing amounts within discrete sale
choices. Its cash identities and two counterexamples distinguish a feasible
funding witness, a liquidity optimum and a settlement-order shortfall.
The exact reference checks 1,428 rational cases; the continuous domain follows
from the written derivation. The copied companion reproduces every trace.
All 428 source/build checks pass; 17 rendered-page bindings cover the repaired
chapter and affected pages. The 414-file package verifies and both volumes
reproduce all normalized page text from a separate copy. Earlier source/history,
coupling, opening, EPS, edition and particle-weight repairs remain preserved.

The separate 234-file executable component reproduces 37 source/history/opening/
report exchanges with 1,667 checks. Its accepted timing/certificate/conflict-set
comparison rules remain explicit. It is not yet included in this document
package. All 27 mapped literature claims have bounded current dispositions.
The 236 observations, 101 equations and 180 unresolved issuer obligations remain;
no actual issuer history or opening is inferred.

Ordered reading of the protected 5.52-R2 main volume reaches physical page150;
resume at151. Local successor regressions do not imply whole-book acceptance.
Continue the executable inclusion, compatible joins, wider source questions and
ordered manuscript work. The authorized pursuit ends at15:19:56UTC.

All 35 original MC provisions,114 acceptance rows and156 authored clauses are
retained. The201 failure rows are targets/evidence, not201 executed tests. All53
obligations,six interactions,46 operations and18 packages remain open. S1–S5
partial; S6 held; E3 deferred. Complete feasible internal work before focused
external referral. No publication,outreach or paid engagement is authorized.
Prior live control bytes are retained in this result's control-before directory.

'''
for p in paths[2:-1]:
    s=before[p].decode();title=s.split('\n\n',1)[0]
    head,tail=s.split('Historical assessments below are preserved.',1)
    assert 'Governing candidate **5.54-R1**' in head
    new[p]=title+'\n\n'+body+'Historical assessments below are preserved.'+tail
p=paths[-1];s=before[p].decode()
assert s.count('**Version 5.54-R1, 834 pages**')==1
s=s.replace('**Version 5.54-R1, 834 pages**','**Version 5.54-R2, 835 pages**')
s=s.replace('**263 pages**','**264 pages**').replace('**242 body pages**','**243 body pages**')
s=s.replace('release-pursuit-20261027/filter-convention/result.md','release-pursuit-20261027/refinancing-domain/result.md')
new[p]=s
backup=D/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():
    q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
dump(backup/'stable-links.json',link_before)
assert all((R/p).read_bytes()==b for p,b in before.items())
assert all(os.readlink(R/p)==s for p,s in link_before.items())
assert all(sha(R/p)==h for p,h in preserved.items())
for p,s in new.items():(R/p).write_text(s)
for p,name in links.items():
    link=R/p;tmp=link.with_name(link.name+'.v554r2-next')
    assert not tmp.exists() and not tmp.is_symlink()
    tmp.symlink_to(os.path.relpath(T/name,link.parent));os.replace(tmp,link)
    assert link.resolve()==T/name
assert all(sha(R/p)==h for p,h in preserved.items())
dump(D/'advancement.json',{'passed':True,'candidate':'5.54-R2;835 pages;not_ready',
    'timestamp_utc':datetime.now(timezone.utc).isoformat(),'next_plan':plan,
    'preserved_technical_result':technical[0],
    'controls':[{'path':p,'before':hashlib.sha256(before[p]).hexdigest(),'after':sha(R/p)} for p in paths],
    'links':{p:{'before':link_before[p],'after':os.readlink(R/p)} for p in links},
    'preserved_release_records':preserved,
    'evidence':{n:sha(D/n) for n in ['candidate-verification-02.json','package-record.json',
        'relocation-01/result.json','companion-reproduction.json','author-review.md','result.md']}})
print(json.dumps({'passed':True,'candidate':'5.54-R2;not_ready','controls':len(paths),'links':4}))
