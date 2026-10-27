"""Freeze prior checked acquisition and source evidence once."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2]
S=H.parent/'acquisition-intragroup-realisation-20261027'
out=H/'predecessor-lock.json';assert not out.exists()
files={R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text())}
files.update(S/p for p in ['attempt-01/source-lock.json','attempt-01/cases.json','attempt-01/verification.json','result.md'])
base=H.parent/'acquisition-consideration-20261027'
files.update(base/p for p in ['reference.py','attempt-01/cases.json','attempt-01/verification.json'])
out.write_text(json.dumps({str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
print(json.dumps(dict(protected_files=len(files))))
