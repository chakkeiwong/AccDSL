"""Snapshot review inputs, then verify against snapshots after live edits."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PACKET = ROOT / "data/accounting-master/review-packet-ordered-eps-20261016"
CONTROLS = {"docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md", "data/accounting-master/next-plan.md"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def assemble():
    started = time.monotonic()
    if PACKET.exists():
        raise SystemExit("Immutable successor already exists; create another version rather than overwrite")
    original = json.loads((ROOT / "data/accounting-master/review-packet-20261016/packet.json").read_text())
    manuscript = json.loads((OUT / "manuscript-checks.json").read_text())
    chosen = {ROOT / entry["path"] for entry in original["evidence_files"]}
    chosen.update(ROOT / name for name in (
        "MISSION_CONTROL.md", "docs/plans/accounting-continuation-integrity-and-eps-20261016.md",
        "docs/plans/accounting-company-eps-join-20261016.md",
        "data/accounting-master/r03-residual-route-20261016/route.md",
        "data/accounting-master/r03-residual-route-20261016/route.json",
        "data/accounting-master/r03-residual-route-20261016/run-manifest.json",
        "data/accounting-master/r07-whole-candidate-20261016/scan.json",
        "data/accounting-master/r07-whole-candidate-20261016/run-manifest.json",
        "data/accounting-master/r08-assessment-20261016/first-slice.md",
        "data/accounting-master/r08-assessment-20261016/run-manifest.json",
        "data/accounting-master/candidate-reconciliation-20261016/candidate-delta.json",
        "data/accounting-master/candidate-reconciliation-20261016/run-manifest.json",
        "docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt"))
    # The exact new calculator, pre-authored inputs, retained attempts, source
    # lock and decisions are review inputs. Avoid duplicate historical copies.
    excluded = {"snapshots", "baseline-sources", "manuscript-attempt-01", "manuscript-attempt-02", "__pycache__"}
    for p in OUT.rglob("*"):
        rel = p.relative_to(OUT)
        if p.is_file() and not any(part in excluded or part.startswith("render-attempt-") for part in rel.parts) and p.suffix in {".md", ".json", ".py", ".tex", ".log"}:
            chosen.add(p)
    # Bind only the final images separately; old images remain retained outside
    # this packet and are identified by the preserved attempt manifests.
    for item in json.loads((OUT / "render-manifest.json").read_text())["pages"]:
        chosen.add(ROOT / item["path"])
    candidate_dir = (ROOT / manuscript["candidate_pdf"]).parent
    chosen.update(p for p in candidate_dir.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".lark", ".pdf", ".log"})
    for directory in ROOT.glob("data/accounting-master/r03-*-residual-audit-20261016"):
        chosen.update(p for p in directory.glob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"})
    for directory_name in ("company-composition-20261016", "extended-method-exchanges-20261015/corporate-residuals",
                           "extended-method-exchanges-20261015/financing-v2"):
        directory = ROOT / "data/accounting-master" / directory_name
        chosen.update(p for p in directory.glob("*") if p.is_file() and p.name in {
            "result.md", "run-manifest.json", "semantic-contract.md", "source-reading.md"})
    for filename in ("backward-snowball.json", "citation-venue.json", "claim-support.json",
                     "forward-snowball.json", "omissions.json", "source-support.json"):
        chosen.add(ROOT / "data/accounting-master/candidate-reconciliation-20261016/six-ledgers-before" / filename)
    missing = [str(p.relative_to(ROOT)) for p in chosen if not p.is_file()]
    if missing:
        raise SystemExit("Missing required review inputs: " + repr(missing))
    PACKET.mkdir()
    entries = []
    for source in sorted(chosen):
        origin = str(source.relative_to(ROOT))
        snapshot = PACKET / "inputs" / origin
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, snapshot)
        assert sha(snapshot) == sha(source)
        entries.append(dict(origin_path=origin, snapshot_path=str(snapshot.relative_to(ROOT)),
            sha256=sha(snapshot), bytes=snapshot.stat().st_size,
            role="frozen_live_control" if origin in CONTROLS else "fixed_review_input"))
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), candidate_version="3.15",
        candidate_origin=manuscript["candidate_pdf"],
        candidate_pdf=str((PACKET / "inputs" / manuscript["candidate_pdf"]).relative_to(ROOT)),
        candidate_pdf_sha256=manuscript["pdf_sha256"], predecessor="data/accounting-master/review-packet-20261016/packet.json",
        predecessor_sha256=sha(ROOT / "data/accounting-master/review-packet-20261016/packet.json"),
        question="Check the exact 3.15 proposal, ordered EPS target and scoped residuals using fixed inputs; classify each unresolved claim.",
        review_questions=[
            "Check the signed continuing-operation selection, strict neutrality, independent-additive proof and total-earnings population.",
            "Check completeness, unsupported rights, context/time weighting, evidence resolution and non-mutation boundaries.",
            "Check all five original financing promises and P5/sector residuals remain visible; no whole-row closure from finite checks.",
            "Check inherited P5/P2, R03 route, R04 claims, R06 dependency/terms limits and R07/R08 evidence with the current delta.",
            "Check equations/source preservation and new narrative/reference pages; human comprehension remains separate.",
            "Distinguish candidate failure, missing application evidence and project-direction rejection."],
        evidence_files=entries, status="prepared_for_independent_review", independent_review="pending",
        human_domain_acceptance="pending", mission_readiness="not_ready",
        scope="Every enumerated input is snapshotted. This is not a transitive archive of the entire repository or every cited source.",
        resolver="Resolve each origin_path to its snapshot_path. Mutations to live controls do not alter these review bytes.",
        nonclaims=["runtime conformance", "current-law compliance", "full mission readiness", "human acceptance", "empirical validation"])
    write(PACKET / "packet.json", record)
    write(PACKET / "run-manifest.json", dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command="python3 data/accounting-master/continuation-integrity-eps-20261016/assemble_packet.py assemble",
        environment="system Python; filesystem hashing/copy only; no GPU or network", random_seeds="N/A: deterministic file binding",
        data_version="Version3.15 and enumerated historical/successor evidence", wall_seconds=round(time.monotonic()-started, 3),
        plan="docs/plans/accounting-continuation-integrity-and-eps-20261016.md",
        result="data/accounting-master/continuation-integrity-eps-20261016/result.md",
        packet_sha256=sha(PACKET / "packet.json"), input_count=len(entries),
        output=str((PACKET / "packet.json").relative_to(ROOT))))
    print(json.dumps(dict(snapshot_inputs=len(entries), packet_sha256=sha(PACKET / "packet.json"))))


def verify(tag):
    packet_path = PACKET / "packet.json"
    packet = json.loads(packet_path.read_text())
    manifest = json.loads((PACKET / "run-manifest.json").read_text())
    checks = [dict(name="packet-manifest-binding", passed=sha(packet_path) == manifest["packet_sha256"])]
    origin_differences = []
    for entry in packet["evidence_files"]:
        snapshot = ROOT / entry["snapshot_path"]
        checks.append(dict(name=entry["snapshot_path"], passed=snapshot.is_file() and sha(snapshot) == entry["sha256"]))
        origin = ROOT / entry["origin_path"]
        if not origin.is_file() or sha(origin) != entry["sha256"]:
            origin_differences.append(entry["origin_path"])
    checks.append(dict(name="candidate-pdf-binding", passed=sha(ROOT / packet["candidate_pdf"]) == packet["candidate_pdf_sha256"]))
    preserved = json.loads((OUT / "preservation-manifest.json").read_text())
    for entry in preserved["snapshots"]:
        path = OUT / "snapshots" / entry["path"]
        checks.append(dict(name="predecessor-snapshot/" + entry["path"], passed=sha(path) == entry["sha256"]))
        if entry["path"] not in CONTROLS:
            checks.append(dict(name="immutable-origin/" + entry["path"], passed=sha(ROOT / entry["path"]) == entry["sha256"]))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    index = subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT)
    checks.append(dict(name="git-head", passed=head == preserved["head"]))
    checks.append(dict(name="git-index", passed=hashlib.sha256(index).hexdigest() == preserved["cached_raw_sha256"]))
    if tag == "after-controls":
        checks.append(dict(name="actual-live-control-change-tested", passed="docs/plans/accounting-master-checkpoint.md" in origin_differences))
        checks.append(dict(name="no-unexpected-origin-change", passed=set(origin_differences) <= CONTROLS))
    result = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), packet_sha256=sha(packet_path),
        snapshot_inputs=len(packet["evidence_files"]), checks=len(checks), failures=sum(not c["passed"] for c in checks),
        live_origin_differences=origin_differences, detail=checks, scope="exact listed snapshots and preserved inputs; no independent content acceptance")
    target = OUT / ("packet-verification-" + tag + ".json")
    if target.exists():
        raise SystemExit("Verification record exists; do not silently replace")
    write(target, result)
    print(json.dumps({k: result[k] for k in ("snapshot_inputs", "checks", "failures", "live_origin_differences")}))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    if sys.argv[1] == "assemble":
        assemble()
    else:
        verify(sys.argv[1])
