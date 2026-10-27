"""Fixtures and exact expected outcomes authored before the reference selector.

Expected fractions below are independent hand calculations and the protected
20261014 lifecycle fixture, never copied from selector output.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def context():
    return dict(entity="synthetic-parent", book="consolidated-CU",
        head="synthetic-dated-head-2025", view="synthetic-view-2026-03-01",
        population="parent-and-supplied-subsidiaries", ordinary_class="ordinary-A",
        share_basis="post-two-for-one-split", currency="CU", currency_scale="1",
        rule_version="EU2023/1803-original-IAS33-historical",
        period=dict(start="2025-01-01", end_exclusive="2026-01-01"))


def base(n="12000", total="15000", d="162480/73"):
    ctx = context()
    binding = digest(ctx)
    return dict(wire="OrderedEPS/1", operation="report", context=ctx,
        context_ref=binding,
        inventory=dict(status="complete", ids=[], support=None),
        scope=dict(nonparticipating_rights=True, independent_additive_effects=True,
                   fixed_effects=True, support=None),
        basic=dict(status="ready", context_ref=binding, support=None,
            continuing_numerator=n, total_numerator=total, denominator=d,
            attribution_complete=True, chronology_complete=True), series=[])


def candidate(name, a, b, total=None, start="2025-01-01", end="2026-01-01",
              kind="period_end"):
    return dict(id=name, resolution="candidate", context_ref=digest(context()),
        support=None, continuing_increment=a, total_increment=a if total is None else total,
        share_increment=b, earnings_complete=True, time_weighting_complete=True,
        potential_windows=[dict(start=start, end_exclusive=end)],
        actual_windows=([dict(start=end, end_exclusive="2026-01-01")]
                        if kind == "converted" else []),
        end_kind=kind, actual_in_basic=(kind == "converted"))


def bundle(n, total, d, c_eps, t_eps, disc_eps):
    return dict(continuing_numerator=n, total_numerator=total,
        denominator=d, continuing_eps=c_eps, total_eps=t_eps,
        discontinued_eps=disc_eps)


def author():
    cases = []

    def add(name, request, included, expected, order=None):
        request["inventory"]["ids"] = [s["id"] for s in request["series"]]
        cases.append(dict(id=name, request=request,
            expected=dict(status="conditional_complete", included=included,
                          order=order if order is not None else included, diluted=expected)))

    r = base()
    r["series"] = [candidate("preference", "2000", "400"),
                   candidate("debt", "600", "22080/73", start="2025-07-01"),
                   candidate("options", "0", "240")]
    baseline = deepcopy(r)
    answer = bundle("12600", "15600", "202080/73", "7665/1684", "4745/842", "1825/1684")
    add("existing-three-series", r, ["options", "debt"], answer,
        ["options", "debt", "preference"])
    r = deepcopy(baseline)
    r["basic"]["continuing_numerator"] = "-5000"
    add("continuing-loss-total-profit", r, [],
        bundle("-5000", "15000", "162480/73", "-9125/4062", "9125/1354", "18250/2031"),
        ["options", "debt", "preference"])
    r = deepcopy(baseline)
    r["basic"]["total_numerator"] = "-9000"
    add("continuing-profit-total-loss", r, ["options", "debt"],
        bundle("12600", "-8400", "202080/73", "7665/1684", "-2555/842", "-12775/1684"),
        ["options", "debt", "preference"])
    r = base("100", "120", "10")
    r["series"] = [candidate("tie-z", "5", "5"), candidate("tie-a", "2", "2")]
    add("equal-incremental-ratios", r, ["tie-a", "tie-z"],
        bundle("107", "127", "17", "107/17", "127/17", "20/17"))
    r = base("100", "120", "10")
    r["series"] = [candidate("equal-z", "20", "2"), candidate("equal-a", "10", "1")]
    add("neutral-series-excluded", r, [], bundle("100", "120", "10", "10", "12", "2"),
        ["equal-a", "equal-z"])
    r = base("-20", "20", "10")
    r["series"] = [candidate("options", "0", "5"), candidate("negative-effect", "-15", "5")]
    add("signed-loss-dilution", r, ["negative-effect"],
        bundle("-35", "5", "15", "-7/3", "1/3", "8/3"),
        ["negative-effect", "options"])
    r = base("0", "0", "10")
    r["series"] = [candidate("neutral", "0", "5"), candidate("positive", "1", "1")]
    add("zero-control", r, [], bundle("0", "0", "10", "0", "0", "0"), ["neutral", "positive"])
    r = base("100", "80", "10")
    r["series"] = [candidate("separate-total-effect", "2", "2", total="-1")]
    add("different-total-consequence", r, ["separate-total-effect"],
        bundle("102", "79", "12", "17/2", "79/12", "-23/12"))
    r = deepcopy(baseline)
    r["basic"].update(continuing_numerator="12300", total_numerator="15300", denominator="173520/73")
    r["series"][1] = candidate("debt", "300", "11040/73", start="2025-07-01", end="2025-10-01", kind="converted")
    add("actual-conversion-nonoverlap", r, ["options", "debt"], answer, ["options", "debt", "preference"])
    r = base("100", "120", "10")
    r["series"] = [candidate("lapsed", "0", "13104/73", end="2025-10-01", kind="lapsed")]
    add("lapse-window", r, ["lapsed"],
        bundle("100", "120", "13834/73", "3650/6917", "4380/6917", "730/6917"))
    r = base("100", "120", "10")
    r["series"] = [dict(id="out-of-money", resolution="no_effect", context_ref=r["context_ref"],
        support=None, continuing_increment="0", total_increment="0", share_increment="0",
        reason="separate option method: no incremental shares and no earnings effect")]
    add("visible-no-effect", r, [], bundle("100", "120", "10", "10", "12", "2"), ["out-of-money"])
    add("empty-complete-inventory", base("100", "120", "10"), [],
        bundle("100", "120", "10", "10", "12", "2"))

    # Premises are independent inputs, not fabricated evidence of a real company.
    premises = {"kind": "authored synthetic premises; not real issuer evidence",
        "baseline_source": "protected 20261014 EPS lifecycle case and 3.14 eps-lifecycle.tex",
        "scope": "supplied fixed independent additive effects; historical method only",
        "cases": [{"id": c["id"], "premises": c["request"]} for c in deepcopy(cases)]}
    payload = json.dumps(premises, indent=2) + "\n"
    (OUT / "premises.json").write_text(payload)
    support_hash = hashlib.sha256(payload.encode()).hexdigest()
    for case in cases:
        req = case["request"]
        for node, anchor in [(req["inventory"], "inventory"), (req["scope"], "scope"),
                             (req["basic"], "basic")] + [(s, "series/" + s["id"]) for s in req["series"]]:
            node["support"] = dict(path=str((OUT / "premises.json").relative_to(ROOT)),
                sha256=support_hash, anchor="cases/" + case["id"] + "/" + anchor)
    (OUT / "fixtures.json").write_text(json.dumps(cases, indent=2) + "\n")
    print(json.dumps({"authored_cases": len(cases), "premises_sha256": support_hash}))


if __name__ == "__main__":
    author()
