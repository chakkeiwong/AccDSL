"""Guarded master advancement; retain all independent live execution fields."""
from pathlib import Path
from hashlib import sha256
import copy,json,os
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'edition-date-repair-02'
G=H.parent/'gap-control-history-refresh-20261027'
def j(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def put(p,text):
    q=p.with_name(p.name+'.control-authority.tmp');assert not q.exists()
    q.write_text(text);os.replace(q,p)
assert not (H/'advancement.json').exists()
v=j(D/'verification.json');assert v['status']=='PASS'
assert (H/'result.md').exists() and (H/'author-review.md').exists()
lock=j(D/'source-preservation.json');S=R/lock['source'];T=R/lock['target']
main,sim=v['documents'];gv=j(G/'verification.json');assert gv['status']=='PASS'
for n,h in lock['sources'].items():assert digest(S/n)==h
for n,h in lock['evidence'].items():assert digest(R/n)==h
for d in v['documents']:assert digest(T/(d['document']+'.pdf'))==d['sha256']
links={'docs/AccDSL-latest.pdf':'accounting-product-proposal.pdf','docs/AccDSL-latest.tex':'accounting-product-proposal.tex','docs/AccDSL-simulation-foundations.pdf':'simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex':'simulation-foundations.tex'}
for p,f in links.items():assert (R/p).resolve()==S/f
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths}
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
assert cat['active_execution_note']['current_candidate'].startswith('5.25;')
assert cat['active_execution_note']['current_pdf']==str((S/'accounting-product-proposal.pdf').relative_to(R))
assert np['active_execution']['current_candidate']==cat['active_execution_note']['current_candidate']
finance='docs/plans/accounting-control-group-boundary-20261027.md'
independent=cat['active_execution_note']['compression_next_plan']
assert (R/finance).exists() and (R/independent).exists()
assert cat['active_execution_note']['active_work_plan']=='docs/plans/accounting-control-history-contract-20261026.md'
backup=H/'control-before';backup.mkdir(exist_ok=False)
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R));original=[copy.deepcopy(cat),copy.deepcopy(np)]
updates=dict(updated='2026-10-27',current_candidate=f"5.26;{main['pages']} pages;not_ready",latest_result=result,
 current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=main['sha256'],
 standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=sim['sha256'],
 current_program='docs/plans/accounting-control-authority-rebase-20261027.md',current_audit=base+'/audit-status.json',
 remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',
 full_gap_plan='docs/plans/accounting-control-authority-rebase-20261027.md',full_gap_program=base+'/closure-program.md',
 closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',
 latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',
 gap_program_verification=base+'/verification.json',gap_program_trace_counts=gv['counts'],
 active_work_plan=finance,financing_next_plan=finance,active_work_plans=[finance,independent],
 latest_financing_result='data/accounting-master/control-history-contract-20261026/result.md',
 control_history_result='data/accounting-master/control-history-contract-20261026/result.md',
 current_internal_status='Version5.26 preserves source-policy work and integrates funding/measurement and conditional interval control. Group-method binding, actual admission and dated acquisition authority remain open.')
for d in [cat['active_execution_note'],np['active_execution']]:
    d.update(updates)
    d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[updates['control_history_result']]))
    d['next']=['Execute '+finance,'Continue '+independent,'Continue all18 broad packages using their specific closure evidence']
    d['gap_program_next']=['Bind conditional control history to the current group-report scope','Complete dated acquisition-period authority and measurement','Continue the independent source-time plan and general-domain/recovery/acceptance work']
