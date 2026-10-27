"""Freeze predecessor and primary-source inputs once."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-consideration-20261027'
out=H/'predecessor-lock.json';assert not out.exists()
files={R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text())}
files.update(S/p for p in ['reference.py','contract.md','verify.py','attempt-01/cases.json','attempt-01/verification.json','attempt-01/source-lock.json','result.md'])
for folder in ['source-inspection-01','source-inspection-02']:
    files.update(p for p in (H/folder).iterdir() if p.suffix!='.png')
    for row in json.loads((H/folder/'source-register.json').read_text()):
        p=R/row['source'];assert sha256(p.read_bytes()).hexdigest()==row['sha256'];files.add(p)
lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
out.write_text(json.dumps(lock,indent=2)+'\n');print(json.dumps(dict(protected=len(lock))))
