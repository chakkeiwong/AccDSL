"""Exact diagnostic of the stated positive-weight algorithm, not accounting code."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))


def require(value, label):
    if not value:
        raise ValueError(label)


def capped(weights, ceilings, target):
    require(len(weights) == len(ceilings) > 0, 'dimensions')
    require(all(c > 0 for c in ceilings), 'positive-ceilings')
    require(all(b > 0 for b in weights), 'positive-weights')
    require(all(b < c for b, c in zip(weights, ceilings)), 'interior-weights')
    require(0 < target <= sum(ceilings), 'total-domain')
    require(sum(weights) < target, 'positive-reversal')
    # Implement the existing rule in increase space, preserving original weights.
    residual = target - sum(weights)
    capacity = [c - b for b, c in zip(weights, ceilings)]
    increments = [F(0) for _ in weights]
    active = list(range(len(weights)))
    passes = []
    while residual > 0:
        require(bool(active), 'capacity-exhausted-unexpectedly')
        denominator = sum(weights[i] for i in active)
        shares = {i: residual * weights[i] / denominator for i in active}
        clipped = [i for i in active if shares[i] > capacity[i]]
        passes.append({'active': list(active), 'residual': str(residual), 'clipped': clipped})
        if not clipped:
            for i in active:
                increments[i] = shares[i]
            residual = F(0)
        else:
            for i in clipped:
                increments[i] = capacity[i]
                residual -= capacity[i]
            active = [i for i in active if i not in clipped]
    final = [b + a for b, a in zip(weights, increments)]
    assert sum(final) == target and all(b <= x <= c for b, x, c in zip(weights, final, ceilings))
    assert len(passes) <= len(weights) + 1
    return {'final': [str(x) for x in final], 'increases': [str(a) for a in increments],
            'requested_reversal': str(target - sum(weights)), 'passes': passes}


def calculate():
    fixtures = load(U / 'fixtures.json')
    results, invalid, paths = [], [], []
    for case in fixtures['positive']:
        b, c, t = list(map(F, case['weights'])), list(map(F, case['caps'])), F(case['total'])
        result = capped(b, c, t)
        final = list(map(F, result['final']))
        assert final == list(map(F, case['expected'])), case['id']
        lam = F(case['lambda'])
        assert lam >= 1 and final == [min(ci, lam * bi) for ci, bi in zip(c, b)]
        results.append({'id': case['id'], **result, 'characterization_multiplier': str(lam)})
    for case in fixtures['outside_domain']:
        try:
            capped(list(map(F, case['weights'])), list(map(F, case['caps'])), F(case['total']))
        except ValueError as error:
            assert str(error) == case['error'], case['id']
            invalid.append({'id': case['id'], 'rejection': str(error), 'evaluated_allocation': False})
        else:
            raise AssertionError('Outside-domain input accepted: ' + case['id'])
    for case in fixtures['constructive_paths']:
        c, x, t = list(map(F, case['caps'])), list(map(F, case['target'])), F(case['total'])
        assert 0 < t < sum(c) and sum(x) == t and all(0 <= a <= b for a, b in zip(x, c))
        z = [t * ci / sum(c) for ci in c]
        points = []
        for eps, expected_error in zip(case['epsilons'], case['expected_l1_errors'], strict=True):
            e = F(eps)
            assert 0 < e < 1
            y = [(1 - e) * xi + e * zi for xi, zi in zip(x, z)]
            b = [e * yi for yi in y]
            result = capped(b, c, t)
            assert list(map(F, result['final'])) == y
            error = sum(abs(yi - xi) for yi, xi in zip(y, x))
            assert error == F(expected_error) == e * sum(abs(zi - xi) for zi, xi in zip(z, x))
            points.append({'epsilon': str(e), 'weights': [str(bi) for bi in b],
                           'final': result['final'], 'target_l1_error': str(error)})
        paths.append({'id': case['id'], 'target': case['target'], 'points': points,
                      'limit_support': 'derivation.md equation (3); finite points are diagnostics only'})
    zero = fixtures['boundary_only']
    assert F(zero['total']) == 0 and all(F(x) == 0 for x in zero['unique_feasible_vector'])
    assert zero['positive_reversal_approach_exists'] is False
    by = {r['id']: r for r in results}
    for suffix in ('half', 'tenth', 'millionth'):
        assert by['equal-' + suffix]['final'] == ['3', '3']
        assert by['skew-' + suffix]['final'] == ['1', '5']
        assert by['equal-' + suffix]['requested_reversal'] == by['skew-' + suffix]['requested_reversal']
    return {'positive_cases': results, 'refused_inputs': invalid, 'constructive_paths': paths,
            'boundary_only': zero, 'counts': {'positive_cases': len(results),
                'refused_inputs': len(invalid), 'constructive_path_points': sum(len(p['points']) for p in paths)},
            'mathematical_verdict': 'No path-independent zero-weight extension for at least two positive ceilings and 0<T<sum C',
            'accounting_allocation_at_zero': 'unresolved; no fallback admitted',
            'statistical_ranking': 'N/A exact deterministic checks'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    output, manifest = U / 'calculation.json', U / 'calculation-manifest.json'
    if args.record:
        assert not output.exists() and not manifest.exists()
    t0 = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    result = calculate()
    elapsed = time.monotonic() - t0
    if args.record:
        with output.open('x') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        protection = load(U / 'protection.json')
        value = {'git_commit': protection['head'], 'environment': sys.executable,
                 'python': platform.python_version(), 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard library only',
                 'command': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(Path(__file__).resolve()) + ' --record',
                 'started_utc': started, 'wall_seconds': elapsed,
                 'data_version': 'Hand-authored fixtures and derived positive-weight limit model; exact bound hashes',
                 'seeds': 'N/A deterministic fractions; no stochastic run',
                 'plan': 'docs/plans/accounting-r03-zero-weight-limit-20261023.md',
                 'result': rel(U / 'result.md'), 'output': rel(output),
                 'bindings': {rel(p): sha(p) for p in [Path(__file__).resolve(), U / 'fixtures.json', U / 'derivation.md', output]}}
        with manifest.open('x') as f:
            json.dump(value, f, indent=2)
            f.write('\n')
    elif output.exists():
        assert load(output) == result
    print(json.dumps({'status': 'recorded' if args.record else 'read-only calculation passed', **result['counts']}))


if __name__ == '__main__':
    main()
