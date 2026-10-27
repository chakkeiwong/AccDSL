"""Bounded applicability probes; fresh temporary databases, no production writes."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import unittest

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests')]
import company_persistence_v1 as storage

spec = importlib.util.spec_from_file_location('storage_audit_native', ROOT/'data/accounting-master/company-return-execution-20261024/native_returns.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)

def hash_file(p):
    return sha256(p.read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def payload_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

def conformance():
    checks = []
    observations = []
    def check(name, passed, **details):
        checks.append({'name':name, 'passed':bool(passed)})
        observations.append({'probe':name, **details})
    rows = json.loads((ROOT/'data/accounting-master/sequential-outcome-range-20261024/cases.json').read_text())
    row = rows[0]
    opening = row['request']['family']['first_family']['state']
    replay = row['result']['branches'][0]['replay']['original_complete_replay']
    event = replay['first']['candidate_event']
    proposal = native.propose(opening, event)
    check('original_native_proposal_matches_saved_state', proposal['after'] == replay['first']['after'])
    with tempfile.TemporaryDirectory(prefix='accdsl-storage-audit-', dir='/tmp') as tmp:
        tmp = Path(tmp)
        path = tmp/'objects.db'
        retained = {}
        with storage.Store(path) as db:
            for name, value in [('opening',opening),('proposal',proposal),('request',row['request'])]:
                key = db.add_node('audit_'+name, value)
                retained[name] = key
                check('roundtrip_'+name, db.node(key) == value)
            candidate = next(r for r in rows if r['case']=='candidate_obligations')['request']
            key = db.add_node('audit_candidate_request', candidate)
            check('candidate_obligations_preserved', db.node(key) == candidate and bool(db.node(key)['family']['obligations']))
            count = db.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            rejected = None
            try:
                db.add_node('audit_full_result', row['result'])
            except storage.P07Error as exc:
                rejected = {'code':exc.code, 'reason':str(exc)}
            check('float_metadata_refused_without_insertion', rejected is not None and rejected['code']=='CanonicalError' and db.db.execute('SELECT count(*) FROM nodes').fetchone()[0] == count, rejection=rejected, field='/wall_seconds')
            raw = payload_bytes(row['result'])
            envelope = {'profile':'OpaqueAuditBytes/1', 'sha256':sha256(raw).hexdigest(), 'bytes_hex':raw.hex()}
            key = db.add_node('audit_raw_result', envelope)
            retained['raw_result'] = key
            saved = bytes.fromhex(db.node(key)['bytes_hex'])
            check('opaque_bytes_preserve_complete_result', saved == raw and json.loads(saved) == row['result'], byte_count=len(raw), sha256=sha256(raw).hexdigest())
            changed = deepcopy(proposal)
            changed['after']['balances']['cash'] = native.fmt(native.q(changed['after']['balances']['cash'])+1)
            changed['after']['balances']['original_equity'] = native.fmt(native.q(changed['after']['balances']['original_equity'])-1)
            native.invariant(changed['after'])
            key = db.add_node('audit_forged_proposal', changed)
            refused = False
            try:
                native.apply(opening, event, db.node(key))
            except native.Rejected:
                refused = True
            check('generic_integrity_does_not_check_native_semantics', db.integrity()['integrity']=='ok' and refused, generic_storage='accepted', original_semantic_replay='rejected')
            first = {'label':'caf\u00e9'}
            second = {'label':'cafe\u0301'}
            a = db.add_node('audit_unicode', first)
            b = db.add_node('audit_unicode', second)
            check('generic_normalization_can_alias_distinct_bytes', a == b and db.node(b) != second, first_utf8=payload_bytes(first).hex(), second_utf8=payload_bytes(second).hex())
            a = db.add_node('audit_constraints', {'constraints':['second','first']})
            b = db.add_node('audit_constraints', {'constraints':['first','second']})
            check('generic_set_field_identity_is_not_order_preserving', a == b and db.node(b)['constraints'] == ['second','first'])
            ids = []
            for value in [first, second]:
                raw = payload_bytes(value)
                ids.append(db.add_node('audit_raw_unicode', {'sha256':sha256(raw).hexdigest(),'bytes_hex':raw.hex()}))
            check('opaque_bytes_avoid_normalized_identity_alias', ids[0] != ids[1])
            count = db.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            try:
                db.add_node('audit_missing_dep', {}, ['absent'])
                missing = False
            except storage.P07Error as exc:
                missing = exc.code == 'MissingReference'
            check('missing_dependency_refused_atomically', missing and count == db.db.execute('SELECT count(*) FROM nodes').fetchone()[0])
        script = """import json,sys
