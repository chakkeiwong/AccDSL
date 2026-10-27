"""Bounded rational diagnostics; candidate selection rules are not admitted EPS."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def main():
    start = time.monotonic()
    checks = []

    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected,
                           actual=str(actual), expected=str(expected)))

    def earnings(profit, n):
        p = Q(profit) + 20 * n
        return (p - Q(1, 2) * max(p - 100, 0)) * Q(4, 5)

    comparisons = []
    for p in (80, 90):
        e = [earnings(p, n) for n in range(3)]
        eps = [e[n] / (100 + 20*n) for n in range(3)]
        selected = []
        for series in ("A", "B"):
            n = len(selected)
            if eps[n+1] < eps[n]:
                selected.append(series)
        expected = (64, 80, 88) if p == 80 else (72, 84, 92)
        for n in range(3):
            check(f"P{p}.world{n}.earnings", e[n], Q(expected[n]))
        check(f"P{p}.sequential", selected, [] if p == 80 else ["A", "B"])
        frozen = e[0] + 2 * (e[1]-e[0])
        check(f"P{p}.frozen_increments_disagree", frozen != e[2], True)
        comparisons.append(dict(pretax=p, earnings=list(map(str, e)),
            eps=list(map(str, eps)), fixed_ranking_actual_world=selected,
            marginal_ranking_actual_world=selected,
            raw_subset_minimum=["A", "B"], frozen_increment_earnings=str(frozen),
            admitted_selection=None, selection_status="not_evaluated"))

    # Values independently transcribed from official illustrative Example 9.
    current_e, current_n = Q(10000000), Q(2000000)
    trace = []
    for name, a, b in [("options", 0, 20000), ("bonds", 3000000, 2000000),
                       ("preferences", 6400000, 1600000)]:
        trial = (current_e+a)/(current_n+b)
        selected = trial < current_e/current_n
        trace.append(dict(series=name, trial=str(trial), selected=selected))
        if selected:
            current_e += a
            current_n += b
    check("Example9.selection", [r["series"] for r in trace if r["selected"]],
          ["options", "bonds"])
    check("Example9.continuing", current_e/current_n, Q(650, 201))
    check("Example9.total", (current_e-4000000)/current_n, Q(150, 67))
    check("Example9.preference_trial", trace[-1]["trial"], "970/281")
    for p, expected in [(330, 120), (550, 200), (110, 40)]:
        check(f"TaxDecision.profit{p}.ordinary", Q(p, 11)+Q(p*10, 11)*Q(3, 10),
              Q(expected))

    protected = [ROOT/'data/accounting-master/dependent-eps-20261016/semantic-contract.md',
        ROOT/'data/accounting-master/dependent-eps-20261016/authored-cases.json',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        OUT/'aasb133-2020.pdf', OUT/'ias33-tax-agenda.pdf', OUT/'ias33-tax-example.pdf',
        OUT/'source-reading.md', Path(__file__).resolve()]
    hashes = [dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
              for p in protected]
    result = dict(checks=checks, passed=all(c['passed'] for c in checks),
                  candidate_comparisons=comparisons, source_example9=trace,
                  protected_inputs=hashes, wall_seconds=time.monotonic()-start,
                  git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  command='python3 data/accounting-master/dependent-eps-source-selection-20261017/check_selection.py',
                  environment='system Python; fractions; CPU only; no numerical framework or GPU import',
                  seeds='N/A: deterministic rational arithmetic',
                  plan='docs/plans/accounting-dependent-eps-source-selection-20261017.md',
                  result='data/accounting-master/dependent-eps-source-selection-20261017/result.md',
                  claim='Arithmetic and source discrimination only; no final nonadditive EPS method admitted')
    target = OUT/'selection-checks.json'
    if target.exists():
        raise RuntimeError('Preserve completed diagnostics; use a fresh attempt for repairs')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checks=len(checks),passed=result['passed'],artifact=str(target.relative_to(ROOT)))))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
