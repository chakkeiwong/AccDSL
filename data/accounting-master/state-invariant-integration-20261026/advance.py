from pathlib import Path
from hashlib import sha256
import json,sys,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
v=json.loads((HERE/'verification.json').read_text());assert v['passed_preservation'] and not v['new_warnings']
assert (HERE/'review.md').exists();backup=HERE/'control-before';assert not backup.exists()
plan='docs/plans/accounting-authored-event-contract-20261026.md';result=str((HERE/'result.md').relative_to(ROOT));remaining=str((HERE/'remaining-work.md').relative_to(ROOT))
prior=(HERE.parent/'authored-program-integration-20261026/remaining-work.md').read_text()
prior=prior[:prior.index('## Next dependency:')].replace('Version 4.46, 542 pages','Version 4.47, 543 pages')
prior+=NL.join(['## Next dependency: full event intent and selected contract','',
 'The original authored program now has an explicit state-invariant successor:',
 '22 commands preserved; 16 counterexamples refused. Event intent remains separate.',
 'Two sealed-window probes and four intent-loss cases require complete original',
 'events and a named specialization/eligibility contract. Execute '+plan+'.',
 'General portable specialization, broader sources/methods and acceptance remain.',
 'No whole obligation closes. S6 held; E3 deferred.',''])
(ROOT/remaining).write_text(prior)
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json'];before={n:(ROOT/n).read_bytes() for n in targets}
for n,b in before.items():p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
note=NL.join(['## State invariants integrated — 26 October 2026','',
 'Version 4.47 is 543 pages, not_ready. A.54.10 explains sixteen counterexamples',
 'and the explicit state-guard repair. All 181 predecessor sources remain;',
 'no new warnings. Cover and physical pages 508–511 inspected.',
 'Next: full event intent and selected lifecycle eligibility/specialization.',
 'All 53 obligations, six interactions and 46 operations remain. S1–S5 partial;',
 'S6 held, E3 deferred.','Result: '+result+'.','Next plan: '+plan+'.','',''])
for n in concise:
    old=before[n].decode();tail=old[old.index('Mission:'):];lines=[]
    for line in tail.splitlines():
        if line.startswith('Current question:'):line='Current question: how can original event intent govern authored method specialization?'
        elif line.startswith('Next action:'):line='Next action: execute '+plan+'.'
        elif line.startswith('Current residuals:'):line='Current residuals: '+remaining+'.'
        elif line.startswith('PDF:'):line='PDF: '+v['pdf']
        elif line.startswith('SHA256:'):line='SHA256: '+v['pdf_sha256']+'.'
        lines.append(line)
    (ROOT/n).write_text('# Current AccDSL master program'+NL*2+note+NL.join(lines)+NL)
for n in historical:
    first,rest=before[n].decode().split(NL,1);(ROOT/n).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.47;543 pages;not_ready',
 'current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Retain complete event intent and exact selected native lifecycle contract','Check original refusal scope and full program results','Keep S6 held and S7/E3 deferred']
a['completed_increments'].append('Version4.47:543 pages;181 sources preserved;16 state counterexamples repaired;event intent audit completed')
a['latest_results'].append(result);p.write_text(json.dumps(d,indent=2)+NL)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);p.write_text(json.dumps(d,indent=2)+NL)
def dump(name,x):(HERE/name).write_text(json.dumps(x,indent=2)+NL)
dump('control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n,b in before.items()}})
dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/state-invariant-integration-20261026/integrate.py prepare/build/verify (separate calls)',
 'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic build',
 'wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],'data_version':v['pdf_sha256'],
 'plan_file':'docs/plans/accounting-state-invariant-integration-20261026.md','result_file':result,
 'artifact_paths':[v['pdf'],'baseline.json','verification.json','review.md','control-refresh.json']})
assert all(plan in (ROOT/n).read_text() for n in targets)
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.47, 543 pages, not_ready. State guard integration/control refresh complete.'+NL+
 'Active plan: '+plan+NL+'Next: implement selected full-intent lifecycle contract and verify original refusals.'+NL+
 'No background process running. E3 deferred. Preserve frozen sources and completed writers.'+NL)
print(json.dumps({'refreshed':len(targets),'candidate':updates['current_candidate'],'next_plan':plan}))
