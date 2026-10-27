"""Source-only coverage: inspect first, record once, then replay read-only."""
import argparse
from datetime import datetime, timezone
import json
import platform
import subprocess
import sys
import time

from coverage import (FULL, MASTER, OUT, PLAN, ROOT, binding, construct, load, path_summary)
from source_index import XS, anchor, digest, global_index, parse_source, qname, require, type_node


def fixtures():
    raw = b'''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:t="urn:test" xmlns:p="urn:outer" targetNamespace="urn:test">
      <xs:element name="Scoped" xmlns:p="urn:inner" type="p:T" note="x>y"/>
      <xs:element name="Restored" type="p:T"/>
      <xs:complexType name="Container"><xs:sequence>
        <xs:element name="LocalOnly" type="xs:string"/>
      </xs:sequence></xs:complexType>
      <xs:simpleType name="A"><xs:restriction base="t:B"/></xs:simpleType>
      <xs:simpleType name="B"><xs:restriction base="t:A"/></xs:simpleType>
      <xs:simpleType name="Choice"><xs:union memberTypes="xs:date xs:dateTime"/></xs:simpleType>
      <xs:simpleType name="Many"><xs:list itemType="xs:token"/></xs:simpleType>
      <xs:complexType name="BaseScope"><xs:simpleContent>
        <xs:extension xmlns:p="urn:base" base="p:C"/>
      </xs:simpleContent></xs:complexType>
      <xs:element name="Ambiguous" type="xs:string"/>
      <xs:element name="Ambiguous" type="xs:token"/>
      <xs:element name="Unbound" type="absent:T"/>
      <xs:simpleType name="Inline"><xs:list><xs:simpleType>
        <xs:restriction base="xs:token"/>
      </xs:simpleType></xs:list></xs:simpleType>
    </xs:schema>'''
    source = parse_source(raw, "IN_MEMORY_FIXTURE")
    index = global_index([source])
    tests = []

    def check(label, condition):
        require(condition, "FIXTURE:" + label)
        tests.append(label)

    def element(name):
        return index[("element", "{urn:test}" + name)][0][1]

    check("per_element_prefix_rebinding", qname("p:T", source, element("Scoped")) == "{urn:inner}T")
    check("sibling_scope_restored", qname("p:T", source, element("Restored")) == "{urn:outer}T")
    check("local_declaration_does_not_satisfy_global_join", ("element", "{urn:test}LocalOnly") not in index)
    check("ambiguous_global_declaration_retained", len(index[("element", "{urn:test}Ambiguous")]) == 2)
    check("quoted_greater_than_in_self_closing_span",
          anchor(source, element("Scoped"))["text"].endswith('note="x>y"/>'))
    choice = type_node(index, "{urn:test}Choice")
    check("union_keeps_both_member_edges",
          [e["target"] for e in choice["edges"]] == ["{" + XS + "}date", "{" + XS + "}dateTime"])
    check("list_keeps_item_type", type_node(index, "{urn:test}Many")["edges"][0]["target"] == "{" + XS + "}token")
    check("base_attribute_uses_its_own_scope", type_node(index, "{urn:test}BaseScope")["edges"][0]["target"] == "{urn:base}C")
    nodes = {name: type_node(index, name) for name in ["{urn:test}A", "{urn:test}B"]}
    check("cyclic_path_is_unresolved", path_summary(nodes, "{urn:test}A")["unresolved"][0]["reason"] == "cyclic_type_path")
    check("missing_type_is_unresolved", type_node(index, "{urn:test}Absent")["reason"] == "missing_definition")
    check("inline_type_is_explicitly_unsupported", type_node(index, "{urn:test}Inline")["reason"] == "unsupported_inline_simple_type")
    try:
        qname("absent:T", source, element("Unbound"))
    except ValueError as error:
        check("unbound_prefix_rejected", str(error) == "UNBOUND_PREFIX")
    else:
        raise ValueError("FIXTURE:UNBOUND_PREFIX_ACCEPTED")
    try:
        parse_source(b'<!DOCTYPE schema><schema/>', "IN_MEMORY_FIXTURE")
    except ValueError as error:
        check("doctype_rejected_before_tree_parse", str(error) == "DTD_NOT_ADMITTED")
    else:
        raise ValueError("FIXTURE:DTD_ACCEPTED")
    return tests