sys.path.insert(0,sys.argv[1])
from company_persistence_v1 import Store
with Store(sys.argv[2]) as db:
 print(json.dumps({k:db.node(v) for k,v in json.loads(sys.argv[3]).items()},ensure_ascii=False))
"""
        child = subprocess.run([sys.executable,'-B','-c',script,str(ROOT/'scripts'),str(path),json.dumps(retained)],capture_output=True,text=True,timeout=15)
        decoded = json.loads(child.stdout) if child.returncode == 0 else {}
        check('fresh_process_complete_record_reopen', child.returncode == 0 and decoded.get('opening') == opening and decoded.get('proposal') == proposal and decoded.get('request') == row['request'] and json.loads(bytes.fromhex(decoded['raw_result']['bytes_hex'])) == row['result'], returncode=child.returncode)
        child_code = """import os,sys
sys.path.insert(0,sys.argv[1])
from company_persistence_v1 import Store
with Store(sys.argv[2]) as db:
 mode=sys.argv[3]
 if mode!='separate':db.db.execute('BEGIN IMMEDIATE')
 a=db.add_node('batch_a',{'value':'first'})
 if mode in ['separate','before_commit']:os._exit(73)
 db.add_node('batch_b',{'value':'second'},[a])
 db.db.commit()
 os._exit(73)
"""
        for mode, expected in [('separate',1),('before_commit',0),('after_commit',2)]:
            path = tmp/(mode+'.db')
            with storage.Store(path):pass
            child = subprocess.run([sys.executable,'-B','-c',child_code,str(ROOT/'scripts'),str(path),mode],capture_output=True,text=True,timeout=15)
            with storage.Store(path) as db:
                count = db.db.execute("SELECT count(*) FROM nodes WHERE kind LIKE 'batch_%'").fetchone()[0]
                integrity = db.integrity()
            check('process_exit_'+mode, child.returncode == 73 and count == expected and integrity == {'integrity':'ok','foreign_keys':[]}, returncode=child.returncode, retained_batch_nodes=count)
    # Retain a bounded existing regression slice, with its original P05 comparator.
    from test_accounting_p07 import P07Tests
    names = ['test_foreground_process_kill_before_and_after_commit',
             'test_retry_conflict_locks_and_closed_period_no_mutation',
             'test_migration_success_failure_repeat_and_replay']
    suite = unittest.TestSuite(P07Tests(name) for name in names)
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(suite)
    if not tests.wasSuccessful():print(stream.getvalue(),file=sys.stderr)
    check('three_original_p07_recovery_retry_migration_methods', tests.wasSuccessful() and tests.testsRun==3, methods=names)
    locks = json.loads((HERE/'source-lock.json').read_text())
    for name, digest in locks.items():check('protected:'+name, hash_file(ROOT/name)==digest)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'observations':observations}, locks

def main():
    mode = sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode != '--record' or not (HERE/'manifest.json').exists()
    if mode == '--replay':
        manifest = json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for p,h in manifest[group].items():assert hash_file(ROOT/p)==h,p
    started = datetime.now(timezone.utc).isoformat(); start = time.monotonic()
    result, locks = conformance()
    assert result['passed'],[c for c in result['checks'] if not c['passed']]
    observation = {'mode':mode,'passed':True,'checks':len(result['checks']),'probes':len(result['checks'])-len(locks),'protected_inputs':len(locks),'wall_seconds':time.monotonic()-start}
    if mode == '--record':
        dump(HERE/'audit.json',result)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'python3 -B '+str(HERE.relative_to(ROOT)/'audit.py')+' --record',
          'environment':'Python '+platform.python_version()+'; SQLite '+storage.sqlite3.sqlite_version,
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic storage audit',
          'data_version':'source-lock.json; retained complete native and conditional records',
          'inputs':locks,'implementation':{str(p.relative_to(ROOT)):hash_file(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
          'outputs':{str((HERE/'audit.json').relative_to(ROOT)):hash_file(HERE/'audit.json')},
          'plan':'docs/plans/accounting-simulator-storage-reuse-audit-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode == '--replay':assert result==json.loads((HERE/'audit.json').read_text())
    print(json.dumps(observation))

if __name__=='__main__':main()
