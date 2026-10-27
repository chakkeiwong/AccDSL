"""One-shot publication of verified EPS supplement; preserve prior evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
ARCHIVE = ROOT / "data/accounting-master/p17-completion-20261014/control-refresh-19"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-continuation-requirements-20261007.md",
            "docs/plans/accounting-p17-completion-20261014.md",
            "docs/plans/accounting-p18-completion-20261014.md", "data/accounting-master/next-plan.md"]
OLD_HASH = "80fe67ccd17dfc412eaf2db7b52035a158bff9c53485e41b33b00dc70cd27120"
NEW_HASH = "a45c9368d89a10981010a60513ad2fce2508c9b6ce0cb964815a6cef63ff077f"
SUMMARY = "P17-08/10/11's sector-evidence revision supplement is integrated in Version 2.91: 29 composition traces, 235 independent checks, 22 EPS financing-repair checks and 100 preservation/build checks pass; seven rendered pages were inspected. Time admission, candidate membership, frozen/current results and exact replay preserve committed books. The EPS coupon schedule is now explicit and the after-coupon conversion transfer is corrected from9600 to9200; EPS values are unchanged. Result: data/accounting-master/p17-completion-20261014/P17-08/sector-revision/result.md. P17/E01/E07/E14 remain open."
OLD_NEXT = 'Next: execute the audited P17-08/10/11 sector-evidence revision plan (docs/plans/accounting-sector-evidence-revision-20261014.md). Connect original credit risk and treaty timing to admission cutoffs, candidate membership, frozen/current results and unchanged committed books; withhold unsupported monetary corrections. Runtime execution remains held.'
NEXT = 'Next: execute the audited P17-04/08/11 error-versus-estimate bridge plan (docs/plans/accounting-error-estimate-bridge-20261014.md). Read the retained AASB108 standard, then distinguish new estimates from prior errors through comparative, opening-equity and current-book bridges with explicit availability, materiality and treatment limits. Runtime execution remains held.'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + chr(10))

assert not ARCHIVE.exists()
for filename, count in [("exchange-checks.json",235), ("eps-repair-checks.json",22), ("manuscript-checks.json",100)]:
    result = json.loads((OUT/filename).read_text())
    assert result["passed"] and result["check_count"] == count, filename
pdf = ROOT/"docs/design/proposal/manuscript-sector-revision-20261014/accounting-product-proposal.pdf"
assert sha(pdf) == NEW_HASH
index = subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT)
assert index == (ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
originals = {n: (ROOT/n).read_text() for n in CONTROLS}
updates = {}
for name, s in originals.items():
    for old, new in [('manuscript-eps-lifecycle-20261014/accounting-product-proposal.pdf', 'manuscript-sector-revision-20261014/accounting-product-proposal.pdf'), ('Version **2.90**', 'Version **2.91**'), ('**Version 2.90,', '**Version 2.91,'), ('Version 2.90, 266', 'Version 2.91, 268'), ('current Version 2.90 candidate', 'current Version 2.91 candidate'), ('progress — Version 2.90', 'progress — Version 2.91'), ('266 pages', '268 pages'), ('2.73–2.90', '2.73–2.91'), ('through 2.90', 'through 2.91'), ('Version2.90 and full2.72 assessment', 'Version2.91 and full2.72 assessment')]+[(OLD_HASH, NEW_HASH),(OLD_NEXT, NEXT)]:
        s = s.replace(old, new)
    if name.endswith("accounting-master-current.md"):
        s = s.replace("**P17-08/10/11: sector revisions, frozen results and committed books.**",
                      "**P17-04/08/11: prior errors, new estimates and comparative bridges.**" + chr(10)*2 + SUMMARY)
        s = s.replace("Six pages of 2.90 received", "Seven pages of 2.91 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s = s.replace("## Latest completed work" + chr(10)*2, "## Latest completed work" + chr(10)*2 + SUMMARY + chr(10)*2, 1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s = s.replace(chr(10) + "P17-05/11's EPS lifecycle", chr(10) + SUMMARY + chr(10)*2 + "P17-05/11's EPS lifecycle", 1)
        s = s.replace("The immediate work is the P17-08/10/11 sector-evidence revision,", "The immediate work is the P17-04/08/11 error-versus-estimate bridge,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s = s.replace(chr(10) + NEXT, chr(10) + SUMMARY + chr(10)*2 + NEXT, 1)
        s = s.replace("the P17-08/10/11 sector-evidence revision is the immediate ready action", "the P17-04/08/11 error-versus-estimate bridge is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s = s.replace("integration follows the audited P17-08/10/11 sector-evidence revision.", "integration follows the audited P17-04/08/11 error-versus-estimate bridge." + chr(10)*2 + SUMMARY)
    else:
        s = s.replace("1. " + NEXT, "1. " + NEXT + chr(10) + "   " + SUMMARY, 1)
        s = s.replace("EPS lifecycle in 2.90.", "EPS lifecycle in 2.90; sector revisions and EPS financing repair in 2.91.")
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
matrix = ROOT/"data/accounting-master/p17-completion-20261014/P17-08/operation-matrix.md"
(OUT/"before").mkdir(exist_ok=True)
shutil.copy2(matrix, OUT/"before/cross-cutting-operation-matrix.md")
s = matrix.read_text().replace("current2.84","current2.91")
s = s.replace("Connect sector original-risk/group/treaty dates with frozen-result/new-manifest receipts", "Delivered2.91: bank original-risk admission, treaty-order revisions, membership/ancestry invalidation, frozen/current results and exact original replay. Actual availability, full portable composition/runtime and accounting correction treatment remain")
s += chr(10)+"Sector-revision composition delivered; see sector-revision/result.md. The same successor repairs the EPS financing coupon schedule without changing EPS values. Continue the prior-error versus new-estimate comparative bridge; wider numerical/continuous and mapping contracts remain open."+chr(10)
matrix.write_text(s)
financing=ROOT/"data/accounting-master/p17-completion-20261014/P17-05/operation-matrix.md"
shutil.copy2(financing,OUT/"before/financing-operation-matrix.md")
financing.write_text(financing.read_text().replace("Refreshed through2.90", "Refreshed through2.91")+chr(10)+"Version2.91 repairs the supplied EPS bond's coupon/EIR schedule:400 coupon1October, conversion liability9200 after payment; the prior9600 transfer is superseded for this schedule. EPS amounts unchanged. See ../P17-08/sector-revision/eps-financing-repair.md."+chr(10))
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"], cwd=ROOT) == index
assert all((ROOT/n).read_text() == v for n,v in updates.items())
save(ARCHIVE/"refresh-manifest.json", {"before": before, "after": {n:sha(ROOT/n) for n in CONTROLS}, "index_preserved":True, "next":NEXT})
(ARCHIVE/"execution-note.md").write_text("# Control refresh19" + chr(10)*2 + "Closeout audit: exact candidate/hash, separate arithmetic/source/preservation checks, source dates and scoped claims verified. Check counts do not establish wider readiness. Prior controls and index preserved." + chr(10)*2 + SUMMARY + chr(10)*2 + NEXT + chr(10))
paths = [p for p in OUT.rglob("*") if p.is_file() and p.name != "run-manifest.json"]
paths += [ROOT/n for n in CONTROLS]
paths += [ROOT/"docs/plans/accounting-sector-evidence-revision-20261014.md", ROOT/"docs/plans/accounting-error-estimate-bridge-20261014.md", ROOT/"docs/design/proposal/architecture/sector-evidence-revision-20261014.md", pdf, matrix]
save(OUT/"run-manifest.json", {
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "recorded_utc":datetime.now(timezone.utc).isoformat(),
    "environment":"System Python Fraction; LuaLaTeX; Poppler/PyMuPDF",
    "cpu_gpu_status":"CPU documentary checks; no numerical framework/GPU initialization",
    "random_seeds":"N/A; exact deterministic authored case",
    "data_version":"Authored bank/insurance evidence revisions; pinned H5/evidencev3/timev2/persistencev1; prior bank2.82 insurance2.83/2.88; EPS financing repair",
    "plan":"docs/plans/accounting-sector-evidence-revision-20261014.md", "result":str((OUT/"result.md").relative_to(ROOT)),
    "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["build_fixture.py","verify_traces.py","check_eps_repair.py","prepare.py","verify_candidate.py","closeout.py"]],
    "exchange_checks":json.loads((OUT/"exchange-checks.json").read_text())["check_count"],
    "verification_seconds":json.loads((OUT/"exchange-checks.json").read_text())["wall_seconds"],
    "build_record":json.loads((OUT/"build-run.json").read_text()),
    "source_records":["revision-traces.json","eps-financing-repair.md"],
    "render_records":["first-render/render-manifest.json"],
    "eps_repair_seconds":json.loads((OUT/"eps-repair-checks.json").read_text())["wall_seconds"],
    "manuscript_verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
    "wall_time_note":"Build/check/access timings retained; total interactive authoring time not measured",
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.91","controls":6,"index_preserved":True,"next":"P17-04/08/11 error-estimate bridge"}))
