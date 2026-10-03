#!/usr/bin/env python3
"""Independently check retained bytes, provenance and the published coverage grid.

This verifies source integrity and ledger consistency, not financial semantics.
It deliberately does not import the collector's selection/coverage functions.
"""
import argparse
import hashlib
import json
import re
import sys
import platform
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/financial-report-benchmark"
SUCCESS = {"acquired_verified", "revalidated_verified", "local_imported_verified"}


def verify(root, data):
    coverage = json.loads((data / "coverage.json").read_text())
    panel = json.loads((root / coverage["panel"]).read_text())
    evidence = json.loads((data / "source-evidence.json").read_text())
    qa_version = evidence["qa_version"]
    issues, inventory, versions = [], {}, {}

    def check_file(relative, digest, role):
        if not relative or not digest:
            issues.append({"path": relative, "issue": "missing_path_or_digest", "role": role})
            return
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            issues.append({"path": relative, "issue": "missing_or_outside_root", "role": role})
            return
        if relative not in inventory:
            content = path.read_bytes()
            inventory[relative] = {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "roles": []}
        item = inventory[relative]
        if role not in item["roles"]:
            item["roles"].append(role)
        if digest != item["sha256"]:
            issues.append({"path": relative, "issue": "hash_mismatch", "expected": digest, "actual": item["sha256"]})

    records = [json.loads(line) for line in (data / "acquisition-results.jsonl").read_text().splitlines() if line.strip()]
    for record in records:
        if record.get("local_path"):
            check_file(record["local_path"], record.get("sha256"), "original")
            versions[(record["document_id"], record["local_path"])] = record
        text_path = record.get("extracted_text_path")
        if text_path:
            match = re.fullmatch(r"extracted-([0-9a-f]{64})\.txt", Path(text_path).name)
            if match:
                check_file(text_path, match[1], "extracted_text")
            else:
                # Early extraction files predate immutable text names. Keep
                # them in inventory, but they cannot certify current evidence.
                path = root / text_path
                if path.is_file():
                    check_file(text_path, hashlib.sha256(path.read_bytes()).hexdigest(), "legacy_unpinned_text")
        if record.get("response_body_path"):
            check_file(record["response_body_path"], record.get("response_sha256"), "failed_response")
    for record in json.loads((data / "source-access.json").read_text()):
        if record.get("local_path"):
            check_file(record["local_path"], record.get("sha256"), "source_index")
    for entries in json.loads((data / "resolved-sources.json").read_text()).values():
        for record in entries:
            for key in ["landing", "discovery"]:
                if record.get(key + "_path"):
                    check_file(record[key + "_path"], record.get(key + "_sha256"), "link_provenance")

    expected, classes_by_issuer = {}, {}
    start = panel["coverage_window"]["start_year"]
    end = panel["coverage_window"]["end_year"]
    for issuer in panel["issuers"]:
        classes = ["annual", "q1", "q2", "q3"] if issuer["standard_family"] == "us_gaap" else ["annual", "interim_h1"]
        classes_by_issuer[issuer["issuer_id"]] = classes
        for year in range(start, end + 1):
            for cls in classes:
                expected[f"{issuer['issuer_id']}-{year}-{cls}"] = (issuer["issuer_id"], year, cls)
    rows = {row["document_id"]: row for row in coverage["rows"]}
    if len(rows) != len(coverage["rows"]) or set(rows) != set(expected):
        issues.append({"issue": "coverage_grid_disagrees_with_panel"})
    if coverage["expected_documents"] != len(expected):
        issues.append({"issue": "incorrect_expected_count"})

    verified = set()
    digests = defaultdict(list)
    publication_status = defaultdict(int)
    basis_anchors = {}
    pdf_pages = {}
    pdf_repair_diagnostics = []
    for doc_id, row in rows.items():
        candidates = [v for (key, _), v in versions.items() if key == doc_id and v.get("status") in SUCCESS and v.get("qa_version") == qa_version]
        if bool(candidates) != (row["status"] in SUCCESS):
            issues.append({"document_id": doc_id, "issue": "coverage_disagrees_with_current_version_verdicts"})
        if row["status"] not in SUCCESS:
            continue
        version = versions.get((doc_id, row["local_path"]), {})
        if version.get("status") not in SUCCESS or version.get("qa_version") != qa_version:
            issues.append({"document_id": doc_id, "issue": "selected_version_not_current_and_verified"})
            continue
        for field in ["sha256", "extracted_text_path", "source_url", "qa_version"]:
            if row.get(field) != version.get(field):
                issues.append({"document_id": doc_id, "issue": "coverage_field_disagrees_with_ledger", "field": field})
        selected_evidence = evidence.get("documents", {}).get(doc_id, {})
        for field in ["local_path", "sha256", "extracted_text_path", "status", "qa_version"]:
            if selected_evidence.get(field) != version.get(field):
                issues.append({"document_id": doc_id, "issue": "source_evidence_disagrees_with_selected_ledger_version", "field": field})
        verified.add(doc_id)
        digests[row["sha256"]].append(doc_id)
        checks = version.get("checks", {})
        for key in ["issuer", "period_year", "report_class", "statements", "notes", "accounting_basis"]:
            if checks.get(key, {}).get("status") not in {"matched", "verified"}:
                issues.append({"document_id": doc_id, "issue": "missing_required_evidence", "check": key})
        if not re.match(r"https?://", version.get("source_url") or ""):
            issues.append({"document_id": doc_id, "issue": "missing_public_source"})
        if not re.fullmatch(r"extracted-[0-9a-f]{64}\.txt", Path(version.get("extracted_text_path") or "").name):
            issues.append({"document_id": doc_id, "issue": "current_extraction_not_hash_pinned"})
        text = (root / version["extracted_text_path"]).read_text()
        original = root / row["local_path"]
        if original.suffix.lower() == '.pdf':
            import fitz
            try:
                with fitz.open(original) as pdf:
                    pdf_pages[doc_id] = pdf.page_count
                    if pdf.needs_pass or pdf.page_count == 0:
                        issues.append({"document_id": doc_id, "issue": "unreadable_pdf"})
                    else:
                        pdf.load_page(0).get_text()
                        pdf.load_page(pdf.page_count - 1).get_text()
                    if pdf.is_repaired:
                        pdf_repair_diagnostics.append(doc_id)
            except Exception as error:
                issues.append({"document_id": doc_id, "issue": "pdf_parse_failure", "error": str(error)})
        compact = " ".join(text.split())
        anchors = checks.get("accounting_basis", {}).get("evidence", [])
        if not anchors:
            issues.append({"document_id": doc_id, "issue": "missing_basis_quote"})
        for anchor in anchors:
            if anchor["quote"] not in compact:
                issues.append({"document_id": doc_id, "issue": "basis_quote_not_in_retained_text"})
        basis_anchors[doc_id] = {"original": row["local_path"], "source_url": version["source_url"], "anchors": anchors}
        if original.suffix.lower() == '.pdf':
            pages = text.split('\f')
            boundaries, offset = [], 0
            for page_no, page in enumerate(pages, 1):
                normalized = ' '.join(page.split())
                if normalized:
                    boundaries.append((offset, page_no))
                    offset += len(normalized) + 1
            located = []
            for anchor in anchors:
                quote_offset = compact.find(anchor['quote'])
                def page_at(position):
                    candidates = [page for start, page in boundaries if start <= position]
                    return candidates[-1] if candidates else None
                located.append({**anchor,
                                'pdf_page_at_quote_start': page_at(quote_offset),
                                'pdf_page_at_quote_end': page_at(quote_offset + len(anchor['quote']) - 1),
                                'pdf_page_at_basis_match': page_at(anchor.get('match_text_offset', quote_offset))})
            basis_anchors[doc_id]['anchors'] = located
        metadata = version.get("source_metadata", {})
        publication_status[metadata.get("publication_date_status", "not_verified")] += 1

    duplicates = [{"sha256": digest, "documents": ids} for digest, ids in digests.items() if len(ids) > 1]
    if duplicates:
        issues.append({"issue": "duplicate_bytes_across_selected_slots", "duplicates": duplicates})
    sequences = {}
    minimum = panel["coverage_window"]["minimum_complete_years_per_issuer"]
    for issuer, classes in classes_by_issuer.items():
        complete = [year for year in range(start, end + 1) if all(f"{issuer}-{year}-{cls}" in verified for cls in classes)]
        longest = run = 0
        for year in range(start, end + 1):
            run = run + 1 if year in complete else 0
            longest = max(longest, run)
        sequences[issuer] = {"complete_years": complete, "longest_consecutive_complete_years": longest}
        stated = coverage["per_issuer"][issuer]
        if stated["complete_years"] != complete or stated["longest_consecutive_complete_years"] != longest:
            issues.append({"issuer_id": issuer, "issue": "coverage_sequence_disagrees"})
    if len(verified) != coverage["verified_documents"]:
        issues.append({"issue": "verified_count_disagrees"})
    ready = all(s["longest_consecutive_complete_years"] >= minimum for s in sequences.values()) and not duplicates
    if ready != (coverage["acceptance"]["status"] == "source_corpus_ready"):
        issues.append({"issue": "readiness_disagrees"})

    return {"generated_at": datetime.now(timezone.utc).isoformat(), "status": "pass" if not issues else "fail",
            "scope": "Byte integrity, retained provenance, current source-QA evidence and independent period-grid recomputation; no accounting or model certification",
            "qa_version": qa_version, "python": platform.python_version(), "ledger_records": len(records), "retained_original_versions": len(versions),
            "verified_slots": len(verified), "coverage_minimum_met": ready,
            "source_readiness": ready and not issues, "issuer_sequences": sequences,
            "panel": {"path": coverage["panel"], "sha256": hashlib.sha256((root / coverage["panel"]).read_bytes()).hexdigest()},
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "publication_date_status": dict(publication_status), "issues": issues,
            "input_sha256": {name: hashlib.sha256((data / name).read_bytes()).hexdigest() for name in ["coverage.json", "source-evidence.json", "acquisition-results.jsonl", "resolved-sources.json", "source-access.json"]},
            "files": inventory, "basis_anchors": basis_anchors, "accepted_pdf_page_counts": pdf_pages,
            "pdf_repair_diagnostics": pdf_repair_diagnostics}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DATA)
    args = parser.parse_args()
    result = verify(ROOT, args.data_root)
    (args.data_root / "integrity-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "ledger_records", "retained_original_versions", "verified_slots", "source_readiness", "issues"]}, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
