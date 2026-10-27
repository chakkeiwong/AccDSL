"""Capture this diagnostic's immutable inputs exactly once."""
from pathlib import Path
import json
from bridge import ROOT, HERE, ATTEMPT, hash_bytes

target = HERE / 'source-lock.json'
if target.exists():
    raise SystemExit('source-lock already exists; do not overwrite')
paths = [ATTEMPT / 'portable-exchanges.json', ATTEMPT / 'record-schemas.json',
         ROOT / 'docs/plans/accounting-common-method-input-boundary-20261026.md',
         ROOT / 'data/accounting-master/company-portable-authoring-20261023/blobs/4b568956dda9135f67d48c7195d58899dd04e711de7e925dc7209837826326eb']
paths += list(ATTEMPT.joinpath('inputs').glob('*.py'))
paths += list(ATTEMPT.joinpath('bytes').glob('*.json'))
paths += list(ROOT.joinpath('scripts').glob('method_requirement*.py'))
paths += list(ROOT.joinpath('scripts').glob('method_input_binding*.py'))
paths += [ROOT / 'data/accounting-master/company-portable-authoring-20261023/portable.py',
          ROOT / 'data/accounting-master/company-path-admission-20261023/admission.py']
lock = {'files': {str(p.relative_to(ROOT)): hash_bytes(p.read_bytes()) for p in sorted(set(paths))}}
target.write_text(json.dumps(lock, indent=2) + chr(10))
print(json.dumps({'protected_files': len(lock['files'])}))
