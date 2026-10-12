"""Create Version 2.51 with a bounded real ASBE lease example."""
import datetime
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = ROOT / "docs/design/proposal/manuscript-munich-transition-20261012"
CAND = ROOT / "docs/design/proposal/manuscript-pingan-leases-20261013"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def expected_text(rel):
    text = (BASE / rel).read_text()
    if rel == "accounting-product-proposal.tex":
        assert text.count("Version 2.50 (proposal candidate)") == 1
        text = text.replace("Version 2.50 (proposal candidate)", "Version 2.51 (proposal candidate)")
        text = text.replace("12 October 2026", "13 October 2026")
    elif rel == "sections/standards-methods.tex":
        anchor = "\\hypertarget{matched-case-outcomes-and-decision}"
        assert text.count(anchor) == 1
        text = text.replace(anchor, (OUT / "lease-addition.tex").read_text() + "\n" + anchor, 1)
    elif rel == "references.bib":
        text += (OUT / "references-addition.bib").read_text()
    return text


def main():
    assert not CAND.exists() and not (OUT / "completion.json").exists()
    source = json.loads((OUT / "source-checks.json").read_text())
    assert source["passed"] == 51 and not source["failed"]
    baseline_digest = "b9171185897b808f35ac08dc4a75892ce24fb8948ef0fa83070aa7e8993c788c"
    assert sha(BASE / "accounting-product-proposal.pdf") == baseline_digest
    inputs = sorted(p for p in BASE.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".lark"})
    hashes = {str(p.relative_to(BASE)): sha(p) for p in inputs}
    for rel in hashes:
        dest = CAND / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(expected_text(rel))
    save("candidate.json", {"baseline": str(BASE.relative_to(ROOT)), "baseline_pdf_sha256": baseline_digest,
                            "source_hashes": hashes, "candidate": str(CAND.relative_to(ROOT)),
                            "new_passage_sha256": sha(OUT / "lease-addition.tex"),
                            "new_reference_sha256": sha(OUT / "references-addition.bib"),
                            "scope": "One real lease-transition section, one reference, version/date; prior source content preserved",
                            "readiness": "not_ready"})
    command = ["latexmk", "-g", "-lualatex", "-interaction=nonstopmode", "-halt-on-error", "accounting-product-proposal.tex"]
    overrides = {"TEXMFVAR": "/tmp/accdsl-texmfvar", "TEXMFCACHE": "/tmp/accdsl-texmfvar", "CUDA_VISIBLE_DEVICES": "-1"}
    env = os.environ.copy()
    env.update(overrides)
    start = time.monotonic()
    with (OUT / "build-stdout.log").open("w") as log:
        result = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {"command": command, "cwd": str(CAND.relative_to(ROOT)), "environment_overrides": overrides,
              "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "wall_seconds": time.monotonic()-start, "exit_code": result.returncode}
    save("build-run.json", record)
    print(json.dumps(record))
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
