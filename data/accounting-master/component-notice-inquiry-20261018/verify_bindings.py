"""Verify retained notice bytes and their exact-source/protected-input bindings."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import tarfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def main():
    started = time.monotonic()
    d = json.loads((OUT / 'source-manifest.json').read_text())
    checks = []
    digest = lambda raw: hashlib.sha256(raw).hexdigest()

    def check(label, condition):
        checks.append({'check': label, 'passed': bool(condition)})

    check('exact retained archive', digest((ROOT / d['archive']).read_bytes()) == d['archive_sha256'])
    check('completed audited plan', digest((ROOT / d['plan']).read_bytes()) == d['plan_sha256'])
    for row in d['files']:
        check(row['role'] + ': ' + row['path'], digest((ROOT / row['path']).read_bytes()) == row['sha256'])
    check('five explicitly bounded selected texts', len(d['selected_texts']) == 5)
    with tarfile.open(ROOT / d['archive'], 'r:gz') as tf:
        for row in d['selected_texts']:
            members = [m for m in tf.getmembers() if m.name == row['archive_member']]
            check('unique regular member: ' + row['archive_member'],
                  len(members) == 1 and members[0].isfile() and not members[0].islnk() and not members[0].issym())
            raw = (ROOT / row['path']).read_bytes()
            check('exact member bytes: ' + row['path'], raw == tf.extractfile(members[0]).read())
            check('file digest and size: ' + row['path'], digest(raw) == row['sha256'] and len(raw) == row['size'])
            encoding = 'utf-8' if row['inspection_encoding'] == 'utf-8' else 'latin-1'
            check('lossless complete inspection view: ' + row['path'],
                  raw.decode(encoding).encode(encoding) == raw and len(raw.decode(encoding).splitlines()) == row['lines'])
    for row in d['anchors']:
        raw = b''.join((ROOT / row['path']).read_bytes().splitlines(keepends=True)[row['first_line'] - 1:row['last_line']])
        check('inspected span: ' + row['id'], digest(raw) == row['sha256'])
    check('eleven earlier documentary exchanges retained',
          len(json.loads((ROOT / 'data/accounting-master/selected-reuse-20261015/exchanges.json').read_text())) == 11)
    result = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
              'check_count': len(checks), 'passed': all(r['passed'] for r in checks),
              'wall_seconds': time.monotonic() - started,
              'scope': 'Static text/source preservation only; not component completeness, compatibility or rights clearance'}
    (OUT / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Notice source bindings: {sum(r['passed'] for r in checks)}/{len(checks)} pass; build-specific applicability remains open.")
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
