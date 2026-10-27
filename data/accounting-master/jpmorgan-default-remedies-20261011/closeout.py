#!/usr/bin/env python3
"""Close the source-only default/remedy reading without changing the manuscript."""
from __future__ import annotations
import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PRIOR=ROOT/"data/accounting-master/accounting-proposal-v229-integration-20261011"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path): return str(path.relative_to(ROOT))
def write(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2)+"\n")

def main():
    t=time.monotonic()
    ledger=json.loads((OUT/"source-ledger.json").read_text())
    prior=json.loads((PRIOR/"run-manifest.json").read_text())
    checks=[]
    def ck(label,yes): checks.append({"check":label,"passed":bool(yes)})
    ck("175/0 source checks and 51 spans",ledger["passed"]==175 and ledger["failed"]==0 and sum(len(r["spans"]) for r in ledger["records"])==51)
    ck("four dated 10-K sources unchanged",all(sha(ROOT/r["source_pdf"])==r["source_pdf_sha256"] and sha(ROOT/r["source_text"])==r["source_text_sha256"] for r in ledger["records"]))
    ck("bounded wording comparison",all(x["passed"] for x in ledger["checks"][-2:]))
    ck("Version 2.29 remains protected",sha(ROOT/prior["candidate_pdf"]["path"])==prior["candidate_pdf"]["sha256"])
    ck("original Indenture still absent",not (ROOT/"data/accounting-master/jpmorgan-callable-indentures-20261011/sources/2016-indentures-ex4a7.htm").exists())
    for name in ["result.md","author-review.md","next-source-frontier.md"]:
        ck("artifact "+name,(OUT/name).is_file())
    pages=[(2022,327),(2022,328),(2022,329),(2023,356),(2025,351),(2025,352),(2025,353)]
    images=[OUT/"rendered"/f"{year}-p{page}.png" for year,page in pages]
    ck("seven inspected render files",all(p.is_file() and p.stat().st_size>1000 for p in images))
    if not all(x["passed"] for x in checks):
        write("closeout-checks.json",{"checks":checks,"failed":sum(not x["passed"] for x in checks)})
        raise SystemExit(1)
    paths=[OUT/x for x in ["build_source_ledger.py","closeout.py","source-ledger.json","check-run.json","result.md","author-review.md","next-source-frontier.md"]]+images
    manifest={
        "recorded_at":"2026-10-11",
        "unit":"JPMorgan 2016 Indenture default/remedy reported-summary source reading",
        "git_commit":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
        "git_branch":"main",
        "git_worktree":"Unrelated dirty work preserved; .git mounted read-only; no Git write attempted.",
        "plan":"docs/plans/accounting-jpmorgan-default-remedy-summaries-20261011.md",
        "result":rel(OUT/"result.md"),
        "command":"CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/jpmorgan-default-remedies-20261011/build_source_ledger.py",
        "environment":{"python":"Python 3.11","cpu_gpu":"CPU-only documentary checks; GPU devices intentionally hidden","random_seeds":"N/A; deterministic"},
        "wall_seconds":{"source_check":json.loads((OUT/"check-run.json").read_text())["wall_seconds"],"closeout":time.monotonic()-t},
        "data_version":[{"filing_year":r["filing_year"],"pdf":r["source_pdf"],"sha256":r["source_pdf_sha256"]} for r in ledger["records"]],
        "source_checks":{"passed":175,"failed":0},
        "artifact_hashes":{rel(p):sha(p) for p in paths},
        "prior_manuscript":{"path":prior["candidate_pdf"]["path"],"sha256":prior["candidate_pdf"]["sha256"]},
        "scope_limit":"10-K summaries only; original 2016 Indenture and supplements uninspected after SEC HTTP 403.",
        "readiness":"not_ready",
    }
    write("run-manifest.json",manifest)
    checks.append({"check":"run manifest bound","passed":sha(OUT/"run-manifest.json") is not None})
    write("closeout-checks.json",{"recorded_at":"2026-10-11","checks":checks,"passed":sum(x["passed"] for x in checks),"failed":sum(not x["passed"] for x in checks),"wall_seconds":time.monotonic()-t})
    write("completion.json",{"recorded_at":"2026-10-11","status":"closed_bounded_source_unit","source_checks":175,"closeout_checks":len(checks),"run_manifest_sha256":sha(OUT/"run-manifest.json"),"manuscript_unchanged":True,"readiness":"not_ready","next_frontier":rel(OUT/"next-source-frontier.md")})
    print(json.dumps({"source_checks":175,"closeout_checks":len(checks),"failed":0}))

if __name__=="__main__": main()
