"""Exact authored diagnostics; no acquired program or empirical model executes."""
from fractions import Fraction as F
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]


def load(path):
    return json.loads(path.read_text())


def bind(path):
    return {"path": str(path.relative_to(R)), "sha256": sha256(path.read_bytes()).hexdigest()}


def rational_root(x):
    n, d = isqrt(x.numerator), isqrt(x.denominator)
    assert n*n == x.numerator and d*d == x.denominator
    return F(n, d)


def mean(xs, ps):
    return sum((x*p for x, p in zip(xs, ps)), F(0))


def variance(xs, ps):
    m = mean(xs, ps)
    return mean([(x-m)**2 for x in xs], ps)


def ph(xs, ps, rho):
    assert len(xs) == len(ps) and len(xs) > 0
    assert all(x >= 0 for x in xs) and list(xs) == sorted(xs)
    assert all(p > 0 for p in ps) and sum(ps) == 1
    tails = [F(1)]
    for p in ps:
        tails.append(tails[-1]-p)
    assert rho in (1, 2), "only the two predeclared exact diagnostic parameters"
    ts = tails if rho == 1 else [rational_root(t) for t in tails]
    weights = [a-b for a, b in zip(ts, ts[1:])]
    weighted = mean(xs, weights)
    integrated = xs[0] + sum(((xs[j]-xs[j-1])*ts[j] for j in range(1, len(xs))), F(0))
    return weights, weighted, integrated


def quantile(xs, ps, alpha):
    assert 0 < alpha <= 1
    total = F(0)
    for x, p in zip(xs, ps):
        total += p
        if total >= alpha:
            return x
    raise AssertionError("unreachable with a complete law")


def quantile_integral(xs, ps, alpha):
    assert 0 <= alpha < 1
    total = numerator = F(0)
    for x, p in zip(xs, ps):
        right = total+p
        numerator += x*max(F(0), right-max(total, alpha))
        total = right
    assert total == 1
    return numerator/(1-alpha)


