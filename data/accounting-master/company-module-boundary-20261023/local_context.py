"""Only fixed inspected local paths can supply executable methods."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
from boundary import canonical, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent/'company-composition-20261016'


def context():
    packet_path = BASE/'attempt-03/portable-exchanges.json'
    validation_path = BASE/'attempt-03/validation-01.json'
    prior = json.loads(validation_path.read_text())
    need(prior['failed'] == 0, 'predecessor_failed')
    need(sha256(packet_path.read_bytes()).hexdigest() == prior['packet_sha256'], 'predecessor_packet_changed')
    packet = json.loads(packet_path.read_text())
    m = deepcopy(next(x for x in packet['migrations'] if x['subset'] == 'return'))
    locked = {str(packet_path.relative_to(ROOT)): prior['packet_sha256'],
              str(validation_path.relative_to(ROOT)): sha256(validation_path.read_bytes()).hexdigest()}
    for key in ['source_packet', 'source_schema']:
        row = m[key]; raw = (ROOT/row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'] and len(raw) == row['byte_length'], 'protected_source_changed')
        locked[row['path']] = row['sha256']
    for key, row in packet['input_snapshots'].items():
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'protected_method_input_changed')
        locked[row['path']] = row['sha256']
    method_path = ROOT/packet['input_snapshots']['migration_design.py']['path']
    need(sha256(method_path.read_bytes()).hexdigest() == prior['migration_sha256'], 'migration_method_changed')
    spec = importlib.util.spec_from_file_location('retained_return_migration', method_path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    source = json.loads((ROOT/m['source_packet']['path']).read_text())
    source_state = source['record_registry'][m['source_state_ref']['digest']]['body']
    descriptor = {'method_id': 'rcost.settle', 'subset': 'return',
        'method_file_sha256': prior['migration_sha256'], 'source_packet_sha256': m['source_packet']['sha256'],
        'source_schema_sha256': m['source_schema']['sha256'],
        'source_state_ref': m['source_state_ref'], 'source_closing_ref': m['source_closing_ref'],
        'event_sha256': sha256(canonical(m['event'])).hexdigest(),
        'read_write_accounts': sorted(m['projected']['balances']),
        'memory_fields': sorted(m['projected']), 'posting_mode': 'proposal_only'}
    def project(): return module.projection(source, m['source_state_ref'], 'return', need)
    def step(state, event, checker): return module.target_step(state, event, checker)
    return {'migration': m, 'descriptor': descriptor, 'account_map': module.SPECS['return']['accounts'],
        'project': project, 'step': step, 'expected_after': module.map_closed_result(source, m['source_closing_ref'], 'return'),
        'locked': locked, 'source_state': source_state, 'source_packet': source, 'module': module}
