"""Validate the supervised research program; never execute its task descriptions."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'data/accounting-master/unified-program-20261028'


def validate(root: Path, directory: Path) -> dict:
    def read(path):
        return json.loads(path.read_text())
    program = read(directory / 'program.json')
    tasks = program['tasks']
    errors = []
    ids = [t['id'] for t in tasks]
    by_id = {t['id']: t for t in tasks}
    if len(ids) != len(by_id):
        errors.append('duplicate task identifiers')
    states = {'planned', 'in_progress', 'complete', 'held'}
    for t in tasks:
        if t['status'] not in states:
            errors.append('invalid status: ' + t['id'])
        for key in ('deliverable', 'completion_criterion', 'next_action', 'failure_conditions', 'requirements', 'closure_packages'):
            if not t.get(key):
                errors.append('missing ' + key + ': ' + t['id'])
        for dep in t['depends_on']:
            if dep not in by_id:
                errors.append('missing dependency ' + dep + ': ' + t['id'])
            elif t['status'] == 'complete' and by_id[dep]['status'] != 'complete':
                errors.append('complete task has unfinished prerequisite: ' + t['id'])
        if t['status'] == 'complete' and not t.get('evidence'):
            errors.append('complete task has no evidence: ' + t['id'])
        for path in t.get('evidence', []):
            if not (root / path).is_file():
                errors.append('missing evidence ' + path)
    visiting, visited = set(), set()
    def visit(id):
        if id in visiting:
            errors.append('dependency cycle at ' + id)
            return
        if id in visited or id not in by_id:
            return
        visiting.add(id)
        for dep in by_id[id]['depends_on']:
            visit(dep)
        visiting.remove(id)
        visited.add(id)
    for id in ids:
        visit(id)
    populations = {}
    for file, expected_count in [('acceptance-map.json', 114), ('clause-map.json', 156)]:
        mapped = read(directory / file)
        baseline = read(root / mapped['baseline'])['rows']
        rows = mapped['rows']
        populations[file] = len(rows)
        if len(rows) != expected_count or [r['original_row'] for r in rows] != baseline:
            errors.append('original conditions changed: ' + file)
        if file == 'acceptance-map.json' and sum(r['id'].startswith('MC') for r in rows) != 35:
            errors.append('original MC population changed')
        for row in rows:
            if not row['tasks'] or any(t not in by_id for t in row['tasks']):
                errors.append('missing task coverage: ' + row['id'])
    packages = read(directory / 'package-map.json')['rows']
    original_packages = read(root / 'data/accounting-master/acceptance-priority-20261027/closure-packages.json')['packages']
    if [p['original_row'] for p in packages] != original_packages:
        errors.append('original package conditions changed')
    if len(packages) != 18 or {p['id'] for p in packages} != {f'W{i:02d}' for i in range(1, 19)}:
        errors.append('closure-package population changed')
    for p in packages:
        if not p['tasks'] or any(t not in by_id or p['id'] not in by_id[t]['closure_packages'] for t in p['tasks']):
            errors.append('package has incompatible task mapping: ' + p['id'])
    for path, expected in read(directory / 'source-lock.json').items():
        p = root / path
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            errors.append('protected/source identity changed: ' + path)
    failures = read(directory / 'failure-map.json')
    original_failures = read(root / failures['baseline'])
    expected_failures = [dict(group=k, original_row=x) for k in ['original', 'literature_extensions', 'cross_interface'] for x in original_failures[k]]
    if len(failures['rows']) != 201 or [dict(group=r['group'], original_row=r['original_row']) for r in failures['rows']] != expected_failures:
        errors.append('original failure population changed')
    for r in failures['rows']:
        if not r['tasks'] or any(t not in by_id for t in r['tasks']):
            errors.append('unmapped failure: ' + r['original_row']['id'])
    complete = {t['id'] for t in tasks if t['status'] == 'complete'}
    ready = [t['id'] for t in tasks if t['status'] in {'planned', 'in_progress'} and set(t['depends_on']) <= complete]
    pending = {t['id']: [d for d in t['depends_on'] if d not in complete] for t in tasks if t['status'] in {'planned', 'in_progress'} and t['id'] not in ready}
    return dict(valid=not errors, errors=errors, tasks=len(tasks), populations=populations,
                complete=sorted(complete), ready=ready, awaiting_dependencies=pending,
                held=[t['id'] for t in tasks if t['status'] == 'held'],
                release_status=program['release_status'],
                scope='Structural consistency and protected identities only; no scientific or release acceptance')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', type=Path, default=DEFAULT)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    result = validate(ROOT, args.directory.resolve())
    if args.output:
        with args.output.open('x') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
    print(json.dumps(result, indent=2))
    return 0 if result['valid'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
