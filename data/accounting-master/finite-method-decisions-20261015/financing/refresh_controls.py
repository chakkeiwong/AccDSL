"""Refresh verified 2.96 controls once, preserving their exact predecessors."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform, re, shutil, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
ARCHIVE = OUT / "control-before-r03b"
FILES = [
    "docs/plans/accounting-master-current.md",
    "docs/plans/accounting-master-checkpoint.md",
    "docs/plans/accounting-continuation-requirements-20261007.md",
    "docs/plans/accounting-p17-completion-20261014.md",
    "docs/plans/accounting-p18-completion-20261014.md",
    "data/accounting-master/next-plan.md",
]
MATRIX = "data/accounting-master/p17-completion-20261014/P17-05/operation-matrix.md"
OLD = "fc496a3d2bb1b6453e474afbfe8ca6742ced3ecbec460bf6672bbe85a665c2c8"
NEW = "10af497755650076da3ee4516cea72359528ba09aedef3a1082f97e800dc00a4"
SUMMARY = ("R03-A's scoped financing repair is integrated in Version 2.96: "
           "nine cases, 302 independent checks and 103 preservation/build checks pass; "
           "seven rendered pages were inspected. Repurchase/inducement allocation, "
           "cash-flow reserve transfers, fair-value hedge amortisation and conditional "
           "benchmark reform are explicit. Historical authority, actual valuations and "
           "broader financing residuals remain distinct. Result: "
           "data/accounting-master/finite-method-decisions-20261015/financing/result.md. "
           "R03 and full readiness remain open.")
NEXT = ("Next: continue R03-B priced insurance guarantees and acquisition/reinsurance "
        "interactions under docs/plans/accounting-finite-method-decisions-20261015.md, "
        "then R03-C bank, R03-D group bindings and R03-E finite corporate/authority decisions. "
        "Continue ready R04 literature, R05 future validation protocols and R06 reuse locks "
        "before R07/R08. Runtime execution remains held.")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert not ARCHIVE.exists()
checks = {}
for name in ["independent-checks.json", "manuscript-checks.json"]:
    value = json.loads((OUT / name).read_text())
    assert value["passed"] and all(row["passed"] for row in value["checks"])
    checks[name] = value
pdf = ROOT / "docs/design/proposal/manuscript-financing-changes-20261015/accounting-product-proposal.pdf"
assert sha(pdf) == NEW and (OUT / "result.md").exists()
index = subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT)
assert index == (ROOT / "data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
updates = {}
for name in FILES:
    original = (ROOT / name).read_text()
    text = original.replace(
        "manuscript-real-package-20261015/accounting-product-proposal.pdf",
        "manuscript-financing-changes-20261015/accounting-product-proposal.pdf"
    ).replace(OLD, NEW)
    for a, b in [
        ("Version **2.95**, 281", "Version **2.96**, 284"),
        ("**Version 2.95, 281", "**Version 2.96, 284"),
        ("Version 2.95, 281", "Version 2.96, 284"),
        ("current Version 2.95 candidate", "current Version 2.96 candidate"),
        ("through 2.95", "through 2.96"),
        ("2.73–2.95", "2.73–2.96"),
        ("Version2.95 and full2.72 assessment", "Version2.96 and full2.72 assessment"),
    ]:
        text = text.replace(a, b)
    text = re.sub(r"Next: execute R03 finite method[^\n]*", NEXT, text)
    text = text.replace(
        "## Real-package completion and next work — 15 October 2026",
        "## Financing repair and next work — 15 October 2026\n\n" + SUMMARY +
        "\n\n" + NEXT + "\n\n## Real-package completion — 15 October 2026", 1
    )
    assert text != original and SUMMARY in text
    updates[name] = text
matrix = (ROOT / MATRIX).read_text().replace(
    "Refreshed through2.91; preceding scoped audit2.81.",
    "Refreshed through2.96; preceding scoped audits2.81/2.91."
).replace(
    "Induced/early conversion, options, cash alternatives and legal-capital regimes need precise support",
    "Delivered2.96: unchanged-rights repurchase and immediate unconditional share-only inducement, with amendment-date measurement and cash-alternative classification boundaries. Delayed/contingent inducement, option valuation and actual legal-capital regimes remain"
).replace(
    "Hedge designation/effectiveness/OCI/reclassification and reform-specific methods remain open; choose source-supported scope before examples",
    "Delivered2.96: historical eligibility, cumulative effectiveness, inventory basis adjustment, earnings/cancellation releases, fair-value adjustment amortisation and conditional benchmark reform. Actual valuation, excluded components, general rebalancing/group hedges and current authority remain"
)
matrix += ("\nVersion2.96's scoped financing repair has nine cases,302 independent checks "
           "and103 preservation/build checks; seven rendered pages inspected. See "
           "../../finite-method-decisions-20261015/financing/result.md. R03-B–E and "
           "the remaining financing/profile decisions continue; no full-method closure is asserted.\n")
updates[MATRIX] = matrix
before = {name: sha(ROOT / name) for name in updates}
for name in updates:
    target = ARCHIVE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, target)
for name, value in updates.items():
    (ROOT / name).write_text(value)
assert subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT) == index
(OUT / "control-refresh.json").write_text(json.dumps({
    "recorded_utc": datetime.now(timezone.utc).isoformat(), "before": before,
    "after": {name: sha(ROOT / name) for name in updates},
    "index_preserved": True, "next": NEXT
}, indent=2) + "\n")
commands = [
    "python3 data/accounting-master/finite-method-decisions-20261015/financing/" + name + ".py"
    for name in ["build_cases", "verify_cases", "prepare_manuscript", "verify_manuscript", "refresh_controls"]
]
commands += [
    "python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-financing-changes-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/financing --timeout 240 --force",
    "python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-financing-changes-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/financing/final-render --pages 1,163-168 --dpi 110"
]
sources = json.loads((OUT / "source-support.json").read_text())
manifest = {
    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "worktree": "dirty; 100 unrelated staged entries preserved; no commit",
    "commands": commands,
    "environment": {"python": platform.python_version(), "execution": "exact fractions and document build",
                    "cpu": "CPU documentary checks", "gpu": "N/A; no GPU or numerical framework"},
    "data_version": [{"id": row["id"], "pdf": row["pdf"], "pdf_sha256": row["pdf_sha256"]}
                     for row in sources["authorities"]],
    "random_seeds": "N/A; deterministic illustrative arithmetic",
    "wall_time": {"independent_checks_seconds": checks["independent-checks.json"]["wall_seconds"],
                  "build": json.loads((OUT / "build-run.json").read_text()),
                  "interactive_total": "not measured"},
    "plan": "docs/plans/accounting-financing-changes-20261015.md",
    "result": str((OUT / "result.md").relative_to(ROOT)),
    "candidate_pdf": str(pdf.relative_to(ROOT)), "candidate_pdf_sha256": NEW,
    "artifacts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)}
                  for p in sorted(OUT.glob("*")) if p.is_file() and p.name != "run-manifest.json"]
}
(OUT / "run-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"candidate": "2.96", "controls": len(FILES),
                  "matrix": "P17-05", "index_preserved": True, "next": "R03-B"}))
