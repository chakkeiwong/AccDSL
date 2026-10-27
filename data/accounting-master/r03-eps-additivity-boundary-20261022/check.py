"""Exact, finite documentary checks; no accounting runtime is implemented."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

U = Path(__file__).resolve().parent
R = U.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))


def model(raw, defaults):
    values = defaults | raw
    m = {k: F(values[k]) for k in ('P', 'H', 'q', 't', 'n')}
    m['I'], m['b'] = [F(x) for x in raw['I']], [F(x) for x in raw['b']]
    if (len(m['I']) != len(m['b']) or any(x < 0 for x in m['I'])
            or any(x <= 0 for x in m['b']) or m['n'] <= 0
            or not 0 <= m['q'] <= 1 or not 0 <= m['t'] <= 1):
        raise ValueError('Outside the stated theorem domain')
    return m


def worlds(m):
    result = []
    for mask in range(1 << len(m['I'])):
        indices = [i for i in range(len(m['I'])) if mask & (1 << i)]
        pretax = m['P'] + sum((m['I'][i] for i in indices), F(0))
        bonus = m['q'] * max(pretax - m['H'], F(0))
        tax = m['t'] * (pretax - bonus)
        earnings = pretax - bonus - tax
        shares = m['n'] + sum((m['b'][i] for i in indices), F(0))
        result.append(dict(mask=mask, pretax=pretax, bonus=bonus, tax=tax,
                           N=earnings, D=shares, ratio=earnings / shares))
    return result


def inspect_additivity(m, w):
    a = [w[1 << i]['N'] - w[0]['N'] for i in range(len(m['I']))]
    reconstructed = [w[0]['N'] + sum((a[i] for i in range(len(a)) if mask & (1 << i)), F(0))
                     for mask in range(len(w))]
    actual = all(row['N'] == reconstructed[mask] for mask, row in enumerate(w))
    conditions = [m['q'] * (1 - m['t']) == 0, m['P'] >= m['H'],
                  m['P'] + sum(m['I'], F(0)) <= m['H'],
                  sum(x > 0 for x in m['I']) <= 1]
    assert actual == any(conditions), (m, actual, conditions)
    gap = reconstructed[-1] - w[-1]['N']
    if m['P'] < m['H'] < m['P'] + sum(m['I'], F(0)):
        c = m['H'] - m['P']
        formula = m['q'] * (1 - m['t']) * (sum((min(x, c) for x in m['I']), F(0)) - c)
        assert gap == formula, (m, gap, formula)
    assert gap == 0 if actual else gap > 0
    return dict(additive=actual, sufficient_conditions=conditions, increments=a, full_set_gap=gap)


def candidate(m, w, mode):
    """Two prior diagnostic paths; neither supplies nonadditive final EPS."""
    remaining = list(range(len(m['I'])))
    standalone = [(w[1 << i]['N'] - w[0]['N']) / m['b'][i] for i in remaining]
    current, selected, trace = 0, [], []
    while remaining:
        ratios = {i: standalone[i] if mode == 'fixed' else
                  (w[current | (1 << i)]['N'] - w[current]['N']) / m['b'][i]
                  for i in remaining}
        i = min(remaining, key=lambda j: (ratios[j], j))
        trial = current | (1 << i)
        before, after = w[current], w[trial]
        cross = after['N'] * before['D'] - before['N'] * after['D']
        trace.append(dict(series=chr(65 + i), ranked_remaining={chr(65 + j): ratios[j] for j in remaining},
                          before_mask=current, trial_mask=trial, before_N=before['N'], before_D=before['D'],
                          trial_N=after['N'], trial_D=after['D'], cross_product=cross, admitted=cross < 0))
        if cross < 0:
            selected.append(chr(65 + i))
            current = trial
        remaining.remove(i)
    return dict(selected=selected, mask=current, ratio=w[current]['ratio'], trace=trace)


def exact_json(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def run():
    fixtures = load(U / 'fixtures.json')
    outcomes, invalid = [], []
    for f in fixtures['cases']:
        m = model(f, fixtures['defaults'])
        w = worlds(m)
        a = inspect_additivity(m, w)
        assert [row['N'] for row in w] == [F(x) for x in f['N']], f['name']
        assert a['additive'] == f['additive'] and a['full_set_gap'] == F(f['gap']), f['name']
        minimum = min(row['ratio'] for row in w)
        paths = {}
        if a['additive'] or 'fixed' in f:
            paths = {mode: candidate(m, w, mode) for mode in ('fixed', 'marginal')}
        if a['additive']:
            for path in paths.values():
                assert path['selected'] == f['selected'], f['name']
                assert path['ratio'] == F(f['ratio']) == minimum, f['name']
        elif 'fixed' in f:
            for mode, path in paths.items():
                assert path['selected'] == f[mode], f['name']
                assert path['ratio'] == F(f[mode + '_ratio']), f['name']
            assert minimum == F(f['minimum']), f['name']
        if 'order_difference' in f:
            assert paths['fixed']['ratio'] - paths['marginal']['ratio'] == F(f['order_difference'])
        if 'delete_A_difference' in f:
            assert paths['marginal']['ratio'] - w[6]['ratio'] == F(f['delete_A_difference']) > 0
        if f.get('pairwise_at_empty'):
            assert all(w[(1 << i) | (1 << j)]['N'] == w[1 << i]['N'] + w[1 << j]['N'] - w[0]['N']
                       for i, j in combinations(range(len(m['I'])), 2))
            assert not a['additive']
        outcomes.append(dict(name=f['name'], model=m, worlds=w, additivity=a, diagnostic_paths=paths,
                             minimum_conditional_ratio=minimum, final_accounting_selection='not_admitted'))
    for f in fixtures['invalid_cases']:
        try:
            model(f, fixtures['defaults'])
        except ValueError as e:
            invalid.append(dict(name=f['name'], rejected_before_world_evaluation=True, reason=str(e)))
        else:
            raise AssertionError(f['name'])
    counts = dict(models=0, additive=0, nonadditive=0, worlds=0, additive_selector_comparisons=0)
    digest = hashlib.sha256()
    for P, H, q, t in product(('-2', '0', '1', '2'), ('-1', '0', '2'), ('0', '1/2', '1'), ('0', '1/5', '1')):
        for size in range(4):
            for savings in product(('0', '1', '2'), repeat=size):
                m = model(dict(P=P, H=H, q=q, t=t, n='7/3', I=list(savings),
                               b=[str(F(i + 1, 2)) for i in range(size)]), {})
                w = worlds(m)
                a = inspect_additivity(m, w)
                counts['models'] += 1
                counts['worlds'] += len(w)
                counts['additive' if a['additive'] else 'nonadditive'] += 1
                if a['additive']:
                    minimum = min(row['ratio'] for row in w)
                    for mode in ('fixed', 'marginal'):
                        assert candidate(m, w, mode)['ratio'] == minimum, (m, mode)
                        counts['additive_selector_comparisons'] += 1
                digest.update((json.dumps(dict(model=m, N=[row['N'] for row in w], additivity=a),
                                          default=exact_json, sort_keys=True) + '\n').encode())
    assert counts['models'] == 4320
    return dict(status='pass', fixtures=outcomes, invalid_controls=invalid,
                grid=counts | dict(ordered_result_sha256=digest.hexdigest()),
                evidence_scope='Exact finite transcription checks. Universal equivalence rests on derivation.md; no accounting selection or runtime admission.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    if args.record:
        assert not (U / 'checks.json').exists() and not (U / 'calculation-manifest.json').exists()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    protection = load(U / 'protection.json')
    for name, digest in protection['protected'].items():
        assert sha(R / name) == digest, name
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip() == protection['head']
    assert sha(R / '.git/index') == protection['index_sha256']
    for name, digest in protection['tracked_dirty'].items():
        assert sha(R / name) == digest, name
    before = {rel(p): sha(p) for p in (U / 'check.py', U / 'fixtures.json', U / 'derivation.md',
                                     R / 'docs/plans/accounting-r03-eps-additivity-boundary-20261022.md')}
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    result = run()
    elapsed = time.monotonic() - tick
    assert all(sha(R / name) == digest for name, digest in before.items())
    if args.record:
        with (U / 'checks.json').open('x') as f:
            json.dump(result, f, indent=2, default=exact_json)
            f.write('\n')
        manifest = dict(git_commit=protection['head'], branch=protection['branch'], environment=sys.executable,
                        python_version=sys.version, cpu_gpu='CPU only; GPU devices intentionally hidden before imports',
                        seeds='N/A deterministic exact rational enumeration', started_utc=started,
                        finished_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=elapsed,
                        command=['env', 'CUDA_VISIBLE_DEVICES=-1', sys.executable, '-B', rel(U / 'check.py'), '--record'],
                        data_version='Declared synthetic fixtures; prior frozen EPS sources and witnesses', input_bindings=before,
                        plan='docs/plans/accounting-r03-eps-additivity-boundary-20261022.md',
                        result=rel(U / 'result.md'), outputs={rel(U / 'checks.json'): sha(U / 'checks.json')})
        with (U / 'calculation-manifest.json').open('x') as f:
            json.dump(manifest, f, indent=2)
            f.write('\n')
    print(json.dumps(dict(status=result['status'], fixtures=len(result['fixtures']),
                          rejected_controls=len(result['invalid_controls']), grid=result['grid'], wall_seconds=elapsed)))
