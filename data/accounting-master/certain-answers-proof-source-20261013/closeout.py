"""Bind this completed semantics unit and controls without altering frozen evidence."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
assert not (U/'completion.json').exists(),'Completed unit; do not overwrite'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):(U/name).write_text(json.dumps(obj,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());c=json.loads((U/'candidate.json').read_text());checks={}
for file in ['source-checks.json','manuscript-checks.json']:
    checks[file]=not json.loads((U/file).read_text())['failed']
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R)
checks['unrelated_index_preserved']=index==(U/'unrelated-index-before.txt').read_bytes()
checks['100_staged_entries']=len(index.splitlines())==100
nextplan='docs/plans/accounting-post-certainty-readiness-20261013.md'
for x in b['controls']:
    checks['snapshot:'+x['live']]=sha(R/x['snapshot'])==x['sha256']
    t=(R/x['live']).read_text()
    checks['control:'+x['live']]='2.72' in t and 'not_ready' in t and Path(nextplan).name in t
for group in ['frozen','candidate_files']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
checks['next_plan_present']=(R/nextplan).is_file()
checks['all_mc_g_preserved']='All35 requirements/18 gaps' in (R/'docs/plans/accounting-continuation-requirements-20261007.md').read_text()
checks['current_assessment_link']='post-adapter-readiness-20261013/dispositions.md' in (R/'docs/plans/accounting-master-current.md').read_text()
checks['historical_directives_marked']='Those directives are historical' in (R/'docs/plans/accounting-continuation-requirements-20261007.md').read_text()
failed=[k for k,v in checks.items() if not v]
save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed})
assert not failed,failed
finished=datetime.now(timezone.utc)
manifest={'git_commit':b['git_commit'],'commands':['Four bounded curl requests in receipts.json','Full26-page technical reading and source renders in proof-review.md','check_source.py','integrate.py','latexmk command/environment in build-run.json','PyMuPDF rendering and author inspection','check_manuscript.py','closeout.py'],
 'environment':{'python':sys.executable,'version':sys.version,'libraries':'Python stdlib, PyMuPDF; LuaLaTeX/latexmk'},
 'cpu_gpu':'CPU-only document/arithmetic processing; CUDA_VISIBLE_DEVICES=-1; GPU intentionally hidden; no GPU imports/probes',
 'data_version':'Libkin2016 journal work: inspected26-page author preprint dated2015-11-17, SHAed3a343607504a2a83c709760d994052e963e56c474e500cab1d81fe9fa6db01; exact KR/journal-version equivalence unchecked',
 'random_seeds':'N/A deterministic source/document/arithmetic work','started_at':b['started_at'],'finished_at':finished.isoformat(),'wall_seconds':(finished-datetime.fromisoformat(b['started_at'])).total_seconds(),'wall_scope':'elapsed unit including handoff, source review and writing; not a benchmark',
 'plan':'docs/plans/accounting-certain-answers-proof-source-20261013.md','result':str((U/'result.md').relative_to(R)),'candidate':c['candidate'],
 'candidate_files':{str(p.relative_to(R)):sha(p) for p in sorted((R/c['candidate']).rglob('*')) if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf','.log','.bbl','.blg'}},
 'outputs':{str(p.relative_to(R)):sha(p) for p in sorted(U.rglob('*')) if p.is_file() and p.name not in {'run-manifest.json','completion.json'}},
 'controls':{x['live']:sha(R/x['live']) for x in b['controls']}}
save('run-manifest.json',manifest)
save('completion.json',{'status':'complete_within_versioned_primary_proof_scope','readiness':'not_ready','finished_at':finished.isoformat(),'manifest_sha256':sha(U/'run-manifest.json'),'next_plan':nextplan})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'staged_entries':100,'readiness':'not_ready'}))
