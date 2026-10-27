"""One-shot customer-profile freeze and live documentary control refresh."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "corporate-v5"
assert not (OUT / "run-manifest.json").exists(), "Do not rerun a profile closeout"
checks = json.loads((OUT / "checks.json").read_text())
assert checks["passed"] and checks["count"] == 7160
assert checks["financial_steps"] == 161 and checks["exchanges"] == 670
packet = json.loads((OUT / "portable-exchanges.json").read_text())
methods = [r["body"] for r in packet["record_registry"].values() if r["kind"] == "MethodDefinition"]
assert len(methods) == 94
assert sum(x["method_status"] == "specified_finite" for x in methods) == 93
assert [x["method_id"] for x in methods if x["method_status"] != "specified_finite"] == ["rcost.settle"]
index = subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT)
assert index == (ROOT / "data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
for file in [HERE / "protected-inputs.json", OUT / "predecessor.json"]:
    for pin in json.loads(file.read_text())["files"]:
        assert hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"], pin["path"]

paths = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
         "docs/plans/accounting-continuation-requirements-20261007.md",
         "docs/plans/accounting-p17-completion-20261014.md",
         "docs/plans/accounting-p18-completion-20261014.md", "data/accounting-master/next-plan.md"]
tag = "## Extended method exchanges in progress — 15 October 2026"
section = """R03-P1 maps all46 operation rows and protects204 inputs. CorporateComponents/5
retains /1–/4 and passes7,160 documentary checks across93 supported finite
methods plus one unresolved settlement boundary,161 transitions in61 paths,
670 exchanges and28 annual reports. Complete customer advance/invoice/collection,
separate additions, variable consideration and cost-recovery fallback have
typed positive/adverse paths. Actual nonzero-cost return settlement is unspecified.
Result: data/accounting-master/extended-method-exchanges-20261015/corporate-v5/result.md.
All13 corporate rows are reconciled in the sibling p2-coverage-reconciliation.md;
P2 residual methods/authority and P5 combined-company joins remain open.
Next ready work: P3 financing/bank/group and P4 insurance successors, then P5
integration, R04/R06 residuals, R07 and all53/interactions R08. Active PDF:
Version3.13,340 pages. Full readiness is not_ready; runtime/empirical work is held."""
prepared = {}
for path in paths:
    old = (ROOT / path).read_text()
    assert old.count(tag) == 1
    prefix, tail = old.split(tag)
    prior, rest = tail.split("\n## ", 1)
    assert "4,809" in prior
    prepared[path] = prefix + tag + "\n\n" + section + "\n\n## " + rest
next_path = str((HERE / "next-units.md").relative_to(ROOT))
prepared[next_path] = (ROOT / next_path).read_text() + """
## P2d customer increment delivered — 15 October 2026

CorporateComponents/5 passes7,160 checks across93 supported finite methods and
one unresolved actual-return settlement boundary,161 transitions/61 paths and
670 exchanges. Ten new customer paths retain gross rights, advance consumption,
separate allocation, original bonus identities and unknown progress. The exact
profile and predecessor bytes are frozen. See corporate-v5/result.md.

All13 corporate rows are now reconciled in p2-coverage-reconciliation.md. P2
is not closed: all-zero reversal, heterogeneous lease allocation, actual-return
settlement, further benefit/tax interactions and operative authority remain
named dependencies. P5 still owes complete company/report joins and migration.
Next execute the independently ready P3 financing/bank/group successors and P4
insurance, then P5/R04/R06/R07/R08. Preserve /1–/5, Version3.13, the negative
Version2.72 all53 assessment and the100-entry staged index.
"""
backup = HERE / "controls-before-p2d-customer"
backup.mkdir(exist_ok=False)
refresh = []
for path, content in prepared.items():
    p = ROOT / path
    before = p.read_bytes()
    (backup / p.name).write_bytes(before)
    p.write_text(content)
    refresh.append({"path": path, "before_sha256": hashlib.sha256(before).hexdigest(),
                    "after_sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
(backup / "refresh.json").write_text(json.dumps(refresh, indent=2) + "\n")
run = json.loads((OUT / "validation-run.json").read_text())
assert all(x["exit_code"] == 0 for x in run["runs"])
manifest = {
    "date": "2026-10-15", "profile": "CorporateComponents/5",
    "git_commit": run["git_commit"], "plan": str((HERE / "customer-successor-plan.md").relative_to(ROOT)),
    "result": str((OUT / "result.md").relative_to(ROOT)), "validation": run,
    "data_version": "Retained historical AASB/EU sources; inherited finite cases and explicit synthetic customer premises",
    "random_seeds": "N/A: exact deterministic arithmetic", "checks": checks["count"],
    "supported_methods": 93, "unsupported_method_boundaries": ["rcost.settle"],
    "financial_steps": 161, "paths": 61, "exchanges": 670, "annual_reports": 28,
    "readiness": "not_ready", "index_preserved": True,
    "index_sha256": hashlib.sha256(index).hexdigest(),
    "control_refresh": str((backup / "refresh.json").relative_to(ROOT)),
    "related_artifacts": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in [HERE / "p2-coverage-reconciliation.md", Path(__file__)]],
    "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(OUT.rglob("*")) if p.is_file()],
    "next": "P3/P4 sector successors; P2 residuals; P5 integration and R04/R06/R07/R08",
}
assert subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT) == index
(OUT / "run-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"frozen": manifest["profile"], "checks": checks["count"],
                  "controls_refreshed": len(prepared), "index_preserved": True}))
