"""Read-only metadata integrity and documentary-scope checks; no data loading."""
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
REVISION = "aa575e798cb00a296925e2086addb3e3fd9a1903"


def validate_declarations(record):
    # Numeric implications and data admission are intentionally separate.
    assert record["cropped"] == {"total": 135578, "private": 5804, "implied_public": 129774}
    assert record["single_pages"] == {"total": 467541, "private": 43288, "implied_public": 424253}
    for name in ("cropped", "single_pages"):
        r = record[name]
        assert r["total"] - r["private"] == r["implied_public"]
    assert record["full_documents"] == 9172
    assert record["table_categories"] == [9492, 630, 14740]
    assert sum(record["table_categories"]) == record["table_total"] == 24862
    for name in ("archive_memberships_verified", "document_disjointness_verified",
                 "cross_collection_overlap_verified", "experiment_revision_verified",
                 "failure_scoring_verified", "merging_score_difference_explained"):
        assert record[name] is False, name


def check():
    assertions = 0

    def require(condition, label):
        nonlocal assertions
        assert condition, label
        assertions += 1

    def load(name):
        return json.loads((UNIT / name).read_text())

    def bound(item):
        return hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]

    ledger = load("source-ledger.json")
    require(len(ledger["acquisitions"]) == 3, "fixed acquisitions")
    for item in ledger["acquisitions"]:
        for field in ("body", "headers", "receipt"):
            require(bound(item[field]), field)
        receipt = json.loads((ROOT / item["receipt"]["path"]).read_text())
        require(receipt["exitcode"] == 0 and receipt["http_code"] == 200, "HTTP success")
        require(receipt["url"] == item["url"], "request identity")
        require(receipt["size_download"] == (ROOT / item["body"]["path"]).stat().st_size,
                "actual bytes")
        require(receipt["size_download"] < 2097152 and receipt["time_total"] < 35, "request bounds")
    identity = load("sources/01-identity.json")
    tree = load("sources/03-tree.body")
    require(identity["id"] == "kensho/PubTables-v2" and identity["sha"] == REVISION, "dataset revision")
    require(identity["private"] is False and identity["gated"] is False, "access declaration")
    require(identity["cardData"]["license"] == "cdla-permissive-2.0", "declared licence")
    require(len(tree) == 48 and all(r["type"] == "file" for r in tree), "returned tree scope")
    names = {r["path"] for r in tree}
    require(len(names) == 48 and names == {r["rfilename"] for r in identity["siblings"]}, "sibling inventory")
    headers = (UNIT / "sources/03-tree.headers").read_text()
    require(not re.search(r"^link\s*:", headers, flags=re.I | re.M), "no advertised next page")
    archives = {n for n in names if n.endswith(".tar.gz")}
    require(len(archives) == 42, "archive names only")
    require(names - archives == {"README.md", ".gitattributes", "uncompress.sh",
            "uncompress_cropped_tables.sh", "uncompress_full_documents.sh",
            "uncompress_single_pages.sh"}, "no separate split-ID file in returned inventory")
    require(not any(p.name.endswith((".tar.gz", ".zip", ".safetensors"))
                    for p in (UNIT / "sources").iterdir()), "no data acquisition")
    body = (UNIT / "sources/02-card.body").read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
    card_entry = next(r for r in tree if r["path"] == "README.md")
    require(blob == card_entry["oid"] == "29a4e196aa93c9bae62fa4f9c972d390966d57f0", "card git blob")
    require(len(body) == card_entry["size"] == 4295, "card size")
    card_headers = (UNIT / "sources/02-card.headers").read_text()
    require(REVISION in card_headers, "pinned response identity")
    require(datetime.fromisoformat(identity["lastModified"].replace("Z", "+00:00")) <
            datetime.fromisoformat("2026-06-02T00:00:00+00:00"), "release precedes paper v3")
    for item in ledger["passages"]:
        lines = (ROOT / item["path"]).read_text().splitlines()
        require(item["quote"] in lines[item["line"] - 1], item["id"])
    declarations = load("declarations.json")
    validate_declarations(declarations)
    require(True, "declared arithmetic and admission limits")
    mutations = []
    bad = deepcopy(declarations)
    bad["single_pages"]["implied_public"] += 1
    mutations.append(("wrong public-count implication", bad))
    for field in ("archive_memberships_verified", "document_disjointness_verified",
                  "cross_collection_overlap_verified", "experiment_revision_verified",
                  "failure_scoring_verified", "merging_score_difference_explained"):
        bad = deepcopy(declarations)
        bad[field] = True
        mutations.append((field, bad))
    rejected = []
    for label, bad in mutations:
        try:
            validate_declarations(bad)
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError("invalid promotion accepted: " + label)
    for name in ("source-support", "citation-venue", "backward-snowball", "forward-snowball",
                 "claim-support", "omission-risk"):
        require(bool(load(name + "-ledger.json")), name)
    require(len(rejected) == 7, "altered evidence controls")
    return {"status": "passed", "acquisitions": 3, "source_anchors": len(ledger["passages"]),
            "assertions": assertions, "inventory_files": len(tree), "archive_names_only": len(archives),
            "rejected_controls": len(rejected), "data_memberships_verified": False,
            "manuscript_change_required": False, "whole_rows_closed": 0}