text=f'''# Current AccDSL master program

Updated27 October2026. Governing candidate **5.26**, {main['pages']} main pages, not_ready.
Simulation: **{sim['pages']} total / {sim['body_pages']} body pages**,26 chapters.
Both PDF/TeX pairs select {lock['target']}/.
Result: {result}.
Main SHA256: {main['sha256']}.
Simulation SHA256: {sim['sha256']}.

The5.25 source-policy work is preserved. Funding affordability, economic pricing,
issuer/holder measurement and conditional whole-interval control evidence are
integrated. The interval reference passes22 cases,14 controls and214 assertions;
the repaired dependency reference passes30 cases,23 controls and295 assertions.
Neither admits actual control, measurement, journals or complete group reports.

Active financing plan: {finance}.
Independent plan: {independent}.
Authority dependency: docs/plans/accounting-acquisition-period-authority-20261026.md.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All53 obligations, six interactions,46 operations, nine literature gaps and
18 packages remain open. S1–S5 partial; S6 held; E3 deferred. Independent reader,
domain and whole-document acceptance remain pending. Continue feasible internal
work. Preserve successful writers, predecessor sources and failed diagnostics.
No fees, outreach, publication or background campaign is authorized.
Protected pre-advancement controls: {str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Current routes — 27 October2026, Version5.26

Concise recovery: docs/plans/accounting-master-current.md.
Version5.26: {main['pages']} main pages; {sim['pages']} total/{sim['body_pages']} body simulation pages; not_ready.
Funding/measurement and conditional control-history arguments are integrated;
the5.25 source-policy work remains intact. No actual accounting admission follows.
Result: {result}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Active financing plan: {finance}.
Independent plan: {independent}.
All53 obligations, six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Earlier entries remain historical evidence.

'''
for p in paths[4:9]:title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode()
for old,value in [('Version 5.25, 777 pages',f"Version 5.26, {main['pages']} pages"),('**211 pages**',f"**{sim['pages']} pages**"),('**192 body pages**',f"**{sim['body_pages']} body pages**"),('gap-source-policy-refresh-20261027/remaining-work.md','gap-control-history-refresh-20261027/remaining-work.md'),('source-policy-integration-20261027/result.md','control-authority-rebase-20261027/result.md')]:
    assert old in s,old;s=s.replace(old,value)
s=s.replace('- [Source revision and actor views]','- [Conditional whole-interval control history](../data/accounting-master/control-history-contract-20261026/result.md).\n- [Source revision and actor views]')
new['docs/README.md']=s
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,f in links.items():assert (R/p).resolve()==S/f
for p,s in new.items():put(R/p,s)
for p,f in links.items():
    target=R/p;temporary=target.with_name(target.name+'.control-authority-link')
    assert not temporary.exists();temporary.symlink_to(os.path.relpath(T/f,target.parent));os.replace(temporary,target)
checks=[]
def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
for d,key,old in [(cat,'active_execution_note',original[0]),(np,'active_execution',original[1])]:
    ck('legacy_fields',{k:v for k,v in d.items() if k!=key}=={k:v for k,v in old.items() if k!=key})
    ck('independent_plan',d[key]['compression_next_plan']==old[key]['compression_next_plan'])
    ck('unrelated_active_fields',all(d[key][k]==v for k,v in old[key].items() if k not in set(updates)|{'latest_internal_results','next','gap_program_next'}))
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,f in links.items():ck('link:'+p,(R/p).resolve()==T/f)
for n,h in lock['sources'].items():ck('source:'+n,digest(S/n)==h)
for n,h in lock['evidence'].items():ck('evidence:'+n,digest(R/n)==h)
for n,h in j(G/'predecessor-lock.json').items():ck('predecessor_gap:'+n,digest(R/n)==h)
for d in v['documents']:ck('pdf:'+d['document'],digest(T/(d['document']+'.pdf'))==d['sha256'])
ck('all_packages_open',all(p['status']=='open' for p in j(G/'closure-packages.json')['packages']))
(H/'advancement.json').write_text(json.dumps(dict(status='PASS',candidate='5.26',checks=len(checks),results=checks,finance=finance,independent=independent,readiness='independent_reader_pending',mission_complete=False),indent=2)+'\n')
print(json.dumps(dict(status='PASS',candidate='5.26',checks=len(checks),main_pages=main['pages'],simulation_pages=sim['pages'],finance=finance,independent=independent)))
