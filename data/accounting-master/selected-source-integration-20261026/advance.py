from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,os,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
v=json.loads((HERE/'verification.json').read_text())
assert v['passed_preservation'] and v['version']=='5.10' and v['pages']==726
assert not v['new_warnings'] and not v['out_of_page_text_blocks'] and sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
spec=importlib.util.spec_from_file_location('integration',HERE/'integrate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads((HERE/'source-preservation.json').read_text())
for n,h in p['sources'].items():assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items():assert sha(ROOT/n)==h,n
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
standalone='1a39bd1e7e1e3c7e36d914cf324660d135808bb5fe4c21982bdc324791b4ef43'
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
plan='docs/plans/accounting-nonempty-opening-audit-20261026.md';assert (ROOT/plan).exists()
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation};backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.10 — 26 October 2026

Version 5.10 is the 726-page governing design candidate, not_ready. Direct
eligibility, opening, parameter/row recipe and selected-company source are
integrated. Four full programs preserve 44 commands and 26 adverse programs;
only the predeclared whole-program serialization-order digest differs. All
other results are exact with native lifecycle/builder disabled. All 220
predecessor sources are protected under four named edits. The 26 simulation
chapters and standalone Version 5.5 (171 pages/155 body pages) remain exact.
No new warnings; cover, physical page 268 and pages 690–694 inspected.
All 53 obligations, six interactions and 46 operations remain; no whole
requirement closes. S1–S5 partial, S6 held, E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for n in concise:
    tail='Mission:'+before[n].decode().split('Mission:',1)[1];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: which existing checks admit a carried book with live claims, and which empty-opening assumptions require a separate successor?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='# Current AccDSL master program\n\n'+note+'\n'.join(lines)+'\n'
for n in history:
    first,rest=before[n].decode().split('\n',1);assert '## Current governing candidate — Version 5.9' in rest
    proposed[n]=first+'\n\n'+note+rest.replace('## Current governing candidate — Version 5.9','## Prior governing candidate — Version 5.9',1).lstrip('\n')
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.10;726 pages;not_ready',current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,latest_internal_result='data/accounting-master/selected-company-source-20261026/result.md')
for n in controls[-2:]:
    d=json.loads(before[n]);a=d.get('active_execution',d.get('active_execution_note'));a.update(updates)
    if 'completed_increments' in a:a['completed_increments'].append('Version5.10:726 pages;direct selected company source;4 programs/44 commands and26 adverse;one explicit order-provenance exception')
    if 'latest_results' in a:a['latest_results'].extend([updates['latest_internal_result'],result])
    a['next']=['Audit exact carried nonempty openings and retained continuations','Specify a separately selected successor only after its invariant/report obligations are mapped','Preserve wider financial, source and acceptance residuals; S6 held; E3 deferred']
    proposed[n]=json.dumps(d,indent=2)+'\n'
n='MISSION_CONTROL.md';value=before[n].decode();assert 'Version 5.9 is the current 724-page' in value
value=value.replace('Version 5.9 is the current 724-page','Version 5.10 is the current 726-page',1);lines=value.splitlines()
for i,line in enumerate(lines):
    if line.startswith('The [current integration result]'):
        lines[i]=f'The [current integration result]({result}) records direct selected-company source and complete execution correspondence. The [active plan]({plan}) audits carried openings with live claims before a separate successor contract.';break
else:raise AssertionError('mission_current_link')
proposed[n]='\n'.join(lines)+'\n'
n='docs/README.md';value=before[n].decode();assert '**Version 5.9, 724 pages**' in value
proposed[n]=value.replace('**Version 5.9, 724 pages**','**Version 5.10, 726 pages**',1).replace('opening-binding-integration-20261026/result.md','selected-source-integration-20261026/result.md',1)
n='docs/design/README.md';value=before[n].decode();assert 'Version 5.9,' in value
proposed[n]=value.replace('Version 5.9,','Version 5.10,',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer\n\n'+note+'The full selected-source sequence is complete and integrated. Next: nonempty carried-opening audit, then its explicitly justified repair. No process is running. Main links select 5.10; standalone remains 5.5. Do not rerun completed preparation/advancement writers.\n'
remaining_text=(HERE.parent/'opening-binding-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0].replace('Version 5.9, 724 pages','Version 5.10, 726 pages')
remaining_text+='''## Next dependency

The complete selected source sequence is integrated: ordered eligibility,
opening checks, parameter/row recipes and full company programs. The source
path preserves 30 complete results except one declared serialization-order
identity. New operating books with nonempty claims still exceed the selected
empty-opening contract. Audit exact carried states and continuations under
docs/plans/accounting-nonempty-opening-audit-20261026.md before defining a
separate successor; keep complete claim/state/report obligations explicit.
This does not supply missing actual-company histories. Wider financial/fiscal
rules, sectors, primary-source gaps and independent acceptance remain open.
S6 held; E3 deferred; no whole requirement closes.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(scope.read_text())['groups'].items()};assert counts==dict(obligations=53,interactions=6,operations=46)
for n,b in before.items():q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(remaining_text)
for n,value in proposed.items():assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(value)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix);assert path.is_symlink() and target.exists()
    old=os.readlink(path);relative=os.path.relpath(target,path.parent);temporary=path.with_name(path.name+'.next');assert not temporary.exists() and not temporary.is_symlink()
    os.symlink(relative,temporary);os.replace(temporary,path);links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,next_plan=plan,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True))
build=json.loads((HERE/'build.json').read_text());git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',commands=['configure.py','integrate.py prepare','integrate.py build','integrate.py verify','repair.py','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],wall_time_scope='Final manuscript build',data_version=sha(scope),plan_file='docs/plans/accounting-selected-source-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.10',pages=726,controls=10,main_links=2,standalone_unchanged=True,next_plan=plan)))
