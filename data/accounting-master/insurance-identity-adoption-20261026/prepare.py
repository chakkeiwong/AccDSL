"""Freeze baseline, policy schema and the exact two-expression protocol delta."""
import ast
import json
from hashlib import sha256
from native import HERE, ROOT, OLD, ATT, n, idx

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

assert not (HERE / 'source-lock.json').exists()
protected = list(OLD.glob('*.py')) + [OLD / 'semantic-contract.md', OLD / 'predecessor-lock.json']
protected += [ATT / 'portable-exchanges.json', ATT / 'record-schemas.json']
protected += list((HERE.parent / 'component-identity-repair-20261026').glob('*.py'))
protected += [ROOT / 'docs/design/proposal/manuscript-invariant-source-20261026/accounting-product-proposal.pdf']
base = json.loads((ATT / 'portable-exchanges.json').read_text())
protected += [ROOT / x['path'] for x in base['blobs'].values()]
write('source-lock.json', {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(protected))})

old_schema = json.loads((ATT / 'record-schemas.json').read_text())
ref = old_schema['$defs']['OperationRequest']['properties']['profile_ref']
blob = old_schema['$defs']['Submission']['properties']['wire_blob']
properties = {
    'policy_id': {'const': 'InsuranceComponentsIdentity/1'},
    'financial_profile_ref': ref,
    'financial_schema_blob': blob,
    'financial_contract_blob': blob,
    'identity_schema_blob': blob,
    'identity_contract_blob': blob,
    'index_format': {'const': idx.FORMAT},
    'execution_mode': {'const': 'specification_example'},
}
schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
          'type': 'object', 'properties': properties,
          'required': list(properties), 'additionalProperties': False}
n.Draft202012Validator.check_schema(schema)
write('identity-policy-schema.json', schema)

source = (OLD / 'verify_exchanges.py').read_text()
tree = ast.parse(source)
cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Auditor')
methods = [next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == name)
           for name in ('request', 'exchange')]
chunks = []
old = "r['client_id']+'/'+r['request_id']"
new = "idx.pair_key(r['client_id'],r['request_id'])"
for method in methods:
    chunk = '\n'.join(source.splitlines()[method.lineno - 1:method.end_lineno])
    assert chunk.count(old) == 1
    chunks.append(chunk.replace(old, new))
header = '"""Pinned native protocol: only the two pair-key expressions differ."""\nfrom copy import deepcopy\nfrom native import n, idx\nRefusal=n.Refusal\nFinanceRefusal=n.FinanceRefusal\nneed=n.need\nenc=n.enc\nOPS=n.OPS\nROLES=n.ROLES\ninvariant=n.invariant\nunpack=n.unpack\n\nclass PairProtocol(n.Auditor):\n'
(HERE / 'adapted_protocol.py').write_text(header + '\n'.join(chunks) + '\n')
write('protocol-delta.json', {'source': str((OLD / 'verify_exchanges.py').relative_to(ROOT)),
    'source_sha256': digest(OLD / 'verify_exchanges.py'),
    'methods': ['request', 'exchange'], 'replacement_count': 2,
    'old': old, 'new': new, 'adapted_sha256': digest(HERE / 'adapted_protocol.py')})
print(json.dumps({'protected_files': len(set(protected)), 'adapted_methods': 2, 'policy': 'InsuranceComponentsIdentity/1'}))
