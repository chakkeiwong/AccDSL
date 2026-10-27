"""Read-only dated nominal-component record for nine pinned credit histories."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NATIVE = ROOT / 'data/accounting-master/dated-credit-schedules-20261016'
PROFILE = 'RetainedCreditClaimComponents/1'
FLAGS = {'posts': False, 'mutations': [], 'accounting_admission': False,
         'legal_forgiveness': 'not_assessed', 'recovery_admission': False}


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def protected():
    lock = json.loads((HERE / 'source-lock.json').read_text())
    for name, h in lock['files'].items():
        need(sha256((ROOT / name).read_bytes()).hexdigest() == h, 'source_drift:' + name)
    return lock


def selected(case_id):
    rows = json.loads((NATIVE / 'attempt-01/exchanges.json').read_text())
    row = next((r for r in rows if r['id'] == case_id), None)
    need(row is not None, 'outside_retained_cases')
    return row


def request(case_id):
    row = selected(case_id)
    return {'profile': PROFILE, 'case_id': case_id,
            'native_request_sha256': digest(row['request']),
            'native_result_sha256': digest(row['result'])}


def project(body):
    protected()
    need(type(body) is dict and set(body) == {
        'profile', 'case_id', 'native_request_sha256', 'native_result_sha256'}, 'request_shape')
    need(body['profile'] == PROFILE, 'profile')
    row = selected(body['case_id']); req, native = row['request'], row['result']
    need(body['native_request_sha256'] == digest(req), 'request_binding')
    need(body['native_result_sha256'] == digest(native), 'result_binding')
    need(native['status'] == 'conditional_complete', 'native_status')
    original = dict(req['acquisition']['contract'])
    remaining = {d: Q(v) for d, v in original.items()}
    movements, timeline = [], []
    buckets = ['collections', 'uncollected', 'writeoff', 'revisions']

    def totals():
        out = {k: {} for k in buckets}
        for m in movements:
            bucket = out[m['component']]; d = m['due_date']
            bucket[d] = str(Q(bucket.get(d, '0')) + Q(m['amount']))
        return out

    def snapshot(stage_id, kind, date, event):
        index = len(timeline); s = native['stages'][index]
        need((s['id'], s['kind'], s['date']) == (stage_id, kind, date), 'native_stage_order')
        rem = {d: str(v) for d, v in remaining.items()}
        need(s['remaining_contract'] == rem, 'native_schedule_mismatch')
        accumulated = totals()
        dates = sorted(set(original) | set(rem) |
                       {m['due_date'] for m in movements})
        balances = []
        for d in dates:
            left = Q(original.get(d, '0')) + Q(accumulated['revisions'].get(d, '0'))
            right = sum((Q(accumulated[k].get(d, '0')) for k in buckets[:3]), Q(0)) + Q(rem.get(d, '0'))
            need(left == right, 'dated_conservation:' + stage_id + ':' + d)
            balances.append({'due_date': d, 'original': original.get(d, '0'),
                **{k: accumulated[k].get(d, '0') for k in buckets},
                'remaining': rem.get(d, '0'), 'remaining_entry_present': d in rem,
                'residual': str(left - right)})
        timeline.append({'stage_index': index, 'stage_id': stage_id, 'kind': kind,
            'date': date, 'native_stage_sha256': digest(s),
            'source_sha256': digest(event), 'movement_count': len(movements),
            'remaining': rem, 'totals': accumulated, 'per_due_date': balances})

    def movement(index, e, component, due, amount, portion=None):
        movements.append({'movement_index': len(movements), 'source_event_index': index,
            'source_event_id': e['id'], 'source_event_sha256': digest(e),
            'event_date': e['date'], 'information_date': e['information_date'],
            'component': component, 'due_date': due, 'amount': str(amount),
            'portion_id': portion, 'legal_forgiveness': 'not_assessed'})

    snapshot('acquisition', 'initial', req['acquisition']['date'], req['acquisition'])
    revisions = []
    for i, e in enumerate(req['events']):
        ident, kind, date = e['id'], e['operation'], e['date']
        snapshot(ident + '_accrual', 'accrual', date, e)
        if kind == 'credit_revision':
            fraction = Q(e['writeoff']['fraction'])
            if fraction:
                for due, value in remaining.items():
                    movement(i, e, 'writeoff', due, value * fraction, e['writeoff']['portion_id'])
                remaining = {d: v * (1 - fraction) for d, v in remaining.items()}
        elif kind == 'estimate_revision':
            replacement = {d: Q(v) for d, v in e['expected'].items()}
            revisions.append({'source_event_id': ident, 'source_event_sha256': digest(e),
                'date': date, 'before': {d: str(v) for d, v in remaining.items()},
                'after': dict(e['expected']), 'meaning': 'modeled_receipt_schedule_replacement',
                'unchanged_terms_finding': e['findings']['unchanged_terms']})
            for due in sorted(set(remaining) | set(replacement)):
                movement(i, e, 'revisions', due, replacement.get(due, Q(0)) - remaining.get(due, Q(0)))
            remaining = replacement
        elif kind == 'collect':
            amount = Q(e['amount'])
            movement(i, e, 'collections', date, amount)
            movement(i, e, 'uncollected', date, remaining.pop(date, Q(0)) - amount)
        else:
            need(kind == 'advance', 'unsupported_native_operation')
        snapshot(ident, kind, date, e)
    need(len(timeline) == len(native['stages']), 'missing_native_stage')
    # Preserve the native archives, including zero rows and their original order.
    uncollected = [{'due_date': m['due_date'], 'amount': m['amount'],
                   'legal_forgiveness': m['legal_forgiveness']}
                  for m in movements if m['component'] == 'uncollected']
    writeoff = []
    for i, e in enumerate(req['events']):
        parts = [m for m in movements if m['source_event_index'] == i and m['component'] == 'writeoff']
        if parts:
            writeoff.append({'date': e['date'], 'portion_id': e['writeoff']['portion_id'],
                             'contractual_cash': {m['due_date']: m['amount'] for m in parts}})
    collections = [{'date': m['event_date'], 'kind': 'collection', 'amount': m['amount']}
                   for m in movements if m['component'] == 'collections']
    need(uncollected == native['uncollected_contract'], 'uncollected_archive')
    need(writeoff == native['writeoff_contract'], 'writeoff_archive')
    need(collections == [f for f in native['cash_flows'] if f['kind'] == 'collection'], 'collection_archive')
    return {'profile': PROFILE, 'status': 'checked_read_only', 'case_id': body['case_id'],
        'native_request_sha256': digest(req), 'native_result_sha256': digest(native),
        'context': deepcopy(req['context']), 'amount_meaning': 'nominal_scheduled_cash',
        'original': original, 'movements': movements, 'schedule_replacements': revisions,
        'timeline': timeline, 'endpoint': {'original': original, **totals(),
            'remaining': {d: str(v) for d, v in remaining.items()}},
        'financial_derecognized': native['financial_derecognized'],
        'native_financial_components_sha256': {k: digest(native[k]) for k in
            ['journals', 'stages', 'closing', 'cash_flows', 'uncollected_contract', 'writeoff_contract']},
        'later_recovery_support': 'outside_retained_profile; native events after close are refused',
        **deepcopy(FLAGS)}


def assess(body):
    try:
        return project(body)
    except (ValueError, TypeError, KeyError, IndexError, OSError) as exc:
        return {'profile': PROFILE, 'status': 'rejected', 'reason': str(exc), **deepcopy(FLAGS)}


def validate(body, record, record_sha256):
    try:
        need(digest(record) == record_sha256, 'record_hash')
        expected = project(body)
        need(canonical(record) == canonical(expected), 'record_mismatch')
        return {'status': 'verified', 'record_sha256': record_sha256}
    except (ValueError, TypeError, KeyError, IndexError, OSError) as exc:
        return {'status': 'rejected', 'reason': str(exc)}
