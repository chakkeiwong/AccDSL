"""Join frozen package populations to dated inquiries without changing either."""
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PACKAGE = ROOT / "docs/design/cases/apple/continuation-20261007/case-supplement-v1.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence(name):
    path = ROOT / "data/accounting-master" / name / "result.md"
    assert path.is_file(), path
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path),
            "role": "carry prior scoped source judgment; not a new full-source review"}


# Entries identify the live missing facts, not just a generic completion status.
NOTE_WORK = {
    "policy": (["apple-perimeter-20261009", "apple-pronouncements-20261010"],
        "Legal control dates, complete subsidiary population, eliminations and operative policy choices.",
        "Which legal entity owns each asset or owes each obligation at the query date?",
        "Retained subsidiary and policy disclosures are a starting population; public filings for an identified event, then actual control/contract facts where undisclosed."),
    "revenue": (["apple-revenue-20261008"],
        "Contract performance dates, returns, price allocation and gross deferred-revenue additions/releases remain unidentified.",
        "How much future revenue or collection follows from existing contracts, on which dates?",
        "Retained Note 2 and its policy dependencies; contract cohorts and actual performance/settlement records are needed for execution."),
    "eps": (["apple-eps-20261009", "apple-award-versions-20261013"],
        "Time-weighted actual share issues/repurchases and instrument-specific dilution conditions remain missing.",
        "What basic/diluted EPS follows from this same history, rather than a ratio of incompatible aggregate populations?",
        "Retained EPS/share/award notes and proxy; executed grants and dated share movement facts for a full denominator."),
    "financial": (["apple-debt-20261009", "apple-liquidity-20261009"],
        "Instrument-level resets, hedge designations, valuation inputs, currencies and OCI recycling dates remain missing.",
        "What cash, fair-value and OCI consequences arise under a specified rate or FX path?",
        "Retained financial-instrument notes; identified instrument supplements and hedge documentation where available. Notional is not an exposure allocation."),
    "assets": (["apple-assets-20261008", "apple-history-compatibility-20261013", "apple-coupled-completion-20261013", "apple-settlement-paths-20261013"],
        "Inventory lots, asset cohorts/lives/retirements and the independent expense obligation used by the conditional completion are not issuer facts.",
        "Which depreciation, retirement loss, supplier payment and cash category follows from a jointly admissible history?",
        "Retained asset/policy/statement sources constrain aggregates; lot, cohort, obligation and settlement records are needed to admit an actual completion."),
    "supplemental": (["apple-tax-20261009", "apple-assets-20261008", "apple-coupled-completion-20261013"],
        "Broad other-asset/liability captions do not identify the hypothetical expense obligation, tax basis or cash-flow classification.",
        "Can a proposed offset obligation inhabit both the balance-sheet caption and the required noncash cash-flow row?",
        "Inspect an identified actual obligation and its classification/tax facts; no residual-balancing journal is admissible."),
    "tax": (["apple-tax-20261009"],
        "Jurisdiction-specific tax bases, reversal schedules, recognition conditions and settlement allocations remain missing.",
        "How much is current expense, deferred expense, payable or later cash settlement for the same entity and period?",
        "Retained Note 7 and interim payment dependencies; operative jurisdictional law and actual tax records where the public source stops."),
    "lease": (["apple-commitments-20261008", "apple-assets-20261008"],
        "Individual payments, rates, renewal judgments, modification facts and variable-payment drivers remain missing.",
        "Which ROU/liability/expense and operating or financing cash follows from an individual lease?",
        "Retained Note 8 constrains reported populations; identified contracts and applicable dated rules are needed for execution."),
    "debt": (["apple-debt-20261009", "apple-2018-indenture-source-20261012"],
        "Missing indentures/certificates, currency allocations, noncash movements and omitted instrument identities prevent a complete debt history.",
        "What is legally payable, by whom, when, with which trigger and cash-flow category?",
        "Specific annual exhibit targets 4.2–4.28 and a distinct supported public route. Reuse recorded 2018-indenture failures; no blind retry or invented terms."),
    "equity": (["apple-eps-20261009", "apple-stock-plan-source-20261013", "apple-performance-award-20261013", "apple-award-versions-20261013"],
        "Authorization is not execution; actual grant notices, exercise/vesting conditions, share delivery and repurchase dates remain missing.",
        "Which actual cash and share movements follow, and what reserve/share/EPS population does each affect?",
        "Retained plan and versioned forms plus proxy; named executed grants or dated transactions must resolve actual outcomes."),
    "commitment": (["apple-commitments-20261008", "apple-legal-20261010", "apple-litigation-risk-20261010"],
        "Obligating events, legal outcomes, payment dates and admissible estimates remain missing; narrative qualifications supply no probability or universal threshold.",
        "Does this item require recognition, disclosure, payment, or a conditional scenario only?",
        "Retained commitment/contingency/legal passages and any identified later legal filing; actual contracts or claims where public disclosure does not decide."),
    "segment": (["apple-segments-20261009"],
        "The 2025 retrospective tables now disclose selected 2024/2023 regional expenses. Product-by-region sales, entity cash, remaining allocations and behavior still are not identified.",
        "What did each named source disclose about the same year, and can regional stress be propagated without inventing cross-classifications?",
        "Use this unit's checked FY2025 Note 1/13 comparison; require reviewed scope mappings and further actual cross-classified facts for simulation."),
}
ANNUAL = {1:"policy",2:"revenue",3:"eps",4:"financial",5:"assets",6:"supplemental",7:"tax",8:"lease",9:"debt",10:"equity",11:"equity",12:"commitment",13:"segment"}
INTERIM = {1:"policy",2:"revenue",3:"eps",4:"financial",5:"assets",6:"debt",7:"equity",8:"equity",9:"commitment",10:"segment"}


