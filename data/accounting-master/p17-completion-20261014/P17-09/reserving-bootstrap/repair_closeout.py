"""Finish the documented 2.85 closeout without changing manuscript bytes."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

review_path = OUT / "render-review.json"
review = json.loads(review_path.read_text())
review["physical_pages"] = [1, 182, 183, 184, 185, 247, 248]
review["supplemental_review"] = {
    "manifest": "bibliography-render/render-manifest.json",
    "physical_page": 247,
    "finding": "Bibliographic entries inspected; version distinctions and layout remain legible.",
    "provenance": "Completed visual inspection recorded in preceding session handoff."
}
dump(review_path, review)
matrix = OUT.parents[1] / "P17-07/operation-matrix.md"
saved = OUT / "before/insurance-operation-matrix.md"
if not saved.exists():
    saved.write_bytes(matrix.read_bytes())
text = matrix.read_text().replace("Current candidate 2.83", "Current candidate 2.85")
text = text.replace(
    "| Actuarial estimation | Mack point formula and unresolved variance, RA interface/assumptions | Target-specific validation/uncertainty protocols, justified competing methods and downstream measurement inputs |",
    "| Actuarial estimation | Version 2.85: two-stage uncertainty, exact process-law identity, shared-fit dependence, sparse-data refusal and one-year re-estimation; 46 exact checks | Mack-bootstrap consistency audit; target-specific validation protocol, justified competing methods and downstream measurement inputs remain |")
matrix.write_text(text)
subprocess.run(["python3", str(OUT / "verify_candidate.py")], cwd=ROOT, check=True)
manifest_path = OUT / "run-manifest.json"
manifest = json.loads(manifest_path.read_text())
manifest["closeout_repaired_utc"] = datetime.now(timezone.utc).isoformat()
command = "python3 " + str((OUT / "repair_closeout.py").relative_to(ROOT))
if command not in manifest["commands"]:
    manifest["commands"].append(command)
paths = {ROOT / record["path"] for record in manifest["artifacts"]}
paths.update([saved, matrix, Path(__file__).resolve()])
manifest["artifacts"] = [
    {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    for path in sorted(paths) if path != manifest_path
]
dump(manifest_path, manifest)
print(json.dumps({"review_pages": review["physical_pages"], "artifact_hashes": len(manifest["artifacts"]), "matrix": str(matrix.relative_to(ROOT))}))
