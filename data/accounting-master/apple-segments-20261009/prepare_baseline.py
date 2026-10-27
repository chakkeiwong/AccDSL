"""Verify V2.13 and preserve the four mutable resume records before edits."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
if (OUT / 'baseline.json').exists():
    raise SystemExit('Baseline already exists')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
prior_path = ROOT / 'data/accounting-master/apple-liquidity-20261009/run-manifest.json'
prior = read(prior_path)
completion = read(prior_path.parent / 'completion.json')
assert sha(prior_path) == completion['manifest_sha256']
assert completion['pdf']['pages'] == 149
bad = [n for n, h in prior['artifact_hashes'].items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
assert not bad, bad
pointers = ['docs/plans/accounting-master-checkpoint.md',
            'data/accounting-master/next-plan.md',
            'docs/plans/accounting-continuation-requirements-20261007.md',
            'docs/plans/accounting-master-current.md']
relocations = []
for name in pointers:
    dst = OUT / 'pointers-before' / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, dst)
    assert sha(ROOT / name) == sha(dst)
    relocations.append(dict(historical_path=name, preserved_path=str(dst.relative_to(ROOT)), sha256=sha(dst)))
protected = {}
for base in [prior_path.parent, ROOT / 'docs/design/proposal/manuscript-liquidity-20261009']:
    protected.update({str(p.relative_to(ROOT)): sha(p) for p in base.rglob('*') if p.is_file()})
for name in ['MISSION_CONTROL.md', 'docs/plans/accounting-mission-requirements.md',
             'docs/plans/accounting-product-design-checkpoint.md', 'scripts/accounting_master_catalog.json',
             'docs/plans/accounting-apple-liquidity-20261009.md']:
    protected[name] = sha(ROOT / name)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
record = dict(recorded_at=datetime.now(timezone.utc).isoformat(), git_commit=head,
              protected_hashes=protected, pointer_relocations=relocations,
              prior_manifest=str(prior_path.relative_to(ROOT)), prior_manifest_sha256=sha(prior_path),
              prior_manifest_references=len(prior['artifact_hashes']),
              git_worktree='Extensive pre-existing dirty work preserved; no broad staging or controller execution')
(OUT / 'baseline.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(dict(protected_files=len(protected), previous_manifest_references=len(prior['artifact_hashes']), pointers=4, git_commit=head)))
