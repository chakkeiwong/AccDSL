"""Finite retained-file correspondence. No Arelle import or general XML adapter."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / "data/accounting-master/taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml"
EXPECTED_HASH = "e92b4267ed5015cb6136aa00c48a73c00ac12e0cbfec18686811436cde898f2d"
PLAN = ROOT / "docs/plans/accounting-native-occurrence-bytes-20261018.md"
INTEGRATION = ROOT / "data/accounting-master/early-conversion-integration-20261018"
XI = "{http://www.xbrl.org/2003/instance}"
XD = "{http://xbrl.org/2006/xbrldi}"
XS = "{http://www.w3.org/2001/XMLSchema-instance}"
XML = "{http://www.w3.org/XML/1998/namespace}"
# Fixed before construction: ID, concept local name, context, unit, reading, exact literal.
SELECTION = [
    ("f-7", "EntityRegistrantName", "c-1", None, "Text", "Apple Inc."),
    ("f-60", "RevenueFromContractWithCustomerExcludingAssessedTax", "c-13", "usd", "Decimal", "294866000000"),
    ("f-94", "NonoperatingIncomeExpense", "c-19", "usd", "Decimal", "-565000000"),
    ("f-102", "NetIncomeLoss", "c-1", "usd", "Decimal", "93736000000"),
    ("f-105", "EarningsPerShareBasic", "c-1", "usdPerShare", "Decimal", "6.11"),
    ("f-147", "CashAndCashEquivalentsAtCarryingValue", "c-21", "usd", "Decimal", "29943000000"),
    ("f-191", "CommitmentsAndContingencies", "c-21", "usd", "Nil", None),
    ("f-325", "ProceedsFromIssuanceOfLongTermDebt", "c-1", "usd", "Decimal", "0"),
    ("f-356", "InventoryPolicyTextBlock", "c-1", None, "MarkupText", None),
    ("f-1106", "AuditorName", "c-1", None, "Text", "Ernst & Young LLP"),
    ("f-207", "StockholdersEquity", "c-21", "usd", "Decimal", "56950000000"),
    ("f-256", "StockholdersEquity", "c-21", "usd", "Decimal", "56950000000"),
]
CONTEXT_IDS = ["c-1", "c-13", "c-19", "c-21"]
UNIT_IDS = ["usd", "usdPerShare"]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())}


def load(path):
    return json.loads(path.read_bytes())


def require(condition, code):
    if not condition:
        raise ValueError(code)


def unknown(reason):
    return {"tag": "Unknown", "reason": reason}


def rational(token):
    number = Fraction(token)
    return {"n": str(number.numerator), "d": str(number.denominator)}


def tree_reading(element):
    return {"name": element.tag, "attributes": dict(element.attrib), "text": element.text,
            "children": [{**tree_reading(c), "tail": c.tail} for c in element]}


def source_material():
    raw = SOURCE.read_bytes()
    require(sha(raw) == EXPECTED_HASH, "SOURCE_HASH")
    require(raw.startswith(b'<?xml version="1.0" encoding="utf-8"?>\r\n'), "SOURCE_ENCODING_DECLARATION")
    raw.decode("utf-8", "strict")
    require(b"<!DOCTYPE" not in raw and b"<![CDATA[" not in raw, "UNSUPPORTED_LEXICAL_FORM")
    root = ET.fromstring(raw)
    namespaces = list(ET.iterparse(BytesIO(raw), events=("start-ns",)))
    bindings = [v for _, v in namespaces]
    require(len(bindings) == len(dict(bindings)), "NAMESPACE_REDECLARATION")
    by_id = {e.get("id"): e for e in root if e.get("id")}
    require(len(by_id) == sum(bool(e.get("id")) for e in root), "AMBIGUOUS_ID")
    wrapper = '<root ' + ' '.join(('xmlns' + (':' + p if p else '') + '="' + v + '"') for p, v in bindings) + '>'
    positions = {id(e): i for i, e in enumerate(root, 1)}
    def locate(key):
        marker = ('id="' + key + '"').encode()
        require(raw.count(marker) == 1, "AMBIGUOUS_LEXICAL_ID:" + key)
        index = raw.index(marker)
        start = raw.rfind(b"<", 0, index)
        opening_end = raw.index(b">", index) + 1
        match = re.match(br"<([A-Za-z_][A-Za-z0-9_.:-]*)(?=\s|/?>)", raw[start:opening_end])
        require(match is not None, "START_TAG:" + key)
        token = match.group(1)
        if raw[opening_end - 2:opening_end] == b"/>":
            end = opening_end
            content = b""
        else:
            close = b"</" + token + b">"
            finish = raw.index(close, opening_end)
            end = finish + len(close)
            content = raw[opening_end:finish]
        chunk = raw[start:end]
        fragment = ET.fromstring(wrapper.encode() + chunk + b"</root>")[0]
        expected = deepcopy(by_id[key])
        expected.tail = None
        require(ET.tostring(fragment) == ET.tostring(expected), "FRAGMENT_TREE:" + key)
        return {"id": key, "byte_start": start, "byte_end": end, "element_path": "/1/" + str(positions[id(by_id[key])]),
                "slice_sha256": sha(chunk), "byte_length": len(chunk), "raw_utf8": chunk.decode(),
                "content_utf8": content.decode(), "lexical_qname": token.decode()}, chunk
    return raw, root, by_id, bindings, locate


def construct():
    raw, root, by_id, bindings, locate = source_material()
    spans, chunks = {}, {}
    for key in [r[0] for r in SELECTION] + CONTEXT_IDS + UNIT_IDS:
        spans[key], chunks[key] = locate(key)
    contexts = []
    for key in CONTEXT_IDS:
        element = by_id[key]
        dimensions = []
        for container in ["segment", "scenario"]:
            node = element.find((XI + "entity/" if container == "segment" else "") + XI + container)
            for child in list(node) if node is not None else []:
                dimensions.append({"container": container, "reading": tree_reading(child)})
        contexts.append({"id": key, "span": spans[key], "identifier": tree_reading(element.find(XI + "entity/" + XI + "identifier")),
                         "period": tree_reading(element.find(XI + "period")), "dimensions_and_qualifiers": dimensions})
    units = []
    for key in UNIT_IDS:
        element = by_id[key]
        divide = element.find(XI + "divide")
        numerator = element if divide is None else divide.find(XI + "unitNumerator")
        denominator = [] if divide is None else divide.find(XI + "unitDenominator")
        def measures(node):
            values = []
            for child in node:
                token = child.text
                prefix, local = token.split(":", 1) if ":" in token else ("", token)
                values.append({"token": token, "expanded_name": "{" + dict(bindings)[prefix] + "}" + local})
            return values
        units.append({"id": key, "span": spans[key], "numerator": measures(numerator), "denominator": measures(denominator)})
    facts = []
    for key, concept, cid, uid, kind, literal in SELECTION:
        element = by_id[key]
        require(not list(element), "SELECTED_CHILD_CONTENT:" + key)
        value = {"tag": kind}
        if kind == "Decimal":
            value["rational"] = rational(element.text)
        elif kind in ("Text", "MarkupText"):
            value["text"] = element.text
        facts.append({"id": key, "span": spans[key], "expanded_concept": element.tag, "source_attributes": dict(element.attrib),
                      "decoded_text": element.text, "candidate_value": value, "source_context_id": cid, "source_unit_id": uid,
                      "explicit_language": element.get(XML + "lang"),
                      "root_language_evidence": {"source_path": "/1", "attribute": XML + "lang", "value": root.get(XML + "lang")},
                      "financial_context": {k: unknown("No admitted mapping in this documentary unit") for k in ["legal_entity", "book", "perimeter", "basis", "currency_or_unit", "calendar", "dimensions", "financial_time"]},
                      "admission": "candidate_only"})
    packet = {"evidence_mode": "retained_source_documentary_reading", "upstream_executed": False,
              "source": {**binding(SOURCE), "byte_length": len(raw)},
              "namespace_bindings": [{"prefix": p, "namespace_uri": v} for p, v in bindings],
              "facts": facts, "contexts": contexts, "units": units,
              "publication_time": unknown("Not inferred from this instance or filesystem metadata"),
              "taxonomy_validation": "not_run", "portable_record_status": "not_yet_translated"}
    return packet, chunks


def validate(packet):
    checks = []
    def check(label, condition):
        require(condition, label)
        checks.append(label)
    raw, root, by_id, namespaces, locate = source_material()
    check("SOURCE_IDENTITY", packet["source"] == {**binding(SOURCE), "byte_length": len(raw)})
    check("DOCUMENTARY_ONLY", packet["upstream_executed"] is False and packet["taxonomy_validation"] == "not_run" and packet["portable_record_status"] == "not_yet_translated")
    check("PUBLICATION_UNKNOWN", packet["publication_time"]["tag"] == "Unknown" and bool(packet["publication_time"]["reason"].strip()))
    check("NAMESPACE_EVIDENCE", packet["namespace_bindings"] == [{"prefix": p, "namespace_uri": v} for p, v in namespaces])
    check("SELECTED_OCCURRENCES", [r["id"] for r in packet["facts"]] == [r[0] for r in SELECTION])
    check("SELECTED_CONTEXTS", [r["id"] for r in packet["contexts"]] == CONTEXT_IDS)
    check("SELECTED_UNITS", [r["id"] for r in packet["units"]] == UNIT_IDS)
    for row in packet["facts"] + packet["contexts"] + packet["units"]:
        check("EXACT_BYTE_SPAN:" + row["id"], row["span"] == locate(row["id"])[0])
    for row, expected in zip(packet["facts"], SELECTION):
        key, local, cid, uid, kind, literal = expected
        element = by_id[key]
        check("CONCEPT:" + key, row["expanded_concept"] == element.tag and element.tag.split("}")[-1] == local)
        check("ATTRIBUTES:" + key, row["source_attributes"] == dict(element.attrib))
        check("SOURCE_JOINS:" + key, row["source_context_id"] == element.get("contextRef") == cid and row["source_unit_id"] == element.get("unitRef") == uid)
        check("DECODED_TEXT:" + key, row["decoded_text"] == element.text)
        value = row["candidate_value"]
        check("VALUE_KIND:" + key, value["tag"] == kind)
        if kind == "Decimal":
            check("EXACT_NUMERIC:" + key, element.text == literal and value == {"tag": kind, "rational": rational(literal)})
        elif kind == "Nil":
            check("NIL_HAS_NO_VALUE:" + key, value == {"tag": "Nil"} and element.text is None and element.get(XS + "nil") == "true")
        else:
            check("TEXT_VALUE:" + key, value == {"tag": kind, "text": element.text})
            if literal is not None:
                check("FIXED_TEXT:" + key, element.text == literal)
        check("LANGUAGE_SOURCE:" + key, row["explicit_language"] is None and row["root_language_evidence"] == {"source_path": "/1", "attribute": XML + "lang", "value": "en-US"})
        check("NO_ADMISSION:" + key, row["admission"] == "candidate_only")
        check("FINANCIAL_UNKNOWNS:" + key, all(v["tag"] == "Unknown" and bool(v["reason"].strip()) for v in row["financial_context"].values()) and set(row["financial_context"]) == {"legal_entity", "book", "perimeter", "basis", "currency_or_unit", "calendar", "dimensions", "financial_time"})
    for row in packet["contexts"]:
        key, element = row["id"], by_id[row["id"]]
        check("IDENTIFIER:" + key, row["identifier"] == tree_reading(element.find(XI + "entity/" + XI + "identifier")))
        check("PERIOD:" + key, row["period"] == tree_reading(element.find(XI + "period")))
        dims = row["dimensions_and_qualifiers"]
        if key == "c-13":
            check("PRODUCT_DIMENSION", len(dims) == 1 and dims[0]["container"] == "segment" and dims[0]["reading"] == tree_reading(element.find(".//" + XD + "explicitMember")) and dims[0]["reading"]["attributes"]["dimension"] == "srt:ProductOrServiceAxis" and dims[0]["reading"]["text"] == "us-gaap:ProductMember")
        else:
            check("NO_ADDED_DIMENSION:" + key, dims == [])
    usd = {"token": "iso4217:USD", "expanded_name": "{http://www.xbrl.org/2003/iso4217}USD"}
    shares = {"token": "shares", "expanded_name": XI + "shares"}
    for row in packet["units"]:
        check("UNIT_SIDES:" + row["id"], row["numerator"] == [usd] and row["denominator"] == ([shares] if row["id"] == "usdPerShare" else []))
    by = {r["id"]: r for r in packet["facts"]}
    check("REPEATED_EQUITY_DISTINCT", by["f-207"]["candidate_value"] == by["f-256"]["candidate_value"] and by["f-207"]["span"]["byte_start"] != by["f-256"]["span"]["byte_start"])
    check("ESCAPED_MARKUP", "&lt;" in by["f-356"]["span"]["content_utf8"] and by["f-356"]["decoded_text"].startswith("<div") and "Inventories are measured using the first-in, first-out method." in by["f-356"]["decoded_text"])
    check("ENTITY_DECODE", "&amp;" in by["f-1106"]["span"]["content_utf8"] and by["f-1106"]["decoded_text"] == "Ernst & Young LLP")
    check("CRLF_PRESERVED", "\r\n" in by["f-105"]["span"]["raw_utf8"])
    return checks


def negative_cases(packet):
    results = []
    def reject(name, code, change):
        candidate = deepcopy(packet)
        by = {r["id"]: r for r in candidate["facts"]}
        change(candidate, by)
        try:
            validate(candidate)
        except ValueError as error:
            require(str(error) == code, "WRONG_DIAGNOSTIC:" + name + ":" + str(error))
            results.append({"case": name, "diagnostic": code, "rejected": True})
        else:
            raise ValueError("CORRUPTION_ACCEPTED:" + name)
    reject("shifted_byte_locator", "EXACT_BYTE_SPAN:f-105", lambda p,b: b["f-105"]["span"].update(byte_start=b["f-105"]["span"]["byte_start"]+1))
    reject("line_endings_normalized", "EXACT_BYTE_SPAN:f-105", lambda p,b: b["f-105"]["span"].update(raw_utf8=b["f-105"]["span"]["raw_utf8"].replace("\r\n","\n")))
    reject("raw_slice_from_other_fact", "EXACT_BYTE_SPAN:f-207", lambda p,b: b["f-207"].update(span=b["f-256"]["span"]))
    reject("nil_to_zero", "VALUE_KIND:f-191", lambda p,b: b["f-191"].update(candidate_value={"tag":"Decimal","rational":{"n":"0","d":"1"}}))
    reject("decimals_applied_as_scale", "EXACT_NUMERIC:f-102", lambda p,b: b["f-102"]["candidate_value"].update(rational={"n":"93736","d":"1"}))
    reject("negative_sign_lost", "EXACT_NUMERIC:f-94", lambda p,b: b["f-94"]["candidate_value"].update(rational={"n":"565000000","d":"1"}))
    reject("per_share_rounded", "EXACT_NUMERIC:f-105", lambda p,b: b["f-105"]["candidate_value"].update(rational={"n":"6","d":"1"}))
    reject("entity_text_left_encoded", "DECODED_TEXT:f-1106", lambda p,b: b["f-1106"].update(decoded_text="Ernst &amp; Young LLP"))
    reject("markup_flattened", "DECODED_TEXT:f-356", lambda p,b: b["f-356"].update(decoded_text="Inventories are measured using the first-in, first-out method."))
    reject("financial_basis_invented", "FINANCIAL_UNKNOWNS:f-7", lambda p,b: b["f-7"]["financial_context"].update(basis={"tag":"Known","reason":"US GAAP"}))
    reject("context_join_changed", "SOURCE_JOINS:f-60", lambda p,b: b["f-60"].update(source_context_id="c-1"))
    reject("duplicate_occurrence_dropped", "SELECTED_OCCURRENCES", lambda p,b: p["facts"].pop())
    reject("product_dimension_dropped", "PRODUCT_DIMENSION", lambda p,b: p["contexts"][1].update(dimensions_and_qualifiers=[]))
    reject("unit_denominator_dropped", "UNIT_SIDES:usdPerShare", lambda p,b: p["units"][1].update(denominator=[]))
    reject("default_unit_namespace_wrong", "UNIT_SIDES:usdPerShare", lambda p,b: p["units"][1]["denominator"][0].update(expanded_name="shares"))
    reject("root_language_reported_explicitly", "LANGUAGE_SOURCE:f-7", lambda p,b: b["f-7"].update(explicit_language="en-US"))
    reject("publication_inferred", "PUBLICATION_UNKNOWN", lambda p,b: p.update(publication_time={"tag":"Known","reason":"period end"}))
    reject("candidate_admitted", "NO_ADMISSION:f-102", lambda p,b: b["f-102"].update(admission="admitted"))
    reject("runtime_credit_invented", "DOCUMENTARY_ONLY", lambda p,b: p.update(upstream_executed=True))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    outputs = ["readings.json","checks.json","run-manifest.json"]
    if args.record:
        for name in outputs + ["slices"]:
            require(not (OUT / name).exists(), "OUTPUT_EXISTS:"+name)
    packet, chunks = construct()
    checks = validate(packet)
    negatives = negative_cases(packet)
    evidence = {"all_passed": True, "checks": checks, "check_count":len(checks),
                "corruption_cases":negatives, "selected_facts":12, "contexts":4, "units":2,
                "exact_byte_slices":len(chunks), "upstream_executed":False,
                "scope":"selected actual native source bytes and documentary readings only"}
    if args.record:
        (OUT/"slices").mkdir()
        for key, raw in chunks.items():
            with (OUT/"slices"/(key+".xmlfrag")).open("xb") as handle:
                handle.write(raw)
        for name,value in [("readings.json",packet),("checks.json",evidence)]:
            with (OUT/name).open("x") as handle:
                json.dump(value,handle,indent=2,ensure_ascii=False)
                handle.write("\n")
        protected=[SOURCE, ROOT/"data/accounting-master/taxonomy-reuse-20261007/graph-final.json",
                   ROOT/"data/accounting-master/selected-reuse-20261015/source-selection.json",
                   ROOT/"docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip",
                   ROOT/"docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf",
                   ROOT/"docs/design/proposal/architecture/native-xbrl-translation-proposed-v1.md",
                   ROOT/"docs/design/proposal/architecture/native-loader-source-delta-v1.md",
                   ROOT/"data/accounting-master/apple-inline-occurrences-20261013/result.md"]
        protected += [INTEGRATION/name for name in ["assessment-successor.json","integration-bindings.json","operation-successor.json","native-xbrl-translation-supplement.json","native-offline-resolution-supplement.json","native-loader-source-supplement.json"]]
        dirty=subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=ROOT,text=True).splitlines()
        require(len(dirty)==36,"DIRTY_BASELINE")
        manifest={"started_utc":started,"finished_utc":datetime.now(timezone.utc).isoformat(),
                  "wall_seconds":time.monotonic()-tick,"command":"python3 data/accounting-master/native-occurrence-bytes-20261018/check.py --record",
                  "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                  "index_sha256":sha((ROOT/".git/index").read_bytes()),"tracked_dirty":dirty,
                  "environment":{"executable":sys.executable,"python":platform.python_version(),"conda_env":os.environ.get("CONDA_DEFAULT_ENV"),
                                 "cpu_gpu_status":"standard-library CPU file/XML checks; no framework or Arelle import, GPU detection or use"},
                  "random_seeds":"N/A: deterministic documentary checks","data_version":binding(SOURCE),
                  "plan":binding(PLAN),"checker":binding(Path(__file__).resolve()),
                  "protected_inputs":[binding(p) for p in protected],
                  "outputs":[binding(OUT/n) for n in ["readings.json","checks.json"]]+[binding(OUT/"slices"/(k+".xmlfrag")) for k in chunks],
                  "result_path":str((OUT/"result.md").relative_to(ROOT)),"time_limit":"check time is not active source reading time"}
        with (OUT/"run-manifest.json").open("x") as handle:
            json.dump(manifest,handle,indent=2);handle.write("\n")
    else:
        require(load(OUT/"readings.json")==packet and load(OUT/"checks.json")==evidence,"EXACT_REPLAY")
        manifest=load(OUT/"run-manifest.json")
        for row in manifest["protected_inputs"]+manifest["outputs"]+[manifest[k] for k in ["plan","checker"]]:
            require(binding(ROOT/row["path"])==row,"BINDING:"+row["path"])
        require(sha((ROOT/".git/index").read_bytes())==manifest["index_sha256"],"INDEX_CHANGED")
        require(subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=ROOT,text=True).splitlines()==manifest["tracked_dirty"],"DIRTY_CHANGED")
        for key,raw in chunks.items():
            require((OUT/"slices"/(key+".xmlfrag")).read_bytes()==raw,"SLICE_REPLAY:"+key)
    print(json.dumps({"status":"recorded" if args.record else "read-only replay passed","checks":len(checks),
                      "rejected_cases":len(negatives),"facts":12,"slices":len(chunks),"runtime_executed":False}))


if __name__=="__main__":
    main()
