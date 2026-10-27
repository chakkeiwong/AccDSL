"""Add companion navigation while preserving concurrent manuscript selections."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
read = lambda p: json.loads(p.read_text())
digest = lambda p: sha256(p.read_bytes()).hexdigest()
supplement = read(HERE / 'acceptance-supplement.json')
assert all(digest(ROOT / p) == h for p, h in supplement['baseline_records'].items())
assert all(digest(ROOT / p) == h for p, h in supplement['evidence'].items())
prefix = str(HERE.relative_to(ROOT))
paths = ['scripts/accounting_master_catalog.json', 'data/accounting-master/next-plan.json',
         'MISSION_CONTROL.md', 'docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
         'docs/plans/accounting-product-design-checkpoint.md', 'docs/plans/accounting-master-current.md',
         'data/accounting-master/next-plan.md']
before = {p: (ROOT / p).read_bytes() for p in paths}
new = {}
retained = {}
for path, key in [(paths[0], 'active_execution_note'), (paths[1], 'active_execution')]:
    obj = json.loads(before[path]); current = obj[key]
    retained[path] = {k: current.get(k) for k in ['current_candidate', 'current_pdf',
        'standalone_pdf', 'active_work_plan', 'latest_manuscript_result',
        'latest_package_result', 'manuscript_review_frontier', 'timed_release_pursuit']}
    assert current['current_candidate'].startswith('5.54-R2;')
    current['latest_internal_result'] = prefix + '/result.md'
    current['latest_reset_memo'] = prefix + '/reset-memo.md'
    current['internal_evidence_companion'] = dict(result=prefix + '/result.md',
        preservation=prefix + '/preservation.json', acceptance_supplement=prefix + '/acceptance-supplement.json',
        archive=prefix + '/internal-evidence-bundle.tar.gz', included_in_selected_manuscript_package=False)
    current.setdefault('latest_internal_results', []).append(prefix + '/result.md')
    current.setdefault('completed_plan_evidence', {})['docs/plans/accounting-internal-evidence-companion-20261027.md'] = prefix + '/result.md'
    assert all(current.get(k) == v for k, v in retained[path].items())
    new[path] = json.dumps(obj, indent=2, ensure_ascii=False) + '\n'
# Keep the generated navigation hash consistent with the narrowly changed catalog.
obj = json.loads(new[paths[1]])
catalog_hash = sha256(new[paths[0]].encode()).hexdigest()
obj['catalog_sha256'] = catalog_hash
for value in obj.values():
    if isinstance(value, dict) and paths[0] in value:
        value[paths[0]] = catalog_hash
new[paths[1]] = json.dumps(obj, indent=2, ensure_ascii=False) + '\n'
old = 'Latest technical result: data/accounting-master/executable-evidence-closure-20261027/result.md.'
addition = (f'Latest technical result: {prefix}/result.md.\n'
            f'Additional acceptance evidence: {prefix}/acceptance-supplement.md.\n'
            'The separate internal companion reproduces retained-source construction and\n'
            'the 37 downstream exchanges with 2,981 checks from 262 declared inputs.\n'
            'It preserves the unresolved issuer obligations; whole-filing interpretation,\n'
            'other runtimes, installation/access and independent acceptance remain open.')
for path in paths[2:]:
    text = before[path].decode()
    head, tail = text.split('Historical assessments below are preserved.', 1)
    assert head.count(old) == 1, path
    new[path] = head.replace(old, addition) + 'Historical assessments below are preserved.' + tail
backup = HERE / 'navigation-before'
backup.mkdir(exist_ok=False)
for path, data in before.items():
    out = backup / path; out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
assert all((ROOT / p).read_bytes() == b for p, b in before.items()), 'concurrent change; inspect before retry'
for path, text in new.items():
    assert (ROOT / path).read_bytes() == before[path], path
    (ROOT / path).write_text(text)
assert all(digest(ROOT / p) == h for p, h in supplement['baseline_records'].items())
report = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), passed=True,
    changes={p: dict(before=sha256(before[p]).hexdigest(), after=digest(ROOT / p)) for p in paths},
    manuscript_controls_preserved=retained, frozen_acceptance_preserved=supplement['baseline_records'],
    stable_links_changed=False, manuscript_bytes_changed=False)
with (HERE / 'navigation-update.json').open('x') as stream:
    json.dump(report, stream, indent=2); stream.write('\n')
print(json.dumps(dict(passed=True, controls=len(paths), manuscript_selection_preserved=True)))
