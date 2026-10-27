from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,x):(HERE/name).write_text(json.dumps(x,indent=2)+NL)
start=time.monotonic();baseline=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
original_sha=sha(baseline);original=json.loads(baseline.read_text());counts={k:len(v) for k,v in original['groups'].items()}
assert counts=={'obligations':53,'interactions':6,'operations':46}
integration=HERE.parent/'event-contract-integration-20261026';v=json.loads((integration/'verification.json').read_text())
assert v['passed_preservation'] and not v['new_warnings'] and v['version']=='4.48'
assert sha(ROOT/v['pdf'])==v['pdf_sha256'] and (integration/'review.md').exists()
units=['complete-method-authoring','authored-method-registry','authored-program-composition','authored-program-invariant-audit','authored-state-invariants','authored-event-prerequisite-audit','authored-event-contract']
results={}
for unit in units:
    folder=HERE.parent/(unit+'-20261026');checks=json.loads((folder/'checks.json').read_text());assert checks['passed']
    results[unit]={'checks_sha256':sha(folder/'checks.json'),'result_sha256':sha(folder/'result.md')}
plan='docs/plans/accounting-common-program-authoring-audit-20261026.md';result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'];backup=HERE/'control-before';assert not backup.exists()
before={n:(ROOT/n).read_bytes() for n in targets}
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
note=NL.join(['## Method-to-program evidence and queue refreshed — 26 October 2026','',
 'Version 4.48 is 544 pages, not_ready. Complete method text, explicit registries,',
 '22 program commands, sixteen repaired state counterexamples and eighteen',
 'matched event-contract refusals now have bounded evidence. All 182 predecessor',
 'manuscript sources preserved; no new warnings. Cover/pages 509–511 inspected.',
 'All 53 obligations, six interactions and 46 operations remain. S1–S5 partial;',
 'S6 held, E3 deferred. Next: coherent complete-program authoring inventory.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
for n in concise:
    old=before[n].decode();tail=old[old.index('Mission:'):];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: how can methods, registries, invariants and intent be authored coherently?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        elif line.startswith('PDF:'):line='PDF: '+v['pdf']
        elif line.startswith('SHA256:'):line='SHA256: '+v['pdf_sha256']+'.'
        lines.append(line)
    (ROOT/n).write_text('# Current AccDSL master program'+NL*2+note+NL.join(lines)+NL)
for n in historical:
    first,rest=before[n].decode().split(NL,1);(ROOT/n).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.48;544 pages;not_ready','current_pdf':v['pdf'],
 'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Inventory common program source fields and existing parser/semantic owners','Specify coherent bounded program authoring and compare full results','Reassess broader sources/methods after this unit; keep S6 held and E3 deferred']
a['completed_increments'].append('Version4.48:544 pages;complete method-to-program/state/intent evidence integrated;53/6/46 queue refreshed')
a['latest_results'].extend([str((integration/'result.md').relative_to(ROOT)),result]);p.write_text(json.dumps(d,indent=2)+NL)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);p.write_text(json.dumps(d,indent=2)+NL)
assert sha(baseline)==original_sha
for n in targets:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text(),n
checks={'passed':True,'original_scope':counts,'original_sha256':original_sha,'candidate':updates['current_candidate'],
 'pdf_sha256':v['pdf_sha256'],'checked_increment_results':results,'refreshed_controls':len(targets),'whole_requirements_closed':0}
dump('checks.json',checks)
dump('control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha(ROOT/n)} for n,b in before.items()}})
dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'command':'python3 data/accounting-master/post-authoring-program-refresh-20261026/refresh.py','environment':sys.version,
 'cpu_gpu':'CPU; no framework/GPU use','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,
 'data_version':original_sha,'plan_file':'docs/plans/accounting-post-authoring-program-refresh-20261026.md','result_file':result,
 'artifact_paths':['checks.json','control-refresh.json','remaining-work.md'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.48, 544 pages, not_ready. PDF: '+v['pdf']+NL+'SHA256: '+v['pdf_sha256']+NL+
 'Active plan: '+plan+NL+'Next: inventory exact program fields and existing text/semantic owners.'+NL+
 'All completed writers preserved. No background process running. E3 deferred.'+NL)
print(json.dumps({'refreshed_controls':10,'original_scope':counts,'candidate':updates['current_candidate'],'next_plan':plan}))
