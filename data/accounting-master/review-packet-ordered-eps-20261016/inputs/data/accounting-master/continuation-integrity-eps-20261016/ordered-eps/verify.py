"""Bounded exact conformance and independently enumerated subset diagnostics."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import platform
import sys
import time

from adverse_cases import author
from reference_selector import calculate, canonical, digest, ROOT, OUT


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def subset_oracle(n, d, effects):
    """Recompute every subset ratio; no sorting or sequential admission test."""
    values = []
    for count in range(len(effects) + 1):
        for subset in combinations(range(len(effects)), count):
            numerator = n + sum((effects[i][0] for i in subset), Fraction(0))
            denominator = d + sum((effects[i][1] for i in subset), Fraction(0))
            values.append((numerator / denominator, set(subset)))
    minimum = min(value for value, _ in values)
    minimizers = [subset for value, subset in values if value == minimum]
    # Neutral series can create extra minimizing subsets; strict admission
    # selects exactly the intersection, not an arbitrarily chosen minimizer.
    strict_population = set.intersection(*minimizers)
    return minimum, strict_population, len(values), len(minimizers)


def run():
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    fixtures = json.loads((OUT / "fixtures.json").read_text())
    attempts = sorted(OUT.glob("attempt-[0-9][0-9]"))
    attempt = OUT / ("attempt-%02d" % (len(attempts) + 1))
    attempt.mkdir()
    checks, results = [], []

    def check(name, passed, details=None):
        checks.append(dict(name=name, passed=bool(passed), details=details))

    lock = json.loads((OUT / "authored-input-lock.json").read_text())
    for item in lock["files"]:
        actual = hashlib.sha256((OUT / item["path"]).read_bytes()).hexdigest()
        check("protected-input/" + item["path"], actual == item["sha256"])
    if not all(c["passed"] for c in checks):
        write(attempt / "checks.json", checks)
        raise SystemExit("Protected authored input changed; dependent run stopped")

    # Existing lifecycle is the first calculation; preserve it even on failure.
    for fixture in fixtures:
        request, expected = fixture["request"], fixture["expected"]
        before = canonical(request)
        actual = calculate(request)
        write(attempt / (fixture["id"] + ".json"), actual)
        prefix = "fixture/" + fixture["id"] + "/"
        check(prefix + "status", actual["status"] == expected["status"], actual["issues"])
        check(prefix + "complete-population", [r["id"] for r in actual["trace"] if r["included"]] == expected["included"])
        check(prefix + "trace-order", [r["id"] for r in actual["trace"]] == expected["order"])
        for key, value in expected["diluted"].items():
            check(prefix + key, actual["diluted"] is not None and actual["diluted"][key] == value)
        check(prefix + "determinism", actual == calculate(request))
        check(prefix + "read-only", canonical(request) == before and actual["mutations"] == [])
        check(prefix + "request-binding", actual["request_sha256"] == digest(request))
        if fixture["id"] == "existing-three-series" and not all(c["passed"] for c in checks):
            write(attempt / "checks.json", checks)
            raise SystemExit("Existing example failed; preserved attempt, stop dependent grid")

    adverse = author(fixtures)
    write(attempt / "adverse-inputs.json", adverse)
    # Freeze independently specified expected refusals before evaluating them.
    write(attempt / "adverse-input-lock.json", dict(sha256=hashlib.sha256(
        (attempt / "adverse-inputs.json").read_bytes()).hexdigest()))
    for case in adverse:
        actual = calculate(case["request"])
        results.append(dict(id=case["id"], result=actual))
        prefix = "adverse/" + case["id"] + "/"
        check(prefix + "status", actual["status"] == case["expected_status"], actual["issues"])
        check(prefix + "reason", case["expected_code"] in [i["code"] for i in actual["issues"]])
        check(prefix + "no-partial-diluted-result", actual["diluted"] is None and actual["trace"] == [])
        check(prefix + "no-mutations", actual["mutations"] == [])
    write(attempt / "adverse-results.json", results)

    baseline = fixtures[0]["request"]
    reference = json.loads((attempt / "existing-three-series.json").read_text())
    for index, perm in enumerate(permutations(baseline["series"])):
        req = deepcopy(baseline)
        req["series"] = list(perm)
        req["inventory"]["ids"] = list(reversed(req["inventory"]["ids"]))
        actual = calculate(req)
        check("permutation/%s/selection" % index, actual["diluted"] == reference["diluted"] and actual["trace"] == reference["trace"])

    # This grid is a deterministic arithmetic diagnostic, not stochastic
    # evidence or an accounting applicability test. Parameters precede output.
    spec = dict(numerators=["-6", "-1", "0", "1", "6"], denominators=["1", "3", "7"],
        effects=[["-3/2", "1/2"], ["-1", "2"], ["0", "1"],
                 ["1", "2"], ["2", "2"], ["1", "1"]], series_count=3,
        role="exhaustive finite additive mathematics; no source/fact eligibility conclusion",
        total_rule="basic total=N+4; total increment=continuing increment-1")
    write(attempt / "grid-premises.json", spec)
    support = dict(path=str((attempt / "grid-premises.json").relative_to(ROOT)),
                   sha256=hashlib.sha256((attempt / "grid-premises.json").read_bytes()).hexdigest(),
                   anchor="all deterministic combinations under the recorded parameter grid")
    grid = []
    subset_count = 0
    for n_text, d_text, effect_texts in product(spec["numerators"], spec["denominators"], product(spec["effects"], repeat=3)):
        n, d = Fraction(n_text), Fraction(d_text)
        effects = [(Fraction(a), Fraction(b)) for a, b in effect_texts]
        minimum, selected, count, ties = subset_oracle(n, d, effects)
        subset_count += count
        req = deepcopy(baseline)
        req["basic"].update(continuing_numerator=str(n), total_numerator=str(n+4), denominator=str(d), support=support)
        req["inventory"].update(ids=["grid-0", "grid-1", "grid-2"], support=support)
        req["scope"]["support"] = support
        req["series"] = []
        for index, (a, b) in enumerate(effects):
            series = deepcopy(baseline["series"][2])
            series.update(id="grid-" + str(index), continuing_increment=str(a),
                          total_increment=str(a-1), share_increment=str(b), support=support)
            req["series"].append(series)
        actual = calculate(req)
        actual_selected = {int(r["id"].split("-")[1]) for r in actual["trace"] if r["included"]}
        index = len(grid)
        check("subset-grid/%d/status" % index, actual["status"] == "conditional_complete")
        check("subset-grid/%d/minimum" % index, actual["diluted"] is not None and Fraction(actual["diluted"]["continuing_eps"]) == minimum)
        check("subset-grid/%d/strict-population" % index, actual_selected == selected)
        expected_total = (n+4+sum((effects[i][0]-1 for i in selected), Fraction(0))) / (d+sum((effects[i][1] for i in selected), Fraction(0)))
        check("subset-grid/%d/same-population-total" % index, actual["diluted"] is not None and Fraction(actual["diluted"]["total_eps"]) == expected_total)
        grid.append(dict(n=n_text, d=d_text, effects=effect_texts, subset_count=count,
            minimizing_subsets=ties, expected_eps=str(minimum), expected_ids=sorted(selected),
            actual_eps=actual["diluted"]["continuing_eps"] if actual["diluted"] else None,
            actual_ids=sorted(actual_selected)))
    write(attempt / "subset-grid.json", grid)
    write(attempt / "checks.json", checks)
    failures = [c for c in checks if not c["passed"]]
    summary = dict(attempt=attempt.name, started_utc=utc, wall_seconds=round(time.monotonic()-started, 3),
        positive_fixtures=len(fixtures), adverse_fixtures=len(adverse), grid_cases=len(grid),
        enumerated_subsets=subset_count, checks=len(checks), failures=len(failures),
        failure_details=failures[:20], cpu_only=os.environ.get("CUDA_VISIBLE_DEVICES") == "-1",
        python=sys.version.split()[0], platform=platform.platform(),
        scope="conditional documentary arithmetic, binding and refusal checks; no runtime or current-law acceptance")
    write(attempt / "summary.json", summary)
    print(json.dumps(summary))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(run())
