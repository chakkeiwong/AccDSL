"""Versioned identity policy over unchanged finite financial records and methods."""
from copy import deepcopy
from collections import Counter
import json
from native import HERE, ROOT, ATT, n, idx
from adapted_protocol import PairProtocol

POLICY = 'InsuranceComponentsIdentity/1'
POLICY_SCHEMA = 'accdsl.insurance-components.identitypolicy.v1'

class Auditor(PairProtocol):
    def __init__(self, packet):
        super().__init__(ATT)
        n.need(packet['base_packet_sha256'] == n.sha((ATT / 'portable-exchanges.json').read_bytes()), 'base_packet_changed')
        self.packet = deepcopy(packet)
        for h, record in packet['records'].items():
            n.need(h not in self.reg or self.reg[h] == record, 'immutable_record_collision')
            self.reg[h] = deepcopy(record)
        for h, value in packet['blobs'].items():
            if h in self.p['blobs']:
                n.need(self.p['blobs'][h] == value, 'immutable_blob_collision')
            self.p['blobs'][h] = deepcopy(value)
        self.policy_ref = deepcopy(packet['identity_profile_ref'])
        self.policy_schema = n.decode((HERE / 'identity-policy-schema.json').read_bytes())
        self.checked_shapes = set()

    def shape(self, record, digest):
        if digest in self.checked_shapes:
            return
        if record['kind'] != 'IdentityPolicy':
            n.Auditor.shape(self, record, digest)
            self.checked_shapes.add(digest)
            return
        n.need(set(record) == {'kind', 'schema', 'key', 'revision', 'body', 'dependencies'}, 'closed_record_shape')
        n.need(record['schema'] == POLICY_SCHEMA and record['revision'] == 0, 'identity_schema')
        n.need(isinstance(record['key'], str) and bool(record['key']), 'record_identity')
        n.need(not list(n.Draft202012Validator(self.policy_schema).iter_errors(record['body'])), 'identity_policy_shape')
        n.need(record['dependencies'] == n.unique(n.refs(record['body'])), 'dependency_closure')
        for ref in n.refs(record['body']):
            self.record(ref)
        for blob in n.blobs(record['body']):
            self.blob(blob)
        n.need(n.sha(('accdsl.portable.v1/' + record['schema']).encode() + b'\0' + n.enc(record)) == digest, 'record_digest')
        self.checked_shapes.add(digest)

    def profile_contract(self, world):
        n.need(world.get('identity_profile_ref') == self.policy_ref, 'identity_policy_binding')
        for h in self.closure([self.policy_ref]):
            self.shape(self.reg[h], h)
        policy = self.body(self.policy_ref)
        n.need(policy['policy_id'] == POLICY and policy['financial_profile_ref'] == self.alias['profile'], 'financial_profile_binding')
        base = self.body(self.alias['profile'])
        lock = self.body(base['schema_lock_ref'])
        n.need(base['profile_id'] == 'InsuranceComponents/1' and base['operations'] == list(n.OPS), 'financial_profile_binding')
        n.need(policy['financial_schema_blob'] == lock['schema_blob'] and policy['financial_contract_blob'] == lock['semantic_contract_blob'], 'financial_lock_binding')
        for field, path in [('financial_schema_blob', ATT / 'record-schemas.json'),
                            ('financial_contract_blob', ATT / 'inputs/semantic-contract.md'),
                            ('identity_schema_blob', HERE / 'identity-policy-schema.json'),
                            ('identity_contract_blob', HERE / 'semantic-contract.md')]:
            n.need(self.blob(policy[field]) == path.read_bytes(), 'identity_contract_lock')

    def request(self, request, submission, world):
        self.profile_contract(world)
        for h in self.closure([request, submission]):
            self.shape(self.reg[h], h)
        body = self.body(request)
        key = idx.pair_key(body['client_id'], body['request_id'])
        if key in world['decisions']:
            decision = world['decisions'][key]
            pair = idx.checked_decision(decision, self.reg, self.alias['profile'])
            n.need(idx.pair_key(*pair) == key, 'index_key_binding')
            for h in self.closure([decision['response_ref']]):
                self.shape(self.reg[h], h)
            response = self.body(decision['response_ref'])
            n.need(response['disposition'] in ('completed', 'partial') and response['additional_commit'], 'retained_decision_status')
            n.need(response['published_digests'] == self.closure([decision['request_ref'], response['submission_ref'], decision['receipt_ref']]), 'retained_publication_closure')
            n.need(set(self.closure([decision['response_ref']])) <= set(world['published_records']), 'retained_publication_missing')
        return PairProtocol.request(self, request, submission, world)

    def exchange(self, exchange):
        for h in self.closure([exchange['response_ref']]):
            self.shape(self.reg[h], h)
        return PairProtocol.exchange(self, exchange)


