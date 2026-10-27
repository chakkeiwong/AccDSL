"""One-shot construction of authored fixture expectations; never imports Arelle."""
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction
import re
import subprocess
import time
import xml.etree.ElementTree as ET

from common import OUT, ROOT, blob, canonical, pointer, record_ref, ref_set, refs, rational, sha, unknown, write_once
from profile_definitions import profile

SPEC = "docs/design/proposal/architecture/native-xbrl-translation-proposed-v1.md"
PLAN = "docs/plans/accounting-native-xbrl-translation-20261018.md"
PREFIX = "docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/arelle__"
NS = {"xbrli": "http://www.xbrl.org/2003/instance", "xsi": "http://www.w3.org/2001/XMLSchema-instance",
      "xbrldi": "http://xbrl.org/2006/xbrldi", "t": "urn:accdsl:synthetic:tax", "iso4217": "http://www.xbrl.org/2003/iso4217"}
XI = "{" + NS["xbrli"] + "}"
XD = "{" + NS["xbrldi"] + "}"


def qname(token):
    prefix, local = token.split(":", 1)
    return {"namespace_uri": NS[prefix], "local_name": local}


def raw_field(element, name):
    return {"tag": "Present", "token": element.attrib[name]} if name in element.attrib else {"tag": "Absent"}


def candidate_time(period):
    try:
        if period["form"] == "duration":
            start, end = period["start_token"], period["end_token"]
            if not all(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v or "") for v in [start, end]):
                raise ValueError()
            finish = date.fromisoformat(end) + timedelta(days=1)
            if date.fromisoformat(start) >= finish:
                raise ValueError()
            return {"tag": "Duration", "start": start, "end_exclusive": finish.isoformat()}
        if period["form"] == "instant" and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", period["instant_token"] or ""):
            return {"tag": "Instant", "date": date.fromisoformat(period["instant_token"]).isoformat()}
    except (ValueError, OverflowError):
        pass
    return unknown("No supported date-only financial-time interpretation")


