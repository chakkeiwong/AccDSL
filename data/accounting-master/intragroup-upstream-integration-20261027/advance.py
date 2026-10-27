"""One-shot guarded 5.34 advancement; retain independent live fields."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.util,json,os
H=Path(__file__).resolve().parent;R=H.parents[2]
G=H.parent/'gap-intragroup-upstream-integration-refresh-20261027'
PLAN='docs/plans/accounting-intragroup-upstream-carry-20261027.md'
INTEGRATION='docs/plans/accounting-intragroup-upstream-integration-20261027.md'
def read(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def put(p,s):
    q=p.with_name(p.name+'.worked-advance.tmp');assert not q.exists()
    q.write_text(s);os.replace(q,p)
assert not (H/'advancement.json').exists() and not G.exists()
assert (H/'author-review.md').exists() and (H/'result.md').exists()
spec=importlib.util.spec_from_file_location('worked_integration',H/'integrate.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
lock=read(H/'source-preservation.json');S=R/lock['source'];T=R/lock['target']
checks=[]
def ck(n,v):
    checks.append(dict(name=n,passed=bool(v)));assert v,n
for p,h in lock['sources'].items():
    ck('predecessor:'+p,digest(S/p)==h)
    ck('candidate:'+p,(T/p).read_text()==mod.transform(p,(S/p).read_text()))
for p,h in lock['evidence'].items():ck('evidence:'+p,digest(R/p)==h)
for p,h in lock['added'].items():ck('added:'+p,digest(T/p)==h)
for p,h in lock['integration_inputs'].items():ck('integration:'+p,digest(H/p)==h)
v=read(H/'verification.json');ck('document_checks',v['status']=='PASS' and v['checks']==686)
for d in v['documents']:ck('pdf:'+d['document'],digest(T/(d['document']+'.pdf'))==d['sha256'])
paths=['scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json',
 'docs/plans/accounting-master-current.md','data/accounting-master/next-plan.md',
 'MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-product-design-checkpoint.md','docs/README.md']
before={p:(R/p).read_bytes() for p in paths}
cat=json.loads(before[paths[0]]);np=json.loads(before[paths[1]])
originals=[deepcopy(cat),deepcopy(np)];a=cat['active_execution_note']
ck('baseline',a['current_candidate']=='5.33;800 pages;not_ready')
ck('active_plan',a['active_work_plan']==INTEGRATION)
for k in ['current_candidate','active_work_plan','current_pdf','current_pdf_sha256',
          'standalone_pdf','standalone_pdf_sha256','full_gap_program','compression_next_plan']:
    ck('consistent_control:'+k,a[k]==np['active_execution'][k])
independent=a['compression_next_plan'];ck('next_plans',(R/PLAN).exists() and (R/independent).exists())
OLD=(R/a['full_gap_program']).parent
ck('gap_baseline',OLD.name=='gap-intragroup-upstream-refresh-20261027')
for p,k in [('current_pdf','current_pdf_sha256'),('standalone_pdf','standalone_pdf_sha256')]:
    ck('current_hash:'+p,digest(R/a[p])==a[k])
links={p:str((R/p).resolve()) for p in ['docs/AccDSL-latest.pdf','docs/AccDSL-latest.tex',
 'docs/AccDSL-simulation-foundations.pdf','docs/AccDSL-simulation-foundations.tex']}
for p,q in links.items():ck('baseline_link:'+p,Path(q).parent==S)
oldlock={str(p.relative_to(R)):digest(p) for p in OLD.iterdir() if p.is_file()}
audit=read(OLD/'audit-status.json');oldaudit=deepcopy(audit)
audit['predecessor']=str(OLD.relative_to(R))
audit['baseline']='Version 5.34 preserves 5.33 and integrates upstream inventory, external supplier cash and conditional NCI attribution.'
audit['successor_deltas'].append(dict(id='D'+str(len(audit['successor_deltas'])+1),
 title='Protected upstream inventory manuscript integration',
 requirements=['MC05','MC17','MC19','MC20','MC24','MC25','MC28','MC32','MC33','MC34','MC35','W05','W06','W08','W11','W12','W16','W17'],
 evidence=str((H/'result.md').relative_to(R)),sha256=digest(H/'result.md'),
 current_disposition='686 checks preserve 262 predecessor sources and 144 evidence files; all added pages/covers author-reviewed. Previously credited numerical companions are not counted again. Independent acceptance pending.'))
packages=read(OLD/'closure-packages.json');oldpackages=deepcopy(packages)
for row in packages['packages']:
    ck('open:'+row['id'],row['status']=='open')
    if row['id'] in ['W05','W06','W08','W11','W12','W16','W17']:
        row['existing_support']+=' Version 5.34 integrates the upstream inventory, external supplier cash and conditional NCI attribution; author review is provisional.'
    if row['id'] in ['W05','W06','W08']:
        row['next_action']='Execute accounting-intragroup-upstream-carry-20261027.md: compare complete upstream opening equity,NCI and later margin/tax release; then prior interests/debt conversion,loss/ownership and general methods.'
    if row['id']=='W17':
        row['next_action']='Integrate verified finance and independent partial/prospective-policy companions; preserve live versions and continue whole-document and reader/domain acceptance.'
    ck('package_preserved:'+row['id'],all(row[k]==x for k,x in next(p for p in oldpackages['packages'] if p['id']==row['id']).items() if k not in ['existing_support','next_action']))
counts=dict(read(OLD/'verification.json')['counts']);counts['successor_deltas']=len(audit['successor_deltas'])
ck('audit_preserved',audit['groups']==oldaudit['groups'] and audit['literature']==oldaudit['literature'] and audit['successor_deltas'][:-1]==oldaudit['successor_deltas'])
ck('counts',counts==dict(obligations=53,interactions=6,operations=46,literature_gaps=9,original_failures=67,literature_extensions=48,cross_interface_challenges=76,successor_deltas=77,closure_packages=18))
base=str(G.relative_to(R));result=str((H/'result.md').relative_to(R))
updates=dict(updated='2026-10-27',active_work_plan=PLAN,financing_next_plan=PLAN,
 current_candidate='5.34;801 pages;not_ready',latest_result=result,current_program=INTEGRATION,full_gap_plan=INTEGRATION,
 current_pdf=str((T/'accounting-product-proposal.pdf').relative_to(R)),current_pdf_sha256=v['documents'][0]['sha256'],
 standalone_pdf=str((T/'simulation-foundations.pdf').relative_to(R)),standalone_pdf_sha256=v['documents'][1]['sha256'],
 current_audit=base+'/audit-status.json',remaining_work=base+'/remaining-work.md',full_gap_remaining_work=base+'/remaining-work.md',
 full_gap_program=base+'/closure-program.md',closure_packages=base+'/closure-packages.json',failure_register=base+'/failure-register.json',
 latest_gap_program_result=base+'/result.md',gap_program_review=base+'/plan-review.md',gap_program_verification=base+'/verification.json',gap_program_trace_counts=counts,
 current_internal_status='Version 5.34 integrates upstream inventory attribution. Next: audited upstream opening equity and NCI carry. Actual accounting admission remains unresolved.')
for d in [a,np['active_execution']]:
    d.update(updates)
    d['active_work_plans']=list(dict.fromkeys([PLAN]+[p for p in d.get('active_work_plans',[]) if p!=INTEGRATION]))
    d['next']=['Execute '+PLAN,'Continue '+independent,'Continue all 18 broad packages using their closure evidence']
    d['gap_program_next']=['Compare upstream two-year opening equity and NCI carry','Extend prior-interest, control and measurement methods','Continue independent partial/prospective-policy, recovery and acceptance work']
allowed=set(updates)|{'active_work_plans','next','gap_program_next'}
for d,key,prior in [(cat,'active_execution_note',originals[0]),(np,'active_execution',originals[1])]:
    ck('legacy_preserved:'+key,all(d[k]==x for k,x in prior.items() if k!=key))
    ck('independent_preserved:'+key,all(d[key][k]==x for k,x in prior[key].items() if k not in allowed))
summary=f'''Updated 27 October 2026. Governing candidate **5.34**, 801 main pages, not_ready.
Simulation **236 total / 215 body pages**, 26 chapters. All four stable PDF/TeX links select this candidate.
Main SHA256: {a['current_pdf_sha256']}.
Simulation SHA256: {a['standalone_pdf_sha256']}.
Manuscript result: {result}.

Upstream inventory, external supplier cash and conditional NCI attribution
are integrated. Prior carry and concurrent observation/frontier work are preserved. 686 document checks preserve 262
predecessor sources and 144 evidence files. All added pages and covers have bounded
author review; independent reader/domain and whole-document acceptance remain pending.
Actual company measurements, tax admission and complete group accounting remain open.

Active financing plan: {PLAN}.
Independent plan: {independent}.
Full program: {base}/closure-program.md.
Remaining work: {base}/remaining-work.md.
Verification: {base}/verification.json.

All 53 obligations, six interactions, 46 operations, nine literature gaps and 18
packages remain open. S1–S5 partial; S6 held; E3 deferred. Continue feasible
internal work. Preserve successful writers, original sources and failed attempts.
Recovery snapshot: {H.relative_to(R)}/control-before/.
'''
new={paths[0]:json.dumps(cat,indent=2)+'\n',paths[1]:json.dumps(np,indent=2)+'\n',
 paths[2]:'# Current AccDSL master program\n\n'+summary,paths[3]:'# Current AccDSL master program\n\n'+summary}
top='## Upstream inventory attribution integrated — 27 October 2026\n\n'+summary+'\n'
for p in paths[4:9]:
    title,body=before[p].decode().split('\n',1);new[p]=title+'\n\n'+top+body.lstrip('\n')
s=before['docs/README.md'].decode()
for old,newtext in [('Version 5.33, 800 pages','Version 5.34, 801 pages'),('**235 pages**','**236 pages**'),('**214 body pages**','**215 body pages**'),('intragroup-carry-integration-20261027/result.md','intragroup-upstream-integration-20261027/result.md'),('gap-intragroup-upstream-refresh-20261027/remaining-work.md','gap-intragroup-upstream-integration-refresh-20261027/remaining-work.md')]:
    ck('readme_anchor:'+old,old in s);s=s.replace(old,newtext)
new['docs/README.md']=s
# All preconditions and transformations are checked before the first write.
for p,b in before.items():ck('prewrite_control:'+p,(R/p).read_bytes()==b)
for p,q in links.items():ck('prewrite_link:'+p,str((R/p).resolve())==q)
backup=H/'control-before';backup.mkdir(exist_ok=False)
for p,b in before.items():q=backup/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
dump(backup/'stable-links.json',links);G.mkdir(exist_ok=False)
dump(G/'predecessor-lock.json',oldlock);dump(G/'audit-status.json',audit);dump(G/'closure-packages.json',packages)
(G/'failure-register.json').write_bytes((OLD/'failure-register.json').read_bytes())
program='# Full closure program after upstream inventory attribution integration\n\n27 October 2026. Version 5.34; all 18 packages remain open.\n'
for row in packages['packages']:
    program+='\n## '+row['id']+' — '+row['title']+'\n\n'
    for key in ['requirements','depends_on','failure','existing_support','closure_evidence','next_action','limits','status']:
        value=row[key];program+=key+': '+(', '.join(value) or 'none' if isinstance(value,list) else value)+'\n\n'
(G/'closure-program.md').write_text(program)
(G/'remaining-work.md').write_text('# Complete remaining-work queue\n\nVersion 5.34 integrates upstream inventory attribution. Next is upstream two-year carry; all broad packages remain open.\n\n'+'\n'.join('- **'+p['id']+' '+p['title']+':** '+p['next_action'] for p in packages['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred.\n')
(G/'plan-review.md').write_text('Skeptical audit passes: unchanged live 5.33 is the comparator; full source and evidence transforms, PDF hashes and bounded author reads support provisional 5.34 advancement only. Companion numerical results were already credited. No proxy metric closes accounting or reader acceptance. Independent partial/prospective-policy fields and every original obligation/failure/package are preserved. Upstream retained/NCI balances,unrecognised tax and recurring equipment schedules are explicit dependencies of the next financial unit.\n')
(G/'result.md').write_text('# Downstream inventory program refresh\n\nOne integration delta is added; prior numerical deltas and all failures are preserved without duplicate credit. All 53 obligations, six interactions, 46 operations and 18 open packages remain. 5.34 is a provisional manuscript; no accounting admission or whole-requirement closure.\n')
dump(G/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0))
for p,b in before.items():ck('commit_control:'+p,(R/p).read_bytes()==b)
for p,q in links.items():ck('commit_link:'+p,str((R/p).resolve())==q)
for p,s in new.items():put(R/p,s)
for p in links:
    name='simulation-foundations' if 'simulation' in p else 'accounting-product-proposal'
    q=T/(name+('.pdf' if p.endswith('.pdf') else '.tex'))
    tmp=(R/p).with_name(Path(p).name+'.worked-link');assert not tmp.exists()
    tmp.symlink_to(os.path.relpath(q,(R/p).parent));os.replace(tmp,R/p);links[p]=str(q)
for p,s in new.items():ck('readback:'+p,(R/p).read_text()==s)
for p,q in links.items():ck('advanced_link:'+p,str((R/p).resolve())==q)
for p,h in oldlock.items():ck('gap_preserved:'+p,digest(R/p)==h)
for p,h in lock['sources'].items():ck('source_preserved:'+p,digest(S/p)==h)
for p,h in lock['evidence'].items():ck('evidence_preserved:'+p,digest(R/p)==h)
for d in v['documents']:ck('final_pdf:'+d['document'],digest(T/(d['document']+'.pdf'))==d['sha256'])
dump(H/'advancement.json',dict(status='PASS',checks=len(checks),results=checks,candidate=a['current_candidate'],counts=counts,source_admission=False,accounting_admission=False,mission_complete=False))
print(json.dumps(dict(status='PASS',checks=len(checks),counts=counts,next=PLAN)))
