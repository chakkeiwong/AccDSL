"""Source identity and local formula deductions; never execute acquired code."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fractions import Fraction as Q
import base64
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    checks, blobs, parsing = [], [], {}
    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
    tree = json.loads((HERE / 'accdsl-actus-mirror-tree.json').read_text())
    dictionary = json.loads((HERE / 'accdsl-actus-dictionary-tree.json').read_text())
    for path in sorted(HERE.glob('accdsl-actus-*.json')):
        obj = json.loads(path.read_text())
        if not isinstance(obj, dict) or 'content' not in obj:
            continue
        raw = base64.b64decode(obj['content'])
        git = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        rows = (tree if 'mirror-' in path.name else dictionary)['tree']
        matches = [x for x in rows if x['sha'] == obj['sha'] and x['type'] == 'blob']
        check(path.name + ':blob_identity', git == obj['sha'] and len(matches) == 1)
        source_path = matches[0]['path']
        decoded = HERE / ('mirror/' + Path(source_path).name if 'mirror-' in path.name else source_path)
        check(path.name + ':decoded_identity', decoded.read_bytes() == raw)
        blobs.append({'response': path.name, 'source_path': source_path, 'decoded': str(decoded.relative_to(HERE)),
                      'git_blob_sha1': git, 'sha256': sha(decoded)})
    for name in ['event', 'terms', 'versions']:
        path = HERE / ('actus-dictionary-' + name + '.json')
        try:
            json.loads(path.read_text())
            parsing[name] = {'valid_json': True}
        except json.JSONDecodeError as exc:
            parsing[name] = {'valid_json': False, 'line': exc.lineno, 'column': exc.colno, 'message': exc.msg}
    check('event_parses_terms_versions_reject', parsing['event']['valid_json'] and not parsing['terms']['valid_json'] and not parsing['versions']['valid_json'])
    events = json.loads((HERE / 'actus-dictionary-event.json').read_text())['event']['eventType']['allowedValues']
    ranks = {e['acronym']: e['sequence'].strip() for e in events}
    check('dictionary_FP_before_IP', int(ranks['FP']) < int(ranks['IP']))
    seq = (HERE / 'mirror/EventSequence.java').read_text()
    check('mirror_offsets_match_inspected_source', 'case IP:\n        offset = 40;' in seq and 'case FP:\n        offset = 60;' in seq and 'case MD:\n        offset = 150;' in seq)
    check('opposite_FP_IP_order', (int(ranks['FP']) < int(ranks['IP'])) != (60 < 40))
    md = datetime(2025, 1, 6, 9, 0)
    ip = md + timedelta(minutes=1)
    check('offset_order_can_reverse_chronology', md < ip and md + timedelta(seconds=150) > ip + timedelta(seconds=40))
    start, end = datetime(2025, 1, 4, 11), datetime(2025, 1, 6, 9)
    calendar_days, full_days = (end.date() - start.date()).days, (end - start).days
    interest_calendar = Q(427, 5) * Q(1, 20) * Q(calendar_days, 365)
    interest_mirror_formula = Q(427, 5) * Q(1, 20) * Q(full_days, 365)
    check('actual_example_day_count_mismatch', calendar_days == 2 and full_days == 1 and interest_calendar == Q(427, 18250) and interest_mirror_formula == Q(427, 36500))
    check('equal_clock_time_two_day_special_case', (datetime(2025, 1, 6, 11) - start).days == 2)
    mirror_md, spec_md = -Q(427, 5), -Q(427, 5) - 1
    check('nonzero_accrual_maturity_mismatch', mirror_md == -Q(427, 5) and spec_md == -Q(432, 5) and mirror_md != spec_md)
    result = {'passed': all(c['passed'] for c in checks), 'checks': checks, 'check_count': len(checks),
              'blobs': blobs, 'dictionary_parsing': parsing, 'deductions': {
              'calendar_interest': str(interest_calendar), 'mirror_formula_interest': str(interest_mirror_formula),
              'mirror_maturity': str(mirror_md), 'spec_maturity': str(spec_md)},
              'runtime_executed': False, 'dependency_adopted': False,
              'interpretation': 'Expected mismatch witnesses support source-boundary findings; not Java execution or core 1.1.0 conformance.'}
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    manifest = {'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'started_utc': started, 'wall_seconds': time.perf_counter() - clock,
                'command': 'env CUDA_VISIBLE_DEVICES=-1 python3 -B docs/design/research/software/actus-core-review-20261023/verify.py',
                'environment': {'executable': sys.executable, 'python': platform.python_version()},
                'cpu_gpu': 'CPU only; GPU intentionally hidden', 'cuda_visible_devices': os.environ.get('CUDA_VISIBLE_DEVICES'),
                'random_seeds': 'N/A: deterministic source checks and rational arithmetic',
                'plan_file': 'docs/plans/accounting-actus-core-review-20261023.md',
                'result_file': 'docs/design/research/actus-core-correspondence-20261023.md',
                'data_version': {'mirror_tree': tree['sha'], 'dictionary_tree': dictionary['sha'], 'identities_are': 'Git trees, not commits'},
                'artifacts': {str(p.relative_to(HERE)): sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name != 'manifest.json'}}
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'verified_blobs': len(blobs), 'failures': [c for c in checks if not c['passed']]}))
    if not result['passed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
