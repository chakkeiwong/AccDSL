"""Run both unchanged bounded components from a fresh internal companion copy."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True,help='New directory inside this bundle')
args=parser.parse_args()
root=Path(__file__).resolve().parent
out=args.output.resolve()
assert out.is_relative_to(root) and out!=root
manifest=json.loads((root/'companion-manifest.json').read_text())
def digest(path): return sha256(path.read_bytes()).hexdigest()
def protect():
    for name,row in manifest['files'].items():
        assert digest(root/name)==row['sha256'],'changed input: '+name
protect()
out.mkdir(exist_ok=False)
started=time.monotonic()
env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1')
results=[]
for component in manifest['components']:
    child=out/component['id']
    cmd=[sys.executable,'-I','-B',str(root/component['driver']),
         '--root',str(root),'--output',str(child)]
    log=out/(component['id']+'.log')
    start=time.monotonic()
    with log.open('x') as stream:
        proc=subprocess.run(cmd,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    row=dict(id=component['id'],command=cmd,exit_code=proc.returncode,
             wall_seconds=time.monotonic()-start,output=str(child.relative_to(root)),
             log_sha256=digest(log))
    results.append(row)
    with (out/'progress.json').open('w') as stream: json.dump(results,stream,indent=2);stream.write('\n')
    if proc.returncode:
        raise SystemExit(component['id']+' failed; inspect '+str(log))
    checks=json.loads((child/'checks.json').read_text())
    audit=json.loads((child/'access-audit.json').read_text())
    assert checks['passed'] and not audit['violations']
    row['checks']=checks['checks']
    row['checks_sha256']=digest(child/'checks.json')
    row['audit_sha256']=digest(child/'access-audit.json')
    if component['id']=='source-to-report':
        assert checks['compatibility_exchanges']==26 and checks['selected_history_exchanges']==11
        assert checks['obligations']==180 and len(checks['normalized_fields'])==7
        assert len(checks['certificate_comparisons'])==3
    else:
        assert checks['raw_facts']==30 and checks['source_observations']==256
        assert checks['source_relations']==143 and checks['normalization']=='none'
protect()
summary=dict(passed=True,components=results,all_inputs_preserved=True,
    timestamp_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-started,
    command=[sys.executable,'-I','-B',*sys.argv],python=sys.version,
    cpu_gpu='CPU only; GPUs intentionally hidden in parent and children',
    git_commit='N/A: source worktree marker unusable; exact manifests retained',
    random_seeds='N/A: exact conformance and declared certificate comparisons',
    data_version=digest(root/'companion-manifest.json'),
    plan='docs/plans/accounting-internal-evidence-companion-20261027.md',
    result='data/accounting-master/internal-evidence-companion-20261027/result.md')
with (out/'result.json').open('x') as stream:json.dump(summary,stream,indent=2);stream.write('\n')
print(json.dumps(dict(passed=True,components=len(results),checks=sum(r['checks'] for r in results),
                     output=str(out),wall_seconds=summary['wall_seconds'])))
