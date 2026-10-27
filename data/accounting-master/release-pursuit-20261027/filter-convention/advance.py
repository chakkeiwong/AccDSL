"""Select the checked manuscript, retaining active technical plans and frozen evidence."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R / 'docs/design/proposal/manuscript-selected-history-v554-20261027'
T = R / 'docs/design/proposal/manuscript-filter-v554r1-20261027'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

assert not (D / 'advancement.json').exists()
v = read(D / 'candidate-verification-02.json')
assert v['passed'] and all(x['passed'] for x in v['checks'])
assert read(D / 'relocation-01/result.json')['passed']
assert read(D / 'exact-check.json')['passed']
record = read(D / 'package-record.json')
assert sha(T / 'package-manifest.json') == record['manifest_sha256']
for row in read(T / 'package-manifest.json')['files']:
    assert sha(T / row['path']) == row['sha256']
    assert (T / row['path']).stat().st_size == row['bytes']
for row in read(D / 'candidate-baseline.json')['files']:
    assert sha(B / row['path']) == row['sha256']
for row in read(D / 'rendered-review.json')['pages']:
    assert row['review'] == 'author_viewed'
    assert sha(T / (row['volume'] + '.pdf')) == row['pdf_sha256']
    assert sha(R / row['path']) == row['image_sha256']
for name in ['result.md', 'author-review.md']:
    assert (D / name).stat().st_size > 500

paths = ['scripts/accounting_master_catalog.json', 'data/accounting-master/next-plan.json',
    'MISSION_CONTROL.md', 'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-master-program.md', 'docs/plans/accounting-mission-requirements.md',
    'docs/plans/accounting-product-design-checkpoint.md', 'docs/plans/accounting-master-current.md',
    'data/accounting-master/next-plan.md', 'docs/README.md']
before = {p: (R / p).read_bytes() for p in paths}
links = {'docs/AccDSL-latest.pdf': 'accounting-product-proposal.pdf',
    'docs/AccDSL-latest.tex': 'accounting-product-proposal.tex',
    'docs/AccDSL-simulation-foundations.pdf': 'simulation-foundations.pdf',
    'docs/AccDSL-simulation-foundations.tex': 'simulation-foundations.tex'}
link_before = {}
for p, name in links.items():
    assert (R / p).is_symlink() and (R / p).resolve() == B / name
    link_before[p] = os.readlink(R / p)
preserved = {p: sha(R / p) for p in [
    'data/accounting-master/state.json',
    'data/accounting-master/release-plan-execution-20261027/release-acceptance.json',
    'data/accounting-master/release-plan-execution-20261027/acceptance-clauses.json',
    'data/accounting-master/release-plan-execution-20261027/current-claim-map.json',
    'data/accounting-master/release-plan-execution-20261027/citation-source-index.json']}
new = {}
plans = []
for p, key in [(paths[0], 'active_execution_note'), (paths[1], 'active_execution')]:
    data = json.loads(before[p]); active = data[key]
    assert active['current_candidate'] == '5.54;834 pages;not_ready'
    for field in ['current_pdf', 'standalone_pdf']:
        assert sha(R / active[field]) == active[field + '_sha256']
    plans.append(active['active_work_plan'])
    active.update(current_candidate='5.54-R1;834 pages;not_ready',
        current_pdf=str((T / 'accounting-product-proposal.pdf').relative_to(R)),
        current_pdf_sha256=v['volumes'][0]['sha256'],
        standalone_pdf=str((T / 'simulation-foundations.pdf').relative_to(R)),
        standalone_pdf_sha256=v['volumes'][1]['sha256'],
        current_package_record=str((D / 'package-record.json').relative_to(R)),
        latest_manuscript_result=str((D / 'result.md').relative_to(R)),
        particle_weight_result=str((D / 'result.md').relative_to(R)),
        manuscript_review_frontier={'baseline': '5.52-R2', 'physical_pages_read': 132,
            'next_page': 133, 'status': 'partial_author_read; node and independent acceptance open'})
    new[p] = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
assert len(set(plans)) == 1
claim_result = json.loads(before[paths[0]])['active_execution_note']['latest_internal_result']
body = f'''## Current execution — 27 October 2026

Governing candidate **5.54-R1**, 834 main pages and 263 total / 242 body
simulation pages, remains **not_ready**. Four stable PDF/TeX links select this
checked provisional successor.
Main SHA256: {v['volumes'][0]['sha256']}.
Simulation SHA256: {v['volumes'][1]['sha256']}.

Master sequence: docs/plans/accounting-release-closure-20261027.md.
Timed pursuit: docs/plans/accounting-release-eight-hour-20261027.md.
Current manuscript result: data/accounting-master/release-pursuit-20261027/filter-convention/result.md.
Active technical plan: {plans[0]}.
Latest technical result: {claim_result}.
Acceptance index: data/accounting-master/release-plan-execution-20261027/release-acceptance.md.
Clause-level work: data/accounting-master/release-plan-execution-20261027/acceptance-clauses.md.

The successor preserves all 5.54 source/history additions and earlier coupling,
opening, EPS and edition corrections. Section 9.3 now distinguishes sequential
importance weighting from weights after ancestor resampling, derives the
ancestor-proposal ratio and illustrates double counting. Section 9.12 names the
source of its convex-program stability conditions. Eighty-one exact finite
cases support the local weight algebra; no new filtering implementation,
convergence theorem or finite-sample accuracy is claimed.

All 425 source/build checks pass. The complete repaired approximation chapter
received bounded author review; 19 final rendered-page bindings are recorded.
The 411-file package verifies. Both relocated volumes reproduce every page's
normalized text with no hidden original-worktree inputs. Full executable
evidence closure, whole-document review and independent acceptance remain open.

Ordered reading of the protected 5.52-R2 baseline has reached physical page 132;
resume at 133. Successor repairs have separate exact source/page bindings and
do not imply a whole-book read of a different PDF. Investigate section 14.13's
finite-policy scope: three asset-sale choices alone do not make continuously
varying borrowing amounts a finite action set. Continue C1/C2/C3/C4/C5 ready
work under the current technical plan; the timed pursuit ends at 15:19:56 UTC.

All 35 original MC provisions, 114 acceptance rows and 156 authored clauses
remain preserved. The 201 failure rows are targets/evidence, not 201 executed
tests. All 53 obligations, six interactions, 46 operations and 18 packages remain
open; S1–S5 partial, S6 held and E3 deferred. Complete feasible internal work
before any specific professional referral. No publication, outreach or paid
engagement is authorized. Previous control bytes are retained in the current
manuscript result's control-before directory; older assessments follow.

'''
for p in paths[2:-1]:
    s = before[p].decode(); title = s.split('\n\n', 1)[0]
    assert 'Governing candidate **5.54**' in s.split('Historical assessments below are preserved.', 1)[0]
    tail = s.split('Historical assessments below are preserved.', 1)[1]
    new[p] = title + '\n\n' + body + 'Historical assessments below are preserved.' + tail
p = paths[-1]; s = before[p].decode()
assert s.count('**Version 5.52-R1, 830 pages**') == 1
s = s.replace('**Version 5.52-R1, 830 pages**', '**Version 5.54-R1, 834 pages**')
s = s.replace('**262 pages**', '**263 pages**').replace('**241 body pages**', '**242 body pages**')
s = s.replace('- [Current integration and checks](../data/accounting-master/release-plan-execution-20261027/result.md).',
    '- [Current integration and checks](../data/accounting-master/release-pursuit-20261027/filter-convention/result.md).')
new[p] = s

backup = D / 'control-before'; backup.mkdir(exist_ok=False)
for p, b in before.items():
    q = backup / p; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(b)
dump(backup / 'stable-links.json', link_before)
assert all((R / p).read_bytes() == b for p, b in before.items())
assert all(os.readlink(R / p) == old for p, old in link_before.items())
assert all(sha(R / p) == h for p, h in preserved.items())
for p, s in new.items():
    (R / p).write_text(s)
for p, name in links.items():
    link = R / p; tmp = link.with_name(link.name + '.v554r1-next')
    assert not tmp.exists() and not tmp.is_symlink()
    tmp.symlink_to(os.path.relpath(T / name, link.parent)); os.replace(tmp, link)
    assert link.resolve() == T / name
assert all(sha(R / p) == h for p, h in preserved.items())
dump(D / 'advancement.json', {'passed': True, 'candidate': '5.54-R1;834 pages;not_ready',
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    'preserved_active_plan': plans[0], 'preserved_source_result': claim_result,
    'controls': [{'path': p, 'before': hashlib.sha256(before[p]).hexdigest(), 'after': sha(R / p)} for p in paths],
    'links': {p: {'before': link_before[p], 'after': os.readlink(R / p)} for p in links},
    'preserved_release_records': preserved,
    'evidence': {n: sha(D / n) for n in ['candidate-verification-02.json', 'package-record.json',
        'relocation-01/result.json', 'author-review.md', 'result.md']}})
print(json.dumps({'passed': True, 'candidate': '5.54-R1;not_ready', 'controls': len(paths), 'links': 4}))
