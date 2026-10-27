"""Finish metadata after the new historical note omitted its PDF identity."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];NL=chr(10)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,x):(HERE/name).write_text(json.dumps(x,indent=2)+NL)
start=time.monotonic();backup=HERE/'control-before';assert backup.exists() and not (HERE/'checks.json').exists()
v=json.loads((HERE.parent/'event-contract-integration-20261026/verification.json').read_text())
plan='docs/plans/accounting-common-program-authoring-audit-20261026.md';result=str((HERE/'result.md').relative_to(ROOT))
targets=[str(p.relative_to(backup)) for p in backup.rglob('*') if p.is_file()];assert len(targets)==10
for name in targets:
    p=ROOT/name;text=p.read_text()
    if p.suffix=='.md' and v['pdf_sha256'] not in text:
        marker='Result: '+result+'.';assert marker in text
        text=text.replace(marker,'PDF: '+v['pdf']+NL+'SHA256: '+v['pdf_sha256']+'.'+NL+marker,1);p.write_text(text)
for name in targets:assert plan in (ROOT/name).read_text() and v['pdf_sha256'] in (ROOT/name).read_text(),name
baseline=ROOT/'data/accounting-master/current-design-reconciliation-20261025/original-obligations.json'
original=json.loads(baseline.read_text());counts={k:len(v) for k,v in original['groups'].items()}
assert counts=={'obligations':53,'interactions':6,'operations':46}
units=['complete-method-authoring','authored-method-registry','authored-program-composition','authored-program-invariant-audit','authored-state-invariants','authored-event-prerequisite-audit','authored-event-contract']
results={}
for unit in units:
    folder=HERE.parent/(unit+'-20261026');assert json.loads((folder/'checks.json').read_text())['passed']
    results[unit]={'checks_sha256':sha(folder/'checks.json'),'result_sha256':sha(folder/'result.md')}
dump('checks.json',{'passed':True,'original_scope':counts,'original_sha256':sha(baseline),'candidate':'4.48;544 pages;not_ready',
 'pdf_sha256':v['pdf_sha256'],'checked_increment_results':results,'refreshed_controls':10,'whole_requirements_closed':0})
dump('control-refresh.json',{'next_plan':plan,'updated_files':{n:{'before':sha(backup/n),'after':sha(ROOT/n)} for n in targets}})
dump('run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'command':'python3 data/accounting-master/post-authoring-program-refresh-20261026/refresh.py; finish-refresh.py after metadata assertion',
 'environment':sys.version,'cpu_gpu':'CPU; no framework/GPU use','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,
 'data_version':sha(baseline),'plan_file':'docs/plans/accounting-post-authoring-program-refresh-20261026.md','result_file':result,
 'artifact_paths':['checks.json','control-refresh.json','remaining-work.md'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
(ROOT/'data/accounting-master/recovery-current-20261026.md').write_text('# Current recovery pointer'+NL*2+
 'Version 4.48, 544 pages, not_ready. PDF: '+v['pdf']+NL+'SHA256: '+v['pdf_sha256']+NL+
 'Active plan: '+plan+NL+'Next: inventory exact program fields and existing text/semantic owners.'+NL+
 'Ten controls agree. Completed writers preserved. No background process running. E3 deferred.'+NL)
(HERE/'recovery-audit.md').write_text('# Control refresh completion'+NL*2+
 'The first refresh wrote all ten controls, then correctly failed its identity'+NL+
 'check because the historical note omitted the new PDF/hash. Added that identity'+NL+
 'to five historical notes without repeating the completed backup/write phase.'+NL+
 'All ten controls now select the new plan and exact 4.48 PDF. Final metadata is'+NL+
 'recorded by finish-refresh.py; do not rerun either one-time writer.'+NL)
print(json.dumps({'refreshed_controls':10,'original_scope':counts,'candidate':'4.48;544 pages;not_ready','next_plan':plan}))
