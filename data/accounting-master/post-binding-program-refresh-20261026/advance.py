"""One-time checkpoint refresh after verified boundary work."""
import json
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
backup=HERE/'control-before'
assert not backup.exists(), 'completed refresh must not be repeated'
assert json.loads((HERE/'checks.json').read_text())['passed']
plan='docs/plans/accounting-complete-method-authoring-audit-20261026.md'
result='data/accounting-master/post-binding-program-refresh-20261026/result.md'
note=NL.join(['## Program dependencies refreshed — 26 October 2026', '', 'Version 4.44 remains the 539-page governing candidate, not_ready.', 'The updated queue credits finite input/timing/composition and credit-cash work.', 'The next gap is complete method authoring over existing semantic engines,', 'including v2 typed claim insertion. All 53 obligations, six interactions and', '46 operations remain. S1–S5 partial; S6 held; S7/E3 deferred.']+['Result: '+result+'.','Next plan: '+plan+'.','',''])
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={name:(ROOT/name).read_bytes() for name in targets}
for name,raw in before.items():
    p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
for name in concise:
    text=before[name].decode();tail=text[text.index('Mission:'):]
    tail=tail.replace('Current question: which remaining dependency best advances the complete simulator design?','Current question: how can complete methods be authored while retaining existing semantics?').replace('docs/plans/accounting-post-binding-program-refresh-20261026.md',plan)
    tail=tail.replace('Full residuals: data/accounting-master/current-design-reconciliation-20261025/remaining-work.md.','Current residuals: data/accounting-master/post-binding-program-refresh-20261026/remaining-work.md.'+NL+'Original all-row audit: data/accounting-master/current-design-reconciliation-20261025/remaining-work.md.')
    (ROOT/name).write_text('# Current AccDSL master program'+NL*2+note+tail)
for name in historical:
    text=before[name].decode();first,rest=text.split(NL,1);(ROOT/name).write_text(first+NL*2+note+rest.lstrip(NL))
path=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(path.relative_to(ROOT))]);a=d['active_execution']
a.update(active_work_plan=plan,latest_result=result,remaining_work='data/accounting-master/post-binding-program-refresh-20261026/remaining-work.md',next=['Audit and author complete methods over existing precondition/effect/memory engines','Preserve typed map growth and compare full state/results, then integrate coherent evidence','Keep product implementation held and E3 deferred'])
a['completed_increments'].append('Post-binding program refresh:53/6/46 preserved;full method authoring including v2 state growth selected')
a['latest_results'].append(result);path.write_text(json.dumps(d,indent=2)+NL)
path=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(path.relative_to(ROOT))]);d['active_execution_note'].update(active_work_plan=plan,latest_result=result,remaining_work='data/accounting-master/post-binding-program-refresh-20261026/remaining-work.md');path.write_text(json.dumps(d,indent=2)+NL)
manifest={'updated_files':{name:{'before':sha256(raw).hexdigest(),'after':sha256((ROOT/name).read_bytes()).hexdigest()} for name,raw in before.items()},'next_plan':plan}
(HERE/'control-refresh.json').write_text(json.dumps(manifest,indent=2)+NL)
assert all(plan in (ROOT/name).read_text() for name in targets)
print(json.dumps({'refreshed':len(targets),'next_plan':plan}))
