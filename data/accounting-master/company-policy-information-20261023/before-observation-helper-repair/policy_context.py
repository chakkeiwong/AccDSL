"""Assemble local trusted callbacks; no packet chooses executable code."""
from pathlib import Path
import hashlib
import json
import sys

from policy_information import HERE, ROOT, TrustedContext, digest
import support
from admission import information_view
from exchanges import load

POLICY = HERE.parent / 'company-policy-20261023'
INFORMATION = HERE.parent / 'company-information-20261023'
EXCHANGE = HERE.parent / 'company-path-exchanges-20261023'
PARENT_NAME = 'second_year_price_revision'


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context():
    previous, engine, validate = support.context()
    method = load('policy_information_locked_generator', POLICY / 'policy.py')
    parent_fixtures = load('policy_information_parent_fixtures', INFORMATION / 'fixtures.py')
    exchange = json.loads((EXCHANGE / 'packet.json').read_text())
    raw = previous.load_blob_files(exchange)
    records = exchange['record_registry']
    root = records[exchange['root_ref']['digest']]['body']
    paths = {records[r['digest']]['body']['name']:
             json.loads(raw[records[r['digest']]['body']['path_blob']['digest']])
             for r in root['path_refs']}
    original = json.loads((support.BASE / 'packet.json').read_text())
    original_root = original['record_registry'][original['root_ref']['digest']]['body']
    original_schema = json.loads((support.OLD / 'record-schemas.json').read_text())
    closure = previous.validate_registry(original['record_registry'],
        [original_root['opening_ref'], original_root['synthetic_admission_ref']],
        original_schema, raw)

    def source(mode, cutoff):
        return information_view(original['record_registry'], closure['record_digests'], mode, cutoff)

    export = records[root['baseline_export_ref']['digest']]['body']
    source_bytes = raw[export['source_bundle_blob']['digest']]

    def execute(path):
        return engine.wire(engine.execute(path, source_bytes))

    materializer = {
        'profile': 'LocalSettlementMaterializerDescriptor/1',
        'implementation': 'SettlementPolicyDraft/1.generate',
        'source': str((POLICY / 'policy.py').relative_to(ROOT)),
        'source_sha256': file_hash(POLICY / 'policy.py'),
        'input_schema_sha256': file_hash(HERE.parent / 'company-operation-path-20261023/schema.json'),
        'scope': 'named_delivery_claims_only; exact rational arithmetic'}
    parent = paths[PARENT_NAME]
    parent_fixture = parent_fixtures.make(parent, digest(exchange))
    trust = TrustedContext(digest(exchange), materializer, frozenset(),
                           validate, source, method.generate, execute)
    saved = json.loads((POLICY / 'checks.json').read_text())
    return {'trust': trust, 'exchange': exchange, 'raw': raw, 'parent': parent,
            'parent_fixture': parent_fixture, 'policy': json.loads((POLICY / 'policy.json').read_text()),
            'materialization': saved['materialization'], 'result': saved['generated_result'],
            'fixed_result': saved['fixed_result'], 'paths': paths}
