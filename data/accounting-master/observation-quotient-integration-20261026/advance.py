"""Advance the verified Version 5.5 candidate and matching reading edition."""
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
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
v=json.loads((HERE/'verification.json').read_text())
assert v['passed_preservation'] and v['version']=='5.5'
main=v['documents']['accounting-product-proposal']; standalone=v['documents']['simulation-foundations']
assert main['pages']==719 and standalone['pages']==171 and v['standalone_body_pages']==155
for doc in (main,standalone):
    assert sha(ROOT/doc['pdf'])==doc['pdf_sha256'] and not doc['new_warnings'] and not doc['out_of_page_text_blocks']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
spec=importlib.util.spec_from_file_location('integration',HERE/'integrate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=json.loads((HERE/'source-preservation.json').read_text())
for n,h in p['sources'].items():
    assert sha(m.SOURCE/n)==h and (m.TARGET/n).read_text()==m.expected(n,(m.SOURCE/n).read_text())
for n,h in p['evidence'].items():assert sha(ROOT/n)==h
assert sha(m.TARGET/p['added_source'])==p['new_section_sha256']
assert sha(ROOT/p['standalone_baseline_pdf'])==p['standalone_baseline_sha256']
plan='docs/plans/accounting-event-specialization-audit-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
assert (ROOT/plan).exists()
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
controls=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
navigation=['MISSION_CONTROL.md','docs/README.md','docs/design/README.md','data/accounting-master/recovery-current-20261026.md']
before={n:(ROOT/n).read_bytes() for n in controls+navigation};backup=HERE/'control-before';assert not backup.exists()
note=f'''## Current governing candidate — Version 5.5 — 26 October 2026

Version 5.5 is the 719-page governing design candidate, not_ready. The matching
171-page simulation edition has 26 chapters and 155 body pages. Finite state
aggregation now has 12 exact full-path comparisons, eight rejected merges,
two explicit false-merge path comparisons and 38 boundary controls. Initial
information and joint dependence are retained; no probabilities are invented.
All 215 predecessor sources are protected under named cover and compression
chapter deltas; 25 other simulation chapters remain exact. Both builds pass
with no new warning. Main cover/pages 63–66 and standalone cover/pages 54–56
inspected. All 53 obligations, six interactions and 46 operations remain.
No whole requirement closes; S1–S5 partial, S6 held, E3 deferred.
PDF: {main['pdf']}
SHA256: {main['pdf_sha256']}.
Standalone PDF: {standalone['pdf']}
Standalone SHA256: {standalone['pdf_sha256']}.
Result: {result}.
Next plan: {plan}.

'''
proposed={}
for n in concise:
    tail='Mission:'+before[n].decode().split('Mission:',1)[1];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: which event-dependent financial specializations still require native Python rather than portable declarations? '
        elif line.startswith('Next action:'):line='Next action: audit and execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        lines.append(line)
    proposed[n]='# Current AccDSL master program\n\n'+note+'\n'.join(lines)+'\n'
for n in historical:
    first,rest=before[n].decode().split('\n',1);assert '## Current governing candidate — Version 5.4' in rest
    proposed[n]=first+'\n\n'+note+rest.replace('## Current governing candidate — Version 5.4','## Prior governing candidate — Version 5.4',1).lstrip('\n')
updates=dict(active_work_plan=plan,latest_result=result,current_candidate='5.5;719 pages;not_ready',current_pdf=main['pdf'],current_pdf_sha256=main['pdf_sha256'],remaining_work=remaining,standalone_pdf=standalone['pdf'],standalone_pdf_sha256=standalone['pdf_sha256'])
n='data/accounting-master/next-plan.json';d=json.loads(before[n]);a=d['active_execution'];a.update(updates)
a['completed_increments'].append('Version5.5:719 main/171 standalone pages;finite observation-preserving state aggregation;12 full path comparisons;8 rejected merges')
a['latest_results'].extend(['data/accounting-master/observation-quotient-20261026/result.md',result])
a['next']=['Audit native event specialization against complete authored methods','Map missing typed constructs and full-intent refusal obligations','Implement only a justified finite declarative extension; S6 held, E3 deferred']
proposed[n]=json.dumps(d,indent=2)+'\n'
n='scripts/accounting_master_catalog.json';d=json.loads(before[n]);d['active_execution_note'].update(updates);proposed[n]=json.dumps(d,indent=2)+'\n'
n='MISSION_CONTROL.md';t=before[n].decode();assert 'Version 5.4 is the current 718-page' in t
t=t.replace('Version 5.4 is the current 718-page','Version 5.5 is the current 719-page',1).replace('26 chapters and 154 body pages','26 chapters and 155 body pages',1)
old='The [current integration result](data/accounting-master/adopted-profile-integration-20261026/result.md) records common effect/composition readers for explicitly adopted profiles. The [active plan](docs/plans/accounting-observation-quotient-20261026.md) checks finite state compression against complete observable paths.'
assert old in t
proposed[n]=t.replace(old,f'The [current integration result]({result}) records finite observation-preserving state aggregation. The [active plan]({plan}) audits event specialization against complete authored methods and retained native requests.')
n='docs/README.md';t=before[n].decode();assert '**Version 5.4, 718 pages**' in t
proposed[n]=t.replace('**Version 5.4, 718 pages**','**Version 5.5, 719 pages**',1).replace('**170 pages**','**171 pages**',1).replace('**154 body pages**','**155 body pages**',1).replace('adopted-profile-integration-20261026/result.md','observation-quotient-integration-20261026/result.md',1)
n='docs/design/README.md';t=before[n].decode();assert 'Version 5.4,' in t
proposed[n]=t.replace('Version 5.4,','Version 5.5,',1).replace('154 body pages','155 body pages',1)
proposed['data/accounting-master/recovery-current-20261026.md']='# Current recovery pointer\n\n'+note+'Finite quotient implementation and both document builds are complete. Next: event-specialization audit.\nTen controls agree; all four stable links select Version 5.5. Do not rerun completed writers. No background process running.\n'
prior=(HERE.parent/'adopted-profile-integration-20261026/remaining-work.md').read_text().split('## Next dependency',1)[0]
prior=prior.replace('Version 5.4, 718 pages','Version 5.5, 719 pages')
prior+=f'''## Next dependency

Finite state compression now has exact supplied-law/relation conformance:
12 complete path comparisons, eight rejected merges and 38 boundary controls.
This does not identify a sufficient economic state from real disclosures.
The full event-intent contract still delegates specialization to a named native
Python owner. Audit {plan} before choosing a portable extension.
Retain the complete authored methods, explicit invariants, 22 command outcomes
and 18 native refusals; do not rebuild them as missing.
Broader fiscal/measurement methods, actual-source histories, sector/group
composition, technical source gaps and independent acceptance remain.
The 26 simulation chapters, 67 failure mechanisms and original 169 teaching
checks remain; new finite conformance evidence is separate. S6 held; E3 deferred.
'''
scope=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(scope.read_text())['groups'].items()};assert counts=={'obligations':53,'interactions':6,'operations':46}
for n,b in before.items():q=backup/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
(HERE/'remaining-work.md').write_text(prior)
for n,t in proposed.items():
    assert (ROOT/n).read_bytes()==before[n],n
    (ROOT/n).write_text(t)
