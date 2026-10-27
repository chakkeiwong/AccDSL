"""Finite source-only period interpretation; no installed XBRL processor."""
from collections import Counter
from copy import deepcopy
from datetime import date, timedelta
from functools import lru_cache
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"
spec = importlib.util.spec_from_file_location("period_source_helpers", B / "r06-numeric-lexical-20261020/compare.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
load, bind, digest = m.load, m.bind, m.digest
INSTANCE, COVERAGE = m.INSTANCE, m.COVERAGE
PACKET = B / "native-full-portable-20261018/native-packet.json"
PORTABLE = B / "native-full-portable-20261018/portable-records.json"
INVENTORY = B / "native-shape-inventory-20261018/inventory.json"
X = "{http://www.xbrl.org/2003/instance}"
DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")


def leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def month_days(year):
    return [31, 29 if leap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def ordinal(year, month, day):
    prior = year - 1
    return 365 * prior + prior // 4 - prior // 100 + prior // 400 + sum(month_days(year)[:month-1]) + day


def following(year, month, day):
    if day < month_days(year)[month-1]:
        return year, month, day+1
    if month < 12:
        return year, month+1, 1
    return year+1, 1, 1


def boundary(token, role):
    assert role in ("startDate", "endDate", "instant")
    collapsed = m.collapse(token)
    match = DATE.fullmatch(collapsed)
    base = {"raw_token": token, "collapsed": collapsed, "role": role,
            "timezone": None, "timezone_status": "absent_not_inferred"}
    if match is None:
        return base | {"status": "outside_scope", "reason": "not selected four-digit untimezoned date form"}
    year, month, day = map(int, match.groups())
    if not (year >= 1 and 1 <= month <= 12 and 1 <= day <= month_days(year)[month-1]):
        return base | {"status": "invalid_calendar_date"}
    observed = date(year, month, day)
    serial = ordinal(year, month, day)
    assert observed.toordinal() == serial
    shift = int(role != "startDate")
    target = following(year, month, day) if shift else (year, month, day)
    if target[0] > 9999:
        return base | {"status": "outside_scope", "reason": "implied endpoint exceeds bounded calendar implementation"}
    independent = observed + timedelta(days=shift)
    assert target == (independent.year, independent.month, independent.day)
    assert ordinal(*target) == serial + shift == independent.toordinal()
    spelling = "%04d-%02d-%02dT00:00:00" % target
    assert independent.isoformat() + "T00:00:00" == spelling
    return base | {"status": "supported", "source_date_ordinal": serial,
                   "implied_boundary": spelling, "boundary_ordinal": serial+shift,
                   "calendar_day_shift": shift}


def period(tokens):
    # Ordered pairs retain repeated children; a dict could silently remove them.
    names = [pair[0] for pair in tokens]
    if names == ["forever"]:
        if tokens[0][1] not in ("", None):
            return {"status": "invalid_period_shape", "reason": "nonempty forever"}
        return {"status": "supported", "form": "forever", "required_periodType": "duration",
                "calendar_day_span": None, "timezone": None}
    if names == ["instant"]:
        result = boundary(tokens[0][1], "instant")
        return {"status": result["status"], "form": "instant", "instant": result,
                "required_periodType": "instant", "calendar_day_span": None}
    if names != ["startDate", "endDate"]:
        return {"status": "invalid_period_shape", "reason": "ordered period child sequence"}
    start, end = [boundary(value, role) for role, value in tokens]
    if start["status"] != "supported" or end["status"] != "supported":
        return {"status": "outside_scope" if "outside_scope" in (start["status"], end["status"]) else "invalid_calendar_date",
                "form": "duration", "start": start, "end": end}
    span = end["boundary_ordinal"] - start["boundary_ordinal"]
    return {"status": "supported" if span > 0 else "end_not_after_start",
            "form": "duration", "required_periodType": "duration",
            "start": start, "end": end, "calendar_day_span": span,
            "span_role": "explanatory_calendar_day_difference_not_elapsed_UTC_or_financial_year_fraction"}


def compatible(period_type, interpreted):
    if interpreted["status"] != "supported":
        return False
    return period_type in ("instant", "duration") and period_type == interpreted["required_periodType"]


def tokens_of(element):
    assert element.tag == X + "period" and not element.attrib
    assert not (element.text or "").strip()
    result = []
    for child in element:
        assert child.tag.startswith(X) and not child.attrib and len(child) == 0
        assert not (child.tail or "").strip()
        result.append([child.tag[len(X):], child.text])
    return result


def span_check(span, raw):
    piece = raw[span["byte_start"]:span["byte_end"]]
    assert digest(piece) == span["slice_sha256"]
    assert len(piece) == span["byte_length"]
    assert piece.decode() == span["raw_utf8"]


def source_context(row, actual, raw):
    span_check(row["span"], raw)
    assert row["id"] == actual.get("id") and actual.tag == X + "context"
    actual_periods = actual.findall(X + "period")
    assert len(actual_periods) == 1
    tokens = tokens_of(actual_periods[0])
    recorded = row["period"]
    assert recorded["name"] == X + "period" and not recorded["attributes"]
    assert all(not c["attributes"] and not c["children"] for c in recorded["children"])
    assert tokens == [[c["name"].removeprefix(X), c["text"]] for c in recorded["children"]]
    return tokens


@lru_cache(None)
def declarations(path):
    root, scopes = m.schema(path)
    return root, scopes, {e.get("name"): e for e in root if e.tag == m.XS + "element"}


def derive():
    raw = INSTANCE.read_bytes()
    root = ET.fromstring(raw)
    actual = {e.get("id"): e for e in root if e.get("id")}
    packet = load(PACKET)
    coverage = load(COVERAGE)
    inventory = {r["id"]: r for r in load(INVENTORY)["entries"] if r["category"] == "context"}
    source_contexts = {r["body"]["xml_id"]: r for r in load(PORTABLE) if r["kind"] == "XbrlContextEvidence"}
    contexts = []
    for row in packet["contexts"]:
        ident = row["id"]
        tokens = source_context(row, actual[ident], raw)
        inv = inventory[ident]
        assert all(inv["span"][k] == row["span"][k] for k in inv["span"])
        interpretation = period(tokens)
        assert interpretation["status"] == "supported", ident
        form = interpretation["form"]
        expected = {"form": form, "start_token": tokens[0][1] if form == "duration" else None,
                    "end_token": tokens[1][1] if form == "duration" else None,
                    "instant_token": tokens[0][1] if form == "instant" else None}
        assert source_contexts[ident]["body"]["period"] == expected
        contexts.append({"context_id": ident, "source_span": row["span"], "raw_period": tokens,
                         "portable_period": expected, "interpretation": interpretation,
                         "financial_time": "Unknown_unchanged", "full_validation": "not_run"})
    assert len(contexts) == len(root.findall(X + "context")) == len(inventory) == len(source_contexts) == 193
    by_id = {r["context_id"]: r for r in contexts}
    concept_records = []
    for name, row in sorted(coverage["concepts"].items()):
        m.checked_anchor(row["declaration_anchor"])
        path = row["declaration_anchor"]["source_path"]
        schema, scopes, decls = declarations(path)
        declaration = decls[row["source_attributes"]["name"]]
        assert declaration.attrib == row["source_attributes"]
        assert "{" + schema.get("targetNamespace") + "}" + declaration.get("name") == name
        assert m.expanded(declaration.get("substitutionGroup"), scopes[id(declaration)]) == X + "item"
        declared = declaration.get(X + "periodType")
        assert declared in ("duration", "instant")
        concept_records.append({"concept": name, "periodType": declared,
                                "declaration_anchor": row["declaration_anchor"]})
    concepts = {r["concept"]: r for r in concept_records}
    financial = {r["key"].removeprefix("ctx-"): r["body"] for r in load(PORTABLE) if r["kind"] == "Context"}
    facts = []
    for row in coverage["occurrences"]:
        ident = row["fact_id"]
        span_check(row["source_span"], raw)
        source = actual[ident]
        assert source.tag == row["source_concept"] and source.attrib == row["source_attributes"]
        context_id = row["source_context_id"]
        assert source.get("contextRef") == context_id
        interpretation = by_id[context_id]["interpretation"]
        declared = concepts[row["source_concept"]]["periodType"]
        assert compatible(declared, interpretation), ident
        assert financial[ident]["time"]["tag"] == financial[ident]["calendar"]["tag"] == "Unknown"
        facts.append({"fact_id": ident, "concept": row["source_concept"], "context_id": context_id,
                      "declared_periodType": declared, "period_form": interpretation["form"],
                      "compatible": True, "financial_time": financial[ident]["time"],
                      "source_span": {k: row["source_span"][k] for k in ("byte_start", "byte_end", "slice_sha256")},
                      "full_validation": "not_run"})
    assert len(facts) == len(financial) == 1127 and len(concept_records) == 382
    return contexts, concept_records, facts


def check():
    checks = 0

    def require(condition, label):
        nonlocal checks
        assert condition, label
        checks += 1

    ledger = load(U / "source-ledger.json")
    for binding in ledger["bindings"]:
        require(bind(R / binding["path"]) == binding, binding["path"])
    for anchor in ledger["anchors"]:
        path = R / anchor["source"]["path"]
        require(bind(path) == anchor["source"], anchor["id"])
        require("\n".join(path.read_text().splitlines()[anchor["first_line"]-1:anchor["last_line"]]) == anchor["excerpt"], anchor["id"])
    contexts, concepts, facts = derive()
    for name, rows in (("contexts", contexts), ("concepts", concepts), ("facts", facts)):
        require(rows == load(U / (name + ".json")), name + " exact records")
    fixtures = load(U / "fixtures.json")
    for fixture in fixtures:
        observed = period(fixture["tokens"])
        for key, expected in fixture["expected"].items():
            require(observed[key] == expected, fixture["id"] + " " + key)
        for key in ("start", "end", "instant"):
            if key in fixture:
                for field, expected in fixture[key].items():
                    require(observed[key][field] == expected, fixture["id"] + " " + key + " " + field)
        if "periodType" in fixture:
            require(compatible(fixture["periodType"], observed) == fixture["compatible"], fixture["id"] + " compatibility")
    controls = load(U / "altered-controls.json")
    by_id = {r["context_id"]: r for r in contexts}
    for control in controls["period_changes"]:
        original = by_id[control["context_id"]]
        altered = period(control["tokens"])
        if control["effect"] == "different_boundary":
            require(altered != original["interpretation"], control["id"])
        else:
            require(altered["status"] == control["effect"], control["id"])
    for row in facts:
        wrong = "instant" if row["declared_periodType"] == "duration" else "duration"
        require(not compatible(wrong, by_id[row["context_id"]]["interpretation"]), row["fact_id"] + " altered declaration")
    packet = load(PACKET)
    raw = INSTANCE.read_bytes()
    actual = ET.fromstring(raw).find(X + "context")
    for alteration in controls["source_corruptions"]:
        changed = deepcopy(packet["contexts"][0])
        if alteration == "span_hash":
            changed["span"]["slice_sha256"] = "0" * 64
        elif alteration == "date_token":
            changed["period"]["children"][0]["text"] = "2020-01-01"
        elif alteration == "date_role":
            changed["period"]["children"][0]["name"] = X + "instant"
        else:
            raise AssertionError(alteration)
        try:
            source_context(changed, actual, raw)
        except AssertionError:
            require(True, alteration)
        else:
            raise AssertionError("accepted corrupted source " + alteration)
    require(Counter(r["interpretation"]["form"] for r in contexts) == {"duration": 98, "instant": 95}, "context forms")
    return {"assertions": checks, "contexts": len(contexts), "duration_contexts": 98, "instant_contexts": 95,
            "facts": len(facts), "concepts": len(concepts), "fixtures": len(fixtures),
            "opposite_periodType_rejections": len(facts), "source_corruptions_rejected": len(controls["source_corruptions"]),
            "altered_period_controls": len(controls["period_changes"]),
            "input_bindings": len(ledger["bindings"]), "source_anchors": len(ledger["anchors"]),
            "new_acquisitions": 0, "upstream_executed": False, "full_validation": "not_run", "whole_rows_closed": 0}
