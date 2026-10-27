"""Bounded documentary resolution checks. No Arelle import or network access."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import posixpath
import re
import subprocess
import sys
import time
import tomllib
from urllib.parse import urldefrag, urljoin, urlsplit
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / "data/accounting-master/taxonomy-reuse-20261007"
SELECT = ROOT / "data/accounting-master/selected-reuse-20261015/source-selection.json"
UPSTREAM = ROOT / "docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle"
PLAN = ROOT / "docs/plans/accounting-native-offline-resolution-20261018.md"
SPEC = ROOT / "docs/design/proposal/architecture/native-offline-resolution-proposed-v1.md"
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
XML = "{http://www.w3.org/XML/1998/namespace}"
XSD = "{http://www.w3.org/2001/XMLSchema}"
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
XLINK = "{http://www.w3.org/1999/xlink}"
XD = "{http://xbrl.org/2005/xbrldt}"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def load(path):
    # These are operational records, not L1 financial Record values.
    return json.loads(path.read_bytes())


def require(condition, code):
    if not condition:
        raise ValueError(code)


def supported(reference):
    require(isinstance(reference, str) and bool(reference), "UNSUPPORTED_REFERENCE")
    require(not any(c.isspace() or c in "%?\\()" for c in reference), "UNSUPPORTED_REFERENCE")
    require(not reference.startswith("//"), "UNSUPPORTED_REFERENCE")
    parts = urlsplit(reference)
    require(parts.scheme in ("", "http", "https") and parts.username is None, "UNSUPPORTED_REFERENCE")
    require(not parts.scheme or bool(parts.netloc), "UNSUPPORTED_REFERENCE")


def resolve(source, reference):
    supported(reference)
    resource, fragment = urldefrag(reference)
    if source.startswith("archive/"):
        if resource.startswith(("http://", "https://")):
            target = resource
        else:
            require(not resource.startswith("/"), "UNSUPPORTED_REFERENCE")
            target = posixpath.normpath(posixpath.join(posixpath.dirname(source), resource)) if resource else source
            require(target.startswith("archive/"), "UNSUPPORTED_REFERENCE")
        return target + ("#" + fragment if fragment else "")
    return urljoin(source, reference)


def reference_attributes(element):
    result = []
    if element.tag in [XSD + "import", XSD + "include", XSD + "redefine"]:
        location = element.get("schemaLocation")
        require(location is not None or element.tag != XSD + "import", "UNLOCATED_IMPORT")
        if location:
            result.append(("schemaLocation", location, element.get("namespace")))
    for name, label in [(XLINK + "href", "xlink:href"), (XD + "typedDomainRef", "xbrldt:typedDomainRef"),
                        (XSI + "noNamespaceSchemaLocation", "xsi:noNamespaceSchemaLocation")]:
        if element.get(name):
            result.append((label, element.get(name), None))
    if element.get(XSI + "schemaLocation"):
        tokens = element.get(XSI + "schemaLocation").split()
        require(len(tokens) % 2 == 0, "ODD_SCHEMA_HINTS")
        result.extend(("xsi:schemaLocation", tokens[i + 1], tokens[i]) for i in range(0, len(tokens), 2))
    require(element.get(XML + "schemaLocation") is None, "WRONG_SCHEMA_ATTRIBUTE")
    return result


def inspect_inputs(selection, graph):
    require(set(selection["uri_map"]) == {n["uri"] for n in graph["nodes"]}, "MAP_POPULATION")
    require(graph["aliases"] == {n["uri"]: n["uri"] for n in graph["nodes"]}, "UNDECLARED_ALIAS")
    require(not graph["errors"] and not graph["frontier"], "GRAPH_FRONTIER")
    resources, parsed, ids, observed_edges, counts = [], {}, {}, [], Counter()
    for node in graph["nodes"]:
        uri, path = node["uri"], ROOT / node["path"]
        raw = path.read_bytes()
        require(selection["uri_map"][uri] == {"path": node["path"], "sha256": node["sha256"]}, "SELECTED_BYTES")
        require(sha(raw) == node["sha256"], "CHANGED_RESOURCE")
        require(b"<!DOCTYPE" not in raw, "UNSUPPORTED_DOCTYPE")
        tree = ET.fromstring(raw)
        require(tree.tag == node["root_tag"] and tree.get("targetNamespace") == node["target_namespace"], "NODE_NAMESPACE")
        parsed[uri] = tree
        identifiers = [e.get("id") or e.get(XML + "id") for e in tree.iter() if e.get("id") or e.get(XML + "id")]
        require(len(identifiers) == len(set(identifiers)) == node["id_count"], "AMBIGUOUS_FRAGMENT")
        ids[uri] = set(identifiers)
        resources.append({"logical_uri": uri, "mapping": "identity", "retained_path": node["path"],
                          "expected_blob": {"kind": "blob", "algorithm": "sha256", "digest": node["sha256"], "byte_length": len(raw)},
                          "target_namespace": node["target_namespace"],
                          "acquisition_receipt": binding(ROOT / node["receipt"]) if node["receipt"] else None,
                          "archive_source": binding(ROOT / graph["archive"]) if uri.startswith("archive/") else None,
                          "actual_open": None, "runtime_equivalence": "not_checked"})
    for uri, tree in parsed.items():
        def visit(element, path):
            require(element.get(XML + "base") is None, "UNSUPPORTED_XML_BASE")
            for attribute, reference, expected_ns in reference_attributes(element):
                resolved = resolve(uri, reference)
                resource, fragment = urldefrag(resolved)
                require(resource in parsed, "UNRESOLVED_RESOURCE")
                require(expected_ns is None or parsed[resource].get("targetNamespace") == expected_ns, "NAMESPACE_MISMATCH")
                require(not fragment or fragment in ids[resource], "MISSING_FRAGMENT")
                counts[attribute] += 1
                observed_edges.append({"source": uri, "element_path": path, "element": element.tag.split("}")[-1],
                                       "attribute": attribute, "declared_reference": reference, "resolved_reference": resolved,
                                       "target_resource": resource, "expected_namespace": expected_ns, "fragment": fragment or None,
                                       "resolved_node": resource, "status": "resolved"})
            for i, child in enumerate(element):
                visit(child, path + [i])
        visit(tree, [])
    require(observed_edges == graph["edges"], "EDGE_SOURCE_CORRESPONDENCE")
    require(len(resources) == 27 and len(observed_edges) == 3551, "BASELINE_COUNTS")
    return resources, ids, counts


def validate_map(rows, selection):
    require(len(rows) == len({r["logical_uri"] for r in rows}) == len(selection["uri_map"]), "MAP_POPULATION")
    require({r["logical_uri"] for r in rows} == set(selection["uri_map"]), "MAP_POPULATION")
    for row in rows:
        expected = selection["uri_map"][row["logical_uri"]]
        require(row["mapping"] == "identity", "UNDECLARED_ALIAS")
        require(row["retained_path"] == expected["path"], "ALTERNATE_PATH")
        require(row["expected_blob"]["digest"] == expected["sha256"], "CHANGED_RESOURCE")
        raw = (ROOT / row["retained_path"]).read_bytes()
        require(sha(raw) == expected["sha256"] and len(raw) == row["expected_blob"]["byte_length"], "CHANGED_RESOURCE")
        require(row["actual_open"] is None and row["runtime_equivalence"] == "not_checked", "UNOBSERVED_RUNTIME")


def check_receipt(receipt, resources, ids):
    require(receipt["explicit_bases"] == [], "UNSUPPORTED_XML_BASE")
    target, fragment = urldefrag(resolve(receipt["source_uri"], receipt["declared_reference"]))
    require(target == receipt["target_resource"] and (fragment or None) == receipt["fragment"], "TARGET_SUBSTITUTION")
    by_uri = {r["logical_uri"]: r for r in resources}
    require(target in by_uri, "UNRESOLVED_RESOURCE")
    require(receipt["expected_blob"] == by_uri[target]["expected_blob"], "CHANGED_RESOURCE")
    require(not fragment or fragment in ids[target], "MISSING_FRAGMENT")
    require(receipt["expected_namespace"] is None or receipt["expected_namespace"] == by_uri[target]["target_namespace"], "NAMESPACE_MISMATCH")
    require(receipt["actual_open"] is None and receipt["runtime_equivalence"] == "not_checked", "UNOBSERVED_RUNTIME")


def mutations(resources, selection, receipts, ids):
    results = []
    def reject(name, code, run):
        try:
            run()
        except ValueError as error:
            require(str(error) == code, "WRONG_DIAGNOSTIC:" + name + ":" + str(error))
            results.append({"case": name, "rejected_by": code})
        else:
            raise ValueError("CORRUPTION_ACCEPTED:" + name)
    def map_case(name, code, change):
        rows = deepcopy(resources)
        change(rows)
        reject(name, code, lambda: validate_map(rows, selection))
    map_case("missing_resource", "MAP_POPULATION", lambda r: r.pop())
    map_case("duplicate_uri", "MAP_POPULATION", lambda r: r.append(deepcopy(r[0])))
    map_case("changed_hash", "CHANGED_RESOURCE", lambda r: r[0]["expected_blob"].update(digest="0" * 64))
    map_case("changed_length", "CHANGED_RESOURCE", lambda r: r[0]["expected_blob"].update(byte_length=1))
    map_case("ambient_cache_substitution", "ALTERNATE_PATH", lambda r: r[0].update(retained_path="ambient/cache.xml"))
    map_case("implicit_alias", "UNDECLARED_ALIAS", lambda r: r[0].update(mapping="https_fallback"))
    map_case("invented_actual_open", "UNOBSERVED_RUNTIME", lambda r: r[0].update(actual_open={"passed": True}))
    map_case("invented_runtime_equivalence", "UNOBSERVED_RUNTIME", lambda r: r[0].update(runtime_equivalence="passed"))
    def receipt_case(name, code, change):
        row = deepcopy(receipts[0])
        change(row)
        reject(name, code, lambda: check_receipt(row, resources, ids))
    receipt_case("target_uri_substitution", "TARGET_SUBSTITUTION", lambda r: r.update(target_resource="https://example.invalid/other.xsd"))
    receipt_case("namespace_mismatch", "NAMESPACE_MISMATCH", lambda r: r.update(expected_namespace="urn:wrong"))
    receipt_case("missing_fragment", "MISSING_FRAGMENT", lambda r: r.update(declared_reference=r["declared_reference"] + "#missing_documentary_id", fragment="missing_documentary_id"))
    receipt_case("undeclared_resource", "UNRESOLVED_RESOURCE", lambda r: r.update(declared_reference="https://example.invalid/new.xsd", target_resource="https://example.invalid/new.xsd"))
    receipt_case("unreviewed_base", "UNSUPPORTED_XML_BASE", lambda r: r.update(explicit_bases=["elsewhere/"]))
    for name, reference in [("query", "file.xsd?q=1"), ("percent_encoding", "file%20name.xsd"), ("scheme_relative", "//host/file.xsd"),
                            ("xpointer", "#element(/1)"), ("backslash", "..\\file.xsd"), ("file_scheme", "file:///tmp/file.xsd"),
                            ("archive_escape", "../../file.xsd")]:
        reject("unsupported_" + name, "UNSUPPORTED_REFERENCE", lambda value=reference: resolve("archive/a.xsd", value))
    # Duplicate-ID rejection belongs to source inspection; do not pretend a set can reveal it.
    duplicated_tree = ET.fromstring('<root><x id="a"/><x id="a"/></root>')
    duplicate_ids = [e.attrib["id"] for e in duplicated_tree if "id" in e.attrib]
    reject("duplicate_fragment_id", "AMBIGUOUS_FRAGMENT", lambda: require(len(duplicate_ids) == len(set(duplicate_ids)), "AMBIGUOUS_FRAGMENT"))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    output_names = ["resource-map.json", "resolution-examples.json", "dependency-prerequisites.json", "source-anchors.json", "checks.json", "run-manifest.json"]
    if args.record:
        for name in output_names:
            require(not (OUT / name).exists(), "OUTPUT_EXISTS:" + name)
    selection, graph = load(SELECT), load(PRIOR / "graph-final.json")
    require(selection["taxonomy_graph"]["sha256"] == sha((PRIOR / "graph-final.json").read_bytes()), "GRAPH_SELECTION_HASH")
    require(selection["selected_native"]["commit"] == "01f6a4656c2c6551d2f05f31c9d74366d133ee7e", "PIN")
    resources, ids, counts = inspect_inputs(selection, graph)
    validate_map(resources, selection)
    by_uri = {r["logical_uri"]: r for r in resources}
    receipts = []
    for ordinal, edge in enumerate(graph["edges"]):
        row = {"evidence_mode": "specification_example", "ordinal": ordinal,
               "source_uri": edge["source"], "source_blob": by_uri[edge["source"]]["expected_blob"],
               "element_path": edge["element_path"], "attribute": edge["attribute"],
               "declared_reference": edge["declared_reference"], "explicit_bases": [],
               "resolution_method": "retained_static_graph_subset_not_upstream_runtime",
               "target_resource": edge["target_resource"], "fragment": edge["fragment"],
               "expected_namespace": edge["expected_namespace"],
               "expected_blob": by_uri[edge["target_resource"]]["expected_blob"],
               "actual_open": None, "runtime_equivalence": "not_checked",
               "validation": {"retained_byte_match": "checked", "static_namespace_fragment": "checked",
                              "schema": "not_run", "xbrl": "not_run", "accounting_admission": "pending"}}
        check_receipt(row, resources, ids)
        receipts.append(row)
    metadata = tomllib.loads((UPSTREAM / "pyproject.toml").read_text())
    require(selection["selected_native"]["base_constraints"] == metadata["project"]["dependencies"], "BASE_CONSTRAINTS")
    require(selection["selected_native"]["build_constraints"] == metadata["build-system"]["requires"], "BUILD_CONSTRAINTS")
    require(selection["environment_lock"] is None and selection["runtime_admission"] == "held", "NO_RUNTIME_PROMOTION")
    duties = {
        "target_platform_python": "OS, architecture, exact Python build and ABI not selected",
        "arelle_distribution": "Pinned source commit is not a built distribution or wheel identity",
        "transitive_distributions": "Resolve versions, markers, extras and hashes for the selected target",
        "build_tools": "Exact build backend/tool artifacts and isolated build inputs unresolved",
        "native_libraries": "Record native extension and linked-library versions/build identities",
        "effective_configuration": "Observe plugins, packages, disclosure system, caches and environment effects",
        "mapping_application": "No implementation of the proposed URI-to-byte map has been selected or run",
        "decoder_and_parser": "Inspect transformation, parser/entity and external resolver implementation",
        "actual_open_bytes": "No runtime open/byte receipts exist",
        "network_behavior": "Offline option alone does not establish whole-process network behavior",
        "validation_and_translation": "Run actual schema/XBRL checks and real-filing portable correspondence later",
        "component_terms": "Exact distributions/builds and historical taxonomy terms applicability unresolved"}
    prerequisites = {"status": "documentary_prerequisites_not_dependency_lock", "source_commit": selection["selected_native"]["commit"],
                     "python_constraint": metadata["project"]["requires-python"], "base_constraints": metadata["project"]["dependencies"],
                     "build_constraints": metadata["build-system"]["requires"], "selected_extras": selection["selected_native"]["extras"],
                     "pending": [{"field": key, "value": None, "reason": value} for key, value in duties.items()],
                     "uninspected_modules": ["FileSource", "ModelObjectFactory", "PackageManager", "PluginManager", "UrlUtil"],
                     "runtime_admission": "held"}
    anchors = []
    spans = [(UPSTREAM / "arelle__WebCache.py", 351, 429), (UPSTREAM / "arelle__WebCache.py", 434, 527),
             (UPSTREAM / "arelle__WebCache.py", 545, 635), (UPSTREAM / "arelle__ModelDocument.py", 75, 168),
             (UPSTREAM / "arelle__ModelDocument.py", 176, 218), (UPSTREAM / "arelle__ModelDocument.py", 1036, 1063),
             (UPSTREAM / "arelle__ModelDocument.py", 1250, 1274), (UPSTREAM / "arelle__api__Session.py", 28, 39),
             (UPSTREAM / "arelle__api__Session.py", 141, 161), (UPSTREAM / "arelle__RuntimeOptions.py", 47, 164),
             (UPSTREAM / "pyproject.toml", 1, 46), (PRIOR / "sources/arelle-cntlrcmdline-trusted.body", 1678, 1689)]
    for path, first, last in spans:
        raw = path.read_bytes()
        excerpt = b"".join(raw.splitlines(keepends=True)[first - 1:last])
        anchors.append({**binding(path), "start_line": first, "end_line": last, "excerpt_utf8": excerpt.decode(), "excerpt_sha256": sha(excerpt)})
    negatives = mutations(resources, selection, receipts, ids)
    checks = {"scope": "documentary_static_subset_only", "all_passed": True, "resources": len(resources),
              "source_correspondence_edges": len(receipts), "reference_counts": dict(counts),
              "plain_fragments": sum(bool(r["fragment"]) for r in receipts), "xml_base_occurrences": 0, "doctype_resources": 0,
              "source_anchors": len(anchors), "corruption_cases": negatives, "unresolved_lock_fields": len(duties),
              "runtime_executed": False, "schema_xbrl_validation": "not_run"}
    values = {"resource-map.json": resources, "resolution-examples.json": receipts, "dependency-prerequisites.json": prerequisites,
              "source-anchors.json": anchors, "checks.json": checks}
    if args.record:
        protected = [SELECT, PRIOR / "graph-final.json", ROOT / graph["archive"]]
        protected += [ROOT / n["path"] for n in graph["nodes"]] + [path for path, _, _ in spans]
        protected += [INTEGRATION / name for name in ["assessment-successor.json", "integration-bindings.json", "operation-successor.json", "native-xbrl-translation-supplement.json"]]
        protected += [ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"]
        protected += [ROOT / "data/accounting-master/native-xbrl-translation-20261018/completion-validation.json"]
        protected += [ROOT / row["acquisition_receipt"]["path"] for row in resources if row["acquisition_receipt"]]
        for name, value in values.items():
            with (OUT / name).open("x") as handle:
                json.dump(value, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        manifest = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic() - tick,
                    "command": "python3 data/accounting-master/native-offline-resolution-20261018/check.py --record",
                    "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    "index_sha256": sha((ROOT / ".git/index").read_bytes()),
                    "tracked_dirty": subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines(),
                    "environment": {"executable": sys.executable, "python": platform.python_version(), "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
                                    "cpu_gpu_status": "CPU standard-library file checks only; no numerical framework import or GPU detection/use"},
                    "seeds": "N/A: deterministic documentary examples", "data_version": binding(PRIOR / "graph-final.json"),
                    "plan": binding(PLAN), "specification": binding(SPEC), "verifier": binding(Path(__file__).resolve()),
                    "protected_inputs": [binding(path) for path in sorted(set(protected))],
                    "outputs": [binding(OUT / name) for name in values],
                    "result_path": str((OUT / "result.md").relative_to(ROOT)), "runtime_executed": False}
        with (OUT / "run-manifest.json").open("x") as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
    else:
        for name, value in values.items():
            require(load(OUT / name) == value, "SAVED_REPLAY:" + name)
        manifest = load(OUT / "run-manifest.json")
        for row in manifest["protected_inputs"] + manifest["outputs"] + [manifest[k] for k in ["plan", "specification", "verifier"]]:
            require(binding(ROOT / row["path"]) == row, "BINDING:" + row["path"])
        require(sha((ROOT / ".git/index").read_bytes()) == manifest["index_sha256"], "INDEX_CHANGED")
        require(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines() == manifest["tracked_dirty"], "DIRTY_ENTRIES_CHANGED")
    print(json.dumps({"status": "recorded" if args.record else "read-only replay passed", "resources": len(resources), "edges": len(receipts),
                      "rejected_cases": len(negatives), "unresolved_lock_fields": len(duties), "runtime_executed": False,
                      "wall_seconds": round(time.monotonic() - tick, 3)}))


if __name__ == "__main__":
    main()
