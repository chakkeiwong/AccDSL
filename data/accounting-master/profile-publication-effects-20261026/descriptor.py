"""Read-only, exact-lock description of retained documentary world changes."""
from copy import deepcopy
from hashlib import sha256
import json


class Refusal(ValueError):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def refs(value):
    if isinstance(value, dict):
        if set(value) == {'kind', 'schema', 'digest'}:
            yield value
        else:
            for child in value.values():
                yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)


CONFIG = {
    'insurance': {'identity': 'client_id', 'index': 'decisions',
        'fields': {'heads', 'current_view_ref', 'journals', 'decisions', 'published_records', 'unrelated_heads'},
        'mutable': {'heads', 'journals', 'decisions', 'published_records'},
        'flag_meaning': 'new_result_or_report_publication'},
    'group': {'identity': 'workspace_key', 'index': 'decisions',
        'fields': {'group_heads', 'legal_heads', 'unrelated_heads', 'journals', 'decisions', 'published_records', 'current_view_ref'},
        'mutable': {'group_heads', 'journals', 'decisions', 'published_records'},
        'flag_meaning': 'new_component_or_report_publication'},
    'bank-assessment': {'identity': 'workspace_key', 'index': 'query_index',
        'fields': {'accounting_heads', 'journals', 'query_index', 'published_records', 'current_view_ref', 'unrelated_owners'},
        'mutable': {'query_index', 'published_records'}, 'flag_meaning': 'new_query_publication'},
    'insurance-assessment': {'identity': 'client_id', 'index': 'query_index',
        'fields': {'accounting_heads', 'balances', 'journals', 'unrelated_owners', 'current_view_ref', 'query_index', 'published_records'},
        'mutable': {'query_index', 'published_records'}, 'flag_meaning': 'financial_commit'},
}


