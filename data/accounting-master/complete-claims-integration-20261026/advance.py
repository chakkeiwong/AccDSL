"""Advance only the checked Version 5.11 candidate and current pointers."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util, json, os, subprocess, sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def sha(p): return sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def dump(name, value): (HERE/name).write_text(json.dumps(value, indent=2)+'\n')
v = read(HERE/'verification.json')
assert v['passed_preservation'] and v['version']=='5.11' and v['pages']==728
assert not v['new_warnings'] and not v['out_of_page_text_blocks']
assert sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
spec=importlib.util.spec_from_file_location('integration', HERE/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=read(HERE/'source-preservation.json')
for n,h in p['sources'].items():
    assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items(): assert sha(ROOT/n)==h,n
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
standalone='1a39bd1e7e1e3c7e36d914cf324660d135808bb5fe4c21982bdc324791b4ef43'
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
plan='docs/plans/accounting-post-opening-language-reassessment-20261026.md'
assert (ROOT/plan).exists()
result=str((HERE/'result.md').relative_to(ROOT))
remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation}
backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.11 — 26 October 2026

Version 5.11 is the 728-page governing design candidate, not_ready. Complete
supplied carried-claim openings and their explicit source are integrated.
Four carried programs preserve ten commands; four empty programs preserve
44 commands. The source run passes 32 controls/787 assertions with 393 protected
files. Only two named program serialization-order digests differ; both are
recomputed. Full execution and event-input order remain exact, with native
lifecycle/builder disabled. All 221 predecessor manuscript sources are protected
under four named edits. All 26 simulation chapters and standalone Version 5.5
(171 pages/155 body pages) remain exact. No new warnings; cover, pages 268–269
and 691–696 inspected. All 53 obligations, six interactions and 46 operations
remain; no whole requirement closes. S1–S5 partial, S6 held, E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for n in concise:
    tail='Mission:'+before[n].decode().split('Mission:',1)[1]
    lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'): line='Current question: which consequential language/composition gap remains after the checked live-opening extension and earlier history/partial-population work?'
        elif line.startswith('Next action:'): line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'): line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='# Current AccDSL master program\n\n'+note+'\n'.join(lines)+'\n'
for n in history:
    first,rest=before[n].decode().split('\n',1)
    assert '## Current governing candidate — Version 5.10' in rest,n
    proposed[n]=first+'\n\n'+note+rest.replace('## Current governing candidate — Version 5.10','## Prior governing candidate — Version 5.10',1).lstrip('\n')
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.11;728 pages;not_ready',current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,latest_internal_result='data/accounting-master/complete-claims-source-20261026/result.md')
for n in controls[-2:]:
    d=json.loads(before[n]);a=d.get('active_execution',d.get('active_execution_note'));a.update(updates)
    if 'completed_increments' in a:a['completed_increments'].append('Version5.11:728 pages;complete supplied claim openings and source;8 programs/54 commands;32 source controls;two exact order-identity exceptions')
    if 'latest_results' in a:a['latest_results'].extend([updates['latest_internal_result'],result])
    a['next']=['Reassess actual language and partial-history dependencies without rebuilding completed bridges','Select a consequential bounded repair with exact existing comparator','Preserve broader financial/source/acceptance residuals; S6 held; E3 deferred']
    proposed[n]=json.dumps(d,indent=2)+'\n'
n='MISSION_CONTROL.md';value=before[n].decode()
assert 'Version 5.10 is the current 726-page' in value
value=value.replace('Version 5.10 is the current 726-page','Version 5.11 is the current 728-page',1)
lines=value.splitlines()
for i,line in enumerate(lines):
    if line.startswith('The [current integration result]'):
        lines[i]=f'The [current integration result]({result}) records complete supplied carried-claim openings and exact source correspondence. The [active plan]({plan}) reassesses the next language dependency against existing history, population and fiscal work.';break
else:raise AssertionError('mission_current_link')
proposed[n]='\n'.join(lines)+'\n'
n='docs/README.md';value=before[n].decode();assert '**Version 5.10, 726 pages**' in value
proposed[n]=value.replace('**Version 5.10, 726 pages**','**Version 5.11, 728 pages**',1).replace('selected-source-integration-20261026/result.md','complete-claims-integration-20261026/result.md',1)
n='docs/design/README.md';value=before[n].decode();assert 'Version 5.10,' in value
proposed[n]=value.replace('Version 5.10,','Version 5.11,',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer\n\n'+note+'Complete-claims typed and source evidence is frozen and integrated. Next: audited post-opening language reassessment. Main links select 5.11; standalone stays 5.5. No process is running. Do not rerun completed preparation, verification writers or advancement scripts.\n'
remaining_text=(HERE.parent/'selected-source-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0].replace('Version 5.10, 726 pages','Version 5.11, 728 pages')
remaining_text+='''## Next dependency

Live carried openings now have a separately selected complete-supplied-state
contract and explicit source. Four carried and four empty programs retain
54 commands and complete results under two checked order-identity exceptions.
Partial/unknown populations remain unresolved and five corrupt states refuse.
The next plan audits the remaining language boundary against already completed
conditional history/opening/continuation, partial population, prospective term
history and fiscal work. Avoid rebuilding those completed mechanisms. Missing
actual issuer claims cannot be replaced by synthetic completeness premises.
Wider financial algorithms, source/version gaps and independent acceptance
remain. S6 held; E3 deferred; no whole requirement closes.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in read(scope)['groups'].items()}
assert counts==dict(obligations=53,interactions=6,operations=46)
for n,b in before.items():q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(remaining_text)
for n,value in proposed.items():assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(value)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix)
    assert path.is_symlink() and target.exists()
    old=os.readlink(path);relative=os.path.relpath(target,path.parent)
    temporary=path.with_name(path.name+'.next');assert not temporary.exists() and not temporary.is_symlink()
    os.symlink(relative,temporary);os.replace(temporary,path)
    links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==standalone
dump('control-refresh.json',dict(updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,next_plan=plan,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True))
build=read(HERE/'build.json');git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',commands=['configure.py','integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],wall_time_scope='Manuscript build',data_version=sha(scope),plan_file='docs/plans/accounting-complete-claims-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate='5.11',pages=728,controls=10,main_links=2,standalone_unchanged=True,next_plan=plan)))
