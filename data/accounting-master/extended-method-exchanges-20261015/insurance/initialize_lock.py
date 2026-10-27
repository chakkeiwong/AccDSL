"""One-time successor lock; abort rather than replace any protection baseline."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    target = OUT / 'predecessor-lock.json'
    assert not target.exists(), 'Existing lock must never be recreated'
    previous = OUT.parent / 'group' / 'predecessor-lock.json'
    lock = json.loads(previous.read_text())
    original = ROOT / lock['original_protection_manifest']
    assert sha(original) == lock['original_manifest_sha256']
    protected = json.loads(original.read_text())
    for item in protected['files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
        assert sha(ROOT / item['snapshot']) == item['sha256'], item['snapshot']
    for item in lock['predecessor_files']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    assert commit == lock['git_commit']
    assert hashlib.sha256(index).hexdigest() == lock['index_sha256']
    assert len(index.splitlines()) == lock['index_entries'] == 100
    paths = {item['path']: item for item in lock['predecessor_files']}
    for path in sorted((OUT.parent / 'group').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            key = str(path.relative_to(ROOT))
            assert key not in paths
            paths[key] = {'path': key, 'sha256': sha(path)}
    lock['predecessor_files'] = [paths[key] for key in sorted(paths)]
    lock['previous_lock_path'] = str(previous.relative_to(ROOT))
    lock['previous_lock_sha256'] = sha(previous)
    with target.open('x') as stream:
        stream.write(json.dumps(lock, indent=2) + '\n')
    print(json.dumps({'protected_inputs': len(protected['files']),
                      'predecessor_files': len(paths), 'staged_entries': len(index.splitlines()),
                      'lock_sha256': sha(target)}))

if __name__ == '__main__':
    main()
