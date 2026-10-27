"""Bounded documentary link; reuse existing binding and requirement semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import method_requirements_v1 as core
import method_input_binding_v2 as binder

ATTEMPT = ROOT / 'data/accounting-master/extended-method-exchanges-20261015/bank-assessment/attempt-03'
OP = 'bank.regulatory.assess@1'
PROFILE = 'NativeRequirementLink/1'
CAPABILITY = 'selected-date-requirements'
RESIDUALS = [
    'Native schema and complete semantic input closure',
    'Last-day condition, scenario window and evidence timing',
    'Accounting and regulatory source applicability and eligibility',
    'Current view and accounting head at invocation time',
    'Environment, resource budgets and runtime capability',
    'Request identity, replay and publication/acknowledgement semantics']
BOUNDARY = {'executed': False, 'source_admission': False,
            'accounting_admission': False, 'method_eligible': False}
FIELDS = {
    'assessment_date': ('basis', '/body/assessment_date'),
    'period_start': ('basis', '/body/period_start'),
    'period_end': ('basis', '/body/period_end_exclusive'),
    'state_date': ('state', '/body/as_of_date')}


def hash_bytes(raw):
    return sha256(raw).hexdigest()


def native_digest(record):
    return hash_bytes(('accdsl.portable.v1/' + record['schema']).encode() +
                      bytes([0]) + core.canonical(record))


class Bridge:
    def __init__(self):
        self.packet = json.loads((ATTEMPT / 'portable-exchanges.json').read_bytes())
        self.registry = self.packet['record_registry']
        self.exchanges = {e['id']: e for e in self.packet['exchanges']}
        good = self.exchanges['capital.final']
        request = self.record(good['request_ref'])['body']
        self.profile_ref = self.packet['profile_ref']
        self.signature_ref = request['signature_ref']

    def record(self, ref):
        core.closed(ref, ['kind', 'schema', 'digest'], 'native_reference')
        if ref['digest'] not in self.registry:
            raise binder.prior.Unavailable('native_record_unavailable')
        record = self.registry[ref['digest']]
        core.need(record['kind'] == ref['kind'] and record['schema'] == ref['schema'],
                  'native_reference_type')
        core.need(native_digest(record) == ref['digest'], 'native_record_digest')
        return record

    def selected(self, exchange_id):
        e = self.exchanges[exchange_id]
        request = self.record(e['request_ref'])['body']
        core.need(request['operation'] == OP, 'operation_selection')
        basis_ref = request['arguments']['value']['basis_ref']
        basis = self.record(basis_ref)
        state_ref = basis['body']['state_ref']
        state = self.record(state_ref)
        context_ref = basis['body']['context_ref']
        context = self.record(context_ref)['body']
        return e, request, basis_ref, state_ref, context_ref, context, basis, state

    def make(self, exchange_id, version=1):
        e, request, br, sr, cr, context, basis, state = self.selected(exchange_id)
        types = {'kind': 'date', 'context': {**context,
                 'native_context_ref': core.canonical(cr).decode()}}
        records = {'basis': basis, 'state': state}
        raws = {name: core.canonical(record) for name, record in records.items()}
        ref = lambda key: {'op': 'ref', 'id': key}
        relation = lambda op, a, b: {'op': op, 'left': ref(a), 'right': ref(b)}
        predicates = [('nonempty-period', 'lt', 'period_start', 'period_end'),
                      ('assessment-in-period-start', 'le', 'period_start', 'assessment_date'),
                      ('assessment-in-period-end', 'lt', 'assessment_date', 'period_end'),
                      ('state-date-agrees', 'eq', 'assessment_date', 'state_date')]
        profile = 'MethodRequirements/' + str(version)
        definition = {'profile': profile, 'method_id': 'bank.regulatory.selected-dates',
                      'version': '1', 'inputs': {}, 'requirements': [],
                      'capabilities': [CAPABILITY], 'residual_prerequisites': RESIDUALS.copy()}
        schemas, refs, bindings = {}, {}, []
        for name in records:
            shape = {'profile': binder.SCHEMA, 'requirements_profile': profile,
                     'schema_id': 'native-selected-dates.' + name, 'fields': {}}
            for key, (origin, pointer) in FIELDS.items():
                if origin != name:
                    continue
                definition['inputs'][key] = {
                    'type': deepcopy(types), 'role': 'state',
                    'source_ref': 'sha256:' + hash_bytes(raws[name]) + '#' + pointer}
                shape['fields'][pointer] = {'type': deepcopy(types), 'role': 'state',
                                           'encoding': 'scalar', 'missing': 'unresolved'}
                bindings.append({'input': key, 'record': name, 'pointer': pointer})
            sk = core.digest(shape)
            schemas[sk] = shape
            refs[name] = {'raw_sha256': hash_bytes(raws[name]), 'schema_digest': sk}
        for key, op, a, b in predicates:
            requirement = {'id': key, 'predicate': relation(op, a, b),
                           'requires': sorted([a, b]), 'admission_refs': [],
                           'on_false': 'invalid', 'on_unknown': 'unresolved'}
            if version == 3:
                requirement.update(guard={'op': 'const', 'type': core.BOOL, 'value': True},
                                   guard_requires=[])
            definition['requirements'].append(requirement)
        if version == 3:
            definition['required_known'] = sorted(FIELDS)
        dk = core.digest(definition)
        plan = {'profile': binder.PROFILE, 'manifest_digest': dk,
                'records': refs, 'bindings': bindings}
        packet = {'plan': plan, 'manifests': {dk: definition}, 'schemas': schemas,
                  'blobs': {hash_bytes(raw): raw for raw in raws.values()},
                  'available_capabilities': [CAPABILITY]}
        link = {'profile': PROFILE, 'exchange_id': exchange_id,
                'request_ref': deepcopy(e['request_ref']),
                'submission_ref': deepcopy(e['submission_ref']),
                'profile_ref': deepcopy(request['profile_ref']),
                'signature_ref': deepcopy(request['signature_ref']),
                'basis_ref': br, 'context_ref': cr,
                'input_sources': {'basis': br, 'state': sr},
                'manifest_digest': dk, 'binding_plan_digest': core.digest(plan)}
        return link, packet

    def assess(self, link, packet):
        binding = binder.assess_bound(**packet)
        result = {**BOUNDARY, 'binding': binding, 'residual_prerequisites': RESIDUALS.copy()}
        try:
            core.closed(link, ['profile', 'exchange_id', 'request_ref', 'submission_ref',
                        'profile_ref', 'signature_ref', 'basis_ref', 'context_ref',
                        'input_sources', 'manifest_digest', 'binding_plan_digest'], 'native_link')
            core.need(link['profile'] == PROFILE, 'link_profile')
            core.need(link['exchange_id'] in self.exchanges, 'exchange_selection')
            e, rq, br, sr, cr, context, basis, state = self.selected(link['exchange_id'])
            for field in ['request_ref', 'submission_ref']:
                core.need(link[field] == e[field], 'exchange_' + field)
            core.need(link['profile_ref'] == rq['profile_ref'] == self.profile_ref, 'profile_binding')
            core.need(link['signature_ref'] == rq['signature_ref'] == self.signature_ref, 'signature_binding')
            sig = self.record(link['signature_ref'])['body']
            core.need(sig == {'operation': OP, 'profile_ref': self.profile_ref,
                      'arguments_definition': 'Arguments.' + OP,
                      'payload_kinds': ['RegulatoryAssessment'], 'effects': 'read'}, 'signature_semantics')
            core.need(rq['arguments']['tag'] == OP, 'argument_tag')
            core.need(link['basis_ref'] == br and link['context_ref'] == cr, 'basis_context_binding')
            core.need(state['body']['context_ref'] == cr, 'state_context_binding')
            core.need(link['input_sources'] == {'basis': br, 'state': sr}, 'input_sources_binding')
            sub = self.record(e['submission_ref'])['body']['blob_ref']
            meta = self.packet['blobs'][sub['digest']]
            path = (ROOT / meta['path']).resolve()
            core.need(path.is_relative_to(ROOT), 'submission_path')
            raw = path.read_bytes()
            core.need(hash_bytes(raw) == sub['digest'] and len(raw) == sub['byte_length'] == meta['byte_length'], 'submission_bytes_digest')
            core.need(raw == core.canonical(self.record(e['request_ref'])), 'submission_bytes_binding')
            plan = packet['plan']
            core.need(link['binding_plan_digest'] == core.digest(plan), 'binding_plan_identity')
            core.need(link['manifest_digest'] == plan['manifest_digest'], 'manifest_link')
            if binding['status'] == 'unsupported':
                return {**result, 'status': 'unsupported', 'reason': binding['reason']}
            definition = packet['manifests'][plan['manifest_digest']]
            core.need(definition['profile'] in ['MethodRequirements/1', 'MethodRequirements/2',
                      'MethodRequirements/3'], 'requirements_version')
            _, expected = self.make(link['exchange_id'], int(definition['profile'][-1]))
            core.need(definition == expected['manifests'][expected['plan']['manifest_digest']],
                      'selected_definition_binding')
            for name, record in [('basis', basis), ('state', state)]:
                core.need(plan['records'][name]['raw_sha256'] == hash_bytes(core.canonical(record)), 'input_raw_binding')
            core.need(binding['status'] == 'bound', 'input_binding_' + binding['status'])
            expected_context = {**context, 'native_context_ref': core.canonical(cr).decode()}
            core.need(set(binding['lineage']) == set(FIELDS), 'selected_field_set')
            for key, (name, pointer) in FIELDS.items():
                line = binding['lineage'][key]
                core.need((line['record'], line['pointer'], line['role'], line['encoding']) ==
                          (name, pointer, 'state', 'scalar'), 'selected_field_mapping')
                core.need(line['type'] == {'kind': 'date', 'context': expected_context}, 'native_field_context')
            result.update(status='linked_selected_requirements',
                          selected_status=binding['assessment']['status'],
                          native_request_digest=e['request_ref']['digest'],
                          native_submission_sha256=sub['digest'])
        except binder.prior.Unavailable as exc:
            result.update(status='unsupported', reason=str(exc))
        except (ValueError, TypeError, KeyError, OSError) as exc:
            result.update(status='invalid', reason=str(exc)[:250])
        return result
