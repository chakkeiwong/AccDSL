"""Add the checked intragroup companion without changing manuscript controls."""
from hashlib import sha256
from datetime import datetime, timezone
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
digest = lambda p: sha256(p.read_bytes()).hexdigest()
supplement = json.loads((HERE / 'acceptance-supplement.json').read_text())
for p, h in {**supplement['baseline_records'], **supplement['evidence']}.items(): assert digest(ROOT / p) == h
prefix = str(HERE.relative_to(ROOT))
paths = ['scripts/accounting_master_catalog.json', 'data/accounting-master/next-plan.json',
         'MISSION_CONTROL.md', 'docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
         'docs/plans/accounting-product-design-checkpoint.md', 'docs/plans/accounting-master-current.md',
         'data/accounting-master/next-plan.md']
before = {p: (ROOT / p).read_bytes() for p in paths}; new = {}; retained = {}
for p, key in [(paths[0], 'active_execution_note'), (paths[1], 'active_execution')]:
    obj = json.loads(before[p]); current = obj[key]
    retained[p] = {k: v for k, v in current.items() if k in ['current_candidate','current_pdf','standalone_pdf',
        'active_work_plan','latest_manuscript_result','latest_package_result','manuscript_review_frontier','timed_release_pursuit']}
    current.update(latest_internal_result=prefix + '/result.md', latest_reset_memo=prefix + '/reset-memo.md')
    current['intragroup_evidence_companion'] = dict(result=prefix + '/result.md', preservation=prefix + '/preservation.json',
        acceptance_supplement=prefix + '/acceptance-supplement.json', archive=prefix + '/intragroup-replay-bundle.tar.gz',
        included_in_selected_manuscript_package=False)
    current.setdefault('latest_internal_results', []).append(prefix + '/result.md')
    current.setdefault('completed_plan_evidence', {})['docs/plans/accounting-intragroup-evidence-replay-20261027.md'] = prefix + '/result.md'
    assert all(current[k] == v for k, v in retained[p].items())
    new[p] = json.dumps(obj, indent=2, ensure_ascii=False) + '\n'
obj = json.loads(new[paths[1]]); h = sha256(new[paths[0]].encode()).hexdigest(); obj['catalog_sha256'] = h
for value in obj.values():
    if isinstance(value, dict) and paths[0] in value: value[paths[0]] = h
new[paths[1]] = json.dumps(obj, indent=2, ensure_ascii=False) + '\n'
old = 'Latest technical result: data/accounting-master/internal-evidence-companion-20261027/result.md.'
replacement = (f'Latest technical result: {prefix}/result.md.\n'
               f'Intragroup acceptance evidence: {prefix}/acceptance-supplement.md.\n'
               'Five additional intragroup profiles reproduce all 351 complete exchanges\n'
               'exactly, including 28 unresolved-tax cases; the separate internal archive\n'
               'preserves 166 inputs. Actual accounting and independent acceptance remain open.')
for p in paths[2:]:
    head, tail = before[p].decode().split('Historical assessments below are preserved.', 1)
    assert head.count(old) == 1, p
    new[p] = head.replace(old, replacement) + 'Historical assessments below are preserved.' + tail
backup = HERE / 'navigation-before'; backup.mkdir(exist_ok=False)
for p, content in before.items():
    dest = backup / p; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(content)
assert all((ROOT / p).read_bytes() == content for p, content in before.items())
for p, content in new.items():
    assert (ROOT / p).read_bytes() == before[p]
    (ROOT / p).write_text(content)
for p, h in supplement['baseline_records'].items(): assert digest(ROOT / p) == h
record = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), passed=True,
    controls={p:dict(before=sha256(before[p]).hexdigest(), after=digest(ROOT / p)) for p in paths},
    manuscript_controls_preserved=retained, frozen_acceptance_preserved=supplement['baseline_records'],
    stable_links_changed=False, manuscript_bytes_changed=False)
with (HERE / 'navigation-update.json').open('x') as stream: json.dump(record, stream, indent=2); stream.write('\n')
print(json.dumps(dict(passed=True, controls=len(paths), manuscript_selection_preserved=True)))
