"""Bounded registry composition; every entry retains the v1 structural checks."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import company_method_clock_v1 as prior

transition = prior.transition
core = prior.core
REGISTRY = 'CompanyMethodRegistry/2'
PROFILE = 'CompanyMethodCall/2'
MAX_ENTRIES = prior.MAX_ENTRIES
PRIOR_SHA256 = '39d9499cf9a36fa14eb3ec0d4d68f23e7a47c137e0494a4d83c2101e317b2f8d'
TRANSITION_SHA256 = prior.TRANSITION_SHA256
FLAGS = prior.FLAGS
digest = core.digest
Unsupported = prior.Unsupported
event_declarations = prior.event_declarations
event_for = prior.event_for
transition_request = prior.transition_request


def protected():
    core.need(sha256(Path(prior.__file__).read_bytes()).hexdigest() == PRIOR_SHA256,
              'method_v1_dependency_hash')
    prior.protected()


def bounded_registry(registry):
    core.need(len(core.canonical(registry)) <= core.MAX_BYTES, 'registry_size_limit')
    transition.closed(registry, ['profile', 'context', 'entries'])
    core.need(registry['profile'] == REGISTRY, 'registry_profile')
    transition.memory.bounded(registry['context'])
    entries = registry['entries']
    core.need(type(entries) is dict and 0 < len(entries) <= MAX_ENTRIES, 'registry_entry_limit')
    for name, entry in entries.items():
        transition.text(name, 'method_key')
        transition.memory.bounded(entry)


def materialize(book, call):
    protected()
    core.need(len(core.canonical(call)) <= core.MAX_BYTES, 'call_size_limit')
    transition.closed(call, ['profile', 'expected_state_sha256', 'expected_registry_sha256',
                            'registry', 'method_key', 'event'])
    transition.memory.bounded({k: v for k, v in call.items() if k != 'registry'})
    core.need(call['profile'] == PROFILE, 'call_profile')
    core.need(call['expected_state_sha256'] == digest(book), 'stale_state')
    registry = call['registry']
    bounded_registry(registry)
    core.need(call['expected_registry_sha256'] == digest(registry), 'registry_digest')
    core.need(registry['context'] == book['context'], 'registry_context')
    selected = call['method_key']
    transition.text(selected, 'selected_method')
    event = call['event']
    transition.closed(event, ['id', 'date', 'inputs'])
    transition.text(event['id'], 'event_id')
    core.scalar(event['date'], 'date')
    core.need(type(event['inputs']) is dict, 'event_inputs')
    # The unchanged materializer checks all fields, types, schemas and obligations
    # in each single-entry registry. Economic predicates remain for actual execution.
    for name, entry in registry['entries'].items():
        core.need(type(entry) is dict and type(entry.get('event_inputs')) is dict,
                  'entry_event_inputs')
        one = {'profile': prior.REGISTRY, 'context': deepcopy(registry['context']),
               'entries': {name: deepcopy(entry)}}
        probe = {'id': event['id'], 'date': event['date'], 'inputs': {
            k: {'type': deepcopy(t), 'value': {'status': 'unknown', 'reason': 'static_registry_check'},
                'provenance': 'Unknown placeholder for structural validation only'}
            for k, t in entry['event_inputs'].items()}}
        prior.materialize(book, {'profile': prior.PROFILE, 'expected_state_sha256': digest(book),
            'expected_registry_sha256': digest(one), 'registry': one, 'method_key': name, 'event': probe})
    if selected not in registry['entries']:
        raise Unsupported('unregistered_method:' + selected)
    one = {'profile': prior.REGISTRY, 'context': deepcopy(registry['context']),
           'entries': {selected: deepcopy(registry['entries'][selected])}}
    return prior.materialize(book, {'profile': prior.PROFILE, 'expected_state_sha256': digest(book),
        'expected_registry_sha256': digest(one), 'registry': one, 'method_key': selected,
        'event': deepcopy(event)})


def failure(exc):
    return {'profile': PROFILE, **FLAGS,
            'status': 'unsupported' if isinstance(exc, Unsupported) else 'invalid',
            'reason': str(exc)[:300] or type(exc).__name__}


def propose(book, call):
    try:
        request = materialize(book, call)
        result = transition.propose(book, request)
        return {'profile': PROFILE, **FLAGS, 'status': result['status'], 'call_sha256': digest(call),
                'before_sha256': digest(book), 'registry_sha256': digest(call['registry']),
                'method_key': call['method_key'], 'materialized_request': request, 'transition': result,
                'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
                'transition_sha256': TRANSITION_SHA256, 'materializer_v1_sha256': PRIOR_SHA256}
    except Exception as exc:
        return failure(exc)


def apply(book, call, proposal):
    try:
        transition.memory.bounded(proposal)
        expected = propose(book, call)
        core.need(core.canonical(expected) == core.canonical(proposal), 'proposal_recomputation_mismatch')
        if expected['status'] != 'proposed':
            return expected
        result = transition.apply(book, expected['materialized_request'], expected['transition'])
        return {**deepcopy(expected), 'status': result['status'], 'transition': result}
    except Exception as exc:
        return failure(exc)
