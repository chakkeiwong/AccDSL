"""Refresh scoped gap evidence and promote the checked dual-edition draft."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import copy, importlib.util, json, os, sys
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / 'data/accounting-master/gap-program-20261026'
INTEGRATION = ROOT / 'data/accounting-master/financing-inference-integration-20261026'
def read(p): return json.loads(p.read_text())
def digest(p): return sha256(p.read_bytes()).hexdigest()
def save(p, x): p.write_text(json.dumps(x, indent=2, ensure_ascii=False) + chr(10))
def rel(p): return p.relative_to(ROOT).as_posix()
assert not (HERE/'verification.json').exists(), 'completed refresh must not rerun'
spec=importlib.util.spec_from_file_location('integration', INTEGRATION/'integrate.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
v=read(INTEGRATION/'verification.json'); p=read(INTEGRATION/'source-preservation.json')
assert v['status']=='PASS' and v['count']==897
for n,h in p['sources'].items():
    assert digest(m.SOURCE/n)==h,n
    assert (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items(): assert digest(ROOT/n)==h,n
for n,h in p['added'].items(): assert digest(m.TARGET/n)==h,n
for d in v['documents']:
    assert digest(ROOT/d['pdf'])==d['sha256'] and not d['new_warnings'] and not d['out_of_page_text_blocks']
assert digest(ROOT/'docs/AccDSL-latest.pdf')==m.BASE, 'new governing predecessor; rebase'
assert digest(ROOT/'docs/AccDSL-simulation-foundations.pdf')==m.STANDALONE
for n in ['review.md','result.md','remaining-work.md']: assert (INTEGRATION/n).is_file()
controls=list(read(ROOT/'data/accounting-master/financing-history-integration-20261026/control-refresh.json')['updated_files'])
before={n:(ROOT/n).read_bytes() for n in controls}
catalog=json.loads(before['scripts/accounting_master_catalog.json'])
active=catalog['active_execution_note']
assert active['current_candidate']=='5.16;750 pages;not_ready'
carry_plan=active['active_work_plan']
assert 'financing-carry' in carry_plan
inference_plan='docs/plans/accounting-inference-vintage-20261026.md'
refresh_plan='docs/plans/accounting-gap-refresh-20261026.md'
for n in [carry_plan,inference_plan,refresh_plan]: assert (ROOT/n).is_file()
oldnames=['audit-status.json','closure-packages.json','failure-register.json','closure-program.md','remaining-work.md','verification.json']
oldhash={rel(OLD/n):digest(OLD/n) for n in oldnames}
a=read(OLD/'audit-status.json'); packages=read(OLD/'closure-packages.json'); failures=read(OLD/'failure-register.json')
originals=copy.deepcopy((a,packages,failures))
updates={
'W03': ('E02 exact exchange/support counterexample now appears in both 5.17 editions.', 'Execute the immutable-vintage inference plan; separately inspect modern waste-free/resampling dependencies and actor-policy coupling.'),
'W05': ('Explicit financing opening/transition invariants, selected remedies /2 and /3 freshness, and separate /2 fiscal carry now have exact reference evidence.', 'Complete separate /3 carry compatibility, multiple-clause and economic-acceleration consequences; then dated funding and rights-changing cases. Preserve unknown actual terms.'),
'W11': ('Version 5.15 integrates selected native term structure, direct nested source, amendments, assessment, collection and carry with complete comparator evidence.', 'Extend language coverage only for a concrete unsatisfied cross-domain operation; general migration and compatible independent implementation remain open.'),
'W16': ('Same-day stale remedy, supplied-revision/category controls and retained fiscal missed-payment history are tested within selected profiles.', 'Compose evidence replacement with dependent decisions and multiple clauses; test guarantee/control and compression interactions without treating isolated checks as closure.'),
'W17': ('5.17 integrates E01, qualified E03, /3 freshness and E02 inference derivation into shared chapters; 755-page main and 188-page companion pass bounded review.', 'Integrate later carry/revision results through a protected successor; inspect whole-document consistency and retain independent reader/domain acceptance separately.')
}
for w in packages['packages']:
    if w['id'] in updates:
        w['predecessor_record']=copy.deepcopy(w)
        support,nxt=updates[w['id']];w['existing_support']+=' '+support;w['next_action']=nxt
    assert w['status']=='open'
byid={w['id']:w for w in packages['packages']}
for rows in a['groups'].values():
    for row in rows:
        row['predecessor_record']=copy.deepcopy(row)
        row['remaining_work_and_next_action']=' '.join(k+': '+byid[k]['next_action'] for k in row['closure_packages'])
        row['current_trace_status']='Successor evidence reconciled; no new independent whole-row acceptance'
        assert not row['full_requirement_closed']
newunits=[
('term-execution-integration','Selected nested term execution integrated','W11','20 complete comparisons, two continuous traces, nine controls and 1,018 assertions; bounded source-authored term scope.'),
('financing-opening-invariants','Financing opening and history invariants','W05','20 complete comparisons, 34 controls and 283 assertions; fiscal opening remains distinct from intermediate state.'),
('financing-remedy-state-binding','Economic-state remedy freshness /2','W05','Same-day payment discriminator repaired under /2; do not confuse this schema with /3.'),
('financing-history-integration','Version 5.16 integration','W17','750-page predecessor preserved in full; selected financing history and /2 remedies integrated.'),
('financing-remedy-freshness','Evidence-revision and clause freshness /3','W05','58 classifications, eight main transitions, 16 controls and 357 assertions; supplied revision truth and /2 compatibility not established.'),
('financing-carry','Selected fiscal carry /2','W05','30 full comparisons, 15 controls and 364 assertions; paid/unpaid claims and history survive; /3 compatibility remains separate.'),
('financing-inference-integration','Shared simulation-chapter integration 5.17','W17','Both editions preserve source qualifications and exact E02 support/exchange argument; no general inference/runtime adoption.')
]
newdeltas=[]
for unit,title,wid,scope in newunits:
    result=ROOT/('data/accounting-master/'+unit+'-20261026/result.md'); assert result.exists()
    d=dict(id='D'+str(len(a['successor_deltas'])+1),title=title,requirements=byid[wid]['requirements'],evidence=rel(result),sha256=digest(result),current_disposition=scope)
    a['successor_deltas'].append(d);newdeltas.append(d)
a['baseline']='Current checked 5.17; predecessor 5.16 and original 4.40 all-row assessment retained; scoped trace reconciliation only'
a['predecessor']=dict(path=rel(OLD/'audit-status.json'),sha256=oldhash[rel(OLD/'audit-status.json')])
for id_,title,case in [
('X15','Same-day remedy reuse after economy or evidence changes','A principal clause observed before payment, or under an earlier supplied source revision, cannot authorize a new acceleration without reassessment.'),
('X16','Carry preserves history but does not refresh observations','Paid/unpaid claims cross a fiscal boundary; preserve old miss and acceleration while refusing to redate the clause finding or silently convert /2 to /3.')]:
    failures['cross_interface'].append(dict(id=id_,failure=title,closure_packages=['W05','W12','W16'],discriminating_case=case,status='Scoped exact evidence; broader source applicability and profile composition open',evidence=newdeltas[-3 if id_=='X15' else -2]['evidence']))
counts=dict(obligations=len(a['groups']['obligations']),interactions=len(a['groups']['interactions']),operations=len(a['groups']['operations']),literature_gaps=len(a['literature']),original_failures=len(failures['original']),literature_extensions=len(failures['literature_extensions']),cross_interface_challenges=len(failures['cross_interface']),successor_deltas=len(a['successor_deltas']),closure_packages=len(packages['packages']))
assert counts==dict(obligations=53,interactions=6,operations=46,literature_gaps=9,original_failures=67,literature_extensions=48,cross_interface_challenges=16,successor_deltas=22,closure_packages=18)
assert a['successor_deltas'][:15]==originals[0]['successor_deltas']
assert a['literature']==originals[0]['literature']
for k in ['original','literature_extensions']: assert failures[k]==originals[2][k]
assert failures['cross_interface'][:14]==originals[2]['cross_interface']
for group,rows in a['groups'].items(): assert [r['predecessor_record'] for r in rows]==originals[0]['groups'][group]
save(HERE/'audit-status.json',a);save(HERE/'closure-packages.json',packages);save(HERE/'failure-register.json',failures)
save(HERE/'predecessor-lock.json',oldhash)
program=['# Current full gap closure program','', '26 October 2026. Successor of the frozen gap-program-20261026. All 18 broad packages remain open. Historical rows and evidence are retained; scoped progress is not whole-row acceptance.','']
for w in packages['packages']:
    program += ['## '+w['id']+' — '+w['title'],'','Dependencies: '+(', '.join(w['depends_on']) or 'none')+'.','',w['existing_support'],'','Failure: '+w['failure'],'','Required closure evidence: '+w['closure_evidence'],'','Next: '+w['next_action'],'','Limits: '+w['limits'],'']
(HERE/'closure-program.md').write_text(chr(10).join(program))
remaining='''# Current remaining work

26 October 2026. Version 5.17 is the checked design candidate, not_ready; main 755 pages and simulation volume 188 total/170 body pages. All 53 obligations, six interactions, 46 operations and 18 broad packages remain.

Priority execution:

1. W03/W12: immutable-vintage inference requests with exact replay and support restoration under corrections; plan docs/plans/accounting-inference-vintage-20261026.md.
2. W05: retain concurrent financing carry and its /3 compatibility successor. Existing /2 carry is checked, not a compatibility proof. Then multiple clauses, dated funding, economic acceleration and control-changing conversions.
3. W01/W02: actual underlying debt instruments, amendments, series and notice facts; preserve legal issuer and availability qualifications. No missing source becomes an assumed fact.
4. W04/W15: mixed/continuous compression and guard margins, modern SMC resampling/waste-free and quantitative source dependencies. Available technical reading remains internal work.
5. W07–W14: execute the domain, numerical, language and persistence packages according to concrete dependencies in closure-packages.json; the original 46 operation rows remain individually traceable.
6. W16/W17: cross-interface failures, protected integration of later results, whole-document consistency, independent implementation and ordinary reader feedback. Complete feasible internal work before paid professional referral.

Term structural/source/event binding and selected financing opening invariants are no longer listed as untouched work. All inherited failure and literature records survive; 22 successor deltas and 16 cross-interface challenges describe current progress. These finite records do not enumerate every possible failure or all relevant literature. S1–S5 partial; S6 held; E3 forecasting deferred.
'''
(HERE/'remaining-work.md').write_text(remaining)
review='''# Refresh review

The audited plan is docs/plans/accounting-gap-refresh-20261026.md. Frozen gap files are copied into a successor rather than regenerated. All original row records, literature entries and failure entries are retained exactly; only current next actions and explicit successor deltas change. The 5.17 sources are checked against 5.16 and all 121 protected evidence files before updating aliases. Carry /2 and /3 are explicitly distinct. Legacy controller state and phase bindings are unchanged. Page/check counts remain descriptive. No broad closure or independent acceptance is inferred.
'''
(HERE/'plan-review.md').write_text(review)
(HERE/'result.md').write_text('# Refreshed master and gap program'+chr(10)*2+'26 October 2026. The current design candidate is 5.17 (755-page main; 188-page simulation volume, 170 body pages). Preserved all 53 obligations, six interactions, 46 operations, nine literature gaps, 67 original failures and 48 literature extensions. Seven scoped deltas extend the existing 15 to 22; two cross-interface failures extend 14 to 16. All 18 broad packages remain open. Completed term/invariant/integration work receives credit, stale next actions are replaced, and concurrent carry work remains active. See verification.json for source and route checks; remaining-work.md and closure-program.md give the executable next sequence. No general design, real-company or independent-reader acceptance follows.'+chr(10))
main,sim=v['documents'];gbase=rel(HERE);ires=rel(INTEGRATION/'result.md')
note=f'''## Current candidate and execution — 26 October 2026

Version 5.17: main 755 pages; simulation volume 188 total/170 body pages; not_ready.
Shared chapters integrate settlement history, qualified remedies, /3 freshness
and E02 inference dependencies. Sources, citations and bounded rendered review
pass; 237 predecessor sources and 121 evidence files remain protected.
Main PDF: {main['pdf']}
SHA256: {main['sha256']}
Standalone PDF: {sim['pdf']}
SHA256: {sim['sha256']}
Integration result: {ires}.
Full program: {gbase}/closure-program.md.
Full remaining work: {gbase}/remaining-work.md.
Concurrent financing work: {carry_plan}.
Independent next unit: {inference_plan}.
All 53 obligations, six interactions, 46 operations and 18 broad packages remain;
S1–S5 partial, S6 held, E3 deferred. No whole requirement closes. Human feedback
and domain acceptance remain separate from feasible internal work.

'''
proposed={}
for n,raw in before.items():
    s=raw.decode()
    if n.endswith('.json'):
        x=json.loads(s);key='active_execution_note' if n.startswith('scripts/') else 'active_execution';e=x[key]
        e.update(current_candidate='5.17;755 pages;not_ready',latest_result=ires,current_pdf=main['pdf'],current_pdf_sha256=main['sha256'],standalone_pdf=sim['pdf'],standalone_pdf_sha256=sim['sha256'],current_program=refresh_plan,current_audit=gbase+'/audit-status.json',remaining_work=rel(INTEGRATION/'remaining-work.md'),full_gap_plan=refresh_plan,full_gap_program=gbase+'/closure-program.md',full_gap_remaining_work=gbase+'/remaining-work.md',closure_packages=gbase+'/closure-packages.json',failure_register=gbase+'/failure-register.json',latest_gap_program_result=gbase+'/result.md',gap_program_review=gbase+'/plan-review.md',gap_program_verification=gbase+'/verification.json',gap_program_trace_counts=counts,latest_internal_result='data/accounting-master/financing-carry-20261026/result.md',current_internal_status='Scoped /2 carry and /3 freshness checked; compatibility successor and immutable-vintage inference remain active')
        plans=e.get('active_work_plans',[carry_plan]);e['active_work_plans']=list(dict.fromkeys([carry_plan,inference_plan,refresh_plan]+plans))
        e['next']=['W05: preserve ongoing carry /3 compatibility work','W03/W12: execute immutable-vintage inference and exact support restoration','Continue all open packages; S6 held and E3 deferred']
        e['gap_program_next']=e['next']+['W01/W02 actual source applicability; W04/W15 compression and quantitative dependencies']
        if 'completed_increments' in e:
            for d in newdeltas:
                if d['evidence'] not in e['completed_increments']:e['completed_increments'].append(d['evidence'])
        assert e['active_work_plan']==carry_plan
        assert {k:z for k,z in x.items() if k!=key}=={k:z for k,z in json.loads(s).items() if k!=key}
        proposed[n]=json.dumps(x,indent=2,ensure_ascii=False)+chr(10)
    elif n in ['docs/README.md','docs/design/README.md']:
        s=s.replace('Version 5.16, 750 pages','Version 5.17, 755 pages').replace('Version 5.16,','Version 5.17,')
        s=s.replace('**183 pages**','**188 pages**').replace('**165 body pages**','**170 body pages**').replace('165 body pages (183 total pages)','170 body pages (188 total pages)')
        s=s.replace('financing-history-integration-20261026/result.md','financing-inference-integration-20261026/result.md')
        proposed[n]=s
    elif n in ['docs/plans/accounting-master-current.md','data/accounting-master/recovery-current-20261026.md']:
        proposed[n]=s.split(chr(10),1)[0]+chr(10)*2+note+'Detailed history is preserved in the linked results and the refresh control-before snapshot. Do not rerun successful evidence writers. Continue the independent inference unit while retaining concurrent carry work.'+chr(10)
    else:
        first,rest=s.split(chr(10),1)
        rest=rest.replace('## Current governing candidate — Version 5.16','## Prior governing candidate — Version 5.16')
        rest=rest.replace('Status: active mission; Version 5.16 is the current 750-page design candidate.','Status: active mission; Version 5.17 is the current 755-page design candidate.')
        if n=='MISSION_CONTROL.md':rest=rest.replace('26 chapters and 165 body pages (183 total pages)','26 chapters and 170 body pages (188 total pages)')
        proposed[n]=first+chr(10)*2+note+rest.lstrip(chr(10))
backup=HERE/'control-before';assert not backup.exists()
for n,raw in before.items():
    path=backup/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
links=[]
for stem,base in [('AccDSL-latest','accounting-product-proposal'),('AccDSL-simulation-foundations','simulation-foundations')]:
    for ext in ['pdf','tex']:
        q=ROOT/'docs'/(stem+'.'+ext);assert q.is_symlink()
        links.append(dict(path=rel(q),before=os.readlink(q),after=os.path.relpath(m.TARGET/(base+'.'+ext),q.parent)))
for n,raw in before.items():assert (ROOT/n).read_bytes()==raw,'concurrent change: '+n
for n,s in proposed.items():(ROOT/n).write_text(s)
for link in links:
    q=ROOT/link['path'];tmp=q.with_name(q.name+'.next');assert not tmp.exists() and not tmp.is_symlink()
    os.symlink(link['after'],tmp);os.replace(tmp,q)
for n,h in oldhash.items():assert digest(ROOT/n)==h
assert digest(ROOT/'docs/AccDSL-latest.pdf')==main['sha256']
assert digest(ROOT/'docs/AccDSL-simulation-foundations.pdf')==sim['sha256']
for n in controls:assert '5.17' in (ROOT/n).read_text(),n
save(HERE/'control-refresh.json',dict(files={n:dict(before=sha256(before[n]).hexdigest(),after=digest(ROOT/n)) for n in controls},links=links,preserved_active_plan=carry_plan))
save(HERE/'verification.json',dict(status='PASS',counts=counts,preserved_original_records=True,all_packages_open=True,frozen_sources_unchanged=True,controls=len(controls),aliases=4,legacy_controller_unchanged=True,whole_requirements_closed=0))
build=read(INTEGRATION/'build.json')
save(INTEGRATION/'run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable: unusable repository marker preserved',commands=['integrate.py prepare','integrate.py build','integrate.py verify',rel(HERE/'refresh.py')],environment=sys.version,build_environment=build['environment'],cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=sum(r['wall_seconds'] for r in build['results']),wall_time_scope='two document builds',data_version=rel(INTEGRATION/'source-preservation.json'),plan_file='docs/plans/accounting-financing-inference-integration-20261026.md',result_file=ires,artifact_paths=[rel(INTEGRATION/'verification.json'),rel(INTEGRATION/'review.md'),rel(HERE/'control-refresh.json')]))
print(json.dumps(dict(status='PASS',candidate='5.17',main_pages=755,standalone_pages=188,body_pages=170,counts=counts,preserved_active_plan=carry_plan)))
