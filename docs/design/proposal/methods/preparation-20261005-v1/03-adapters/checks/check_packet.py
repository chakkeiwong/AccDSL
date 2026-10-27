"""Bounded source/fixture diagnostic, not a library integration or benchmark."""
import ast
import copy
from datetime import datetime, timezone
import datetime as datetime_module
from decimal import Decimal
import hashlib
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import sys
import time

BASE = Path(__file__).resolve().parents[1]
START = time.monotonic()
CHECKS = []

def check(name, condition, evidence_class, detail=None):
    assert condition, (name, detail)
    CHECKS.append({"name": name, "status": "pass", "evidence_class": evidence_class, "detail": detail})

def read_json(name):
    return json.loads((BASE / name).read_text())

register = read_json("source-register.json")
for row in register["sources"]:
    data = (BASE / row["path"]).read_bytes()
    check("source:" + row["path"], hashlib.sha256(data).hexdigest() == row["sha256"], "integrity")
for row in read_json("retained-register.json"):
    data = (BASE / row["path"]).read_bytes()
    check("retained:" + row["path"], hashlib.sha256(data).hexdigest() == row["sha256"], "integrity")
anchor_ids = set()
for row in read_json("source-anchors.json"):
    check("unique-anchor:" + row["id"], row["id"] not in anchor_ids, "structure")
    anchor_ids.add(row["id"])
    for seg in row["segments"]:
        raw = (BASE / seg["path"]).read_bytes()
        excerpt = "".join(raw.decode().splitlines(keepends=True)[seg["line_start"]-1:seg["line_end"]])
        check("anchor:" + row["id"] + ":" + str(seg["line_start"]),
              hashlib.sha256(raw).hexdigest() == seg["source_sha256"] and hashlib.sha256(excerpt.encode()).hexdigest() == seg["excerpt_sha256"], "integrity")

cases = read_json("adapter-cases-v1.json")["cases"]
check("unique-case-ids", len({r["id"] for r in cases}) == len(cases), "structure")
by_id = {r["id"]: r for r in cases}
for case in cases:
    check("case-anchor-links:" + case["id"], all(a in anchor_ids for a in case["evidence"]), "structure")
    check("case-has-input-output-and-rejection:" + case["id"], bool(case["input"]) and bool(case["expected"]) and bool(case["reject"]), "structure")

apple = read_json("apple-instant-case.json")
raw = (BASE / apple["source_path"]).read_bytes()
check("Apple-original-full-hash", hashlib.sha256(raw).hexdigest() == apple["source_sha256"], "real_source_integrity")
for name, part in apple["parts"].items():
    check("Apple-original-byte-span:" + name,
          raw[part["byte_start"]:part["byte_end_exclusive"]].decode() == part["excerpt"], "real_source_locator")
fact = apple["parts"]["fact"]["excerpt"]
attrs = dict(re.findall(r'(\w+)="([^"]*)"', fact))
literal = re.search(r'>([^<]+)</', fact).group(1)
check("Apple-original-attributes", attrs["contextRef"] == "c-17" and attrs["unitRef"] == "usd" and attrs["decimals"] == "-6" and attrs["scale"] == "6", "real_source_reading")
check("Apple-inline-scale-once", Decimal(literal.replace(",", "")) * Decimal(10) ** int(attrs["scale"]) == Decimal(apple["expected"]["normalized_decimal"]), "exact_specification_arithmetic")
check("Apple-original-instant", "<xbrli:instant>2024-12-28</xbrli:instant>" in apple["parts"]["context"]["excerpt"], "real_source_reading")

# Load only selected pure source functions without importing the packages. The
# origin validator's declared Uint64 alias is represented by int for its branch.
# This checks exact retained function bodies, not Pydantic or adapter execution.
origin_path = BASE / "sources/upstream/docling-core/docling_core__types__doc__common__origin.py"
tree = ast.parse(origin_path.read_text())
func = copy.deepcopy(next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "parse_hex_string"))
func.decorator_list = []
module = ast.fix_missing_locations(ast.Module(body=[func], type_ignores=[]))
ns = {"Uint64": int}
exec(compile(module, str(origin_path), "exec"), ns)
source_a = by_id["AD06"]["input"]["source_sha256_a"]
source_b = by_id["AD06"]["input"]["source_sha256_b"]
check("AD06-distinct-full-hashes", len(source_a) == len(source_b) == 64 and source_a != source_b, "synthetic_counterexample")
low_a, low_b = (ns["parse_hex_string"](None, x) for x in (source_a, source_b))
check("retained-origin-validator-low64-collision", low_a == low_b == int("0123456789abcdef", 16), "isolated_source_function_probe", "No Docling/Pydantic import; int stands for Uint64 alias, not package compatibility evidence.")

hash_path = BASE / "sources/upstream/docling/docling__utils__utils.py"
hash_tree = ast.parse(hash_path.read_text())
hash_func = copy.deepcopy(next(n for n in hash_tree.body if isinstance(n, ast.FunctionDef) and n.name == "create_file_hash"))
hash_module = ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), hash_func], type_ignores=[]))
hash_ns = {"BytesIO": BytesIO, "Path": Path, "hashlib": hashlib}
exec(compile(hash_module, str(hash_path), "exec"), hash_ns)
stream = BytesIO(b"abcdef")
stream.seek(3)
observed_hash = hash_ns["create_file_hash"](stream)
check("Docling-helper-hashes-current-stream-suffix", observed_hash == hashlib.sha256(b"def").hexdigest() and observed_hash != hashlib.sha256(b"abcdef").hexdigest() and stream.tell() == 6, "isolated_source_function_probe", "Retained helper body only; full converter not invoked.")

