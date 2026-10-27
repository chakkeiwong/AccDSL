"""One-time P3a2 lock extending completed P4b; never recreate a protection lock."""
from pathlib import Path
import hashlib
import json
import subprocess
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    target = HERE / 'predecessor-lock.json'
    assert not target.exists(), 'Never recreate an existing lock'
    previous = HERE.parent / 'insurance-assessment' / 'predecessor-lock.json'
    lock = json.loads(previous.read_text())
    original = ROOT / lock['original_protection_manifest']
    assert sha(original) == lock['original_manifest_sha256']
    for item in json.loads(original.read_text())['files']:
        for key in ('path', 'snapshot'):
            assert sha(ROOT / item[key]) == item['sha256'], item[key]
    for item in lock['predecessor_files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == lock['git_commit']
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    assert hashlib.sha256(index).hexdigest() == lock['index_sha256']
    assert len(index.splitlines()) == lock['index_entries'] == 100
    paths = {x['path']: x for x in lock['predecessor_files']}
    extra = [p for p in (HERE.parent / 'insurance-assessment').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    extra += [HERE.parent / 'p4b-coverage-reconciliation.md', HERE.parent / 'requirements-successor-p4b-20261016.md']
    for p in sorted(extra):
        k = str(p.relative_to(ROOT)); assert k not in paths
        paths[k] = dict(path=k, sha256=sha(p))
    lock.update(predecessor_files=[paths[k] for k in sorted(paths)], previous_lock_path=str(previous.relative_to(ROOT)), previous_lock_sha256=sha(previous))
    with target.open('x') as f: f.write(json.dumps(lock, indent=2) + '\n')
    print(json.dumps(dict(predecessor_files=len(paths), original_inputs=204, staged_entries=100, lock_sha256=sha(target))))
if __name__ == '__main__': main()
