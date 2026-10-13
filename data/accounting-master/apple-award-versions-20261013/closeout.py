"""Close source/manuscript evidence with controls and prior files preserved."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, data):
    (UNIT / name).write_text(json.dumps(data,indent=2)+'\n')
b = json.loads((UNIT / 'baseline.json').read_text())
c = json.loads((UNIT / 'candidate.json').read_text())
checks = {}
for file in ['source-arithmetic-checks.json','manuscript-checks.json']:
    a = json.loads((UNIT / file).read_text())
    checks[file] = not a['failed']
index = subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
checks['unrelated_index_preserved'] = index == (UNIT / 'unrelated-index-before.txt').read_bytes()
checks['100_staged_entries'] = len(index.splitlines()) == 100
for p in b['controls']:
    checks['snapshot:'+p['live']] = sha(ROOT / p['snapshot']) == p['sha256']
    text = (ROOT / p['live']).read_text()
    checks['live:'+p['live']] = '2.67' in text and 'accounting-post-awards-readiness-20261013.md' in text and 'not_ready' in text
for path,digest in b['frozen'].items():
    checks['frozen:'+path] = sha(ROOT / path) == digest
for path,digest in b['candidate_files'].items():
    checks['prior:'+path] = sha(ROOT / path) == digest
checks['next_plan_present'] = (ROOT/'docs/plans/accounting-post-awards-readiness-20261013.md').is_file()
failed = [k for k,v in checks.items() if not v]
save('closeout-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed})
if failed:
    raise SystemExit(str(failed))
finished = datetime.now(timezone.utc)
manifest = {'git_commit':b['git_commit'],'commands':['CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/apple-award-versions-20261013/check_versions.py','Build command and exact environment in build-run.json','CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/apple-award-versions-20261013/check_manuscript.py','CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 data/accounting-master/apple-award-versions-20261013/closeout.py'],
    'environment':{'python':sys.executable,'version':sys.version,'libraries':'standard library, PyMuPDF; LuaLaTeX/latexmk build'},
    'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 during checks/build; no GPU library imported or device probed',
    'data_version':'Retained2022 CEO and2024 general/CEO forms; exact source spans, selected clauses, twelve PDF images and one derived HTML view; deterministic conditional consequences',
    'random_seeds':'N/A deterministic source/document/arithmetic work','started_at':b['started_at'],'finished_at':finished.isoformat(),
    'wall_seconds':(finished-datetime.fromisoformat(b['started_at'])).total_seconds(),'wall_scope':'elapsed unit including review/writing, not a benchmark',
    'plan':'docs/plans/accounting-apple-award-versions-20261013.md','result':str((UNIT/'result.md').relative_to(ROOT)),
    'candidate':c['candidate'],'candidate_files':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/c['candidate']).rglob('*')) if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf','.log','.bbl','.blg'}},
    'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(UNIT.rglob('*')) if p.is_file() and p.name not in {'run-manifest.json','completion.json'}},
    'controls':{p['live']:sha(ROOT/p['live']) for p in b['controls']}}
save('run-manifest.json',manifest)
save('completion.json',{'status':'complete_within_selected_version_comparison_scope','readiness':'not_ready','finished_at':finished.isoformat(),'manifest_sha256':sha(UNIT/'run-manifest.json'),'next_plan':'docs/plans/accounting-post-awards-readiness-20261013.md'})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'staged_entries':100}))
