"""Preserve live controls before closing Apple filing-event evidence."""
import hashlib
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
CONTROLS = [
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-master-current.md',
    'docs/plans/accounting-continuation-requirements-20261007.md',
    'data/accounting-master/next-plan.md',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / 'baseline.json').exists(), 'Snapshots are immutable'
    checks = json.loads((OUT / 'checks.json').read_text())
    assert checks['passed'] == 43 and not checks['failed']
    snapshots = []
    (OUT / 'pointers-before').mkdir(exist_ok=True)
    for rel in CONTROLS:
        path = ROOT / rel
        target = OUT / 'pointers-before' / path.name
        assert not target.exists()
        shutil.copyfile(path, target)
        snapshots.append({'live': rel, 'snapshot': str(target.relative_to(ROOT)), 'sha256': sha(target)})
    baseline = {'current_candidate_version': '2.37',
                'current_pdf_sha256': '9e6d0b433ebdbc30b65a17122dcbb2834b3c63d195b31ffaf2bea68eaa1fc880',
                'pointer_snapshots': snapshots}
    (OUT / 'baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
    print(json.dumps({'controls_preserved': len(snapshots)}))


if __name__ == '__main__':
    main()
