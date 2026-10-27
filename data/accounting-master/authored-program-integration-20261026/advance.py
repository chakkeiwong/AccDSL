"""Refresh current controls once, preserving every historical control."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
v=json.loads((HERE/'verification.json').read_text());assert v['passed_preservation'] and not v['new_warnings']
assert (HERE/'review.md').exists() and (HERE/'result.md').exists()
backup=HERE/'control-before';assert not backup.exists()
plan='docs/plans/accounting-authored-program-invariant-audit-20261026.md'
result='data/accounting-master/authored-program-integration-20261026/result.md'
remaining='data/accounting-master/authored-program-integration-20261026/remaining-work.md'
old=(ROOT/'data/accounting-master/method-timing-integration-20261026/remaining-work.md').read_text()
old=old.replace('Version 4.44, 539 pages','Version 4.46, 542 pages')
old=old.replace('Exact native information override awaits next coherent integration','Full native information-profile adoption remains open')
old=old.replace('Audit full CompanyBookMethod/1 authoring against existing requirement, monetary and memory grammars; author matched method definitions that use existing semantic validators','Connect the checked complete-method frontend to explicitly versioned registries; then verify program composition and reporting')
prefix=old[:old.index('## Next dependency:')]
tail=NL.join(['## Next dependency: cross-record invariant coverage','',
 'Complete method authoring, explicit v1/v2 registry calls and two eleven-command',
 'programs now have full retained-state/report/carry comparisons. Unknown and',
 'refused later commands preserve successful prefixes. Outer lifecycle controls',
 'still need a separate audit: claim totals versus receivables, event membership,',
 'dates and assessment snapshots. Equal happy paths do not establish equal',
 'refusal scope. Audit these checks before wider dynamic language expansion.',
 '', 'Execute '+plan+'. Broader sources, fiscal/sector methods and acceptance remain.',
 'No whole obligation closes. S6 held; E3 deferred.', ''])
(ROOT/remaining).write_text(prefix+tail)
note=NL.join(['## Authored program composition integrated — 26 October 2026','',
 'Version 4.46 is 542 pages, not_ready. A.54.9 explains authored registry',
 'dispatch and complete finite program composition. All 180 predecessor sources',
 'remain; no new warnings. Cover and physical pages 507–510 inspected.',
 'Next: audit outer lifecycle invariants and refusal scope. All 53 obligations,',
 'six interactions and 46 operations remain; S1–S5 partial, S6 held, E3 deferred.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={name:(ROOT/name).read_bytes() for name in targets}
for name,raw in before.items():
    p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
for name in concise:
    old=before[name].decode();tail=old[old.index('Mission:'):]
    tail=tail.replace('Current question: which native cross-record invariants remain outside authored programs?','Current question: which native cross-record invariants remain outside authored programs?')
    tail=tail.replace('docs/plans/accounting-authored-method-registry-20261026.md',plan)
    tail=tail.replace('data/accounting-master/method-timing-integration-20261026/remaining-work.md',remaining)
    tail=tail.replace('docs/design/proposal/manuscript-method-authoring-20261026/accounting-product-proposal.pdf',v['pdf'])
    tail=tail.replace('3cdfb69adfa669a75cb8902fc7ee45d25ed939a988f571b8204350cb784e576e',v['pdf_sha256'])
    (ROOT/name).write_text('# Current AccDSL master program'+NL*2+note+tail)
for name in historical:
    first,rest=before[name].decode().split(NL,1);(ROOT/name).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.46;542 pages;not_ready',
 'current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256'],'remaining_work':remaining}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Audit outer lifecycle invariants against authored programs','Bind explicit cross-record requirements using existing evaluators','Keep S6 held and S7/E3 deferred']
a['completed_increments'].append('Version4.46:542 pages;180 predecessor sources preserved;authored registry/program composition integrated')
a['latest_results'].append(result);p.write_text(json.dumps(d,indent=2)+NL)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);p.write_text(json.dumps(d,indent=2)+NL)
def dump(name,x):(HERE/name).write_text(json.dumps(x,indent=2)+NL)
dump('control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n,b in before.items()}})
dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/authored-program-integration-20261026/integrate.py prepare/build/verify (separate commands)',
 'environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic document build',
 'wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],'data_version':v['pdf_sha256'],
 'plan_file':'docs/plans/accounting-authored-program-integration-20261026.md','result_file':result,
 'artifact_paths':[v['pdf'],'baseline.json','build.json','verification.json','review.md','control-refresh.json']})
assert all(plan in (ROOT/n).read_text() for n in targets)
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.46, 542 pages, not_ready. Authored-program integration and ten-control refresh completed.'+NL+
 'Active plan: '+plan+NL+'Next: audit cross-record invariants and refusal scope in authored programs.'+NL+
 'Do not rerun completed integration/advance writers. E3 deferred; no background process running.'+NL)
print(json.dumps({'refreshed':len(targets),'candidate':updates['current_candidate'],'next_plan':plan}))
