from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-prior-interest-20261027'
out=H/'predecessor-lock.json';assert not out.exists()
files={R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text())}
files.update(S/p for p in ['attempt-01/cases.json','attempt-01/verification.json','attempt-01/source-lock.json','result.md','source-inspection-02/aasb128-nov2024-jan2025.pdf'])
out.write_text(json.dumps({str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n');print(json.dumps(dict(protected_files=len(files))))
