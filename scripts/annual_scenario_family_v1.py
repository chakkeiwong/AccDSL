"""Unweighted authored alternatives over the selected reusable annual book."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

import annual_program_authoring_v1 as author

annual = author.annual
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/annual-scenario-family-20261025'
LOCK = '28a133d0bee69984e773f24bcf74ff5be339d88bd335d6f45439150c2c61f7d8'
PROFILE = 'AnnualScenarioFamily/1'
QUERY = 'AnnualScenarioReports/1'
MAX_MEMBERS = 64
MAX_PERIODS = 64
FLAGS = {**annual.FLAGS, 'probability_admitted': False,
         'historical_family_admitted': False, 'exhaustive_scenario_coverage': False}
Invalid = author.Invalid
need = author.need
canonical = annual.caller.canonical
digest = annual.book.digest


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest() == LOCK, 'family_source_lock_changed')
    for name, expected in json.loads(raw).items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             'family_dependency_changed:' + name)
    author.protected()


def text(value, label):
    need(type(value) is str and 0 < len(value) <= 4096 and bool(value.strip()), label)
    value.encode('utf-8', errors='strict')


def request(root, periods, members, max_members, name='annual alternatives'):
    return {'profile': PROFILE, 'name': name, 'meaning': 'authored_exogenous_scenarios',
            'weighting': 'unweighted', 'coverage': 'authored_members_only',
            'root_request': deepcopy(root), 'root_sha256': digest(root),
            'periods': deepcopy(periods), 'members': deepcopy(members),
            'budget': {'max_members': max_members}}


def member_request(body, member):
    program = {'profile': author.PROFILE, 'name': 'annual_member',
               'root_sha256': body['root_sha256'], 'operations': member['operations']}
    return author.compile_program(program, {body['root_sha256']: body['root_request']})['request']


def validate(body):
    protected()
    author.guarded(annual.caller.bounded, body)
    author.closed(body, ['profile', 'name', 'meaning', 'weighting', 'coverage',
                        'root_request', 'root_sha256', 'periods', 'members', 'budget'], 'family')
    need(body['profile'] == PROFILE, 'family_profile')
    text(body['name'], 'family_name')
    need(body['meaning'] == 'authored_exogenous_scenarios', 'family_meaning')
    need(body['weighting'] == 'unweighted', 'unweighted_only')
    need(body['coverage'] == 'authored_members_only', 'authored_coverage_only')
    author.digest(body['root_sha256'])
    need(body['root_sha256'] == digest(body['root_request']), 'root_digest')
    periods = body['periods']
    need(type(periods) is list and 0 < len(periods) <= MAX_PERIODS, 'period_limit')
    for period in periods:
        author.period(period)
        need(period['start'] < period['end_exclusive'], 'positive_period')
    need(all(a['end_exclusive'] == b['start'] for a, b in zip(periods, periods[1:])),
         'contiguous_periods')
    author.closed(body['budget'], ['max_members'], 'budget')
    budget = body['budget']['max_members']
    need(type(budget) is int and 0 <= budget <= MAX_MEMBERS, 'member_budget')
    members = body['members']
    need(type(members) is list and len(members) <= MAX_MEMBERS, 'member_limit')
    ids = set()
    for member in members:
        author.closed(member, ['id', 'assumptions', 'operations'], 'member')
        text(member['id'], 'member_id')
        need(member['id'] not in ids, 'duplicate_member_id')
        ids.add(member['id'])
        assumptions = member['assumptions']
        need(type(assumptions) is list, 'assumptions_list')
        assumption_ids = set()
        for item in assumptions:
            author.closed(item, ['id', 'statement', 'provenance'], 'assumption')
            for key in item:
                text(item[key], 'assumption_' + key)
            need(item['id'] not in assumption_ids, 'duplicate_assumption_id')
            assumption_ids.add(item['id'])
        member_request(body, member)  # Structural compilation only.
        carried = [op['event']['next_period'] for op in member['operations']
                   if op['kind'] == 'provisional_carry']
        need(carried == periods[1:], 'member_horizon')
    # Validate the root import even for an empty family.
    member_request(body, {'operations': []})
    return body


def error(reason):
    return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(reason)[:350],
            'members': [], 'weighting': 'unweighted', 'coverage': 'authored_members_only'}


def run(body):
    try:
        validate(body)
        # The explicit budget counts member runs, not this common-root check.
        root = annual.run(annual.request(body['root_request'], []))
        base = {'profile': PROFILE, **FLAGS, 'family_sha256': digest(body),
                'root_sha256': body['root_sha256'], 'periods': deepcopy(body['periods']),
                'source_lock_sha256': LOCK,
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'weighting': 'unweighted', 'coverage': 'authored_members_only',
                'root_check': root, 'members': []}
        if root['status'] != 'complete_provisional':
            base.update(status='root_unavailable', declared_search='not_started',
                        checked_members=0, unvisited_member_ids=[m['id'] for m in body['members']])
            base['members'] = [unvisited(m, body, 'root_unavailable') for m in body['members']]
            return base
        need(root['period_book']['after']['period'] == body['periods'][0], 'root_period')
        checked = min(len(body['members']), body['budget']['max_members'])
        for index, member in enumerate(body['members']):
            if index >= checked:
                base['members'].append(unvisited(member, body, 'member_budget'))
                continue
            req = member_request(body, member)
            result = annual.run(req)
            base['members'].append({'id': member['id'], 'assumptions': deepcopy(member['assumptions']),
                'member_sha256': digest(member), 'request_sha256': digest(req),
                'status': result['status'], 'result_sha256': digest(result), 'result': result})
        pending = [m['id'] for m in body['members'][checked:]]
        base.update(checked_members=checked, unvisited_member_ids=pending,
                    declared_search='complete' if not pending else 'partial' if checked else 'not_started')
        base['status'] = ('empty_authored_selection' if not body['members'] else
                          'partial_evaluation' if pending else
                          'evaluated_all_members' if all(m['status'] == 'complete_provisional'
                                                        for m in base['members']) else
                          'evaluated_with_incomplete_members')
        return base
    except (ValueError, TypeError, KeyError, AttributeError, OSError,
            AssertionError, OverflowError, RecursionError) as exc:
        return error(exc)


def unvisited(member, body, reason):
    return {'id': member['id'], 'assumptions': deepcopy(member['assumptions']),
            'member_sha256': digest(member), 'request_sha256': digest(member_request(body, member)),
            'status': 'unvisited', 'reason': reason, 'result_sha256': None, 'result': None}


def verify_result(body, saved):
    expected = run(body)
    try:
        return expected['status'] != 'invalid' and canonical(expected) == canonical(saved)
    except (ValueError, TypeError, OverflowError, RecursionError):
        return False


def joint_report(body, saved, period_start):
    base = {'profile': QUERY, **FLAGS, 'weighting': 'unweighted',
            'coverage': 'authored_members_only'}
    if not verify_result(body, saved):
        return {**base, 'status': 'invalid', 'reason': 'family_replay', 'members': []}
    periods = [p for p in body['periods'] if p['start'] == period_start]
    if len(periods) != 1:
        return {**base, 'status': 'invalid', 'reason': 'outside_authored_horizon', 'members': []}
    period = periods[0]
    rows = []
    for member in saved['members']:
        row = {k: deepcopy(member[k]) for k in
               ['id', 'assumptions', 'member_sha256', 'request_sha256', 'result_sha256']}
        row.update(execution_status=member['status'], status='unavailable',
                   report=None, report_sha256=None, reason='period_not_reached')
        result = member['result']
        state = result.get('period_book') if result else None
        if state:
            archives = [a for a in state['period_archive'] if a['after']['period'] == period]
            need(len(archives) <= 1, 'duplicate_archived_period')
            if archives:
                archive = archives[0]
                row.update(status='archived_provisional', report=deepcopy(archive['report']),
                           report_sha256=digest(archive['report']), reason=None,
                           through_date=archive['after']['date'], book_sha256=digest(archive),
                           assessment_status={'current': archive['current_period_tax'],
                                              'deferred': archive['current_period_deferred_tax']})
            elif state['after']['period'] == period:
                report = result['recorded_statements']
                row.update(status='current_prefix_provisional', report=deepcopy(report),
                           report_sha256=digest(report), reason=None,
                           through_date=state['after']['date'], book_sha256=digest(state),
                           assessment_status={'current': state['current_period_tax'],
                                              'deferred': state['current_period_deferred_tax']})
        elif member['status'] == 'unvisited':
            row['reason'] = member['reason']
        else:
            row['reason'] = 'member_has_no_valid_book'
        rows.append(row)
    return {**base, 'status': 'empty_authored_selection' if not rows else 'joint_authored_reports',
            'family_sha256': saved['family_sha256'], 'period': deepcopy(period),
            'declared_search': saved['declared_search'], 'members': rows}
