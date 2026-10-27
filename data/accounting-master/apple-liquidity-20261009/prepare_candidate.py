"""Copy protected manuscript sources without changing the frozen baseline."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'docs/design/proposal/manuscript-debt-20261009'
NEW = ROOT / 'docs/design/proposal/manuscript-liquidity-20261009'
if NEW.exists() or (OUT / 'completion.json').exists():
    raise SystemExit('Preserve an existing candidate')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
copied = {}
for p in sorted(OLD.rglob('*')):
    if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}:
        dest = NEW / p.relative_to(OLD)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
        assert sha(p) == sha(dest)
        copied[str(dest.relative_to(ROOT))] = sha(dest)
(OUT / 'candidate-copy-receipt.json').write_text(json.dumps(dict(
    recorded_at=datetime.now(timezone.utc).isoformat(), script_sha256=sha(Path(__file__)),
    baseline=str(OLD.relative_to(ROOT)), candidate=str(NEW.relative_to(ROOT)),
    copied_hashes=copied, method='Exact source copy before manual bounded integration'), indent=2) + '\n')
print(json.dumps(dict(copied_sources=len(copied))))