def validate(evidence, expected, schemas):
    checks = []

    def check(label, condition):
        require(condition, label)
        checks.append(label)

    check("EXACT_COVERAGE", evidence == expected)
    packet = load(FULL / "native-packet.json")
    check("ALL_FACT_IDS_IN_SOURCE_ORDER", [r["fact_id"] for r in evidence["occurrences"]] == [f["id"] for f in packet["facts"]])
    check("CANDIDATE_VALUE_COUNTS_PRESERVED", evidence["counts"]["portable_value_tags"] == {"Decimal": 961, "Nil": 2, "Text": 157, "Unknown": 7})
    check("VALIDATION_NOT_RUN", evidence["schema_xbrl_validation"] == "not_run" and not evidence["upstream_executed"])
    check("RUNTIME_HELD", evidence["runtime_admission"] == "held")
    sources = {s["path"]: s for s in schemas}
    anchors = [c["declaration_anchor"] for c in evidence["concepts"].values() if "declaration_anchor" in c]
    anchors += [n["anchor"] for n in evidence["type_nodes"].values() if "anchor" in n]
    for position, location in enumerate(anchors):
        source = sources[location["source_path"]]
        raw = source["raw"]
        chunk = raw[location["byte_start"]:location["byte_end"]]
        check("ANCHOR_BYTES:" + str(position), digest(chunk) == location["slice_sha256"] and chunk.decode("utf-8") == location["text"])
        check("ANCHOR_SOURCE:" + str(position), source["sha256"] == location["source_sha256"])
    for row, fact in zip(evidence["occurrences"], packet["facts"]):
        key = fact["id"]
        check("OCCURRENCE_SOURCE:" + key, row["source_concept"] == fact["expanded_concept"] and row["decoded_text"] == fact["decoded_text"] and row["source_attributes"] == fact["source_attributes"])
        check("OCCURRENCE_CANDIDATE:" + key, row["packet_candidate_value"] == fact["candidate_value"] and not row["portable_value_mutated"])
        check("OCCURRENCE_UNVALIDATED:" + key, row["validation_status"] == "not_run")
    old = load(MASTER / "unitless-type-evidence-20261018/declarations.json")
    for prior in old["rows"]:
        concept = evidence["concepts"][prior["source_concept"]]
        check("SEVEN_DECLARATION_PRESERVED:" + prior["fact_id"], concept["declared_type"] == prior["declared_type"])
        check("SEVEN_TERMINAL_PRESERVED:" + prior["fact_id"], concept["type_path"]["terminal_references"] == [prior["terminal_builtin"]])
    reconciliation = load(MASTER / "r06-duty-reconciliation-20261018/reconciliation.json")
    check("TWELVE_RUNTIME_NULLS_PRESERVED", len(reconciliation["duties"]) == 12 and all(d["runtime_value"] is None and d["original"]["value"] is None for d in reconciliation["duties"]))
    for row in reconciliation["protected"]:
        check("PROTECTED:" + row["path"], binding(ROOT / row["path"]) == row)
    return checks


def git_state():
    git = lambda *args: subprocess.check_output(["git", *args], cwd=ROOT)
    baseline = load(MASTER / "r06-duty-reconciliation-20261018/run-manifest.json")["git_baseline"]
    require(git("rev-parse", "HEAD").decode().strip() == baseline["git_commit"], "GIT_HEAD")
    require(digest((ROOT / ".git/index").read_bytes()) == baseline["index_sha256"], "GIT_INDEX")
    require(not git("diff", "--cached", "--name-only"), "GIT_STAGING")
    dirty = [p.decode() for p in git("diff", "--name-only", "-z").split(b"\0") if p]
    require(set(dirty) == {row["path"] for row in baseline["tracked_dirty"]}, "DIRTY_PATHS")
    controls = {"docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
                "data/accounting-master/next-plan.md", "docs/plans/accounting-mission-requirements.md"}
    for row in baseline["tracked_dirty"]:
        if row["path"] not in controls:
            require(binding(ROOT / row["path"]) == row, "UNRELATED_DIRTY_FILE")
    return {"git_commit": baseline["git_commit"], "index_sha256": baseline["index_sha256"],
            "tracked_dirty_count": len(dirty), "staged_diff": "empty"}


def write_new(name, value):
    with (OUT / name).open("x") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--record", action="store_true")
    mode.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    expected, protected, schemas = construct()
    evidence = expected if args.record or args.check_only else load(OUT / "coverage.json")
    checks = validate(evidence, expected, schemas)
    fixture_checks = fixtures()
    findings = {"all_passed": True, "counts": expected["counts"],
                "source_preservation_checks": checks, "structural_fixture_checks": fixture_checks,
                "check_count": len(checks), "fixture_count": len(fixture_checks)}
    state = git_state()
    if args.record:
        for name in ("coverage.json", "checks.json", "run-manifest.json"):
            require(not (OUT / name).exists(), "ALREADY_RECORDED")
        write_new("coverage.json", evidence)
        write_new("checks.json", findings)
        write_new("run-manifest.json", {
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "command": [sys.executable, str(OUT / "check.py"), "--record"],
            "wall_seconds": time.monotonic() - tick, **state,
            "environment": {"executable": sys.executable, "python": platform.python_version(),
                            "cpu_gpu": "CPU standard-library XML/JSON/hash only; GPU not accessed.",
                            "upstream_imports": "none"},
            "data_version": binding(FULL / "native-packet.json"),
            "random_seeds": "N/A: deterministic source inspection",
            "plan_file": binding(PLAN), "result_file": str((OUT / "result.md").relative_to(ROOT)),
            "protected_inputs": protected,
            "artifacts": [binding(OUT / n) for n in ("source_index.py", "coverage.py", "check.py", "coverage.json", "checks.json")],
        })
    if not args.check_only:
        require(load(OUT / "checks.json") == findings, "FROZEN_FINDINGS")
        manifest = load(OUT / "run-manifest.json")
        for row in manifest["protected_inputs"] + manifest["artifacts"] + [manifest["plan_file"]]:
            require(binding(ROOT / row["path"]) == row, "MANIFEST_BINDING:" + row["path"])
    print(json.dumps({"status": "recorded" if args.record else "check-only passed" if args.check_only else "read-only replay passed",
                      "counts": expected["counts"], "checks": len(checks), "fixtures": len(fixture_checks),
                      "upstream_executed": False, "schema_xbrl_validation": "not_run"}))


if __name__ == "__main__":
    main()