def reference_group(row):
    number = row["number"]
    if number in ("101", "104"):
        return "taxonomy"
    if number.startswith("3."):
        return "constitution"
    if number.startswith("4.") and number != "4.29":
        return "debt"
    if number.startswith("10.") or number == "4.29":
        return "equity"
    if number == "21.1":
        return "policy"
    return "governance"


def main():
    started = time.perf_counter()
    package = json.loads(PACKAGE.read_text())
    notes = []
    for old in package["note_dispositions"]:
        period, _, number = old["note_id"].split(".")
        group = (ANNUAL if period == "annual" else INTERIM)[int(number)]
        names, residual, query, route = NOTE_WORK[group]
        notes.append({"id":old["note_id"],"frozen_assertion_ids":old["assertion_ids"],
            "frozen_disposition":old["status"],"affected_model_areas":old["affected_model_areas"],
            "group":group,"latest_evidence":[evidence(n) for n in names],
            "remaining_facts":residual,"affected_query":query,"next_supported_route":route,
            "complete_semantic_formalisation":False})
    groups = {key:{"latest_evidence":[evidence(n) for n in value[0]],
        "remaining_facts":value[1],"affected_query":value[2],"next_supported_route":value[3]}
        for key,value in NOTE_WORK.items()}
    groups.update({
        "constitution":{"latest_evidence":[evidence("apple-constitutional-sources-20261011")],
            "remaining_facts":"Exact historical articles and bylaws bodies remain unacquired.",
            "affected_query":"Which historical governance/authority restrictions apply to an identified corporate action?",
            "next_supported_route":"Only a distinct located public counterpart matched to the stated 2020/2024 edition; existing refused and failed routes are recorded."},
        "taxonomy":{"latest_evidence":[evidence("apple-inline-occurrences-20261013")],
            "remaining_facts":"Four concepts have a selected cross-filing occurrence comparison; complete external/transitive taxonomy closure and full fact mapping remain open.",
            "affected_query":"Do these occurrences denote the same entity/date/unit/concept, and is a proposed aggregation valid?",
            "next_supported_route":"Retained extension archive and exact X03 import URIs; inspect transitive definitions and mappings before using them. Converted annual HTML is not inline XBRL."},
        "governance":{"latest_evidence":[],
            "remaining_facts":"A retained certification, policy, consent or authorization does not establish all financial assertions or operative event authority.",
            "affected_query":"Who asserted or authorized this item, for which period and with what qualifications?",
            "next_supported_route":"Read the exact retained body or referenced certification; preserve its period, signer and qualifications. Missing interim bodies require a located exact counterpart."},
    })
    counterparts = {"annual.exhibit.10.13":"2022 filing Exhibit 10.1", "annual.exhibit.10.14":"2022 filing Exhibit 10.2", "annual.exhibit.10.15":"2022 filing Exhibit 10.3"}
    refs = []
    for old in package["reference_frontier"]:
        group = reference_group(old)
        row = {"id":old["id"],"description":old["description"],
            "frozen_document_status":old["document_status"],"frozen_semantic_status":old["semantic_status"],
            "source_pointer":"reference_frontier/"+old["id"],
            "exact_target_links":old["target_links"],"group":group,**groups[group],
            "counterpart_in_stock_plan_inquiry":counterparts.get(old["id"]),
            "reading_status":"retain frozen status with linked, scoped later inquiries; no blanket resolved label"}
        if old["id"] in counterparts:
            row["reading_status"] = "later exact filing counterpart and selected operative clauses inspected; actual grant facts and full amendment chain remain open"
        if old["id"] == "annual.exhibit.10.2":
            row.update({"remaining_facts":"Exact indemnification agreement and covered persons/events, advancement/reimbursement/insurance terms remain needed.",
                "affected_query":"Which defense-cost or indemnification obligation arises on which legal event?",
                "latest_evidence":[evidence("apple-litigation-risk-20261010")],
                "next_supported_route":"Exact incorporated indemnification form and identified later amendment, then actual event/claim facts."})
        refs.append(row)
    obligations = []
    queries = {
        "annual.partIII.item10":"Which dated governance assertions qualify authority for a corporate event?",
        "annual.partIII.item11":"Which compensation terms and actual awards explain expense and later settlement?",
        "annual.partIII.item12":"Who owns shares at the proxy's January 2, 2025 date, as distinct from FY2024 end?",
        "annual.partIII.item13":"Which related-party transactions or qualifications affect the proposed interpretation?",
        "annual.partIII.item14":"What services and reporting-period populations underlie the disclosed audit/tax/other fees?",
        "annual.exhibit.4.1.in_pdf":"Which specific instrument terms qualify the general securities description?",
        "omitted_debt_instruments":"Can the complete population of debt contracts be enumerated from this package?"}
    for old in package["package_obligations"]:
        base=old["baseline_obligation"]
        obligations.append({"id":base["id"],"frozen_status":base["status"],
            "affected_query":queries[base["id"]],"consequence":base["consequence"],
            "remaining_facts":base.get("unresolved", "Complete underlying contract identities and terms remain open."),
            "next_supported_route":base["next_route"],
            "source_pointer":"package_obligations/"+base["id"],
            "latest_evidence":([evidence("apple-eps-20261009"),evidence("apple-award-versions-20261013")] if base["id"].endswith(("item11","item12")) else [evidence("apple-debt-20261009")] if "debt" in base["id"] or "4.1" in base["id"] else [])})
    notes_by_id={r["id"]:r for r in notes}
    assertions=[{"id":a["id"],"note_id":a["note_id"],"frozen_translation_status":a["translation_status"],
        "source":a["source"],"proposed_consequence":a["proposed_consequence"],
        "residual_link":"note_dispositions/"+a["note_id"],
        "affected_query":notes_by_id[a["note_id"]]["affected_query"]} for a in package["material_assertions"]]
    frontier=[]
    for old in package["additional_frontier"]:
        row={"frozen":old,"current_disposition":"Preserve original limit; use the connected row groups and note inquiries above."}
        if old["id"]=="X02":
            row["current_disposition"]="The 2022 plan counterpart is now read; private grant facts, executed terms and amendment completeness remain unresolved. Do not repeat the old plan-unresolved label as current."
        if old["id"]=="X03":
            row["current_disposition"]="Selected actual occurrence comparison delivered; direct and transitive external taxonomy closure not established."
        frontier.append(row)
    doc={"schema_version":1,"scope":"Connected query/residual map, not full semantic closure or actual company completion.",
        "frozen_package":{"path":str(PACKAGE.relative_to(ROOT)),"sha256":digest(PACKAGE),"coverage":package["coverage"]},
        "reference_frontier":refs,"package_obligations":obligations,"note_dispositions":notes,
        "material_assertions":assertions,"additional_frontier":frontier,
        "retrospective_supplement":"retrospective-segment-readings.json",
        "network_evidence":[evidence(n) for n in ["apple-statement-network-20261013","apple-interim-network-20261013","apple-history-compatibility-20261013","apple-coupled-completion-20261013","apple-settlement-paths-20261013"]],
        "separate_company_and_clock_evidence":[evidence(n) for n in ["apple-annual-filing-events-20261012","publication-frontier-20261013","jpmorgan-subsidiary-guarantees-20261011","jpmorgan-funds-transfer-20261012","jpmorgan-filing-events-20261013"]]}
    (OUT/"connected-package-map.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
    report=["# Connected Apple package and unresolved queries", "", "This is a dated supplement to the frozen inventory. Original statuses remain evidence of the earlier inquiry. Linked results carry their original scopes; a complete note reading is not complete semantic formalisation.", "", "## All 23 note dispositions", "", "| Note / original assertion IDs | Latest evidence | Remaining facts and affected query | Next supported route |", "|---|---|---|---|"]
    for row in notes:
        links="; ".join(f"[{Path(e['path']).parent.name}](../../{Path(e['path']).parent.name}/result.md)" for e in row["latest_evidence"])
        report.append(f"| {row['id']} ({', '.join(row['frozen_assertion_ids'])}) | {links} | {row['remaining_facts']} {row['affected_query']} | {row['next_supported_route']} |")
    report += ["", "## All seven package obligations", "", "| Obligation | Preserved status | Query / remaining facts | Route |", "|---|---|---|---|"]
    for row in obligations:
        report.append(f"| {row['id']} | {row['frozen_status']} | {row['affected_query']} {row['remaining_facts']} | {row['next_supported_route']} |")
    report += ["", "## All 70 reference rows", "", "The JSON companion binds each exact description and target URI to the affected query, missing facts, later evidence and route. The groups below are navigation aids, not new semantic statuses.", "", "| Reference | Frozen document status | Query group | Supplemental counterpart |", "|---|---|---|---|"]
    for row in refs:
        report.append(f"| {row['id']} | {row['frozen_document_status']} | {row['group']} | {row['counterpart_in_stock_plan_inquiry'] or 'No new counterpart asserted in this consolidation'} |")
    (OUT/"connected-package-map.md").write_text("\n".join(report)+"\n")
    populations={"reference_frontier":70,"package_obligations":7,"note_dispositions":23,"material_assertions":32,"additional_frontier":7}
    for key,count in populations.items():
        assert len(doc[key])==count
    assert len({r["id"] for r in refs})==70
    assert sum(r["frozen_document_status"]=="unresolved_target" for r in refs)==40
    assert sum(r["counterpart_in_stock_plan_inquiry"] is not None for r in refs)==3
    assert {r["id"] for r in assertions}=={a for n in notes for a in n["frozen_assertion_ids"]}
    (OUT/"package-map-checks.json").write_text(json.dumps({"populations":populations,"unique_reference_ids":70,"frozen_unresolved_population":40,"stock_plan_counterparts":3,"historical_inquiry_remainder":37,"assertion_note_links_match":True,"recursive_reference_closure":False,"semantic_completion":False,"wall_seconds":time.perf_counter()-started},indent=2)+"\n")
    print(json.dumps({"mapped_populations":populations,"checks":"passed","full_semantic_closure":False}))


if __name__=="__main__":
    main()
