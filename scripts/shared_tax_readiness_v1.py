"""Finite tax-information declarations, without tax calculation or admission."""
from copy import deepcopy
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
import json
import shared_book_authoring_v1 as author
import method_requirements_v3 as requirements

reports = author.reports
book = reports.book
core = requirements.v1
ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'data/accounting-master/shared-tax-readiness-20261024'
LOCK = '5e79e90fd87a448f0738382caf341429fdb72f190969aba9552a486dd3258939'
PROFILE = 'SharedTaxInformation/1'
FLAGS = {'executed': False, 'calculation_ready': False, 'source_admission': False,
         'accounting_admission': False, 'annual_close_ready': False}
GLOBAL_TEXT = ['jurisdiction', 'regime', 'interval_basis', 'loss_route',
               'deferred_recognition', 'recovery_basis', 'cash_settlement_policy']
GLOBAL_FINDINGS = ['interval_coverage', 'reconciliation_coverage',
                   'temporary_difference_population', 'opening_basis_support',
                   'recognition_support']


def protected():
    raw = (HERE / 'source-lock.json').read_bytes()
    core.need(sha256(raw).hexdigest() == LOCK, 'source_lock_changed')
    for name, expected in json.loads(raw).items():
        core.need(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                  'protected_source_changed:' + name)


def pointer(value): return value.replace('~', '~0').replace('/', '~1')
def reference(key): return {'op': 'ref', 'id': key}
def constant(value, kind): return {'op': 'const', 'type': kind, 'value': value}
def compare(op, a, b): return {'op': op, 'left': a, 'right': b}


def request(report_request, interval, information):
    return {'profile': PROFILE, 'report_request': deepcopy(report_request),
            'report_request_sha256': book.digest(report_request),
            'interval': deepcopy(interval), 'information': deepcopy(information)}


def population(native, report_request):
    states = [report_request['opening']]
    states += [r['result']['proposal']['after'] for r in native['execution']['trace']
               if r['result']['status'] == 'proposed']
    rights = set()
    for state in states:
        for lease in state['leases']:
            for right in lease['component']['rights']:
                rights.add((lease['component']['lease_id'], right['right_id']))
    return {'pretax_accounts': [k for k in reports.INCOME if k not in ['current_tax', 'deferred_tax']],
            'basis_accounts': [k for k in reports.ASSETS + reports.LIABILITIES if k not in ['dta', 'dtl']],
            'lease_rights': [{'lease_id': a, 'right_id': b} for a, b in sorted(rights)]}


def catalog(native, report_request):
    pop = population(native, report_request)
    text_type = {'kind': 'text', 'context': {}}
    context = {k: v for k, v in native['context'].items() if k != 'currency'}
    money = {'kind': 'rational', 'context': context,
             'dimensions': {'currency:' + native['context']['currency']: 1}, 'scale': '1/1'}
    rational = {'kind': 'rational', 'context': {}, 'dimensions': {}, 'scale': '1/1'}
    fields = {key: text_type for key in GLOBAL_TEXT}
    fields.update({key: core.BOOL for key in GLOBAL_FINDINGS})
    fields['rate'] = rational
    for account in pop['pretax_accounts']:
        root = 'income/' + pointer(account)
        fields[root + '/treatment'] = text_type
        fields[root + '/current_adjustment'] = money
    for account in pop['basis_accounts']:
        root = 'basis/' + pointer(account)
        fields[root + '/opening'] = money; fields[root + '/closing'] = money
    for right in pop['lease_rights']:
        root = 'lease/' + pointer(right['lease_id']) + '/' + pointer(right['right_id'])
        for when in ['opening', 'closing']:
            for side in ['asset', 'liability']:
                fields[root + '/' + when + '_' + side + '_tax_base'] = money
        for item in ['deduction_timing', 'modification_gain_treatment']:
            fields[root + '/' + item] = text_type
    return deepcopy(fields), pop


def inspect(body):
    protected(); author.lexical.bounded(body)
    core.closed(body, ['profile', 'report_request', 'report_request_sha256', 'interval', 'information'], 'tax_information_request')
    core.need(body['profile'] == PROFILE, 'profile')
    core.need(body['report_request_sha256'] == book.digest(body['report_request']), 'report_request_digest')
    report_request = body['report_request']
    author.validate_program(author.from_request(report_request, 'tax_information'))
    interval = body['interval']
    core.closed(interval, ['start', 'end_exclusive', 'activity_through'], 'interval')
    start, end, through = [core.scalar(interval[k], 'date') for k in ['start', 'end_exclusive', 'activity_through']]
    opening = report_request['opening']
    core.need(start == date.fromisoformat(opening['date']) == date.fromisoformat(opening['period']['start']),
              'opening_interval_start')
    core.need(start < end <= date.fromisoformat(opening['period']['end_exclusive']), 'interval_bounds')
    core.need(through == end - timedelta(days=1), 'exclusive_endpoint')
    for outer in report_request['events']:
        day = date.fromisoformat(outer['event']['date'])
        core.need(start <= day < end, 'event_outside_tax_interval')
    core.need(type(body['information']) is dict, 'information_map')
    native = reports.calculate(report_request)
    return native


