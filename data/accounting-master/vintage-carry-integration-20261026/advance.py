"""Advance reviewed 5.18 and reconcile a successor gap queue."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import copy,json,os,sys
import integrate as m
ROOT,HERE=m.ROOT,m.HERE
GAP=ROOT/'data/accounting-master/gap-vintage-carry-20261026'
OLD=ROOT/'data/accounting-master/gap-refresh-20261026'
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def rel(p):return p.relative_to(ROOT).as_posix()
assert not GAP.exists() and not (HERE/'control-refresh.json').exists()
v=read(HERE/'verification.json');assert v['status']=='PASS' and v['count']==806
main,sim=v['documents'];assert (main['pages'],sim['pages'])==(757,190)
lock=read(HERE/'source-preservation.json')
for n,h in lock['sources'].items():
    assert sha(m.SOURCE/n)==h
    assert (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text())
for n,h in lock['evidence'].items():assert sha(ROOT/n)==h,n
for n,h in lock['added'].items():assert sha(m.TARGET/n)==h
for unit,attempt in [('inference-vintage-20261026','attempt-02'),('financing-carry-freshness-20261026','attempt-01')]:
    for n,h in read(HERE.parent/unit/attempt/'source-lock.json').items():assert sha(ROOT/n)==h,n
for d in [main,sim]:assert sha(ROOT/d['pdf'])==d['sha256'] and not d['new_warnings'] and not d['out_of_page_text_blocks']
for n in ['review.md','result.md','remaining-work.md']:assert (HERE/n).is_file()
assert sha(ROOT/'docs/AccDSL-latest.pdf')==m.BASE
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
names=list(read(OLD/'control-refresh.json')['files'])
before={n:(ROOT/n).read_bytes() for n in names}
active=json.loads(before['scripts/accounting_master_catalog.json'])['active_execution_note']
assert active['current_candidate']=='5.17;755 pages;not_ready'
previous_plan=active['active_work_plan']
next_plan='docs/plans/accounting-two-date-financing-control-20261026.md'
assert (ROOT/next_plan).is_file()
assert 'financing-carry' in previous_plan or previous_plan==next_plan,'preserve newly active unrelated work'
GAP.mkdir()
original={n:read(OLD/n) for n in ['audit-status.json','closure-packages.json','failure-register.json']}
a,packages,failures=[copy.deepcopy(original[n]) for n in original]
changes={
 'W03':('FiniteVintageInference/1 exactly checks corrected/retracted support, declared semantic duplicate information, fixed actor/cutoff/model and verified checkpoints.', 'Bind a real evidence-view selector and downstream actor-specific decision; audit particle auxiliaries and modern quantitative dependencies before sampler adoption.'),
 'W05':('SelectedFinancingCarry/1 has separate /3 compatibility evidence for paid/unpaid fiscal histories and later payment, integrated in 5.18.', 'Continue multiple-clause and economic acceleration methods with actual sources; preserve independent W06 financing/control work.'),
 'W12':('Finite evidence/checkpoint identity and exact replay now have bounded comparator evidence; this is not persistent-store durability.', 'Connect source revision invalidation and actor views; retain migration, real-store faults and sufficient checkpoint dependencies as distinct requirements.'),
 'W16':('Declared duplicate information and replacement support are checked together with exact vintage dependencies; /3 carry history is retained.', 'Combine actor information corrections with financing/control decisions and compression; retain full cross-interface outcomes.'),
 'W17':('Version5.18 integrates finite inference and /3 fiscal carry into both editions; all previous shared chapters remain.', 'Integrate subsequent checked decisions through protected sources; continue whole-document consistency and independent reader/domain assessment.')}
byid={w['id']:w for w in packages['packages']}
for wid,(support,nxt) in changes.items():
    w=byid[wid];w['predecessor_record']=copy.deepcopy(w);w['existing_support']+=' '+support;w['next_action']=nxt
for rows in a['groups'].values():
    for row in rows:
        row['predecessor_record']=copy.deepcopy(row)
        row['remaining_work_and_next_action']=' '.join(k+': '+byid[k]['next_action'] for k in row['closure_packages'])
        assert not row['full_requirement_closed']
new=[]
for unit,title,wid,scope in [
 ('financing-carry-freshness','Selected /3 fiscal carry compatibility','W05','30 full transitions,21 controls,406 assertions; original carry implementation unchanged.'),
 ('inference-vintage','Exact immutable-vintage replay and semantic identity','W03','311 assertions over64 finite requests; full masses/normalizers and call path checked; actual likelihood/source validity open.'),
 ('vintage-carry-integration','Shared 5.18 carry and inference integration','W17','757-page main,190-page companion with172 body pages;806 source/build checks and bounded rendered review.')]:
    result=HERE.parent/(unit+'-20261026')/'result.md'
    d=dict(id='D'+str(len(a['successor_deltas'])+1),title=title,requirements=byid[wid]['requirements'],evidence=rel(result),sha256=sha(result),current_disposition=scope)
    a['successor_deltas'].append(d);new.append(d)
a['baseline']='Checked Version5.18; preceding 5.17 refresh and original all-row evidence retained; scoped reconciliation only'
a['predecessor']=dict(path=rel(OLD/'audit-status.json'),sha256=sha(OLD/'audit-status.json'))
failures['cross_interface'].append(dict(id='X17',failure='A new slot counts the same corrected information twice',closure_packages=['W03','W12','W16'],discriminating_case='Duplicating likelihood (1/4,3/4) changes the equal-prior posterior to (1/10,9/10); declared duplicate identity must refuse.',status='Checked finite declared-identity refusal; semantic truth and independence remain external premises',evidence=new[1]['evidence']))
counts=dict(obligations=53,interactions=6,operations=46,literature_gaps=9,original_failures=67,literature_extensions=48,cross_interface_challenges=17,successor_deltas=25,closure_packages=18)
assert {k:len(x) for k,x in a['groups'].items()}==dict(obligations=53,interactions=6,operations=46)
assert len(a['successor_deltas'])==25 and len(failures['cross_interface'])==17
assert all(w['status']=='open' for w in packages['packages'])
for k in ['original','literature_extensions']:assert failures[k]==original['failure-register.json'][k]
assert failures['cross_interface'][:16]==original['failure-register.json']['cross_interface']
for k,rows in a['groups'].items():assert [r['predecessor_record'] for r in rows]==original['audit-status.json']['groups'][k]
for n,obj in [('audit-status.json',a),('closure-packages.json',packages),('failure-register.json',failures)]:save(GAP/n,obj)
save(GAP/'predecessor-lock.json',{rel(OLD/n):sha(OLD/n) for n in original})
lines=['# Full gap program after evidence replay and fiscal carry','','26 October2026. All18 broad packages remain open; prior rows and source evidence are retained.','']
for w in packages['packages']:
    lines+=['## '+w['id']+' — '+w['title'],'','Dependencies: '+(', '.join(w['depends_on']) or 'none')+'.','',w['existing_support'],'','Failure: '+w['failure'],'','Required evidence: '+w['closure_evidence'],'','Next: '+w['next_action'],'','Limits: '+w['limits'],'']
(GAP/'closure-program.md').write_text(chr(10).join(lines))
(GAP/'remaining-work.md').write_text((HERE/'remaining-work.md').read_text()+'\nActive financing plan: '+next_plan+'.\nExact inference follow-up: data/accounting-master/inference-vintage-20261026/remaining-work.md.\n')
(GAP/'plan-review.md').write_text('The plan docs/plans/accounting-gap-refresh-20261026.md remains applicable. This successor preserves its22 deltas and16 challenges, adding only three inspected result deltas and the semantic-duplicate counterexample. Whole requirements remain open; no independent all-row revalidation is inferred. The current two-date financing plan is retained as the next active work.\n')
(GAP/'result.md').write_text('Refreshed after checked Version5.18. Preserved53 obligations,6 interactions,46 operations,9 literature gaps,67 original failures and48 literature extensions. There are25 scoped successor deltas,17 cross-interface challenges and18 open packages. The exact finite inference and /3 carry results are integrated; next actions no longer repeat them. See closure-program.md, remaining-work.md and verification.json.\n')
gap=rel(GAP);result=rel(HERE/'result.md');remaining=rel(HERE/'remaining-work.md')
note=f'''## Current candidate and execution — 26 October 2026

Version5.18: governing main757 pages; simulation volume190 total/172 body pages;
not_ready. Exact evidence replacement/retraction, semantic duplicate-information
rejection and /3 fiscal carry are integrated in shared chapters. Source/build
checks and bounded rendered review pass; independent acceptance remains open.
Main PDF: {main['pdf']}
SHA256: {main['sha256']}
Standalone PDF: {sim['pdf']}
SHA256: {sim['sha256']}
Current result: {result}.
Full program: {gap}/closure-program.md.
Remaining work: {gap}/remaining-work.md.
Active next work: {next_plan}.
Inference follow-up: data/accounting-master/inference-vintage-20261026/remaining-work.md.
All53 obligations,6 interactions,46 operations and18 broad packages remain;
S1–S5 partial, S6 held, E3 deferred. Detailed prior history is preserved in
linked results and control-before snapshots. Do not rerun successful writers.

'''
proposed={}
for n,raw in before.items():
    s=raw.decode()
    if n.endswith('.json'):
        obj=json.loads(s);key='active_execution_note' if n.startswith('scripts/') else 'active_execution';e=obj[key]
        e.update(current_candidate='5.18;757 pages;not_ready',current_pdf=main['pdf'],current_pdf_sha256=main['sha256'],standalone_pdf=sim['pdf'],standalone_pdf_sha256=sim['sha256'],latest_result=result,latest_internal_result='data/accounting-master/inference-vintage-20261026/result.md',active_work_plan=next_plan,remaining_work=remaining,current_audit=gap+'/audit-status.json',full_gap_program=gap+'/closure-program.md',full_gap_remaining_work=gap+'/remaining-work.md',closure_packages=gap+'/closure-packages.json',failure_register=gap+'/failure-register.json',latest_gap_program_result=gap+'/result.md',gap_program_review=gap+'/plan-review.md',gap_program_verification=gap+'/verification.json',gap_program_trace_counts=counts,current_internal_status='Finite vintage replay and /3 fiscal carry checked and integrated; two-date financing/control active; real source-view and decision coupling open')
        e['active_work_plans']=list(dict.fromkeys([next_plan,'docs/plans/accounting-gap-refresh-20261026.md']+[p for p in e.get('active_work_plans',[]) if p not in [previous_plan,'docs/plans/accounting-inference-vintage-20261026.md','docs/plans/accounting-gap-program-20261026.md']]))
        e['next']=['W06/W16: execute the active two-date financing/control plan','W03/W12: bind real source-view selection and downstream actor-specific decisions','W01/W02 actual sources; W04/W15 compression and inference dependencies; all remaining packages open']
        e['gap_program_next']=e['next']
        if 'gap_program_execution' in e:
            e['gap_program_execution']['E01']='Exact financing invariant, remedy and /3 carry continuation integrated through5.18; broader financing open'
            e['gap_program_execution']['E02']='Exact exchange counterexample plus finite immutable-vintage replay integrated through5.18; modern sampler and source-view coupling open'
            e['gap_program_execution']['E03']='Qualified source reference plus selected /3 remedy and fiscal carry integrated; actual applicability and general rights effects open'
        if 'completed_increments' in e:
            for d in new:
                if d['evidence'] not in e['completed_increments']:e['completed_increments'].append(d['evidence'])
        assert {k:z for k,z in obj.items() if k!=key}=={k:z for k,z in json.loads(s).items() if k!=key}
        proposed[n]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
    elif n in ['docs/README.md','docs/design/README.md']:
        s=s.replace('Version 5.17, 755 pages','Version 5.18, 757 pages').replace('Version 5.17,','Version 5.18,')
        s=s.replace('**188 pages**','**190 pages**').replace('**170 body pages**','**172 body pages**').replace('170 body pages (188 total pages)','172 body pages (190 total pages)')
        proposed[n]=s.replace('financing-inference-integration-20261026/result.md','vintage-carry-integration-20261026/result.md')
    elif n in ['docs/plans/accounting-master-current.md','data/accounting-master/recovery-current-20261026.md']:
        proposed[n]=s.split(chr(10),1)[0]+chr(10)*2+note
    else:
        first,rest=s.split(chr(10),1)
        if rest.lstrip().startswith('## Current candidate and execution —'):
            start=rest.index('## Current candidate and execution —');end=rest.find('\n## ',start+4)
            if end!=-1:rest=rest[end:]
        rest=rest.replace('Version 5.17 is the current 755-page design candidate.','Version 5.18 is the current 757-page design candidate.')
        if n=='MISSION_CONTROL.md':rest=rest.replace('26 chapters and 170 body pages (188 total pages)','26 chapters and 172 body pages (190 total pages)')
        proposed[n]=first+chr(10)*2+note+rest.lstrip(chr(10))
backup=HERE/'control-before';assert not backup.exists()
for n,raw in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
links=[]
for stem,base in [('AccDSL-latest','accounting-product-proposal'),('AccDSL-simulation-foundations','simulation-foundations')]:
    for ext in ['pdf','tex']:
        p=ROOT/'docs'/(stem+'.'+ext);assert p.is_symlink();links.append(dict(path=rel(p),before=os.readlink(p),after=os.path.relpath(m.TARGET/(base+'.'+ext),p.parent)))
for n,raw in before.items():assert (ROOT/n).read_bytes()==raw,'concurrent control drift:'+n
for n,s in proposed.items():(ROOT/n).write_text(s)
for link in links:
    p=ROOT/link['path'];tmp=p.with_name(p.name+'.next');assert not tmp.exists() and not tmp.is_symlink();os.symlink(link['after'],tmp);os.replace(tmp,p)
assert sha(ROOT/'docs/AccDSL-latest.pdf')==main['sha256'] and sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==sim['sha256']
for n,h in read(GAP/'predecessor-lock.json').items():assert sha(ROOT/n)==h
save(HERE/'control-refresh.json',dict(files={n:dict(before=sha256(raw).hexdigest(),after=sha(ROOT/n)) for n,raw in before.items()},links=links,active_plan=next_plan,legacy_controller_unchanged=True))
save(GAP/'verification.json',dict(status='PASS',counts=counts,original_records_preserved=True,whole_requirements_closed=0,all_packages_open=True,current_aliases_verified=True))
build=read(HERE/'build.json')
save(HERE/'run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable: unusable marker preserved',commands=['integrate.py prepare','integrate.py build (attempt01 failed, attempt02 passed)','integrate.py verify','advance.py'],environment=sys.version,build_environment=build['environment'],cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=sum(r['wall_seconds'] for r in build['results']),wall_time_scope='successful document builds',data_version=rel(HERE/'source-preservation.json'),plan_file='docs/plans/accounting-vintage-carry-integration-20261026.md',result_file=result,artifacts=['verification.json','review.md','source-preservation.json','control-refresh.json','remaining-work.md']))
print(json.dumps(dict(status='PASS',candidate='5.18',main_pages=757,simulation_pages=190,simulation_body_pages=172,counts=counts,active_plan=next_plan)))