class Descriptor:
    def __init__(self, packet, lock):
        self.packet = packet
        self.lock = lock
        self.name = lock['name']
        need(self.name in CONFIG, 'unsupported_profile')
        self.config = CONFIG[self.name]
        self.registry = packet['record_registry']
        self.checked = set()
        self.profile_ref = packet.get('profile_ref') or packet['aliases']['profile']
        need(self.profile_ref == lock['profile_ref'], 'profile_lock_mismatch')
        profile = self.body(self.profile_ref)
        need(profile['profile_id'] == lock['profile_id'], 'profile_id_mismatch')
        self.operations = profile.get('operations') or [profile['operation']]
        self.prefix = self.profile_ref['schema'].removesuffix('profile.v1')

    def body(self, ref):
        need(isinstance(ref, dict) and set(ref) == {'kind', 'schema', 'digest'}, 'invalid_reference')
        record = self.registry.get(ref['digest'])
        need(isinstance(record, dict), 'missing_record')
        need(record.get('kind') == ref['kind'] and record.get('schema') == ref['schema'], 'reference_binding')
        if ref['digest'] not in self.checked:
            need(set(record) == {'kind', 'schema', 'key', 'revision', 'body', 'dependencies'}, 'record_shape')
            digest = sha256(('accdsl.portable.v1/' + record['schema']).encode() + b'\x00' + canonical(record)).hexdigest()
            need(digest == ref['digest'], 'record_digest_mismatch')
            dependencies = sorted({canonical(r): r for r in refs(record['body'])}.values(), key=canonical)
            need(record['dependencies'] == dependencies, 'dependency_binding')
            self.checked.add(ref['digest'])
        return record['body']

    def closure(self, roots):
        found, active = set(), set()
        def visit(ref):
            digest = ref['digest']
            need(digest not in active, 'reference_cycle')
            if digest in found:
                return
            self.body(ref)
            active.add(digest)
            for child in self.registry[digest]['dependencies']:
                visit(child)
            active.remove(digest)
            found.add(digest)
        for ref in roots:
            visit(ref)
        return sorted(found)

    def pair(self, request):
        pair = [request[self.config['identity']], request['request_id']]
        need(all(isinstance(s, str) and s for s in pair), 'invalid_identity')
        return pair

    def legacy_key(self, request):
        pair = self.pair(request)
        return '/'.join(pair) if self.name == 'insurance' else canonical(pair).decode()

    def check_submission(self, submission_ref, request_ref):
        need(submission_ref['kind'] == 'Submission' and
             submission_ref['schema'] == self.prefix + 'submission.v1', 'unsupported_submission_schema')
        submission = self.body(submission_ref)
        request = self.body(request_ref)
        if self.name in {'insurance', 'insurance-assessment'}:
            need(submission.get('request_ref') == request_ref, 'submission_request')
        blob = submission.get('blob_ref', submission.get('wire_blob'))
        wire = canonical(request if self.name == 'insurance' else self.registry[request_ref['digest']])
        need(isinstance(blob, dict) and blob.get('kind') == 'blob' and blob.get('algorithm') == 'sha256', 'submission_blob_shape')
        need(blob['digest'] == sha256(wire).hexdigest() and blob['byte_length'] == len(wire), 'submission_bytes_binding')
        if self.name in {'group', 'bank-assessment'}:
            need(submission['decoder_ref'] == self.packet['aliases']['decoder'], 'decoder_binding')
            self.body(submission['decoder_ref'])

    def transport(self, observation_ref, request_ref, submission_ref):
        observation = self.body(observation_ref)
        request = self.body(request_ref)
        need(observation_ref['kind'] == 'TransportObservation', 'not_transport_observation')
        need(observation_ref['schema'] == self.prefix + 'transportobservation.v1', 'unsupported_response_schema')
        need(request_ref['schema'] == self.prefix + 'operationrequest.v1', 'unsupported_request_schema')
        need(request_ref['kind'] == 'OperationRequest' and request['operation'] in self.operations, 'unsupported_operation')
        self.check_submission(submission_ref, request_ref)
        need(request['profile_ref'] == self.profile_ref, 'request_profile')
        need(observation.get('submission_ref') == submission_ref, 'observation_submission')
        if 'request_ref' in observation:
            need(observation['request_ref'] == request_ref, 'observation_request')
        need(observation.get('commit_knowledge', observation.get('commit_observation')) == 'unknown', 'unknown_acknowledgement_required')
        need(observation.get('receipt_ref') is None, 'fabricated_transport_receipt')
        return {'schema': 'PublicationEffects/1', 'profile_ref': deepcopy(self.profile_ref),
            'source_packet': self.lock['packet'], 'source_packet_sha256': self.lock['files'][self.lock['packet']],
            'identity': self.pair(request), 'request_ref': deepcopy(request_ref),
            'submission_ref': deepcopy(submission_ref), 'response_ref': deepcopy(observation_ref),
            'evidence_mode': 'specification_example', 'execution_admission': False,
            'disposition': 'transport_unknown', 'publication_knowledge': 'unknown',
            'operation': request['operation'],
            'receipt_ref': None, 'effects': None,
            'native_flag': {'value': None, 'meaning': self.config['flag_meaning']}}

    def describe(self, exchange):
        request_ref, response_ref = exchange['request_ref'], exchange['response_ref']
        request, response = self.body(request_ref), self.body(response_ref)
        submission_ref = exchange['submission_ref']
        submission = self.body(submission_ref)
        need(request_ref['kind'] == 'OperationRequest' and request['profile_ref'] == self.profile_ref, 'request_profile')
        need(request_ref['schema'] == self.prefix + 'operationrequest.v1', 'unsupported_request_schema')
        need(submission_ref['schema'] == self.prefix + 'submission.v1', 'unsupported_submission_schema')
        need(request['operation'] in self.operations, 'unsupported_operation')
        self.check_submission(submission_ref, request_ref)
        if response_ref['kind'] == 'TransportObservation':
            return self.transport(response_ref, request_ref, submission_ref)
        need(response_ref['kind'] == 'OperationResult', 'unsupported_response')
        need(response_ref['schema'] == self.prefix + 'operationresult.v1', 'unsupported_response_schema')
        need(response['request_ref'] == request_ref and response['submission_ref'] == submission_ref, 'result_binding')
        if 'operation' in response:
            need(response['operation'] == request['operation'], 'result_operation')
        before, after = exchange['world_before'], exchange['world_after']
        need(set(before) == set(after) == self.config['fields'], 'world_shape')
        changed = {k for k in before if before[k] != after[k]}
        need(changed <= self.config['mutable'], 'unauthorized_world_change')
        disposition = response['disposition']
        need(disposition in {'completed', 'partial', 'replayed', 'rejected'}, 'unsupported_disposition')
        payload = response.get('payload') or {}
        if payload:
            need(payload['tag'] == request['operation'], 'payload_operation')
        flag = response.get('additional_commit', payload.get('additional_commit'))
        receipt_ref = response['receipt_ref']
        output_ref = response.get('output_ref')
        if 'payload' in response and payload:
            outputs = payload['result_refs']
            need(len(outputs) <= 1, 'unsupported_output_count')
            output_ref = outputs[0] if outputs else None
        key = self.legacy_key(request)
        index_name = self.config['index']
        index_before, index_after = before[index_name], after[index_name]

        if disposition == 'rejected':
            need(before == after, 'rejection_mutated_world')
            need(receipt_ref is None and output_ref is None, 'rejection_success_payload')
            need(flag is None if self.name == 'group' else flag is False, 'native_flag_mismatch')
        elif disposition == 'replayed':
            need(before == after and flag is False, 'replay_mutated_world')
            need(key in index_before, 'missing_replay_decision')
            prior = index_before[key]
            need(prior.get('request_ref', request_ref)['digest'] == request_ref['digest'] and
                 prior.get('request_digest', request_ref['digest']) == request_ref['digest'], 'replay_identity_conflict')
            old = self.body(prior['response_ref'])
            expected_replay = deepcopy(old)
            expected_replay['disposition'] = 'replayed'
            if self.name in {'group', 'bank-assessment'}:
                expected_replay['payload']['additional_commit'] = False
            else:
                expected_replay['additional_commit'] = False
            need(response == expected_replay, 'changed_replay_metadata')
            need(receipt_ref == prior['receipt_ref'] and output_ref == prior['output_ref'], 'changed_replay_result')
            need(set(self.closure([prior['response_ref']])) <= set(before['published_records']), 'replay_missing_publication')
        else:
            need(key not in index_before, 'publication_identity_exists')
            need(set(index_after) == set(index_before) | {key}, 'index_delta')
            need(all(index_after[k] == v for k, v in index_before.items()), 'overwritten_decision')
            expected = {'response_ref': response_ref, 'output_ref': output_ref, 'receipt_ref': receipt_ref}
            expected['request_ref' if self.name == 'insurance' else 'request_digest'] = request_ref if self.name == 'insurance' else request_ref['digest']
            need(index_after[key] == expected, 'decision_binding')
            need(flag is (self.name != 'insurance-assessment'), 'native_flag_mismatch')
            old_records, new_records = before['published_records'], after['published_records']
            need(old_records == sorted(set(old_records)) and new_records == sorted(set(new_records)), 'publication_set')
            need(new_records == sorted(set(old_records) | set(self.closure([response_ref]))), 'publication_closure')
            self.check_publication(request_ref, request, response, output_ref, receipt_ref, before, after)

        if receipt_ref is not None:
            receipt = self.body(receipt_ref)
            need(receipt['request_ref'] == request_ref, 'receipt_request')
            bound_output = receipt.get('output_ref', receipt.get('result_ref', receipt.get('report_ref')))
            need(bound_output == output_ref, 'receipt_output')
        if 'commit_observation' in response:
            need(response['commit_observation'] == ('not_committed' if disposition == 'rejected' else 'committed'), 'native_commit_observation')
        old_journals = before['journals']
        need(after['journals'][:len(old_journals)] == old_journals, 'journal_history_changed')
        journal_additions = after['journals'][len(old_journals):]
        head_changes = {}
        for field in ('heads', 'group_heads', 'accounting_heads', 'legal_heads'):
            if field in changed:
                head_changes[field] = {'before': deepcopy(before[field]), 'after': deepcopy(after[field])}
        effects = {'record_publication': disposition in {'completed', 'partial'},
            'query_publication': disposition in {'completed', 'partial'} and
                (self.name.endswith('assessment') or request['operation'].endswith('report@1')),
            'component_head_changes': ({role: {'before': deepcopy(before['heads'][role]), 'after': deepcopy(after['heads'][role])}
                for role in ('issued', 'replacement', 'held') if before['heads'][role] != after['heads'][role]}
                if self.name == 'insurance' else head_changes),
            'legal_account_head_changed': self.name == 'insurance' and before['heads']['accounts'] != after['heads']['accounts'],
            'legal_account_head_changes': ({'accounts': {'before': deepcopy(before['heads']['accounts']), 'after': deepcopy(after['heads']['accounts'])}}
                if self.name == 'insurance' and before['heads']['accounts'] != after['heads']['accounts'] else {}),
            'journal_scope': 'group_worksheet' if self.name == 'group' else 'insurance_legal_book' if self.name == 'insurance' else 'none',
            'journal_additions': deepcopy(journal_additions),
            'world_changes': {k: {'before': deepcopy(before[k]), 'after': deepcopy(after[k])} for k in sorted(changed)},
            'unchanged_world_fields': sorted(set(before) - changed)}
        return {'schema': 'PublicationEffects/1', 'profile_ref': deepcopy(self.profile_ref),
            'source_packet': self.lock['packet'], 'source_packet_sha256': self.lock['files'][self.lock['packet']],
            'identity': self.pair(request), 'request_ref': deepcopy(request_ref),
            'submission_ref': deepcopy(submission_ref), 'response_ref': deepcopy(response_ref),
            'receipt_ref': deepcopy(receipt_ref), 'output_ref': deepcopy(output_ref),
            'operation': request['operation'], 'disposition': disposition,
            'publication_knowledge': 'known', 'evidence_mode': 'specification_example',
            'execution_admission': False, 'native_flag': {'value': flag, 'meaning': self.config['flag_meaning']},
            'native_metadata': {k: deepcopy(response[k]) for k in ('diagnostics', 'statuses', 'coverage', 'unresolved', 'continuation_ref', 'commit_observation', 'accounting_effect') if k in response},
            'world_before_sha256': sha256(canonical(before)).hexdigest(),
            'world_after_sha256': sha256(canonical(after)).hexdigest(), 'effects': effects}

    def check_publication(self, request_ref, request, response, output_ref, receipt_ref, before, after):
        need(output_ref is not None and receipt_ref is not None, 'missing_publication_receipt')
        output, receipt = self.body(output_ref), self.body(receipt_ref)
        need(receipt['request_ref'] == request_ref, 'receipt_request')
        journals = []
        is_report = request['operation'].endswith('report@1')
        if self.name == 'insurance':
            need(receipt_ref['kind'] == 'Receipt' and receipt_ref['schema'] == self.prefix + 'receipt.v1', 'receipt_schema')
            need(set(before['heads']) == set(after['heads']) == {'issued', 'replacement', 'held', 'accounts'}, 'owner_set')
            need(request['expected_heads'] == before['heads'], 'request_read_set')
            need(receipt['before_heads'] == before['heads'] and receipt['after_heads'] == after['heads'], 'receipt_heads')
            written = [role for role in ('issued', 'replacement', 'held', 'accounts') if before['heads'][role] != after['heads'][role]]
            need(receipt['written_roles'] == written, 'receipt_write_set')
            for role in before['heads']:
                old, new = self.body(before['heads'][role]), self.body(after['heads'][role])
                need(all(old[k] == new[k] for k in ('context_ref', 'role', 'owner_id', 'group_id')), 'owner_identity_changed')
                need(old['role'] == role, 'owner_role')
                if role in written:
                    need(new['generation'] == old['generation'] + 1 and new['last_result_ref'] == output_ref, 'owner_generation')
                if not is_report:
                    need(new['balances'] == output['closing'][role], 'component_closing')
            if is_report:
                need(output_ref['kind'] == 'ComponentReport' and output['state_refs'] == before['heads'], 'report_state')
                need(before['heads'] == after['heads'] and receipt['status'] == 'report_published', 'report_financial_change')
            else:
                need(output_ref['kind'] == 'ComponentResult', 'output_kind')
                status = 'unresolved_published' if response['disposition'] == 'partial' else 'committed'
                need(receipt['status'] == status, 'receipt_status')
                if response['disposition'] == 'partial':
                    need(not written and not output['journal'], 'partial_financial_change')
                if output['journal']:
                    journals = [{'request_ref': request_ref, 'result_ref': output_ref, 'lines': output['journal']}]
            need(response['published_digests'] == self.closure([request_ref, response['submission_ref'], receipt_ref]), 'native_publication_closure')
        elif self.name == 'group':
            need(receipt.get('legal_effect') == 'none', 'group_legal_effect')
            need(set(before['group_heads']) == set(after['group_heads']), 'owner_set')
            owner = request['expected_head']['owner_key']
            need(before['group_heads'].get(owner) == request['expected_head'], 'request_read_set')
            need(all(after['group_heads'][k] == v for k, v in before['group_heads'].items() if k != owner), 'other_component_changed')
            old, new = before['group_heads'][owner], after['group_heads'][owner]
            if is_report:
                need(receipt_ref['kind'] == 'ReportReceipt' and receipt_ref['schema'] == self.prefix + 'reportreceipt.v1', 'receipt_schema')
                need(old == new and receipt['status'] == 'component_report_published' and receipt['state_ref'] == old['state_ref'], 'report_financial_change')
            else:
                proposal_ref = request['arguments']['value']['proposal_ref']
                proposal = self.body(proposal_ref)
                need(proposal['result_ref'] == output_ref and receipt['proposal_ref'] == proposal_ref, 'proposal_result_binding')
                need(proposal['from_state_ref'] == old['state_ref'] and proposal['to_state_ref'] == new['state_ref'], 'proposal_state_binding')
                need(receipt_ref['kind'] == 'PublicationReceipt' and receipt_ref['schema'] == self.prefix + 'publicationreceipt.v1', 'receipt_schema')
                need(receipt['from_state_ref'] == old['state_ref'] and receipt['to_state_ref'] == new['state_ref'], 'receipt_heads')
                status = 'unresolved_result_published' if response['disposition'] == 'partial' else 'component_committed'
                need(receipt['status'] == status, 'receipt_status')
                if response['disposition'] == 'partial':
                    need(old == new and not output['adjustment_journal'], 'partial_financial_change')
                else:
                    need(new['owner_key'] == owner and new['generation'] == old['generation'] + 1, 'owner_generation')
                    old_state, new_state = self.body(old['state_ref']), self.body(new['state_ref'])
                    need(new_state['sequence'] == old_state['sequence'] + 1 and new_state['last_result_ref'] == output_ref, 'component_state')
                    need(all(new_state[k] == old_state[k] for k in ('owner_key', 'context_ref', 'branch_id', 'component_scope')), 'owner_identity_changed')
                    # A new component state can read a later immutable legal-book
                    # snapshot. That does not mutate the world's legal heads.
                if output['adjustment_journal']:
                    journals = [{'owner_key': owner, 'result_ref': output_ref, 'lines': output['adjustment_journal']}]
        else:
            expected_kind = 'QueryPublicationReceipt' if self.name == 'bank-assessment' else 'PublicationReceipt'
            need(receipt_ref['kind'] == expected_kind and receipt_ref['schema'] == self.prefix + expected_kind.lower() + '.v1', 'receipt_schema')
            need(receipt['status'] == 'query_published' and receipt['accounting_effect'] == 'none', 'query_financial_effect')
            if self.name == 'insurance-assessment':
                need(response['accounting_effect'] == output['accounting_effect'] == 'none', 'query_financial_effect')
                need(response['published_digests'] == self.closure([output_ref, receipt_ref]), 'native_publication_closure')
        need(after['journals'] == before['journals'] + journals, 'journal_delta')