def assess(body):
    try:
        native = inspect(body)
        if native['status'] != 'recorded_prefix':
            return {'profile': PROFILE, **FLAGS, 'status': native['status'],
                    'reason': 'native_report:' + native.get('reason', native['status']),
                    'request': deepcopy(body), 'native_report': native}
        fields, pop = catalog(native, body['report_request'])
        info = body['information']; core.need(set(info) <= set(fields), 'undeclared_information')
        inputs, values, rules = {}, {}, []
        request_hash = book.digest(body)
        for key, kind in fields.items():
            inputs[key] = {'type': deepcopy(kind), 'role': 'assumption',
                'source_ref': 'sha256:' + request_hash + '#/information/' + pointer(key)}
            if key in info:
                item = info[key]
                core.need(type(item) is dict, 'information_binding')
                if item.get('status') == 'known':
                    core.closed(item, ['status', 'value', 'provenance'], 'known_information')
                    origin = item['provenance']; core.closed(origin, ['kind', 'reference'], 'provenance')
                    core.need(origin['kind'] in ['assumption', 'source_reference'], 'provenance_kind')
                    core.text(origin['reference'], 'provenance_reference')
                    core.scalar(item['value'], kind['kind'])
                    core.need(item['value'] != 'unknown', 'unknown_must_be_explicit')
                    values[key] = {'status': 'known', 'value': deepcopy(item['value'])}
                    inputs[key]['role'] = 'assumption' if origin['kind'] == 'assumption' else 'reported_measurement'
                else:
                    core.closed(item, ['status', 'reason'], 'unknown_information')
                    core.need(item['status'] == 'unknown', 'information_status')
                    core.text(item['reason'], 'unknown_reason'); values[key] = deepcopy(item)
            predicate = reference(key) if kind == core.BOOL else compare('eq', reference(key), reference(key))
            if key == 'rate':
                predicate = compare('le', constant('0/1', kind), reference(key))
            rules.append({'id': key, 'guard': constant(True, core.BOOL), 'guard_requires': [],
                'predicate': predicate, 'requires': [key], 'admission_refs': [],
                'on_false': 'unsupported' if kind == core.BOOL else 'invalid', 'on_unknown': 'unresolved'})
        complete = native['execution']['status'] == 'complete'
        inputs['execution_complete'] = {'type': core.BOOL, 'role': 'state',
            'source_ref': 'sha256:' + book.digest(native) + '#/execution/status'}
        values['execution_complete'] = {'status': 'known', 'value': True} if complete else {
            'status': 'unknown', 'reason': 'requested_events_not_completed'}
        rules.append({'id': 'execution_complete', 'guard': constant(True, core.BOOL), 'guard_requires': [],
            'predicate': reference('execution_complete'), 'requires': ['execution_complete'],
            'admission_refs': [], 'on_false': 'unsupported', 'on_unknown': 'unresolved'})
        definition = {'profile': requirements.PROFILE, 'method_id': 'shared.tax.information', 'version': '1',
            'inputs': inputs, 'requirements': rules, 'required_known': list(inputs), 'capabilities': [],
            'residual_prerequisites': ['Jurisdictional method validity, source admission, tax computation, posting and annual completion remain separate.']}
        selected = core.digest(definition)
        result = requirements.assess({selected: definition}, selected, values, [])
        status = 'information_supplied' if result['status'] == 'requirements_satisfied' else result['status']
        return {'profile': PROFILE, **FLAGS, 'status': status, 'request_sha256': request_hash,
            'source_bundle_sha256': LOCK, 'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'request': deepcopy(body), 'native_report': native, 'population': pop,
            'required_information': fields, 'requirements_definition': definition, 'requirements_result': result,
            'unresolved_information': [r['input'] for r in result.get('required_known_findings', []) if r['consequence'] == 'unresolved'],
            'meaning': 'Declared information completeness only; no tax amount or annual authorization is established'}
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError, OverflowError, AssertionError) as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}


def verify_result(body, result):
    try: return book.caller.canonical(result) == book.caller.canonical(assess(body))
    except (ValueError, TypeError, RecursionError, OverflowError): return False
