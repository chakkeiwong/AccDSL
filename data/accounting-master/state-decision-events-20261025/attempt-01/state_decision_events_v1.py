"""Authored current-state decisions; native annual accounting remains unchanged."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from pathlib import Path
import annual_inventory_program_v1 as runtime
import company_functions_v1 as functions

PROFILE = 'StateDecisionEvent/1'
FLAGS = {'committed': False, 'physical_durability': False, 'source_admission': False,
         'accounting_admission': False, 'method_eligible': False,
         'temporal_admission': False, 'historical_execution_established': False,
         'forecast_admission': False, 'real_behavior_evidence': False}
PINS = {
    'annual_inventory_program_v1.py': 'a2e76cddfb8bb7061d9c5ab616f39f0de0adc764dabd354ec4065259fc971fa9',
    'company_functions_v1.py': '148aa59be38de0afb46b86983e3d3e2b83284b043ffdfc6058a7af9a32f3f447'}
MAX_DECISIONS = 64
MAX_INPUTS = 32

class Refused(ValueError):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason
        super().__init__(reason)

def need(ok, reason, status='invalid'):
    if not ok: raise Refused(status, reason)

def closed(value, fields):
    need(type(value) is dict and set(value) == set(fields), 'closed_fields')

def text(value, label):
    need(type(value) is str and 0 < len(value) <= 4096 and bool(value.strip()), label)
    value.encode('utf-8', 'strict')

def day(value):
    need(type(value) is str, 'date_required')
    result = date.fromisoformat(value)
    need(result.isoformat() == value, 'canonical_date')
    return result

def digest(value): return functions.digest(value)

def protected():
    folder = Path(__file__).resolve().parent
    for name, expected in PINS.items():
        need(sha256((folder/name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)
    runtime.protected()

def types(state):
    context = 'book:' + digest(state['after']['context'])
    return {
        'units': {'kind': 'number', 'dimensions': {'unit': 1}, 'context': context},
        'cash': {'kind': 'number', 'dimensions': {state['after']['context']['currency']: 1}, 'context': context},
        'boolean': {'kind': 'boolean'}}

def availability(value, at):
    if value == 'unknown': return 'unknown_date'
    return 'available' if day(value) <= at else 'future_date'

def findings_shape(findings):
    closed(findings, runtime.partial.FINDINGS)
    for key, item in findings.items():
        need(type(item) is dict, 'finding_record:' + key)
        if item.get('status') == 'unknown':
            closed(item, ['status', 'reason']); text(item['reason'], 'finding_reason')
        else:
            closed(item, ['status', 'value', 'provenance'])
            need(item['status'] == 'known' and type(item['value']) is bool, 'finding_boolean')
            text(item['provenance'], 'finding_provenance')

def prepare(state, request):
    protected(); runtime.annual.invariant(state); runtime.annual.caller.bounded(request)
    closed(request, ['profile', 'id', 'expected_state_sha256', 'context', 'decision_date',
                     'scenario', 'model', 'bindings', 'output_map', 'event'])
    need(request['profile'] == PROFILE, 'profile'); text(request['id'], 'decision_id')
    need(request['expected_state_sha256'] == digest(state), 'stale_state')
    need(request['context'] == state['after']['context'], 'context_mismatch')
    at = day(request['decision_date']); financial = state['after']
    need(day(financial['date']) <= at < day(financial['period']['end_exclusive']), 'decision_chronology')
    closed(request['scenario'], ['kind', 'premise'])
    need(request['scenario']['kind'] == 'authored_closed_path', 'scenario_kind', 'unsupported')
    text(request['scenario']['premise'], 'closed_path_premise')
    event = request['event']
    closed(event, ['id', 'date', 'method', 'lot_id', 'findings'])
    text(event['id'], 'event_id'); text(event['lot_id'], 'lot_id')
    need(day(event['date']) == at, 'same_day_event_required', 'unsupported')
    need(event['method'] == runtime.partial.MODEL, 'selected_event_method', 'unsupported')
    need(event['lot_id'] in financial['lots'], 'missing_selected_lot')
    findings_shape(event['findings'])
    model = request['model']; closed(model, ['program', 'available_on', 'provenance'])
    text(model['provenance'], 'model_provenance')
    model_available = availability(model['available_on'], at)
    template = model['program']; compiled = functions.compile_program(template)
    need(len(template['inputs']) <= MAX_INPUTS, 'input_limit')
    need(all(item['value'] == 'unknown' for item in template['inputs'].values()), 'placeholder_inputs_required')
    mapping = request['output_map']; closed(mapping, ['execute', 'sold_units', 'proceeds'])
    need(all(type(value) is str for value in mapping.values()), 'output_names')
    need(len(set(mapping.values())) == 3 and set(mapping.values()) == set(template['outputs']), 'exact_output_mapping')
    type_map = types(state); base = functions.load_baseline()
    for key, typ in [('execute', type_map['boolean']), ('sold_units', type_map['units']), ('proceeds', type_map['cash'])]:
        base.compatible(compiled['analysis']['outputs'][mapping[key]], typ)
    bindings = request['bindings']
    need(type(bindings) is dict and set(bindings) == set(template['inputs']), 'exact_input_bindings')
    program = deepcopy(template); observations = {}
    for key, binding in bindings.items():
        need(type(binding) is dict, 'binding_record')
        typ = template['inputs'][key]['type']; kind = binding.get('kind')
        if kind == 'state_lot_units':
            closed(binding, ['kind', 'lot_id'])
            need(binding['lot_id'] == event['lot_id'], 'selected_lot_binding')
            base.compatible(typ, type_map['units'])
            value = financial['lots'][event['lot_id']]['units']; status = 'current_state'
        elif kind == 'state_cash':
            closed(binding, ['kind']); base.compatible(typ, type_map['cash'])
            value = financial['balances']['cash']; status = 'current_state'
        elif kind == 'scenario':
            closed(binding, ['kind', 'type', 'value', 'available_on', 'provenance'])
            base.compatible(typ, binding['type']); base.typed_value(typ, binding['value'])
            text(binding['provenance'], 'input_provenance')
            status = availability(binding['available_on'], at)
            value = binding['value'] if status == 'available' else 'unknown'
        else: raise Refused('unsupported', 'binding_kind')
        base.typed_value(typ, value); program['inputs'][key]['value'] = value
        observations[key] = {'binding': deepcopy(binding), 'visibility': status, 'value_used': value}
    return program, compiled, observations, model_available

def failure(exc):
    status = exc.status if hasattr(exc, 'status') else 'invalid'
    need(status in ['invalid', 'unresolved', 'unsupported', 'funding_failure'], 'unexpected_refusal_status')
    return {'profile': PROFILE, **FLAGS, 'status': status,
            'reason': getattr(exc, 'reason', type(exc).__name__ + ':' + str(exc).splitlines()[0][:300])}

def propose(state, request):
    try:
        program, _, observations, model_available = prepare(state, request)
        result = {'profile': PROFILE, **FLAGS, 'request_sha256': digest(request), 'state_sha256': digest(state),
                  'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                  'dependency_sha256': deepcopy(PINS), 'input_observations': observations,
                  'model_visibility': model_available, 'decision_date': request['decision_date']}
        if model_available != 'available':
            return {**result, 'status': 'unresolved', 'reason': 'model_not_available'}
        compiled = functions.compile_program(program); base = functions.load_baseline()
        mapping = request['output_map']; guard_graph = deepcopy(compiled['graph'])
        guard_graph['outputs'] = {'execute': compiled['graph']['outputs'][mapping['execute']]}
        guard = base.evaluate(guard_graph); result.update(program_sha256=digest(program), compilation=compiled, guard=guard)
        if guard['status'] != 'evaluated':
            return {**result, 'status': guard['status'], 'reason': 'decision_guard_' + guard['status']}
        if guard['outputs']['execute']['value'] is False:
            return {**result, 'status': 'no_action', 'reason': 'guard_false'}
        evaluation = base.evaluate(compiled['graph']); result['evaluation'] = evaluation
        if evaluation['status'] != 'evaluated':
            return {**result, 'status': evaluation['status'], 'reason': 'event_values_' + evaluation['status']}
        event = deepcopy(request['event']); event['profile'] = runtime.partial.PROFILE
        event['sold_units'] = evaluation['outputs'][mapping['sold_units']]['value']
        event['proceeds'] = evaluation['outputs'][mapping['proceeds']]['value']
        operation = {'kind': 'partial_inventory_sale', 'event': event}
        return {**result, 'status': 'proposed', 'operation': operation, 'operation_sha256': digest(operation)}
    except Exception as exc: return failure(exc)

def apply(state, request, proposed):
    try:
        expected = propose(state, request)
        need(expected == proposed, 'proposal_recomputation_mismatch')
        if expected['status'] == 'no_action':
            return {'profile': PROFILE, **FLAGS, 'status': 'no_action', 'after': deepcopy(state), 'decision': expected}
        if expected['status'] != 'proposed': return expected
        result = runtime.transition(state, expected['operation'])
        return {'profile': PROFILE, **FLAGS, 'status': 'applied_provisional',
                'after': result['after'], 'transition': result, 'decision': expected}
    except Exception as exc: return failure(exc)

def run_sequence(state, requests):
    try:
        protected(); runtime.annual.invariant(state)
        need(type(requests) is list and len(requests) <= MAX_DECISIONS, 'decision_sequence_limit')
        current = deepcopy(state); trace = []; stop = None; seen = set(); cursor = day(state['after']['date'])
        for index, request in enumerate(requests):
            try:
                need(type(request) is dict, 'decision_record')
                text(request.get('id'), 'decision_id'); need(request['id'] not in seen, 'duplicate_decision')
                when = day(request['decision_date']); need(when >= cursor, 'backward_decision_date')
                proposed = propose(current, request); outcome = apply(current, request, proposed)
            except Exception as exc: outcome = failure(exc)
            if outcome['status'] not in ['applied_provisional', 'no_action']:
                stop = {'index': index, 'outcome': outcome}; break
            seen.add(request['id']); cursor = when; current = outcome['after']
            trace.append({'request': deepcopy(request), 'result': outcome})
        report = runtime.annual.root.carry.statements(current['opening'], current['after'], current['account_classes'])
        report.update(scope='Recorded conditional state after an authored decision prefix; not a complete fiscal event population',
                      unresolved=deepcopy(runtime.annual.UNRESOLVED))
        return {'profile': PROFILE, **FLAGS, 'status': 'stopped_provisional' if stop else 'complete_decision_sequence',
                'after': current, 'trace': trace, 'stop': stop, 'decision_cursor': cursor.isoformat(),
                'remaining_requests': deepcopy(requests[len(trace):]), 'recorded_statements': report,
                'fiscal_complete': False}
    except Exception as exc: return failure(exc)
