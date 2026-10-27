"""Build complete documentary schedule bodies; never changes original evidence."""
from copy import deepcopy
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
source = json.loads((ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json').read_text())
dates = {
    'purchase': '2025-01-02T09:00:00Z',
    'delivery': '2025-01-03T09:00:00Z',
    'collection': '2025-01-05T09:00:00Z',
    'supplier_payment': '2025-01-06T09:00:00Z',
    'payroll': '2025-01-07T09:00:00Z',
    'plant_addition': '2025-12-31T09:00:00Z',
    'depreciation': '2025-12-31T10:00:00Z',
    'interest': '2025-12-31T11:00:00Z',
    'tax': '2025-12-31T12:00:00Z',
    'dividend': '2025-12-31T13:00:00Z',
    'close': '2025-12-31T14:00:00Z',
}
base = {'profile': 'SettlementScheduleDraft/1',
        'projection_ref': source['aliases']['projection.stress7'],
        'horizon': {'start': '2025-01-01T00:00:00Z', 'end_exclusive': '2026-01-01T00:00:00Z'},
        'funding_knowledge': {'tag': 'known_none', 'assumption': 'No eligible committed facility or capital action in this synthetic schedule.'},
        'events': [{'event_kind': k, 'at': v, 'after': []} for k, v in dates.items()]}
cases = []


def add(name, expected, edits=None):
    body = deepcopy(base)
    if edits:
        edits(body)
    cases.append({'id': name, 'expected': expected, 'body': body})


def event(body, kind):
    return next(e for e in body['events'] if e['event_kind'] == kind)


def early(body):
    event(body, 'supplier_payment')['at'] = '2025-01-04T09:00:00Z'


def unknown_funding(body):
    early(body)
    body['funding_knowledge'] = {'tag': 'unknown', 'reason': 'Facility availability has not been established.', 'obligations': ['facility_terms']}


def tie(body, resolve=False):
    event(body, 'supplier_payment')['at'] = event(body, 'collection')['at']
    if resolve:
        event(body, 'supplier_payment')['after'] = ['collection']


add('collection_before_supplier', 'complete')
add('supplier_before_collection', 'funding_failure', early)
add('unknown_collection_date', 'unresolved_timing', lambda b: event(b, 'collection').update(at={'tag': 'unknown', 'reason': 'Collection date not specified.', 'obligations': ['collection_date']}))
add('unknown_facility', 'unresolved_funding', unknown_funding)
add('same_instant_unordered', 'unresolved_timing', tie)
add('same_instant_ordered', 'complete', lambda b: tie(b, True))
add('missing_event', 'invalid_event_coverage', lambda b: b['events'].pop())
add('duplicate_event', 'invalid_event_coverage', lambda b: b['events'].append(deepcopy(b['events'][0])))
add('cyclic_dependency', 'invalid_dependency_cycle', lambda b: event(b, 'purchase').update(after=['delivery']))
add('predecessor_scheduled_later', 'invalid_date_order', lambda b: event(b, 'delivery').update(at='2025-01-01T12:00:00Z'))
add('end_exclusive_event', 'invalid_horizon', lambda b: event(b, 'close').update(at='2026-01-01T00:00:00Z'))
add('unsupported_field', 'invalid_schema', lambda b: b.update(hidden_overdraft=100))
add('unresolved_reference', 'invalid_reference', lambda b: b['projection_ref'].update(digest='0' * 64))
add('invalid_calendar_date', 'invalid_schema', lambda b: event(b, 'collection').update(at='2025-02-30T09:00:00Z'))
add('reversed_array_same_dates', 'complete', lambda b: b['events'].reverse())
out = OUT / 'schedule-cases.json'
assert not out.exists(), 'Preserve existing examples; use an explicit revision for changes.'
out.write_text(json.dumps({'scope': 'synthetic schedule annotations; not inferred invoice dates', 'cases': cases}, indent=2) + chr(10))
print(json.dumps({'prepared': len(cases), 'path': str(out.relative_to(ROOT))}))
