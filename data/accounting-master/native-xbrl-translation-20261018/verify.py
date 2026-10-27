"""Read-only documentary correspondence checks; --record creates evidence once."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from common import OUT, ROOT, blob, canonical, decode, pointer, read, record_ref, ref_set, refs, require, sha, typed, write_once
from profile_definitions import profile as declared_profile

NS = {"xbrli": "http://www.xbrl.org/2003/instance", "xsi": "http://www.w3.org/2001/XMLSchema-instance",
      "xbrldi": "http://xbrl.org/2006/xbrldi", "t": "urn:accdsl:synthetic:tax", "iso4217": "http://www.xbrl.org/2003/iso4217"}
XI = "{" + NS["xbrli"] + "}"
XD = "{" + NS["xbrldi"] + "}"
SPEC = "docs/design/proposal/architecture/native-xbrl-translation-proposed-v1.md"
PLAN = "docs/plans/accounting-native-xbrl-translation-20261018.md"
COMMAND = "python3 data/accounting-master/native-xbrl-translation-20261018/verify.py"
EXPECTED_VALUES = {
    "F_DEC": ("Decimal", "241", "2"), "F_DUP": ("Decimal", "241", "2"),
    "F_NIL": ("Nil",), "F_ZERO": ("Decimal", "0", "1"), "F_EMPTY": ("Unknown",),
    "F_FRACTION": ("Fraction", "1", "3"), "F_FRACZERO": ("Unknown",), "F_TEXT": ("Text",),
    "F_MISSING": ("Decimal", "5", "4"), "F_NOUNIT": ("Decimal", "5", "4"),
    "F_DATETIME": ("Decimal", "5", "4"), "F_FOREVER": ("Decimal", "5", "4"),
    "F_PRODUCT": ("Decimal", "2", "1"), "F_REVERSED": ("Decimal", "2", "1"),
    "F_BADDATE": ("Decimal", "2", "1"), "F_NONFINITE": ("Unknown",),
    "F_BADDEC": ("Unknown",), "F_MISSINGTYPE": ("Unknown",), "F_XMLCONTENT": ("Unknown",),
}


def check_material(packet, records, profile, xml):
    checks = []

    def check(label, condition):
        require(condition, label)
        checks.append(label)

    check("PROFILE_BASELINE", profile == declared_profile())
    typed(packet, profile["packet_type"], profile)
    check("PACKET_CLOSED_TYPES", True)
    check("RECORD_LIST", isinstance(records, list))
    check("PACKET_DOCUMENTARY", packet["upstream_executed"] is False and packet["evidence_mode"] == "specification_example")
    check("SOURCE_BLOB", packet["source_blob"] == blob(OUT / "source.xml"))
    by_key = {}
    for record in records:
        check("ENVELOPE:" + record["key"], set(record) == set(profile["envelope_fields"]))
        check("KIND_SCHEMA:" + record["key"], record["kind"] in profile["records"] and record["schema"] == profile["records"][record["kind"]]["schema"])
        check("REVISION:" + record["key"], type(record["revision"]) is int and record["revision"] >= 0)
        check("KEY:" + record["key"], isinstance(record["key"], str) and bool(re.fullmatch(r"[A-Za-z0-9_.:/@-]+", record["key"])))
        check("UNIQUE_KEY:" + record["key"], record["key"] not in by_key)
        typed(record["body"], profile["records"][record["kind"]]["body_type"], profile)
        typed(record["dependencies"], {"list": "Ref"}, profile)
        canonical(record)
        by_key[record["key"]] = record
    check("TYPE_CLOSURE", True)
    root = ET.fromstring(xml)
    check("XML_ROOT", root.tag == XI + "xbrl")
    namespaces = [{"prefix": k, "namespace_uri": v} for k, v in NS.items()]
    parsed_bindings = [{"prefix": k, "namespace_uri": v} for _, (k, v) in ET.iterparse(BytesIO(xml), events=("start-ns",))]
    check("NAMESPACE_BINDINGS", packet["namespace_bindings"] == namespaces == parsed_bindings)
    native_entries = packet["contexts"] + packet["units"] + packet["facts"]
    elements = {element.attrib["id"]: element for element in root}
    check("XML_ID_UNIQUENESS", len(elements) == len(root))
    check("SOURCE_FIELD_COVERAGE", len(native_entries) == len(elements) and {e["xml_id"] for e in native_entries} == set(elements))
    check("FACT_FIXTURE_ORACLE", {f["xml_id"] for f in packet["facts"]} == set(EXPECTED_VALUES))
    expected_keys = {"native-xbrl-method", "synthetic-source", "synthetic-mapping", "synthetic-comparison", "synthetic-import"}
    expected_keys |= {"occ-" + e["xml_id"] for e in native_entries}
    expected_keys |= {e["xml_id"] for e in packet["contexts"] + packet["units"] + packet["facts"]}
    expected_keys |= {"ctx-" + e["xml_id"] for e in packet["facts"]}
    check("OUTPUT_POPULATION", set(by_key) == expected_keys)
    source = by_key["synthetic-source"]["body"]
    check("ORIGINAL_XML_IDENTITY", source["original_bytes_ref"] == packet["source_blob"])
    check("SOURCE_METADATA", source["origin"] == packet["origin"] and source["document_identity"] == packet["fixture_id"] and source["media_type"] == "application/xml" and source["namespace_bindings"] == namespaces)
    for field in ["acquisition", "issuer", "publication_evidence", "vintage_evidence"]:
        check("SOURCE_UNKNOWN:" + field, source[field]["tag"] == "Unknown" and bool(source[field]["reason"]))
    ordered = list(root)
    previous_end = None
    for i, element in enumerate(ordered, 1):
        key = element.attrib["id"]
        entry = next(e for e in native_entries if e["xml_id"] == key)
        loc = entry["locator"]
        check("LOCATOR_BOUNDS:" + key, 0 <= loc["byte_start"] < loc["byte_end"] <= len(xml))
        check("LOCATOR_PATH:" + key, loc["element_id"] == key and loc["element_path"] == "/1/" + str(i))
        if previous_end is not None:
            check("LOCATOR_NONOVERLAP:" + key, loc["byte_start"] >= previous_end and xml[previous_end:loc["byte_start"]].strip() == b"")
        previous_end = loc["byte_end"]
        chunk = xml[loc["byte_start"]:loc["byte_end"]]
        wrapper = ('<wrapper ' + " ".join('xmlns:' + k + '="' + v + '"' for k, v in NS.items()) + '>').encode() + chunk + b"</wrapper>"
        copied = ET.fromstring(wrapper)[0]
        expected_element = deepcopy(element)
        copied.tail = expected_element.tail = None
        check("LOCATOR_DECODED_ELEMENT:" + key, ET.tostring(copied) == ET.tostring(expected_element))
        occurrence = by_key["occ-" + key]["body"]
        check("LOCATOR_CORRESPONDENCE:" + key, occurrence["locator"] == loc)
        check("OCCURRENCE_SOURCE:" + key, occurrence["source_ref"] == record_ref(by_key["synthetic-source"]) and occurrence["package_root_key"] == packet["fixture_id"] and occurrence["parent_key"] == "xml-root")
    for entry in packet["contexts"]:
        key = entry["xml_id"]
        body, element = by_key[key]["body"], elements[key]
        check("CONTEXT_GROUP:" + key, element.tag == XI + "context")
        check("CONTEXT_EVIDENCE:" + key, all(body[name] == entry[name] for name in ["xml_id", "identifier", "period", "dimensions", "non_dimension_spans"]))
        identifier = element.find(XI + "entity/" + XI + "identifier")
        check("ENTITY_READING:" + key, body["identifier"] == {"scheme": identifier.attrib["scheme"], "text": identifier.text})
        period = element.find(XI + "period")
        expected_form = {XI + "startDate": "duration", XI + "instant": "instant", XI + "forever": "forever"}.get(period[0].tag, "other")
        check("PERIOD_FORM:" + key, body["period"]["form"] == expected_form)
        for field, name in [("start_token", "startDate"), ("end_token", "endDate"), ("instant_token", "instant")]:
            check("PERIOD_TOKEN:" + key + ":" + field, body["period"][field] == period.findtext(XI + name))
        check("CONTEXT_OCCURRENCE:" + key, body["occurrence_ref"] == record_ref(by_key["occ-" + key]))
        dimensions, non_dimensions = [], []
        for container in ["segment", "scenario"]:
            node = element.find((XI + "entity/" if container == "segment" else "") + XI + container)
            for child in list(node) if node is not None else []:
                if child.tag in [XD + "explicitMember", XD + "typedMember"]:
                    dimensions.append((container, child))
                else:
                    non_dimensions.append(child)
        check("DIMENSION_COUNT:" + key, len(body["dimensions"]) == len(dimensions))
        check("NON_DIMENSION_COUNT:" + key, len(body["non_dimension_spans"]) == len(non_dimensions))

        def verify_child_span(span, child, label):
            loc = entry["locator"]
            check(label + "_RANGE:" + key, loc["byte_start"] <= span["byte_start"] < span["byte_end"] <= loc["byte_end"])
            chunk = xml[span["byte_start"]:span["byte_end"]]
            wrapped = ('<wrapper ' + " ".join('xmlns:' + k + '=\"' + v + '\"' for k, v in NS.items()) + '>').encode() + chunk + b"</wrapper>"
            decoded = ET.fromstring(wrapped)
            expected_child = deepcopy(child)
            expected_child.tail = None
            check(label + "_CONTENT:" + key, len(decoded) == 1 and ET.tostring(decoded[0]) == ET.tostring(expected_child))

        for dim, (container, child) in zip(body["dimensions"], dimensions):
            verify_child_span(dim["source_span"], child, "DIMENSION_SPAN")
            axis_prefix, axis_local = child.attrib["dimension"].split(":", 1)
            explicit = child.tag == XD + "explicitMember"
            check("DIMENSION_AXIS:" + key, dim["axis_token"] == child.attrib["dimension"] and dim["axis_qname"] == {"namespace_uri": NS[axis_prefix], "local_name": axis_local})
            check("DIMENSION_FORM_CONTAINER:" + key, dim["container"] == container and dim["form"] == ("explicit" if explicit else "typed"))
            check("DIMENSION_MEMBER_TOKEN:" + key, dim["member_token"] == (child.text if explicit else None))
        for span, child in zip(body["non_dimension_spans"], non_dimensions):
            verify_child_span(span, child, "NON_DIMENSION_SPAN")
    duration = by_key["C_DURATION"]["body"]
    check("DIMENSION_POPULATION", len(duration["dimensions"]) == 2 and len(duration["non_dimension_spans"]) == 1)
    for dimension in duration["dimensions"]:
        span = dimension["source_span"]
        check("DIMENSION_SPAN", packet["contexts"][0]["locator"]["byte_start"] <= span["byte_start"] < span["byte_end"] <= packet["contexts"][0]["locator"]["byte_end"])
        chunk = xml[span["byte_start"]:span["byte_end"]]
        check("DIMENSION_RAW", dimension["axis_token"].encode() in chunk and dimension["container"] == "segment")
        if dimension["form"] == "typed":
            check("TYPED_RAW_AND_NAMESPACES", b"K&#x31;" in chunk and dimension["member_qname"]["tag"] == "Unknown")
        else:
            check("EXPLICIT_DIMENSION", dimension["member_token"] == "t:East" and dimension["member_qname"] == {"namespace_uri": NS["t"], "local_name": "East"})
    check("NON_DIMENSION_RAW", xml[duration["non_dimension_spans"][0]["byte_start"]:duration["non_dimension_spans"][0]["byte_end"]] == b"<t:qualifier>draft</t:qualifier>")
    for entry in packet["units"]:
        key = entry["xml_id"]
        body, element = by_key[key]["body"], elements[key]
        check("UNIT_GROUP:" + key, element.tag == XI + "unit")
        check("UNIT_EVIDENCE:" + key, all(body[k] == entry[k] for k in ["xml_id", "numerator", "denominator"]))
        measure_tokens = [e.text for e in element.iter(XI + "measure")]
        check("UNIT_ORDER_MULTIPLICITY:" + key, [m["token"] for m in body["numerator"] + body["denominator"]] == measure_tokens)
        divide = element.find(XI + "divide")
        for side, xml_side in [("numerator", "unitNumerator"), ("denominator", "unitDenominator")]:
            expected_tokens = [e.text for e in (divide.find(XI + xml_side) if divide is not None else element if side == "numerator" else [])]
            check("UNIT_SIDE:" + key + ":" + side, [m["token"] for m in body[side]] == expected_tokens)
        for measure in body["numerator"] + body["denominator"]:
            prefix, local = measure["token"].split(":", 1)
            check("MEASURE_QNAME:" + key, measure["qname"] == {"namespace_uri": NS[prefix], "local_name": local})
        check("UNIT_OCCURRENCE:" + key, body["occurrence_ref"] == record_ref(by_key["occ-" + key]))
    for fact in packet["facts"]:
        key = fact["xml_id"]
        body, context, element = by_key[key]["body"], by_key["ctx-" + key]["body"], elements[key]
        value, expected = body["value"], EXPECTED_VALUES[key]
        hint = "fraction" if key in ("F_FRACTION", "F_FRACZERO") else "text" if key in ("F_TEXT", "F_XMLCONTENT") else "unknown" if key == "F_MISSINGTYPE" else "decimal"
        check("FIXTURE_TYPE_HYPOTHESIS:" + key, fact["type_hypothesis"] == hint)
        check("SOURCE_CHILD_CONTENT:" + key, fact["has_child_content"] == bool(list(element)))
        check("SOURCE_FRACTION_TOKENS:" + key, fact["numerator_token"] == element.findtext(XI + "numerator") and fact["denominator_token"] == element.findtext(XI + "denominator"))
        check("CANDIDATE_VALUE:" + key, value["tag"] == expected[0] and (len(expected) == 1 or value["rational"] == {"n": expected[1], "d": expected[2]}))
        if value["tag"] == "Fraction":
            check("FRACTION_COMPONENTS:" + key, value["numerator_token"] == "1" and value["denominator_token"] == "3")
        if value["tag"] == "Text":
            check("XML_TEXT_DECODING:" + key, value["text"] == "Caf\u00e9 & Co")
        check("LITERAL_TEXT:" + key, body["reported_text"] == fact["reported_text"] == "".join(element.itertext()))
        check("SOURCE_ATTRIBUTES:" + key, body["source_attributes"] == fact["attributes"] == [{"name": k, "value": v} for k, v in element.attrib.items()])
        for field, attribute in [("context_id_token", "contextRef"), ("unit_id_token", "unitRef"), ("decimals", "decimals"), ("precision", "precision"), ("explicit_language", "{http://www.w3.org/XML/1998/namespace}lang")]:
            expected_field = {"tag": "Present", "token": element.attrib[attribute]} if attribute in element.attrib else {"tag": "Absent"}
            check("SOURCE_TOKEN:" + key + ":" + field, body[field] == fact[field] == expected_field)
        check("CONCEPT:" + key, body["concept"] == fact["concept"] == {"namespace_uri": NS["t"], "local_name": element.tag.split("}")[1]})
        check("LANGUAGE_NOT_DEFAULTED:" + key, body["effective_language"]["tag"] == "Unknown")
        for name in ["legal_entity", "book", "perimeter", "basis", "currency_or_unit", "calendar", "dimensions"]:
            check("FINANCIAL_UNKNOWN:" + key + ":" + name, context[name]["tag"] == "Unknown" and bool(context[name]["reason"]))
        cid = element.attrib.get("contextRef", "")
        if cid == "C_DURATION":
            expected_time = {"tag": "Duration", "start": "2024-01-01", "end_exclusive": "2025-01-01"}
        elif cid == "C_INSTANT":
            expected_time = {"tag": "Instant", "date": "2024-12-31"}
        else:
            expected_time = None
        check("FINANCIAL_TIME:" + key, context["time"] == expected_time if expected_time else context["time"]["tag"] == "Unknown")
        if cid in by_key:
            check("CONTEXT_JOIN:" + key, context["source_context_ref"] == record_ref(by_key[cid]))
        else:
            check("MISSING_CONTEXT:" + key, context["source_context_ref"].get("tag") == "Unknown")
        uid = element.attrib.get("unitRef", "").strip()
        if uid in by_key:
            check("UNIT_JOIN:" + key, context["source_unit_ref"] == record_ref(by_key[uid]))
        else:
            check("MISSING_UNIT:" + key, context["source_unit_ref"].get("tag") == ("NotApplicable" if fact["type_hypothesis"] == "text" else "Unknown"))
        check("ASSERTION_CONTEXT:" + key, body["context_ref"] == record_ref(by_key["ctx-" + key]))
        check("ASSERTION_OCCURRENCE:" + key, body["occurrence_refs"] == [record_ref(by_key["occ-" + key])])
    # Reference integrity is checked after semantic checks so mutations cannot pass
    # merely by creating a stale digest that conceals the intended semantic test.
    by_digest = {record_ref(r)["digest"]: r for r in records}
    for record in records:
        check("DEPENDENCY_SET:" + record["key"], record["dependencies"] == ref_set(refs(record["body"])))
        for ref in record["dependencies"]:
            check("REF_CLOSURE:" + record["key"], ref["digest"] in by_digest and record_ref(by_digest[ref["digest"]]) == ref)
    visiting, visited = set(), set()

    def visit(digest):
        check("ACYCLIC_REFERENCE", digest not in visiting)
        if digest in visited:
            return
        visiting.add(digest)
        for ref in by_digest[digest]["dependencies"]:
            visit(ref["digest"])
        visiting.remove(digest)
        visited.add(digest)

    for digest in by_digest:
        visit(digest)
    mapping = by_key["synthetic-mapping"]["body"]
    excluded = {"ConversionMethod", "LegacyImport", "ImportMapping", "ImportComparison"}
    outputs = [record_ref(r) for r in records if r["kind"] not in excluded]
    check("IMPORT_OUTPUT_SET", mapping["outputs"] == ref_set(outputs) and bool(outputs))
    expected_pairs = {(r["digest"], "/body/" + f) for r in outputs for f in by_digest[r["digest"]]["body"]}
    pairs = [(m["target_ref"]["digest"], m["target_path"]) for m in mapping["field_mappings"]]
    check("FIELD_MAPPING_COVERAGE", len(pairs) == len(set(pairs)) and set(pairs) == expected_pairs)
    origins = {"synthetic-source": ""}
    for group in ["contexts", "units", "facts"]:
        for i, entry in enumerate(packet[group]):
            path = "/" + group + "/" + str(i)
            origins[entry["xml_id"]] = origins["occ-" + entry["xml_id"]] = path
            if group == "facts":
                origins["ctx-" + entry["xml_id"]] = path
    for item in mapping["field_mappings"]:
        original = pointer(packet, item["source_path"])
        record = by_digest[item["target_ref"]["digest"]]
        target = pointer(record, item["target_path"])
        field = item["target_path"].removeprefix("/body/")
        alias = {"SourceVersion": {"original_bytes_ref": "source_blob", "document_identity": "fixture_id"},
                 "ReportedAssertion": {"source_attributes": "attributes"}}.get(record["kind"], {}).get(field, field)
        own_path = origins[record["key"]]
        field_path = own_path + "/" + alias
        try:
            direct_equal = canonical(pointer(packet, field_path)) == canonical(target)
        except (KeyError, IndexError, TypeError, ValueError):
            direct_equal = False
        check("MAPPING_OWNING_ENTRY", item["source_path"] == (field_path if direct_equal else own_path))
        check("MAPPING_RELATION", item["relation"] == ("equal_decoded_value" if direct_equal else "explicit_conversion"))
        if item["relation"] == "equal_decoded_value":
            check("EQUAL_DECODED_MAPPING", canonical(original) == canonical(target))
        else:
            check("NAMED_CONVERSION", item["conversion_method_ref"] == record_ref(by_key["native-xbrl-method"]))
    comparison = by_key["synthetic-comparison"]["body"]
    check("COMPARISON_COVERS_OUTPUTS", comparison["output_digests"] == sorted(r["digest"] for r in outputs))
    check("COMPARISON_COVERS_MAPPINGS", comparison["mapping_ref"] == record_ref(by_key["synthetic-mapping"]) and comparison["field_mapping_count"] == len(pairs))
    legacy = by_key["synthetic-import"]["body"]
    check("LEGACY_FORMAT", legacy["format"] == "authored_native_xbrl_packet.proposed.v1")
    check("LEGACY_ORIGINAL_BYTES", legacy["original_bytes_ref"] == blob(OUT / "native-packet.json") and legacy["original_id"] == packet["fixture_id"])
    check("LEGACY_LINKS", legacy["decoder_ref"] == record_ref(by_key["native-xbrl-method"]) and legacy["portable_ref"] == record_ref(by_key["synthetic-mapping"]) and legacy["comparison_ref"] == record_ref(by_key["synthetic-comparison"]))
    check("METHOD_SPECIFICATION_BYTES", by_key["native-xbrl-method"]["body"]["specification_ref"] == blob(ROOT / "docs/design/proposal/architecture/native-xbrl-translation-proposed-v1.md"))
    check("METHOD_EVIDENCE", by_key["native-xbrl-method"]["body"]["evidence_mode"] == "specification_example" and by_key["native-xbrl-method"]["body"]["name"] == "authored-fixture-native-xbrl-proposed-v1")
    return checks


def rebuild_refs(original, modified):
    """Propagate altered identities in this topologically ordered in-memory fixture.

    Preserve supplied dependency lists, including deliberate omissions/duplicates.
    Do not repair the semantic corruption that a negative case is testing.
    """
    old_by_key = {r["key"]: r for r in original}
    replacements = {}

    def replace(value):
        if isinstance(value, dict):
            if set(value) == {"kind", "schema", "digest"}:
                return deepcopy(replacements.get(canonical(value), value))
            return {k: replace(v) for k, v in value.items()}
        if isinstance(value, list):
            return [replace(v) for v in value]
        return value

    result = []
    for record in modified:
        changed = replace(record)
        changed["dependencies"] = sorted(changed["dependencies"], key=canonical)
        if changed["kind"] == "ImportMapping":
            changed["body"]["outputs"] = sorted(changed["body"]["outputs"], key=canonical)
        replacements[canonical(record_ref(old_by_key[record["key"]]))] = record_ref(changed)
        result.append(changed)
    return result


def corruption_checks(packet, records, profile, xml):
    results = []

    def case(name, expected_code, mutate):
        p, r, s = deepcopy(packet), deepcopy(records), deepcopy(profile)
        by = {entry["key"]: entry["body"] for entry in r}
        mutate(p, r, s, by)
        r = rebuild_refs(records, r)
        try:
            check_material(p, r, s, xml)
        except ValueError as error:
            require(str(error) == expected_code, "WRONG_MUTATION_DIAGNOSTIC:" + name + ":" + str(error))
            results.append({"case": name, "diagnostic": str(error), "rejected": True, "dependent_refs_rebuilt": True})
        else:
            raise ValueError("CORRUPTION_ACCEPTED:" + name)

    def value_case(name, key, value, code=None):
        case(name, code or "CANDIDATE_VALUE:" + key, lambda p, r, s, b: b[key].update(value=value))

    decimal_zero = {"tag": "Decimal", "rational": {"n": "0", "d": "1"}}
    value_case("nil_is_not_zero", "F_NIL", decimal_zero)
    value_case("empty_is_not_default_zero", "F_EMPTY", decimal_zero)
    value_case("decimals_is_not_scaling", "F_DEC", {"tag": "Decimal", "rational": {"n": "120500", "d": "1"}})
    value_case("fraction_components_preserved", "F_FRACTION", {"tag": "Fraction", "numerator_token": "2", "denominator_token": "3", "rational": {"n": "1", "d": "3"}}, "FRACTION_COMPONENTS:F_FRACTION")
    value_case("xml_decoded_text_preserved", "F_TEXT", {"tag": "Text", "text": "Cafe & Co"}, "XML_TEXT_DECODING:F_TEXT")
    value_case("rational_must_be_reduced", "F_DEC", {"tag": "Decimal", "rational": {"n": "482", "d": "4"}}, "UNION")
    value_case("mixed_content_not_scalar", "F_XMLCONTENT", {"tag": "Text", "text": "ABC"})
    case("missing_context_not_guessed", "MISSING_CONTEXT:F_MISSING", lambda p, r, s, b: b["ctx-F_MISSING"].update(source_context_ref=b["ctx-F_ZERO"]["source_context_ref"]))
    case("datetime_not_guessed_date", "FINANCIAL_TIME:F_DATETIME", lambda p, r, s, b: b["ctx-F_DATETIME"].update(time={"tag": "Instant", "date": "2024-12-31"}))
    case("instant_not_shifted", "FINANCIAL_TIME:F_ZERO", lambda p, r, s, b: b["ctx-F_ZERO"].update(time={"tag": "Instant", "date": "2025-01-01"}))
    case("duration_end_is_exclusive", "FINANCIAL_TIME:F_DEC", lambda p, r, s, b: b["ctx-F_DEC"]["time"].update(end_exclusive="2024-12-31"))
    case("publication_not_inferred", "LITERAL", lambda p, r, s, b: b["synthetic-source"]["publication_evidence"].update(tag="Known"))
    case("financial_basis_not_inferred", "LITERAL", lambda p, r, s, b: b["ctx-F_DEC"]["basis"].update(tag="Known"))
    case("raw_unit_whitespace_preserved", "SOURCE_TOKEN:F_DEC:unit_id_token", lambda p, r, s, b: b["F_DEC"]["unit_id_token"].update(token="U_USD"))
    case("duplicate_fact_occurrence_not_dropped", "OUTPUT_POPULATION", lambda p, r, s, b: r.remove(next(v for v in r if v["key"] == "F_DUP")))

    def unit_change(p, b, key, transform):
        entry = next(e for e in p["units"] if e["xml_id"] == key)
        transform(entry)
        b[key].update(numerator=deepcopy(entry["numerator"]), denominator=deepcopy(entry["denominator"]))

    case("numerator_denominator_not_merged", "UNIT_SIDE:U_RATE:numerator", lambda p, r, s, b: unit_change(p, b, "U_RATE", lambda e: e.update(numerator=e["numerator"] + e["denominator"], denominator=[])))
    case("measure_order_preserved", "UNIT_ORDER_MULTIPLICITY:U_PRODUCT", lambda p, r, s, b: unit_change(p, b, "U_PRODUCT", lambda e: e["numerator"].reverse()))
    case("measure_multiplicity_preserved", "UNIT_ORDER_MULTIPLICITY:U_PRODUCT", lambda p, r, s, b: unit_change(p, b, "U_PRODUCT", lambda e: e["numerator"].pop()))

    def context_change(p, b, transform):
        transform(p["contexts"][0])
        for field in ["dimensions", "non_dimension_spans", "period"]:
            b["C_DURATION"][field] = deepcopy(p["contexts"][0][field])

    case("dimension_default_not_inserted", "DIMENSION_COUNT:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e["dimensions"].append(deepcopy(e["dimensions"][0]))))
    case("dimension_axis_not_relabelled", "DIMENSION_AXIS:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e["dimensions"][0]["axis_qname"].update(local_name="Class")))
    case("dimension_container_preserved", "DIMENSION_FORM_CONTAINER:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e["dimensions"][0].update(container="scenario")))
    case("typed_member_exact_span", "DIMENSION_SPAN_CONTENT:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e["dimensions"][1].update(source_span=deepcopy(e["dimensions"][0]["source_span"]))))
    case("non_dimensional_content_not_dropped", "NON_DIMENSION_COUNT:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e.update(non_dimension_spans=[])))
    case("period_form_preserved", "PERIOD_FORM:C_DURATION", lambda p, r, s, b: context_change(p, b, lambda e: e["period"].update(form="forever")))
    case("negative_byte_offset_rejected", "SPAN_RANGE", lambda p, r, s, b: p["facts"][0]["locator"].update(byte_start=-1))
    case("byte_locator_cannot_skip_fact", "LOCATOR_NONOVERLAP:F_DEC", lambda p, r, s, b: p["facts"][0]["locator"].update(byte_start=p["facts"][1]["locator"]["byte_start"], byte_end=p["facts"][1]["locator"]["byte_end"]))
    case("byte_locator_identifies_own_element", "LOCATOR_DECODED_ELEMENT:C_DURATION", lambda p, r, s, b: p["contexts"][0]["locator"].update(p["contexts"][0]["dimensions"][0]["source_span"]))
    case("type_hypothesis_not_silent", "FIXTURE_TYPE_HYPOTHESIS:F_MISSINGTYPE", lambda p, r, s, b: next(e for e in p["facts"] if e["xml_id"] == "F_MISSINGTYPE").update(type_hypothesis="decimal"))
    case("child_content_flag_checked", "SOURCE_CHILD_CONTENT:F_XMLCONTENT", lambda p, r, s, b: p["facts"][-1].update(has_child_content=False))
    case("source_packet_closed", "CLOSED_FIELDS", lambda p, r, s, b: p.update(admitted=True))
    case("candidate_has_no_admission", "LITERAL", lambda p, r, s, b: b["F_DEC"].update(interpretation_status="admitted"))
    case("record_body_closed", "CLOSED_FIELDS", lambda p, r, s, b: b["F_DEC"].update(posting_authority=True))
    case("unknown_reason_required", "EMPTY_REASON", lambda p, r, s, b: b["synthetic-source"]["acquisition"].update(reason="  "))
    case("legacy_packet_blob_not_xml_blob", "LEGACY_ORIGINAL_BYTES", lambda p, r, s, b: b["synthetic-import"].update(original_bytes_ref=p["source_blob"]))
    case("negative_blob_length_rejected", "BLOB_LENGTH", lambda p, r, s, b: b["synthetic-import"]["original_bytes_ref"].update(byte_length=-1))
    case("field_mapping_cannot_be_omitted", "FIELD_MAPPING_COVERAGE", lambda p, r, s, b: b["synthetic-mapping"]["field_mappings"].pop())
    case("field_mapping_cannot_be_duplicated", "FIELD_MAPPING_COVERAGE", lambda p, r, s, b: b["synthetic-mapping"]["field_mappings"].append(deepcopy(b["synthetic-mapping"]["field_mappings"][0])))

    def unrelated_mapping(p, r, s, b):
        target = record_ref(next(e for e in r if e["key"] == "ctx-F_DEC"))
        item = next(m for m in b["synthetic-mapping"]["field_mappings"] if m["target_ref"] == target and m["target_path"] == "/body/time")
        item["source_path"] = "/facts/1"

    case("conversion_uses_own_occurrence", "MAPPING_OWNING_ENTRY", unrelated_mapping)
    case("dependency_cannot_be_omitted", "DEPENDENCY_SET:F_DEC", lambda p, r, s, b: next(e for e in r if e["key"] == "F_DEC")["dependencies"].pop())
    case("dependency_cannot_be_duplicated", "DEPENDENCY_SET:F_DEC", lambda p, r, s, b: next(e for e in r if e["key"] == "F_DEC")["dependencies"].append(deepcopy(next(e for e in r if e["key"] == "F_DEC")["dependencies"][0])))

    def dangling(p, r, s, b):
        b["synthetic-source"]["acquisition"]["obligation_refs"].append({"kind": "Obligation", "schema": "accdsl.proposed.obligation.v1", "digest": "a" * 64})
        source = next(e for e in r if e["key"] == "synthetic-source")
        source["dependencies"] = ref_set(refs(source["body"]))

    case("dangling_typed_ref_rejected", "REF_CLOSURE:synthetic-source", dangling)
    for name, raw, expected in [("duplicate_json_key", '{"x":1,"x":2}', "DUPLICATE_JSON_KEY"),
                                ("json_float", '{"x":1.5}', "NON_INTEGER_JSON_NUMBER"),
                                ("json_nan", '{"x":NaN}', "NON_INTEGER_JSON_NUMBER")]:
        try:
            decode(raw)
        except ValueError as error:
            require(str(error) == expected, "WRONG_JSON_DIAGNOSTIC:" + name)
            results.append({"case": name, "diagnostic": str(error), "rejected": True, "dependent_refs_rebuilt": False})
        else:
            raise ValueError("CORRUPTION_ACCEPTED:" + name)
    typed(-7, "Int", profile)
    results.append({"case": "signed_integer_is_valid", "accepted": True})
    return results


def check_preservation(preparation):
    checks = []
    for row in read(OUT / "protected-inputs.json"):
        require(sha((ROOT / row["path"]).read_bytes()) == row["sha256"], "PROTECTED_INPUT:" + row["path"])
        checks.append("PROTECTED_INPUT:" + row["path"])
    for row in read(OUT / "source-anchors.json"):
        source = (ROOT / row["path"]).read_bytes()
        excerpt = b"".join(source.splitlines(keepends=True)[row["start_line"] - 1:row["end_line"]])
        require(sha(source) == row["sha256"] and sha(excerpt) == row["excerpt_sha256"] and excerpt.decode() == row["excerpt_utf8"], "SOURCE_ANCHOR")
        checks.append("SOURCE_ANCHOR:" + row["path"] + ":" + str(row["start_line"]))
    require(sha((ROOT / ".git/index").read_bytes()) == preparation["index_sha256"], "INDEX_PRESERVED")
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == preparation["git_commit"], "COMMIT_PRESERVED")
    require(subprocess.check_output(["git", "diff", "--cached", "--binary"], cwd=ROOT) == b"", "STAGED_DIFF_EMPTY")
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines()
    require(dirty == preparation["tracked_dirty"] and len(dirty) == 36, "DIRTY_ENTRIES_PRESERVED")
    checks.extend(["INDEX_PRESERVED", "COMMIT_PRESERVED", "STAGED_DIFF_EMPTY", "DIRTY_ENTRIES_PRESERVED"])
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="Exclusively create check evidence and run manifest; default is read-only replay")
    args = parser.parse_args()
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    if args.record:
        require(not (OUT / "checks.json").exists() and not (OUT / "run-manifest.json").exists(), "RECORD_ALREADY_EXISTS")
    preparation, p = read(OUT / "preparation.json"), read(OUT / "profile.json")
    packet, records, xml = read(OUT / "native-packet.json"), read(OUT / "portable-records.json"), (OUT / "source.xml").read_bytes()
    checks = check_preservation(preparation) + check_material(packet, records, p, xml)
    require(preparation["fixture_counts"] == {k: len(packet[k]) for k in ["contexts", "units", "facts"]}, "PREPARATION_COUNTS")
    require(preparation["record_count"] == len(records) and preparation["field_mappings"] == len(next(r for r in records if r["kind"] == "ImportMapping")["body"]["field_mappings"]), "PREPARATION_RECORD_COUNTS")
    checks.extend(["PREPARATION_COUNTS", "PREPARATION_RECORD_COUNTS"])
    mutations = corruption_checks(packet, records, p, xml)
    evidence = {"schema": "accdsl.native_xbrl.documentary_checks.v1", "evidence_mode": "specification_example", "upstream_executed": False,
                "checks": checks, "check_count": len(checks), "corruption_and_primitive_cases": mutations,
                "case_count": len(mutations), "records": len(records), "fixture_counts": preparation["fixture_counts"],
                "field_mappings": preparation["field_mappings"], "product_acceptance": "not_established"}
    if args.record:
        names = ["source.xml", "profile.json", "native-packet.json", "portable-records.json", "source-anchors.json", "protected-inputs.json", "preparation.json",
                 "common.py", "profile_definitions.py", "prepare.py", "verify.py", "README.md"]
        paths = [OUT / n for n in names] + [ROOT / PLAN, ROOT / SPEC]
        write_once(OUT / "checks.json", evidence)
        manifest = {"schema": "accdsl.native_xbrl.documentary_run.v1", "command": COMMAND + " --record", "git_commit": preparation["git_commit"],
                    "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": str(time.monotonic() - tick),
                    "environment": {"python_executable": sys.executable, "python_version": platform.python_version(), "platform": platform.platform(),
                                    "execution": "CPU-only standard-library static file checks; no numerical framework or GPU detection/import", "gpu": "N/A", "conda_env": "N/A"},
                    "seeds": "N/A: deterministic authored fixtures", "data_version": packet["source_blob"], "plan": PLAN,
                    "result": str((OUT / "result.md").relative_to(ROOT)), "checks": blob(OUT / "checks.json"),
                    "inputs_and_code": [{"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes())} for path in paths],
                    "tracked_dirty_count": len(preparation["tracked_dirty"]), "index_sha256": preparation["index_sha256"],
                    "upstream_executed": False, "interpretation": "Bounded documentary consistency only; not parser/taxonomy/accounting or runtime acceptance"}
        write_once(OUT / "run-manifest.json", manifest)
        mode = "initial evidence recorded"
    else:
        require(read(OUT / "checks.json") == evidence, "SAVED_CHECKS_EXACT_REPLAY")
        manifest = read(OUT / "run-manifest.json")
        require(manifest["checks"] == blob(OUT / "checks.json"), "SAVED_CHECKS_BYTES")
        for row in manifest["inputs_and_code"]:
            require(sha((ROOT / row["path"]).read_bytes()) == row["sha256"], "RUN_INPUT:" + row["path"])
        mode = "read-only replay passed"
    print(json.dumps({"status": mode, "checks": len(checks), "corruption_and_primitive_cases": len(mutations),
                      "records": len(records), "field_mappings": preparation["field_mappings"], "wall_seconds": round(time.monotonic() - tick, 3),
                      "upstream_executed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
