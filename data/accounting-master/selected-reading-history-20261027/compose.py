"""SelectedReadingHistoryAttachment/1: explicit, provisional source composition.

The exact original source parent is retained. No actual history or opening
is inferred, and the older network/history interface is not modified.
"""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import retained_network_history_v1 as native

core = native.core
PROFILE = "SelectedReadingHistoryAttachment/1"
BOUNDARY = {
    **native.BOUNDARY,
    "scope": "one_selected_source_reading_and_supplied_context_histories",
    "actual_history": "unknown",
    "executable_opening": None,
    "whole_statement_history_complete": False,
}
PINS = {
    "scripts/retained_network_history_v1.py": "ea3f245ea30cf5b93a52ecba40c438fda16af835a8560b2f98418719f394b432",
    "scripts/typed_history_measurement_attachment_v1.py": "e510add72b6b0fe355f9b22c9f73f5d0451146312a66b5aad6791c60bd81abcd",
    "scripts/temporal_measurement_constraints_v1.py": "bfd2311c2142614d6726a7748c7f3e1c4bf0e7f516a462678d570b479fd75229",
    "data/accounting-master/debt-reading-network-20261027/compose.py": "06f7ab0f289736397097192c4dc7663bac74e84122b3b209a00095fdf9f54d68",
}


def source_module():
    for name, expected in PINS.items():
        core.need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                  "dependency_hash:" + name)
    path = ROOT / "data/accounting-master/debt-reading-network-20261027/compose.py"
    spec = importlib.util.spec_from_file_location("selected_history_source_reading", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


def prepare(body):
    source = source_module()
    core.closed(body, ["profile", "source_parent", "reading", "rounding", "histories", "budget"],
                "selected_reading_history_request")
    core.need(body["profile"] == PROFILE, "profile")
    selected = source.prepare(body["source_parent"], body["reading"], body["rounding"])
    if selected["status"] != "prepared":
        return selected, None
    histories = body["histories"]
    core.need(type(histories) is dict and bool(histories), "histories")
    # The source parent is an exact separately locked record; this existing
    # native bound applies to newly supplied histories, not a truncated parent.
    core.need(len(core.canonical(histories)) <= core.MAX_BYTES, "history_request_size_limit")
    for row in histories.values():
        core.closed(row, ["history", "bindings"], "supplied_history")
        core.need(type(row["bindings"]) is dict, "bindings")
    definitions = native.definitions({"histories": histories}, selected)
    return selected, definitions


def assess(body):
    try:
        selected, definitions = prepare(body)
        common = {
            "profile": PROFILE, **BOUNDARY,
            "request_sha256": core.digest(body),
            "budget": deepcopy(body["budget"]),
            "selected_source": selected,
            "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "dependency_sha256": deepcopy(PINS),
        }
        if definitions is None:
            return {**common, "status": "unresolved", "reason": selected["reason"],
                    "attachments": {}, "history_assessment_started": False}
        results = {key: native.attachment.assess(definition, body["budget"])
                   for key, definition in definitions.items()}
        statuses = [row["status"] for row in results.values()]
        if "invalid" in statuses:
            status = "invalid_history_attachment"
        elif "conditionally_infeasible" in statuses:
            status = "supplied_history_incompatible"
        elif "unresolved" in statuses:
            status = "unresolved"
        elif any(s in ["unknown", "unsupported"] for s in statuses):
            status = "unknown"
        else:
            status = "conditional_candidates_with_unresolved_facts"
        return {
            **common, "status": status, "attachments": results,
            "history_assessment_started": True,
            "selected_observations": len(selected["definition"]["observations"]),
            "selected_relations": len(selected["definition"]["relations"]),
            "context_count": len(results),
            "interpretation": "Each source context constrains its supplied history; unmapped measurements and actual-history obligations remain. No cross-context history or executable opening is supplied.",
        }
    except (ValueError, TypeError, KeyError, AttributeError, OSError,
            RecursionError, OverflowError) as exc:
        return {"profile": PROFILE, **BOUNDARY, "status": "invalid", "reason": str(exc)[:350]}
