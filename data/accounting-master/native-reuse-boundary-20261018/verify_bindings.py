"""Check this static source inquiry without importing upstream package code."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    started = time.monotonic()
    manifest = json.loads((OUT / "source-manifest.json").read_text())
    checks = []

    def check(label, condition):
        checks.append({"check": label, "passed": bool(condition)})

    for row in manifest["files"]:
        p = ROOT / row["path"]
        check("file: " + row["path"], p.is_file() and digest(p.read_bytes()) == row["sha256"])
    for row in manifest["anchors"]:
        lines = (ROOT / row["path"]).read_text().splitlines(keepends=True)
        raw = "".join(lines[row["first_line"] - 1:row["last_line"]]).encode()
        check("anchor: " + row["id"], digest(raw) == row["sha256"])
    metadata = json.loads((ROOT / manifest["metadata"]).read_text())
    source_rows = [r for r in metadata["urls"] if r["filename"] == "pypdfium2-5.9.0.tar.gz"]
    check("unique exact archive metadata", len(source_rows) == 1)
    if len(source_rows) == 1:
        archive = (OUT / "sources/pypdfium2-5.9.0.tar.gz").read_bytes()
        check("metadata archive digest", digest(archive) == source_rows[0]["digests"]["sha256"])
        check("metadata archive byte count", len(archive) == source_rows[0]["size"] == 272455)
    extraction = json.loads((OUT / "extraction-manifest.json").read_text())
    check("twelve selected text members", len(extraction["extracted"]) == 12)
    check("28 notices inventoried only", len(extraction["notice_inventory_only"]) == 28)
    for row in extraction["extracted"]:
        check("extracted: " + row["archive_member"], digest((ROOT / row["path"]).read_bytes()) == row["sha256"])
    record = json.loads((OUT / "sources/extracted/autorelease/record.json").read_text())
    check("declared witness pin only", record == {"tag": "5.9.0", "pdfium": 7869, "post_pdfium": None})
    exchanges = json.loads((ROOT / "data/accounting-master/selected-reuse-20261015/exchanges.json").read_text())
    check("eleven protected exchanges", len(exchanges) == 11)
    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "passed": all(r["passed"] for r in checks),
        "check_count": len(checks),
        "wall_seconds": time.monotonic() - started,
        "scope": "static identity and preservation only; no runtime or rights clearance",
    }
    (OUT / "checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Static source bindings: {sum(r['passed'] for r in checks)}/{len(checks)} pass; runtime/terms closure pending")
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