def derive():
    claims = {}

    def expect(name, got, wanted):
        assert got == wanted, (name, got, wanted)
        claims[name] = True

    printed = [F(1,2), F(-1,2)]
    expect("printed PH weights violate positivity", any(w < 0 for w in printed), True)
    expect("printed PH denominator is zero at rho=1", sum(printed), F(0))
    expect("printed unnormalised PH sum is -2", mean([F(0),F(4)], printed), F(-2))
    ph_cases = []
    for xs, ps, rho, wanted in [
        ([F(0),F(4)], [F(1,2)]*2, 1, F(2)),
        ([F(0),F(4),F(10)], [F(5,9),F(1,3),F(1,9)], 2, F(14,3)),
        ([F(4)]*3, [F(5,9),F(1,3),F(1,9)], 2, F(4)),
        ([F(0),F(4),F(4)], [F(5,9),F(1,3),F(1,9)], 2, F(8,3)),
        ([F(0),F(4)], [F(5,9),F(4,9)], 2, F(8,3)),
    ]:
        weights, weighted, integrated = ph(xs, ps, rho)
        label = "PH case " + str(len(ph_cases)+1)
        expect(label+" mass", sum(weights), F(1))
        expect(label+" positivity", all(w >= 0 for w in weights), True)
        expect(label+" independent integral", integrated, wanted)
        expect(label+" weighted value", weighted, wanted)
        ph_cases.append({"losses":list(map(str,xs)),"probabilities":list(map(str,ps)),
                         "rho":rho,"weights":list(map(str,weights)),"value":str(weighted),
                         "integral":str(integrated)})
    expect("rho2 ordinary mean", mean([F(0),F(4),F(10)], [F(5,9),F(1,3),F(1,9)]), F(22,9))

    xs = list(map(F, [0,2,8,14])); ps = [F(1,4)]*4
    lower, upper = xs[:2], xs[2:]
    cm = [mean(a,[F(1,2)]*2) for a in [lower,upper]]
    cv = [variance(a,[F(1,2)]*2) for a in [lower,upper]]
    expect("conditional means", cm, [F(1),F(11)])
    expect("conditional variances", cv, [F(1),F(9)])
    expected_sd = mean([rational_root(v) for v in cv], [F(1,2)]*2)
    expected_var = mean(cv,[F(1,2)]*2)
    total_var = variance(xs,ps)
    expect("expected future SD", expected_sd, F(2))
    expect("expected future variance", expected_var, F(5))
    expect("initial variance", total_var, F(30))
    expect("conditional total variance", expected_var+variance(cm,[F(1,2)]*2), total_var)
    expect("Jensen and total variance strict bounds", expected_sd**2 < expected_var < total_var, True)
    d1 = [F(6)-cm[j//2] for j in range(4)]
    d2 = [cm[j//2]-xs[j] for j in range(4)]
    expect("CDR path telescoping", [a+b for a,b in zip(d1,d2)], [F(6)-x for x in xs])
    expect("first CDR mean", mean(d1,ps), F(0))
    expect("second CDR mean", mean(d2,ps), F(0))
    expect("first CDR variance", variance(d1,ps), F(25))
    expect("second CDR variance", variance(d2,ps), F(5))
    expect("CDR covariance", mean([a*b for a,b in zip(d1,d2)],ps), F(0))
    expect("CDRs are dependent despite zero covariance", set(abs(x) for x in d2[:2]) != set(abs(x) for x in d2[2:]), True)
    expect("RMS upper bound is not pathwise", cv[1] > expected_var, True)

    tx = list(map(F,[0,4,10])); tp = [F(1,2),F(1,4),F(1,4)]; alpha = F(3,5)
    q = quantile(tx,tp,alpha)
    es = quantile_integral(tx,tp,alpha)
    cdfq = sum(p for x,p in zip(tx,tp) if x <= q)
    boundary = (sum(x*p for x,p in zip(tx,tp) if x>q) + q*(cdfq-alpha))/(1-alpha)
    expect("atomic quantile", q, F(4))
    expect("integrated quantile tail", es, F(31,4))
    expect("independent partial-atom tail", boundary, es)
    expect("tail strictly above quantile differs", F(10) != es, True)
    expect("tail at-or-above quantile differs", F(7) != es, True)
    expect("relative expected shortfall", es-mean(tx,tp), F(17,4))
    expect("ES0 equals mean", quantile_integral(tx,tp,F(0)), mean(tx,tp))
    expect("CDF at ES", sum(p for x,p in zip(tx,tp) if x<=es), F(3,4))
    expect("CDF coverage is not exact quantile equivalence", quantile(tx,tp,F(3,4)) != es, True)
    expect("VaR match at upper interval endpoint", quantile(tx,tp,F(3,4)), F(4))
    expect("VaR match excludes lower interval endpoint", quantile(tx,tp,F(1,2)), F(0))
    return {"source_formula_verdict":"accepted manuscript Appendix 2 printed weights are wrong relative to its integral",
            "exact_assertions":len(claims), "assertions":claims, "ph_cases":ph_cases,
            "future_information":{"outcomes":list(map(str,xs)),"probabilities":list(map(str,ps)),
                "conditional_means":list(map(str,cm)),"conditional_variances":list(map(str,cv)),
                "expected_SD":"2","root_expected_variance":"sqrt(5)","initial_SD":"sqrt(30)",
                "CDR1":list(map(str,d1)),"CDR2":list(map(str,d2)),"covariance":"0","independent":False},
            "atom_case":{"quantile":str(q),"expected_shortfall":str(es),"relative_ES":"17/4",
                "exact_VaR_equivalent_for_ES":None,"CDF_coverage_at_ES":"3/4","quantile4_levels":"(1/2,3/4]"},
            "stochastic_run":False,"law_or_risk_preference_selected_for_entity":False}


def check():
    result = derive()
    assert result == load(U / "comparison.json")
    ledger = load(U / "source-ledger.json")
    for item in ledger["bindings"]:
        assert bind(R/item["path"]) == item, item["path"]
    for item in ledger["anchors"]:
        path=R/item["source"]["path"]
        assert bind(path)==item["source"]
        assert path.read_text()[item["start"]:item["end"]] == item["excerpt"]
    for item in load(U / "render-review.json")["pages"]:
        assert bind(R/item["image"]["path"]) == item["image"]
    assert bind(R/ledger["paper"]["path"]) == ledger["paper"]
    assert ledger["paper"]["sha256"] == "d195f617ffacdb72e6f5f445d54b829cb1f47ad6dc4d0fbe55cc67b06cc70268"
    return {"status":"source-specific derivations and exact diagnostics passed",
            "exact_assertions":result["exact_assertions"],"ph_cases":len(result["ph_cases"]),
            "source_bindings":len(ledger["bindings"]),"anchors":len(ledger["anchors"]),
            "rendered_pages_inspected":6,"printed_source_formula_rejected":True,
            "empirical_execution":False,"whole_rows_closed":0}
