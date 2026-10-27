"""Index explicitly written batch judgments without inventing unread findings."""
from pathlib import Path
from hashlib import sha256
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    baseline = json.loads((HERE / 'baseline.json').read_text())
    for row in baseline['files']:
        assert sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    original = json.loads((HERE / 'original-obligations.json').read_text())
    judgments = {}
    for path in sorted(HERE.glob('batch-*.md')):
        for line_no, line in enumerate(path.read_text().splitlines(), 1):
            fields = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(fields) != 4 or not re.fullmatch(r'(MC\d{2}|G\d+|I\d{2}|P17-\d{2}\.\d{2})', fields[0]):
                continue
            key = fields[0]
            assert key not in judgments, ('duplicate judgment', key)
            judgments[key] = {'id': key, 'review_status': 'scoped_documentary_review',
                              'supported_scope': fields[1], 'historical_residual_disposition': fields[2],
                              'remaining_work_and_next_action': fields[3],
                              'review_note': str(path.relative_to(ROOT)), 'line': line_no,
                              'note_sha256': sha256(path.read_bytes()).hexdigest(),
                              'full_requirement_closed': False, 'acceptance': 'not_promoted'}
    groups = {}
    ids = set()
    for group, rows in original['groups'].items():
        groups[group] = []
        for row in rows:
            ids.add(row['id'])
            out = judgments.get(row['id'], {'id': row['id'], 'review_status': 'uninspected'})
            groups[group].append(out)
    assert set(judgments) <= ids
    complete = all(r['review_status'] != 'uninspected' for rows in groups.values() for r in rows)
    result = {'baseline': 'baseline.json',
              'judgment': 'scoped_documentary_review_complete' if complete else 'in_progress', 'groups': groups,
              'reviewed_counts': {key: sum(r['review_status'] != 'uninspected' for r in rows) for key, rows in groups.items()},
              'protected_original_counts': {key: len(rows) for key, rows in groups.items()}}
    (HERE / 'audit-status.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: result[k] for k in ['judgment','reviewed_counts','protected_original_counts']}))


if __name__ == '__main__':
    main()