def candidate_value(fact):
    nil = next((a["value"] for a in fact["attributes"] if a["name"] == "{" + NS["xsi"] + "}nil"), None)
    if nil in ("1", "true"):
        return {"tag": "Nil"}
    if nil not in (None, "0", "false"):
        return unknown("Invalid explicit nil token")
    hint = fact["type_hypothesis"]
    if fact["has_child_content"] and hint != "fraction":
        return unknown("Structured content has no supported scalar interpretation")
    if hint == "text":
        return {"tag": "Text", "text": fact["reported_text"]}
    try:
        if hint == "fraction":
            num, den = fact["numerator_token"], fact["denominator_token"]
            if not all(re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", v or "") for v in [num, den]):
                raise ValueError()
            quotient = Fraction(num) / Fraction(den)
            return {"tag": "Fraction", "numerator_token": num, "denominator_token": den, "rational": rational(quotient)}
        if hint == "decimal" and re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", fact["reported_text"]):
            return {"tag": "Decimal", "rational": rational(Fraction(fact["reported_text"]))}
    except (ValueError, ZeroDivisionError):
        return unknown("Invalid fraction or zero denominator; no numeric quotient")
    return unknown("No supported finite decimal or established scalar type")


def main():
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    names = ["profile.json", "native-packet.json", "portable-records.json", "source-anchors.json", "protected-inputs.json", "preparation.json"]
    for name in names:
        assert not (OUT / name).exists(), name
    raw = (OUT / "source.xml").read_bytes()
    root = ET.fromstring(raw)  # Only this authored local fixture; no external resource loading.

    def locator(element, ordinal):
        key = element.attrib["id"]
        marker = ('id="' + key + '"').encode()
        assert raw.count(marker) == 1
        start = raw.rfind(b"<", 0, raw.index(marker))
        opening_end = raw.index(b">", start) + 1
        tag = raw[start + 1:raw.index(b" ", start)].decode()
        end = opening_end if raw[opening_end - 2:opening_end] == b"/>" else raw.index(('</' + tag + '>').encode(), opening_end) + len(tag) + 3
        return {"byte_start": start, "byte_end": end, "element_id": key, "element_path": "/1/" + str(ordinal)}

    def child_span(parent_loc, start_token, end_token):
        start = raw.index(start_token.encode(), parent_loc["byte_start"], parent_loc["byte_end"])
        end = raw.index(end_token.encode(), start, parent_loc["byte_end"]) + len(end_token)
        return {"byte_start": start, "byte_end": end}

    packet = {"fixture_id": "authored-native-xbrl-v1", "evidence_mode": "specification_example", "upstream_executed": False,
              "source_blob": blob(OUT / "source.xml"), "origin": "authored-fixture:source.xml",
              "namespace_bindings": [{"prefix": k, "namespace_uri": v} for k, v in NS.items()],
              "contexts": [], "units": [], "facts": []}
    for ordinal, element in enumerate(root, 1):
        loc = locator(element, ordinal)
        entry = {"xml_id": element.attrib["id"], "locator": loc}
        if element.tag == XI + "context":
            ident = element.find(XI + "entity/" + XI + "identifier")
            per = element.find(XI + "period")
            start, end, instant = (per.findtext(XI + name) for name in ["startDate", "endDate", "instant"])
            form = "duration" if start is not None and end is not None else "instant" if instant is not None else "forever" if per.find(XI + "forever") is not None else "other"
            dimensions, other = [], []
            for container in ["segment", "scenario"]:
                node = element.find((XI + "entity/" if container == "segment" else "") + XI + container)
                for child in list(node) if node is not None else []:
                    local = child.tag.split("}")[-1]
                    prefix = "xbrldi" if child.tag.startswith(XD) else "t"
                    span = child_span(loc, "<" + prefix + ":" + local, "</" + prefix + ":" + local + ">")
                    if child.tag in [XD + "explicitMember", XD + "typedMember"]:
                        explicit = child.tag == XD + "explicitMember"
                        dimensions.append({"container": container, "form": "explicit" if explicit else "typed", "axis_token": child.attrib["dimension"],
                                           "axis_qname": qname(child.attrib["dimension"]), "member_token": child.text if explicit else None,
                                           "member_qname": qname(child.text) if explicit else unknown("Typed member retained as XML with inherited namespaces"), "source_span": span})
                    else:
                        other.append(span)
            entry.update(identifier={"scheme": ident.attrib["scheme"], "text": ident.text},
                         period={"form": form, "start_token": start, "end_token": end, "instant_token": instant},
                         dimensions=dimensions, non_dimension_spans=other)
            packet["contexts"].append(entry)
        elif element.tag == XI + "unit":
            divide = element.find(XI + "divide")
            top = divide.find(XI + "unitNumerator") if divide is not None else element
            bottom = divide.find(XI + "unitDenominator") if divide is not None else []
            entry.update(numerator=[{"token": e.text, "qname": qname(e.text)} for e in top],
                         denominator=[{"token": e.text, "qname": qname(e.text)} for e in bottom])
            packet["units"].append(entry)
        else:
            local = element.tag.split("}")[-1]
            hint = {"Amount": "decimal", "Fraction": "fraction", "Description": "text"}.get(local, "unknown")
            entry.update(concept={"namespace_uri": NS["t"], "local_name": local},
                         context_id_token=raw_field(element, "contextRef"), unit_id_token=raw_field(element, "unitRef"),
                         reported_text="".join(element.itertext()),
                         attributes=[{"name": k, "value": v} for k, v in element.attrib.items()],
                         decimals=raw_field(element, "decimals"), precision=raw_field(element, "precision"),
                         explicit_language=raw_field(element, "{http://www.w3.org/XML/1998/namespace}lang"),
                         type_hypothesis=hint, has_child_content=bool(list(element)),
                         numerator_token=element.findtext(XI + "numerator"), denominator_token=element.findtext(XI + "denominator"))
            packet["facts"].append(entry)
    write_once(OUT / "native-packet.json", packet)
    p = profile()
    write_once(OUT / "profile.json", p)
    records, outputs, mappings = [], [], []

    def add(kind, key, body, source_path=None):
        record = {"kind": kind, "schema": p["records"][kind]["schema"], "key": key, "revision": 0,
                  "body": body, "dependencies": ref_set(refs(body))}
        ref = record_ref(record)
        records.append(record)
        if source_path is not None:
            outputs.append(ref)
            for field, value in body.items():
                alias = {"SourceVersion": {"original_bytes_ref": "source_blob", "document_identity": "fixture_id"},
                         "ReportedAssertion": {"source_attributes": "attributes"}}.get(kind, {}).get(field, field)
                path = source_path + "/" + alias
                try:
                    equal = canonical(pointer(packet, path)) == canonical(value)
                except (KeyError, IndexError, TypeError, ValueError):
                    equal = False
                mappings.append({"source_path": path if equal else source_path, "target_ref": ref, "target_path": "/body/" + field,
                                 "relation": "equal_decoded_value" if equal else "explicit_conversion",
                                 **({} if equal else {"conversion_method_ref": method})})
        return ref

    method = add("ConversionMethod", "native-xbrl-method", {"name": "authored-fixture-native-xbrl-proposed-v1",
                 "algorithm": "Source-preserving proposed construction, explicit fixture type hypotheses, exact base-ten/fraction arithmetic, date-only candidate interpretation; no admission",
                 "specification_ref": blob(ROOT / SPEC), "evidence_mode": "specification_example"})
    source = add("SourceVersion", "synthetic-source", {"original_bytes_ref": packet["source_blob"], "media_type": "application/xml", "origin": packet["origin"],
                 "acquisition": unknown("Synthetic fixture has no acquisition receipt"), "issuer": unknown("No actual issuer"), "document_identity": packet["fixture_id"],
                 "publication_evidence": unknown("No publication evidence"), "vintage_evidence": unknown("No historical-byte evidence"), "namespace_bindings": packet["namespace_bindings"]}, "")
    contexts, units = {}, {}
    for group, kind, target in [("contexts", "XbrlContextEvidence", contexts), ("units", "XbrlUnitEvidence", units)]:
        for i, entry in enumerate(packet[group]):
            path = "/" + group + "/" + str(i)
            occurrence = add("UnitOccurrence", "occ-" + entry["xml_id"], {"source_ref": source, "locator": entry["locator"], "package_root_key": packet["fixture_id"], "parent_key": "xml-root", "disposition": "retained"}, path)
            body = {k: v for k, v in entry.items() if k != "locator"}
            body["occurrence_ref"] = occurrence
            target[entry["xml_id"]] = add(kind, entry["xml_id"], body, path)
    for i, fact in enumerate(packet["facts"]):
        path, key = "/facts/" + str(i), fact["xml_id"]
        occurrence = add("UnitOccurrence", "occ-" + key, {"source_ref": source, "locator": fact["locator"], "package_root_key": packet["fixture_id"], "parent_key": "xml-root", "disposition": "retained"}, path)
        cid = fact["context_id_token"].get("token", "")
        uid = fact["unit_id_token"].get("token", "").strip()
        per = next((e["period"] for e in packet["contexts"] if e["xml_id"] == cid), None)
        context = add("Context", "ctx-" + key, {"source_context_ref": contexts.get(cid, unknown("Missing or ambiguous source context")),
                      "source_unit_ref": units.get(uid, {"tag": "NotApplicable", "reason": "Authored nonnumeric fixture type"} if fact["type_hypothesis"] == "text" else unknown("Missing or ambiguous numeric unit")),
                      **{name: unknown("Not established by XML context, taxonomy or unit") for name in ["legal_entity", "book", "perimeter", "basis", "currency_or_unit", "calendar", "dimensions"]},
                      "time": candidate_time(per) if per is not None else unknown("No resolved source period"), "interpretation_status": "candidate"}, path)
        assertion = {k: fact[k] for k in ["concept", "context_id_token", "unit_id_token", "reported_text", "decimals", "precision", "explicit_language"]}
        assertion.update(occurrence_refs=[occurrence], context_ref=context, source_attributes=fact["attributes"], value=candidate_value(fact),
                         effective_language=unknown("Effective/inherited/configured language not established"), interpretation_status="candidate")
        add("ReportedAssertion", key, assertion, path)
    mapping = add("ImportMapping", "synthetic-mapping", {"outputs": ref_set(outputs), "field_mappings": mappings})
    comparison = add("ImportComparison", "synthetic-comparison", {"mapping_ref": mapping, "output_digests": sorted(r["digest"] for r in outputs),
                     "field_mapping_count": len(mappings), "verdict": "correspondence_checked", "evidence_mode": "specification_example"})
    add("LegacyImport", "synthetic-import", {"format": "authored_native_xbrl_packet.proposed.v1", "original_bytes_ref": blob(OUT / "native-packet.json"),
        "original_id": packet["fixture_id"], "decoder_ref": method, "portable_ref": mapping, "comparison_ref": comparison})
    write_once(OUT / "portable-records.json", records)
    anchors = [("ModelInstanceObject.py", 174, 201), ("ModelInstanceObject.py", 308, 410),
               ("ModelInstanceObject.py", 1011, 1102), ("ModelInstanceObject.py", 1140, 1158),
               ("ModelInstanceObject.py", 1171, 1263), ("ModelInstanceObject.py", 1466, 1509),
               ("ModelInstanceObject.py", 1544, 1555), ("ModelInstanceObject.py", 1584, 1598),
               ("ModelObject.py", 225, 230), ("ModelObject.py", 258, 295), ("ModelObject.py", 302, 312),
               ("XmlUtil.py", 961, 1034), ("XmlUtil.py", 1126, 1160)]
    anchor_rows = []
    for filename, start, end in anchors:
        path = ROOT / (PREFIX + filename)
        excerpt = b"".join(path.read_bytes().splitlines(keepends=True)[start - 1:end])
        anchor_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path.read_bytes()), "start_line": start,
                            "end_line": end, "excerpt_utf8": excerpt.decode(), "excerpt_sha256": sha(excerpt)})
    write_once(OUT / "source-anchors.json", anchor_rows)
    protected = ["docs/design/proposal/architecture/" + n for n in ["language-ir-contract-v1.md", "evidence-contract-v3.md", "time-contract-v2.md", "interfaces-contract-v1.md", "architecture-integration-v1.md", "cross-contract-amendment-v1.md"]]
    protected += ["data/accounting-master/selected-reuse-20261015/" + n for n in ["source-selection.json", "exchanges.json", "exchange-envelope.schema.json"]]
    protected += ["data/accounting-master/reuse-field-boundary-20261018/source-boundary.md", "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"]
    protected += ["data/accounting-master/early-conversion-integration-20261018/" + n for n in ["assessment-successor.json", "integration-bindings.json", "operation-successor.json"]]
    protected += sorted(set(row["path"] for row in anchor_rows))
    write_once(OUT / "protected-inputs.json", [{"path": n, "sha256": sha((ROOT / n).read_bytes())} for n in protected])
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True).splitlines()
    write_once(OUT / "preparation.json", {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": str(time.monotonic() - tick),
               "command": "python3 data/accounting-master/native-xbrl-translation-20261018/prepare.py", "plan": PLAN, "specification": SPEC,
               "tracked_dirty": dirty, "index_sha256": sha((ROOT / ".git/index").read_bytes()),
               "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "fixture_counts": {k: len(packet[k]) for k in ["contexts", "units", "facts"]}, "record_count": len(records), "field_mappings": len(mappings)})
    print("Authored preparation written; " + str(len(records)) + " proposed records, " + str(len(mappings)) + " field mappings; no upstream execution.")


if __name__ == "__main__":
    main()
