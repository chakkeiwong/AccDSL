"""Map a rechecked selected history into an explicitly conditional opening."""
from copy import deepcopy
from datetime import timedelta
from hashlib import sha256
from pathlib import Path

import typed_history_measurement_attachment_v1 as attachment
import company_memory_types_v1 as memory
import company_book_reports_v1 as reports

engine = memory.engine
core = engine.core
PROFILE = 'ConditionalCompanyOpening/1'
FLAGS = {**reports.FLAGS, 'executed': False, 'execution_clearance': False, 'family_complete': False}
PINS = {
    'typed_history_measurement_attachment_v1.py': 'e510add72b6b0fe355f9b22c9f73f5d0451146312a66b5aad6791c60bd81abcd',
    'typed_affine_history_v1.py': '78b87e283986100744c617d767409941eceb27a1a76acebec8c24e5817a31d42',
    'company_memory_types_v1.py': '58b22d43b895c246fe76b52d5dddb4428ad356a2502e5076a5337f4540083d89',
    'company_book_reports_v1.py': '7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100'}


def protected():
    memory.protected()
    for name, expected in PINS.items():
        core.need(sha256((Path(__file__).parent / name).read_bytes()).hexdigest() == expected, 'dependency_hash:' + name)


def map_opening(request):
    try:
        protected(); engine.memory.bounded(request)
        engine.closed(request, ['profile', 'attachment', 'budget', 'witness', 'mapping'])
        core.need(request['profile'] == PROFILE, 'profile')
        definition, budget, witness, mapping = [request[k] for k in ['attachment', 'budget', 'witness', 'mapping']]
        problem, _, meta = attachment.prepare(definition, budget)
        common = {'profile': PROFILE, **FLAGS, 'request_sha256': core.digest(request),
            'attachment_sha256': core.digest(definition), 'witness_sha256': core.digest(witness),
            'missing_premises': deepcopy(meta['missing_premises']), 'target_obligations': deepcopy(meta['target_obligations']),
            'source_context': deepcopy(definition['history']['value_type']['context']),
            'exclusions': deepcopy(definition['history']['scope']['exclusions'])}
        if problem is None: return {**common, 'status': 'unresolved', 'reason': 'missing_attachment_premises'}
        replay = attachment.replay_witness(definition, budget, witness)
        history = definition['history']; latest = history['dates'][-1]
        engine.closed(mapping, ['source_date', 'context', 'period', 'accounts', 'memory', 'cash_account',
                                'context_premise', 'boundary_premise'])
        engine.text(mapping['context_premise'], 'context_premise'); engine.text(mapping['boundary_premise'], 'boundary_premise')
        core.need(mapping['source_date'] == latest, 'final_declared_snapshot_required')
        core.need(mapping['period']['start'] == (core.scalar(latest, 'date') + timedelta(days=1)).isoformat(), 'next_day_opening_required')
        source_type = history['value_type']; context = mapping['context']
        engine.closed(context, ['entity', 'book', 'currency', 'case_id', 'mode'])
        core.need(context['mode'] == 'synthetic', 'conditional_synthetic_context')
        core.need(all(context[k] == source_type['context'].get(k) for k in ['entity', 'book']), 'source_entity_book_mismatch')
        core.need(source_type['dimensions'] == {'currency:' + context['currency']: 1} and source_type['scale'] == '1/1', 'money_units_mismatch')
        snapshot = replay['history']['snapshots'][latest]
        core.need(type(mapping['accounts']) is dict and set(mapping['accounts']) == set(snapshot['accounts']), 'complete_account_mapping')
        core.need(type(mapping['memory']) is dict and set(mapping['memory']) == set(snapshot['memory']), 'complete_memory_mapping')
        accounts, balances = {}, {}
        for source, target in mapping['accounts'].items():
            engine.closed(target, ['id', 'classification', 'provenance']); engine.text(target['id'], 'target_account')
            engine.text(target['provenance'], 'classification_provenance')
            core.need(target['id'] not in accounts, 'duplicate_target_account')
            accounts[target['id']] = {'classification': target['classification']}; balances[target['id']] = snapshot['accounts'][source]
        value = {}; root = {'node': 'record', 'fields': {}}
        book = {'profile': engine.BOOK, 'context': deepcopy(context), 'period': deepcopy(mapping['period']),
            'date': mapping['period']['start'], 'accounts': accounts, 'balances': balances,
            'cash_account': mapping['cash_account'], 'memory': value,
            'seen': [row['event_id'] for row in replay['history']['events']], 'flows': []}
        paths = []
        for source, target in mapping['memory'].items():
            engine.closed(target, ['path', 'provenance']); engine.text(target['provenance'], 'memory_mapping_provenance')
            path = target['path']; core.need(type(path) is list and 0 < len(path) <= core.MAX_DEPTH, 'memory_path')
            for token in path: engine.text(token, 'memory_path_token')
            for prior in paths: core.need(path[:len(prior)] != prior and prior[:len(path)] != path, 'overlapping_memory_paths')
            paths.append(path); obj, node = value, root
            for token in path[:-1]:
                obj = obj.setdefault(token, {}); node = node['fields'].setdefault(token, {'node': 'record', 'fields': {}})
            typ = deepcopy(replay['history']['field_types']['memory'][source]); typ['context'] = engine.type_context(book)
            obj[path[-1]] = snapshot['memory'][source]; node['fields'][path[-1]] = {'node': 'scalar', 'type': typ}
        memory_definition = {'profile': memory.PROFILE, 'root': root}
        typed = memory.derive(memory_definition, value, book)
        core.need(typed['status'] == 'typed', 'mapped_memory:' + typed.get('reason', ''))
        book.update(memory_types=typed['memory_types'], memory_schema=typed['schema_sha256'])
        schemas = {typed['schema_sha256']: typed['schema']}; engine.validate_book(book, schemas)
        reporting = {'profile': reports.MAP, 'context': deepcopy(context), 'lines': [
            {'id': source, 'label': source, 'classification': target['classification'], 'accounts': [target['id']]}
            for source, target in mapping['accounts'].items()]}
        report_request = reports.request(book, book, schemas, reporting)
        report = reports.report(report_request)
        core.need(report['status'] == 'reported', 'opening_report:' + report.get('reason', ''))
        provenance = {'attachment_definition': deepcopy(definition), 'selected_witness': deepcopy(witness),
            'selection_scope': 'One conditional history; other compatible histories remain in the unchanged parent definition',
            'source_snapshot_date': latest, 'source_snapshot': deepcopy(snapshot),
            'mapping': deepcopy(mapping), 'premises': deepcopy(meta['premises']),
            'target_obligations': deepcopy(meta['target_obligations']), 'missing_premises': deepcopy(meta['missing_premises']),
            'exclusions': deepcopy(history['scope']['exclusions']),
            'operational_preconditions_checked': replay['history']['operational_preconditions_checked'],
            'investor_information_cutoff_checked': False}
        return {**common, 'status': 'candidate_opening_with_unresolved_obligations' if meta['target_obligations'] else 'conditional_opening',
            'opening': book, 'memory_definition': memory_definition, 'schemas': schemas, 'report_mapping': reporting,
            'opening_report': report, 'provenance': provenance, 'replay': replay,
            'opening_sha256': core.digest(book), 'implementation_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': deepcopy(PINS)}
    except Exception as exc:
        return {'profile': PROFILE, **FLAGS, 'status': 'invalid', 'reason': str(exc)[:350]}


def verify(request, result):
    try: return core.canonical(map_opening(request)) == core.canonical(result)
    except Exception: return False
