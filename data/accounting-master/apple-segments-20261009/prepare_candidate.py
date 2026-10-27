"""Copy the frozen V2.13 sources for bounded V2.14 integration."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT/'docs/design/proposal/manuscript-liquidity-20261009'
NEW = ROOT/'docs/design/proposal/manuscript-segments-20261009'
if NEW.exists():
    raise SystemExit('Preserve existing candidate')
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
copied={}
for p in sorted(OLD.rglob('*')):
    if p.is_file() and p.suffix in {'.tex','.bib','.lark'}:
        dst=NEW/p.relative_to(OLD);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,dst);assert sha(p)==sha(dst)
        copied[str(dst.relative_to(ROOT))]=sha(dst)
(OUT/'candidate-copy-receipt.json').write_text(json.dumps(dict(
    recorded_at=datetime.now(timezone.utc).isoformat(),script_sha256=sha(Path(__file__)),
    baseline=str(OLD.relative_to(ROOT)),candidate=str(NEW.relative_to(ROOT)),copied_hashes=copied),indent=2)+'\n')
print(json.dumps(dict(copied_sources=len(copied))))
