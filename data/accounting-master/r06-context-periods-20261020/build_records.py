"""One-time construction of exact retained period interpretations."""
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def write(name, value):
    with (U / name).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def main():
    assert not (U / "contexts.json").exists(), "one-time construction"
    spec = importlib.util.spec_from_file_location("local_periods", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    contexts, concepts, facts = m.derive()
    for name, rows in (("contexts", contexts), ("concepts", concepts), ("facts", facts)):
        write(name + ".json", rows)
    xbrl = B / "r06-enumeration-domain-20261020/sources/03-xbrl21.visible.txt"
    xsd = U / "sources/xsd-part2.visible.txt"
    sections = [
        ("xbrl_period", xbrl, 3025, 3101),
        ("xbrl_period_equality", xbrl, 3703, 3724),
        ("xbrl_periodType", xbrl, 4474, 4506),
        ("xbrl_dependency_edition", xbrl, 6378, 6390),
        ("xsd_datetime_value", xsd, 1155, 1214),
        ("xsd_datetime_lexical_canonical_timezone", xsd, 1216, 1273),
        ("xsd_datetime_order", xsd, 1274, 1334),
        ("xsd_date_value_lexical", xsd, 1385, 1460),
        ("xsd_date_whitespace", xsd, 4958, 4980),
    ]
    anchors = [{"id": ident, "source": m.bind(path), "first_line": first, "last_line": last,
                "excerpt": "\n".join(path.read_text().splitlines()[first-1:last])}
               for ident, path, first, last in sections]
    inputs = {m.INSTANCE, m.COVERAGE, m.PACKET, m.PORTABLE, m.INVENTORY, xbrl, xsd,
              B / "r06-numeric-lexical-20261020/compare.py",
              B / "r06-enumeration-domain-20261020/extract_visible.py",
              B / "r06-enumeration-domain-20261020/sources/03-xbrl21.body",
              B / "r06-unitless-semantics-20261019/sources/02-dated.body",
              B / "r06-normative-schema-20261018/completion.json",
              R / "docs/design/proposal/architecture/native-full-portable-proposed-v1.md"}
    inputs.update(R / r["declaration_anchor"]["source_path"] for r in concepts)
    write("source-ledger.json", {"date": "2026-10-20", "new_acquisitions": 0,
        "bindings": [m.bind(p) for p in sorted(inputs)], "anchors": anchors,
        "scope": "Finite untimezoned positive four-digit dates; all retained concept/context periodType joins",
        "originals": "Already acquired XBRL 2.1 corrected 2013 and XSD 1.0 Second Edition; frozen acquisition receipts inherited",
        "readable_view": "Imported Visible class; explicit inline-hidden subtrees omitted; original HTML retained"})
    write("acquisitions.json", {"new_acquisitions": 0,
        "reused": [m.bind(B / "r06-enumeration-domain-20261020/acquisitions.json"),
                   m.bind(B / "r06-unitless-semantics-20261019/source-ledger.json")]})
    d = lambda start, end: [["startDate", start], ["endDate", end]]
    instant = lambda value: [["instant", value]]
    fixtures = [
        {"id": "same_day", "tokens": d("2024-09-28", "2024-09-28"),
         "expected": {"status": "supported", "calendar_day_span": 1},
         "start": {"implied_boundary": "2024-09-28T00:00:00", "timezone": None},
         "end": {"implied_boundary": "2024-09-29T00:00:00", "timezone": None}},
        {"id": "observed_year", "tokens": d("2023-10-01", "2024-09-28"),
         "expected": {"status": "supported", "calendar_day_span": 364}},
        {"id": "leap_day", "tokens": d("2024-02-28", "2024-02-29"),
         "expected": {"status": "supported", "calendar_day_span": 2},
         "end": {"implied_boundary": "2024-03-01T00:00:00"}},
        {"id": "leap_century", "tokens": d("2000-02-28", "2000-02-29"),
         "expected": {"status": "supported", "calendar_day_span": 2}},
        {"id": "nonleap_century", "tokens": d("1900-02-28", "1900-03-01"),
         "expected": {"status": "supported", "calendar_day_span": 2}},
        {"id": "year_boundary", "tokens": instant("2024-12-31"),
         "expected": {"status": "supported", "form": "instant"},
         "instant": {"implied_boundary": "2025-01-01T00:00:00", "timezone": None}},
        {"id": "month_boundary", "tokens": instant("2024-04-30"),
         "expected": {"status": "supported"}, "instant": {"implied_boundary": "2024-05-01T00:00:00"}},
        {"id": "source_whitespace", "tokens": instant("\t2024-09-28\r\n"),
         "expected": {"status": "supported"}, "instant": {"collapsed": "2024-09-28"}},
        {"id": "zero_duration_after_mapping", "tokens": d("2024-09-29", "2024-09-28"),
         "expected": {"status": "end_not_after_start", "calendar_day_span": 0}},
        {"id": "negative_duration", "tokens": d("2024-10-01", "2024-09-28"),
         "expected": {"status": "end_not_after_start", "calendar_day_span": -2}},
        {"id": "invalid_leap_day", "tokens": instant("1900-02-29"), "expected": {"status": "invalid_calendar_date"}},
        {"id": "invalid_day", "tokens": instant("2024-04-31"), "expected": {"status": "invalid_calendar_date"}},
        {"id": "invalid_month", "tokens": instant("2024-13-01"), "expected": {"status": "invalid_calendar_date"}},
        {"id": "year_zero_xsd10", "tokens": instant("0000-01-01"), "expected": {"status": "invalid_calendar_date"}},
        *[{"id": ident, "tokens": instant(value), "expected": {"status": "outside_scope"}} for ident, value in [
            ("timezone", "2024-09-28Z"), ("datetime", "2024-09-29T00:00:00"),
            ("lexical_24", "2024-09-28T24:00:00"), ("negative_year", "-0001-01-01"),
            ("long_year", "10000-01-01"), ("boundary_overflow", "9999-12-31"),
            ("unicode_digits", "２０２４-09-28"), ("nonxml_space", "\u00a02024-09-28"),
        ]],
        {"id": "duplicate_instant", "tokens": instant("2024-09-28") * 2, "expected": {"status": "invalid_period_shape"}},
        {"id": "mixed_form", "tokens": d("2024-01-01", "2024-09-28") + instant("2024-09-28"), "expected": {"status": "invalid_period_shape"}},
        {"id": "wrong_order", "tokens": list(reversed(d("2024-01-01", "2024-09-28"))), "expected": {"status": "invalid_period_shape"}},
        {"id": "missing_end", "tokens": [["startDate", "2024-01-01"]], "expected": {"status": "invalid_period_shape"}},
        {"id": "forever_duration", "tokens": [["forever", None]], "expected": {"status": "supported", "form": "forever"},
         "periodType": "duration", "compatible": True},
        {"id": "forever_instant", "tokens": [["forever", None]], "expected": {"status": "supported"},
         "periodType": "instant", "compatible": False},
        {"id": "nonempty_forever", "tokens": [["forever", "2024"]], "expected": {"status": "invalid_period_shape"}},
        {"id": "instant_duration_mismatch", "tokens": instant("2024-09-28"), "expected": {"status": "supported"},
         "periodType": "duration", "compatible": False},
    ]
    write("fixtures.json", fixtures)
    sample = contexts[0]
    assert sample["raw_period"] == d("2023-10-01", "2024-09-28")
    write("altered-controls.json", {
        "source_corruptions": ["span_hash", "date_token", "date_role"],
        "period_changes": [
            {"id": "one_day_shift", "context_id": sample["context_id"], "tokens": d("2023-10-01", "2024-09-27"), "effect": "different_boundary"},
            {"id": "inverted", "context_id": sample["context_id"], "tokens": d("2024-09-29", "2024-09-28"), "effect": "end_not_after_start"},
            {"id": "dropped_end", "context_id": sample["context_id"], "tokens": [["startDate", "2023-10-01"]], "effect": "invalid_period_shape"},
            {"id": "invented_timezone", "context_id": sample["context_id"], "tokens": d("2023-10-01Z", "2024-09-28Z"), "effect": "outside_scope"},
        ],
        "declared_type_mutations": "Flip instant/duration on every one of the 1,127 facts; each must reject compatibility",
    })
    groups = defaultdict(list)
    for row in contexts:
        groups[json.dumps(row["raw_period"], separators=(",", ":"))].append(row["context_id"])
    summary = {"role": "explanatory_only", "distinct_source_period_signatures": len(groups),
               "period_groups": [{"tokens": json.loads(key), "contexts": value} for key, value in groups.items()],
               "duration_day_spans": dict(sorted(Counter(r["interpretation"]["calendar_day_span"]
                                                        for r in contexts if r["interpretation"]["form"] == "duration").items())),
               "fact_forms": dict(Counter(r["period_form"] for r in facts)),
               "concept_forms": dict(Counter(r["periodType"] for r in concepts)),
               "not_concluded": "Period equality does not establish context equality, duplicate facts, economic event dates, UTC elapsed time or financial year fractions."}
    write("descriptive-inventory.json", summary)
    write("source-support-ledger.json", {"classification": "PRIMARY_SPECIFICATION_AND_RETAINED_INSTANCE",
        "identity": "source-ledger.json", "read_scope": "Nine technical/dependency anchors",
        "allowed": "Finite role-specific period boundaries and declared-form consistency",
        "forbidden": ["full XBRL validation", "financial time admission", "actual timezone", "generic dateTime processor", "publication vintage"]})
    write("claim-support-ledger.json", {"claims": [
        {"claim": "Date-only starts map to same-day midnight; ends and instants map to following-day midnight.", "class": "PRIMARY_SOURCE", "anchors": ["xbrl_period"]},
        {"claim": "endDate must imply a strictly later point than startDate.", "class": "PRIMARY_SOURCE", "anchors": ["xbrl_period"]},
        {"claim": "Fact period form must match the declared periodType.", "class": "PRIMARY_SOURCE_WITH_FINITE_JOINS", "anchors": ["xbrl_periodType"], "evidence": "facts.json"},
        {"claim": "Missing timezone does not identify UTC or the machine's zone.", "class": "PRIMARY_SOURCE_BOUNDARY", "anchors": ["xsd_datetime_value", "xsd_datetime_order"]},
        {"claim": "A same-date start/end denotes one calendar day under the selected rule.", "class": "LOCAL_DEDUCTION", "evidence": "fixtures.json", "anchors": ["xbrl_period"]},
        {"claim": "Lexical 24:00:00 and canonical hour range differ; no general lexical ban follows.", "class": "PRIMARY_SOURCE_DISTINCTION", "anchors": ["xsd_datetime_lexical_canonical_timezone", "xbrl_period", "xbrl_dependency_edition"]},
    ]})
    write("backward-snowball-ledger.json", {"scope": "Normative dependencies",
        "leads": [{"source": "XSD 1.0 Second Edition", "status": "Explicitly named by retained XBRL bibliography; retained primary sections inspected"},
                  {"source": "ISO 8601 / timezone authority", "status": "No general conversion or actual reporting-zone claim; restricted XSD form suffices for observed dates"},
                  {"source": "XBRL context/dimension equivalence", "status": "Period equality excerpt read; complete context equality and dimensional validation deferred"}]})
    write("forward-snowball-ledger.json", {"scope": "Retained-version inquiry", "new_queries": 0,
        "status": "No claim of latest processor or later errata completeness"})
    write("citation-venue-ledger.json", {"sources": [
        {"title": "XBRL 2.1", "version": "2003-12-31 with 2013-02-20 corrections", "status": "Retained Recommendation"},
        {"title": "XML Schema Part 2: Datatypes Second Edition", "version": "2004-10-28", "status": "Retained W3C Recommendation"}],
        "citation_metrics": "not applicable", "current_errata_completeness": "not checked"})
    write("omission-risk-ledger.json", {"risks": [
        {"risk": "Lexical end-date comparison loses one day", "response": "Role-specific midnight mapping; same-day and observed reporting-year witnesses"},
        {"risk": "Naive year-length or calendar arithmetic", "response": "Gregorian ordinal and rollover algorithm independently match Python date; leap-century tests"},
        {"risk": "Absent timezone inferred from environment", "response": "No timestamp or timezone APIs; every observed boundary remains untimezoned"},
        {"risk": "Wrong concept periodType ignored", "response": "382 exact declarations and 1,127 joins; every opposite-form mutation rejects"},
        {"risk": "Period agreement promoted to context/accounting equivalence", "response": "All 193 context identities and frozen Unknown financial-time fields retained"},
        {"risk": "Broader dateTime forms falsely declared invalid", "response": "Outside-scope results for timezone/negative/long/dateTime forms; lexical/canonical 24 distinction explicit"},
    ]})
    print(json.dumps({"constructed": True, "contexts": len(contexts), "concepts": len(concepts), "facts": len(facts),
                      "fixtures": len(fixtures), "anchors": len(anchors), "bindings": len(inputs),
                      "distinct_period_signatures": len(groups), "fact_forms": summary["fact_forms"],
                      "duration_day_spans": summary["duration_day_spans"]}))


if __name__ == "__main__":
    main()
