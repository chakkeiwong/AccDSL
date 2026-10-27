"""Read-only static integrity checks; --record writes checks.json once."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
NATIVE = ROOT / "data/accounting-master/native-reuse-boundary-20261018"
EARLIER = ROOT / "data/accounting-master/component-notice-inquiry-20261018"
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
PREFIX = "pypdfium2-5.9.0/BUILD_LICENSES/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    checks_path = OUT / "checks.json"
    if args.record and checks_path.exists():
        parser.error("checks.json already exists; use the default read-only verification")
    started = datetime.now(timezone.utc).isoformat()
    clock_start = time.monotonic()
    checks = []

    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
        if not condition:
            raise ValueError(name)

    def binding(row):
        return sha((ROOT / row["path"]).read_bytes()) == row["sha256"]

    manifest_path = OUT / "source-manifest.json"
    manifest = load(manifest_path)
    check("completed reading status", manifest["status"] == "complete_author_reading_actual_build_pending")
    for row in manifest["protected_inputs"]:
        check("protected: " + row["path"], binding(row))
    check("31 protected inputs retained", len(manifest["protected_inputs"]) == len({r["path"] for r in manifest["protected_inputs"]}) == 31)
    for row in [manifest["archive"], manifest["plan"], manifest["pending_reading_snapshot"], *manifest["artifacts"]]:
        check("binding: " + row["path"], binding(row))
    pending = load(ROOT / manifest["pending_reading_snapshot"]["path"])
    check("pending snapshot preserves extraction-stage meaning", pending["status"] == "extracted_reading_pending" and not pending["anchors"] and all(r["reading_status"] == "pending" for r in pending["selected_texts"]))
    check("protected inputs were not replaced at reading completion", pending["protected_inputs"] == manifest["protected_inputs"])
    identity_fields = ["archive_member", "path", "sha256", "size", "lines", "inspection_encoding"]
    check("same 23 extracted identities", [{k:r[k] for k in identity_fields} for r in pending["selected_texts"]] == [{k:r[k] for k in identity_fields} for r in manifest["selected_texts"]])

    inventory = load(NATIVE / "extraction-manifest.json")["notice_inventory_only"]
    inventory_map = {r["archive_member"]: r for r in inventory}
    previous = load(EARLIER / "source-manifest.json")["selected_texts"]
    selected = manifest["selected_texts"]
    old_names = {r["archive_member"] for r in previous}
    new_names = {r["archive_member"] for r in selected}
    check("unique exact 28-member inventory", len(inventory_map) == len(inventory) == 28)
    check("disjoint exact 5+23 coverage", len(old_names) == len(previous) == 5 and len(new_names) == len(selected) == 23 and not old_names & new_names and old_names | new_names == inventory_map.keys())
    check("manifest inventory counts", (manifest["inventory_count"],manifest["earlier_selected_count"],manifest["complement_count"]) == (28,5,23))
    archive_path = ROOT / manifest["archive"]["path"]
    check("exact retained archive", archive_path.stat().st_size == 272455 and sha(archive_path.read_bytes()) == "db1274bd27844db6fda17ef1dbcd0026c47d357437058d838e98060c0da9e92e")
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        notices = [m for m in members if m.name.startswith(PREFIX) and not m.isdir()]
        check("archive exact unique notice inventory", len(notices) == len({m.name for m in notices}) == 28 and {m.name for m in notices} == inventory_map.keys())
        for row in previous + selected:
            name = row["archive_member"]
            matches = [m for m in members if m.name == name]
            check("safe unique regular member: " + name, len(matches) == 1 and matches[0].isfile() and not matches[0].issym() and not matches[0].islnk() and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts and 0 < matches[0].size < 50000)
            raw = archive.extractfile(matches[0]).read()
            retained = (ROOT / row["path"]).read_bytes()
            check("exact retained member: " + name, raw == retained and sha(raw) == row["sha256"] and len(raw) == matches[0].size == row["size"] == inventory_map[name]["size"])
    for row in selected:
        raw = (ROOT / row["path"]).read_bytes()
        decoded = raw.decode("utf-8")
        check("complete reading metadata: " + row["path"], row["inspection_encoding"] == "utf-8" and "\x00" not in decoded and len(decoded.splitlines()) == row["lines"] and row["reading_status"] == "complete_author_inspection" and row["inspected_lines"] == [[1, row["lines"]]] and bool(row["conditional_disposition"]) and bool(row["missing_applicability_facts"]))
    comparison = load(OUT / "apache-comparison.json")
    compared_paths = {r["target"] for r in comparison["files"]}
    check("exact four comparison methods and 19 direct readings", len(comparison["files"]) == len(compared_paths) == 4 and {r["path"] for r in selected if r["reading_method"] == "reference_comparison_and_all_differences"} == compared_paths and sum(r["reading_method"] == "direct_complete_text" for r in selected) == 19)
    reference_path = str((OUT / "sources/abseil.txt").relative_to(ROOT))
    for comparison_row in comparison["files"]:
        reference_raw = (ROOT / comparison_row["reference"]).read_bytes()
        target_raw = (ROOT / comparison_row["target"]).read_bytes()
        check("comparison file identities: " + comparison_row["target"], comparison_row["reference"] == reference_path and sha(reference_raw) == comparison_row["reference_sha256"] and sha(target_raw) == comparison_row["target_sha256"])
        reference_lines = reference_raw.splitlines(keepends=True)
        target_lines = target_raw.splitlines(keepends=True)
        reference_end = target_end = 0
        valid = True
        for block in comparison_row["blocks"]:
            a,z = block["reference_slice_zero_based"]
            b,y = block["target_slice_zero_based"]
            reference_span = b"".join(reference_lines[a:z])
            target_span = b"".join(target_lines[b:y])
            tag = block["kind"]
            valid &= (a == reference_end and b == target_end and 0 <= a <= z <= len(reference_lines) and 0 <= b <= y <= len(target_lines) and (z > a or y > b) and sha(reference_span) == block["reference_sha256"] and sha(target_span) == block["target_sha256"] and tag in {"equal","insert","delete","replace"})
            if tag == "equal":
                valid &= reference_span == target_span
            elif tag == "insert":
                valid &= a == z and b < y
            elif tag == "delete":
                valid &= b == y and a < z
            elif tag == "replace":
                valid &= a < z and b < y and reference_span != target_span
            reference_end,target_end = z,y
        check("comparison blocks and complete ordered coverage: " + comparison_row["target"], valid and reference_end == len(reference_lines) and target_end == len(target_lines) == comparison_row["target_lines"])
    check("anchors cover every complementary text", {r["path"] for r in manifest["anchors"]} == {r["path"] for r in selected})
    for anchor in manifest["anchors"]:
        lines = (ROOT / anchor["path"]).read_bytes().splitlines(keepends=True)
        a,z = anchor["start_line"],anchor["end_line"]
        check(f"clause anchor: {anchor['path']}:{a}-{z}", 1 <= a <= z <= len(lines) and sha(b"".join(lines[a-1:z])) == anchor["sha256"] and bool(anchor["purpose"]))

    assessment = load(INTEGRATION / "assessment-successor.json")
    operations = load(INTEGRATION / "operation-successor.json")
    check("exact candidate hash remains in assessment and operations", assessment["candidate_pdf_sha256"] == operations["candidate_pdf_sha256"] == "afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80")
    check("53 obligations and six interactions retained", len(assessment["rows"]) == 53 and len(assessment["interactions"]) == 6)
    check("46 operation rows retained and not ready", len(operations["rows"]) == 46 and assessment["readiness"] == operations["readiness"] == "not_ready")
    check("independent and human acceptance remain pending", assessment["independent_review"] == assessment["human_acceptance"] == "pending")
    if checks_path.exists():
        recorded = load(checks_path)
        check("recorded checks reproduce current complete verification", recorded["source_manifest_sha256"] == sha(manifest_path.read_bytes()) and recorded["verifier_sha256"] == sha(Path(__file__).read_bytes()) and recorded["all_passed"] is True and recorded["checks"] == checks)
    report = {"scope": "Static preservation and completeness checks; author observations and actual-build rights decisions are not machine-certified.",
              "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "wall_seconds": time.monotonic() - clock_start,
              "source_manifest_sha256": sha(manifest_path.read_bytes()),
              "verifier_sha256": sha(Path(__file__).read_bytes()),
              "checks": checks, "all_passed": True}
    if args.record:
        with checks_path.open("x") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
    print(json.dumps({"all_passed": True,"checks": len(checks),"reading_complement":23,"inventory":28,"mode":"record_once" if args.record else "read_only"}))


if __name__ == "__main__":
    main()
