"""Short local diagnostic; --record saves generated result and measured run."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = ROOT / 'docs/plans/accounting-r05-changing-family-weights-20261023.md'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    started = datetime.now(timezone.utc)
    tick = time.perf_counter()
    spec = importlib.util.spec_from_file_location('changing_family_reference', HERE / 'reference.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.main()
    assert len(result['checks']) == 12 and len(result['refusals']) == 4
    path = HERE / 'reference-results.json'
    if args.record:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        manifest = {
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'command': 'env CUDA_VISIBLE_DEVICES=-1 ' + sys.executable + ' -B ' + str(Path(__file__).relative_to(ROOT)) + ' --record',
            'environment': sys.executable, 'python': sys.version.split()[0],
            'cpu_gpu': 'CPU only; GPU devices intentionally hidden; no ML imports',
            'data_version': 'synthetic point laws and explicit integer time ordering',
            'random_seeds': 'N/A; exact deterministic fractions',
            'started_utc': started.isoformat(), 'completed_utc': datetime.now(timezone.utc).isoformat(),
            'wall_time_seconds': time.perf_counter() - tick,
            'timing_scope': 'this reference/record command only, not drafting',
            'plan': str(PLAN.relative_to(ROOT)),
            'result': str((HERE / 'result.md').relative_to(ROOT)),
            'outputs': [str(path.relative_to(ROOT))],
            'input_hashes': {str(p.relative_to(ROOT)): sha(p) for p in [HERE / 'reference.py', PLAN]},
        }
        (HERE / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    else:
        assert result == json.loads(path.read_text()), 'reference result changed'
        manifest = json.loads((HERE / 'run-manifest.json').read_text())
        for name, expected in manifest['input_hashes'].items():
            assert sha(ROOT / name) == expected
    print(json.dumps({'status': 'PASS', 'checks': len(result['checks']), 'refusals': len(result['refusals']),
                      'member_mass_changes': True, 'feature_partition_choice_remains': True,
                      'empirical_execution': False}))


if __name__ == '__main__':
    main()
