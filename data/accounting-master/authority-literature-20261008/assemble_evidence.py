"""Preserve transport results and claim-specific supplements to frozen ledgers."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
now = datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


receipts = []
for transfer in sorted((OUT / "sources").glob("*.transfer.json")):
    data = json.loads(transfer.read_text())
    stem = transfer.name.removesuffix(".transfer.json")
    files = [p for p in (OUT / "sources").glob(stem + ".*") if p.is_file()]
    if data["exitcode"] != 0:
        disposition = "network_failure; no primary content acquired"
    elif data["http_code"] != 200:
        disposition = "HTTP_error; response body preserved but unusable as primary content"
    elif stem == "asbe22-trusted":
        disposition = "official standard; identity and selected technical articles inspected"
    else:
        disposition = "discovery index only; linked content requires separate retrieval and inspection"
    receipts.append({
        "attempt": stem, "execution": "sandbox" if stem.endswith("-sandbox") else "trusted",
        "url": data.get("url"), "effective_url": data.get("url_effective"),
        "exit_code": data["exitcode"], "http_status": data["http_code"],
        "error": data.get("errormsg"), "bytes": data["size_download"],
        "wall_seconds": data["time_total"], "disposition": disposition,
        "transfer_file_mtime_utc": datetime.fromtimestamp(transfer.stat().st_mtime, timezone.utc).isoformat(),
        "timestamp_limit": "File mtime observed at receipt assembly; not an independently recorded request-start timestamp.",
        "files": {str(p.relative_to(ROOT)): sha(p) for p in files},
    })
write("acquisition-receipts.json", {
    "assembled_at": now, "requests": receipts,
    "distinct_requested_urls": len({r["url"] for r in receipts}),
    "sum_request_seconds": sum(r["wall_seconds"] for r in receipts),
    "budget": "At most twelve distinct resources; two legitimate routes per content target; 30 seconds/request. Sandbox failures retried trusted. No retries after the target route cap.",
    "route_dispositions": {"ASBE22": "official standard obtained", "ASBE22 issuance": "HTTPS and indexed HTTP both 502; branch stopped", "Caiani": "Kingston trusted DNS failure; Insubria handle HTTP 500; branch stopped"},
})

raw = ROOT / "docs/design/research/raw"
extract = json.loads((OUT / "source-extract.json").read_text())
technical_claims = [
    {"id": a["id"], "support_class": "PRIMARY_TECHNICAL_SUPPORT", "source": "asbe22-2017",
     "article": a["article"], "exact_quote": a["quote_zh"], "allowed_claim": a["interpretation_en"]}
    for a in extract["anchors"]
]
technical_claims += [
    {"id": "authored-loan-arithmetic", "support_class": "PROJECT_DERIVATION", "artifact": "loan-calculation.json",
     "allowed_claim": "Specified assumptions reproduce ECL 5/11/55 and subsequent net interest 5.5; a one-year remaining horizon makes general-method stage amounts coincide.",
     "forbidden_claims": ["Actual-bank calibration or stage admission", "Current ASBE compliance", "Standard prescribes this exact journal decomposition"]},
    {"id": "caiani-technical-use", "support_class": "SOURCE_GAP_BLOCKER", "source": "caiani2016",
     "allowed_claim": "Full text remains unavailable through this bounded acquisition; no specific model contribution has been verified.",
     "forbidden_claims": ["Technical model description, validation, official-code equivalence or comparison inferred from metadata"]},
]
forward_dispositions = [
    ("EMPIRICAL_EXAMPLE", "Retain for later climate/financial-stability scenarios; title does not establish a company-disclosure reconstruction method."),
    ("EMPIRICAL_EXAMPLE", "Retain for a later comparison of green-finance policy scenarios; no technical policy effect is imported."),
    ("DIRECT_METHOD", "Inspect when specifying calibration of learned or agent-based forecasts; surrogate-calibration details require full text and downstream evidence."),
    ("IMPLEMENTATION_OR_SOFTWARE", "Prioritise after recovering the base method as a version/correction and official-code lead; update status and code lineage remain unchecked."),
    ("COMPETITOR", "Potential analytical alternative for macroeconomic concentration/markup mechanisms; inspect if an aggregate equilibrium closure is proposed."),
    ("DIRECT_METHOD", "Potential source for how heterogeneous expectations enter stock-flow models; inspect before choosing behavioural assumptions."),
]
forward = []
for filename in ["caiani2016-citing-high.json", "caiani2016-citing-recent.json"]:
    for paper in json.loads((raw / filename).read_text())["results"]:
        classification, action = forward_dispositions[len(forward)]
        forward.append({"title": paper["title"], "doi": paper.get("doi"),
                        "citation_count_in_saved_index": paper.get("cited_by_count", "not available"),
                        "source": str((raw / filename).relative_to(ROOT)), "source_sha256": sha(raw / filename),
                        "classification": classification, "classification_basis": "title and saved metadata only",
                        "action": action, "technical_support": "not inspected"})
inputs = [raw / n for n in ["caiani2016-search.json", "caiani2016-candidate.txt", "caiani2016-citing-high.json", "caiani2016-citing-recent.json"]]
inputs += [ROOT / "docs/design/research" / n for n in ["source-support.json", "claim-support.json", "citation-venue.json", "omissions.json", "backward-snowball.json", "forward-snowball.json"]]
write("source-claim-supplement.json", {
    "recorded_at": now, "original_ledger_policy": "Supplement; original source and research ledgers remain unchanged.",
    "baseline_inputs": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
    "source_support": [
        {"id": "asbe22-2017", "classification": "OFFICIAL_DATED_ACCOUNTING_AUTHORITY", "full_text": "retained official HTML",
         "source_extract": "source-extract.json", "source_sha256": extract["source_sha256"],
         "technical_inspection": extract["inspected_for_current_claims"],
         "limits": ["Not a verified consolidated current text", "Issuance schedule and target-entity adoption remain unverified", "Interpretations 19 and 20 appear as official-index leads; their relevance and operative content are uninspected"]},
        {"id": "caiani2016", "title": "Agent based-stock flow consistent macroeconomics: Towards a benchmark model",
         "journal_doi": "10.1016/j.jedc.2016.06.001", "working_paper_doi": "10.2139/ssrn.2664125",
         "classification": "SOURCE_BLOCKED", "full_text": "not acquired", "technical_sections_inspected": [],
         "official_code": "not identified or audited from primary content", "current_correction_version_review": "not completed",
         "historical_wrong_content": {"recorded_requested_arxiv_id": "1508.02248", "rejected_text_arxiv_id": "1508.02253v2",
                                      "rejected_title": "Average Error Probability in Wireless Sensor Networks With Imperfect Sensing and Communication for Different Decision Rules",
                                      "disposition": "Wrong-source text excluded from all Caiani claims; discrepancy retained, cause unknown."}},
    ],
    "claim_support": technical_claims,
    "citation_and_venue_metadata": {
        "source": "docs/design/research/citation-venue.json", "inherited_ledger_date": "2026-10-02", "live_refresh": "not performed",
        "caiani_journal": "Journal of Economic Dynamics and Control", "historical_citation_count": 319,
        "source_index": "OpenAlex; saved caiani2016-search.json", "saved_retracted_flag": False,
        "venue_ranking": "not independently inspected", "caveat": "Old index flags and counts do not establish full-text identity, a clean correction history or scientific validity."},
    "backward_snowball": {"seed": "caiani2016", "status": "blocked: no verified primary reference list", "new_candidates": []},
    "forward_snowball": {"query": "No new forward query; rescreened the six retained high/recent results", "screened_at": now,
                         "metadata_date_limit": "Inherited ledger date is 2026-10-02; original per-request timestamp is not independently verified here.", "candidates": forward},
    "omissions": [
        {"id": "caiani2016", "status": "SOURCE_BLOCKED", "reason": "Two justified routes failed", "reviewer_risk": "A potentially central stock-flow antecedent still has no inspected technical treatment", "next_action": "Use a genuinely new legitimate source route in a later bounded unit; inspect technical sections and code before use"},
        *[{"id": paper, "status": "SOURCE_BLOCKED", "action": "No new route attempted in this unit; remains in the internal source queue"}
          for paper in ["mccarthy1982", "imielinski_lipski1984", "tamer2010"]],
    ],
    "decision": "Support only the inspected dated ASBE provisions and the local conditional derivation; retain literature and operative-applicability blockers.",
    "not_concluded": "Complete E07/E08, comprehensive snowballing, current standards compliance, stock-flow model superiority or a rejected research direction.",
})
print(json.dumps({"requests": len(receipts), "distinct_urls": len({r["url"] for r in receipts}), "technical_anchors": len(extract["anchors"]), "forward_metadata_decisions": len(forward)}))
