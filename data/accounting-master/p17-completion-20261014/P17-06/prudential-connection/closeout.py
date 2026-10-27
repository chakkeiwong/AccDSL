"""One-shot publication of verified bank supplement; preserve prior evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
ARCHIVE = ROOT / "data/accounting-master/p17-completion-20261014/control-refresh-17"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-continuation-requirements-20261007.md",
            "docs/plans/accounting-p17-completion-20261014.md",
            "docs/plans/accounting-p18-completion-20261014.md", "data/accounting-master/next-plan.md"]
OLD_HASH = "78317ab2612b9752f2e686f269c2a202ede9b0fef9e06d673ff12f59b2166050"
NEW_HASH = "cee2973969d744c36890c032adb04154efbadf7ee595c342465711245cfc8086"
SUMMARY = ("P17-06/11's bank-prudential connection is integrated in Version 2.89: "
           "108 exact accounting/capital/decision checks, 32 source checks and 97 preservation/build checks pass; "
           "eight rendered pages were inspected. One conditional US national-bank book connects earnings, "
           "eligible capital, allowance-cap ordering, exposures and a separately supplied leverage average. "
           "The frozen 1 January2026 rule snapshot and older instruction cross-check do not establish actual-date "
           "compliance or payout permission. Result: data/accounting-master/p17-completion-20261014/P17-06/"
           "prudential-connection/result.md. This advances scoped MC02/05/13–17/19–21/24–28/30/32–35; P17/E07/E14 remain open.")
OLD_NEXT = ("Next: execute the audited P17-06/11 bank-prudential connection plan "
            "(docs/plans/accounting-bank-prudential-connection-20261014.md). Reconcile one synthetic US bank's "
            "book, eligible capital, allowance limits, exposures and separate regulatory denominators under "
            "the retained dated rules; preserve missing eligibility/averaging inputs. Runtime execution remains held.")
NEXT = ("Next: execute the audited P17-05/11 EPS lifecycle plan "
        "(docs/plans/accounting-eps-lifecycle-20261014.md). Read the retained IAS33 text and application guidance, "
        "then reconcile dated ordinary shares, retrospective split factors, attributed earnings and sequential "
        "dilution without mutating the book. Runtime execution remains held.")

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + chr(10))

assert not ARCHIVE.exists()
for filename, count in [("calculation-checks.json",108), ("source-checks.json",32), ("manuscript-checks.json",97)]:
    result = json.loads((OUT/filename).read_text())
    assert result["passed"] and result["check_count"] == count, filename
pdf = ROOT/"docs/design/proposal/manuscript-bank-prudential-20261014/accounting-product-proposal.pdf"
assert sha(pdf) == NEW_HASH
index = subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT)
assert index == (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
originals = {n: (ROOT/n).read_text() for n in CONTROLS}
updates = {}
for name, s in originals.items():
    for old, new in [
        ("manuscript-insurance-atomic-20261014/accounting-product-proposal.pdf", "manuscript-bank-prudential-20261014/accounting-product-proposal.pdf"),
        (OLD_HASH, NEW_HASH), ("Version **2.88**", "Version **2.89**"),
        ("**Version 2.88,", "**Version 2.89,"), ("Version 2.88, 260", "Version 2.89, 263"),
        ("current Version 2.88 candidate", "current Version 2.89 candidate"),
        ("progress — Version 2.88", "progress — Version 2.89"), ("260 pages", "263 pages"),
        ("2.73–2.88", "2.73–2.89"), ("through 2.88", "through 2.89"),
        ("Version2.88 and full2.72 assessment", "Version2.89 and full2.72 assessment"), (OLD_NEXT, NEXT)]:
        s = s.replace(old, new)
    if name.endswith("accounting-master-current.md"):
        s = s.replace("**P17-06/11: one bank book and its regulatory capital.**",
                      "**P17-05/11: dated shares and basic/diluted EPS.**" + chr(10)*2 + SUMMARY)
        s = s.replace("Seven pages of 2.88 received", "Eight pages of 2.89 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s = s.replace("## Latest completed work" + chr(10)*2, "## Latest completed work" + chr(10)*2 + SUMMARY + chr(10)*2, 1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s = s.replace(chr(10) + "P17-10/11's connected-insurance", chr(10) + SUMMARY + chr(10)*2 + "P17-10/11's connected-insurance", 1)
        s = s.replace("The immediate work is the P17-06/11 bank-prudential connection,", "The immediate work is the P17-05/11 EPS lifecycle,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s = s.replace(chr(10) + NEXT, chr(10) + SUMMARY + chr(10)*2 + NEXT, 1)
        s = s.replace("the P17-06/11 bank-prudential connection is the immediate ready action", "the P17-05/11 EPS lifecycle is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s = s.replace("integration follows the audited P17-06/11 bank-prudential connection.", "integration follows the audited P17-05/11 EPS lifecycle." + chr(10)*2 + SUMMARY)
    else:
        s = s.replace("1. " + NEXT, "1. " + NEXT + chr(10) + "   " + SUMMARY, 1)
        s = s.replace("insurance atomic commit in 2.88.", "insurance atomic commit in 2.88; bank prudential connection in 2.89.")
    assert s != originals[name] and OLD_NEXT not in s, name
    assert SUMMARY in s, name
    updates[name] = s
before = {}
for name in CONTROLS:
    target = ARCHIVE/"before"/name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT/name, target)
    before[name] = sha(ROOT/name)
for name, s in updates.items():
    (ROOT/name).write_text(s)
matrix = ROOT/"data/accounting-master/p17-completion-20261014/P17-06/operation-matrix.md"
(OUT/"before").mkdir(exist_ok=True)
shutil.copy2(matrix, OUT/"before/bank-operation-matrix.md")
s = matrix.read_text().replace("current candidate2.82", "current candidate2.89")
s = s.replace("Same-bank accounting-to-capital-to-exposure/RWA connected case with actual dated rules and inputs remains; cannot combine arbitrary AASB case with US capital assumptions",
              "Delivered in 2.89: conditional US bank book, eligible capital, gross exposures, allowance-cap/excess ordering and separate leverage average under a frozen 1 January2026 snapshot; actual facts, operative-date amendment chain, broader exposures/adjustments and calibration remain")
s = s[:s.index("Commitment/drawdown delivered;")] + "Commitment/drawdown and the scoped bank-prudential connection are delivered; see commitment-draw/result.md and prudential-connection/result.md. Preserve actual-fact, full-rule and calibration residuals. Continue P17-05/11 EPS lifecycle; missing human acceptance does not stop provisional design." + chr(10)
matrix.write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT) == index
assert all((ROOT/n).read_text() == v for n,v in updates.items())
save(ARCHIVE/"refresh-manifest.json", {"before": before, "after": {n:sha(ROOT/n) for n in CONTROLS}, "index_preserved":True, "next":NEXT})
(ARCHIVE/"execution-note.md").write_text("# Control refresh17" + chr(10)*2 + "Closeout audit: exact candidate/hash, separate arithmetic/source/preservation checks, source dates and scoped claims verified. Check counts do not establish wider readiness. Prior controls and index preserved." + chr(10)*2 + SUMMARY + chr(10)*2 + NEXT + chr(10))
paths = [p for p in OUT.rglob("*") if p.is_file() and p.name != "run-manifest.json"]
paths += [ROOT/n for n in CONTROLS]
paths += [ROOT/"docs/plans/accounting-bank-prudential-connection-20261014.md", ROOT/"docs/plans/accounting-eps-lifecycle-20261014.md", ROOT/"docs/design/proposal/methods/bank-prudential-connection-20261014.md", pdf, matrix]
save(OUT/"run-manifest.json", {
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "recorded_utc":datetime.now(timezone.utc).isoformat(),
    "environment":"System Python Fraction; LuaLaTeX; Poppler/PyMuPDF",
    "cpu_gpu_status":"CPU documentary checks; no numerical framework/GPU initialization",
    "random_seeds":"N/A; exact deterministic authored case",
    "data_version":"Synthetic restricted US bank; eCFR 1 January2026 snapshot; December2024 FFIEC051 ordering cross-check",
    "plan":"docs/plans/accounting-bank-prudential-connection-20261014.md", "result":str((OUT/"result.md").relative_to(ROOT)),
    "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["check_case.py","check_sources.py","prepare.py","verify_candidate.py","closeout.py"]],
    "calculation_record":json.loads((OUT/"calculation-run.json").read_text()),
    "build_record":json.loads((OUT/"build-run.json").read_text()),
    "source_access_records":["access-receipts.json","instruction-access-receipts.json"],
    "render_records":["first-render/render-manifest.json"],
    "source_check_seconds":json.loads((OUT/"source-checks.json").read_text())["wall_seconds"],
    "manuscript_verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
    "wall_time_note":"Build/check/access timings retained; total interactive authoring time not measured",
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.89","controls":6,"index_preserved":True,"next":"P17-05/11 EPS lifecycle"}))
