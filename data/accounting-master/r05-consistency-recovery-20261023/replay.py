"""Replay retained evidence; --record writes this successor's generated records."""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'data/accounting-master/r05-archive-leads-20261023'
WEIGHT = ROOT / 'data/accounting-master/r05-weight-selector-20261023'
TOY = ROOT / 'data/accounting-master/r05-martingale-estimand-20261023'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    spec = importlib.util.spec_from_file_location(path.parent.name + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = datetime.now(timezone.utc)
    tick = time.perf_counter()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    weight = reference(WEIGHT / 'reference.py')
    assert len(weight['checks']) == 7 and len(weight['refusals']) == 5
    assert all(weight['checks'].values()) and all(weight['refusals'].values())
    old_weight = read(WEIGHT / 'reference-results.json')
    assert len(old_weight['checks']) == 6 and len(old_weight['refusals']) == 4
    assert weight['checks'] == {**old_weight['checks'], 'released_validation_precedes_later_fit': True}
    assert weight['refusals'] == {**old_weight['refusals'], 'validation_outcome_not_yet_released': True}
    toy = reference(TOY / 'conditional_reference.py')
    old_toy = read(TOY / 'reference-results.json')
    assert old_toy['martingale_residuals_zero'] is True

    record = read(ARCHIVE / 'archive-record.json')
    cdx = read(ARCHIVE / 'requests/02-jpmorgan-cdx.body')
    columns = cdx[0]
    captures = [dict(zip(columns, row)) for row in cdx[1:]]
    assert len(captures) == 8
    bodies = {
        '20251119011943': ARCHIVE / 'requests/03-jpmorgan-capture.body',
        '20251226081731': ARCHIVE / 'requests/04-jpmorgan-capture-later.body',
    }
    observed = {}
    payloads = {}
    for stamp, path in bodies.items():
        payload = path.read_bytes()
        payloads[stamp] = payload
        capture = next(row for row in captures if row['timestamp'] == stamp)
        digest = base64.b32encode(hashlib.sha1(payload).digest()).decode().rstrip('=')
        assert digest == capture['digest']
        observed[stamp] = {'bytes': len(payload), 'sha256': sha(path), 'cdx_digest_matches': True,
                           'cdx_length_field': int(capture['length']), 'has_eof_trailer': b'%%EOF' in payload[-1024:]}
    first, later = payloads.values()
    assert later.startswith(first) and len(first) < len(later)
    assert not observed['20251119011943']['has_eof_trailer']
    assert observed['20251226081731']['has_eof_trailer']
    retained = ROOT / record['jpmorgan']['later_replay']['retained_original_path']
    assert later == retained.read_bytes()
    assert sha(retained) == record['jpmorgan']['later_replay']['sha256']
    assert len(first) == record['jpmorgan']['first_replay']['payload_bytes']
    assert len(later) == record['jpmorgan']['later_replay']['size_bytes']
    assert record['admission_decision']['all_192_historical_admissions_remain_false'] is True
    assert read(ARCHIVE / 'requests/01-apple-cdx.body') == []
    assert read(ARCHIVE / 'requests/05-apple-availability.body')['archived_snapshots'] == {}
    pdf = subprocess.run(['pdfinfo', str(bodies['20251226081731'])], check=True, capture_output=True, text=True)
    assert next(line.split(':', 1)[1].strip() for line in pdf.stdout.splitlines() if line.startswith('Pages:')) == '358'

    completion = read(ARCHIVE / 'completion.json')
    for control, expected in completion['control_snapshots_after'].items():
        assert sha(ARCHIVE / 'controls-after' / Path(control).name) == expected
    stale_bindings = [name for name, expected in completion['bindings'].items()
                      if sha(ROOT / name) != expected]
    assert str((ARCHIVE / 'archive-record.json').relative_to(ROOT)) in stale_bindings
    inventory = [
        {'id': 1, 'purpose': 'Apple exact-URL CDX', 'body': '01-apple-cdx.body'},
        {'id': 2, 'purpose': 'JPMorgan exact-URL CDX', 'body': '02-jpmorgan-cdx.body'},
        {'id': 3, 'purpose': 'JPMorgan 19 November replay', 'body': '03-jpmorgan-capture.body'},
        {'id': 4, 'purpose': 'JPMorgan 26 December replay', 'body': '04-jpmorgan-capture-later.body'},
        {'id': 5, 'purpose': 'Apple availability', 'body': '05-apple-availability.body'},
    ]
    assert len(list((ARCHIVE / 'requests').glob('*.body'))) == len(inventory) == record['requests_used'] == 5
    for item in inventory:
        path = ARCHIVE / 'requests' / item['body']
        item.update({'sha256': sha(path), 'headers_retained': path.with_suffix('.headers').is_file(),
                     'dedicated_transport_metadata': 'response headers are retained; separate curl timing metadata is not established'})
    result = {
        'status': 'PASS', 'weight': weight, 'predecessor_weight_counts': {'checks': 6, 'refusals': 4},
        'conditional_reference': toy, 'archive': observed,
        'archive_historical_snapshots_match': True, 'archive_stale_completion_bindings': stale_bindings,
        'archive_request_inventory': inventory,
        'historical_drafting_wall_times': 'unknown; old manifest durations are not measured drafting durations',
        'historical_admissions_changed': 0, 'empirical_execution': False,
    }
    if args.record:
        (OUT / 'check-results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        manifest = {
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'environment': sys.executable, 'python': sys.version.split()[0],
            'cpu_gpu': 'CPU only; CUDA_VISIBLE_DEVICES=-1; no ML imports',
            'data_version': 'retained archive bytes and exact synthetic fixtures',
            'random_seeds': 'N/A; deterministic enumeration',
            'started_utc': start.isoformat(), 'completed_utc': datetime.now(timezone.utc).isoformat(),
            'wall_time_seconds': time.perf_counter() - tick,
            'timing_scope': 'this replay command only; excludes drafting and previous units',
            'command': 'env CUDA_VISIBLE_DEVICES=-1 ' + sys.executable + ' -B ' + str(Path(__file__).relative_to(ROOT)) + ' --record',
            'plan': 'docs/plans/accounting-r05-consistency-recovery-20261023.md',
            'result': str((OUT / 'result.md').relative_to(ROOT)),
            'output': str((OUT / 'check-results.json').relative_to(ROOT)),
        }
        (OUT / 'run-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    else:
        assert result == read(OUT / 'check-results.json'), 'successor record differs; investigate before updating'
    print(json.dumps({'status': 'PASS', 'weight_checks': len(weight['checks']),
                      'weight_refusals': len(weight['refusals']), 'filtration_checks': len(toy['checks']),
                      'archive_requests_reissued': 0, 'historical_snapshots_match': True,
                      'stale_archive_bindings': len(stale_bindings)}))


if __name__ == '__main__':
    main()
