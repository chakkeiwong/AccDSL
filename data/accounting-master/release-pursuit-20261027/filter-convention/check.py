"""Exact finite target/proposal comparisons, not stochastic performance tests."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
import platform
import sys
import time

D = Path(__file__).resolve().parent
assert not (D / 'exact-check.json').exists()
start = time.monotonic()


def normalize(values):
    total = sum(values)
    assert total > 0
    return [x / total for x in values]


checks = []


def check(name, condition, detail=None):
    checks.append({'check': name, 'passed': bool(condition), 'detail': detail})
    assert condition, name


W = [F(3, 4), F(1, 4)]
g = [F(1, 3), F(1)]
direct = normalize([W[j] * g[j] for j in range(2)])
check('direct_Bayes_equal', direct == [F(1, 2), F(1, 2)])
allocation = [0, 0, 0, 1]
mass = [sum((g[j] for a in allocation if a == j), F(0)) for j in range(2)]
check('stated_four_child_allocation', normalize(mass) == direct)
double = normalize([mass[j] * W[j] for j in range(2)])
check('double_parent_weight_changes_target', double == [F(3, 4), F(1, 4)] and double != direct)
r = [F(1, 2), F(1, 2)]
corrected = normalize([r[j] * W[j] / r[j] * g[j] for j in range(2)])
check('different_ancestor_proposal_corrected', corrected == direct)
uncorrected = normalize([r[j] * g[j] for j in range(2)])
check('omitted_ancestor_ratio_changes_target', uncorrected == [F(1, 4), F(3, 4)] and uncorrected != direct)

# Independently form exact posterior masses W_j f_jk g_k, then integrate
# proposed importance weights over the entire (ancestor,state) proposal.
# Non-identity transitions make ancestor-index errors observable.
cases = []
for w0, r0, f0, q0 in itertools.product([F(1, 4), F(1, 2), F(3, 4)], repeat=4):
    w, r = [w0, 1-w0], [r0, 1-r0]
    f = [[f0, 1-f0], [F(2, 3), F(1, 3)]]
    q = [[q0, 1-q0], [F(1, 3), F(2, 3)]]
    direct_joint = [w[j]*f[j][k]*g[k] for j in range(2) for k in range(2)]
    proposal_joint = [r[j]*q[j][k] for j in range(2) for k in range(2)]
    weights = [w[j]/r[j]*g[k]*f[j][k]/q[j][k] for j in range(2) for k in range(2)]
    reconstructed = [p*a for p, a in zip(proposal_joint, weights)]
    check(f'joint_density_ratio_{len(cases)}', reconstructed == direct_joint)
    check(f'normalized_joint_{len(cases)}', normalize(reconstructed) == normalize(direct_joint))
    cases.append({'w': list(map(str,w)), 'r': list(map(str,r)),
                  'f': [[str(x) for x in row] for row in f],
                  'q': [[str(x) for x in row] for row in q],
                  'exact_joint_target': list(map(str,normalize(direct_joint)))})
check('missing_ancestor_support_is_detectable', W[1]*g[1] > 0)
source = (D / 'source-identity.json').read_bytes()
result = {
    'passed': True, 'checks': checks, 'finite_cases': cases,
    'illustration': {'target': list(map(str,direct)), 'double_counted': list(map(str,double)),
                     'uncorrected_different_ancestor_proposal': list(map(str,uncorrected))},
    'source_identity_sha256': hashlib.sha256(source).hexdigest(),
    'command': [sys.executable, str(Path(__file__).resolve())],
    'environment': {'python': sys.version, 'platform': platform.platform(),
                    'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES')},
    'device': 'CPU-only exact Fraction arithmetic; no GPU framework imported',
    'seed': 'N/A deterministic finite enumeration',
    'git_commit': 'unavailable; unusable repository marker',
    'plan': str(D / 'plan.md'), 'wall_seconds': time.monotonic()-start,
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Exact one-update density ratios relative to a supplied finite empirical measure; no stochastic convergence or method ranking.'
}
(D / 'exact-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed': True, 'checks': len(checks), 'finite_cases': len(cases),
                  'illustration': result['illustration']}))
