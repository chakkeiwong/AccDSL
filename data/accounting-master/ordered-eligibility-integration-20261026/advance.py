from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util
import json,os,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+chr(10))
v=json.loads((HERE/'verification.json').read_text())
assert v['passed_preservation'] and v['version']=='5.7' and v['pages']==721
assert not v['new_warnings'] and not v['out_of_page_text_blocks'] and sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
s=importlib.util.spec_from_file_location('integration',HERE/'integrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=json.loads((HERE/'source-preservation.json').read_text())
for n,h in p['sources'].items():assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items():assert sha(ROOT/n)==h,n
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
standalone='1a39bd1e7e1e3c7e36d914cf324660d135808bb5fe4c21982bdc324791b4ef43'
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
plan='docs/plans/accounting-declarative-event-program-20261026.md';assert (ROOT/plan).exists()
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation};backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.7 — 26 October 2026

Version 5.7 is the 721-page governing design candidate, not_ready. Ordered
full-intent eligibility and explicit construction reproduce 38 complete event
requests/transitions and 34 refusals, with 70 boundary controls. Native event
evaluation is disabled in those checks; complete-program composition remains
the next dependency. All 217 predecessor sources are protected under the
three declared prose/cover changes. All simulation chapters are unchanged;
the standalone remains verified Version 5.5, 171 pages, 26 chapters and 155
body pages. No new warnings. Cover/pages 684–687 inspected. All 53 obligations,
six interactions and 46 operations remain; no whole requirement closes.
S1–S5 partial, S6 held, E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for n in concise:
    tail='Mission:'+before[n].decode().split('Mission:',1)[1];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: can explicit event rules preserve complete programs, report/carry results and stopped prefixes?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='# Current AccDSL master program'+chr(10)*2+note+chr(10).join(lines)+chr(10)
for n in history:
    first,rest=before[n].decode().split(chr(10),1);assert '## Current governing candidate — Version 5.6' in rest
    proposed[n]=first+chr(10)*2+note+rest.replace('## Current governing candidate — Version 5.6','## Prior governing candidate — Version 5.6',1).lstrip(chr(10))
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.7;721 pages;not_ready',current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,latest_internal_result='data/accounting-master/ordered-event-eligibility-20261026/result.md')
for n in ('data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'):
    d=json.loads(before[n]);a=d['active_execution'] if 'active_execution' in d else d['active_execution_note'];a.update(updates)
    if 'completed_increments' in a:a['completed_increments'].append('Version5.7:721 pages;38 full events;34 refusals;70 ordered eligibility controls')
    if 'latest_results' in a:a['latest_results'].extend([updates['latest_internal_result'],result])
    a['next']=['Compose ordered eligibility and checked constructors across complete company programs','Preserve state invariants, reports, carry and failed prefixes; native opening admission explicit','Audit wider language/source/history work after integration; S6 held, E3 deferred']
    proposed[n]=json.dumps(d,indent=2)+chr(10)
n='MISSION_CONTROL.md';t=before[n].decode();assert 'Version 5.6 is the current 720-page' in t
t=t.replace('Version 5.6 is the current 720-page','Version 5.7 is the current 721-page',1)
lines=t.splitlines();found=False
for i,line in enumerate(lines):
    if line.startswith('The [current integration result]'):
        lines[i]=f'The [current integration result]({result}) records ordered full-intent eligibility and exact event correspondence. The [active plan]({plan}) composes those explicit rules through complete company programs.';found=True;break
assert found;proposed[n]=chr(10).join(lines)+chr(10)
n='docs/README.md';t=before[n].decode();assert '**Version 5.6, 720 pages**' in t
proposed[n]=t.replace('**Version 5.6, 720 pages**','**Version 5.7, 721 pages**',1).replace('method-specialization-integration-20261026/result.md','ordered-eligibility-integration-20261026/result.md',1)
n='docs/design/README.md';t=before[n].decode();assert 'Version 5.6,' in t;proposed[n]=t.replace('Version 5.6,','Version 5.7,',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer'+chr(10)*2+note+'Ordered eligibility and Version 5.7 integration are complete. Next: compose explicit event rules through full programs. Opening admission remains explicitly native for this next increment. Main links select 5.7; standalone links remain verified 5.5. Do not rerun completed preparation/advancement writers. No background process running.'+chr(10)
remaining_text=(HERE.parent/'method-specialization-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0].replace('Version 5.6, 720 pages','Version 5.7, 721 pages')
remaining_text+=f'''## Next dependency

Finite ordered eligibility is checked against all 38 complete event requests and
transitions, 34 refusals and 70 controls. The complete runner still invokes the
old native event contract. Execute {plan}; retain native opening admission as a
separate named prerequisite and compare full reports/carry and stopped prefixes.
Broader financial/fiscal rules, actual-source partial histories, sector/group
composition, technical source gaps and independent acceptance remain open.
No whole requirement closes. S6 held, E3 deferred.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(scope.read_text())['groups'].items()};assert counts==dict(obligations=53,interactions=6,operations=46)
for n,b in before.items():q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(remaining_text)
for n,t in proposed.items():assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(t)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix);assert path.is_symlink() and target.exists()
    old=os.readlink(path);relative=os.path.relpath(target,path.parent);temp=path.with_name(path.name+'.next');assert not temp.exists() and not temp.is_symlink()
    os.symlink(relative,temp);os.replace(temp,path);links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
dump('control-refresh.json',dict(next_plan=plan,updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,standalone_pdf_sha256=standalone))
build=json.loads((HERE/'build.json').read_text());git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',commands=['configure.py','integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],wall_time_scope='Main manuscript build',data_version=sha(scope),plan_file='docs/plans/accounting-ordered-eligibility-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate=updates['current_candidate'],controls=len(controls),main_links=len(links),standalone_unchanged=True,next_plan=plan)))
