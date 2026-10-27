"""One-shot publication of verified EPS supplement; preserve prior evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
ARCHIVE = ROOT / "data/accounting-master/p17-completion-20261014/control-refresh-18"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-continuation-requirements-20261007.md",
            "docs/plans/accounting-p17-completion-20261014.md",
            "docs/plans/accounting-p18-completion-20261014.md", "data/accounting-master/next-plan.md"]
OLD_HASH = "cee2973969d744c36890c032adb04154efbadf7ee595c342465711245cfc8086"
NEW_HASH = "80fe67ccd17dfc412eaf2db7b52035a158bff9c53485e41b33b00dc70cd27120"
SUMMARY = "P17-05/11's EPS lifecycle is integrated in Version 2.90: 105 exact calculation/admission checks, 31 source checks and 97 preservation/build checks pass; six rendered pages were inspected. Dated shares, split adjustments, attributed earnings, sequential dilution and actual conversion/lapse cases preserve separate monetary events. The retained historical IAS33 text and supplied terms do not establish current issuer compliance or award valuation. Result: data/accounting-master/p17-completion-20261014/P17-05/eps-lifecycle/result.md. This advances scoped MC02/06/07/11/13/15–17/19/20/24–28/30/32–35; P17/E07/E14 remain open."
OLD_NEXT = 'Next: execute the audited P17-05/11 EPS lifecycle plan (docs/plans/accounting-eps-lifecycle-20261014.md). Read the retained IAS33 text and application guidance, then reconcile dated ordinary shares, retrospective split factors, attributed earnings and sequential dilution without mutating the book. Runtime execution remains held.'
NEXT = 'Next: execute the audited P17-08/10/11 sector-evidence revision plan (docs/plans/accounting-sector-evidence-revision-20261014.md). Connect original credit risk and treaty timing to admission cutoffs, candidate membership, frozen/current results and unchanged committed books; withhold unsupported monetary corrections. Runtime execution remains held.'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + chr(10))

assert not ARCHIVE.exists()
for filename, count in [("calculation-checks.json",105), ("source-checks.json",31), ("manuscript-checks.json",97)]:
    result = json.loads((OUT/filename).read_text())
    assert result["passed"] and result["check_count"] == count, filename
pdf = ROOT/"docs/design/proposal/manuscript-eps-lifecycle-20261014/accounting-product-proposal.pdf"
assert sha(pdf) == NEW_HASH
index = subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT)
assert index == (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
originals = {n: (ROOT/n).read_text() for n in CONTROLS}
updates = {}
for name, s in originals.items():
    for old, new in [('manuscript-bank-prudential-20261014/accounting-product-proposal.pdf', 'manuscript-eps-lifecycle-20261014/accounting-product-proposal.pdf'), ('Version **2.89**', 'Version **2.90**'), ('**Version 2.89,', '**Version 2.90,'), ('Version 2.89, 263', 'Version 2.90, 266'), ('current Version 2.89 candidate', 'current Version 2.90 candidate'), ('progress — Version 2.89', 'progress — Version 2.90'), ('263 pages', '266 pages'), ('2.73–2.89', '2.73–2.90'), ('through 2.89', 'through 2.90'), ('Version2.89 and full2.72 assessment', 'Version2.90 and full2.72 assessment')]+[(OLD_HASH, NEW_HASH),(OLD_NEXT, NEXT)]:
        s = s.replace(old, new)
    if name.endswith("accounting-master-current.md"):
        s = s.replace("**P17-05/11: dated shares and basic/diluted EPS.**",
                      "**P17-08/10/11: sector revisions, frozen results and committed books.**" + chr(10)*2 + SUMMARY)
        s = s.replace("Eight pages of 2.89 received", "Six pages of 2.90 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s = s.replace("## Latest completed work" + chr(10)*2, "## Latest completed work" + chr(10)*2 + SUMMARY + chr(10)*2, 1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s = s.replace(chr(10) + "P17-06/11's bank-prudential", chr(10) + SUMMARY + chr(10)*2 + "P17-06/11's bank-prudential", 1)
        s = s.replace("The immediate work is the P17-05/11 EPS lifecycle,", "The immediate work is the P17-08/10/11 sector-evidence revision,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s = s.replace(chr(10) + NEXT, chr(10) + SUMMARY + chr(10)*2 + NEXT, 1)
        s = s.replace("the P17-05/11 EPS lifecycle is the immediate ready action", "the P17-08/10/11 sector-evidence revision is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s = s.replace("integration follows the audited P17-05/11 EPS lifecycle.", "integration follows the audited P17-08/10/11 sector-evidence revision." + chr(10)*2 + SUMMARY)
    else:
        s = s.replace("1. " + NEXT, "1. " + NEXT + chr(10) + "   " + SUMMARY, 1)
        s = s.replace("bank prudential connection in 2.89.", "bank prudential connection in 2.89; EPS lifecycle in 2.90.")
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
matrix = ROOT/"data/accounting-master/p17-completion-20261014/P17-05/operation-matrix.md"
(OUT/"before").mkdir(exist_ok=True)
shutil.copy2(matrix, OUT/"before/financing-operation-matrix.md")
s = matrix.read_text().replace("Refreshed through2.81; baseline2.80.","Refreshed through2.90; preceding scoped audit2.81.")
s = s.replace("Basic/diluted EPS lifecycle, weighting/splits/antidilution and award accounting interaction remain method work; do not turn Apple report reconciliation into complete IAS33/ASC260 method", "Delivered2.90: historical IAS33 dated-share, split, basic/diluted, ordered antidilution, conversion/lapse and supplied future-service bridge; actual award valuation/expense, performance/cash-alternative/participating profiles and current-standard admission remain")
s = s.replace("Foreign goodwill and disposal connection addressed next; hyperinflation/exchangeability/hedging remain specific methods", "Foreign goodwill and disposal delivered2.81; hyperinflation/exchangeability/hedging remain specific methods")
s = s[:s.index("The group-fx-disposal unit is delivered.")]+"The group-FX disposal and bounded EPS lifecycle units are delivered. Continue P17-08/10/11 sector-evidence revisions, preserving financing/hedging and broader EPS residuals. No current multi-GAAP admission, runtime or complete issuer history follows."+chr(10)
matrix.write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT) == index
assert all((ROOT/n).read_text() == v for n,v in updates.items())
save(ARCHIVE/"refresh-manifest.json", {"before": before, "after": {n:sha(ROOT/n) for n in CONTROLS}, "index_preserved":True, "next":NEXT})
(ARCHIVE/"execution-note.md").write_text("# Control refresh18" + chr(10)*2 + "Closeout audit: exact candidate/hash, separate arithmetic/source/preservation checks, source dates and scoped claims verified. Check counts do not establish wider readiness. Prior controls and index preserved." + chr(10)*2 + SUMMARY + chr(10)*2 + NEXT + chr(10))
paths = [p for p in OUT.rglob("*") if p.is_file() and p.name != "run-manifest.json"]
paths += [ROOT/n for n in CONTROLS]
paths += [ROOT/"docs/plans/accounting-eps-lifecycle-20261014.md", ROOT/"docs/plans/accounting-sector-evidence-revision-20261014.md", ROOT/"docs/design/proposal/methods/eps-lifecycle-20261014.md", pdf, matrix]
save(OUT/"run-manifest.json", {
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "recorded_utc":datetime.now(timezone.utc).isoformat(),
    "environment":"System Python Fraction; LuaLaTeX; Poppler/PyMuPDF",
    "cpu_gpu_status":"CPU documentary checks; no numerical framework/GPU initialization",
    "random_seeds":"N/A; exact deterministic authored case",
    "data_version":"Synthetic 2025 share history; retained original EU2023/1803 IAS33 and title-date corrigendum",
    "plan":"docs/plans/accounting-eps-lifecycle-20261014.md", "result":str((OUT/"result.md").relative_to(ROOT)),
    "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["check_case.py","check_sources.py","prepare.py","verify_candidate.py","closeout.py"]],
    "calculation_record":json.loads((OUT/"calculation-run.json").read_text()),
    "build_record":json.loads((OUT/"build-run.json").read_text()),
    "source_records":["source-manifest.json","source-review.md"],
    "render_records":["first-render/render-manifest.json"],
    "source_check_seconds":json.loads((OUT/"source-checks.json").read_text())["wall_seconds"],
    "manuscript_verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
    "wall_time_note":"Build/check/access timings retained; total interactive authoring time not measured",
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.90","controls":6,"index_preserved":True,"next":"P17-08/10/11 sector-evidence revision"}))
