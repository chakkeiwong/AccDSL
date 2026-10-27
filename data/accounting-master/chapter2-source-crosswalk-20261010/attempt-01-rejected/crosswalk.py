#!/usr/bin/env python3
"""Build a bounded inventory for the Chapter 2/source-support audit.

This script only inventories retained records and proposes family locations.
The generated dispositions are review inputs; the accompanying result records
the rendered-reading decision separately.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PDF = ROOT / "docs/design/proposal/manuscript-quality-inventory-20261010/accounting-product-proposal.pdf"
TEX = ROOT / "docs/design/proposal/manuscript-quality-inventory-20261010/chapters/13-reference-company.tex"

SECTION_CATALOG = {
    "case-source": {
        "location": "Chapter 2 §2.6, `sec:apple`, lines 217–367",
        "role": "source package, calendars, measurement identity, debt/FX dependencies, evidence boundary",
    },
    "case-revenue": {
        "location": "Chapter 2 §2.7, `sec:apple-revenue`, lines 369–522",
        "role": "recognition, collection, deferred revenue, product/geography populations, conditional histories",
    },
    "case-commitments": {
        "location": "Chapter 2 §2.8, `sec:apple-commitments`, lines 524–669",
        "role": "lease and purchase commitments, delivery/payment, supplier and legal dependencies",
    },
    "case-liquidity": {
        "location": "Chapter 2 §2.9, included `sections/apple-liquidity.tex`",
        "role": "restricted resources, securities, valuation, receipts and customer overlap",
    },
    "case-segments": {
        "location": "Chapter 2 §2.10, included `sections/apple-segments.tex`",
        "role": "regional/customer labels, cost and asset populations, product exposure",
    },
    "case-perimeter": {
        "location": "Chapter 2 §2.11, included `sections/apple-perimeter.tex`",
        "role": "entities, control, selling/manufacturing/ownership, tax and currency facts",
    },
    "case-legal": {
        "location": "Chapter 2 §2.12, included `sections/apple-legal.tex`",
        "role": "proceedings, allegations, remedies, recognition and operating revenue channels",
    },
    "case-pronouncements": {
        "location": "Chapter 2 §2.13, included `sections/apple-pronouncements.tex`",
        "role": "later disclosure, adoption plans, information cutoffs and estimate continuity",
    },
    "case-litigation": {
        "location": "Chapter 2 §2.14, included `sections/apple-litigation-risk.tex`",
        "role": "claims, indemnity, insurance, defense/settlement and recovery boundaries",
    },
    "case-regulation": {
        "location": "Chapter 2 §2.15, included `sections/apple-regulation.tex`",
        "role": "operative authority boundary and conditional operating restrictions",
    },
    "case-disruption": {
        "location": "Chapter 2 §2.16, included `sections/apple-disruption.tex`",
        "role": "demand, supply, channels, finance, disruption and recovery histories",
    },
    "case-competition": {
        "location": "Chapter 2 §2.17, included `sections/apple-competition-transition.tex`",
        "role": "competition, product transition, ecosystem support and product timing",
    },
    "case-components": {
        "location": "Chapter 2 §2.18, included `sections/apple-component-availability.tex`",
        "role": "supplier agreements, renewal, capacity, yield and delivery alternatives",
    },
    "case-quality": {
        "location": "Chapter 2 §2.19, included `sections/apple-quality-inventory.tex`",
        "role": "defects, safety, service, inventory, impairment, cancellation and recovery",
    },
    "later-assets": {
        "location": "Chapter 9 §9.5, included `sections/apple-operating-assets.tex`",
        "role": "inventory and fixed-asset movement identities",
    },
    "later-tax": {
        "location": "Chapter 9 §9.7, included `sections/apple-tax-settlement.tex`",
        "role": "tax expense, deferred balances, restricted assets and settlement",
    },
    "later-eps": {
        "location": "Chapter 10 §10.2, included `sections/apple-eps-ownership.tex`",
        "role": "shares, awards, repurchases, EPS denominators and ownership histories",
    },
    "later-debt": {
        "location": "Chapter 10 §10.1, included `sections/apple-debt.tex`",
        "role": "debt movements, refinancing and rate/FX exposure",
    },
}

THEME_RULES = [
    ("apple-revenue", ["case-revenue"]),
    ("apple-commitments", ["case-commitments"]),
    ("apple-assets", ["later-assets", "case-quality", "case-disruption"]),
    ("apple-tax", ["later-tax", "case-source", "case-pronouncements"]),
    ("apple-eps", ["later-eps", "case-source"]),
    ("apple-debt", ["case-source", "later-debt", "case-liquidity"]),
    ("apple-liquidity", ["case-liquidity", "case-source"]),
    ("apple-segments", ["case-segments", "case-revenue"]),
    ("apple-perimeter", ["case-perimeter", "case-segments"]),
    ("apple-legal", ["case-legal", "case-regulation"]),
    ("apple-pronouncements", ["case-pronouncements", "case-source"]),
    ("apple-litigation-risk", ["case-litigation", "case-legal"]),
    ("apple-regulation", ["case-regulation", "case-legal"]),
    ("apple-macroeconomic", ["case-disruption", "case-liquidity"]),
    ("apple-business-interruption", ["case-disruption", "case-components", "case-quality"]),
    ("apple-competition-transition", ["case-competition", "case-components", "case-revenue"]),
    ("apple-component-availability", ["case-components", "case-commitments"]),
    ("apple-quality-inventory", ["case-quality", "case-competition"]),
    ("apple-remaining-risks", ["case-competition", "case-commitments", "case-disruption", "case-legal", "case-regulation", "case-liquidity"]),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def first_text(record: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def rows_from(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data = json.loads(path.read_text())
    unit = path.parent.name
    claims: list[dict[str, Any]] = []
    queries: list[dict[str, Any]] = []

    for key in ("claims", "narrative_claims"):
        for item in data.get(key, []) or []:
            if not isinstance(item, dict):
                continue
            rid = first_text(item, ["id", "query", "source_unit"]) or f"{key}-{len(claims)+1}"
            text = first_text(item, ["author_interpretation", "interpretation", "meaning", "literal", "answer", "checked_answer"])
            claims.append({"unit": unit, "record_id": rid, "record_kind": key, "text": text, "source_class": first_text(item, ["source_class", "status"])})

    # Unit rows preserve the retained source interpretation, including explicit
    # heading rows; headings are later marked as structural rather than claims.
    for item in data.get("units", []) or data.get("material_units", []) or []:
        if not isinstance(item, dict):
            continue
        rid = first_text(item, ["id", "source_unit"]) or f"unit-{len(claims)+1}"
        text = first_text(item, ["interpretation", "meaning", "author_interpretation", "literal", "quote"])
        claims.append({"unit": unit, "record_id": rid, "record_kind": "unit", "text": text, "source_class": first_text(item, ["status", "support", "source"])})

    for item in data.get("queries", []) or []:
        if not isinstance(item, dict):
            continue
        rid = first_text(item, ["id", "query"]) or f"query-{len(queries)+1}"
        question = first_text(item, ["question", "query", "id"])
        answer = first_text(item, ["answer", "supported_answer", "checked_answer", "status", "reason", "unresolved", "missing_facts"])
        queries.append({"unit": unit, "record_id": rid, "question": question, "answer_or_boundary": answer})
    return claims, queries


def sections_for(unit: str) -> list[str]:
    for prefix, sections in THEME_RULES:
        if unit.startswith(prefix):
            return sections
    return ["case-source"]


def disposition(unit: str, record_kind: str) -> str:
    if unit in {"apple-assets-20261008", "apple-tax-20261009", "apple-eps-20261009"}:
        return "covered_elsewhere_in_manuscript"
    if unit in {"apple-remaining-risks-20261010", "apple-macroeconomic-20261010", "apple-business-interruption-20261010"}:
        return "covered_by_existing_mechanism_pending_independent_acceptance"
    return "covered_by_existing_mechanism_or_source_boundary"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(set(ROOT.glob("data/accounting-master/apple-*/claim-query-ledger.json")) | set(ROOT.glob("data/accounting-master/apple-*/source-claim-supplement.json")))
    inventory = []
    all_claims = []
    all_queries = []
    for path in files:
        data = json.loads(path.read_text())
        claims, queries = rows_from(path)
        inventory.append({
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
            "claim_rows": len(claims),
            "query_rows": len(queries),
            "top_level_keys": sorted(data),
        })
        all_claims.extend(claims)
        all_queries.extend(queries)

    # Deduplicate the same explicit row when both a claim ledger and source
    # supplement carry it; keep the source supplement as provenance in the
    # inventory and use the stable unit/id pair for the mapping population.
    unique_claims = {}
    for row in all_claims:
        unique_claims.setdefault((row["unit"], row["record_id"], row["record_kind"]), row)
    unique_queries = {}
    for row in all_queries:
        unique_queries.setdefault((row["unit"], row["record_id"]), row)

    crosswalk = []
    for row in sorted(unique_claims.values(), key=lambda r: (r["unit"], r["record_id"], r["record_kind"])):
        secs = sections_for(row["unit"])
        crosswalk.append({**row, "support_locations": [SECTION_CATALOG[s]["location"] for s in secs], "mechanism_roles": [SECTION_CATALOG[s]["role"] for s in secs], "disposition": disposition(row["unit"], row["record_kind"]), "independent_acceptance": "pending"})
    query_rows = []
    for row in sorted(unique_queries.values(), key=lambda r: (r["unit"], r["record_id"])):
        secs = sections_for(row["unit"])
        query_rows.append({**row, "support_locations": [SECTION_CATALOG[s]["location"] for s in secs], "disposition": disposition(row["unit"], "query"), "independent_acceptance": "pending"})

    manifest = {
        "generated_by": str(Path(__file__).relative_to(ROOT)),
        "generated_at": "2026-10-10",
        "baseline": {"pdf": str(PDF.relative_to(ROOT)), "pdf_sha256": sha256(PDF), "tex": str(TEX.relative_to(ROOT)), "tex_sha256": sha256(TEX)},
        "input_file_count": len(files),
        "input_files": inventory,
        "deduplicated_claim_count": len(crosswalk),
        "deduplicated_query_count": len(query_rows),
        "interpretation": "Inventory and family mapping are review inputs. They do not certify semantic coverage or acceptance.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (OUT / "ledger-inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    (OUT / "claim-query-crosswalk.json").write_text(json.dumps({"claims": crosswalk, "queries": query_rows}, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
