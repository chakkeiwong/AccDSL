from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-symbolic-20261027'
out=H/'predecessor-lock.json';assert not out.exists()
files={R/p for p in json.loads((S/'attempt-01/source-lock.json').read_text())}
files.update(S/p for p in ['reference.py','attempt-01/cases.json','attempt-01/verification.json','result.md'])
files.update(R/p for p in ['data/accounting-master/conversion-control-scope-20261026/source-attempt-02/aasb3-2026.pdf','data/accounting-master/conversion-control-scope-20261026/source-attempt-02/aasb127-2022.pdf','data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02/aasb9-2026.pdf'])
out.write_text(json.dumps({str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
print(json.dumps(dict(protected_files=len(files))))
