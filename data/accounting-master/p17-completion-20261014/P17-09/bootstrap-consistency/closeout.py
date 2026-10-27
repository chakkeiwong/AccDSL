"""Refresh live controls after checked 2.86; preserve frozen assessments."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
ARCHIVE=ROOT/"data/accounting-master/p17-completion-20261014/control-refresh-14"
controls=["docs/plans/accounting-master-current.md","docs/plans/accounting-master-checkpoint.md",
          "docs/plans/accounting-continuation-requirements-20261007.md",
          "docs/plans/accounting-p17-completion-20261014.md",
          "docs/plans/accounting-p18-completion-20261014.md","data/accounting-master/next-plan.md"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2)+"\n")
assert not ARCHIVE.exists()
assert json.loads((OUT/"manuscript-checks.json").read_text())["passed"]
assert json.loads((OUT/"ledger-checks.json").read_text())["passed"]
summary=("P17-09's bootstrap-consistency audit is integrated in Version 2.86: "
         "53 exact and 86 preservation/build checks pass; eight rendered pages were inspected. "
         "The final published source, conditioning target, backward-law obligation and corrected reserve center "
         "are explicit. All six literature ledgers preserve historical records. "
         "Result: data/accounting-master/p17-completion-20261014/P17-09/bootstrap-consistency/result.md. "
         "P17/E07/E08 remain open.")
old_next=("Next: audit the retained Steinmetz/Jentsch arXiv2303.05913v1 (10 March2023; published2024 record) for bootstrap consistency. "
          "Refresh the exact target, assumptions, comparator, theorem/proof dependencies and available author code before importing any validity or failure conclusion. No stochastic campaign starts.")
next_text=("Next: execute the refreshed P17-10 reserving-adapter plan "
           "(docs/plans/accounting-reserving-adapter-20261014.md). Bind the inspected native law and zero-coercion behavior "
           "to exact proposed exchanges, partial/cancelled-result semantics and provenance requirements. "
           "No R execution, installation or stochastic campaign starts.")
before={}
for name in controls:
    p=ROOT/name
    q=ARCHIVE/"before"/name
    q.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,q)
    before[name]=sha(p)
    s=p.read_text()
    replacements=[
      ("manuscript-reserving-bootstrap-20261014/accounting-product-proposal.pdf","manuscript-bootstrap-consistency-20261014/accounting-product-proposal.pdf"),
      ("fa2d2a38f0c9ea2d420f7b346ff8f5496d0d9680b6aa8d89322ef05db82a5638","0ce798be2097f362b76935d46fe185878a362a4d18e317caac3b296dfa751303"),
      ("Version **2.85**","Version **2.86**"),("**Version 2.85,","**Version 2.86,"),
      ("Version 2.85, 254","Version 2.86, 256"),("current Version 2.85 candidate","current Version 2.86 candidate"),
      ("progress — Version 2.85","progress — Version 2.86"),("254 pages","256 pages"),
      ("2.73–2.85","2.73–2.86"),("through 2.85","through 2.86"),
      ("Version2.85 and full2.72 assessment","Version2.86 and full2.72 assessment"),
      (old_next,next_text)]
    for a,b in replacements: s=s.replace(a,b)
    if name.endswith("accounting-master-current.md"):
        s=s.replace("**P17-09: bootstrap-consistency follow-up.**",
                    "**P17-10: reserving adapter evidence and failure semantics.**\n\n"+summary)
        s=s.replace("Seven pages of 2.85 received","Eight pages of 2.86 received")
    elif name.endswith("accounting-master-checkpoint.md"):
        s=s.replace("## Latest completed work\n\n","## Latest completed work\n\n"+summary+"\n\n",1)
    elif name.endswith("accounting-continuation-requirements-20261007.md"):
        s=s.replace("\nP17-09 reserving uncertainty", "\n"+summary+"\n\nP17-09 reserving uncertainty",1)
        s=s.replace("The immediate work is the P17-09 bootstrap-consistency audit,",
                    "The immediate work is the P17-10 reserving-adapter audit,")
    elif name.endswith("accounting-p17-completion-20261014.md"):
        s=s.replace("\n"+next_text,"\n"+summary+"\n\n"+next_text,1)
        s=s.replace("the P17-09 consistency audit is the immediate ready action",
                    "the P17-10 reserving-adapter audit is the immediate ready action")
    elif name.endswith("accounting-p18-completion-20261014.md"):
        s=s.replace("integration follows the refreshed P17-09 consistency audit.",
                    "integration follows the refreshed P17-10 reserving-adapter audit.\n\n"+summary)
    else:
        s=s.replace("1. "+next_text,"1. "+next_text+"\n   "+summary.replace("data/accounting-master/",""),1)
        s=s.replace("reserving uncertainty in 2.85.","reserving uncertainty in 2.85; bootstrap consistency in 2.86.")
    assert s!=p.read_text(),name
    p.write_text(s)
index=subprocess.check_output(["git","diff","--cached","--raw","--no-abbrev"],cwd=ROOT)
assert index==(ROOT/"data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt").read_bytes()
save(ARCHIVE/"refresh-manifest.json",{"before":before,"after":{n:sha(ROOT/n) for n in controls},
                                    "index_preserved":True,"next":next_text})
(ARCHIVE/"execution-note.md").write_text("# Control refresh14\n\n"+summary+"\n\n"+next_text+"\n")
paths=[p for p in OUT.rglob("*") if p.is_file() and p.name!="run-manifest.json"]
paths += [ROOT/"docs/plans/accounting-bootstrap-consistency-20261014.md",
          ROOT/"docs/design/proposal/methods/bootstrap-consistency-20261014.md",
          ROOT/"docs/design/proposal/manuscript-bootstrap-consistency-20261014/accounting-product-proposal.pdf"]
paths += [ROOT/n for n in controls]
build=json.loads((OUT/"build-run.json").read_text())
save(OUT/"run-manifest.json",{
 "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
 "recorded_utc":datetime.now(timezone.utc).isoformat(),
 "environment":"System Python Fraction; LuaLaTeX document helper; Poppler/PyMuPDF; curl metadata/full-text retrieval",
 "cpu_gpu_status":"CPU documentary checks; no ML/GPU initialization",
 "random_seeds":"N/A: exact finite laws; no stochastic experiment",
 "data_version":"Final2024 journal, preserved2023 preprint and related2023 dissertation; authored finite laws",
 "plan":"docs/plans/accounting-bootstrap-consistency-20261014.md",
 "result":str((OUT/"result.md").relative_to(ROOT)),
 "commands":["python3 "+str((OUT/f).relative_to(ROOT)) for f in ["check_cases.py","prepare.py","update_ledgers.py","verify_candidate.py","closeout.py"]],
 "build_record":build,
 "render_records":["final-render/render-manifest.json","bibliography-render/render-manifest.json"],
 "calculation_seconds":json.loads((OUT/"calculation-checks.json").read_text())["wall_seconds"],
 "verification_seconds":json.loads((OUT/"manuscript-checks.json").read_text())["wall_seconds"],
 "source_retrievals":["https://hdl.handle.net/2003/44429","https://hdl.handle.net/2003/41966",
   "https://api.crossref.org/works/10.1016/j.insmatheco.2024.01.001",
   "https://api.openalex.org/works?filter=cites:W4391074055&sort=cited_by_count:desc&per-page=25"],
 "wall_time_note":"Individual build/check timings retained; total interactive source-reading time not measured",
 "artifacts":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sorted(set(paths))]})
print(json.dumps({"version":"2.86","controls":6,"index_preserved":True,"next":"P17-10 reserving adapter"}))
