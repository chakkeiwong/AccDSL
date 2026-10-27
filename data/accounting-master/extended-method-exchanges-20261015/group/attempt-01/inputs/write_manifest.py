"""Write the immutable manifest for one independently verified attempt."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=HERE/sys.argv[1];target=attempt/'run-manifest.json';assert not target.exists()
 build=json.loads((attempt/'build-note.json').read_text());check=json.loads((attempt/'verification.json').read_text())
 lock=json.loads((HERE/'predecessor-lock.json').read_text())
 manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),commands=[build['command'],check['command']],interpreter=check['interpreter'],python_version=platform.python_version(),cpu_gpu='CPU only; exact Fraction arithmetic; no GPU framework imported',random_seeds='N/A: deterministic exact fixtures',data_version='GroupComponents/1; historical retained EU sources and synthetic supplied inputs',wall_seconds=build['wall_seconds']+check['wall_seconds'],plan='docs/plans/accounting-group-component-exchanges-20261015.md',result=str((HERE/'result.md').relative_to(ROOT)),status=check['status'],summary=check['summary'],predecessor_lock_sha256=sha(HERE/'predecessor-lock.json'),original_inputs=204,predecessor_files=len(lock['predecessor_files']),staged_entries=lock['index_entries'],files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(attempt.rglob('*')) if p.is_file() and '__pycache__' not in p.parts],limits=['documentary not runtime','synthetic not actual company','historical authority not current-law admission','isolated components not combined statements'])
 with target.open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(path=str(target.relative_to(ROOT)),status=check['status'],files=len(manifest['files']),sha256=sha(target))))
if __name__=='__main__':main()
