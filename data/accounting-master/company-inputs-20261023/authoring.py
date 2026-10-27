"""Documentary CompanyYearInputsDraft/1 frontend; no product API."""
from fractions import Fraction
import shlex


def closed(fields):
    return {'type': 'object', 'additionalProperties': False,
            'required': list(fields), 'properties': fields}


def schema():
    text = {'type': 'string', 'minLength': 1}
    rat = {'type': 'string', 'pattern': r'^(unknown|(?:0|-?[1-9][0-9]*)/[1-9][0-9]*)$'}
    date = {'type': 'string', 'format': 'date', 'pattern': r'^\d{4}-\d{2}-\d{2}$'}
    instant = {'oneOf': [{'const': 'unknown'}, {'type': 'string', 'format': 'date-time',
               'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'}]}
    truth = {'enum': [True, False, 'unknown']}
    digest = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
    asset = closed({'id': text, 'cost': rat, 'life': rat, 'accumulated': rat, 'in_service': date})
    result = closed({
        'profile': {'const': 'CompanyYearInputsDraft/1'}, 'name': text, 'assumption': text,
        'source': closed({'path': text, 'sha256': digest}), 'opening_digest': digest,
        'context': closed({'entity': text, 'book': text, 'currency': text}),
        'period': closed({'start': date, 'end_exclusive': date}),
        'information': {'const': 'archival_exogenous_stress'},
        'inventory': closed({'method': text, 'purchase_policy': text, 'unit_cost': rat,
            'demand_units': rat, 'price': rat, 'target_units': rat, 'control_transferred': truth}),
        'opening_claims': {'type': 'array', 'minItems': 1, 'items': closed({
            'id': text, 'ledger': {'enum': ['receivable', 'payable']}, 'amount': rat, 'settlement': rat})},
        'trade': closed({'sales_claim_id': text, 'purchase_claim_id': text,
            'collection_fraction': rat, 'supplier_payment': rat}),
        'cash': closed({'payroll': rat, 'capex': rat, 'capex_life': rat,
            'capex_id': text, 'capex_service': date, 'dividend': rat}),
        'assets': {'type': 'array', 'minItems': 1, 'items': asset},
        'depreciation_method': text,
        'debt': closed({'principal': rat, 'fixed_rate': rat, 'floating_rate': rat,
            'floating_share': rat, 'coupon_years': rat}),
        'facility': closed({'id': text, 'limit': rat, 'drawn': rat, 'reserved': rat, 'eligible': truth}),
        'loan': closed({'facility_id': text, 'principal': rat, 'annual_rate': rat,
            'day_count': text, 'fee': rat, 'interest_cash_class': text}),
        'tax': closed({'rate': rat, 'method': text}),
        'events': {'type': 'array', 'minItems': 1, 'items': closed({'kind': text, 'at': instant})}})
    result['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    return result


FIELDS = {
    'source': ('path', 'sha256'), 'context': ('entity', 'book', 'currency'),
    'period': ('start', 'end_exclusive'),
    'inventory': ('method', 'purchase_policy', 'unit_cost', 'demand_units', 'price', 'target_units', 'control_transferred'),
    'opening_claim': ('id', 'ledger', 'amount', 'settlement'),
    'trade': ('sales_claim_id', 'purchase_claim_id', 'collection_fraction', 'supplier_payment'),
    'cash': ('payroll', 'capex', 'capex_life', 'capex_id', 'capex_service', 'dividend'),
    'asset': ('id', 'cost', 'life', 'accumulated', 'in_service'),
    'debt': ('principal', 'fixed_rate', 'floating_rate', 'floating_share', 'coupon_years'),
    'facility': ('id', 'limit', 'drawn', 'reserved', 'eligible'),
    'loan': ('facility_id', 'principal', 'annual_rate', 'day_count', 'fee', 'interest_cash_class'),
    'tax': ('rate', 'method'), 'event': ('kind', 'at')}
SINGLE = {'profile', 'name', 'assumption', 'opening_digest', 'information', 'depreciation_method'}
REPEAT = {'opening_claim': 'opening_claims', 'asset': 'assets', 'event': 'events'}


def lower(text):
    body = {v: [] for v in REPEAT.values()}
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        if not line.endswith(';'):
            raise ValueError(f'line {number}: missing semicolon')
        tokens = shlex.split(line[:-1], comments=False, posix=True)
        if not tokens:
            raise ValueError('empty declaration')
        kind, *args = tokens
        count = 1 if kind in SINGLE else len(FIELDS.get(kind, ()))
        if not count or len(args) != count:
            raise ValueError(f'line {number}: unknown declaration or wrong arity')
        if kind not in REPEAT:
            if kind in seen:
                raise ValueError('duplicate declaration: ' + kind)
            seen.add(kind)
        value = args[0] if kind in SINGLE else dict(zip(FIELDS[kind], args))
        if kind in {'inventory', 'facility'}:
            key = 'control_transferred' if kind == 'inventory' else 'eligible'
            if value[key] not in {'true', 'false', 'unknown'}:
                raise ValueError('expected true, false or unknown')
            value[key] = {'true': True, 'false': False, 'unknown': 'unknown'}[value[key]]
        if kind in REPEAT:
            body[REPEAT[kind]].append(value)
        else:
            body[kind] = value
    return body


def q(value):
    if not isinstance(value, str):
        raise ValueError('rational must be text')
    result = Fraction(value)
    if value != f'{result.numerator}/{result.denominator}':
        raise ValueError('noncanonical rational')
    return result
