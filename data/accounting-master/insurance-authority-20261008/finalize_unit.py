"""Bind completed evidence and current pointers without changing historical records."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

import bs4
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


if (OUT / "completion.json").exists():
    raise SystemExit("Closed unit; preserve its outputs instead of regenerating.")
baseline = read(OUT / "baseline.json")
candidate = read(OUT / "candidate-checks.json")
authority = read(OUT / "authority-checks.json")
assert candidate["failed"] == authority["failed"] == 0
assert candidate["checker_sha256"] == sha(OUT / "check_candidate.py")
assert authority["checker_sha256"] == sha(OUT / "check_authority.py")
assert sha(ROOT / candidate["pdf"]["path"]) == candidate["pdf"]["sha256"]
review = read(OUT / "render-review.json")
assert review["author_review_sha256"] == sha(OUT / "author-review.md")

relocations = {r["historical_path"]: r["preserved_path"] for r in baseline["pointer_relocations"]}
previous = read(ROOT / "data/accounting-master/authority-literature-20261008/run-manifest.json")
assert all(sha(ROOT / relocations.get(n, n)) == h for n, h in previous["artifact_hashes"].items())
assert all(sha(ROOT / n) == h for n, h in baseline["protected_hashes"].items())
for key in ["protected_hashes", "upstream_reference_hashes", "controller_hashes"]:
    history = read(ROOT / "data/accounting-master/direct-p19-20261007/recovery-entry-v1.json")[key]
    assert all(sha(ROOT / n) == h for n, h in history.items())

pointer_checks = []
for row in baseline["pointer_relocations"]:
    assert sha(ROOT / row["preserved_path"]) == row["sha256"]
    p = ROOT / row["historical_path"]
    text = p.read_text()
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    bad = [s for s in links if not s.startswith(("http:", "https:", "#")) and not (p.parent / s.split("#")[0]).exists()]
    assert not bad, (str(p), bad)
    assert "Version 2.5" in text
    pointer_checks.append({"path": row["historical_path"], "sha256": sha(p), "links_checked": len(links), "bad_links": bad})
roadmap = (ROOT / "docs/plans/accounting-master-current.md").read_text()
gaps = re.findall(r"^\| (G\d+) —", roadmap, re.M)
assert len(gaps) == 18 and set(gaps) == {f"G{n}" for n in range(1, 19)}
save("closeout-checks.json", {"recorded_at": datetime.now(timezone.utc).isoformat(), "passed": True,
    "pointer_checks": pointer_checks, "gap_map": "All G1–G18 retained once",
    "previous_manifest_references": len(previous["artifact_hashes"]), "unit_baseline_files": len(baseline["protected_hashes"]),
    "historical_preservation_counts": candidate["preservation_counts"], "candidate_and_authority_hashes_current": True,
    "scope": "Final pointer/link/preservation check after documentation updates; earlier substantive checks remain unchanged"})

plan = ROOT / baseline["plan"]
artifacts = [p for p in OUT.rglob("*") if p.is_file() and p.name not in {"run-manifest.json", "completion.json"}]
artifacts += [p for p in (ROOT / baseline["candidate_directory"]).rglob("*") if p.is_file()]
artifacts += [ROOT / p for p in relocations] + [plan]
start = datetime.fromisoformat(baseline["recorded_at"])
end = datetime.now(timezone.utc)
receipts = read(OUT / "acquisition-receipts.json")
commands = [
    {"command": "python3 data/accounting-master/insurance-authority-20261008/extract_sources.py", "exit_code": 0},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-authority-20261008/check_authority.py", "exit_code": 0, "wall_seconds": authority["wall_seconds"]},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-authority-20261008/build_candidate.py", "exit_code": 0, "subsequent_edit": "Two explicit AASB attributions added after initial render review; final builder matches them"},
    {"command": "latexmk -lualatex -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex", "cwd": baseline["candidate_directory"], "execution": "trusted", "exit_code": 0, "runs": 2, "first_run": "Preserved under first-build; final run clarifies AASB source scope"},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-authority-20261008/assemble_evidence.py", "exit_code": 0, "runs": 2, "first_render": "Relocated beneath first-build; final render is separately bound"},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 /home/chakwong/.codex/skills/repair-scholarly-readability/scripts/scholarly_surface_audit.py docs/design/proposal/manuscript-insurance-20261008/sections/insurance-methods.tex --pdf docs/design/proposal/manuscript-insurance-20261008/accounting-product-proposal.pdf --output-json data/accounting-master/insurance-authority-20261008/surface-audit.json --output-md data/accounting-master/insurance-authority-20261008/surface-audit.md", "exit_code": 0},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-authority-20261008/check_candidate.py", "exit_code": 0, "wall_seconds": candidate["wall_seconds"]},
    {"command": "CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-authority-20261008/finalize_unit.py", "exit_code": 0},
]
manifest = {"recorded_at": end.isoformat(), "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "git_branch": baseline["branch"], "git_worktree": "Existing extensive dirty work preserved; hashes identify this unit; no Git mutation",
    "environment": {"python": sys.executable, "version": platform.python_version(), "conda_env": os.environ.get("CONDA_DEFAULT_ENV", "not set"),
                    "platform": platform.platform(), "beautifulsoup": bs4.__version__, "pymupdf": fitz.VersionBind,
                    "latex": "Existing LuaHBTeX/TeX Live; version in retained log; trusted font cache",
                    "cpu_gpu_status": "CPU document and rational-arithmetic tools only; no GPU detection or ML imports. CUDA_VISIBLE_DEVICES=-1 intentionally hides GPU devices for validation/build-helper commands."},
    "random_seeds": "N/A: deterministic authored arithmetic and document operations",
    "data_version": {"ASBE25_raw_sha256": authority["source_sha256"], "AASB17": "Retained December 2022 compilation; hash in baseline", "baseline": "Version 2.4; protected by baseline.json"},
    "plan": baseline["plan"], "audit": "Pre-execution skeptical/default/evidence audit recorded in the plan",
    "result": "data/accounting-master/insurance-authority-20261008/result.md", "commands": commands,
    "acquisition_receipts": "data/accounting-master/insurance-authority-20261008/acquisition-receipts.json",
    "wall_time": {"started_at": start.isoformat(), "completed_at": end.isoformat(), "elapsed_seconds": (end - start).total_seconds(),
                  "scope": "Elapsed from unit initialization through closeout; includes research, approvals, document work and review",
                  "curl_transfer_seconds": sum(r["transfer_seconds"] or 0 for r in receipts["requests"]), "per_build_seconds": "Not separately instrumented"},
    "artifact_hashes": {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(artifacts))},
    "preservation": {"baseline_files": len(baseline["protected_hashes"]), "previous_unit_manifest_references": len(previous["artifact_hashes"]),
                     "historical_counts": candidate["preservation_counts"], "pointers": baseline["pointer_relocations"]},
    "first_build_relocation": "first-build/render-manifest.json paths formerly under render-final now resolve beneath first-build/; current final render uses root render-manifest.json",
    "readiness": "not_ready", "independent_reader": "pending", "human_acceptance": "pending",
    "scope": "Dated source comparison and deterministic conditional example; no real-entity adoption, calibration, full amendment review, product implementation or stochastic ranking"}
save("run-manifest.json", manifest)
save("completion.json", {"recorded_at": end.isoformat(), "status": "bounded_unit_complete_with_applicability_gaps",
    "full_proposal_readiness": "not_ready", "authority_checks": {"passed": authority["passed"], "failed": authority["failed"]},
    "candidate_checks": {"passed": candidate["passed"], "failed": candidate["failed"]}, "pdf": candidate["pdf"],
    "run_manifest_sha256": sha(OUT / "run-manifest.json"), "open_workstreams": ["E01", "E05", "E07", "E08", "E14"],
    "next": "E07 insurance adoption/implementation via separately identified official Q&A; independent E01 work if blocked; see current next-plan.md"})
print(json.dumps({"status": "bounded_unit_complete_with_applicability_gaps", "pages": candidate["pdf"]["pages"], "pdf_sha256": candidate["pdf"]["sha256"],
                  "artifact_count": len(manifest["artifact_hashes"]), "elapsed_seconds": manifest["wall_time"]["elapsed_seconds"]}))
