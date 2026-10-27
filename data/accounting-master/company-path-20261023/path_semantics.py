"""Conditional annual composition; no historical admission or durable store."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import sys

from jsonschema import Draft202012Validator, FormatChecker

YEAR_DIR = Path(__file__).resolve().parent.parent / 'company-inputs-20261023'
sys.path.insert(0, str(YEAR_DIR))
from authoring import closed, q, schema as year_schema
from semantics import execute as execute_year, record_digest
from reporting import build_report


def wire(value):
    if isinstance(value, Q):
        return f'{value.numerator}/{value.denominator}'
    if isinstance(value, dict):
        return {k: wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    return value


def canonical(value):
    return json.dumps(wire(value), ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def schema():
    ys = year_schema()
    yp = ys['properties']
    fields = {k: deepcopy(yp[k]) for k in ['name', 'assumption', 'period',
        'inventory', 'trade', 'cash', 'depreciation_method', 'debt', 'loan', 'tax', 'events']}
    fp = deepcopy(yp['facility']['properties'])
    fp.pop('drawn')
    fields['facility'] = closed(fp)
    fields['opening_settlements'] = {'type': 'array', 'minItems': 1,
        'items': closed({'id': {'type': 'string', 'minLength': 1},
                         'amount': deepcopy(yp['opening_claims']['items']['properties']['settlement'])})}
    value = closed({'profile': {'const': 'CompanyPathInputsDraft/1'},
        'name': {'type': 'string', 'minLength': 1},
        'assumption': {'type': 'string', 'minLength': 1},
        'initial_year': ys,
        'continuations': {'type': 'array', 'minItems': 1, 'items': closed(fields)}})
    value['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    return value


def outcome(status, **kwargs):
    return {'status': status, 'committed': False, 'conditional_state': True, **kwargs}


def closing_memory(body, run):
    """Only a completed annual run may supply a subsequent opening."""
    if run['status'] != 'complete_conditional':
        raise ValueError('incomplete year has no closing memory')
    return {'context': deepcopy(body['context']), 'period': deepcopy(body['period']),
        'balances': deepcopy(run['closing_balances']), 'inventory_units': run['inventory_units'],
        'claims': deepcopy(run['claims']), 'assets': deepcopy(run['assets']),
        'facility_id': body['facility']['id'], 'facility_drawn': run['facility_drawn'],
        'information': body['information'], 'kind': 'conditional_closing'}


def opening_adapter(memory, predecessor_sha):
    """Internal annual API adapter; never exported as historical Facts."""
    ctx = {'kind': 'Context', 'schema': 'accdsl.corporate.context.v1',
        'key': 'internal.conditional-context.' + predecessor_sha, 'revision': 0,
        'body': {**memory['context'],
                 'period_start': memory['period']['start'],
                 'period_end_exclusive': memory['period']['end_exclusive']},
        'dependencies': []}
    cd = record_digest(ctx)
    rat = lambda x: {'n': str(x.numerator), 'd': str(x.denominator)}
    state = {'kind': 'CompanyState', 'schema': 'accdsl.corporate.companystate.v1',
        'key': 'internal.conditional-closing.' + predecessor_sha, 'revision': 0,
        'body': {'context_ref': {'kind': 'Context', 'schema': ctx['schema'], 'digest': cd},
                 'balances': {k: rat(v) for k, v in memory['balances'].items()},
                 'inventory_units': rat(memory['inventory_units'])},
        'dependencies': []}
    sd = record_digest(state)
    raw = canonical({'internal_adapter_only': True, 'record_registry': {cd: ctx, sd: state}})
    return raw, sd


def carry_lifetime_claims(previous, current):
    answer = deepcopy(current)
    for key, old in previous.items():
        now = answer[key]
        now['recognised'] = old['recognised']
        now['settled'] += old['settled']
        if now['recognised'] - now['settled'] != now['outstanding']:
            raise ValueError('lifetime claim identity')
    return answer


def execute(path, source_bytes):
    errors = list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(path))
    if errors:
        return outcome('invalid', reason='path_schema', path=list(errors[0].path))
    branch_sha = digest(path)
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    definitions = [path['initial_year']] + path['continuations']
    names = [d['name'] for d in definitions]
    if len(names) != len(set(names)):
        return outcome('invalid', reason='duplicate_year_name')
    for before, after in zip(definitions, definitions[1:]):
        if before['period']['end_exclusive'] != after['period']['start']:
            return outcome('invalid', reason='nonconsecutive_periods')
    years, predecessor, memory = [], None, None
    for index, definition in enumerate(definitions):
        if index == 0:
            body, raw = deepcopy(definition), source_bytes
            origin = {'kind': 'pinned_historical_opening',
                'source_sha256': source_sha, 'opening_digest': body['opening_digest']}
        else:
            allocations = definition['opening_settlements']
            ids = [a['id'] for a in allocations]
            if len(set(ids)) != len(ids) or set(ids) != set(memory['claims']):
                return outcome('invalid', reason='opening_claim_allocation_set',
                               branch_sha256=branch_sha, years=years, stopped_index=index)
            if definition['facility']['id'] != memory['facility_id']:
                return outcome('invalid', reason='facility_identity_changed',
                               branch_sha256=branch_sha, years=years, stopped_index=index)
            allocation = {a['id']: a['amount'] for a in allocations}
            raw, od = opening_adapter(memory, predecessor)
            body = {k: deepcopy(v) for k, v in definition.items() if k != 'opening_settlements'}
            body.update(profile='CompanyYearInputsDraft/1', source={
                'path': 'internal-conditional-state:' + predecessor,
                'sha256': hashlib.sha256(raw).hexdigest()}, opening_digest=od,
                context=deepcopy(memory['context']), information=memory['information'],
                assets=deepcopy(memory['assets']),
                opening_claims=[{'id': k, 'ledger': c['ledger'],
                    'amount': wire(c['outstanding']), 'settlement': allocation[k]}
                    for k, c in memory['claims'].items()])
            body['facility']['drawn'] = wire(memory['facility_drawn'])
            origin = {'kind': 'conditional_predecessor', 'result_sha256': predecessor,
                      'closing_memory_sha256': digest(memory), 'historical_admission': False}
        annual = execute_year(body, raw)
        report = build_report(body, annual, raw)
        if report['status'] == 'invalid' and annual['status'] != 'invalid':
            return outcome('invalid', reason='annual_report', detail=report, years=years)
        record = {'index': index, 'name': definition['name'], 'period': body['period'],
            'origin': origin, 'definition_sha256': digest(definition),
            'annual_input_sha256': annual['input_sha256'],
            'annual_run': annual, 'annual_report': report}
        if annual['status'] == 'complete_conditional':
            next_memory = closing_memory(body, annual)
            if memory is not None:
                next_memory['claims'] = carry_lifetime_claims(memory['claims'], annual['claims'])
            record['closing_memory'] = next_memory
        record['result_sha256'] = digest(record)
        years.append(record)
        if annual['status'] != 'complete_conditional':
            return outcome('partial', branch_sha256=branch_sha, source_sha256=source_sha,
                years=years, stopped_index=index, stopped_status=annual['status'],
                unexecuted=[{'index': i, 'period': d['period'], 'status': 'unresolved',
                    'reason': 'predecessor_incomplete'} for i, d in enumerate(definitions) if i > index])
        predecessor, memory = record['result_sha256'], next_memory
    return outcome('complete_conditional', branch_sha256=branch_sha, source_sha256=source_sha,
                   years=years, unexecuted=[])


def verify_chain(path, result):
    if list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(path)):
        return False
    if result.get('branch_sha256') != digest(path) or result.get('source_sha256') != path['initial_year']['source']['sha256']:
        return False
    definitions = [path['initial_year']] + path['continuations']
    years = result.get('years', [])
    if not years or len(years) > len(definitions):
        return False
    if result.get('status') == 'complete_conditional':
        if len(years) != len(definitions) or result.get('unexecuted') != []:
            return False
    elif result.get('status') == 'partial':
        if result.get('stopped_index') != len(years)-1:
            return False
        expected = [{'index': i, 'period': d['period'], 'status': 'unresolved',
                     'reason': 'predecessor_incomplete'}
                    for i, d in enumerate(definitions) if i >= len(years)]
        if result.get('unexecuted') != expected:
            return False
    else:
        return False
    for i, record in enumerate(years):
        payload = {k: v for k, v in record.items() if k != 'result_sha256'}
        if record.get('result_sha256') != digest(payload) or record['index'] != i:
            return False
        if record['period'] != definitions[i]['period'] or record.get('definition_sha256') != digest(definitions[i]):
            return False
        run, report = record['annual_run'], record['annual_report']
        if run.get('input_sha256') != record['annual_input_sha256']:
            return False
        if run['status'] != 'invalid' and (report.get('input_sha256') != record['annual_input_sha256'] or report.get('source_sha256') != run['source_sha256']):
            return False
        if i == 0 and record['origin'] != {'kind': 'pinned_historical_opening',
            'source_sha256': result['source_sha256'], 'opening_digest': path['initial_year']['opening_digest']}:
            return False
        complete = run['status'] == 'complete_conditional'
        if (result['status'] == 'complete_conditional' or i < len(years)-1) and not complete:
            return False
        if result['status'] == 'partial' and i == len(years)-1 and (complete or result.get('stopped_status') != run['status']):
            return False
        if complete != ('closing_memory' in record):
            return False
        if i and record['origin'] != {'kind': 'conditional_predecessor',
            'result_sha256': years[i-1]['result_sha256'],
            'closing_memory_sha256': digest(years[i-1]['closing_memory']), 'historical_admission': False}:
            return False
    return True


def report_view(path, result, period_start):
    if not verify_chain(path, result):
        return outcome('invalid', reason='path_result_binding')
    matches = [r for r in result['years'] if r['period']['start'] == period_start]
    if not matches:
        requested = [path['initial_year']] + path['continuations']
        status = 'unresolved' if any(d['period']['start'] == period_start for d in requested) else 'invalid'
        return outcome(status, reason='period_not_executed' if status == 'unresolved' else 'period_not_requested')
    return {'branch_sha256': result['branch_sha256'], 'year_result_sha256': matches[0]['result_sha256'],
            'origin': deepcopy(matches[0]['origin']), 'report': deepcopy(matches[0]['annual_report'])}


def revise(path, source_bytes, year_index, replacement, reason):
    if list(Draft202012Validator(schema(), format_checker=FormatChecker()).iter_errors(path)) or not isinstance(replacement, dict):
        return outcome('invalid', reason='revision_schema')
    definitions = [path['initial_year']] + path['continuations']
    if type(year_index) is not int or not 0 <= year_index < len(definitions) or not isinstance(reason, str) or not reason.strip():
        return outcome('invalid', reason='revision_request')
    child = deepcopy(path)
    if year_index == 0:
        # This operation revises assumptions, never the source/opening identity.
        for k in ['source', 'opening_digest', 'context', 'period', 'information']:
            if replacement.get(k) != path['initial_year'][k]:
                return outcome('invalid', reason='revision_changes_historical_binding')
        child['initial_year'] = deepcopy(replacement)
    else:
        if replacement.get('period') != definitions[year_index]['period']:
            return outcome('invalid', reason='revision_changes_period')
        child['continuations'][year_index-1] = deepcopy(replacement)
    if digest(child) == digest(path):
        return outcome('invalid', reason='unchanged_revision')
    run = execute(child, source_bytes)
    return {'kind': 'conditional_assumption_revision', 'reason': reason,
        'parent_input_sha256': digest(path), 'child_input_sha256': digest(child),
        'changed_year_index': year_index, 'historical_restatement': False,
        'path': child, 'result': run}
