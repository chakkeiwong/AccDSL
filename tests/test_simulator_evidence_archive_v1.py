"""Exact bytes and transaction recovery, without promoting raw records to models."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import simulator_evidence_archive_v1 as archive

LIMITS = {'max_records':10,'max_record_bytes':1000000,'max_total_bytes':3000000}

def record(name='one', text='{"profile":"Example/1","value":1}', dependencies=()):
    return {'name':name,'role':'note','profile':'Example/1','json':text,'dependencies':list(dependencies)}

def bundle(*rows):
    return {'profile':archive.PROFILE,'records':list(rows) or [record()]}


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='accdsl-archive-tests-',dir='/tmp')
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'archive.db'

    def error(self, operation, code=None):
        with self.assertRaises(archive.ArchiveError) as caught:
            operation()
        if code:
            self.assertEqual(caught.exception.code,code)

    def test_exact_whitespace_unicode_float_and_number_lexemes(self):
        texts = ['{"profile":"Example/1","value":1}',
                 '{ "value":1.00, "profile":"Example/1" }\n',
                 '{"profile":"Example/1","value":1e0}',
                 '{"profile":"Example/1","name":"café","wall_seconds":0.123}',
                 '{"profile":"Example/1","name":"cafe\u0301","wall_seconds":0.123}',
                 '{"profile":"Example/1","constraints":["a","b"]}',
                 '{"profile":"Example/1","constraints":["b","a"]}']
        keys = []
        with archive.Archive(self.path,LIMITS) as db:
            for text in texts:
                b = bundle(record(text=text)); result = db.archive(b); keys.append(result['receipt'])
                self.assertEqual(db.read(result['receipt'])['bundle'],b)
                for key in archive.BOUNDARY:
                    self.assertIs(result[key],False)
            self.assertEqual(len(set(keys)),len(texts))
        with archive.Archive(self.path,LIMITS) as db:
            self.assertEqual(db.integrity()['receipts'],len(texts))

    def test_exact_retry_and_dependency_order(self):
        b = bundle(record('a'),record('b'),record('c',dependencies=['b','a']))
        with archive.Archive(self.path,LIMITS) as db:
            first = db.archive(b)
            count = db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            self.assertEqual(first,db.archive(b))
            self.assertEqual(count,db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0])
            self.assertEqual(db.read(first['receipt'])['bundle'],b)
            changed = deepcopy(b);changed['records'][2]['dependencies'].reverse()
            other = db.archive(changed)
            self.assertNotEqual(first['receipt'],other['receipt'])
            self.assertEqual(db.read(other['receipt'])['bundle'],changed)

    def test_complete_saved_range_result_and_unknowns_roundtrip(self):
        rows = json.loads((ROOT/'data/accounting-master/sequential-outcome-range-20261024/cases.json').read_text())
        result = next(r for r in rows if r['case']=='candidate_obligations')['result']
        text = json.dumps(result,ensure_ascii=False,indent=2)
        r = {'name':'candidate','role':'result','profile':result['profile'],'json':text,'dependencies':[]}
        with archive.Archive(self.path,LIMITS) as db:
            stored = db.archive(bundle(r));read = db.read(stored['receipt'])
            self.assertEqual(read['bundle']['records'][0]['json'],text)
            self.assertFalse(read['semantic_verified'])
            self.assertEqual(json.loads(text)['actual_outcome'],'unknown')

    def test_bad_json_profiles_and_shapes_reject_without_writes(self):
        cases = [bundle(record(text='{"profile":"Example/1","x":1,"x":2}')),
                 bundle(record(text='{"x":NaN}')),bundle(record(text='{"x":Infinity}')),
                 bundle(record(text='{"x":"\\ud800"}')),bundle(record(text='[]')),
                 bundle(record(text='{"profile":"Other/1"}')),bundle(record(text='{"x":"\ud800"}')),
                 bundle(record(text='{"x":01}')),bundle(record(text='{"x":1} trailing'))]
        with archive.Archive(self.path,LIMITS) as db:
            count = db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            for b in cases:
                self.error(lambda:db.archive(b))
                self.assertEqual(count,db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0])

    def test_invalid_order_names_roles_and_closed_fields(self):
        cases=[bundle(record('a',dependencies=['later']),record('later')),
               bundle(record('a'),record('a')),bundle(record('a',dependencies=['a'])),
               bundle(record('a'),record('b',dependencies=['a','a']))]
        x=bundle();x['records'][0]['role']='execute';cases.append(x)
        x=bundle();x['records'][0]['extra']=False;cases.append(x)
        x=bundle();x['extra']=False;cases.append(x)
        x=bundle();x['records'][0]['name']='../path';cases.append(x)
        x=bundle();x['records'][0]['profile']='\ud800';cases.append(x)
        with archive.Archive(self.path,LIMITS) as db:
            for x in cases:self.error(lambda:db.archive(x))
            self.assertEqual(db.integrity()['receipts'],0)

    def test_explicit_limits_reject_before_writes(self):
        self.error(lambda:archive.Archive(self.path,{}))
        self.assertFalse(self.path.exists())
        self.error(lambda:archive.Archive(self.path,{**LIMITS,'max_records':True}))
        for limits in [{**LIMITS,'max_records':1},{**LIMITS,'max_record_bytes':1},{**LIMITS,'max_total_bytes':1}]:
            with archive.Archive(self.path,limits) as db:
                self.error(lambda:db.archive(bundle(record('a'),record('b'))),'Limit')
                self.assertEqual(db.integrity()['receipts'],0)

    def test_declared_unicode_profile_preserves_exact_bytes(self):
        values=[]
        with archive.Archive(self.path,LIMITS) as db:
            for profile in ['Café/1','Cafe\u0301/1']:
                r=record();r['profile']=profile;r['json']=json.dumps({'profile':profile},ensure_ascii=False)
                result=db.archive(bundle(r));values.append(result['receipt'])
                self.assertEqual(db.read(result['receipt'])['bundle'],bundle(r))
            self.assertNotEqual(*values)

    def test_existing_unrelated_store_refused_without_mutation(self):
        with archive.p07.Store(self.path):pass
        before=self.path.read_bytes()
        self.error(lambda:archive.Archive(self.path,LIMITS),'Unsupported')
        self.assertEqual(before,self.path.read_bytes())

    def test_marker_and_version_refused_readonly(self):
        with archive.Archive(self.path,LIMITS):pass
        with sqlite3.connect(self.path) as db:db.execute('PRAGMA user_version=999')
        before=self.path.read_bytes()
        self.error(lambda:archive.Archive(self.path,LIMITS),'Unsupported')
        self.assertEqual(before,self.path.read_bytes())

    def test_symlink_refused(self):
        original=Path(self.tmp.name)/'original.db'
        with archive.Archive(original,LIMITS):pass
        self.path.symlink_to(original)
        self.error(lambda:archive.Archive(self.path,LIMITS))

    def test_native_forgery_archives_as_unverified_and_replay_rejects(self):
        spec=importlib.util.spec_from_file_location('archive_test_native',ROOT/'data/accounting-master/company-return-execution-20261024/native_returns.py')
        native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
        row=json.loads((ROOT/'data/accounting-master/sequential-outcome-range-20261024/cases.json').read_text())[0]
        opening=row['request']['family']['first_family']['state']
        event=row['result']['branches'][0]['replay']['original_complete_replay']['first']['candidate_event']
        proposal=native.propose(opening,event)
        proposal['after']['balances']['cash']=native.fmt(native.q(proposal['after']['balances']['cash'])+1)
        proposal['after']['balances']['original_equity']=native.fmt(native.q(proposal['after']['balances']['original_equity'])-1)
        native.invariant(proposal['after'])
        r={'name':'proposal','role':'proposal','profile':proposal['profile'],'json':json.dumps(proposal),'dependencies':[]}
        with archive.Archive(self.path,LIMITS) as db:
            result=db.archive(bundle(r));read=db.read(result['receipt'])
            self.assertFalse(read['semantic_verified'])
            with self.assertRaises(native.Rejected):native.apply(opening,event,json.loads(read['bundle']['records'][0]['json']))

    def test_receipt_payload_and_hash_forgery_rejects(self):
        with archive.Archive(self.path,LIMITS) as db:
            key=db.archive(bundle())['receipt']
            value=db.store.node(key);value['boundary']['semantic_verified']=True
            db.store.db.execute('DROP TRIGGER immutable_nodes_UPDATE')
            db.store.db.execute('UPDATE nodes SET payload=?,digest=?,canonical=? WHERE id=?',
                (archive.p07.dump(value),archive.p07.identity('archive_receipt',value),archive.p07.canonical(value),key))
            self.error(lambda:db.read(key),'Integrity')

    def test_dependency_edge_tampering_rejects(self):
        with archive.Archive(self.path,LIMITS) as db:
            key=db.archive(bundle(record('a'),record('b',dependencies=['a'])))['receipt']
            receipt=db.store.node(key);child=receipt['ordered_records'][1]['node'];parent=receipt['ordered_records'][0]['node']
            db.store.db.execute('DROP TRIGGER immutable_edges_DELETE')
            db.store.db.execute('DELETE FROM edges WHERE parent=? AND child=?',(parent,child))
            self.error(lambda:db.read(key),'Integrity')

    def test_record_bytes_tampering_rejects(self):
        with archive.Archive(self.path,LIMITS) as db:
            key=db.archive(bundle())['receipt'];node=db.store.node(key)['ordered_records'][0]['node']
            value=db.store.node(node);value['bytes_hex']='7b7d'
            db.store.db.execute('DROP TRIGGER immutable_nodes_UPDATE')
            db.store.db.execute('UPDATE nodes SET payload=? WHERE id=?',(archive.p07.dump(value),node))
            self.error(lambda:db.read(key),'Integrity')

    def test_retry_does_not_silently_accept_corrupted_existing_node(self):
        with archive.Archive(self.path,LIMITS) as db:
            b=bundle();key=db.archive(b)['receipt']
            node=db.store.node(key)['ordered_records'][0]['node']
            value=db.store.node(node);value['bytes_hex']='7b7d'
            db.store.db.execute('DROP TRIGGER immutable_nodes_UPDATE')
            db.store.db.execute('UPDATE nodes SET payload=? WHERE id=?',(archive.p07.dump(value),node))
            self.error(lambda:db.archive(b),'Integrity')
            self.assertFalse(db.store.db.in_transaction)

    def test_mutated_marker_vetoes_archive_before_write(self):
        with archive.Archive(self.path,LIMITS) as db:
            db.store.db.execute('DROP TRIGGER immutable_nodes_UPDATE')
            db.store.db.execute('UPDATE nodes SET payload=? WHERE id=?',('{}',db.marker_id))
            before=db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            self.error(lambda:db.archive(bundle()),'Integrity')
            self.error(lambda:db.integrity(),'Integrity')
            self.assertEqual(before,db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0])

    def test_reopen_with_smaller_limits_refuses_oversize_read(self):
        b=bundle(record('a'),record('b',dependencies=['a']))
        with archive.Archive(self.path,LIMITS) as db:key=db.archive(b)['receipt']
        with archive.Archive(self.path,{**LIMITS,'max_total_bytes':1}) as db:
            self.error(lambda:db.read(key),'Limit')

    def test_exceptions_roll_back_group_and_retry(self):
        b=bundle(record('a'),record('b',dependencies=['a']))
        for point in ['record_0','record_1','before_commit']:
            with archive.Archive(self.path,LIMITS) as db:
                count=db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
                def fault(name):
                    if name==point:raise RuntimeError(point)
                db.fault=fault
                with self.assertRaises(RuntimeError):db.archive(b)
                self.assertEqual(count,db.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0])
                self.assertEqual(db.integrity()['receipts'],0)
        with archive.Archive(self.path,LIMITS) as db:
            result=db.archive(b);self.assertEqual(db.read(result['receipt'])['bundle'],b)

    def test_process_exit_initialization_and_atomic_bundle(self):
        source="""import json,os,sys
