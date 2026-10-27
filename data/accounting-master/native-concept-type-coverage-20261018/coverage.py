"""Construct the source-only fact/declaration/type correspondence."""
from collections import Counter
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from source_index import XS, anchor, digest, global_index, parse_source, qname, require, type_node

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
MASTER = ROOT / "data/accounting-master"
FULL = MASTER / "native-full-portable-20261018"
MAP = MASTER / "native-offline-resolution-20261018/resource-map.json"
PLAN = ROOT / "docs/plans/accounting-native-concept-type-coverage-20261018.md"
INSTANCE = MASTER / "taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml"


def load(path):
    return json.loads(path.read_bytes())


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def path_summary(nodes, start):
    terminals = set()
    problems = []

    def visit(name, trail):
        if name in trail:
            problems.append({"type": name, "reason": "cyclic_type_path"})
            return
        node = nodes[name]
        if node["status"] == "builtin_reference_only":
            terminals.add(name)
        elif node["status"] == "unresolved":
            problems.append({"type": name, "reason": node["reason"]})
        else:
            for edge in node["edges"]:
                visit(edge["target"], trail | {name})

    visit(start, set())
    return {"status": "unresolved" if problems else "resolved_to_terminal_references",
            "terminal_references": sorted(terminals), "unresolved": problems}


