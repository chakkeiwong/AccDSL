from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];out=H/'predecessor-lock.json';assert not out.exists();files=set()
for folder in ['acquisition-prior-interest-scope-20261027','acquisition-consideration-20261027']:
    s=H.parent/folder;files.update(R/p for p in json.loads((s/'attempt-01/source-lock.json').read_text()));files.update(s/p for p in ['reference.py','attempt-01/cases.json','attempt-01/verification.json','result.md'])
out.write_text(json.dumps({str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n');print(json.dumps(dict(protected_files=len(files))))
