"""Independently specified refusal cases, not inferred from selector output."""
from copy import deepcopy


def author(fixtures):
    baseline = fixtures[0]["request"]
    cases = []

    def add(name, status, code, mutate):
        request = deepcopy(baseline)
        mutate(request)
        cases.append(dict(id=name, request=request,
                          expected_status=status, expected_code=code))

    def set_basic(key, value):
        return lambda r: r["basic"].__setitem__(key, value)

    def set_series(key, value):
        return lambda r: r["series"][1].__setitem__(key, value)

    add("missing-total-consequence", "rejected", "schema", lambda r: r["series"][1].pop("total_increment"))
    add("unknown-field", "rejected", "schema", lambda r: r.__setitem__("post_journal", True))
    add("unknown-operation", "rejected", "schema", lambda r: r.__setitem__("operation", "commit"))
    add("incomplete-inventory", "unresolved", "incomplete_inventory", lambda r: r["inventory"].__setitem__("status", "incomplete"))
    add("missing-inventoried-series", "rejected", "inventory_mismatch", lambda r: r["series"].pop())
    add("uninventoried-series", "rejected", "inventory_mismatch", lambda r: r["inventory"]["ids"].pop())
    add("duplicate-series", "rejected", "duplicate_series", lambda r: r["series"].append(deepcopy(r["series"][1])))
    add("duplicate-inventory-id", "rejected", "schema", lambda r: r["inventory"]["ids"].append("debt"))
    add("participating-rights", "unsupported", "unsupported_scope", lambda r: r["scope"].__setitem__("nonparticipating_rights", False))
    add("dependent-effects", "unsupported", "unsupported_scope", lambda r: r["scope"].__setitem__("independent_additive_effects", False))
    add("unfixed-consequences", "unsupported", "unsupported_scope", lambda r: r["scope"].__setitem__("fixed_effects", False))
    add("unresolved-attribution", "unresolved", "incomplete_basic", set_basic("attribution_complete", False))
    add("unresolved-basic-chronology", "unresolved", "incomplete_basic", set_basic("chronology_complete", False))
    add("unresolved-earnings", "unresolved", "incomplete_effects", set_series("earnings_complete", False))
    add("unresolved-weighting", "unresolved", "incomplete_effects", set_series("time_weighting_complete", False))
    for field in ("entity", "population", "book", "head", "view", "share_basis", "currency", "rule_version"):
        add("changed-context-" + field, "rejected", "context_hash_mismatch",
            lambda r, field=field: r["context"].__setitem__(field, "other-context"))
    add("wrong-basic-binding", "rejected", "context_mismatch", set_basic("context_ref", "0" * 64))
    add("wrong-series-binding", "rejected", "context_mismatch", set_series("context_ref", "0" * 64))
    add("reducible-basic-rational", "rejected", "noncanonical_rational", set_basic("denominator", "20/2"))
    add("redundant-unit-denominator", "rejected", "noncanonical_rational", set_series("share_increment", "2/1"))
    for name, text in (("zero-denominator", "1/0"), ("negative-denominator", "1/-2"),
                       ("negative-zero", "-0"), ("leading-zero", "02"),
                       ("float", "0.25"), ("exponent", "1e2")):
        add(name, "rejected", "schema", set_series("share_increment", text))
    add("zero-basic-shares", "rejected", "nonpositive_basic_denominator", set_basic("denominator", "0"))
    add("negative-basic-shares", "rejected", "nonpositive_basic_denominator", set_basic("denominator", "-2"))
    add("zero-candidate-shares", "rejected", "nonpositive_share_increment", set_series("share_increment", "0"))
    add("negative-candidate-shares", "rejected", "nonpositive_share_increment", set_series("share_increment", "-1"))
    add("invalid-calendar-date", "rejected", "schema", lambda r: r["context"]["period"].__setitem__("start", "2025-02-30"))
    add("reversed-period", "rejected", "invalid_period", lambda r: r["context"]["period"].__setitem__("end_exclusive", "2024-01-01"))
    add("window-before-period", "rejected", "invalid_window", lambda r: r["series"][1]["potential_windows"][0].__setitem__("start", "2024-12-31"))
    add("overlapping-potential-windows", "rejected", "overlapping_windows", lambda r: r["series"][1]["potential_windows"].append(deepcopy(r["series"][1]["potential_windows"][0])))
    add("missing-source-bytes", "unresolved", "evidence_unavailable", lambda r: r["series"][1]["support"].__setitem__("path", "data/accounting-master/continuation-integrity-eps-20261016/intentionally-absent-source.json"))
    add("stale-source-hash", "rejected", "evidence_hash_mismatch", lambda r: r["series"][1]["support"].__setitem__("sha256", "0" * 64))

    def disposition(r, kind):
        s = r["series"][1]
        r["series"][1] = {k: s[k] for k in ("id", "context_ref", "support")}
        r["series"][1].update(resolution=kind, reason="independently specified missing/unsupported consequence")

    add("visible-unresolved-series", "unresolved", "unresolved_series", lambda r: disposition(r, "unresolved"))
    add("visible-unsupported-series", "unsupported", "unsupported_series", lambda r: disposition(r, "unsupported"))

    def both(r):
        disposition(r, "unsupported")
        r["inventory"]["status"] = "incomplete"

    add("unsupported-and-unresolved", "blocked", "unsupported_series", both)

    def basic_unresolved(r):
        b = r["basic"]
        r["basic"] = {k: b[k] for k in ("context_ref", "support")}
        r["basic"].update(status="unresolved", reason="ordinary earnings attribution not supplied")

    add("explicit-unresolved-basic", "unresolved", "unresolved_basic", basic_unresolved)

    conversion = next(f["request"] for f in fixtures if f["id"] == "actual-conversion-nonoverlap")
    for name, code, mutate in (
        ("conversion-overlap", "overlapping_windows", lambda s: s["actual_windows"][0].__setitem__("start", "2025-09-30")),
        ("conversion-not-in-basic", "conversion_not_in_basic", lambda s: s.__setitem__("actual_in_basic", False)),
        ("conversion-without-actual-window", "missing_actual_window", lambda s: s.__setitem__("actual_windows", [])),
        ("actual-window-before-potential", "conversion_order", lambda s: s.__setitem__("actual_windows", [dict(start="2025-01-01", end_exclusive="2025-02-01")])),
    ):
        request = deepcopy(conversion)
        mutate(request["series"][1])
        cases.append(dict(id=name, request=request, expected_status="rejected", expected_code=code))
    no_effect = next(f["request"] for f in fixtures if f["id"] == "visible-no-effect")
    request = deepcopy(no_effect)
    request["series"][0]["total_increment"] = "1"
    cases.append(dict(id="nonzero-no-effect", request=request, expected_status="rejected", expected_code="nonzero_no_effect"))
    return cases
