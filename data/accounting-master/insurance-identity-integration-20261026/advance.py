"""Advance checked 5.3 controls without rerunning any predecessor writer."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
v=json.loads((HERE/'verification.json').read_text())
assert v['version']=='5.3' and v['pages']==717 and v['passed_preservation']
assert not v['new_warnings'] and not v['out_of_page_text_blocks']
assert sha(ROOT/v['pdf'])==v['pdf_sha256'] and (HERE/'review.md').exists() and (HERE/'result.md').exists()
spec=importlib.util.spec_from_file_location('integration',HERE/'integrate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads((HERE/'source-preservation.json').read_text())
for name,h in p['sources'].items():
 assert sha(m.SOURCE/name)==h and (m.TARGET/name).read_text()==m.expected(name,(m.SOURCE/name).read_text())
for name,h in p['evidence'].items(): assert sha(ROOT/name)==h
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
plan='docs/plans/accounting-adopted-profile-effects-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
assert (ROOT/plan).exists()
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation}
backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.3 — 26 October 2026

Version 5.3 is the 717-page governing design candidate, not_ready. Explicit
insurer identity-policy adoption preserves 672 native exchanges and converts
127 worlds without financial changes. Two colliding identities now post and
replay correctly; 686 saved exchanges revalidate. All 213 predecessor sources
are preserved under the recorded prose delta; all 26 simulation chapters remain.
No new warnings. Cover/pages 516–518 inspected. All 53 obligations, six interactions
and 46 operations remain; no whole requirement closes. S1–S5 partial, S6 held,
E3 deferred.
PDF: {v['pdf']}
SHA256: {v['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for name in concise:
 tail='Mission:'+before[name].decode().split('Mission:',1)[1]
 lines=[]
 for line in tail.splitlines():
  if line.startswith('Current question:'):line='Current question: can common effect/composition readers preserve adopted profile and identity-policy bindings?'
  elif line.startswith('Next action:'):line='Next action: audit and execute '+plan+'.'
  elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
  lines.append(line)
 proposed[name]='# Current AccDSL master program\n\n'+note+'\n'.join(lines)+'\n'
for name in historical:
 first,rest=before[name].decode().split('\n',1)
 rest=rest.replace('## Current governing candidate — Version 5.2','## Prior governing candidate — Version 5.2',1)
 proposed[name]=first+'\n\n'+note+rest.lstrip('\n')
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.3;717 pages;not_ready',current_pdf=v['pdf'],current_pdf_sha256=v['pdf_sha256'],remaining_work=remaining)
name='data/accounting-master/next-plan.json';d=json.loads(before[name]);a=d['active_execution'];a.update(updates)
a['completed_increments'].append('Version5.3:717 pages;insurer identity execution policy;672 native exchanges preserved;127 migrated worlds;686 saved exchanges')
a['latest_results'].extend(['data/accounting-master/insurance-identity-adoption-20261026/result.md',result])
a['next']=['Audit exact successor provider bindings in effect/composition readers','Preserve complete native effects, policy identity and dependency refusals','Integrate checked common-interface result; S6 held, E3 deferred']
proposed[name]=json.dumps(d,indent=2)+'\n'
name='scripts/accounting_master_catalog.json';d=json.loads(before[name]);d['active_execution_note'].update(updates);proposed[name]=json.dumps(d,indent=2)+'\n'
name='MISSION_CONTROL.md';t=before[name].decode();assert 'Version 5.2 is the current 716-page' in t
t=t.replace('Version 5.2 is the current 716-page','Version 5.3 is the current 717-page',1)
old='The [current integration result](data/accounting-master/invariant-source-integration-20261026/result.md) records explicit finite invariant authoring and preserved simulation content. The [active plan](docs/plans/accounting-insurance-identity-adoption-20261026.md) audits insurer request identity with complete financial publication and recovery.'
assert old in t
proposed[name]=t.replace(old,f'The [current integration result]({result}) records insurer identity adoption with preserved financial publications. The [active plan]({plan}) extends common effect/composition descriptions to the explicitly adopted profiles.')
name='docs/README.md';proposed[name]=before[name].decode().replace('**Version 5.2, 716 pages**','**Version 5.3, 717 pages**',1).replace('invariant-source-integration-20261026/result.md','insurance-identity-integration-20261026/result.md',1)
name='docs/design/README.md';proposed[name]=before[name].decode().replace('Version 5.2,','Version 5.3,',1)
name='data/accounting-master/recovery-current-20261026.md';proposed[name]='# Current recovery pointer\n\n'+note+'Next: explicit adopted-profile bindings in common effect/composition readers. Insurer adoption and manuscript integration are complete.\nTen controls agree. Main links select 5.3; unchanged standalone links retain the verified 5.1 reading edition.\nDo not rerun completed writers. No background process running.\n'
prior=(HERE.parent/'invariant-source-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0]
prior=prior.replace('Version 5.2, 716 pages','Version 5.3, 717 pages').replace('Bank exact-time adoption now has finite documentary evidence; insurer identity adoption and general migration remain','Bank exact-time and insurer identity adoption have finite documentary evidence; common reader adoption and general migration remain')
prior+=f'''## Next dependency

Finite invariant source, bank exact-time profile adoption and insurer identity
execution-policy adoption are complete. The insurer repair preserves exact
financial requests and 672 original exchanges; it does not rewrite the financial
profile or infer erased history. Execute {plan}.
Common effect/composition readers still pin legacy packets and world shapes.
Admit the checked successors through explicit source/policy bindings and complete
effect comparisons, retaining the unsupported cross-profile state adapter.

Broader rule authoring, fiscal/measurement methods, actual-source histories,
sector/group composition, source gaps and independent whole-document acceptance
remain. All 26 simulation chapters and their 67 failure mechanisms/169 teaching
checks remain; none releases S6 or E3. Do not repeat exhausted source routes.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(scope.read_text())['groups'].items()};assert counts=={'obligations':53,'interactions':6,'operations':46}
standalone=ROOT/'docs/AccDSL-simulation-foundations.pdf';old=json.loads((HERE.parent/'invariant-source-integration-20261026/control-refresh.json').read_text());assert sha(standalone)==old['standalone_pdf_sha256']
for name,b in before.items():
 q=backup/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(prior)
for name,t in proposed.items():
 assert (ROOT/name).read_bytes()==before[name],'concurrent_control_change:'+name
 (ROOT/name).write_text(t)
links=[]
for suffix in ('pdf','tex'):
 path=ROOT/('docs/AccDSL-latest.'+suffix);target=m.TARGET/('accounting-product-proposal.'+suffix)
 assert path.is_symlink() and target.exists()
 old=os.readlink(path);relative=os.path.relpath(target,path.parent);temp=path.with_name(path.name+'.next')
 assert not temp.exists() and not temp.is_symlink();os.symlink(relative,temp);os.replace(temp,path)
 links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for name in controls:assert plan in (ROOT/name).read_text() and v['pdf_sha256'] in (ROOT/name).read_text()
dump(HERE/'control-refresh.json',dict(next_plan=plan,updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_unchanged=True,standalone_pdf_sha256=sha(standalone)))
dump(HERE/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),commands=['integrate.py prepare','integrate.py build','integrate.py verify','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=json.loads((HERE/'build.json').read_text())['wall_seconds'],wall_time_scope='Main manuscript build only',data_version=sha(scope),plan_file='docs/plans/accounting-insurance-identity-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate=updates['current_candidate'],controls=len(controls),main_links=len(links),standalone_unchanged=True,next_plan=plan)))