class Store:
    """Append-only documentary record author, never a live persistence service."""
    def __init__(self):
        self.base = n.Auditor(ATT)
        self.packet = {'profile': POLICY, 'base_packet_sha256': n.sha((ATT / 'portable-exchanges.json').read_bytes()),
                       'records': {}, 'blobs': {}, 'exchanges': [], 'migrations': []}
        self.reg = deepcopy(self.base.reg)
        self._auditor = None
        self.checked_base = set()
        lock = self.base.body(self.base.body(self.base.alias['profile'])['schema_lock_ref'])
        policy = dict(policy_id=POLICY, financial_profile_ref=self.base.alias['profile'],
                      financial_schema_blob=lock['schema_blob'], financial_contract_blob=lock['semantic_contract_blob'],
                      identity_schema_blob=self.blob(HERE / 'identity-policy-schema.json'),
                      identity_contract_blob=self.blob(HERE / 'semantic-contract.md'),
                      index_format=idx.FORMAT, execution_mode='specification_example')
        self.packet['identity_profile_ref'] = self.add('IdentityPolicy', 'identity-policy', policy)

    def blob(self, path, raw=None):
        if raw is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                n.need(path.read_bytes() == raw, 'existing_blob_differs')
            else:
                path.write_bytes(raw)
        data = path.read_bytes()
        h = n.sha(data)
        meta = dict(path=str(path.relative_to(ROOT)), byte_length=len(data))
        if h not in self.base.p['blobs']:
            self.packet['blobs'][h] = meta
        return dict(kind='blob', algorithm='sha256', digest=h, byte_length=len(data))

    def add(self, kind, key, body):
        schema = POLICY_SCHEMA if kind == 'IdentityPolicy' else self.base.schema['schema_ids'][kind]
        record = dict(kind=kind, schema=schema, key=key, revision=0, body=deepcopy(body), dependencies=n.unique(n.refs(body)))
        h = n.sha(('accdsl.portable.v1/' + schema).encode() + b'\0' + n.enc(record))
        n.need(h not in self.reg or self.reg[h] == record, 'immutable_record_collision')
        self.reg[h] = record
        if h not in self.base.reg:
            self.packet['records'][h] = record
        return dict(kind=kind, schema=schema, digest=h)

    def auditor(self):
        if self._auditor is None:
            self._auditor = Auditor(self.packet)
        self._auditor.reg = self.reg
        self._auditor.p['blobs'].update(self.packet['blobs'])
        return self._auditor

    def mapped_world(self, world):
        """Pure expected-value conversion; validation belongs to migrate()."""
        result = deepcopy(world)
        result['identity_profile_ref'] = deepcopy(self.packet['identity_profile_ref'])
        result['decisions'] = {}
        for entry in world['decisions'].values():
            request = self.base.body(entry['request_ref'])
            key = idx.pair_key(request['client_id'], request['request_id'])
            n.need(key not in result['decisions'] or result['decisions'][key] == entry, 'conflicting_decision_history')
            result['decisions'][key] = deepcopy(entry)
        return result

    def migrate(self, world, publications):
        n.need('identity_profile_ref' not in world, 'already_bound_world')
        decisions = []
        for publication in publications:
            for h in self.base.closure([publication['response_ref']]):
                if h not in self.checked_base:
                    self.base.shape(self.base.reg[h], h)
                    self.checked_base.add(h)
            self.base.exchange(publication)
            response = self.base.body(publication['response_ref'])
            n.need(response['disposition'] in ('completed', 'partial') and response['additional_commit'], 'not_publication')
            decisions.append({k: publication['request_ref'] if k == 'request_ref' else publication['response_ref'] if k == 'response_ref' else response[k]
                              for k in ('request_ref', 'response_ref', 'output_ref', 'receipt_ref')})
        index = idx.migrate_legacy(world['decisions'], decisions, self.base.reg, self.base.alias['profile'])
        for entry in decisions:
            n.need(set(self.base.closure([entry['response_ref']])) <= set(world['published_records']), 'retained_publication_missing')
        expected_journals = []
        for entry in world['decisions'].values():
            output = self.base.body(entry['output_ref'])
            if entry['output_ref']['kind'] == 'ComponentResult' and output['journal']:
                expected_journals.append(dict(request_ref=entry['request_ref'], result_ref=entry['output_ref'], lines=output['journal']))
        # A JSON object's iteration order is not the chronology of its decisions.
        # Check exact membership/multiplicity, then preserve the original sequence.
        n.need(Counter(map(n.enc, world['journals'])) == Counter(map(n.enc, expected_journals)), 'retained_journal_history')
        self.base.values(world['heads'])
        for head in world['heads'].values():
            self.base.state(head)
        after = deepcopy(world)
        after['decisions'] = index['entries']
        after['identity_profile_ref'] = deepcopy(self.packet['identity_profile_ref'])
        n.need(after == self.mapped_world(world), 'migration_drift')
        self.packet['migrations'].append(dict(before=deepcopy(world), after=deepcopy(after),
                                              publication_ids=[p['id'] for p in publications],
                                              complete_history='caller_supplied_assumption'))
        return after

    def request(self, template, label, client_id, request_id, **changes):
        body = deepcopy(self.reg[template['digest']]['body'])
        body.update(changes, client_id=client_id, request_id=request_id)
        rq = self.add('OperationRequest', 'request.' + label, body)
        sub = self.add('Submission', 'submission.' + label, dict(request_ref=rq,
                       wire_blob=self.blob(HERE / 'request-bytes' / (label + '.json'), n.enc(body)),
                       decoder='canonical_JSON_exact_rationals_v1'))
        return rq, sub

    def execute(self, label, request, submission, world, report_ref=None):
        """Construct a complete finite decision; financial validation is retained."""
        a = self.auditor()
        # Policy/byte errors are boundary refusals, not normal financial decisions.
        a.profile_contract(world)
        for h in a.closure([request, submission]):
            a.shape(a.reg[h], h)
        r = a.body(request)
        s = a.body(submission)
        n.need(s['request_ref'] == request and a.blob(s['wire_blob']) == n.enc(r), 'wire_binding')
        n.need(r['profile_ref'] == a.alias['profile'], 'request_profile')
        key = idx.pair_key(r['client_id'], r['request_id'])
        after = deepcopy(world)
        if key in world['decisions']:
            old = world['decisions'][key]
            idx.checked_decision(old, a.reg, a.alias['profile'])
            n.need(idx.pair_key(*idx.request_pair(old['request_ref'], a.reg, a.alias['profile'])) == key, 'index_key_binding')
            if old['request_ref'] != request:
                response = dict(request_ref=request, submission_ref=submission, disposition='rejected', diagnostics=['identity_conflict'], output_ref=None, receipt_ref=None, published_digests=[], additional_commit=False)
            else:
                # Independently check retained publication before constructing retry.
                a.request(request, submission, world)
                response = dict(a.body(old['response_ref']), disposition='replayed', additional_commit=False)
        else:
            try:
                n.need(not r['require_current'] or r['view_ref'] == world['current_view_ref'], 'stale_view')
                n.need(r['expected_heads'] == world['heads'], 'stale_head')
                n.need(a.body(r['view_ref'])['context_ref'] == r['context_ref'], 'request_context')
                if r['operation'] == n.OPS[0]:
                    n.need(set(r['arguments']) == {'proposal_ref'}, 'operation_arguments')
                    proposal = a.proposal(r['arguments']['proposal_ref'])
                    basis = a.body(proposal['basis_ref'])
                    n.need(proposal['before_heads'] == r['expected_heads'] and basis['view_ref'] == r['view_ref'] and basis['context_ref'] == r['context_ref'], 'request_basis')
                    output, heads = proposal['result_ref'], proposal['after_heads']
                    codes = a.body(output)['diagnostics']
                    status = 'unresolved_published' if codes else 'committed'
                else:
                    n.need(r['operation'] == n.OPS[1] and set(r['arguments']) == {'state_refs'}, 'operation_arguments')
                    n.need(r['arguments']['state_refs'] == r['expected_heads'], 'report_heads')
                    for head in r['expected_heads'].values():
                        a.state(head)
                    n.invariant(n.unpack(a.values(r['expected_heads'])))
                    n.need(report_ref is not None, 'missing_report')
                    report = a.body(report_ref)
                    n.need(report_ref['kind'] == 'ComponentReport' and report['context_ref'] == r['context_ref'] and report['state_refs'] == r['expected_heads'], 'report_binding')
                    output, heads, codes, status = report_ref, r['expected_heads'], [], 'report_published'
                receipt = self.add('Receipt', 'receipt.' + label, dict(request_ref=request, output_ref=output,
                                   before_heads=world['heads'], after_heads=heads,
                                   written_roles=[role for role in n.ROLES if world['heads'][role] != heads[role]], status=status))
                a.reg = self.reg
                response = dict(request_ref=request, submission_ref=submission, disposition='partial' if codes else 'completed',
                                diagnostics=codes, output_ref=output, receipt_ref=receipt,
                                published_digests=a.closure([request, submission, receipt]), additional_commit=True)
                after['heads'] = deepcopy(heads)
                if r['operation'] == n.OPS[0] and a.body(output)['journal']:
                    after['journals'].append(dict(request_ref=request, result_ref=output, lines=a.body(output)['journal']))
            except (n.Refusal, n.FinanceRefusal) as error:
                response = dict(request_ref=request, submission_ref=submission, disposition='rejected', diagnostics=[error.code],
                                output_ref=None, receipt_ref=None, published_digests=[], additional_commit=False)
        response_ref = self.add('OperationResult', 'response.' + label, response)
        a.reg = self.reg
        if response['additional_commit']:
            after['published_records'] = sorted(set(after['published_records']) | set(a.closure([response_ref])))
            after['decisions'][key] = dict(request_ref=request, response_ref=response_ref, output_ref=response['output_ref'], receipt_ref=response['receipt_ref'])
        exchange = dict(id=label, role='publication' if response['additional_commit'] else response['disposition'],
                        request_ref=request, submission_ref=submission, response_ref=response_ref,
                        world_before=deepcopy(world), world_after=after)
        self.auditor().exchange(exchange)
        self.packet['exchanges'].append(exchange)
        return exchange
