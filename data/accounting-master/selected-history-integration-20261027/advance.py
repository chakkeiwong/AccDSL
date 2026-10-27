"""Select only the checked successor; retain concurrent and frozen records."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import integrate as base

H, R, S, T = base.H, base.R, base.S, base.T
read, sha, dump = base.read, base.sha, base.dump
assert not (H / 'advancement.json').exists()
v = read(H / 'verification.json')
assert v['passed'] and all(c['passed'] for c in v['checks'])
assert read(H / 'relocation-01/result.json')['passed']
record = read(H / 'package-record.json')
assert sha(T / 'package-manifest.json') == record['manifest_sha256']
package = read(T / 'package-manifest.json')
assert len(package['files']) == 411
for row in package['files']:
    p = T / row['path']
    assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
lock = read(H / 'source-lock.json')
for name, expected in lock['sources'].items():
    assert sha(S / name) == expected
    if (S / name).suffix in ['.tex', '.md']:
        assert (T / name).read_text() == base.transform(name, (S / name).read_text())
    else:
        assert sha(T / name) == expected
for key, root in [('pdfs', S), ('evidence', R), ('inputs', H)]:
    for name, expected in lock[key].items():
        assert sha(root / name) == expected, name
for document in v['documents']:
    assert sha(T / (document['document'] + '.pdf')) == document['sha256']
for name in ['author-review.md', 'result.md', 'reset-memo.md']:
    assert (H / name).stat().st_size > 500
plan = 'docs/plans/accounting-current-claim-reconciliation-20261027.md'
old_plan = 'docs/plans/accounting-selected-history-integration-20261027.md'
assert (R / plan).is_file()
paths = ['scripts/accounting_master_catalog.json', 'data/accounting-master/next-plan.json',
    'MISSION_CONTROL.md', 'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
    'docs/plans/accounting-product-design-checkpoint.md', 'docs/plans/accounting-master-current.md',
    'data/accounting-master/next-plan.md']
before = {p: (R / p).read_bytes() for p in paths}
new = {}
preserved = {str((base.B / 'release-plan-execution-20261027' / n).relative_to(R)):
    sha(base.B / 'release-plan-execution-20261027' / n) for n in
    ['release-acceptance.json', 'acceptance-clauses.json', 'current-claim-map.json', 'citation-source-index.json']}
preserved['data/accounting-master/state.json'] = sha(base.B / 'state.json')
for path, key in [(paths[0], 'active_execution_note'), (paths[1], 'active_execution')]:
    data = json.loads(before[path])
    active = data[key]
    assert active['current_candidate'] == '5.53-R1;833 pages;not_ready'
    assert active['active_work_plan'] == old_plan
    for field in ['current_pdf', 'standalone_pdf']:
        assert sha(R / active[field]) == active[field + '_sha256']
    active.update(current_candidate='5.54;834 pages;not_ready',
        current_pdf=str((T / 'accounting-product-proposal.pdf').relative_to(R)),
        current_pdf_sha256=v['documents'][0]['sha256'],
        standalone_pdf=str((T / 'simulation-foundations.pdf').relative_to(R)),
        standalone_pdf_sha256=v['documents'][1]['sha256'],
        active_work_plan=plan, full_gap_plan=plan,
        latest_internal_result=str((H / 'result.md').relative_to(R)),
        selected_history_integration_result=str((H / 'result.md').relative_to(R)),
        current_package_record=str((H / 'package-record.json').relative_to(R)),
        next=['Reconcile C21 and all changed claim locations after the protected corrections',
              'Review retained local claims C01/C25/C23/C22; continue remaining C2/C4 and source work',
              'Keep whole-document and independent acceptance open; S6 held and E3 deferred'])
    for field in ['compression_next_plan', 'next_plan']:
        if active.get(field) == old_plan:
            active[field] = plan
    if 'active_work_plans' in active:
        active['active_work_plans'] = [plan if x == old_plan else x for x in active['active_work_plans']]
    active.setdefault('completed_plan_evidence', {})[old_plan] = str((H / 'result.md').relative_to(R))
    new[path] = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
for path in paths[2:]:
    text = before[path].decode()
    head, tail = text.split('Historical assessments below are preserved.', 1)
    head = base.once(head, 'Governing candidate **5.53-R1**, 833 main pages and 263 total / 242 body',
        'Governing candidate **5.54**, 834 main pages and 263 total / 242 body')
    head = base.once(head, '86b84b8b6cb4f63aa09b8e196f579fac8ea75058d37314cd0dcd9fffe650959f', v['documents'][0]['sha256'])
    head = base.once(head, '7d1b2e9f49b8db0d9b288fe18b03a8e8ba3de8576d36fe05045a3aa863755b98', v['documents'][1]['sha256'])
    head = base.once(head, 'Active plan: ' + old_plan + '.', 'Active plan: ' + plan + '.')
    head = base.once(head, 'Current result: data/accounting-master/selected-reading-history-20261027/result.md.',
        'Current result: data/accounting-master/selected-history-integration-20261027/result.md.')
    head = base.once(head, 'Integrate the checked join in protected5.54.',
        'The checked join is integrated in protected 5.54.')
    head += '\nThe actual predecessor is 5.53-R1, whose coupling, opening, EPS and edition\ncorrections and reading guide are preserved. The stale Markdown baseline is\nreconciled with both live JSON controls. Version 5.54 passes 3,502 source/build\nchecks, ten rendered-page inspections and the 411-file package verification.\nBoth relocated volumes match every page of normalized text with no hidden\noriginal-worktree inputs. The simulation body is unchanged from 5.53-R1.\nContinue current-claim reconciliation; the earlier C21 review must be superseded\nby inspection of its repaired hypotheses. All broad acceptance remains open.\n'
    new[path] = head + 'Historical assessments below are preserved.' + tail
links = {'docs/AccDSL-latest.pdf': 'accounting-product-proposal.pdf',
    'docs/AccDSL-latest.tex': 'accounting-product-proposal.tex',
    'docs/AccDSL-simulation-foundations.pdf': 'simulation-foundations.pdf',
    'docs/AccDSL-simulation-foundations.tex': 'simulation-foundations.tex'}
for path, name in links.items():
    assert (R / path).is_symlink() and (R / path).resolve() == S / name
    assert os.readlink(R / path) == lock['stable_links'][path]
backup = H / 'control-before'
backup.mkdir(exist_ok=False)
for path, data in before.items():
    target = backup / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
dump(backup / 'stable-links.json', lock['stable_links'])
assert all((R / path).read_bytes() == data for path, data in before.items())
assert all(sha(R / path) == expected for path, expected in preserved.items())
for path, data in new.items():
    (R / path).write_text(data)
for path, name in links.items():
    link = R / path
    temporary = link.with_name(link.name + '.v554-next')
    assert not temporary.exists() and not temporary.is_symlink()
    temporary.symlink_to(os.path.relpath(T / name, link.parent))
    os.replace(temporary, link)
    assert link.resolve() == T / name
assert all(sha(R / path) == expected for path, expected in preserved.items())
dump(H / 'advancement.json', dict(passed=True, candidate='5.54;834 pages;not_ready',
    next_plan=plan, timestamp_utc=datetime.now(timezone.utc).isoformat(),
    controls=[dict(path=p, before=sha256(before[p]).hexdigest(), after=sha(R / p)) for p in paths],
    links={p: dict(before=lock['stable_links'][p], after=os.readlink(R / p)) for p in links},
    preserved_release_records=preserved,
    evidence={n: sha(H / n) for n in ['verification.json', 'package-record.json',
        'relocation-01/result.json', 'author-review.md', 'result.md', 'reset-memo.md']}))
print(json.dumps(dict(passed=True, controls=9, links=4, candidate='5.54;834 pages;not_ready', next_plan=plan)))
