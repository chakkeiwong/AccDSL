"""Publish checked proposal pointers; preserve all previous evidence and index."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
ARCHIVE=ROOT/"data/accounting-master/p17-completion-20261014/control-refresh-16"
CONTROLS=["docs/plans/accounting-master-current.md","docs/plans/accounting-master-checkpoint.md",
          "docs/plans/accounting-continuation-requirements-20261007.md",
          "docs/plans/accounting-p17-completion-20261014.md",
          "docs/plans/accounting-p18-completion-20261014.md","data/accounting-master/next-plan.md"]
OLD_HASH="1af3ff838342d23e23924a2d5b2fe0038fb3f07a502e81c99212a3144fd11742"
NEW_HASH="78317ab2612b9752f2e686f269c2a202ede9b0fef9e06d673ff12f59b2166050"
SUMMARY=("P17-10/11's connected-insurance atomic-commit specification is integrated in Version 2.88: "
         "27 complete exchanges, 2,428 independent exchange checks and 95 preservation/build checks pass; "
         "seven rendered pages were inspected. Four distinct events preserve component and journal changes, "
         "published dependency closure, replay before freshness and both lost-acknowledgement worlds. "
         "Result: data/accounting-master/p17-completion-20261014/P17-10/insurance-atomic/result.md. "
         "This advances scoped MC02/04/11/13/18/20/22/24/25/27/28/32–35; P17/E07/E14 remain open.")
OLD_NEXT=("Next: execute the audited P17-10/11 connected-insurance atomic-commit plan "
          "(docs/plans/accounting-insurance-atomic-commit-20261014.md). Bind the three separate groups to one "
          "entity/book/branch event with complete journals/component changes, all-or-none publication, "
          "replay-before-freshness and failed-measurement traces. Runtime execution remains held.")
NEXT=("Next: execute the audited P17-06/11 bank-prudential connection plan "
      "(docs/plans/accounting-bank-prudential-connection-20261014.md). Reconcile one synthetic US bank's "
      "book, eligible capital, allowance limits, exposures and separate regulatory denominators under "
      "the retained dated rules; preserve missing eligibility/averaging inputs. Runtime execution remains held.")

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value): p.write_text(json.dumps(value,indent=2)+"\n")

assert not ARCHIVE.exists()
assert json.loads((OUT/"exchange-checks.json").read_text())["passed"]
assert json.loads((OUT/"manuscript-checks.json").read_text())["passed"]
assert sha(ROOT/"docs/design/proposal/manuscript-insurance-atomic-20261014/accounting-product-proposal.pdf")==NEW_HASH
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
before={}
for name in CONTROLS:
    p=ROOT/name; q=ARCHIVE/"before"/name
    q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,q); before[name]=sha(p)
    s=p.read_text()
    for old,new in [
        ("manuscript-reserving-adapter-20261014/accounting-product-proposal.pdf","manuscript-insurance-atomic-20261014/accounting-product-proposal.pdf"),
        (OLD_HASH,NEW_HASH),("Version **2.87**","Version **2.88**"),("**Version 2.87,","**Version 2.88,"),
        ("Version 2.87, 258","Version 2.88, 260"),("current Version 2.87 candidate","current Version 2.88 candidate"),
        ("progress — Version 2.87","progress — Version 2.88"),("258 pages","260 pages"),
        ("2.73–2.87","2.73–2.88"),("through 2.87","through 2.88"),
        ("Version2.87 and full2.72 assessment","Version2.88 and full2.72 assessment"),(OLD_NEXT,NEXT)]:
        s=s.replace(old,new)
    if name.endswith("accounting-master-current.md"):
        s=s.replace("**P17-10/11: connected-insurance atomic commit and replay.**",
                    "**P17-06/11: one bank book and its regulatory capital.**\n\n"+SUMMARY)
        s=s.replace("Six pages of 2.87 received","Seven pages of 2.88 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s=s.replace("## Latest completed work\n\n","## Latest completed work\n\n"+SUMMARY+"\n\n",1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s=s.replace("\nP17-10's reserving-adapter", "\n"+SUMMARY+"\n\nP17-10's reserving-adapter",1)
        s=s.replace("The immediate work is the P17-10/11 insurance atomic-commit interaction,",
                    "The immediate work is the P17-06/11 bank-prudential connection,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s=s.replace("\n"+NEXT,"\n"+SUMMARY+"\n\n"+NEXT,1)
        s=s.replace("the P17-10/11 insurance atomic-commit interaction is the immediate ready action",
                    "the P17-06/11 bank-prudential connection is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s=s.replace("integration follows the audited P17-10/11 insurance atomic-commit interaction.",
                    "integration follows the audited P17-06/11 bank-prudential connection.\n\n"+SUMMARY)
    else:
        s=s.replace("1. "+NEXT,"1. "+NEXT+"\n   "+SUMMARY.replace("data/accounting-master/",""),1)
        s=s.replace("reserving adapter in 2.87.","reserving adapter in 2.87; insurance atomic commit in 2.88.")
    assert s!=p.read_text(),name
    p.write_text(s)
matrix=ROOT/"data/accounting-master/p17-completion-20261014/P17-07/operation-matrix.md"
(OUT/"before").mkdir(exist_ok=True); shutil.copy2(matrix,OUT/"before/insurance-operation-matrix.md")
s=matrix.read_text().replace("Current candidate 2.87","Current candidate 2.88")
s=s.replace("Cross-group version/atomicity/replay acceptance in P17-08/10/11",
            "Version 2.88 supplies four-phase atomic publication/replay and timeout exchanges; actual runtime isolation/durability and broader group interactions remain")
matrix.write_text(s)
assert subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)==index
save(ARCHIVE/"refresh-manifest.json",{"before":before,"after":{n:sha(ROOT/n) for n in CONTROLS},"index_preserved":True,"next":NEXT})
(ARCHIVE/"execution-note.md").write_text("# Control refresh16\n\n"+SUMMARY+"\n\n"+NEXT+"\n")
paths=[p for p in OUT.rglob("*") if p.is_file() and p.name!="run-manifest.json"]
paths += [ROOT/n for n in CONTROLS]
paths += [ROOT/"docs/plans/accounting-insurance-atomic-commit-20261014.md",
          ROOT/"docs/plans/accounting-bank-prudential-connection-20261014.md",
          ROOT/"docs/design/proposal/architecture/insurance-atomic-commit-20261014.md",
          ROOT/"docs/design/proposal/manuscript-insurance-atomic-20261014/accounting-product-proposal.pdf",matrix]
save(OUT/"run-manifest.json",{
    "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
    "recorded_utc":datetime.now(timezone.utc).isoformat(),
    "environment":"System Python Fraction/jsonschema; LuaLaTeX; Poppler/PyMuPDF",
    "cpu_gpu_status":"CPU documentary checks; no numerical framework/GPU initialization",
    "random_seeds":"N/A; exact deterministic authored exchanges",
    "data_version":"Preserved A/B/R timely-treaty case; AASB17 December2022 F2023C00382; pinned common contracts",
    "plan":"docs/plans/accounting-insurance-atomic-commit-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
    "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["build_exchange.py","verify_exchange.py","prepare.py","verify_candidate.py","closeout.py"]],
    "build_record":json.loads((OUT/"build-run.json").read_text()),"render_records":["final-render/render-manifest.json"],
    "verification_record":json.loads((OUT/"verification-run.json").read_text()),
    "manuscript_verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
    "wall_time_note":"Build/check timings retained; total interactive authoring time not measured",
    "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.88","controls":6,"index_preserved":True,"next":"P17-06/11 bank-prudential connection"}))
