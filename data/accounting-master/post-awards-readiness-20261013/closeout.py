"""Close the full-program delta review without changing frozen evidence."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed assessment.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());checks={}
checks['integrity']=not json.loads((U/'integrity-checks.json').read_text())['failed']
x=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['index_preserved']=x==(U/'unrelated-index-before.txt').read_bytes();checks['100_entries']=len(x.splitlines())==100
for r in b['controls']:
    checks['snapshot:'+r['live']]=sha(R/r['snapshot'])==r['sha256']
    t=(R/r['live']).read_text();checks['current:'+r['live']]='2.67' in t and 'not_ready' in t and 'accounting-arelle-fact-identity-20261013.md' in t
for p,h in b['frozen'].items():checks['frozen:'+p]=sha(R/p)==h
checks['next_plan']=(R/'docs/plans/accounting-arelle-fact-identity-20261013.md').is_file()
failed=[k for k,x in checks.items() if not x];save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed})
if failed:raise SystemExit(str(failed))
now=datetime.now(timezone.utc)
save('run-manifest.json',{'git_commit':b['git_commit'],'commands':['python3 data/accounting-master/post-awards-readiness-20261013/build_assessment.py','python3 data/accounting-master/post-awards-readiness-20261013/refresh_controls.py','python3 data/accounting-master/post-awards-readiness-20261013/closeout.py'],
 'environment':{'python':sys.executable,'version':sys.version,'libraries':'standard library only'},'cpu_gpu':'CPU text/hash work only; no GPU libraries or device probing',
 'data_version':'V2.67 checked candidate, V2.64 assessment, completed V2.65–2.67 units and frozen source inventory',
 'random_seeds':'N/A deterministic documentary assessment','started_at':b['started_at'],'finished_at':now.isoformat(),
 'wall_seconds':(now-datetime.fromisoformat(b['started_at'])).total_seconds(),'wall_scope':'Elapsed audit/writing, not a benchmark',
 'plan':'docs/plans/accounting-post-awards-readiness-20261013.md','result':str((U/'result.md').relative_to(R)),
 'candidate':b['candidate'],'candidate_pdf_sha256':b['candidate_pdf_sha256'],
 'outputs':{str(p.relative_to(R)):sha(p) for p in U.rglob('*') if p.is_file() and p.name not in {'run-manifest.json','completion.json'}},
 'controls':{x['live']:sha(R/x['live']) for x in b['controls']}})
save('completion.json',{'status':'author_delta_assessment_complete','readiness':'not_ready','finished_at':now.isoformat(),'manifest_sha256':sha(U/'run-manifest.json'),'next_plan':'docs/plans/accounting-arelle-fact-identity-20261013.md'})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'index_entries':100}))
