"""Check current claim identities and independent finite examples; no old writers."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256, sha1
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
L = B / 'literature-closure-20261026'
S = R / 'docs/design/proposal/manuscript-selected-history-v554-20261027'
OUT = H / 'attempt-01'
OUT.mkdir(exist_ok=False)
started = time.monotonic()
checks, protected, source_rows = [], {}, []

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def check(name, value, detail=None):
    checks.append(dict(name=name, passed=bool(value), detail=detail))
    if not value:
        dump(OUT / 'failure.json', dict(checks=checks, failed=name))
        raise AssertionError(name)

def protect(path, expected=None):
    actual = digest(path)
    key = str(path.relative_to(R))
    if expected is not None:
        check('identity:' + key, actual == expected)
    if key in protected:
        check('consistent_lock:' + key, protected[key] == actual)
    protected[key] = actual

prior = B / 'current-claim-reconciliation-20261027'
for name, expected in read(prior / 'attempt-02/source-lock.json').items():
    protect(R / name, expected)
for name in ['current-claim-ledger.json', 'attempt-02/checks.json',
             'attempt-02/run-manifest.json', 'attempt-02/source-lock.json', 'result.md']:
    protect(prior / name)
for name in ['review.md', 'expected.md', 'verify.py']:
    protect(H / name)
protect(R / 'docs/plans/accounting-remaining-claim-review-20261027.md')

source_ids = {'smc2', 'particle_mcmc', 'pseudomarginal', 'epstein', 'strebulaev',
              'seaman', 'disclosure-tilburg', 'maliar', 'duarte', 'gneiting',
              'investment-payout-debt', 'shapiro-rectangular',
              'pichler-shapiro-foundations', 'xin-goldberg-time'}
for row in read(L / 'source-support.json')['records']:
    if row['id'] not in source_ids:
        continue
    protect(R / row['path'], row['sha256'])
    source_rows.append(deepcopy(row))
    for key in ['retraction_check', 'correction_check']:
        item = row.get(key, {})
        if item.get('source') not in [None, 'not available']:
            protect(R / item['source'], item.get('sha256'))
check('all_requested_source_rows', {r['id'] for r in source_rows} == source_ids)

for name in ['source-reading.md', 'software-audit.md', 'evaluation-protocol.md',
             'pmcmc-dependency.md', 'pmcmc-exact.py', 'pmcmc-exact-results.json',
             'code-integrity.json', 'actus_fixture_check.py', 'actus-fixture-results.json',
             'actus-fixture-manifest.json', 'sources/particle-mcmc-primary.txt',
             'sources/pseudomarginal-primary.txt', 'sources/smc-particles_smc_samplers.py',
             'sources/smc-particles_mcmc.py', 'text/smc2.txt', 'text/seaman.txt',
             'text/disclosure-tilburg.txt', 'text/maliar.txt', 'text/maliar-code.txt',
             'text/duarte.txt', 'text/shapiro-rectangular.txt',
             'text/pichler-shapiro-foundations.txt', 'text/xin-goldberg-time.txt',
             'text/actus-spec.txt', 'sources/actus-service-build.gradle.kts',
             'sources/actus-spec-commit.json', 'sources/dictionary12-actus-dictionary.json',
             'sources/dictionary12-actus-dictionary-terms.json',
             'sources/dictionary12-actus-dictionary-event.json',
             'sources/dictionary12-actus-dictionary-versions.json',
             'sources/actus-core-repo.json', 'sources/actus-maven.json',
             'sources/actus-tests-tests_actus-tests-pam.json']:
    protect(L / name)
protect(L / 'sources/smc-particles_smc_samplers.py',
        'edbcd79a32b1ddb1aa9364fd52b10409130de885347a0c4b86d10db38a8e5637')
protect(L / 'sources/smc-particles_mcmc.py',
        '5e1fa6e9679eb9f76dea8b1d33af9ad6e8db99ba84d68ed1839d5a5a67771fc2')
for row in read(L / 'code-integrity.json')['records']:
    p = L / 'sources' / row['local']
    protect(p, row['sha256'])
    raw = p.read_bytes()
    check('git_blob:' + row['local'], sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['expected'])
for name in ['smc2-transfer.md', 'smc2_exchange.py', 'smc2-exchange-results.json', 'smc2-run-manifest.json']:
    protect(B / 'gap-program-20261026' / name)
protect(R / 'docs/design/research/actus-interface-boundary-20261023.md')
protect(R / 'docs/design/research/software/actus-interface-20261023/EventController.java')
protect(B / 'simulation-history-financing-review-20261026/strebulaev2012.txt')

# The reference results are read, never imported or executed.
for name in ['exact-results.json', 'recent-method-results.json',
             'persistent-financing-results.json', 'pmcmc-exact-results.json']:
    result = read(L / name)
    check('retained_pass:' + name, result['status'] == 'PASS' and
          all(r['passed'] for r in result['checks']), len(result['checks']))

# C06: conditioning, revision and resampling have different meanings.
norm = lambda v: [x / sum(v) for x in v]
check('replacement_from_original_prior', norm([Q(1, 8), Q(3, 8)]) == [Q(1, 4), Q(3, 4)])
check('old_zero_cannot_recover', norm([Q(1, 4), Q(0)]) == [Q(1), Q(0)])
post = lambda p: 4*p/(1+3*p)
check('prior_set_endpoints', [post(Q(1, 4)), post(Q(3, 4))] == [Q(4, 7), Q(12, 13)])
check('rare_type_extinction', Q(99, 100)**100 > Q(1, 3))

def pmmh(laws):
    states = [(theta, z) for theta in [0, 1] for z, mass in laws[theta]]
    target = [Q(1, 2)*z*mass for theta in [0, 1] for z, mass in laws[theta]]
    kernel = []
    for i, (theta, z) in enumerate(states):
        row = [Q(0)] * len(states)
        for zp, prob in laws[1-theta]:
            acceptance = min(Q(1), zp/z)
            row[states.index((1-theta, zp))] += prob*acceptance
            row[i] += prob*(1-acceptance)
        kernel.append(row)
    return states, target, kernel

def step(mass, kernel):
    return [sum(mass[i]*kernel[i][j] for i in range(len(mass))) for j in range(len(mass))]

old = {0: [(Q(1, 2), Q(1, 2)), (Q(3, 2), Q(1, 2))], 1: [(Q(1), Q(1))]}
new = {0: [(Q(1, 4), Q(1, 2)), (Q(7, 4), Q(1, 2))], 1: [(Q(1), Q(1))]}
for label, laws, target_expected, kernel_expected in [
    ('retained', old, [Q(1, 8), Q(3, 8), Q(1, 2)],
     [[0, 0, 1], [0, Q(1, 3), Q(2, 3)], [Q(1, 4), Q(1, 2), Q(1, 4)]]),
    ('exchange', new, [Q(1, 16), Q(7, 16), Q(1, 2)],
     [[0, 0, 1], [0, Q(3, 7), Q(4, 7)], [Q(1, 8), Q(1, 2), Q(3, 8)]])]:
    states, target, kernel = pmmh(laws)
    check(label + '_target', target == target_expected)
    check(label + '_kernel', kernel == kernel_expected)
    check(label + '_invariance', step(target, kernel) == target)
    for i, j in product(range(3), repeat=2):
        check(f'{label}_balance_{i}_{j}', target[i]*kernel[i][j] == target[j]*kernel[j][i])

refresh_rates = [sum(pa*pb*min(Q(1), b/a) for a, pa in old[t] for b, pb in old[1-t]) for t in [0, 1]]
check('refresh_rates', refresh_rates == [Q(5, 6), Q(3, 4)])
refresh_mass = refresh_rates[0]/sum(refresh_rates)
check('refresh_stationary', refresh_mass == Q(10, 19))
check('refresh_bias', refresh_mass-Q(1, 2) == Q(1, 38))
weighted, unweighted = {}, {}
for theta in [0, 1]:
    for a, pa in old[theta]:
        for b, pb in new[theta]:
            s = (theta, b)
            mass = Q(1, 2)*a*pa*pb
            weighted[s] = weighted.get(s, Q(0)) + mass*b/a
            unweighted[s] = unweighted.get(s, Q(0)) + mass
check('exchange_weighted_joint', [weighted[s] for s in states] == target)
wrong = [unweighted[s] for s in states]
check('exchange_wrong_joint', wrong == [Q(1, 4), Q(1, 4), Q(1, 2)])
check('exchange_one_step_mass', step(wrong, kernel)[2] == Q(65, 112))
check('exchange_one_step_bias', step(wrong, kernel)[2]-Q(1, 2) == Q(9, 112))
retained = read(L / 'pmcmc-exact-results.json')
check('retained_refresh_result', Q(retained['refresh_type1']) == refresh_mass)
exchange = read(B / 'gap-program-20261026/smc2-exchange-results.json')
check('retained_exchange_result', exchange['status'] == 'PASS' and all(r['passed'] for r in exchange['checks']))
check('retained_exchange_joint', [Q(x) for x in exchange['desired_new_joint']] == target)

# C07/C09/C17: cash, promises, priority and ownership.
payoff = Q(9, 10)*100 + Q(1, 10)*40
price = payoff/Q(21, 20)
yield_good = 100/price-1
yield_wrong = (105-Q(1, 10)*40)/90-1
price_wrong = 100/(1+yield_wrong)
check('debt_price_and_yield', [payoff, price, yield_good] == [94, Q(1880, 21), Q(11, 94)])
check('debt_wrong_convention', [yield_wrong, price_wrong] == [Q(11, 90), Q(9000, 101)])
check('debt_payoff_residual', payoff-Q(21, 20)*price_wrong == Q(44, 101))
estate, senior, junior = 70, 60, 50
allocation = [min(estate, senior), min(max(estate-senior, 0), junior)]
check('one_estate_priority', allocation == [60, 10] and sum(allocation) == estate)
check('proportional_overdistribution', Q(7, 10)*(senior+junior) == 77 > estate)
for subscription, expected_old, expected_new in [(10, Q(1000), Q(200)), (8, Q(2900, 3), Q(580, 3))]:
    value = 1000+20*subscription
    old_value, new_value = Q(100, 120)*value, Q(20, 120)*value
    check('issue_value_' + str(subscription), [old_value, new_value] == [expected_old, expected_new])
    check('issue_conservation_' + str(subscription), old_value+new_value == value)
cash = [16-coupon-6 for coupon in [5, 7]]
check('pre_financing_cash', cash == [5, 3])
check('pre_financing_covenant', [v >= 5 for v in cash] == [True, False])
max_proceeds = (Q(4, 5)*5+Q(1, 5)*2)/Q(21, 20)
issue_face = 3/(max_proceeds/5)
check('max_debt_proceeds', max_proceeds == Q(88, 21) < 5)
check('issue_face', issue_face == Q(315, 88) and issue_face*max_proceeds/5 == 3)
gross, fee, pre_value, old_shares = Q(6), Q(1), Q(20), Q(100)
post_value = pre_value+gross-fee
share_price = (post_value-gross)/old_shares
new_shares = gross/share_price
check('equity_quote', [post_value, share_price, new_shares] == [25, Q(19, 100), Q(600, 19)])
check('equity_fraction', new_shares/(old_shares+new_shares) == Q(6, 25))
check('closing_cash_equal', [cash[0]+3, cash[1]+gross-fee] == [8, 8])

# C10/C11/C12: explicit selection and distinct structural responses.
disclose = norm([Q(9, 20), Q(1, 20)])
silence = norm([Q(1, 20), Q(9, 20)])
check('selection_posteriors', [disclose[0], silence[0]] == [Q(9, 10), Q(1, 10)])
polynomial = lambda a: a*a+2*a-1
check('cutoff_root_bracket', polynomial(Q(4142, 10000)) < 0 < polynomial(Q(4143, 10000)))
for a in [Q(0), Q(1, 4), Q(1, 2), Q(1)]:
    price_silence = (1+a*a)/(2*(1+a))
    check('cutoff_algebra_' + str(a), 2*(1+a)*(a-price_silence) == polynomial(a))
observed_a, observed_b, intervened_a, intervened_b = {}, {}, [], []
for u in [0, 1]:
    x = u
    observed_a[(x, u)] = observed_a.get((x, u), 0)+Q(1, 2)
    observed_b[(x, x)] = observed_b.get((x, x), 0)+Q(1, 2)
    intervened_a.append(Q(u, 2))
    intervened_b.append(Q(1, 2))
check('causal_observational_equality', observed_a == observed_b == {(0, 0): Q(1, 2), (1, 1): Q(1, 2)})
check('causal_intervention_difference', [sum(intervened_a), sum(intervened_b)] == [Q(1, 2), Q(1)])

# C13: only retained metadata and the explicitly scoped fixture evidence.
spec = (L / 'text/actus-spec.txt').read_text()
check('actus_spec_identity', 'v1.1-843f7a3-2020-06-08' in spec and 'dictionary-v1.2' in spec)
check('actus_spec_revision', read(L/'sources/actus-spec-commit.json')['sha'] == '843f7a362c0886f98619034f35a4cc753faec022')
build = (L/'sources/actus-service-build.gradle.kts').read_text()
check('actus_requested_dependency', 'org.actus:actus-core:1.1.0' in build and 'mavenLocal()' in build)
controller = (R/'docs/design/research/software/actus-interface-20261023/EventController.java').read_text()
check('actus_wall_clock_fallback', 'LocalDateTime.now().plusYears(5)' in controller)
check('actus_failed_versions_request_preserved', (L/'sources/dictionary12-actus-dictionary-versions.json').read_text().strip() == '404: Not Found')
fixture = read(L/'actus-fixture-results.json')
check('actus_fixture_scope', fixture['status'] == 'PASS' and len(fixture['records']) == 24 and
      all(r['passed'] for r in fixture['records']) and 'Not runtime conformance' in fixture['scope'])
check('actus_fixture_source', digest(L/'sources/actus-tests-tests_actus-tests-pam.json') == fixture['source_sha256'])

# C14: independent random contributions, objectives and derivative paths.
for theta in [Q(-1), Q(0), Q(1, 2), Q(1), Q(2)]:
    residual = lambda e: theta-1+theta*e
    mean = sum(residual(e) for e in [-1, 1])/2
    second = sum(residual(e)**2 for e in [-1, 1])/2
    paired = sum(residual(e1)*residual(e2) for e1, e2 in product([-1, 1], repeat=2))/4
    check('residual_mean_' + str(theta), mean == theta-1)
    check('residual_variance_' + str(theta), second == (theta-1)**2+theta**2)
    check('independent_pair_' + str(theta), paired == (theta-1)**2)
    check('wrong_minimum_square_' + str(theta), second == 2*(theta-Q(1, 2))**2+Q(1, 2))
a, epsilon = Q(2), Q(1, 100)
total = ((a+epsilon)**2-(a-epsilon)**2)/(2*epsilon)
partial = ((a+epsilon)*a-(a-epsilon)*a)/(2*epsilon)
check('total_versus_partial', [total, partial] == [4, 2])

# C15: mathematical propriety, not empirical forecast performance.
for p, q in product([Q(0), Q(1, 4), Q(1, 2), Q(1)], repeat=2):
    risk = q*(1-p)**2+(1-q)*p*p
    check(f'proper_binary_score_{p}_{q}', risk == (p-q)**2+q*(1-q))
    check(f'proper_binary_unique_minimum_{p}_{q}', (risk == q*(1-q)) == (p == q))

# C16: the same path support can hide a different joint-law family.
static = [sum(Q(int(x == theta), 2) for x in [0, 1]) for theta in [0, 1]]
nested = sum(Q(max(int(x == theta) for theta in [0, 1]), 2) for x in [0, 1])
check('static_nested_difference', static == [Q(1, 2), Q(1, 2)] and nested == 1)
for mix in [Q(0), Q(1, 4), Q(1, 2), Q(1)]:
    check('mixture_stays_half_' + str(mix), mix*static[0]+(1-mix)*static[1] == Q(1, 2))
es = min(t+Q(2, 3)*sum(max(Q(z)-t, 0) for z in [0, 1, 2]) for t in [Q(0), Q(1), Q(2)])
check('conditional_expected_shortfall', es == Q(5, 3))
witness = [Q(0), Q(0), Q(1, 6), Q(5, 18), Q(5, 18), Q(5, 18)]
check('six_state_envelope_feasible', sum(witness) == 1 and all(0 <= q <= Q(1, 3) for q in witness))
conditional = norm(witness[:3])
check('conditional_envelope_maximum', sum(q*z for q, z in zip(conditional, [0, 1, 2])) == 2)

# Keep all old records and their locations, adding the inspected argument routes.
ledger_path = prior / 'current-claim-ledger.json'
ledger = deepcopy(read(ledger_path))
reviewed = {'C06', 'C07', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C_PMMCMC_AUX'}
check('expected_review_population', {r['id'] for r in ledger['rows'] if r['review_status'] == 'inherited_support_not_newly_reaccepted'} == reviewed)
ledger.update(baseline_current_ledger=str(ledger_path.relative_to(R)),
              baseline_current_ledger_sha256=digest(ledger_path),
              current_review=str((H/'review.md').relative_to(R)))
def location(file, heading):
    p = S / file
    text = p.read_text()
    match = re.search(r'\\(?:sub)*section\*?\{' + re.escape(heading) + r'\}', text)
    assert match, heading
    following = re.search(r'\n\\(?:sub)*section\*?\{', text[match.end():])
    end = match.end()+following.start() if following else len(text)
    return dict(file=file, heading=heading, line_start=text[:match.start()].count('\n')+1,
                line_end=text[:end].count('\n'), sha256=digest(p))
for row in ledger['rows']:
    for loc in row['current_locations']:
        check('current_location:' + row['id'] + ':' + loc['file'], digest(S/loc['file']) == loc['sha256'])
    if row['id'] not in reviewed:
        continue
    row['prior_review_status'] = row['review_status']
    row['review_status'] = 'current_scope_matches_bounded_support_provisionally'
    row['current_review'] = str((H/'review.md').relative_to(R))
    row['next_action'] = 'Preserve checked scope and remaining edition, full-runtime, issuer-fact and independent acceptance limits'
    row['pre_review_current_locations'] = deepcopy(row['current_locations'])
    if row['id'] == 'C06':
        row['current_locations'].append(location('simulation/inference-exchange.tex', 'A correction can restore an excluded history'))
        row['source_scope_note'] = 'Epstein remains historical context; the accepted current update/replay identities are local derivations, not a new general ambiguity-learning theorem.'
    if row['id'] == 'C15':
        row['current_locations'].append(location('simulation/24-evaluation.tex', 'Conditional scenario evaluation'))
        row['source_scope_note'] = 'Gneiting supports conditional propriety; local timing, comparability and structural examples support the protocol. No new Lambrecht identification theorem or empirical E3 result.'
remaining = [r['id'] for r in ledger['rows'] if r['review_status'] == 'inherited_support_not_newly_reaccepted']
check('mapped_queue_dispositioned', not remaining and len(ledger['rows']) == 27)
for name, expected in protected.items():
    check('protected_after:' + name, digest(R/name) == expected)
dump(H/'current-claim-ledger.json', ledger)
dump(OUT/'source-support-snapshot.json', dict(records=source_rows,
     status='Retained editions and bounded historical metadata; no publisher clearance inferred'))
dump(OUT/'source-lock.json', protected)
dump(OUT/'checks.json', dict(passed=True, checks=checks, reviewed=sorted(reviewed),
     remaining=remaining, protected_files=len(protected)))
dump(OUT/'run-manifest.json', dict(command=[sys.executable, str(Path(__file__).resolve())],
     git_commit='unavailable; unusable marker preserved', environment=platform.python_version(),
     cpu_gpu='CPU standard-library exact arithmetic; no GPU or framework imports',
     seeds='N/A deterministic exact finite calculations', data_version=digest(OUT/'source-lock.json'),
     wall_seconds=time.monotonic()-started, timestamp_utc=datetime.now(timezone.utc).isoformat(),
     plan='docs/plans/accounting-remaining-claim-review-20261027.md',
     result=str((H/'result.md').relative_to(R)),
     artifacts=['current-claim-ledger.json', 'attempt-01/checks.json',
                'attempt-01/source-lock.json', 'attempt-01/source-support-snapshot.json']))
print(json.dumps(dict(passed=True, checks=len(checks), reviewed=sorted(reviewed),
     remaining=remaining, protected_files=len(protected), seconds=time.monotonic()-started)))
