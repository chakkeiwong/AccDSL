"""Replay retained teaching arithmetic and exact midpoint checks in new output."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    out = args.output_dir.resolve()
    if out.exists():
        parser.error('output directory already exists; choose a new directory')
    lock = json.loads((source / 'provenance.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name, expected in lock['inputs'].items():
        if sha(source / name) != expected:
            raise ValueError('source integrity mismatch: ' + name)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    copied = out / 'teaching-original'
    copied.mkdir()
    shutil.copy2(source / 'teaching-original.py', copied / 'check_examples.py')
    env = dict(os.environ, CUDA_VISIBLE_DEVICES='-1', PYTHONDONTWRITEBYTECODE='1')
    cmd = [sys.executable, '-I', '-B', str(copied / 'check_examples.py')]
    run = subprocess.run(cmd, cwd=out, env=env, text=True, capture_output=True, timeout=45)
    (out / 'teaching.stdout').write_text(run.stdout)
    (out / 'teaching.stderr').write_text(run.stderr)
    if run.returncode:
        raise RuntimeError('original teaching checker failed: ' + run.stderr)
    actual = json.loads((copied / 'arithmetic.json').read_text())
    expected = json.loads((source / 'teaching-expected.json').read_text())
    if actual != expected:
        raise AssertionError('complete original teaching result changed')

    records = []
    for n in range(1, 65):
        points = [F(2*i-1, 2*n) for i in range(1, n+1)]
        thresholds = {F(0), F(1), F(3,10), F(49,100), F(51,100)}
        for point in points:
            thresholds.update([point-F(1,8*n), point, point+F(1,8*n)])
        for t in sorted(thresholds):
            strict_count = sum(x > t for x in points)
            inclusive_count = sum(x >= t for x in points)
            count_formula = n - math.floor(n*t + F(1,2))
            p = F(strict_count, n)
            error = p - (1-t)
            assert strict_count == count_formula, (n,t,strict_count,count_formula)
            assert abs(error) <= F(1,2*n), (n,t,error)
            assert inclusive_count-strict_count == int(t in points)
            assert sum(points)/n == F(1,2)
            records.append({'n':n,'threshold':str(t),'strict_probability':str(p),
                            'inclusive_probability':str(F(inclusive_count,n)),
                            'signed_error':str(error),'bound':str(F(1,2*n))})
    fixed = {}
    for n, want in [(4,F(3,4)),(5,F(3,5)),(10,F(7,10)),(11,F(8,11))]:
        p = F(sum(F(2*i-1,2*n)>F(3,10) for i in range(1,n+1)),n)
        assert p == want
        fixed[str(n)] = {'probability':str(p),'absolute_error':str(abs(p-F(7,10)))}
    assert F(fixed['5']['absolute_error']) > F(fixed['4']['absolute_error'])
    assert F(fixed['11']['absolute_error']) > F(fixed['10']['absolute_error'])
    (out / 'grid-cases.json').write_text(json.dumps(records,indent=2)+'\n')
    result = {'passed':True,'original_teaching_checks':actual['count'],
              'complete_original_result_matches':True,'grid_cases':len(records),
              'grid_n_range':[1,64],'counterexamples':fixed,
              'scope':'Exact rational test instances; all-real-threshold bound follows from the manuscript floor proof, not case enumeration. No stochastic experiment or empirical ranking.'}
    (out / 'result.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest = {'command':sys.argv,'teaching_command':cmd,'python':sys.version,
                'executable':sys.executable,'platform':platform.platform(),
                'cpu_gpu':'CPU-only standard library; CUDA_VISIBLE_DEVICES=-1 for child',
                'seeds':'N/A: deterministic arithmetic','wall_seconds':time.monotonic()-start,
                'git_commit':'unavailable: unusable repository marker',
                'input_lock':lock,'verifier_sha256':sha(Path(__file__)),
                'plan':'docs/plans/accounting-midpoint-reference-20261027.md',
                'outputs':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
    (out / 'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
