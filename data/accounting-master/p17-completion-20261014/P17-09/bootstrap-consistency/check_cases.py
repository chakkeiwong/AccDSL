"""Exact explanatory examples; no empirical or asymptotic claim."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent
started = time.perf_counter()
checks = []

def check(name, actual, expected):
    checks.append({"name": name, "actual": str(actual), "expected": str(expected),
                   "passed": actual == expected})

def mean(law):
    return sum(x * p for x, p in law.items())

def variance(law):
    m = mean(law)
    return sum(p * (x-m)**2 for x, p in law.items())

def validate(name, law):
    check(name + ":mass", sum(law.values()), F(1))
    check(name + ":nonnegative_mass", all(p >= 0 for p in law.values()), True)

# Q is fixed; past histories remain equiprobable and yield estimates 90/110.
# Future R is 80/120 equally, independent of past given Q.
future = {F(80): F(1,2), F(120): F(1,2)}
estimates = {F(90): F(1,2), F(110): F(1,2)}
root = defaultdict(F)
for r, pr in future.items():
    for h, ph in estimates.items():
        root[r-h] += pr*ph
fixed_root = {r-90:p for r,p in future.items()}
validate("future", future)
validate("estimates", estimates)
validate("root_given_diagonal", root)
validate("root_given_full_history", fixed_root)
check("root_support", sorted(root), list(map(F, [-30,-10,10,30])))
check("diagonal_root_mean", mean(root), F(0))
check("diagonal_root_variance", variance(root), F(500))
check("fixed_history_root_mean", mean(fixed_root), F(10))
check("fixed_history_root_variance", variance(fixed_root), F(400))
check("conditional_total_variance", variance(root), variance(future)+variance(estimates))
check("conditional_targets_differ", root != fixed_root, True)

# Positive one-step cumulative claims: E[Y|X]=2X, Var[Y|X]=X.
prior = {F(1): F(1,2), F(2): F(1,2)}
forward = {F(1): {F(1): F(1,2), F(3): F(1,2)},
           F(2): {F(3): F(2,3), F(6): F(1,3)}}
joint = {(x,y):px*py for x,px in prior.items() for y,py in forward[x].items()}
for x, law in forward.items():
    validate("forward:"+str(x), law)
    check("conditional_mean:"+str(x), mean(law), 2*x)
    check("conditional_variance:"+str(x), variance(law), x)
    factors = {y/x:p for y,p in law.items()}
    check("factor_mean:"+str(x), mean(factors), F(2))
    check("factor_variance:"+str(x), variance(factors), 1/x)
check("joint_mass", sum(joint.values()), F(1))
mass_at_three = sum(p for (x,y),p in joint.items() if y == 3)
backward = {x:p/mass_at_three for (x,y),p in joint.items() if y == 3}
validate("backward_given_three", backward)
check("diagonal_three_mass", mass_at_three, F(7,12))
check("backward_prob_one", backward[F(1)], F(3,7))
check("backward_prob_two", backward[F(2)], F(4,7))
check("backward_mean", mean(backward), F(11,7))
check("backward_variance", variance(backward), F(12,49))
check("reciprocal_mean_is_wrong", mean(backward) != F(3,2), True)
check("reciprocal_variance_is_wrong", variance(backward) != F(3), True)

# Reserve/ultimate centering. q is already-paid cumulative claims.
q, ultimate, fitted_ultimate = F(100), F(130), F(120)
reserve, fitted_reserve = ultimate-q, fitted_ultimate-q
check("reserve", reserve, F(30))
check("fitted_reserve", fitted_reserve, F(20))
check("reserve_root", reserve-fitted_reserve, F(10))
check("product_difference_root", ultimate-fitted_ultimate, F(10))
check("literal_ultimate_centered_root", reserve-fitted_ultimate, F(-90))
check("centering_error", (reserve-fitted_ultimate)-(reserve-fitted_reserve), -q)
check("no_development_root", (q-q)-(q-q), F(0))
check("no_development_literal_root", (q-q)-q, F(-100))

# Equal unscaled limits need not identify a vanishing component.
# If P is a fair +/-1 sign, E_n is fair +/-1/n, then root variance is
# 1+1/n^2. Omitting E_n leaves limit 1 but scaled component variance 0 vs 1.
for n in [1,2,10,100]:
    process = {F(-1):F(1,2), F(1):F(1,2)}
    estimation = {F(-1,n):F(1,2), F(1,n):F(1,2)}
    combined = defaultdict(F)
    for p,pp in process.items():
        for e,pe in estimation.items():
            combined[p+e] += pp*pe
    check("root_variance:"+str(n), variance(combined), 1+F(1,n*n))
    check("scaled_component_variance:"+str(n), variance(estimation)*n*n, F(1))

result = {"passed":all(x["passed"] for x in checks), "check_count":len(checks),
          "checks":checks, "wall_seconds":time.perf_counter()-started,
          "scope":"Authored finite probability laws and arithmetic only; not a bootstrap theorem test."}
(OUT/"calculation-checks.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:result[k] for k in ["passed","check_count","wall_seconds"]}))
if not result["passed"]:
    raise SystemExit(1)
