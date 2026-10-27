"""Identity-preserving documentary join; standard library only, no model execution."""
import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = "data/accounting-master/"
CORPUS = "data/financial-report-benchmark/"
PILOT = "docs/design/proposal/methods/preparation-20261005-v1/04-annotation/"
COVERAGE = CORPUS + "coverage.json"
PANEL = CORPUS + "target-panel-v2.json"
QA = CORPUS + "source-evidence.json"
PROTOCOL = CORPUS + "benchmark-protocol-v1.json"
INVENTORY = BASE + "publication-evidence-20261011/selected-date-inventory.json"
EVENTS = BASE + "publication-evidence-20261011/filing-events.json"
ALTERNATES = BASE + "publication-evidence-20261011/dated-alternate-sources.json"
MUNICH = BASE + "munich-publication-imprints-20261012/date-evidence.json"
HENKEL = BASE + "publication-frontier-20261013/henkel-date-evidence.json"
HSBC = BASE + "publication-frontier-20261013/hsbc-date-evidence.json"
LABELS = PILOT + "labels-v1.json"
SELECTION = PILOT + "selection.json"
SEMANTIC = BASE + "accounting-package-semantic-annotation-20261011/annotations.json"
PLAN = "docs/plans/accounting-r05-vintage-admission-20261018.md"
PDF = "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"
INTEGRATION = BASE + "early-conversion-integration-20261018/"
CONTROLS = [
    "docs/plans/accounting-master-current.md",
    "docs/plans/accounting-master-checkpoint.md",
    "data/accounting-master/next-plan.md",
    "docs/plans/accounting-mission-requirements.md",
]
FROZEN = {
    PDF: "afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80",
    INTEGRATION + "assessment-successor.json": "37ce6cae6d860bc05be31459b997f35b5ac8f2f12bd0aea3e295f4fab90ddb50",
    INTEGRATION + "integration-bindings.json": "33dd3b29449a35975747b5e238ca9d6b515df9107ce74f42a1db968da3f8cc1a",
    INTEGRATION + "operation-successor.json": "81ae6c695494f33ecc570c25f84a5c5247ca4d75e74e744cf76a7f1ec94d3626",
}
INPUTS = [
    COVERAGE, PANEL, QA, PROTOCOL, INVENTORY, EVENTS, ALTERNATES,
    MUNICH, HENKEL, HSBC, LABELS, SELECTION, SEMANTIC,
    PILOT + "RESULT.md", PILOT + "verification.json",
    BASE + "future-validation-20261015/protocol-ledger.md",
    BASE + "future-validation-20261015/source-reading.md",
    BASE + "source-protocol-reuse-refresh-20261016/protocol-successor.md",
    BASE + "protocol-delta-refresh-20261018/protocol-supplement.md",
    BASE + "protocol-delta-refresh-20261018/bindings.json",
    BASE + "r06-duty-reconciliation-20261018/run-manifest.json", PLAN,
] + list(FROZEN)
HISTORICAL = ["munich-publication-imprints-20261012", "publication-frontier-20261013"]


def load(path):
    return json.loads((ROOT / path).read_bytes())


