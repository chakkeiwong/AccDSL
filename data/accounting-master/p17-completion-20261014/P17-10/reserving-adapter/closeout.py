"""Refresh live controls after checked 2.87; preserve frozen assessments."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
ARCHIVE=ROOT/"data/accounting-master/p17-completion-20261014/control-refresh-15"
controls=["docs/plans/accounting-master-current.md","docs/plans/accounting-master-checkpoint.md",
          "docs/plans/accounting-continuation-requirements-20261007.md",
          "docs/plans/accounting-p17-completion-20261014.md",
          "docs/plans/accounting-p18-completion-20261014.md","data/accounting-master/next-plan.md"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2)+"\n")
assert not ARCHIVE.exists()
assert json.loads((OUT/"manuscript-checks.json").read_text())["passed"]
assert json.loads((OUT/"exchange-checks.json").read_text())["passed"]
summary=("P17-10's reserving-adapter contract is integrated in Version 2.87: "
         "18 complete exchanges, 1,115 independent exchange checks and 93 preservation/build checks pass; "
         "six rendered pages were inspected. The native zero-coercion limitation, process-law identity, "
         "partial/cancelled draws and resume limits are explicit. "
         "Result: data/accounting-master/p17-completion-20261014/P17-10/reserving-adapter/result.md. "
         "This advances scoped MC11/12/20/23–27/30–35; P17/E07/E14 remain open.")
old_next=("Next: execute the refreshed P17-10 reserving-adapter plan "
          "(docs/plans/accounting-reserving-adapter-20261014.md). Bind the inspected native law and zero-coercion behavior "
          "to exact proposed exchanges, partial/cancelled-result semantics and provenance requirements. "
          "No R execution, installation or stochastic campaign starts.")
next_text=("Next: execute the audited P17-10/11 connected-insurance atomic-commit plan "
           "(docs/plans/accounting-insurance-atomic-commit-20261014.md). Bind the three separate groups to one "
           "entity/book/branch event with complete journals/component changes, all-or-none publication, "
           "replay-before-freshness and failed-measurement traces. Runtime execution remains held.")
before={}
for name in controls:
    p=ROOT/name
    q=ARCHIVE/"before"/name
    q.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,q)
    before[name]=sha(p)
    s=p.read_text()
    replacements=[
      ("manuscript-bootstrap-consistency-20261014/accounting-product-proposal.pdf","manuscript-reserving-adapter-20261014/accounting-product-proposal.pdf"),
      ("0ce798be2097f362b76935d46fe185878a362a4d18e317caac3b296dfa751303","1af3ff838342d23e23924a2d5b2fe0038fb3f07a502e81c99212a3144fd11742"),
      ("Version **2.86**","Version **2.87**"),("**Version 2.86,","**Version 2.87,"),
      ("Version 2.86, 256","Version 2.87, 258"),("current Version 2.86 candidate","current Version 2.87 candidate"),
      ("progress — Version 2.86","progress — Version 2.87"),("256 pages","258 pages"),
      ("2.73–2.86","2.73–2.87"),("through 2.86","through 2.87"),
      ("Version2.86 and full2.72 assessment","Version2.87 and full2.72 assessment"),(old_next,next_text)]
    for a,b in replacements: s=s.replace(a,b)
    if name.endswith("accounting-master-current.md"):
        s=s.replace("**P17-10: reserving adapter evidence and failure semantics.**",
                    "**P17-10/11: connected-insurance atomic commit and replay.**\n\n"+summary)
        s=s.replace("Eight pages of 2.86 received","Six pages of 2.87 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s=s.replace("## Latest completed work\n\n","## Latest completed work\n\n"+summary+"\n\n",1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s=s.replace("\nP17-09's bootstrap-consistency", "\n"+summary+"\n\nP17-09's bootstrap-consistency",1)
        s=s.replace("The immediate work is the P17-10 reserving-adapter audit,",
                    "The immediate work is the P17-10/11 insurance atomic-commit interaction,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s=s.replace("\n"+next_text,"\n"+summary+"\n\n"+next_text,1)
        s=s.replace("the P17-10 reserving-adapter audit is the immediate ready action",
                    "the P17-10/11 insurance atomic-commit interaction is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s=s.replace("integration follows the refreshed P17-10 reserving-adapter audit.",
                    "integration follows the audited P17-10/11 insurance atomic-commit interaction.\n\n"+summary)
    else:
        s=s.replace("1. "+next_text,"1. "+next_text+"\n   "+summary.replace("data/accounting-master/",""),1)
        s=s.replace("bootstrap consistency in 2.86.","bootstrap consistency in 2.86; reserving adapter in 2.87.")
    assert s!=p.read_text(),name
    p.write_text(s)
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
save(ARCHIVE/"refresh-manifest.json",{"before":before,"after":{n:sha(ROOT/n) for n in controls},
                                    "index_preserved":True,"next":next_text})
(ARCHIVE/"execution-note.md").write_text("# Control refresh15\n\n"+summary+"\n\n"+next_text+"\n")
matrix=ROOT/"data/accounting-master/p17-completion-20261014/P17-07/operation-matrix.md"
(OUT/"before").mkdir(exist_ok=True)
shutil.copy2(matrix,OUT/"before/insurance-operation-matrix.md")
t=matrix.read_text().replace("Current candidate 2.85","Current candidate 2.87")
t=t.replace("Mack-bootstrap consistency audit; target-specific validation protocol", "Version 2.86 specifies the conditional target, backward-law obligation and corrected reserve center; target-specific validation protocol")
t=t.replace("Group events/component distinction, unresolved inputs and failure behavior", "Group events/component distinction, unresolved inputs and failure behavior; Version 2.87 reserving-law, failed-draw and cancellation exchanges")
matrix.write_text(t)
paths=[p for p in OUT.rglob("*") if p.is_file() and p.name!="run-manifest.json"]
paths += [ROOT/"docs/plans/accounting-reserving-adapter-20261014.md",
          ROOT/"docs/plans/accounting-insurance-atomic-commit-20261014.md",
          ROOT/"docs/design/proposal/architecture/reserving-adapter-contract-20261014.md",
          ROOT/"docs/design/proposal/manuscript-reserving-adapter-20261014/accounting-product-proposal.pdf",matrix]
paths += [ROOT/n for n in controls]
build=json.loads((OUT/"build-run.json").read_text())
save(OUT/"run-manifest.json",{
 "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
 "recorded_utc":datetime.now(timezone.utc).isoformat(),
 "environment":"System Python Fraction/jsonschema; LuaLaTeX document helper; Poppler/PyMuPDF",
 "cpu_gpu_status":"CPU documentary checks; no numerical ML framework or GPU initialization",
 "random_seeds":"N/A: authored exact values; no RNG execution",
 "data_version":"Retained ChainLadder commit 5cd0dd441c3bb9e1ee6d7572d5bc1475f29be728; authored finite exchanges",
 "plan":"docs/plans/accounting-reserving-adapter-20261014.md",
 "result":str((OUT/"result.md").relative_to(ROOT)),
 "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["build_exchange.py","verify_exchange.py","prepare.py","verify_candidate.py","closeout.py"]],
 "build_record":build,"render_records":["final-render/render-manifest.json"],
 "exchange_verification":{k:v for k,v in json.loads((OUT/"exchange-checks.json").read_text()).items() if k != "checks"},
 "manuscript_verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
 "wall_time_note":"Individual build/check timings retained; total interactive authoring time not measured",
 "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.87","controls":6,"index_preserved":True,"next":"P17-10/11 insurance atomic commit"}))
