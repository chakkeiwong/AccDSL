"""Read retained evidence and check independent arithmetic; never run old writers."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import platform
import re
import sys
import time

H = Path(__file__).resolve().parent
R = H.parents[2]
B = H.parent
S = R / 'docs/design/proposal/manuscript-selected-history-v554-20261027'
OLD = R / 'docs/design/proposal/manuscript-release-prep-v552r1-20261027'
L = B / 'literature-closure-20261026'
OUT = H / 'attempt-01'
OUT.mkdir(exist_ok=False)
started = time.monotonic()
checks, protected = [], {}

def read(p):
    return json.loads(p.read_text())

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def check(name, value):
    checks.append(dict(name=name, passed=bool(value)))
    assert value, name

def protect(p, expected=None):
    actual = digest(p)
    if expected is not None:
        check('identity:' + str(p.relative_to(R)), actual == expected)
    protected[str(p.relative_to(R))] = actual

def section(text, heading):
    match = re.search(r'\\(?:sub)*section\*?\{' + re.escape(heading) + r'\}', text)
    assert match, heading
    following = re.search(r'\n\\(?:sub)*section\*?\{', text[match.end():])
    end = match.end() + following.start() if following else len(text)
    return text[match.start():end]

package = read(S / 'package-manifest.json')
record = read(B / 'selected-history-integration-20261027/package-record.json')
protect(S / 'package-manifest.json', record['manifest_sha256'])
for row in package['files']:
    protect(S / row['path'], row['sha256'])
    check('size:' + row['path'], (S / row['path']).stat().st_size == row['bytes'])
old_ledger_path = B / 'consequential-source-review-20261027/current-claim-ledger.json'
old_ledger = read(old_ledger_path)
protect(old_ledger_path)
for name in ['review.md', 'expected.md', 'location-delta.json', 'verify.py']:
    protect(H / name)
protect(R / 'docs/plans/accounting-current-claim-reconciliation-20261027.md')
for name in ['source-reading.md', 'source-support.json', 'persistent-financing.py',
             'persistent-financing-results.json', 'runtime-integration.py',
             'runtime-integration-results.json', 'runtime-integration-manifest.json',
             'recent-method-cases.py', 'recent-method-results.json', 'exact_cases.py',
             'exact-results.json']:
    protect(L / name)
for row in read(L / 'source-support.json')['records']:
    if row['id'] in ['hart-moore', 'mccarthy']:
        protect(R / row['path'], row['sha256'])
        for key in ['retraction_check', 'correction_check']:
            info = row.get(key, {})
            if info.get('source'):
                protect(R / info['source'], info.get('sha256'))
for n in [7, 15, 16, 17, 18, 29, 30, 49, 50, 51, 52, 53]:
    protect(L / 'hart-reading' / f'page-{n:02d}.png')
coupling = B / 'release-pursuit-20261027/coupling-bound'
for name in ['result.md', 'check_exact.py', 'exact-results.json', 'verification.json']:
    protect(coupling / name)
coupled = read(coupling / 'exact-results.json')
check('retained_coupling_checks', coupled['passed'] and len(coupled['checks']) == 272
      and all(row['pass'] for row in coupled['checks']))
protect(R / coupled['source'], coupled['source_sha256'])
for name in ['result.md', 'verification.json', 'package-record.json']:
    protect(B / 'release-pursuit-20261027/opening-repair' / name)

# C01: independently derive both endpoint pairs and the narrowed family.
interest = lambda a: Q(100) * (Q(1, 20) * (1-a) + Q(7, 100) * a)
check('C01_endpoints', [(interest(a), 95-interest(a)) for a in [Q(0), Q(1)]]
      == [(Q(5), Q(90)), (Q(7), Q(88))])
check('C01_narrowed', [(interest(a), 95-interest(a)) for a in [Q(1, 5), Q(2, 5)]]
      == [(Q(27, 5), Q(448, 5)), (Q(29, 5), Q(446, 5))])
check('C01_marginal_pair_impossible', Q(7) + Q(90) != 95)

# C25: compare every final account and dated cash state, not stored flags alone.
runtime = read(L / 'runtime-integration-results.json')
check('runtime_original_status', runtime['status'] == 'PASS' and runtime['count'] == 174
      and all(row['passed'] for row in runtime['checks']))
manifest = read(L / 'runtime-integration-manifest.json')
protect(L / 'runtime-integration.py', manifest['source_sha256'])
for name, expected in manifest['dependencies'].items():
    protect(R / name, expected)
check('original_case_population', len(runtime['cases']) == 14)
case_map = {case['case']: case for case in runtime['cases']}
for tag in ['fixed.alpha', 'floating.alpha', 'fixed.beta', 'floating.beta']:
    case = case_map[tag]
    body, result = case['program'], case['result']
    fixed = tag.startswith('fixed')
    mapping = {line['id']: line['accounts'][0] for line in body['mapping']['lines']}
    expected = {account: Q(0) for account in body['opening']['accounts']}
    roles = dict(cash=8, inventory=104, debt=-103 if fixed else -100,
                 capital=-20 if fixed else -25, interest=5 if fixed else 7, payroll=6)
    expected.update({mapping[key]: Q(value) for key, value in roles.items()})
    check(tag + ':complete_balances', {k: Q(v) for k, v in result['current']['balances'].items()} == expected)
    expected_cash = [11, 5, 5, 8] if fixed else [9, 3, 3, 9, 8]
    cash = [Q(row['result']['transition']['after']['balances'][mapping['cash']])
            for row in result['trace'][:-1]]
    check(tag + ':dated_cash', cash == list(map(Q, expected_cash)))
    terms = result['current']['memory']['terms']
    check(tag + ':contract_face', Q(terms['face']) == (Q(9115, 88) if fixed else 100))
    check(tag + ':old_shares', Q(terms['old_shares']) == 100)
    check(tag + ':new_shares', Q(terms['new_shares']) == (0 if fixed else Q(600, 19)))
    report = result['trace'][-1]['result']
    check(tag + ':complete_report', report['status'] == 'reported'
          and Q(report['balance_sheet']['total_assets']) == 112
          and Q(report['balance_sheet']['total_liabilities']) == (103 if fixed else 100)
          and Q(report['equity']['closing']) == (9 if fixed else 12))
check('C25_price_and_face', Q(315, 88)*Q(88, 105) == 3)
check('C25_subscription', Q(600, 19)*Q(19, 100) == 6)
check('C25_ownership', Q(600, 19)/(100+Q(600, 19)) == Q(6, 25))
for tag, prefix in [('covenant_blocks_debt', 3), ('face_is_not_proceeds', 3),
                    ('covenant_cannot_precede_payment', 0), ('zero_share_price', 3),
                    ('insufficient_coupon_cash', 0), ('duplicate_issue', 4)]:
    value = case_map[tag]['result']
    check(tag, value['status'] == 'stopped_provisional' and len(value['trace']) == prefix)
mutation = {row['id']: row for row in runtime['checks'] if 'omission' in row['id']}
check('mutation_retained_assertions', len(mutation) == 2 and all(row['passed'] for row in mutation.values()))

# C23: one independent enumeration, with its expectation derived in advance.
masses = {(theta, final): Q(0) for theta, final in product([0, 1], repeat=2)}
observations = [1, None, 0]
for theta in [0, 1]:
    stay = Q(3, 4) if theta == 0 else Q(1, 2)
    for states in product([0, 1], repeat=4):
        weight = Q(1, 4)
        for t, observed in enumerate(observations):
            weight *= stay if states[t] == states[t+1] else 1-stay
            weight *= Q(1) if observed is None else (Q(4, 5) if observed == states[t+1] else Q(1, 5))
        masses[(theta, states[-1])] += weight
ordered = [masses[key] for key in sorted(masses)]
check('C23_unnormalized', ordered == [Q(n, 800) for n in [68, 23, 80, 20]])
check('C23_reopened_posterior', [value/sum(ordered) for value in ordered]
      == [Q(n, 191) for n in [68, 23, 80, 20]])
check('C23_old_restricted_posterior', [value/sum(ordered[:2]) for value in ordered[:2]]
      == [Q(68, 91), Q(23, 91)])
persistent = read(L / 'persistent-financing-results.json')
check('retained_filter_and_financing_checks', persistent['status'] == 'PASS'
      and len(persistent['checks']) == 350 and all(row['passed'] for row in persistent['checks']))
check('108_filter_comparisons', sum(row['id'].startswith('filter_vs_paths_') for row in persistent['checks']) == 108)

# C22: derive the source example's exact constraint boundary.
outside, last = max(Q(16), Q(28, 2)), max(Q(8), Q(26, 2))
check('C22_reservation_values', (outside, last) == (Q(16), Q(13)))
check('C22_wealth_boundary', outside-last-2 == 1)
for wealth in [Q(0), Q(1, 2), Q(1), Q(2)]:
    check('C22_feasibility:' + str(wealth), (wealth+2+last >= outside) == (wealth >= 1))
check('C22_cash_and_participation', (Q(1)-1, Q(1)-1+2-2, Q(1)-1+2-2+26-13) == (0, 0, 13)
      and 1+2+13 == outside and max(Q(2)-2, 0)+13 <= last)
recent = read(L / 'recent-method-results.json')
check('retained_source_example_checks', recent['status'] == 'PASS' and all(row['passed'] for row in recent['checks']))

# Reconcile file drift with actual section boundaries before reusing any review.
for name, headings in {
    'simulation/lit-09-approximation-4.tex': ['A quantitative boundary argument',
        'A common-policy regret argument', 'When sampled paths disclose their own futures'],
    'simulation/03-learning.tex': ['Set-valued evidence updates'],
    'simulation/06-equity.tex': ['A simple cash issue', 'Conversion joins debt and equity'],
}.items():
    for heading in headings:
        check('unchanged_section:' + heading, section((OLD/name).read_text(), heading) == section((S/name).read_text(), heading))
ledger = deepcopy(old_ledger)
ledger.update(candidate='5.54;not_ready', baseline_current_ledger=str(old_ledger_path.relative_to(R)),
    baseline_current_ledger_sha256=digest(old_ledger_path), current_package=str(S.relative_to(R)),
    current_package_manifest_sha256=digest(S/'package-manifest.json'),
    current_review=str((H/'review.md').relative_to(R)))
reviewed = {'C21', 'C01', 'C25', 'C23', 'C22'}
for row in ledger['rows']:
    row['prior_current_locations'] = deepcopy(row['current_locations'])
    for location in row['current_locations']:
        path = S / location['file']
        content = path.read_text()
        if location.get('heading'):
            excerpt = section(content, location['heading'])
            start = content.index(excerpt)
            location['line_start'] = content[:start].count('\n') + 1
            location['line_end'] = location['line_start'] + len(excerpt.splitlines()) - 1
        else:
            location['line_start'] = 1
            location['line_end'] = len(content.splitlines())
        location['sha256'] = digest(path)
    if row['id'] in reviewed:
        row['prior_review_status'] = row['review_status']
        row['review_status'] = 'current_scope_matches_bounded_support_provisionally'
        row['current_review'] = str((H/'review.md').relative_to(R))
        row['next_action'] = 'Preserve scoped premises and remaining source/edition, independent reproduction and acceptance limits'
    if row['id'] == 'C21':
        row['superseded_finding'] = 'Earlier review accepted insufficiently explicit initial-pairing/common-loss hypotheses; repaired current argument checked directly'
    if row['id'] in ['C04', 'C05', 'C06', 'C09']:
        row['location_reconciliation'] = 'Mapped section unchanged inside a changed file; status not promoted by identity comparison'
remaining = [row['id'] for row in ledger['rows'] if row['review_status'] == 'inherited_support_not_newly_reaccepted']
check('remaining_claim_count', len(remaining) == 12)
dump(H/'current-claim-ledger.json', ledger)
for name, expected in protected.items():
    check('protected_after:' + name, digest(R/name) == expected)
dump(OUT/'source-lock.json', protected)
dump(OUT/'checks.json', dict(passed=True, checks=checks, reviewed=sorted(reviewed),
    remaining=remaining, protected_files=len(protected)))
dump(OUT/'run-manifest.json', dict(command=[sys.executable, str(Path(__file__).resolve())],
    git_commit='unavailable; unusable marker preserved', environment=platform.python_version(),
    cpu_gpu='CPU standard-library rational arithmetic; no GPU/framework imports', seeds='N/A deterministic',
    wall_seconds=time.monotonic()-started, data_version=digest(OUT/'source-lock.json'),
    plan='docs/plans/accounting-current-claim-reconciliation-20261027.md', result=str((H/'result.md').relative_to(R)),
    artifacts=['current-claim-ledger.json', 'attempt-01/checks.json', 'attempt-01/source-lock.json'],
    timestamp_utc=datetime.now(timezone.utc).isoformat()))
print(json.dumps(dict(passed=True, checks=len(checks), reviewed=sorted(reviewed), remaining=remaining,
    protected_files=len(protected), seconds=time.monotonic()-started)))
