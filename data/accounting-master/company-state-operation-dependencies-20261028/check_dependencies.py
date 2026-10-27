"""Compare symbolic dependencies with complete independent native replays."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import dependencies as dep
import typed_history_measurement_attachment_v1 as attachment

ROOT = dep.ROOT
HERE = 'data/accounting-master/company-state-operation-dependencies-20261028'
PLAN = 'docs/plans/company-state-operation-dependencies-20261028.md'
PACKET = 'data/accounting-master/company-state-information-bridge-20261028/attempt-01/exact-results.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    packet = json.loads((ROOT / PACKET).read_text())
    history = packet['base']['history']
    budget = packet['views'][0]['native_result']['budget']
    expected_hash = dep.native.core.digest(history)
    queries = []
    def term(kind, field, coefficient='1/1'):
        return dict(kind=kind, field=field, coefficient=coefficient)
    for day in [history['opening_date'], *history['dates']]:
        for group, kind in [('accounts', 'account'), ('memory', 'memory')]:
            for name in history[group]:
                queries.append(dict(id=day+':'+kind+':'+name, date=day, terms=[term(kind, name)]))
    queries.append(dict(id='cancelled_cash', date='2024-07-02',
                        terms=[term('account', 'paa.cash'), term('account', 'paa.cash', '-1/1')]))
    queries.append(dict(id='balance', date='2024-07-02',
                        terms=[term('account', name) for name in history['accounts']]))
    queries.append(dict(id='component_difference', date='2024-07-02',
                        terms=[term('memory', 'transferred_risk'), term('memory', 'nonperformance', '-1/1')]))
    saved = deepcopy((history, queries))
    result = dep.inspect(history, budget, queries, expected_hash)
    checks = []
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=actual, expected=expected))
    check('complete retained witness population', len(packet['views'][0]['independent_replays']), 3)
    check('immutable inputs', (history, queries), saved)
    check('full history retained', result['history'], history)
    check('all obligations retained', result['obligations'], history['obligations'])
    check('all excluded mechanisms retained', result['exclusions'], history['scope']['exclusions'])
    check('no variable removal', result['removed_variables'], [])
    check('all original variables retained', result['retained_variables'], sorted(result['domains']))
    check('not an executable reduction', result['executable_reduction'], None)
    check('no generic precondition claim', result['operational_preconditions_checked'], False)
    check('opening prefix', result['date_prefix']['2023-12-31'], 0)
    check('January final same-day prefix', result['date_prefix']['2024-01-01'], 2)
    check('July final same-day prefix', result['date_prefix']['2024-07-02'], 10)
    check('all event prefixes constrained', sorted({c['prefix'] for c in result['constraints'] if c['kind']=='balance'}), list(range(11)))
    check('all state constraints at all prefixes',
          sorted((c['id'], c['prefix']) for c in result['constraints'] if c['kind']=='state_constraint'),
          sorted((r['id'], i) for r in history['state_constraints'] for i in range(11)))
    check('all measurements constrained', [c['id'] for c in result['constraints'] if c['kind']=='reported_measurement'], ['held_claims'])
    by_id = {r['query']['id']: r for r in result['queries']}
    var = dep.native.identifier
    cash_expected = {var('opening_account', 'paa.cash'): '1/1',
        var('event_amount', 'premium_received'): '1/1', var('event_amount', 'held_premium_paid'): '-1/1',
        var('event_amount', 'claims_paid'): '-1/1', var('event_amount', 'recovery_received'): '1/1'}
    held_expected = {var('opening_account', 'paa.held_claims'): '1/1',
        var('event_amount', 'covered_recovery'): '1/1', var('event_amount', 'transferred_risk'): '1/1',
        var('event_amount', 'nonperformance'): '-1/1', var('event_amount', 'recovery_received'): '-1/1'}
    check('independent cash dependencies', by_id['2024-07-02:account:paa.cash']['expression'], cash_expected)
    check('independent held-claim dependencies', by_id['2024-07-02:account:paa.held_claims']['expression'], held_expected)
    check('component memory preserved', by_id['2024-07-02:memory:transferred_risk']['expression'],
          {var('opening_memory', 'transferred_risk'): '1/1', var('event_amount', 'transferred_risk'): '1/1'})
    cancelled = by_id['cancelled_cash']
    check('exact algebraic cancellation', cancelled['expression'], {})
    check('cancelled inputs remain traceable', cancelled['cancelled_dependencies'], sorted(cash_expected))
    check('cancelled cash still constrained', set(cash_expected) <= set(result['constraint_dependencies']), True)
    check('aggregate balance depends only on opening', by_id['balance']['expression'],
          {var('opening_account', k): '1/1' for k in history['accounts']})
    replays = []
    for index, old in enumerate(packet['views'][0]['independent_replays']):
        witness = old['witness']
        # The attachment witness also includes measurement variables. The native
        # history profile requires exactly its own complete variable population.
        history_witness = {k: witness[attachment.key('history', k)] for k in result['domains']}
        native = dep.native.replay_witness(history, budget, history_witness)
        check('complete retained history '+str(index), native, old['replay']['history'])
        for row in result['queries']:
            query = row['query']
            snapshot = native['snapshots'][query['date']]
            expected = sum((Q(t['coefficient']) * Q(snapshot['accounts' if t['kind']=='account' else 'memory'][t['field']]) for t in query['terms']), Q(0))
            check('native query '+str(index)+':'+query['id'], dep.evaluate(row['expression'], history_witness), dep.native.rat(expected))
        for c in result['constraints']:
            actual = dep.evaluate(c['expression'], history_witness)
            if c['kind'] == 'balance':
                check('balance '+str(index)+':'+str(c['prefix']), actual, '0/1')
            else:
                check('constraint '+str(index)+':'+c['id']+':'+str(c['prefix']),
                      dep.native.prior.in_domain(Q(actual), c['domain']['interval']), True)
        replays.append(dict(witness=history_witness, full_native_replay=native))
    controls = [
        ('unknown date', lambda q: q[0].update(date='2024-07-03')),
        ('unknown field', lambda q: q[0]['terms'][0].update(field='missing')),
        ('unknown kind', lambda q: q[0]['terms'][0].update(kind='economic_truth')),
        ('duplicate query', lambda q: q.append(deepcopy(q[0]))),
        ('invalid coefficient', lambda q: q[0]['terms'][0].update(coefficient='1/0')),
        ('empty expression', lambda q: q[0].update(terms=[])),
        ('zero expression term', lambda q: q[0]['terms'][0].update(coefficient='0/1')),
    ]
    for name, mutate in controls:
        q = deepcopy(queries)
        mutate(q)
        try:
            dep.inspect(history, budget, q, expected_hash)
            refused = False
        except (ValueError, ZeroDivisionError):
            refused = True
        check('refuse ' + name, refused, True)
    for name, h, digest in [('altered external identity', history, '0'*64),
            ('observation is not a history', packet['base']['measurements'], dep.native.core.digest(packet['base']['measurements']))]:
        try:
            dep.inspect(h, budget, queries, digest)
            refused = False
        except ValueError:
            refused = True
        check('refuse ' + name, refused, True)
    changed = deepcopy(history)
    obligation = dict(id='unresolved_operation_population',
                      meaning='Actual operating population remains unknown', affects=['scope'])
    changed['obligations'].append(obligation)
    changed_result = dep.inspect(changed, budget, queries, dep.native.core.digest(changed))
    check('new unresolved obligation retained', changed_result['obligations'], [obligation])
    check('obligation never creates permission', changed_result['executable_reduction'], None)
    failed = [c for c in checks if not c['passed']]
    modules = [dep, attachment, dep.native, dep.native.prior, dep.native.joint, dep.native.core, dep.native.joint.types, dep.native.joint.solver]
    paths = [Path(__file__), ROOT / PLAN, ROOT / PACKET, *(Path(m.__file__) for m in modules)]
    manifest = dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv], environment=sys.version,
        cpu_gpu='CPU-only exact affine inspection and witness replay; no accelerator imports',
        random_seeds='N/A deterministic', data_version='Retained complete synthetic insurance history and all three witnesses',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-start,
        plan_file=PLAN, result_file=HERE+'/result.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths})
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), failed=failed,
        queries=len(queries), prefixes=len(history['events'])+1, full_native_replays=len(replays))
    def safe(x):
        if isinstance(x, set): return sorted(x)
        raise TypeError(type(x).__name__)
    for name,value in [('dependencies.json',result),('full-replays.json',replays),
                       ('checks.json',checks),('verification.json',verification),('run-manifest.json',manifest)]:
        (out/name).write_text(json.dumps(value,indent=2,default=safe)+chr(10))
    print(json.dumps(verification,default=safe))
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
