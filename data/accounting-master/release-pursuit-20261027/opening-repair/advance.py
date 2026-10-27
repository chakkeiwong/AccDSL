"""Guarded selection of the checked manuscript; preserve active technical work."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os

D = Path(__file__).resolve().parent
R = D.parents[3]
S = R / 'docs/design/proposal/manuscript-debt-reading-v553-20261027'
T = R / 'docs/design/proposal/manuscript-release-v553r1-20261027'


def sha(p):
    return sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


assert not (D / 'advancement.json').exists()
v = read(D / 'verification.json')
assert v['pass'] and all(c['pass'] for c in v['checks'])
assert read(D / 'relocation-01/result.json')['passed']
record = read(D / 'package-record.json')
assert sha(T / 'package-manifest.json') == record['manifest_sha256']
package = read(T / 'package-manifest.json')
assert len(package['files']) == 410
for row in package['files']:
    p = T / row['path']
    assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes']
for volume in v['volumes']:
    assert sha(T / (volume['name'] + '.pdf')) == volume['sha256']
assert sha(D / 'verification.json') == record['source_verification_sha256']
assert sha(D / 'rendered-review.json') == record['rendered_review_sha256']
for name in ['result.md', 'reset-memo.md']:
    assert (D / name).stat().st_size > 1000

paths = [
    'scripts/accounting_master_catalog.json',
    'data/accounting-master/next-plan.json',
    'MISSION_CONTROL.md',
    'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-master-program.md',
    'docs/plans/accounting-mission-requirements.md',
    'docs/plans/accounting-product-design-checkpoint.md',
    'docs/plans/accounting-master-current.md',
    'data/accounting-master/next-plan.md',
]
before = {p: (R / p).read_bytes() for p in paths}
catalog = json.loads(before[paths[0]])['active_execution_note']
plan = catalog['active_work_plan']
assert plan == 'docs/plans/accounting-selected-history-integration-20261027.md'
assert (R / plan).is_file()
result_path = str((D / 'result.md').relative_to(R))
preserved = {}
for name in ['release-acceptance.json', 'acceptance-clauses.json',
             'current-claim-map.json', 'citation-source-index.json']:
    p = R / 'data/accounting-master/release-plan-execution-20261027' / name
    preserved[str(p.relative_to(R))] = sha(p)
new = {}
reconciled = {}
for p in paths[:2]:
    d = json.loads(before[p])
    o = d['active_execution_note' if p == paths[0] else 'active_execution']
    assert o['current_candidate'] == '5.53;831 pages;not_ready'
    for key in ['current_pdf', 'standalone_pdf']:
        assert sha(R / o[key]) == o[key + '_sha256']
    # Copy only the reviewed navigation delta, retaining unrelated fields.
    if p == paths[1]:
        for key in ['active_work_plan', 'full_gap_plan', 'latest_internal_result',
                    'latest_reset_memo', 'remaining_work', 'next',
                    'consequential_source_review', 'source_opening_compatibility',
                    'source_opening_result']:
            if key in catalog and o.get(key) != catalog[key]:
                reconciled[key] = {'before': o.get(key), 'after': catalog[key]}
                o[key] = catalog[key]
    o.update(
        current_candidate='5.53-R1;833 pages;not_ready',
        current_pdf=str((T / 'accounting-product-proposal.pdf').relative_to(R)),
        current_pdf_sha256=v['volumes'][0]['sha256'],
        standalone_pdf=str((T / 'simulation-foundations.pdf').relative_to(R)),
        standalone_pdf_sha256=v['volumes'][1]['sha256'],
        current_package_record=str((D / 'package-record.json').relative_to(R)),
        manuscript_repair_result=result_path,
        current_internal_status=(
            '5.53-R1 selected provisionally; bounded mathematical/exposition '
            'repairs, package checks and clean-copy document reproduction pass. '
            'Whole-document, dependency and independent acceptance remain open.'),
    )
    o['active_work_plans'] = list(dict.fromkeys(
        [plan] + o.get('active_work_plans', []) +
        ['docs/plans/accounting-release-eight-hour-20261027.md']))
    timed = o['timed_release_pursuit']
    timed.pop('pending_successor', None)
    timed.update(
        selected_successor=str(T.relative_to(R)),
        manuscript_result=result_path,
        integration_note='Reconciled 5.53 debt-source additions and checked coupling/opening repairs; active technical plan preserved.',
        release_status='not_ready',
    )
    assert o['active_work_plan'] == plan
    new[p] = json.dumps(d, indent=2, ensure_ascii=False) + '\n'

annotation = '''
5.53-R1 preserves the complete 5.53 source-reading addition and corrects the
finite-coupling premises, opening examples, joint scenario domain and EPS sign
qualification. It adds reading orientation and pins the inspected arXiv edition.
All 441 source/build checks pass; nineteen pages received bounded author review.
The 410-file package verifies. Both clean-copy volumes reproduce every page's
text without original-worktree inputs. Full executable evidence closure,
whole-document review and independent acceptance remain open.
Manuscript repair: data/accounting-master/release-pursuit-20261027/opening-repair/result.md.
Timed pursuit: docs/plans/accounting-release-eight-hour-20261027.md.
'''
for p in paths[2:]:
    head, tail = before[p].decode().split('Historical assessments below are preserved.', 1)
    assert 'Active plan: ' + plan + '.' in head
    head = once(head, 'Governing candidate **5.53**, 831 main pages and 262 total / 241 body',
                'Governing candidate **5.53-R1**, 833 main pages and 263 total / 242 body')
    head = once(head, '8b23f78a0cae420b2877d2e4021373aa05fcf734a268ce95b2cb3b4ea51a5aad',
                v['volumes'][0]['sha256'])
    head = once(head, '16b5915a7e58c9e5d76fb0d1222e8d7f58b4c8155ed3d1d10f6da34fd21142de',
                v['volumes'][1]['sha256'])
    new[p] = head + annotation + 'Historical assessments below are preserved.' + tail

links = {
    'docs/AccDSL-latest.pdf': 'accounting-product-proposal.pdf',
    'docs/AccDSL-latest.tex': 'accounting-product-proposal.tex',
    'docs/AccDSL-simulation-foundations.pdf': 'simulation-foundations.pdf',
    'docs/AccDSL-simulation-foundations.tex': 'simulation-foundations.tex',
}
link_before = {}
for p, name in links.items():
    q = R / p
    assert q.is_symlink() and q.resolve() == S / name
    link_before[p] = os.readlink(q)
backup = D / 'control-before'
backup.mkdir(exist_ok=False)
for p, content in before.items():
    q = backup / p
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_bytes(content)
dump(backup / 'stable-links.json', link_before)
assert all((R / p).read_bytes() == b for p, b in before.items())
assert all(sha(R / p) == h for p, h in preserved.items())
assert all(os.readlink(R / p) == old for p, old in link_before.items())
for p, content in new.items():
    # Refuse an observed concurrent change instead of overwriting it.
    assert (R / p).read_bytes() == before[p], p
    (R / p).write_text(content)
for p, name in links.items():
    q = R / p
    tmp = q.with_name(q.name + '.v553r1-next')
    assert not tmp.exists() and not tmp.is_symlink()
    assert os.readlink(q) == link_before[p]
    tmp.symlink_to(os.path.relpath(T / name, q.parent))
    os.replace(tmp, q)
    assert q.resolve() == T / name
assert all((R / p).read_text() == content for p, content in new.items())
assert all(sha(R / p) == h for p, h in preserved.items())
dump(D / 'advancement.json', {
    'passed': True, 'candidate': '5.53-R1;833 pages;not_ready',
    'active_technical_plan': plan,
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'controls': [{'path': p, 'before': sha256(before[p]).hexdigest(),
                  'after': sha(R / p)} for p in paths],
    'links': {p: {'before': link_before[p], 'after': os.readlink(R / p)} for p in links},
    'reconciled_navigation': reconciled,
    'preserved_release_records': preserved,
    'evidence': {n: sha(D / n) for n in ['verification.json', 'package-record.json',
        'relocation-01/result.json', 'rendered-review.json', 'result.md', 'reset-memo.md']},
})
print(json.dumps({'passed': True, 'candidate': '5.53-R1;833 pages;not_ready',
                  'active_technical_plan': plan, 'controls': len(paths), 'links': len(links)}))
