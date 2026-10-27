"""One-time documentary records from already acquired metadata; standard library."""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
PRIOR = UNIT.parent / "r04-pubtablesv2-20261019"


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write(name, value):
    with (UNIT / name).open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def main():
    assert not (UNIT / "source-ledger.json").exists(), "one-time construction"
    acquisitions = []
    for stem in ("01-identity", "02-card", "03-tree"):
        receipt = UNIT / "sources" / (stem + ".receipt.json")
        r = json.loads(receipt.read_text())
        acquisitions.append({"url": r["url"], "effective_url": r["url_effective"],
            "http_status": r["http_code"], "redirects": r["num_redirects"],
            "bytes": r["size_download"], "curl_seconds": r["time_total"],
            "body": bind(ROOT / r["filename_effective"]), "receipt": bind(receipt),
            "headers": bind(UNIT / "sources" / (stem + ".headers")),
            "command_provenance": "Actual curl JSON receipt retained; full prior invocation is not reconstructed as an executed command.",
            "plan_bounds": {"seconds": 35, "bytes": 2097152, "scheme": "HTTPS"}})
    card = UNIT / "sources/02-card.body"
    needles = [
        ("licence", "license: cdla-permissive-2.0"),
        ("evaluation-pending", "Official dataset evaluation scripts and leaderboard coming soon!"),
        ("metric-only-suggestion", "you can create your own evaluation using GriTS"),
        ("metric-release", "2026 Apr 15"),
        ("dataset-release", "2026 Feb 11"),
        ("three-contexts", "Each collection contains tables in a specific context"),
        ("cropped-total", "**135,578** cropped tables"),
        ("cropped-size-filter", "long (30 or more rows) or wide (12 or more columns)"),
        ("cropped-private", "**5,804** of these tables"),
        ("page-total", "**467,541** individual document pages"),
        ("page-table-total", "**548,414** tables"),
        ("page-private", "**43,288** of these pages"),
        ("document-total", "**9,172** full documents"),
        ("card-selection", "every document contains at least one multi-page table"),
        ("table-parts", "**9,492** multi-page tables, **630** single-page tables"),
        ("document-task", "cell structure and content but not location"),
        ("private-purpose", "held back to evaluate data leakage for the public test set in future models"),
        ("archive-format", "collection of tar.gz files"),
    ]
    passages = []
    for identifier, needle in needles:
        lines = card.read_text().splitlines()
        line = next(i for i, text in enumerate(lines, 1) if needle in text)
        passages.append({"id": identifier, "path": str(card.relative_to(ROOT)), "line": line, "quote": needle})
    paper = PRIOR / "sources/02-paper.txt"
    needle = "contains at least one multi-part table. A multi-part table"
    line = next(i for i, text in enumerate(paper.read_text().splitlines(), 1) if needle in text)
    passages.append({"id": "paper-selection", "path": str(paper.relative_to(ROOT)), "line": line, "quote": needle})
    write("source-ledger.json", {"completed_local_date": "2026-10-20", "unit_name_date": "20261019",
        "revision": "aa575e798cb00a296925e2086addb3e3fd9a1903", "acquisitions": acquisitions,
        "passages": passages, "read_scope": "Entire card; all API/tree entries and response headers. No scripts or data records read.",
        "inventory_scope": "48 files; API siblings agree; no pagination Link header; 42 archive names, no archive contents.",
        "comparator": bind(paper)})
    declarations = {"cropped": {"total": 135578, "private": 5804, "implied_public": 129774},
        "single_pages": {"total": 467541, "private": 43288, "implied_public": 424253},
        "full_documents": 9172, "table_categories": [9492, 630, 14740], "table_total": 24862,
        "meaning": "Arithmetic implications of card declarations, not archive/sample observations."}
    for field in ("archive_memberships_verified", "document_disjointness_verified",
                  "cross_collection_overlap_verified", "experiment_revision_verified",
                  "failure_scoring_verified", "merging_score_difference_explained"):
        declarations[field] = False
    write("declarations.json", declarations)
    write("source-support-ledger.json", {"classification": "IMPLEMENTATION_OR_SOFTWARE",
        "title": "PubTables-v2 official dataset card and release metadata", "authors": "kensho dataset owner; no separate card authorship claim",
        "year": 2026, "url": acquisitions[0]["url"], "local_source": bind(card),
        "publication_status": "Dataset documentation at pinned public revision, not a new paper",
        "retraction_quarantine": "No warning observed in inspected card/API; no independent global status search in this unit",
        "full_text_status": "Entire card read; archive contents and scripts uninspected",
        "inspected_sections": ["News", "Collections", "Cropped Tables", "Single Pages", "Full Documents", "Download"],
        "equations_theorems_algorithms": "N/A documentary card",
        "allowed": ["exact release identity", "declared counts/private sets", "returned inventory", "documentation limits"],
        "forbidden": ["split safety", "actual sample memberships", "empirical revision equivalence", "licence clearance", "accounting accuracy"]})
    write("citation-venue-ledger.json", {"access_date_local": "2026-10-20", "citation_count": "not available",
        "citation_source": "not queried for dataset card", "venue": "Hugging Face dataset documentation",
        "venue_metric": "not available", "caveat": "Hosting and access status establish neither research quality nor data validity."})
    write("backward-snowball-ledger.json", {"scope": "All documentary links relevant to the question inspected by role",
        "entries": [
            {"target": "arXiv2512.10888", "classification": "DIRECT_METHOD", "action": "Already technically read as v3 in predecessor; preserve version distinction"},
            {"target": "kensho-technologies/grits", "classification": "IMPLEMENTATION_OR_SOFTWARE", "action": "Pinned source already read; original GriTS technical theory remains next"},
            {"target": "Hugging Face paper page 2512.10888", "classification": "BACKGROUND", "action": "Omit mirror metadata; primary paper identity retained"},
            {"target": "PubTables-1M mention", "classification": "DIRECT_METHOD", "action": "Existing source context; no new technical claims from this card"}],
        "references": "Card has no numbered bibliography; image links are illustrations, not independent technical sources."})
    write("forward-snowball-ledger.json", {"scope": "No new forward search in bounded metadata inquiry",
        "retained_followup": "POTATR arXiv2606.09788v1 is already read in r04-potatr-20261019",
        "query_source_date": "No new query; do not infer global coverage", "status": "Forward coverage remains incomplete"})
    write("claim-support-ledger.json", {"candidate": "3.44", "chapter": "03-literature.tex lines 201-240",
        "manuscript_change": False, "entries": [
            {"claim": "Current release has a pinned documentary identity", "class": "IMPLEMENTATION_EVIDENCE", "support": "API sha + pinned card blob + matching tree/siblings"},
            {"claim": "Implied public totals are 129774 cropped tables and 424253 pages", "class": "PROJECT_DERIVATION", "support": "Declared total minus declared private; declarations.json; no membership verification"},
            {"claim": "Card multi-page and paper multi-part selection wordings differ", "class": "PRIMARY_TECHNICAL_SUPPORT", "support": ["card-selection", "paper-selection"], "limit": "Not a demonstrated contradiction in data"},
            {"claim": "Source does not supply the unresolved exact IDs/protocol in inspected material", "class": "SOURCE_GAP_BLOCKER", "support": "Full card and returned inventory only; archive contents unknown"},
            {"claim": "Extraction metrics establish accounting correctness", "class": "SOURCE_GAP_BLOCKER", "support": "Unsupported by this metadata inquiry; existing manuscript distinction preserved"}]})
    write("omission-risk-ledger.json", {"entries": [
        {"gap": "Exact grouped splits and inter-collection overlap", "status": "requires later authorised data/ID inquiry", "reason": "No standalone ID manifest; all annotation/data archives excluded from this unit"},
        {"gap": "Paper-era evaluation, parse-failure and merging provenance", "status": "open", "reason": "Card announces evaluation scripts as forthcoming; current revision predates v3"},
        {"gap": "Original GriTS technical theory and official code", "status": "inspect next", "reason": "Current wrapper's heuristic description needs original technical scope"},
        {"gap": "Licence terms and applicable artifact rights", "status": "open", "reason": "Label is a declaration; no terms or full artifact audit"}],
        "reviewer_risk": "Metadata-only documentation must not be presented as a split audit or comprehensive extraction survey."})
    write("execution-history.json", {"resumed_local_date": "2026-10-20", "environment": "/home/chakwong/miniconda3/envs/tfgpu/bin/python3",
        "prior_stages": "prepare and three acquisitions completed before resume; actual acquisition receipts are authoritative",
        "resume_commands": ["CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B " + str(UNIT.relative_to(ROOT)) + "/" + name for name in
            ("build_records.py", "verify.py --check", "verify.py --record", "verify.py")],
        "scope": "Deterministic standard-library metadata checks; CPU only, GPU devices intentionally hidden; no statistical experiment."})
    print(json.dumps({"constructed": True, "acquisitions": len(acquisitions), "source_anchors": len(passages), "literature_ledgers": 6}))


if __name__ == "__main__":
    main()
