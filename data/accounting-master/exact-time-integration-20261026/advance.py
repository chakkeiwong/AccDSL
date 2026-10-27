"""One-time manuscript routing refresh; preserve historical controls."""
import json,subprocess,sys
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
v=json.loads((HERE/'verification.json').read_text());assert v['passed_preservation'] and not v['new_warnings']
backup=HERE/'control-before';assert not backup.exists()
plan='docs/plans/accounting-exact-native-timing-20261026.md'
result='data/accounting-master/exact-time-integration-20261026/result.md'
note=NL.join(['## Exact information timing integrated — 26 October 2026','',
 'Version 4.44 is 539 pages, not_ready. S1–S5 partial; S6 held; S7/E3 deferred.',
 'Appendix A.54.6 explains exact timestamp conversion and the native precision',
 'defect, preserving source admission and whole-second scope. All 177',
 'predecessor sources and prior mathematics remain; no new build warnings.',
 'Cover and physical pages 504–507 inspected. No whole obligation closes.',
 'PDF: '+v['pdf'],'SHA256: '+v['pdf_sha256']+'.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={name:(ROOT/name).read_bytes() for name in targets}
for name,raw in before.items():
    p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
for name in concise:
    old=before[name].decode();tail=old[old.index('Mission:'):]
    tail=tail.replace('Current question: can common method bindings preserve exact native information-cutoff timing?','Current question: can exact timing preserve all native information-closure obligations?')
    tail=tail.replace('docs/plans/accounting-native-timing-binding-audit-20261026.md',plan)
    tail=tail.replace('docs/design/proposal/manuscript-method-input-20261026/accounting-product-proposal.pdf',v['pdf'])
    tail=tail.replace('e6e1506a244fc8faf6b4e0e4fa9ec81b170ddeaeaa15743d5eb55d81bd87ae98',v['pdf_sha256'])
    (ROOT/name).write_text('# Current AccDSL master program'+NL*2+note+tail)
for name in historical:
    first,rest=before[name].decode().split(NL,1);(ROOT/name).write_text(first+NL*2+note+rest.lstrip(NL))
updates={'active_work_plan':plan,'latest_result':result,'current_candidate':'4.44;539 pages;not_ready','current_pdf':v['pdf'],'current_pdf_sha256':v['pdf_sha256']}
p=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(p.relative_to(ROOT))]);a=d['active_execution'];a.update(updates)
a['next']=['Compose exact timestamps with native information closure and preserved source duties','Continue wider method, actual-source and adaptation gaps','Keep S6 held and S7/E3 deferred']
a['completed_increments'].append('Version4.44:539 pages;177 predecessor sources preserved;exact information time integrated;no new warnings')
a['latest_results'].append(result);p.write_text(json.dumps(d,indent=2)+NL)
p=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(p.relative_to(ROOT))]);d['active_execution_note'].update(updates);p.write_text(json.dumps(d,indent=2)+NL)
dump=lambda name,x:(HERE/name).write_text(json.dumps(x,indent=2)+NL)
dump('control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha256(b).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n,b in before.items()}})
dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'python3 data/accounting-master/exact-time-integration-20261026/integrate.py prepare/build/verify (separate commands)','environment':sys.version,'cpu_gpu':'CPU; build hides GPU with CUDA_VISIBLE_DEVICES=-1','data_version':v['pdf_sha256'],'random_seeds':'N/A deterministic document build','wall_seconds':json.loads((HERE/'build.json').read_text())['wall_seconds'],'plan_file':'docs/plans/accounting-exact-time-integration-20261026.md','result_file':result,'artifact_paths':[v['pdf'],'baseline.json','build.json','verification.json','review.md']})
assert all(plan in (ROOT/n).read_text() for n in targets)
print(json.dumps({'refreshed':len(targets),'candidate':updates['current_candidate'],'next_plan':plan}))