links=[]
for alias,stem in [('AccDSL-latest','accounting-product-proposal'),('AccDSL-simulation-foundations','simulation-foundations')]:
    for suffix in ('pdf','tex'):
        path=ROOT/('docs/'+alias+'.'+suffix);target=m.TARGET/(stem+'.'+suffix);assert path.is_symlink() and target.exists()
        old=os.readlink(path);relative=os.path.relpath(target,path.parent);temp=path.with_name(path.name+'.next')
        assert not temp.exists() and not temp.is_symlink();os.symlink(relative,temp);os.replace(temp,path)
        links.append(dict(path=str(path.relative_to(ROOT)),before_target=old,after_target=relative,sha256=sha(path)))
for n in controls:assert plan in (ROOT/n).read_text() and main['pdf_sha256'] in (ROOT/n).read_text()
dump('control-refresh.json',dict(next_plan=plan,updated_files={n:dict(before=sha256(b).hexdigest(),after=sha(ROOT/n)) for n,b in before.items()},links=links,ten_controls_agree=True,original_scope=counts,whole_requirements_closed=0,standalone_updated=True,standalone_pdf_sha256=standalone['pdf_sha256']))
build=json.loads((HERE/'build.json').read_text())
dump('run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),commands=['integrate.py prepare','integrate.py build (both documents passed)','integrate.py verify (two parser failures, repaired third passed)','advance.py'],environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=sum(x['wall_seconds'] for x in build.values()),wall_time_scope='Main and standalone builds',builds=build,data_version=sha(scope),plan_file='docs/plans/accounting-observation-quotient-integration-20261026.md',result_file=result,artifact_paths=['source-preservation.json','verification.json','verification-repair.md','review.md','control-refresh.json','remaining-work.md'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(candidate=updates['current_candidate'],standalone_pages=171,controls=len(controls),links=len(links),next_plan=plan)))