sys.path.insert(0,sys.argv[1])
from simulator_evidence_archive_v1 import Archive
def fault(point):
 if point==sys.argv[3]:os._exit(74)
with Archive(sys.argv[2],json.loads(sys.argv[4]),fault=fault) as db:
 db.archive(json.loads(sys.argv[5]))
"""
        b=bundle(record('a'),record('b',dependencies=['a']))
        for point,exists,receipts in [('initial_before_publish',False,0),('initial_after_publish',True,0),('record_0',True,0),('before_commit',True,0),('after_commit',True,1)]:
            path=Path(self.tmp.name)/(point+'.db')
            child=subprocess.run([sys.executable,'-B','-c',source,str(ROOT/'scripts'),str(path),point,json.dumps(LIMITS),json.dumps(b)],capture_output=True,text=True,timeout=15,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1'})
            self.assertEqual(child.returncode,74,child.stderr)
            self.assertEqual(path.exists(),exists)
            with archive.Archive(path,LIMITS) as db:
                self.assertEqual(db.integrity()['receipts'],receipts)
                result=db.archive(b)
                self.assertEqual(db.read(result['receipt'])['bundle'],b)
                self.assertEqual(db.integrity()['receipts'],1)

    def test_fresh_process_reads_full_exact_bundle(self):
        b=bundle(record('a'),record('b',text=' {"profile":"Example/1","x":1.0} ',dependencies=['a']))
        with archive.Archive(self.path,LIMITS) as db:key=db.archive(b)['receipt']
        code="""import json,sys
sys.path.insert(0,sys.argv[1])
from simulator_evidence_archive_v1 import Archive
with Archive(sys.argv[2],json.loads(sys.argv[3])) as db:print(json.dumps(db.read(sys.argv[4])))
"""
        child=subprocess.run([sys.executable,'-B','-c',code,str(ROOT/'scripts'),str(self.path),json.dumps(LIMITS),key],capture_output=True,text=True,timeout=15)
        self.assertEqual(child.returncode,0,child.stderr)
        self.assertEqual(json.loads(child.stdout)['bundle'],b)


if __name__=='__main__':unittest.main()
