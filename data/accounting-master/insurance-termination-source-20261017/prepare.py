"""Preserve inputs for the bounded documentary source audit; never overwrite."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
manifest_path = OUT / "input-manifest.json"
if manifest_path.exists():
    raise SystemExit("Inputs already preserved; do not rerun preparation")

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

controls = [
    "docs/plans/accounting-master-checkpoint.md",
    "docs/plans/accounting-master-current.md",
    "data/accounting-master/next-plan.md",
]
inputs = controls + [
    "docs/plans/accounting-insurance-termination-source-20261017.md",
    "docs/design/research/p08-v3-preparation/eu-2023-1803-original.pdf",
    "docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt",
    "docs/design/research/standards/aasb17.txt",
    "data/accounting-master/insurance-service-finance-origins-20261016/source-reading.md",
    "data/accounting-master/insurance-service-finance-origins-20261016/input-lock-v2.json",
    "docs/design/proposal/manuscript-origin-matched-cessation-20261017/sections/insurance-service-finance-origins.tex",
    "docs/design/proposal/manuscript-origin-matched-cessation-20261017/accounting-product-proposal.pdf",
]
for name in controls:
    target = OUT / "controls-before" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise SystemExit(f"Refusing overwrite: {target}")
    shutil.copy2(ROOT / name, target)

source = ROOT / inputs[5]
lines = source.read_text().splitlines()
parts = [(55531, 55593, "74–77"), (55686, 55764, "87–92"),
         (58421, 58553, "B128–B136")]
excerpts = []
for start, end, anchor in parts:
    excerpts.append(f"## IFRS17.{anchor}; retained lines {start}–{end}\n\n")
    excerpts.extend(f"{i + 1}: {lines[i]}\n" for i in range(start - 1, end))
(OUT / "retained-source-excerpts.txt").write_text("".join(excerpts))
manifest = {
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "git_commit": "03fea070f089821f4759e49a4466a3399b7fc078",
    "kind": "documentary source audit; no numerical or empirical run",
    "command": "python3 data/accounting-master/insurance-termination-source-20261017/prepare.py",
    "environment": "system Python standard library; no framework import",
    "cpu_gpu_status": "CPU file operations only; no GPU detection or initialization",
    "random_seeds": "N/A source inspection",
    "data_version": "retained EU2023/1803 original historical edition; AASB compilation 31 December 2022",
    "inputs": [{"path": p, "sha256": digest(ROOT / p)} for p in inputs],
    "outputs": ["controls-before/" + p for p in controls] + ["retained-source-excerpts.txt"],
    "plan": "docs/plans/accounting-insurance-termination-source-20261017.md",
    "result": "data/accounting-master/insurance-termination-source-20261017/result.md",
}
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Preserved {len(controls)} controls; locked {len(inputs)} inputs; no prior evidence changed")
