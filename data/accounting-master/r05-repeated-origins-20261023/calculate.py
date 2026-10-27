"""Finite algebra examples; no company losses, models or source code execution."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))


def moments(values):
    mean = sum(values) / len(values)
    return mean, sum((v - mean) ** 2 for v in values) / len(values)


def calculate():
    results = []
    for label, weights, expected in (
        ('equal-company', (F(1, 2), F(1, 2)), (F(2), F(3, 4), F(1, 2))),
        ('unequal-company', (F(1, 4), F(3, 4)), (F(5, 2), F(13, 16), F(5, 8)))):
        values = []
        for v1, v2, e11, e12, e21, e22 in product((-1, 1), repeat=6):
            rows = ((1 + v1 + e11, 1 + v2 + e12), (3 + v1 + e21, 3 + v2 + e22))
            values.append(sum(weights[i] * F(sum(rows[i]), 2) for i in range(2)))
        mean, variance = moments(values)
        formula = (1 + sum(w * w for w in weights)) / 2
        # Explicit covariance double sum, separate from sampled-world aggregation.
        cov_sum = F(0)
        for i, t, j, s in product(range(2), repeat=4):
            covariance = int(t == s) + int(i == j and t == s)
            cov_sum += weights[i] * weights[j] * F(1, 4) * covariance
        independent_cells = sum(w * w for w in weights)
        assert (mean, variance, independent_cells) == expected
        assert variance == formula == cov_sum
        results.append({'id': label, 'worlds': len(values), 'weights': list(map(str, weights)),
                        'mean': str(mean), 'variance': str(variance),
                        'coefficient_formula': str(formula), 'covariance_double_sum': str(cov_sum),
                        'false_independent_cells': str(independent_cells)})
    serial = [F((z0 + z1) + (z1 + z2), 2) for z0, z1, z2 in product((-1, 1), repeat=3)]
    mean, variance = moments(serial)
    assert mean == 0 and variance == F(3, 2)
    n, k = 9, 8
    true, wrong = F(1, k) + F(1, n * k), F(2, n * k)
    assert (true, wrong, true / wrong) == (F(5, 36), F(1, 36), F(5))
    return {'fixed_panel': results, 'serial_overlap': {'worlds': 8, 'mean': str(mean),
              'variance': str(variance), 'false_independent_origins': '1'},
            'nine_by_eight_illustration': {'variance': str(true), 'false_independent_cells': str(wrong),
                                         'ratio': str(true / wrong), 'company_data': False},
            'status': 'Exact synthetic-law expectations only; no statistical ranking or inference procedure'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    out, manifest = U / 'calculation.json', U / 'calculation-manifest.json'
    if args.record:
        assert not out.exists() and not manifest.exists()
    started, t0 = datetime.now(timezone.utc).isoformat(), time.monotonic()
    results = calculate()
    elapsed = time.monotonic() - t0
    if args.record:
        with out.open('x') as f:
            json.dump(results, f, indent=2)
            f.write('\n')
        value = {'git_commit': load(U / 'protection.json')['head'], 'environment': sys.executable,
                 'cpu_gpu': 'CPU only; GPU devices intentionally hidden; standard-library exact enumeration',
                 'command': 'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B ' + rel(Path(__file__).resolve()) + ' --record',
                 'started_utc': started, 'wall_seconds': elapsed,
                 'data_version': 'Explicit finite symmetric-sign examples in derivation.md, no company outcomes',
                 'seeds': 'N/A complete deterministic enumeration',
                 'plan': 'docs/plans/accounting-r05-repeated-origins-20261023.md',
                 'result': rel(U / 'result.md'), 'output': rel(out),
                 'bindings': {rel(p): sha(p) for p in [Path(__file__).resolve(), U / 'derivation.md', out]}}
        with manifest.open('x') as f:
            json.dump(value, f, indent=2)
            f.write('\n')
    elif out.exists():
        assert results == load(out)
    print(json.dumps({'status': 'recorded' if args.record else 'read-only calculation passed',
                      'fixed_panel_cases': 2, 'worlds_per_case': 64, 'serial_worlds': 8}))


if __name__ == '__main__':
    main()
