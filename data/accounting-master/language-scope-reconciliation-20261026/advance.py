"""Complete the saved 4.50 checkpoint without replaying predecessor writers."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+NL)
v=json.loads((HERE/'verification.json').read_text())
assert v['version']=='4.50' and v['passed_preservation'] and not v['new_warnings']
assert sha(ROOT/v['pdf'])==v['pdf_sha256'] and (HERE/'review.md').exists()
plan='docs/plans/accounting-exact-bank-request-conformance-20261026.md'
result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
backup=HERE/'control-before';assert not backup.exists()
before={n:(ROOT/n).read_bytes() for n in targets}
for n,b in before.items():
 p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
note=NL.join(['## Language scope reconciled — 26 October 2026','',
 'Version 4.50 is 546 pages, not_ready. Chapter 7 now distinguishes current',
 'authoring responsibilities, imported rules and remaining language gaps.',
 'All 31 previous scope references and 184 predecessor sources are preserved.',
 'No new warnings; cover and physical pages 98–102 inspected.',
 'All 53 obligations, six interactions and 46 operations remain. S1–S5 partial;',
 'S6 held and E3 deferred. Next: complete-request exact banking timing checks.',
 'PDF: '+v['pdf'],'SHA256: '+v['pdf_sha256']+'.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
for n in concise:
 old=before[n].decode();tail=old[old.index('Mission:'):]
 lines=[]
 for line in tail.splitlines():
  if line.startswith('Current question:'):line='Current question: do exact information-time rules preserve full bank request/refusal/publication semantics?'
  elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
  elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
  lines.append(line)
 (ROOT/n).write_text('# Current AccDSL master program'+NL*2+note+NL.join(lines)+NL)
for n in historical:
 first,rest=before[n].decode().split(NL,1);(ROOT/n).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.50;546 pages;not_ready',
 'current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Inspect complete banking request dependency and publication ownership','Test exact information timing on repinned complete request/response fixtures','Determine explicit schema/profile adoption boundary; preserve S6 hold and E3 deferral']
a['completed_increments'].append('Version4.50:546 pages;main language scope reconciled;31 previous references retained;semantic/source identity checked')
a['latest_results'].append(result);dump(p,d)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);dump(p,d)
prior=(HERE.parent/'common-program-authoring-integration-20261026/remaining-work.md').read_text()
prior=prior[:prior.index('## Next dependency')].replace('Version 4.49, 545 pages','Version 4.50, 546 pages')
prior=prior.replace('reconcile main explanation, then extend','retain reconciled main explanation, then extend')
(HERE/'remaining-work.md').write_text(prior+NL.join(['## Next dependency','',
 'Common program source and the main language scope repair are complete within',
 'their declared finite bounds. All original obligations remain open at whole',
 'requirement level. Wider accounting methods, real-source partial histories,',
 'group/sector state, source/version gaps and full-document acceptance remain.','',
 'Execute '+plan+'.',
 'The exact bank information checker has eleven isolated information cases and',
 '271 retained response checks. Complete derived request/response fixtures are',
 'still missing. Test those before any claim of successor profile adoption.',
 'No general native migration, real timestamp authenticity or accounting',
 'authority follows. Source gaps block only their dependent claims; do not',
 'repeat exhausted Gentry/ACTUS routes without new leads.','']))
original=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
counts={k:len(x) for k,x in json.loads(original.read_text())['groups'].items()};assert counts=={'obligations':53,'interactions':6,'operations':46}
for n in targets:assert plan in (ROOT/n).read_text() and v['pdf_sha256'] in (ROOT/n).read_text(),n
dump(HERE/'control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha(ROOT/n)} for n,b in before.items()},'original_scope':counts,'whole_requirements_closed':0})
dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'commands':['audit_baseline.py','identity_probe.py','reconcile.py prepare','reconcile.py build','reconcile.py verify','advance.py'],
 'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic',
 'wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],'wall_time_scope':'Build only; narrative authoring not timed',
 'data_version':sha(original),'plan_file':'docs/plans/accounting-language-scope-reconciliation-20261026.md','result_file':result,
 'artifact_paths':['baseline.json','source-preservation.json','identity-check.json','verification.json','review.md','content-map.md','control-refresh.json'],
 'timestamp_utc':datetime.now(timezone.utc).isoformat()})
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.50, 546 pages, not_ready. PDF: '+v['pdf']+NL+'SHA256: '+v['pdf_sha256']+NL+
 'Active plan: '+plan+NL+'Next: inspect and derive full banking timing requests.'+NL+
 'Ten controls agree. Completed writers remain protected. No background process running.'+NL+
 'Original scope 53/6/46 retained; S6 held; E3 deferred.'+NL)
print(json.dumps({'candidate':updates['current_candidate'],'controls':len(targets),'next_plan':plan}))
