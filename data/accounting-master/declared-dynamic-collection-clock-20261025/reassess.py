"""Resolve historical coverage without returning nested records to the client."""
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'data/accounting-master/post-collection-mission-reassessment-20261025'
PRIOR = 'data/accounting-master/declared-financing-schedules-coverage-20261025/inventory.json'


def digest(x): return sha256(json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p, x): p.write_text(json.dumps(x, indent=2, ensure_ascii=False) + chr(10))


def main():
    HERE.mkdir(exist_ok=True); cache = {}; paths = {}; checks = []
    def load(name):
        if name not in cache:
            p = ROOT / name; cache[name] = json.loads(p.read_text()); paths[name] = sha(p)
        return cache[name]
    def resolve(row):
        depth = 0; trail = []; seen = set()
        while any(k in row for k in ['prior_ref', 'prior_entry', 'prior_record']):
            if 'prior_ref' in row:
                ref = row['prior_ref']; key = (ref['path'], ref['collection'], ref['id'])
                assert key not in seen; seen.add(key)
                targets = [r for r in load(ref['path'])[ref['collection']] if r['id'] == ref['id']]
                assert len(targets) == 1 and digest(targets[0]) == ref['sha256'], key
                trail.append(ref); row = targets[0]
            else:
                row = row['prior_entry'] if 'prior_entry' in row else row['prior_record']
            depth += 1
        return {'id': row['id'], 'original': row, 'reference_chain': trail, 'nesting_depth': depth}
    baseline = load(PRIOR); resolved = {}
    for group, count in [('obligations', 53), ('interactions', 6), ('operations', 46)]:
        rows = baseline[group]; assert len(rows) == len({r['id'] for r in rows}) == count
        resolved[group] = [resolve(r) for r in rows]
        assert all(a['id'] == b['id'] for a, b in zip(rows, resolved[group]))
        checks.append({'name': 'complete_and_bound:' + group, 'passed': True, 'count': count})
    inspected = ['scripts/company_book_transition_v1.py', 'scripts/method_memory_effects_v1.py',
                 'scripts/declared_collection_clock_v1.py', 'scripts/native_company_sale_v1.py',
                 'scripts/typed_history_measurement_attachment_v1.py',
                 'data/accounting-master/corporate-composition-audit-20261025/audit.md',
                 'data/accounting-master/simulator-architecture-reassessment-20261025/result.md',
                 'docs/plans/accounting-post-collection-mission-reassessment-20261025.md']
    for name in inspected: paths[name] = sha(ROOT / name)
    assert not (HERE / 'resolved-inventory.json').exists(), 'preserve recorded audit'
    dump(HERE / 'resolved-inventory.json', {'baseline': PRIOR, 'whole_requirements_closed': 0, **resolved})
    dump(HERE / 'source-lock.json', paths)
    dump(HERE / 'checks.json', {'passed': True, 'checks': checks, 'scope': 'Exact inventory/reference resolution, not acceptance of inherited claims'})
    selected = [r['original'] for r in resolved['obligations'] if r['id'] in ['MC08', 'MC09', 'MC11', 'MC19', 'MC20', 'MC23', 'MC24']]
    print(json.dumps({'coverage': [len(resolved[g]) for g in ['obligations','interactions','operations']],
                      'protected_files': len(paths), 'selected': [{k: r.get(k) for k in ['id','label','original_obligation']} for r in selected]}, indent=2))


if __name__ == '__main__': main()
