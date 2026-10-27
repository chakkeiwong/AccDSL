"""One-time checkpoint refresh after verified boundary work."""
import json
from pathlib import Path
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
backup=HERE/'control-before'
assert not backup.exists(), 'completed refresh must not be repeated'
assert json.loads((HERE/'checks.json').read_text())['passed']
plan='docs/plans/accounting-method-input-integration-20261026.md'
result='data/accounting-master/common-method-input-boundary-20261026/result.md'
note=NL.join(['## Selected inputs linked to native requests — 26 October 2026','',
 'Version 4.42 remains the 537-page governing candidate, not_ready.',
 'NativeRequirementLink/1 checks exact request/input identities for one',
 'regulatory operation: 271 native exchanges, 813 text/typed pairs, 19',
 'negative cases, nine unknown/capability cases; 191 source files unchanged.',
 'Selected requirements pass in 95 rejected exchanges, so eligibility stays',
 'separate. S1–S5 partial; S6 held; S7/E3 deferred. No whole obligation closes.',
 'Result: '+result+'.','Next plan: '+plan+'.','',''])
concise=['docs/plans/accounting-master-current.md','docs/plans/accounting-current-program-20261025.md','data/accounting-master/next-plan.md']
historical=['docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-program.md','docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md','data/accounting-master/simulator-session-20261023.md']
targets=concise+historical+['data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={name:(ROOT/name).read_bytes() for name in targets}
for name,raw in before.items():
    p=backup/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
for name in concise:
    text=before[name].decode();tail=text[text.index('Mission:'):]
    tail=tail.replace('Current question: what must connect versioned requirement/input binding to a native invocation without inventing eligibility?','Current question: how should the checked native input boundary enter the governing design?').replace('docs/plans/accounting-common-method-input-boundary-20261026.md',plan)
    (ROOT/name).write_text('# Current AccDSL master program'+NL*2+note+tail)
for name in historical:
    text=before[name].decode();first,rest=text.split(NL,1);(ROOT/name).write_text(first+NL*2+note+rest.lstrip(NL))
path=ROOT/'data/accounting-master/next-plan.json';d=json.loads(before[str(path.relative_to(ROOT))]);a=d['active_execution']
a.update(active_work_plan=plan,latest_result=result,next=['Integrate checked native input binding into a preserved manuscript successor','Refresh wider common-language, company-source and method residuals','Keep product implementation held and E3 deferred'])
a['completed_increments'].append('Native method-input boundary:271 exchanges;813 text/typed pairs;19 negatives;9 unknown/capability cases;191 protected files')
a['latest_results'].append(result);path.write_text(json.dumps(d,indent=2)+NL)
path=ROOT/'scripts/accounting_master_catalog.json';d=json.loads(before[str(path.relative_to(ROOT))]);d['active_execution_note'].update(active_work_plan=plan,latest_result=result);path.write_text(json.dumps(d,indent=2)+NL)
manifest={'updated_files':{name:{'before':sha256(raw).hexdigest(),'after':sha256((ROOT/name).read_bytes()).hexdigest()} for name,raw in before.items()},'next_plan':plan}
(HERE/'control-refresh.json').write_text(json.dumps(manifest,indent=2)+NL)
assert all(plan in (ROOT/name).read_text() for name in targets)
print(json.dumps({'refreshed':len(targets),'next_plan':plan}))