def construct():
    schemas = []
    protected = [MAP, FULL / "native-packet.json", FULL / "portable-records.json",
                 FULL / "completion.json", FULL / "run-manifest.json",
                 MASTER / "unitless-type-evidence-20261018/declarations.json",
                 MASTER / "unitless-type-evidence-20261018/completion.json",
                 MASTER / "r06-duty-reconciliation-20261018/reconciliation.json",
                 MASTER / "r06-duty-reconciliation-20261018/completion.json", PLAN, INSTANCE]
    for row in load(MAP):
        path = ROOT / row["retained_path"]
        raw = path.read_bytes()
        require(digest(raw) == row["expected_blob"]["digest"], "RESOURCE_HASH:" + str(path))
        require(len(raw) == row["expected_blob"]["byte_length"], "RESOURCE_LENGTH")
        protected.append(path)
        for name in ("acquisition_receipt", "archive_source"):
            if row[name] is not None:
                receipt = row[name]
                require(binding(ROOT / receipt["path"]) == receipt, "RECEIPT_HASH")
                protected.append(ROOT / receipt["path"])
        source = parse_source(raw, str(path.relative_to(ROOT)))
        if source["root"].tag == "{" + XS + "}schema":
            require(source["namespace"] == row["target_namespace"], "MAP_SCHEMA_NAMESPACE")
            schemas.append(source)
    index = global_index(schemas)
    packet = load(FULL / "native-packet.json")
    facts = packet["facts"]
    require(len(facts) == 1127 and len({f["id"] for f in facts}) == 1127, "SOURCE_OCCURRENCES")
    instance = ET.fromstring(INSTANCE.read_bytes())
    source_facts = {e.get("id"): e for e in instance if e.get("contextRef") is not None}
    require(len(source_facts) == 1127, "INSTANCE_FACT_COUNT")
    reported = {r["key"]: r["body"] for r in load(FULL / "portable-records.json")
                if r["kind"] == "ReportedAssertion"}
    require(len(reported) == 1127, "PORTABLE_FACT_COUNT")
    concepts = {}
    for name in sorted({f["expanded_concept"] for f in facts}):
        matches = index.get(("element", name), [])
        concept = {"concept": name, "candidate_count": len(matches)}
        if len(matches) != 1:
            concept.update(status="unresolved", reason="missing_declaration" if not matches else "ambiguous_declaration",
                           candidate_anchors=[anchor(s, e) for s, e in matches])
        else:
            source, element = matches[0]
            concept.update(declaration_anchor=anchor(source, element), source_attributes=dict(element.attrib))
            try:
                declared = qname(element.get("type"), source, element)
                concept.update(status="unique_explicit_type_declaration", declared_type=declared)
            except ValueError as error:
                concept.update(status="unresolved", reason="type_reference:" + str(error))
        concepts[name] = concept
    nodes = {}
    pending = {c["declared_type"] for c in concepts.values() if "declared_type" in c}
    while pending:
        name = min(pending)
        pending.remove(name)
        if name in nodes:
            continue
        node = type_node(index, name)
        nodes[name] = node
        pending.update(e["target"] for e in node["edges"] if e["target"] not in nodes)
    for concept in concepts.values():
        if "declared_type" in concept:
            concept["type_path"] = path_summary(nodes, concept["declared_type"])
    occurrences = []
    for fact in facts:
        original = source_facts[fact["id"]]
        require(original.tag == fact["expanded_concept"], "INSTANCE_CONCEPT:" + fact["id"])
        require(dict(original.attrib) == fact["source_attributes"], "INSTANCE_ATTRIBUTES:" + fact["id"])
        require(original.text == fact["decoded_text"], "INSTANCE_TEXT:" + fact["id"])
        value = reported["fact-" + fact["id"]]["value"]
        concept = concepts[fact["expanded_concept"]]
        occurrences.append({
            "fact_id": fact["id"], "source_concept": fact["expanded_concept"],
            "source_context_id": fact["source_context_id"], "source_unit_id": fact["source_unit_id"],
            "source_attributes": fact["source_attributes"], "decoded_text": fact["decoded_text"],
            "source_span": fact["span"], "packet_candidate_value": fact["candidate_value"],
            "portable_candidate_value": value, "lexical_class": fact["lexical_class"],
            "declaration_status": concept["status"],
            "type_path_status": concept.get("type_path", {}).get("status", "unresolved"),
            "validation_status": "not_run", "portable_value_mutated": False,
        })
    cross = Counter()
    for row in occurrences:
        concept = concepts[row["source_concept"]]
        terminal = "|".join(concept.get("type_path", {}).get("terminal_references", [])) or "UNRESOLVED"
        cross[(terminal, row["portable_candidate_value"]["tag"])] += 1
    counts = {
        "resources": len(load(MAP)), "retained_schema_roots": len(schemas), "fact_occurrences": len(occurrences),
        "distinct_concepts": len(concepts), "unique_explicit_declarations":
            sum(c["status"] == "unique_explicit_type_declaration" for c in concepts.values()),
        "unresolved_concepts": sum(c["status"] == "unresolved" for c in concepts.values()),
        "type_nodes": len(nodes),
        "resolved_type_paths": sum(c.get("type_path", {}).get("status") == "resolved_to_terminal_references" for c in concepts.values()),
        "unresolved_fact_paths": sum(r["type_path_status"] == "unresolved" for r in occurrences),
        "portable_value_tags": dict(sorted(Counter(r["portable_candidate_value"]["tag"] for r in occurrences).items())),
    }
    coverage = {
        "schema": "accdsl.native_concept_type_coverage.documentary.v1",
        "scope": "retained_declarations_and_type_references_only",
        "schema_inventory": [{"source": binding(ROOT / s["path"]), "target_namespace": s["namespace"],
                              "global_children": len(s["root"])} for s in schemas],
        "concepts": concepts, "type_nodes": nodes, "occurrences": occurrences,
        "terminal_reference_candidate_tag_counts": [
            {"terminal_references": k[0].split("|"), "portable_tag": k[1], "occurrences": v}
            for k, v in sorted(cross.items())],
        "counts": counts, "schema_xbrl_validation": "not_run", "upstream_executed": False,
        "runtime_admission": "held", "financial_admission": "not_established",
        "source_qualification": "Retained XBRL schema describes its copy as non-normative; asserted Appendix A equivalence is unverified. Terminal references are not built-in lexical/value-space validation.",
    }
    return coverage, [binding(p) for p in dict.fromkeys(protected)], schemas
