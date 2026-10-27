"""One-time checkpoint refresh after verified boundary work."""
import json
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
backup=HERE/'control-before'
assert not backup.exists(), 'completed refresh must not be repeated'
assert json.loads((HERE/'checks.json').read_text())['passed']
plan='docs/plans/accounting-post-binding-program-refresh-20261026.md'
result='data/accounting-master/exact-native-timing-20261026/result.md'
note=NL.join(['## Native exact information checks completed — 26 October 2026', '', 'Version 4.44 remains the 539-page governing candidate, not_ready.', 'ExactBankInformation/1 preserves 271 retained regulatory responses and checks', '11 derived information cases, with five intentional repaired refusals. Eight', 'pinned source files remain unchanged. Native profile adoption remains open.', 'S1–S5 partial; S6 held; S7/E3 deferred. No whole obligation closes.']+['Result: '+result+'.','Next plan: '+plan+'.','',''])
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={name:(ROOT/name).read_bytes() for name in targets}
for name,raw in before.items():
    p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
for name in concise:
    text=before[name].decode();tail=text[text.index('Mission:'):]
    tail=tail.replace('Current question: can exact timing preserve all native information-closure obligations?','Current question: which remaining dependency best advances the complete simulator design?').replace('docs/plans/accounting-exact-native-timing-20261026.md',plan)
    (ROOT/name).write_text('# Current AccDSL master program'+NL*2+note+tail)
for name in historical:
    text=before[name].decode();first,rest=text.split(NL,1);(ROOT/name).write_text(first+NL*2+note+rest.lstrip(NL))
path=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(path.relative_to(ROOT))]);a=d['active_execution']
a.update(active_work_plan=plan,latest_result=result,next=['Refresh current remaining phases and choose the next consequential design dependency','Refresh wider common-language, company-source and method residuals','Keep product implementation held and E3 deferred'])
a['completed_increments'].append('Exact native information successor:271 retained responses;11 derived cases;5 changed outcomes;8 protected files')
a['latest_results'].append(result);path.write_text(json.dumps(d,indent=2)+NL)
path=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(path.relative_to(ROOT))]);d['active_execution_note'].update(active_work_plan=plan,latest_result=result);path.write_text(json.dumps(d,indent=2)+NL)
manifest={'updated_files':{name:{'before':sha256(raw).hexdigest(),'after':sha256((ROOT/name).read_bytes()).hexdigest()} for name,raw in before.items()},'next_plan':plan}
(HERE/'control-refresh.json').write_text(json.dumps(manifest,indent=2)+NL)
assert all(plan in (ROOT/name).read_text() for name in targets)
print(json.dumps({'refreshed':len(targets),'next_plan':plan}))