def digest(path):
    h = hashlib.sha256()
    with (ROOT / path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def binding(path):
    return {"path": path, "sha256": digest(path)}


def pointer(document, ptr):
    for token in ptr.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def escaped(key):
    return key.replace("~", "~0").replace("/", "~1")


def construct():
    data = {p: load(p) for p in [
        COVERAGE, PANEL, QA, PROTOCOL, INVENTORY, EVENTS, ALTERNATES,
        MUNICH, HENKEL, HSBC, LABELS, SELECTION, SEMANTIC,
    ]}
    sources = {p: binding(p) for p in INPUTS}

    def retain(path, expected=None):
        if path not in sources:
            sources[path] = binding(path)
        if expected is not None and sources[path]["sha256"] != expected:
            raise ValueError("source hash mismatch: " + path)

    def evidence(path, ptr):
        return {
            "source": {**sources[path], "json_pointer": ptr},
            "record": copy.deepcopy(pointer(data[path], ptr)),
        }

    def indexed(path, list_ptr=""):
        records = pointer(data[path], list_ptr)
        return {r["document_id"]: evidence(path, list_ptr + "/" + str(i))
                for i, r in enumerate(records)}

    for folder in HISTORICAL:
        prefix = BASE + folder + "/"
        completion = load(prefix + "completion.json")
        retain(prefix + "completion.json")
        retain(prefix + "run-manifest.json", completion["manifest_sha256"])
        for path, expected in load(prefix + "run-manifest.json")["artifact_hashes"].items():
            retain(path, expected)
    for path, expected in FROZEN.items():
        retain(path, expected)

    inventories = indexed(INVENTORY)
    events = indexed(EVENTS)
    alternates = indexed(ALTERNATES)
    selections = indexed(SELECTION, "/records")
    declarations = {}
    for path in [MUNICH, HENKEL, HSBC]:
        for key, item in indexed(path, "/primary").items():
            declarations.setdefault(key, []).append(item)
    exclusions = {}
    for path, ptr in [
        (MUNICH, "/excluded_candidate"),
        (HSBC, "/excluded/0"),
        *[(MUNICH, "/other_date_roles/" + str(i)) for i in range(3)],
    ]:
        item = evidence(path, ptr)
        exclusions.setdefault(item["record"]["document_id"], []).append(item)
    labels = {}
    for i, label in enumerate(data[LABELS]):
        labels.setdefault(label["document_id"], []).append(evidence(LABELS, "/" + str(i)))
    semantic = {}
    for i, package in enumerate(data[SEMANTIC]["packages"]):
        year = package["year"]
        actual = package["roles"]["complete_issuer_10k"]
        retain(actual["path"], actual["sha256"])
        quotes = []
        for j, quote in enumerate(data[SEMANTIC]["quotes"]):
            if quote["year"] != year:
                continue
            quotes.append(evidence(SEMANTIC, "/quotes/" + str(j)))
            retain(quote["source_text"], quote["source_text_sha256"])
            retain(quote["original_layout_text"], quote["original_layout_sha256"])
        semantic["jpmorgan-" + str(year) + "-annual"] = {
            "scope": "issuer_family_complete_10k_source",
            "package": evidence(SEMANTIC, "/packages/" + str(i)),
            "exposed_source": copy.deepcopy(actual),
            "exact_selected_byte_annotations": False,
            "assertions": [evidence(SEMANTIC, "/assertions/" + str(j))
                           for j, a in enumerate(data[SEMANTIC]["assertions"]) if a["year"] == year],
            "quotes": quotes,
            "label_status": "author_review_only_not_independent_gold",
        }
    rows = []
    for i, selected in enumerate(data[COVERAGE]["rows"]):
        key, issuer = selected["document_id"], selected["issuer_id"]
        retain(selected["local_path"], selected["sha256"])
        retain(selected["extracted_text_path"])
        filing = [events[key]] if key in events else []
        for item in filing:
            event = item["record"]
            retain(event["filing_event"]["source_path"], event["filing_event"]["source_sha256"])
            retain(event["retained_text"]["path"], event["retained_text"]["sha256"])
        rows.append({
            "document_id": key, "issuer_id": issuer,
            "active_coverage": evidence(COVERAGE, "/rows/" + str(i)),
            "selected": {"path": selected["local_path"], "sha256": selected["sha256"],
                         "source_url": selected["source_url"]},
            "frozen_date_metadata": inventories[key],
            "official_filing_events": filing,
            "attributed_publication_declarations": declarations.get(key, []),
            "alternate_source_date_candidates": [alternates[key]] if key in alternates else [],
            "other_or_excluded_date_roles": exclusions.get(key, []),
            "known_exposure": {
                "scope": "nonexhaustive_lower_bound_no_absence_inference",
                "acquisition_qa": {
                    "source": {**sources[QA], "json_pointer": "/documents/" + escaped(key)},
                    "document_id": key, "path": data[QA]["documents"][key]["local_path"],
                    "sha256": data[QA]["documents"][key]["sha256"],
                    "status": "source_acquisition_and_qa_not_semantic_gold",
                },
                "pilot_selection": selections.get(key),
                "pilot_annotations": labels.get(key, []),
                "pilot_label_status": "author_development_answers_not_independent_gold",
                "publication_reading_sources": [d["source"] for d in declarations.get(key, [])],
                "filing_event_check_sources": [d["source"] for d in filing],
                "complete_issuer_semantic": semantic.get(key),
            },
            "family_role": {
                "source": {**sources[PROTOCOL],
                           "json_pointer": "/provisional_issuer_family_roles/" + escaped(issuer)},
                "value": data[PROTOCOL]["provisional_issuer_family_roles"][issuer],
                "split_status": data[PROTOCOL]["split_status"], "promoted": False,
            },
            "selected_byte_available_at": None, "as_of_admission": False,
            "untouched_model_or_test_status": "not_established",
        })
    families = []
    for issuer in sorted({r["issuer_id"] for r in rows}):
        group = [r for r in rows if r["issuer_id"] == issuer]
        families.append({
            "issuer_id": issuer, "selected_reports": len(group),
            "provisional_role": data[PROTOCOL]["provisional_issuer_family_roles"][issuer],
            "acquisition_qa_exposed": True, "untouched_test_admitted": False,
            "pilot_reports": [r["document_id"] for r in group if r["known_exposure"]["pilot_annotations"]],
            "declaration_reports": [r["document_id"] for r in group if r["attributed_publication_declarations"]],
            "filing_event_reports": [r["document_id"] for r in group if r["official_filing_events"]],
            "complete_10k_semantic_reports": [r["document_id"] for r in group
                                             if r["known_exposure"]["complete_issuer_semantic"]],
            "scope": "nonexhaustive; keep mirrors, amendments and all years in the issuer family",
        })
    frozen = {r["document_id"] for r in rows if r["frozen_date_metadata"]["record"]["selected_date"]}
    event_set, pub_set = set(events), set(declarations)
    summary = {
        "active_reports": len(rows), "source_registry_reports": len(data[QA]["documents"]),
        "excluded_registry_reports": sorted(set(data[QA]["documents"]) - {r["document_id"] for r in rows}),
        "frozen_with_filing_metadata": len(frozen), "frozen_unverified_date": len(rows) - len(frozen),
        "official_filing_event_reports": len(event_set), "publication_declaration_reports": len(pub_set),
        "date_role_pair_overlaps": {"metadata_event": len(frozen & event_set),
                                    "metadata_declaration": len(frozen & pub_set),
                                    "event_declaration": len(event_set & pub_set)},
        "any_of_three_selected_source_date_roles": len(frozen | event_set | pub_set),
        "none_of_three_selected_source_date_roles": len(rows) - len(frozen | event_set | pub_set),
        "alternate_source_candidate_reports": len(alternates),
        "selected_byte_availability_admissions": 0,
        "pilot_annotations": sum(len(x) for x in labels.values()),
        "pilot_reports": len(labels),
        "complete_10k_semantic_assertions": sum(len(s["assertions"]) for s in semantic.values()),
        "complete_10k_semantic_reports": len(semantic),
        "independently_adjudicated_gold_labels_established": False,
        "issuer_families": len(families), "untouched_test_families_established": 0,
    }
    document = {
        "schema_version": 1, "scope": "documentary_internal_preparation_no_empirical_admission",
        "date_role_policy": "metadata, filing events and attributed declarations stay distinct; no selected-byte vintage transfer",
        "exposure_policy": "nonexhaustive lower bound; no absence, clean-test or independent-label inference",
        "summary": summary, "families": families, "rows": rows,
    }
    return document, data, [sources[p] for p in sorted(sources)]
