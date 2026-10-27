"""One-shot control refresh; preserve the exact pre-refresh text and index."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
paths = [
    "docs/plans/accounting-master-current.md",
    "docs/plans/accounting-master-checkpoint.md",
    "docs/plans/accounting-continuation-requirements-20261007.md",
    "docs/plans/accounting-p17-completion-20261014.md",
    "docs/plans/accounting-p18-completion-20261014.md",
    "data/accounting-master/next-plan.md",
    str((HERE / "next-units.md").relative_to(ROOT)),
]
index = subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT)
assert index == (ROOT / "data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
manifest = json.loads((HERE / "corporate-v2/run-manifest.json").read_text())
for item in manifest["outputs"]:
    assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
tag = "## Extended method exchanges in progress — 15 October 2026"
new = """R03-P1 maps all 46 original operation rows and protects 204 inputs. The frozen
CorporateComponents/1 increment passes 1,110 checks. Its source-specific
CorporateComponents/2 successor specifies 48 methods, 63 financial transitions
in 24 paths, 253 exchanges and 14 annual reports; all 2,665 checks pass.
Result: data/accounting-master/extended-method-exchanges-20261015/corporate-v2/result.md.
P2 remains open for asset/benefit/tax and contract-composition variants. The
active PDF remains Version 3.13, 340 pages; integration follows P5 reconciliation.
Next: P2c under data/accounting-master/extended-method-exchanges-20261015/next-units.md,
then P3/P4 sector profiles and P5 assembly/integration. R04/R06 residuals,
whole-candidate R07 and all53/interactions R08 remain. Full readiness is not_ready;
runtime and empirical execution remain held."""
prepared = {}
for p in paths[:-1]:
    old = (ROOT / p).read_text()
    assert old.count(tag) == 1
    a, b = old.split(tag)
    current, rest = b.split("\n## ", 1)
    assert "1,110" in current and "2,665" not in current
    prepared[p] = a + tag + "\n\n" + new + "\n\n## " + rest
old = (ROOT / paths[-1]).read_text()
prepared[paths[-1]] = old.replace("# R03-P continuation after the first corporate exchanges", "# R03-P continuation after the second corporate exchanges", 1).replace(
    "15 October 2026. P1 is delivered as a coverage/field audit; the first P2 profile\npasses its finite checks. No original operation row is closed wholesale.",
    "15 October 2026. P1 is delivered. CorporateComponents/1 and /2 are frozen;\n/2 passes 2,665 checks across 48 methods, 63 transitions and 253 exchanges.\nFourteen annual reports preserve period-specific profit, OCI and cash. No\noriginal operation row is closed wholesale.", 1).replace(
    "1. Customer/assurance/production-payable variants:",
    "1. Delivered in P2b (corporate-v2/result.md): customer/assurance/production-payable variants:", 1).replace(
    "Complete P2 customer/source variants next.",
    "Complete P2c asset/benefit/tax variants and the remaining separate-contract\ncomposition, variable consideration, nonzero return recovery costs and\nunmeasurable-progress fallback next.", 1)
backup = HERE / "controls-before-p2b"
backup.mkdir(exist_ok=False)
entries = []
for p in paths:
    target = ROOT / p
    before = target.read_bytes()
    saved = backup / target.name
    saved.write_bytes(before)
    target.write_text(prepared[p])
    entries.append({"path": p, "before_sha256": hashlib.sha256(before).hexdigest(),
                    "after_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
assert subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT) == index
(backup / "refresh.json").write_text(json.dumps({"date": "2026-10-15", "controls": entries,
    "index_preserved": True, "manuscript_version": "3.13", "readiness": "not_ready"}, indent=2) + "\n")
print(json.dumps({"refreshed": len(entries), "index_preserved": True, "v2_hashes_match": True}))
