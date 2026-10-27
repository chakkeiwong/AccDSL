from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util
import json
import os
import subprocess
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+chr(10))
v=json.loads((HERE/'verification.json').read_text());assert v['passed_preservation'] and v['version']=='5.6' and v['pages']==720
assert not v['new_warnings'] and not v['out_of_page_text_blocks'] and sha(ROOT/v['pdf'])==v['pdf_sha256']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
s=importlib.util.spec_from_file_location('integration',HERE/'integrate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=json.loads((HERE/'source-preservation.json').read_text())
for n,h in p['sources'].items():assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text()),n
for n,h in p['evidence'].items():assert sha(ROOT/n)==h,n
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
prior=json.loads((HERE.parent/'observation-quotient-integration-20261026/verification.json').read_text())['documents']['simulation-foundations']
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==prior['pdf_sha256']
plan='docs/plans/accounting-event-eligibility-audit-20261026.md';assert (ROOT/plan).exists()
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
history=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+history+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation};backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.6 — 26 October 2026

Version 5.6 is the 720-page governing design candidate, not_ready. Typed
parameters preserve 18 complete sale/collection requests and transitions;
ordered claim expansion preserves 20 assessments. Both construct with native
specialization disabled, while native full-intent eligibility stays explicit.
All 216 predecessor sources are protected under the cover/input insertion
delta. Simulation content is unchanged; the 171-page standalone remains at
verified Version 5.5, with 26 chapters and 155 body pages. No new warnings.
Cover/pages 683–686 inspected. All 53 obligations, six interactions and 46
operations remain; no whole requirement closes. S1–S5 partial, S6 held, E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for n in concise:
    tail='Mission:'+before[n].decode().split('Mission:',1)[1];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: can full-intent eligibility preserve exact native failure ordering through explicit declarations?'
        elif line.startswith('Next action:'):line='Next action: audit and execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='# Current AccDSL master program'+chr(10)*2+note+chr(10).join(lines)+chr(10)
for n in history:
    first,rest=before[n].decode().split(chr(10),1);assert '## Current governing candidate — Version 5.5' in rest
    proposed[n]=first+chr(10)*2+note+rest.replace('## Current governing candidate — Version 5.5','## Prior governing candidate — Version 5.5',1).lstrip(chr(10))
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.6;720 pages;not_ready',current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining,latest_internal_result='data/accounting-master/ordered-assessment-expansion-20261026/result.md')
n='data/accounting-master/next-plan.json';d=json.loads(before[n]);a=d['active_execution'];a.update(updates)
a['completed_increments'].append('Version5.6:720 pages;18 parameterized requests/transitions;20 ordered assessments;native eligibility explicit')
a['latest_results'].extend(['data/accounting-master/event-specialization-audit-20261026/result.md','data/accounting-master/parameterized-method-construction-20261026/result.md','data/accounting-master/ordered-assessment-expansion-20261026/result.md',result])
a['next']=['Audit full-intent eligibility and exact failure precedence','Reuse existing guarded predicates with explicit binding/date requirements','Implement a finite ordered gate only after audit; S6 held, E3 deferred']
proposed[n]=json.dumps(d,indent=2)+chr(10)
n='scripts/accounting_master_catalog.json';d=json.loads(before[n]);d['active_execution_note'].update(updates);proposed[n]=json.dumps(d,indent=2)+chr(10)
n='MISSION_CONTROL.md';t=before[n].decode();assert 'Version 5.5 is the current 719-page' in t
t=t.replace('Version 5.5 is the current 719-page','Version 5.6 is the current 720-page',1)
lines=t.splitlines();found=False
for i,line in enumerate(lines):
    if line.startswith('The [current integration result]'):
        lines[i]=f'The [current integration result]({result}) records typed parameter and ordered claim construction. The [active plan]({plan}) audits full-intent eligibility and exact failure ordering.';found=True;break
assert found;proposed[n]=chr(10).join(lines)+chr(10)
n='docs/README.md';t=before[n].decode();assert '**Version 5.5, 719 pages**' in t
proposed[n]=t.replace('**Version 5.5, 719 pages**','**Version 5.6, 720 pages**',1).replace('observation-quotient-integration-20261026/result.md','method-specialization-integration-20261026/result.md',1)
n='docs/design/README.md';t=before[n].decode();assert 'Version 5.5,' in t;proposed[n]=t.replace('Version 5.5,','Version 5.6,',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer'+chr(10)*2+note+'Parameter construction and ordered assessment are complete; Version 5.6 is integrated and verified. Next: full-intent eligibility audit. Ten controls agree. Main links select 5.6; unchanged standalone links select verified 5.5. Do not rerun completed writers. No background process running.'+chr(10)
remaining_text=(HERE.parent/'observation-quotient-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0].replace('Version 5.5, 719 pages','Version 5.6, 720 pages')
remaining_text+=f'''## Next dependency

Typed scalar construction and ordered claim expansion are checked: 18 and 20
complete requests/transitions, including consequential variants and explicit
order identity. Native full-intent eligibility remains a named dependency.
Execute {plan}. Preserve the prior 22 complete command results and 18 refusals;
probe multi-failure precedence before substituting a flat guarded manifest.
Broader financial/fiscal methods, actual-source partial histories, wider
sector/group composition, primary source gaps and independent acceptance remain.
The finite observation quotient and all 26 simulation chapters remain credited.
S6 held, E3 deferred; no whole requirement closes.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(scope.read_text())['groups'].items()};assert counts=={'obligations':53,'interactions':6,'operations':46}
for n,b in before.items():q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(remaining_text)
for n,t in proposed.items():assert (ROOT/n).read_bytes()==before[n];(ROOT/n).write_text(t)
links=[]
for suffix in ('pdf','tex'):
    path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix);assert path.is_symlink() and target.exists()
    old=os.readlink(path);relative=os.path.relpath(target,path.parent);temp=path.with_name(path.name+'.next');assert not temp.exists() and not temp.is_symlink()
    os.symlink(relative,temp);os.replace(temp,path);links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for n in controls:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text()
assert sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==prior['pdf_sha256']
dump('control-refresh.json',dict(next_plan=plan,updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,standalone_pdf_sha256=prior['pdf_sha256']))
build=json.loads((HERE/'build.json').read_text())
dump('run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),commands=['configure.py','integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=build['wall_seconds'],wall_time_scope='Main manuscript build',data_version=sha(scope),plan_file='docs/plans/accounting-method-specialization-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate=updates['current_candidate'],controls=len(controls),main_links=len(links),standalone_unchanged=True,next_plan=plan)))
