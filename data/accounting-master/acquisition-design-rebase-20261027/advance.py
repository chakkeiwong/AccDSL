"""Credit verified companions, preserving live editions and independent work."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,os
H=Path(__file__).resolve().parent; R=H.parents[2]
G=H.parent/'gap-acquisition-design-refresh-20261027'
PLAN='docs/plans/accounting-acquisition-worksheet-20261027.md'
AUTH='data/accounting-master/acquisition-period-authority-20261026'
GROUP='data/accounting-master/control-group-boundary-20261027'
def j(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def put(p,s):
    t=p.with_name(p.name+'.acquisition-progress.tmp');assert not t.exists()
    t.write_text(s);os.replace(t,p)
assert not (H/'advancement.json').exists()
assert (H/'author-review.md').exists() and (H/'result.md').exists()
doclock=j(H/'source-preservation.json');source=R/doclock['source']
for n,h in doclock['sources'].items():assert digest(source/n)==h
for n,h in doclock['evidence'].items():assert digest(R/n)==h
assert j(R/AUTH/'verification-attempt-03/verification.json')['status']=='PASS'
assert j(R/GROUP/'attempt-02/verification.json')['status']=='PASS'
assert (R/PLAN).exists() and (R/AUTH/'result.md').exists()
for input_lock in [R/AUTH/'verification-attempt-03/source-lock.json',R/GROUP/'attempt-02/source-lock.json']:
    for p,h in j(input_lock).items():assert digest(R/p)==h,'protected_input:'+p
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json','docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md','MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md']
before={p:(R/p).read_bytes() for p in paths}
before['docs/README.md']=(R/'docs/README.md').read_bytes()
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
a=cat['active_execution_note'];old=deepcopy(a)
assert a['current_candidate'].startswith('5.28;')
assert a['active_work_plan']=='docs/plans/accounting-acquisition-symbolic-20261027.md'
assert np['active_execution']['current_candidate']==a['current_candidate']
independent=a['compression_next_plan'];assert (R/independent).exists()
OLD=(R/a['full_gap_program']).parent
assert OLD.name=='gap-family-policy-refresh-20261027'
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:assert digest(R/a[p])==a[k]
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex','docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
assert (R/a['current_pdf']).parent==source
for p,target in links.items():assert Path(target).parent==source
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
G.mkdir(exist_ok=False)
lock={str(p.relative_to(R)):digest(p) for p in OLD.iterdir() if p.is_file()}
dump(G/'predecessor-lock.json',lock)
audit=j(OLD/'audit-status.json');old_audit=deepcopy(audit)
audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version5.29 preserves5.28 family policies and integrates dated acquisition authority and symbolic amount dependencies.'
items=[('Conditional acquisition amount dependencies','data/accounting-master/acquisition-symbolic-20261027/result.md','25 cases,21 refusals,505 assertions; unknown amounts remain symbols and no report is authorized.'),('Protected acquisition design integration',str((H/'result.md').relative_to(R)),'5.29 preserves256 predecessor sources and227 evidence files;758 checks and bounded author review; independent acceptance pending.')]
for title,p,scope in items:
    audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),title=title,requirements=['MC05','MC17','MC19','MC20','MC24','MC25','MC28','MC30','MC33','MC34','MC35','W05','W06','W07','W08','W11','W12','W16','W17'],evidence=p,sha256=digest(R/p),current_disposition=scope))
dump(G/'audit-status.json',audit)
fail=j(OLD/'failure-register.json');oldfail=deepcopy(fail)
for finding,case,evidence in [('Balanced symbolic acquisition expressions are treated as a complete measured group worksheet','Require identified item-level measurements and full independently authored account,adjustment and report comparisons.','data/accounting-master/acquisition-symbolic-20261027/result.md')]:
    fail['cross_interface'].append(dict(id='X'+str(len(fail['cross_interface'])+1),failure=finding,closure_packages=['W05','W06','W08','W12','W16'],discriminating_case=case,status='Conditional boundary/specification checked; actual method and measurement remain open',evidence=evidence))
dump(G/'failure-register.json',fail)
packages=j(OLD/'closure-packages.json');oldpackages=deepcopy(packages)
for row in packages['packages']:
    if row['id'] in ['W05','W06','W08','W11','W12','W16']:
        row['existing_support']+=' Symbolic acquisition dependencies pass25 cases/505 assertions; the dated authority and conditional expressions are integrated in5.29.'
    if row['id'] in ['W05','W06','W08']:
        row['next_action']='Execute accounting-acquisition-worksheet-20261027.md with independently authored full accounts, adjustments and reports; then extend noncash/prior-interest/loss/revision branches and actual admission.'
    if row['id']=='W07':row['existing_support']+=' A bounded13-PDF acquisition-authority audit distinguishes entity, election and later-period dependencies; actual applicability stays open.'
    if row['id']=='W17':
        row['existing_support']+=' Version5.29 integrates the dated acquisition-authority and unknown-amount argument while preserving5.28 common policies.'
        row['next_action']='Integrate verified acquisition and independent source-time companions while preserving the live manuscript; continue whole-document and reader/domain acceptance.'
    assert row['status']=='open'
dump(G/'closure-packages.json',packages)
text='# Full closure program after acquisition authority audit\n\n27 October2026. Version5.29 remains governing; all18 packages remain open.\n'
for row in packages['packages']:
    text+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for label,key in [('Requirements','requirements'),('Dependencies','depends_on'),('Known failure','failure'),('Existing support','existing_support'),('Closure evidence','closure_evidence'),('Next action','next_action'),('Limits','limits'),('Status','status')]:
        v=row[key];text+=label+': '+(', '.join(v) or 'none' if isinstance(v,list) else v)+'\n\n'
(G/'closure-program.md').write_text(text)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nDated authority and symbolic dependencies are checked and integrated. Item-level acquisition worksheets are next; actual measurements, financial methods and reporting remain open. Independent observation-map work continues.\n\n'+'\n'.join('- **'+x['id']+' '+x['title']+':** '+x['next_action'] for x in packages['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. All53 obligations, six interactions,46 operations and18 packages remain open.\n')
(G/'plan-review.md').write_text('Skeptical audit passes after concurrent-baseline repair: use repaired30-case endpoint,22-case history and23-case scope dependencies. Source identity and symbolic arithmetic cannot promote actual accounting admission. Preserve5.29 and independent temporal-family work; no unknown measurement becomes zero. Full worksheets/reports remain mandatory before posting claims.\n')
assert audit['groups']==old_audit['groups'] and audit['literature']==old_audit['literature']
assert audit['successor_deltas'][:-2]==old_audit['successor_deltas']
assert all(fail[k]==oldfail[k] for k in ['original','literature_extensions']) and fail['cross_interface'][:-1]==oldfail['cross_interface']
for row,prior in zip(packages['packages'],oldpackages['packages']):assert all(row[k]==v for k,v in prior.items() if k not in ['existing_support','next_action'])
counts=dict(j(OLD/'verification.json')['counts']);counts.update(successor_deltas=len(audit['successor_deltas']),cross_interface_challenges=len(fail['cross_interface']))
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
(G/'result.md').write_text('# Acquisition authority program refresh\n\n27 October2026. Two checked deltas and one interface challenge are added. All original obligations and all18 open packages remain. Candidate5.29, its four stable links and independent temporal-family work are preserved. Group-scope evidence already credited in5.27 is not duplicated. The checked acquisition explanation is integrated; no accounting admission follows.\n')
base=str(G.relative_to(R));updates=dict(updated='2026-10-27',active_work_plan=PLAN,financing_next_plan=PLAN,current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,latest_internal_result='data/accounting-master/acquisition-symbolic-20261027/result.md',latest_financing_result='data/accounting-master/acquisition-symbolic-20261027/result.md',control_group_scope_result=GROUP+'/result.md',acquisition_authority_result=AUTH+'/result.md',current_internal_status='Version5.29 preserves family-policy work and integrates dated authority/symbolic acquisition dependencies. Item-level worksheet comparison is next; actual accounting admission remains open.')
v=j(H/'verification.json');assert v['status']=='PASS'
T=R/j(H/'source-preservation.json')['target']
for doc in v['documents']:assert digest(T/(doc['document']+'.pdf'))==doc['sha256']
updates.update(current_candidate='5.29;790 pages;not_ready',latest_result=str((H/'result.md').relative_to(R)),current_program='docs/plans/accounting-acquisition-design-integration-20261027.md',full_gap_plan='docs/plans/accounting-acquisition-design-integration-20261027.md',current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=v['documents'][0]['sha256'],standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=v['documents'][1]['sha256'])
originals=[deepcopy(cat),deepcopy(np)]
for d in [a,np['active_execution']]:
    d.update(updates)
    d['active_work_plans']=list(dict.fromkeys([PLAN]+[p for p in d.get('active_work_plans',[]) if p!=old['active_work_plan']]))
    d['latest_internal_results']=list(dict.fromkeys(d.get('latest_internal_results',[])+[GROUP+'/result.md',AUTH+'/result.md','data/accounting-master/acquisition-symbolic-20261027/result.md']))
    d['next']=['Execute '+PLAN,'Continue '+independent,'Continue all18 broad packages using their closure evidence']
    d['gap_program_next']=['Compare item-level acquisition worksheets and full reports against independent expectations','Complete supported measurements and full acquisition worksheet/report comparison','Continue independent source-time, general-domain, recovery and acceptance work']
text=f'''# Current AccDSL master program

Updated27 October2026. Governing candidate **5.29**,790 main pages,not_ready.
Simulation **223 total/204 body pages**,26 chapters. Stable PDF/TeX links select the protected acquisition successor.
Main SHA256: {a['current_pdf_sha256']}.
Simulation SHA256: {a['standalone_pdf_sha256']}.
Manuscript result: {a['latest_result']}.

Version5.29 preserves temporal families/common policies and integrates acquisition design:
{GROUP}/result.md:23 cases,15 refusals,291 assertions.
Integrated dated authority and symbolic companions:
- {AUTH}/result.md:13 primary PDFs,242 checks,67 protected files.
- data/accounting-master/acquisition-symbolic-20261027/result.md:25 cases,21 refusals,505 assertions.
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

Version5.29 now governs:790 main pages;223 total/204 body simulation pages;
not_ready. Dated acquisition authority and symbolic dependencies are integrated;
25 cases/505 assertions and758 document checks preserve the inspected boundaries.
Results: {GROUP}/result.md; {AUTH}/result.md.
Active financing plan: {PLAN}.
Independent plan: {independent}.
Full program: {base}/closure-program.md.
All53 obligations,six interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Continue feasible internal work.

'''
for p in paths[4:]:title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode()
for oldtext,newtext in [('Version 5.28, 786 pages','Version 5.29, 790 pages'),('**219 pages**','**223 pages**'),('**200 body pages**','**204 body pages**'),('family-policy-integration-20261027/result.md','acquisition-design-rebase-20261027/result.md'),('gap-temporal-group-refresh-20261027/remaining-work.md','gap-acquisition-design-refresh-20261027/remaining-work.md')]:
    assert oldtext in s,oldtext;s=s.replace(oldtext,newtext)
s=s.replace('- [Complete temporal-family binding]','- [Conditional acquisition design](../data/accounting-master/acquisition-symbolic-20261027/result.md).\n- [Dated acquisition authority](../data/accounting-master/acquisition-period-authority-20261026/result.md).\n- [Complete temporal-family binding]')
new['docs/README.md']=s
for p,b in before.items():assert (R/p).read_bytes()==b,'concurrent_control_drift:'+p
for p,target in links.items():assert str((R/p).resolve())==target
for p,h in lock.items():assert digest(R/p)==h
for p,s in new.items():put(R/p,s)
for p in links:
    name='simulation-foundations' if 'simulation' in p else 'accounting-product-proposal'
    ext='.pdf' if p.endswith('.pdf') else '.tex';target=T/(name+ext)
    temp=(R/p).with_name(Path(p).name+'.acquisition-link');assert not temp.exists()
    temp.symlink_to(os.path.relpath(target,(R/p).parent));os.replace(temp,R/p)
    links[p]=str(target)
checks=[]
def ck(name,ok):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,target in links.items():ck('link:'+p,str((R/p).resolve())==target)
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:ck('pdf:'+p,digest(R/a[p])==a[k])
for p,h in lock.items():ck('predecessor:'+p,digest(R/p)==h)
for n,h in doclock['sources'].items():ck('source:'+n,digest(source/n)==h)
for n,h in doclock['evidence'].items():ck('evidence:'+n,digest(R/n)==h)
allowed=set(updates)|{'active_work_plans','latest_internal_results','next','gap_program_next'}
for d,key,prior in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
    ck('legacy_fields',all(d[k]==v for k,v in prior.items() if k!=key))
    ck('independent_fields',all(d[key][k]==v for k,v in prior[key].items() if k not in allowed))
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,source_admission=False,accounting_admission=False,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=PLAN)))