# Exact ISO-date helper from Arelle plus its exact pattern and timezone helper.
xml_path = BASE / "sources/upstream/arelle/arelle__XmlUtil.py"
tree = ast.parse(xml_path.read_text())
nodes = []
for node in tree.body:
    names = [n.id for n in node.targets if isinstance(n, ast.Name)] if isinstance(node, ast.Assign) else []
    if set(names) & {"datetimePattern", "DATETIME_MINYEAR", "DATETIME_MAXYEAR"} or isinstance(node, ast.FunctionDef) and node.name in {"tzinfo", "datetimeValue"}:
        nodes.append(copy.deepcopy(node))
module = ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[]))
ns = {"datetime": datetime_module, "re": re}
exec(compile(module, str(xml_path), "exec"), ns)
original = apple["expected"]["reported_instant"]
boundary = ns["datetimeValue"](original, addOneDay=True)
check("Arelle-date-helper-boundary", boundary.isoformat() == apple["expected"]["normalized_xbrl_boundary"], "isolated_source_function_probe", "Stdlib re substituted for regex only for the retained ISO pattern and checked ISO inputs; no parser/model import.")
check("Docling-instance-formatting-date-counterexample", str(boundary.date()) != original, "source_derived_counterexample", "Equivalent native-instance context; not Docling output on Apple inline HTML.")
check("Arelle-explicit-timestamp-no-extra-day", ns["datetimeValue"]("2024-12-28T12:00:00Z", addOneDay=True).isoformat() == "2024-12-28T12:00:00+00:00", "isolated_source_function_probe")

# Detect whether the collected dimension list actually reaches a graph output.
xbrl_path = BASE / "sources/upstream/docling/docling__backend__xml__xbrl_backend.py"
tree = ast.parse(xbrl_path.read_text())
convert = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "convert")
value_assign = next(n for n in ast.walk(convert) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "value_cells" for t in n.targets))
labels = [e.elts[1].value for e in value_assign.value.elts]
check("Docling-XBRL-value-cells-omit-dimensions", labels == ["value", "period", "unit", "decimals"], "static_source_structure")
loads = [n for n in ast.walk(convert) if isinstance(n, ast.Name) and n.id == "dimensions" and isinstance(n.ctx, ast.Load)]
check("Docling-dimensions-only-append-no-export-use", len(loads) == 1, "static_source_structure", "The sole load is dimensions.append; inspected surrounding code confirms output never consumes it.")
check("Docling-XBRL-first-numerator-only", "fact.unit.measures[0][0].localName" in xbrl_path.read_text(), "static_source_structure")

box = by_id["AD07"]["input"]["bbox"]
height = by_id["AD07"]["input"]["page_height"]
expected = by_id["AD07"]["expected"]["top_left_bbox"]
check("AD07-coordinate-conversion", [box["l"], height-box["t"], box["r"], height-box["b"]] == [expected[k] for k in ("l", "t", "r", "b")], "exact_specification_arithmetic")
p = by_id["AD08"]["input"]
check("AD08-success-and-failure-account-for-known-pages", set(p["successful_pages"]) | set(p["failed_placeholder_pages"]) == set(p["known_page_inventory"]) and not (set(p["successful_pages"]) & set(p["failed_placeholder_pages"])), "specification_consistency")
check("AD03-distinct-occurrences-preserved", len({r["occurrence_id"] for r in by_id["AD03"]["input"]["facts"]}) == by_id["AD03"]["expected"]["proposed_assertion_count"], "specification_consistency")
check("AD09-time-evidence-aware", datetime.fromisoformat(by_id["AD09"]["input"]["acquisition_receipt"]["ingested_at"]).tzinfo is not None and datetime.fromisoformat(by_id["AD09"]["input"]["docling_save_timestamp"]).tzinfo is None, "specification_consistency")

report = {
    "status": "pass_bounded_source_and_specification_checks", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    "command": "python3 checks/check_packet.py", "working_directory": "packet 03-adapters",
    "environment": {"python": sys.version, "platform": platform.platform(), "GPU": "N/A: no GPU framework imported or device queried"},
    "wall_seconds": time.monotonic() - START, "check_count": len(CHECKS), "checks": CHECKS,
    "git_commit": "N/A: isolated unversioned preparation packet; upstream source commits in source-register.json",
    "seed": "N/A: deterministic source and specification diagnostic", "data_version": "retained Apple full hash and corpus report ID in apple-instant-case.json",
    "plan": "PLAN.md", "result": "capability-matrix.md", "artifact": "checks/verification.json",
    "limits": "No Arelle/Docling/pdfplumber package imported, installed or run; three extracted helper bodies probed with declared stand-ins. Not adapter integration, extraction benchmark, statistical ranking or production acceptance. Other proposed cases received structural and model/code review, not engine execution or human acceptance.",
}
(BASE / "checks/verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("status", "check_count", "wall_seconds", "limits")}, indent=2))
