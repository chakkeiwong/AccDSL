"""Close a bounded proposal unit without rewriting earlier evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys

import bs4
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
if (OUT/"completion.json").exists():
    raise SystemExit("Closed unit; preserve it")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
baseline=read(OUT/"baseline.json")
candidate=read(OUT/"candidate-checks.json")
evidence=read(OUT/"evidence-checks.json")
assert candidate["failed"]==evidence["failed"]==0
assert candidate["checker_sha256"]==sha(OUT/"check_candidate.py")
assert evidence["checker_sha256"]==sha(OUT/"prepare_evidence.py")
assert sha(ROOT/candidate["pdf"]["path"])==candidate["pdf"]["sha256"]
for hashes in [candidate["inputs"],evidence["inputs"],evidence["output_hashes"],baseline["protected_hashes"]]:
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
relocations={r["historical_path"]:r["preserved_path"] for r in baseline["pointer_relocations"]}
previous=read(ROOT/baseline["prior_manifest"])
assert all(sha(ROOT/relocations.get(n,n))==h for n,h in previous["artifact_hashes"].items())
history=read(ROOT/"data/accounting-master/direct-p19-20261007/recovery-entry-v1.json")
for k in ["protected_hashes","upstream_reference_hashes","controller_hashes"]:
    assert all(sha(ROOT/n)==h for n,h in history[k].items())
first_relocations=read(OUT/"first-build/relocations.json")
first_render=read(OUT/"first-build/render-manifest.json")
assert all(sha(ROOT/first_relocations[r["path"]])==r["sha256"] for r in first_render["rendered_pages"].values())
assert first_render["pdf_sha256_before"]==sha(OUT/"first-build/candidate/accounting-product-proposal.pdf")
first_build=read(OUT/"first-build/build-receipt.json")
assert first_build["log_sha256"]==sha(OUT/"first-build/build.log")
review=read(OUT/"render-review.json")
assert review["author_review_sha256"]==sha(OUT/"author-review.md")
assert review["render_manifest_sha256"]==sha(OUT/"render-manifest.json")
pointer_checks=[]
for row in baseline["pointer_relocations"]:
    assert sha(ROOT/row["preserved_path"])==row["sha256"]
    p=ROOT/row["historical_path"];t=p.read_text()
    assert "Version 2.6" in t and "E01" in t
    links=re.findall(r"\[[^\]]+\]\(([^)]+)\)",t)
    bad=[s for s in links if not s.startswith(("http:","https:","#")) and not (p.parent/s.split("#")[0]).exists()]
    assert not bad,(p,bad)
    pointer_checks.append(dict(path=row["historical_path"],sha256=sha(p),links_checked=len(links),broken_links=bad))
roadmap=(ROOT/"docs/plans/accounting-master-current.md").read_text()
gaps=re.findall(r"^\| (G\d+) —",roadmap,re.M)
assert len(gaps)==18 and set(gaps)=={f"G{n}" for n in range(1,19)}
assert "136 unverified publication dates" in roadmap
actual=read(OUT/"actual-curl-commands.json")
assert len(actual)==2 and all(r["execution"]=="require_escalated" for r in actual)
save("closeout-checks.json",dict(recorded_at=datetime.now(timezone.utc).isoformat(),passed=True,pointer_checks=pointer_checks,
     gap_map="All G1–G18 retained once",previous_manifest_references=len(previous["artifact_hashes"]),baseline_files=len(baseline["protected_hashes"]),
     historical_preservation_counts=candidate["preservation_counts"],first_build_verified_through_relocations=True,
     source_and_candidate_outputs_current=True,full_readiness="not_ready"))

now=datetime.now(timezone.utc)
start=datetime.fromisoformat(baseline["recorded_at"])
new=ROOT/"docs/design/proposal/manuscript-adoption-20261008"
artifacts={str(p.relative_to(ROOT)):sha(p) for base in [OUT,new] for p in base.rglob("*") if p.is_file() and p.name not in {"run-manifest.json","completion.json"}}
plan=ROOT/"docs/plans/accounting-insurance-adoption-20261008.md"
artifacts[str(plan.relative_to(ROOT))]=sha(plan)
for row in pointer_checks:
    artifacts[row["path"]]=row["sha256"]
commands=[
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-adoption-20261008/prepare_evidence.py",exit_code=0,runs=2,reason_for_second="Bind generated source/bridge outputs in evidence check record"),
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-adoption-20261008/build_candidate.py",exit_code=0,subsequent_edit="Split new timetable sentence and insert local clearpage before Section 12.8; final builder updated to match, not rerun into existing directory"),
    dict(command="latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex > /home/chakwong/python/AccDSL/data/accounting-master/insurance-adoption-20261008/build.log 2>&1",cwd=str(new),execution="trusted",exit_code=0,runs=2),
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-adoption-20261008/render_candidate.py",exit_code=0,runs=2,first_output="Preserved in first-build with relocations"),
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-adoption-20261008/sections/insurance-methods.tex --pdf docs/design/proposal/manuscript-adoption-20261008/accounting-product-proposal.pdf --output-json data/accounting-master/insurance-adoption-20261008/surface-audit.json --output-md data/accounting-master/insurance-adoption-20261008/surface-audit.md",exit_code=0,runs=2),
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-adoption-20261008/check_candidate.py",exit_code=0,wall_seconds=candidate["wall_seconds"],initial_exit_code=1,initial_disposition="Checker PDF-comma spacing and late-bound summary regex repaired; failed checker/output retained"),
    dict(command="CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-adoption-20261008/finalize_unit.py",exit_code=0),
]
manifest=dict(recorded_at=now.isoformat(),git_commit=baseline["git_commit"],git_branch="main",
     git_worktree="Extensive pre-existing dirty state; artifact hashes supplement commit; no Git mutation",
     environment=dict(python=sys.executable,version=platform.python_version(),conda_env=os.environ.get("CONDA_DEFAULT_ENV"),platform=platform.platform(),
                      beautifulsoup=bs4.__version__,pymupdf=fitz.VersionBind,latex="Existing LuaHBTeX; exact engine in retained log; trusted font cache",
                      cpu_gpu_status="CPU document tools only. No GPU detection or ML imports; CUDA_VISIBLE_DEVICES=-1 intentionally hides devices in validation/helper commands."),
     random_seeds="N/A: deterministic documentary/arithmetic work",data_version=evidence["inputs"],
     plan=str(plan.relative_to(ROOT)),audit="Skeptical/default/evidence audit in plan before acquisition or manuscript generation",
     result=str((OUT/"result.md").relative_to(ROOT)),commands=commands,actual_network_commands=actual,
     acquisition_receipts=str((OUT/"acquisition-receipts.json").relative_to(ROOT)),
     auxiliary_operations="Python stdlib/PyMuPDF extraction and source renders; Pillow contact sheets; apply_patch prose/control edits. Source-render files beyond the specified inspected pages are not claimed as read.",
     wall_time=dict(started_at=start.isoformat(),finished_at=now.isoformat(),elapsed_seconds=(now-start).total_seconds(),basis="From baseline preservation to closeout; includes source inspection, approvals, builds and review; not a performance measurement"),
     artifact_hashes=artifacts,preservation=dict(baseline_files=len(baseline["protected_hashes"]),previous_manifest_references=len(previous["artifact_hashes"]),
                      historical_counts=candidate["preservation_counts"],pointers=baseline["pointer_relocations"]),
     first_build_relocations=str((OUT/"first-build/relocations.json").relative_to(ROOT)),
     readiness="not_ready",independent_reader="pending",human_acceptance="pending",
     scope="Official-explanation/issuer-source comparison and original/restated query design; no operative-notice completion, historical-availability repair, runtime, stochastic ranking or publication")
save("run-manifest.json",manifest)
assert all(sha(ROOT/n)==h for n,h in artifacts.items())
save("completion.json",dict(recorded_at=now.isoformat(),status="bounded_unit_complete_with_operative_gaps",manifest_sha256=sha(OUT/"run-manifest.json"),
     pdf=candidate["pdf"],source_checks=evidence["passed"],candidate_checks=candidate["passed"],artifacts_verified=len(artifacts),
     readiness="not_ready",next_work="E01/C03: Apple revenue/deferred-revenue material narrative and query preparation from A04/A05/I03"))
print(json.dumps(dict(status="bounded_unit_complete_with_operative_gaps",artifacts_verified=len(artifacts),source_checks=evidence["passed"],candidate_checks=candidate["passed"],pdf=candidate["pdf"])))
