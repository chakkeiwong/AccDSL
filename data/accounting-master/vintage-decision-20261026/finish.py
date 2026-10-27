"""Record checked decision companions without changing the governing PDFs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import copy,json,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OLD=ROOT/'data/accounting-master/gap-vintage-carry-20261026';NEW=ROOT/'data/accounting-master/gap-decision-refresh-20261026'
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def rel(p):return p.relative_to(ROOT).as_posix()
assert not NEW.exists() and not (HERE/'control-refresh.json').exists()
assert read(HERE/'attempt-01/checks.json')['status']=='PASS'
for n,h in read(HERE/'attempt-01/source-lock.json').items():assert sha(ROOT/n)==h,n
for n in ['decision.py','verify.py']:assert (HERE/n).read_bytes()==(HERE/'attempt-01'/n).read_bytes()
other=HERE.parent/'two-date-financing-control-20261026'
assert read(other/'attempt-01/verification.json')['status']=='PASS'
for n,h in read(other/'attempt-01/source-lock.json').items():assert sha(ROOT/n)==h,n
latest=ROOT/'data/accounting-master/vintage-carry-integration-20261026'
files=list(read(latest/'control-refresh.json')['files']);before={n:(ROOT/n).read_bytes() for n in files}
c=json.loads(before['scripts/accounting_master_catalog.json'])['active_execution_note']
assert c['current_candidate']=='5.18;757 pages;not_ready'
old_plan=c['active_work_plan'];next_plan='docs/plans/accounting-conversion-rights-bridge-20261026.md'
assert old_plan in ['docs/plans/accounting-two-date-financing-control-20261026.md',next_plan]
assert (ROOT/next_plan).is_file()
main_hash=sha(ROOT/'docs/AccDSL-latest.pdf');sim_hash=sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')
assert main_hash==c['current_pdf_sha256'] and sim_hash==c['standalone_pdf_sha256']
NEW.mkdir();objects={n:read(OLD/n) for n in ['audit-status.json','closure-packages.json','failure-register.json']}
a,p,f=[copy.deepcopy(objects[n]) for n in objects];byid={w['id']:w for w in p['packages']}
updates={
'W03':('Actor-specific supplied-registry head selection now calls exact finite inference; future additions preserve earlier requests, unknown/conflicting revisions stay unresolved.', 'Bind actual source/effective-date and actor-access evidence; connect actions to executable financial methods and continue modern inference source dependencies.'),
'W06':('Two-date finite conversion/control and exact participation/funding comparison passes a separate four-strategy comparator, including zero-benefit and tie cases.', 'Execute the audited typed conversion-rights bridge from supplied openings; date0 issuance, intervening measurement and full terminal liquidation remain separate.'),
'W16':('Actor hindsight and conversion-control/price/funding failure cases have bounded exact evidence; full interaction is not claimed.', 'Compose typed conversion/control with financing acceptance and actor information while preserving full journal/state comparisons.'),
'W17':('Version5.18 is current; actor-view and two-date financing companions are checked after that PDF.', 'Integrate those companions and any subsequent typed bridge through a protected successor; retain independent reader/domain and whole-document checks.')}
for wid,(support,nxt) in updates.items():
    w=byid[wid];w['predecessor_record']=copy.deepcopy(w);w['existing_support']+=' '+support;w['next_action']=nxt
for rows in a['groups'].values():
    for row in rows:
        row['predecessor_record']=copy.deepcopy(row);row['remaining_work_and_next_action']=' '.join(k+': '+byid[k]['next_action'] for k in row['closure_packages'])
newd=[]
for unit,title,wid,scope in [
('vintage-decision','Actor-specific finite information and decisions','W03','56 assertions/11 retained cases; unchanged earlier request, duplicate and conflicting information distinctions; actual source/financial execution remains open.'),
('two-date-financing-control','Exact two-date financing and conversion control','W06','Three complete strategy comparisons,139 assertions,28 controls; supplied finite game only; typed conversion and full dated accounting open.')]:
    result=HERE.parent/(unit+'-20261026')/'result.md'
    d=dict(id='D'+str(len(a['successor_deltas'])+1),title=title,requirements=byid[wid]['requirements'],evidence=rel(result),sha256=sha(result),current_disposition=scope)
    a['successor_deltas'].append(d);newd.append(d)
a['baseline']='Version5.18 remains current; actor-view and two-date financing companions added; historical statements of5.17 in concurrent result notes describe their entry context, not current links.'
a['predecessor']=dict(path=rel(OLD/'audit-status.json'),sha256=sha(OLD/'audit-status.json'))
f['cross_interface'].append(dict(id='X18',failure='A later analyst correction rewrites an earlier manager decision',closure_packages=['W03','W06','W12','W16'],discriminating_case='Analyst and manager have different supplied correction times; future-registry additions must leave the earlier manager request/decision unchanged.',status='Checked finite actor-view/decision case; actual availability and financial execution remain open',evidence=newd[0]['evidence']))
counts=dict(obligations=53,interactions=6,operations=46,literature_gaps=9,original_failures=67,literature_extensions=48,cross_interface_challenges=18,successor_deltas=27,closure_packages=18)
assert len(a['successor_deltas'])==27 and len(f['cross_interface'])==18
for key,rows in a['groups'].items():assert [r['predecessor_record'] for r in rows]==objects['audit-status.json']['groups'][key]
assert all(not row['full_requirement_closed'] for rows in a['groups'].values() for row in rows)
assert all(w['status']=='open' for w in p['packages'])
for key in ['original','literature_extensions']:assert f[key]==objects['failure-register.json'][key]
assert f['cross_interface'][:17]==objects['failure-register.json']['cross_interface']
for n,obj in [('audit-status.json',a),('closure-packages.json',p),('failure-register.json',f)]:save(NEW/n,obj)
save(NEW/'predecessor-lock.json',{rel(OLD/n):sha(OLD/n) for n in objects})
lines=['# Current full gap program','','26 October2026. Version5.18 plus two checked companions; all18 broad packages remain open.','']
for w in p['packages']:
    lines+=['## '+w['id']+' — '+w['title'],'','Dependencies: '+(', '.join(w['depends_on']) or 'none')+'.','',w['existing_support'],'','Failure: '+w['failure'],'','Closure evidence: '+w['closure_evidence'],'','Next: '+w['next_action'],'','Limits: '+w['limits'],'']
(NEW/'closure-program.md').write_text(chr(10).join(lines))
(NEW/'remaining-work.md').write_text('''# Current open work after decision companions

26 October2026. Governing Version5.18:757 pages; standalone190 total/172 body pages. Both PDFs remain unchanged by this checkpoint. All18 broad packages remain open.

1. W05/W06/W16: execute the existing conversion-rights bridge plan using generic typed methods and independently authored full states. Its supplied2028 opening is a bounded comparison; date0 funding, interim carrying measurement and terminal liquidation remain separate.
2. W03/W12: connect the checked actor-specific finite selector to actual source/effective-date/access evidence and to executable action feasibility. No missing source or unidentified probability becomes an invented fact.
3. W01/W02: obtain underlying instrument, series/amendment and notice facts with legal-issuer and temporal scope; preserve partial families.
4. W04/W15: mixed/continuous compression and contractual discontinuities; modern waste-free/resampling and quantitative source dependencies; source editions and authentic executable competitors.
5. W07–W14: remaining accounting, group, bank, insurance, numerical, language, migration and real-store fault cases; use per-package dependencies instead of repeating completed finite work.
6. W17: integrate checked actor-decision and two-date financing companions and later bridge results through protected manuscript successors; maintain whole-document consistency and independent implementation/reader/domain assessment.

The inherited53 obligations,6 interactions,46 operations,9 literature gaps,67 original failures and48 literature extensions survive. There are27 scoped deltas and18 cross-interface challenges. No finite register is exhaustive. S1–S5 partial; S6 held; E3 forecasting deferred. Internal work continues before any paid professional referral; none is authorized.
''')
(NEW/'plan-review.md').write_text('Successor trace review follows accounting-gap-refresh-20261026.md and the two audited finite decision plans. All inherited rows are preserved exactly; only current next actions and two explicit deltas change. No page/count proxy closes a package. Historical concurrent5.17 statements are superseded by verified live5.18 pointers. Typed accounting conversion and actual source-view admission remain unresolved. No new experiment is launched by this refresh.\n')
(NEW/'result.md').write_text('Refreshed the full program with actor-specific information/decision and two-date financing/control evidence. Preserved all original scope;27 successor deltas,18 interface challenges and18 open packages. Governing5.18 PDFs unchanged. Next active plan is accounting-conversion-rights-bridge-20261026.md. See remaining-work.md and verification.json.\n')
(HERE/'environment-reconciliation.md').write_text('''# Repository provenance reconciliation

At this checkpoint, read-only git rev-parse reports /home/chakwong/python/AccDSL as a working tree at03fea070f089821f4759e49a4466a3399b7fc078. This differs from the historical project note that the marker was unusable. No repository initialization, commit or restoration was performed here. Earlier manifests retain their then-recorded provenance; this new observation applies to this checkpoint only. Current source hashes and dirty-work preservation remain the evidence for the edits in this session.
''')
gap=rel(NEW);result=rel(HERE/'result.md');otherresult=rel(other/'result.md')
note=f'''## Current execution — 26 October2026

Version5.18 remains the governing757-page candidate, not_ready; the simulation
volume has190 total/172 body pages. Stable PDF and TeX links select one source
package. Main SHA256:{main_hash}. Standalone SHA256:{sim_hash}.
Latest manuscript result:data/accounting-master/vintage-carry-integration-20261026/result.md.
New companions:{result}; {otherresult}.
The actor-specific finite reference passes56 checks/11 cases; the separate
two-date financing comparison passes139 assertions/28 controls. These results
do not establish actual source admission or typed accounting conversion.
Full program:{gap}/closure-program.md.
Remaining work:{gap}/remaining-work.md.
Active next plan:{next_plan}.
All53 obligations,6 interactions,46 operations and18 packages remain open.
S1–S5 partial; S6 held; E3 deferred. Preserve all prior successful evidence.

'''
proposed={}
for n,raw in before.items():
    s=raw.decode()
    if n.endswith('.json'):
        obj=json.loads(s);key='active_execution_note' if n.startswith('scripts/') else 'active_execution';e=obj[key]
        e.update(active_work_plan=next_plan,latest_internal_result=result,latest_internal_results=[result,otherresult],current_audit=gap+'/audit-status.json',full_gap_program=gap+'/closure-program.md',full_gap_remaining_work=gap+'/remaining-work.md',closure_packages=gap+'/closure-packages.json',failure_register=gap+'/failure-register.json',latest_gap_program_result=gap+'/result.md',gap_program_review=gap+'/plan-review.md',gap_program_verification=gap+'/verification.json',gap_program_trace_counts=counts,current_internal_status='Actor-view and two-date financing companions checked; conversion-rights bridge active; actual source admission and broader packages open')
        e['active_work_plans']=list(dict.fromkeys([next_plan]+[p for p in e.get('active_work_plans',[]) if p!=old_plan]))
        e['next']=['Execute the selected typed conversion-rights bridge from its audited supplied opening','Bind actual source-view/access evidence and executable action feasibility','Integrate checked companions and continue the full remaining-work queue']
        e['gap_program_next']=e['next']
        if 'completed_increments' in e:
            for d in newd:
                if d['evidence'] not in e['completed_increments']:e['completed_increments'].append(d['evidence'])
        assert {k:v for k,v in obj.items() if k!=key}=={k:v for k,v in json.loads(s).items() if k!=key}
        proposed[n]=json.dumps(obj,indent=2,ensure_ascii=False)+chr(10)
    elif n in ['docs/README.md','docs/design/README.md']:continue
    elif n in ['docs/plans/accounting-master-current.md','data/accounting-master/recovery-current-20261026.md']:
        proposed[n]=s.split(chr(10),1)[0]+chr(10)*2+note
    else:
        first,rest=s.split(chr(10),1)
        if rest.lstrip().startswith('## Current candidate and execution —'):
            start=rest.index('## Current candidate and execution —');end=rest.find('\n## ',start+4)
            if end!=-1:rest=rest[end:]
        proposed[n]=first+chr(10)*2+note+rest.lstrip(chr(10))
backup=HERE/'control-before';assert not backup.exists()
for n in proposed:
    q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(before[n])
for n in proposed:assert (ROOT/n).read_bytes()==before[n],'concurrent_control_change:'+n
for n,s in proposed.items():(ROOT/n).write_text(s)
assert sha(ROOT/'docs/AccDSL-latest.pdf')==main_hash and sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==sim_hash
for n,h in read(NEW/'predecessor-lock.json').items():assert sha(ROOT/n)==h
save(NEW/'verification.json',dict(status='PASS',counts=counts,original_rows_preserved=True,all_packages_open=True,whole_requirements_closed=0,pdfs_unchanged=True,active_plan=next_plan))
save(HERE/'control-refresh.json',dict(files={n:dict(before=sha256(before[n]).hexdigest(),after=sha(ROOT/n)) for n in proposed},main_pdf_sha256=main_hash,standalone_pdf_sha256=sim_hash,active_plan=next_plan,legacy_controller_unchanged=True))
print(json.dumps(dict(status='PASS',candidate=c['current_candidate'],pdfs_unchanged=True,counts=counts,active_plan=next_plan)))
