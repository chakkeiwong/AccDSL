"""Preserve the completed P4b run facts without replacing prior evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=read(HERE/'predecessor-lock.json')
    index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert commit==lock['git_commit'] and hashlib.sha256(index).hexdigest()==lock['index_sha256']
    runs=[]
    for name in ('attempt-01','attempt-02'):
        p=HERE/name; b=read(p/'build-run.json'); v=read(p/'verification.json')
        runs.append(dict(attempt=name,build=b,verification={k:x for k,x in v.items() if k!='checks_detail'}))
    assert runs[-1]['verification']['status']=='passed'
    selected=[HERE/'result.md',HERE.parent/'p4b-coverage-reconciliation.md',HERE.parent/'requirements-successor-p4b-20261016.md',HERE/'predecessor-lock.json',HERE/'draft-diagnostic-20261016.json']
    selected+=sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix=='.py')
    for name in ('attempt-01','attempt-02'):
        selected+=sorted(p for p in (HERE/name).rglob('*') if p.is_file())
    manifest=dict(date=datetime.now(timezone.utc).isoformat(),git_commit=commit,interpreter=sys.executable,python_version=platform.python_version(),environment='existing tfgpu Python; stdlib/jsonschema '+importlib.metadata.version('jsonschema'),cpu_gpu='CPU exact rational arithmetic; no GPU framework imported',data_version='InsuranceAssessment/1; retained historical sources and synthetic supplied facts',random_seeds='N/A: deterministic exact cases',plan='docs/plans/accounting-insurance-assessment-exchanges-20261015.md',result=str((HERE/'result.md').relative_to(ROOT)),commands=[[sys.executable,str((HERE/'check_draft.py').relative_to(ROOT))]]+[[sys.executable,str((HERE/script).relative_to(ROOT)),*args] for script,args in [('build_exchanges.py',[]),('verify_exchanges.py',['attempt-01']),('build_exchanges.py',[]),('verify_exchanges.py',['attempt-02'])]],runs=runs,wall_seconds=sum(r['build']['wall_seconds']+r['verification']['wall_seconds'] for r in runs),predecessor_lock_sha256=sha(HERE/'predecessor-lock.json'),predecessor_files=len(lock['predecessor_files']),index_sha256=lock['index_sha256'],index_entries=len(index.splitlines()),files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(set(selected))])
    with (HERE/'run-manifest.json').open('x') as f: json.dump(manifest,f,indent=2); f.write('\n')
    print(json.dumps(dict(status='recorded',attempts=len(runs),passed_attempt='attempt-02',checks=runs[-1]['verification']['checks'],files=len(manifest['files']))))
if __name__=='__main__': main()
