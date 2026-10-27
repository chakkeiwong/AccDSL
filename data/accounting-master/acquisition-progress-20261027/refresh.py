"""Credit verified companions, preserving live editions and independent work."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,os
H=Path(__file__).resolve().parent; R=H.parents[2]
G=H.parent/'gap-acquisition-authority-refresh-20261027'
PLAN='docs/plans/accounting-acquisition-symbolic-20261027.md'
AUTH='data/accounting-master/acquisition-period-authority-20261026'
GROUP='data/accounting-master/control-group-boundary-20261027'
def j(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def put(p,s):
    t=p.with_name(p.name+'.acquisition-progress.tmp');assert not t.exists()
    t.write_text(s);os.replace(t,p)
assert not (H/'advancement.json').exists()
assert j(R/AUTH/'verification-attempt-03/verification.json')['status']=='PASS'
assert j(R/GROUP/'attempt-02/verification.json')['status']=='PASS'
assert (R/PLAN).exists() and (R/AUTH/'result.md').exists()
for source in [R/AUTH/'verification-attempt-03/source-lock.json',R/GROUP/'attempt-02/source-lock.json']:
    for p,h in j(source).items():assert digest(R/p)==h,'protected_input:'+p
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md']
before={p:(R/p).read_bytes() for p in paths}
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
a=cat['active_execution_note'];old=deepcopy(a)
assert a['current_candidate'].startswith('5.27;')
assert a['active_work_plan']=='docs/plans/accounting-acquisition-period-authority-20261026.md'
assert np['active_execution']['current_candidate']==a['current_candidate']
independent=a['compression_next_plan'];assert (R/independent).exists()
OLD=(R/a['full_gap_program']).parent
assert OLD.name=='gap-temporal-group-refresh-20261027'
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:assert digest(R/a[p])==a[k]
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
G.mkdir(exist_ok=False)
lock={str(p.relative_to(R)):digest(p) for p in OLD.iterdir() if p.is_file()}
dump(G/'predecessor-lock.json',lock)
audit=j(OLD/'audit-status.json');old_audit=deepcopy(audit)
audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version 5.27 temporal/group integration preserved; the dated acquisition-authority companion awaits integration.'
items=[('Dated acquisition authority and conditional method specification',AUTH+'/result.md','13 retained PDFs,242 identity/anchor checks,67 protected files; entity/election branches and actual measurements remain unresolved.')]
for title,p,scope in items:
    audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title=title,requirements=['MC05','MC17','MC19','MC20','MC24','MC25','MC28','MC30','MC33','MC34','MC35','W05','W06','W07','W08','W11','W12','W16','W17'],evidence=p,sha256=digest(R/p),current_disposition=scope))
dump(G/'audit-status.json',audit)
fail=j(OLD/'failure-register.json');oldfail=deepcopy(fail)
for finding,case,evidence in [('A debt claim is used as previously held equity or a missing acquisition measurement is replaced by a face value','Keep T/Q/P/A/L separately typed and unresolved; inspect pre-existing relationships and consideration before lowering.',AUTH+'/result.md')]:
    fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=finding,closure_packages=['W05','W06','W08','W12','W16'],discriminating_case=case,status='Conditional boundary/specification checked; actual method and measurement remain open',evidence=evidence))
dump(G/'failure-register.json',fail)
packages=j(OLD/'closure-packages.json');oldpackages=deepcopy(packages)
for row in packages['packages']:
    if row['id'] in ['W05','W06','W08','W11','W12','W16']:
        row['existing_support']+=' Dated acquisition requirements now retain unknown measurements and inspected authority alternatives;13 PDFs pass242 identity/anchor checks.'
    if row['id'] in ['W05','W06','W08']:
        row['next_action']='Execute accounting-acquisition-symbolic-20261027.md; then complete supported acquisition measurements and independent full worksheet/report comparisons, including NCI, post-control results and cash perimeter.'
    if row['id']=='W07':row['existing_support']+=' A bounded13-PDF acquisition-authority audit distinguishes entity, election and later-period dependencies; actual applicability stays open.'
    if row['id']=='W17':
        row['existing_support']+=' The checked acquisition-authority companion awaits integration into a successor to5.27; the group-scope argument is already integrated.'
        row['next_action']='Integrate verified acquisition and independent source-time companions while preserving the live manuscript; continue whole-document and reader/domain acceptance.'
    assert row['status']=='open'
dump(G/'closure-packages.json',packages)
text='# Full closure program after acquisition authority audit\n\n27 October2026. Version5.27 remains governing; all18 packages remain open.\n'
for row in packages['packages']:
    text+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
        v=row[key];text+=label+': '+(', '.join(v) or 'none' if isinstance(v,list) else v)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nGroup scope and dated authority companions are checked. Symbolic acquisition dependencies are next; actual measurements, financial methods and reporting remain open. Independent source-time work continues.\n\n'+'\n'.join('- **'+x['id']+' '+x['title']+':** '+x['next_action'] for x in packages['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. All53 obligations, six interactions,46 operations and18 packages remain open.\n')
(G/'plan-review.md').write_text('Skeptical audit passes after concurrent-baseline repair: use repaired30-case endpoint,22-case history and23-case scope dependencies. Source identity and symbolic arithmetic cannot promote actual accounting admission. Preserve5.27 and independent temporal-family work; no unknown measurement becomes zero. Full worksheets/reports remain mandatory before posting claims.\n')
assert audit['groups']==old_audit['groups'] and audit['literature']==old_audit['literature']
assert audit['successor_deltas'][:-1]==old_audit['successor_deltas']
assert all(fail[k]==oldfail[k] for k in ['original','literature_extensions']) and fail['cross_interface'][:-1]==oldfail['cross_interface']
for row,prior in zip(packages['packages'],oldpackages['packages']):assert all(row[k]==v for k,v in prior.items() if k not in ['existing_support','next_action'])
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
(G/'result.md').write_text('# Acquisition authority program refresh\n\n27 October2026. One checked companion delta and one interface challenge are added. All original obligations and all18 open packages remain. Candidate5.27, its four stable links and independent temporal-family work are preserved. Group-scope evidence already credited in5.27 is not duplicated. No new manuscript integration or accounting admission is implied.\n')
base=str(G.relative_to(R));updates=dict(updated='2026-10-27',active_work_plan=PLAN,financing_next_plan=PLAN,current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,latest_internal_result=AUTH+'/result.md',latest_financing_result=AUTH+'/result.md',control_group_scope_result=GROUP+'/result.md',acquisition_authority_result=AUTH+'/result.md',current_internal_status='Version5.27 preserved with group scope integrated. Dated acquisition-authority companion checked; symbolic acquisition dependencies next. Actual admission and full reports remain open.')
originals=[deepcopy(cat),deepcopy(np)]
for d in [a,np['active_execution']]:
    d.update(updates)
    d['active_work_plans']=list(dict.fromkeys([PLAN]+[p for p in d.get('active_work_plans',[]) if p!=old['active_work_plan']]))
    d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[GROUP+'/result.md',AUTH+'/result.md']))
    d['next']=['Execute '+PLAN,'Continue '+independent,'Continue all18 broad packages using their closure evidence']
    d['gap_program_next']=['Preserve unknowns in conditional symbolic acquisition expressions','Complete supported measurements and full acquisition worksheet/report comparison','Continue independent source-time, general-domain, recovery and acceptance work']
text=f'''# Current AccDSL master program

Updated27 October2026. Governing candidate **5.27**,783 main pages,not_ready.
Simulation **216 total/197 body pages**,26 chapters. Stable PDF/TeX links unchanged.
Main SHA256: {a['current_pdf_sha256']}.
Simulation SHA256: {a['standalone_pdf_sha256']}.
Manuscript result: {a['latest_result']}.

Version5.27 preserves temporal information families and integrates group scope:
{GROUP}/result.md:23 cases,15 refusals,291 assertions.
New checked companion, awaiting manuscript integration:
- {AUTH}/result.md:13 primary PDFs,242 checks,67 protected files.
Conditional scope and dated requirements do not admit actual control,
measurement, goodwill,NCI,journals or complete group statements.

Active financing plan: {PLAN}.
Independent plan: {independent}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All53 obligations,six interactions,46 operations,nine literature gaps and18
packages remain open. S1–S5 partial; S6 held; E3 deferred. Independent reader,
domain and whole-document acceptance remain pending. Continue feasible internal
work; preserve successful writers,source evidence and failed diagnostics.
Recovery snapshot: {str(backup.relative_to(R))}/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',paths[2]:text,paths[3]:text}
top=f'''## Acquisition companions checked — 27 October2026

Version5.27 remains governing:783 main pages;216 total/197 body simulation pages;
not_ready. Group scope is integrated; the dated authority audit passes242
checks over13 PDFs and awaits manuscript integration.
Results: {GROUP}/result.md; {AUTH}/result.md.
Active financing plan: {PLAN}.
Independent plan: {independent}.
Full program: {base}/closure-program.md.
All53 obligations,six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Continue feasible internal work.

'''
for p in paths[4:]:title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,h in lock.items():assert digest(R/p)==h
for p,s in new.items():put(R/p,s)
checks=[]
def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,target in links.items():ck('link:'+p,str((R/p).resolve())==target)
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('pdf:'+p,digest(R/a[p])==old[k])
for p,h in lock.items():ck('predecessor:'+p,digest(R/p)==h)
allowed=set(updates)|{'active_work_plans','latest_internal_results','next','gap_program_next'}
for d,key,prior in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
    ck('legacy_fields',all(d[k]==v for k,v in prior.items() if k!=key))
    ck('independent_fields',all(d[key][k]==v for k,v in prior[key].items() if k not in allowed))
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,source_admission=False,accounting_admission=False,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=PLAN)))
