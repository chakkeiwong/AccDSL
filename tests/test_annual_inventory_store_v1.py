from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,os,sqlite3,subprocess,sys,tempfile,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('store_test_examples',ROOT/'data/accounting-master/annual-inventory-persistence-20261025/examples.py')
x=importlib.util.module_from_spec(s);s.loader.exec_module(x);m=x.m
WORKER=ROOT/'data/accounting-master/annual-inventory-persistence-20261025/worker.py'

class AnnualInventoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='accdsl-store-test-',dir='/tmp');self.path=Path(self.tmp.name)/'book.sqlite'
    def tearDown(self):self.tmp.cleanup()
    def request(self):return m.runtime.request(x.inventory.root(),[x.inventory.sale('one'),x.inventory.sale('two')])
    def worker(self,action):return subprocess.run([sys.executable,'-B',str(WORKER),str(self.path),action],cwd=ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1'},capture_output=True,text=True,timeout=60)

    def test_chunked_and_uninterrupted_results_match(self):
        for row in x.requests():
            path=Path(self.tmp.name)/(row['case']+'.sqlite');q=row['request'];expected=m.runtime.run(q)
            with m.Store(path,q) as store:
                while store.current['status']=='paused_provisional':store.advance(1,expected_cursor=store.cursor)
                self.assertEqual(store.current,expected)
            with m.Store(path,q) as store:self.assertEqual(store.current,expected)

    def test_successive_process_reopens_preserve_tax_and_archives(self):
        q=x.inventory.residual_carry()
        with m.Store(self.path,q) as store:store.advance(2)
        for budget in [1,1,1]:
            with m.Store(self.path,q) as store:result=store.advance(budget,expected_cursor=store.cursor)
        self.assertEqual(result['result'],m.runtime.run(q));book=result['result']['period_book']
        self.assertEqual(len(book['after']['balances']),26);self.assertEqual(book['after']['balances']['income_tax_payable'],'-49/4')
        self.assertEqual(book['period_archive'][0]['after']['lots']['recovered']['units'],'1/1')
        process=self.worker('inspect');self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual(json.loads(process.stdout)['result_sha256'],result['result_sha256'])

    def test_zero_budget_and_retry_cursor_do_not_repeat_sales(self):
        q=self.request()
        with m.Store(self.path,q) as store:
            zero=store.advance(0,expected_cursor=0);self.assertEqual(zero['cursor'],0);self.assertEqual(zero['result']['status'],'paused_provisional')
            first=store.advance(1,expected_cursor=0);self.assertEqual(first['cursor'],1)
            self.assertEqual(store.advance(1,expected_cursor=0),first)
            final=store.advance(1,expected_cursor=1);self.assertEqual(final['result'],m.runtime.run(q))
            self.assertEqual(store.advance(10,expected_cursor=2),final)

    def test_before_commit_process_exit_rolls_back(self):
        q=self.request()
        with m.Store(self.path,q):pass
        process=self.worker('before_commit');self.assertEqual(process.returncode,73,process.stderr)
        with m.Store(self.path,q) as store:
            self.assertEqual(store.cursor,0);self.assertEqual(store.current['period_book']['after']['balances']['cash'],'452/1')
            self.assertEqual(store.advance(2,expected_cursor=0)['result'],m.runtime.run(q))

    def test_interrupted_initialization_recovers_with_original_request(self):
        q=self.request();request_file=Path(self.tmp.name)/'request.json';request_file.write_text(json.dumps(q))
        process=subprocess.run([sys.executable,'-B',str(WORKER),str(self.path),'initial_before_commit',str(request_file)],cwd=ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1'},capture_output=True,text=True,timeout=60)
        self.assertEqual(process.returncode,73,process.stderr)
        with self.assertRaisesRegex(m.Invalid,'uninitialized_store_requires_request'):m.Store(self.path)
        with m.Store(self.path,q) as store:
            self.assertEqual(store.cursor,0);self.assertEqual(store.advance(2)['result'],m.runtime.run(q))

    def test_initial_commit_survives_process_exit(self):
        q=self.request();request_file=Path(self.tmp.name)/'request.json';request_file.write_text(json.dumps(q))
        process=subprocess.run([sys.executable,'-B',str(WORKER),str(self.path),'initial_after_commit',str(request_file)],cwd=ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1'},capture_output=True,text=True,timeout=60)
        self.assertEqual(process.returncode,73,process.stderr)
        with m.Store(self.path) as store:
            self.assertEqual(store.cursor,0);self.assertEqual(store.advance(2)['result'],m.runtime.run(q))

    def test_after_commit_process_exit_retains_exactly_one_sale(self):
        q=self.request()
        with m.Store(self.path,q):pass
        process=self.worker('after_commit');self.assertEqual(process.returncode,73,process.stderr)
        with m.Store(self.path,q) as store:
            self.assertEqual(store.cursor,1);self.assertEqual(store.current['period_book']['after']['balances']['cash'],'467/1')
            self.assertEqual(store.advance(1,expected_cursor=0)['cursor'],1)
            self.assertEqual(store.advance(1,expected_cursor=1)['result'],m.runtime.run(q))

    def test_refused_operation_is_terminal_and_counted_once(self):
        q=m.runtime.request(x.inventory.root(),[x.inventory.sale('one'),x.inventory.sale('over','2/1'),x.inventory.sale('later')])
        with m.Store(self.path,q) as store:
            result=store.advance(10);self.assertEqual(result['cursor'],2);self.assertEqual(len(result['result']['trace']),1)
            self.assertEqual(result['result'],m.runtime.run(q));self.assertEqual(store.advance(10),result)
        with m.Store(self.path,q) as store:self.assertEqual(store.inspect(),result)

    def test_unavailable_root_is_terminal(self):
        q=self.request();q['root_request']['operations'].append({'kind':'unknown','event':{}});q['root_sha256']=m.digest(q['root_request'])
        with m.Store(self.path,q) as store:
            initial=store.inspect();self.assertEqual(initial['cursor'],0);self.assertEqual(initial['result'],m.runtime.run(q))
            self.assertEqual(store.advance(10),initial)

    def test_incompatible_database_is_unchanged(self):
        with sqlite3.connect(self.path) as db:db.execute('CREATE TABLE unrelated(value TEXT)');db.execute("INSERT INTO unrelated VALUES('keep')")
        before=sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(m.Invalid):m.Store(self.path,self.request())
        self.assertEqual(sha256(self.path.read_bytes()).hexdigest(),before)

    def test_changed_request_including_future_operations_rejects(self):
        q=self.request()
        with m.Store(self.path,q) as store:store.advance(1)
        changed=deepcopy(q);changed['operations'][1]['event']['proceeds']='20/1'
        with self.assertRaisesRegex(m.Invalid,'request_mismatch'):m.Store(self.path,changed)

    def test_corrupt_hash_and_rehashed_balances_reject(self):
        q=self.request()
        for rehash in [False,True]:
            path=Path(self.tmp.name)/('rehash.sqlite' if rehash else 'corrupt.sqlite')
            with m.Store(path,q) as store:store.advance(1)
            with sqlite3.connect(path) as db:
                db.execute('DROP TRIGGER checkpoints_no_update')
                raw=db.execute('SELECT payload FROM checkpoints WHERE seq=1').fetchone()[0];value=json.loads(raw)
                value['period_book']['after']['balances']['cash']='999/1'
                if rehash:db.execute('UPDATE checkpoints SET payload=?,result_sha256=? WHERE seq=1',(m.canonical(value),m.digest(value)))
                else:db.execute('UPDATE checkpoints SET payload=? WHERE seq=1',(m.canonical(value),))
                db.execute("CREATE TRIGGER checkpoints_no_update BEFORE UPDATE ON checkpoints BEGIN SELECT RAISE(ABORT,'immutable checkpoint'); END")
            with self.assertRaisesRegex(m.Invalid,'checkpoint_replay' if rehash else 'checkpoint_digest'):m.Store(path,q)

    def test_schema_and_source_binding_drift_reject(self):
        q=self.request()
        with m.Store(self.path,q):pass
        with sqlite3.connect(self.path) as db:db.execute('PRAGMA user_version=99')
        with self.assertRaisesRegex(m.Invalid,'schema_version'):m.Store(self.path,q)
        with sqlite3.connect(self.path) as db:
            db.execute('PRAGMA user_version=1');db.execute('DROP TRIGGER metadata_no_update')
            row=json.loads(db.execute('SELECT payload FROM metadata').fetchone()[0]);row['binding']['source_lock_sha256']='0'*64
            db.execute('UPDATE metadata SET payload=?',(m.canonical(row),))
            db.execute("CREATE TRIGGER metadata_no_update BEFORE UPDATE ON metadata BEGIN SELECT RAISE(ABORT,'immutable metadata'); END")
        with self.assertRaisesRegex(m.Invalid,'source_binding'):m.Store(self.path,q)

    def test_budgets_and_cursor_types_reject(self):
        with m.Store(self.path,self.request()) as store:
            for bad in [True,-1,4097,1.5]:
                with self.assertRaises(m.Invalid):store.advance(bad)
            for bad in [True,-1,1,1.5]:
                with self.assertRaises(m.Invalid):store.advance(1,expected_cursor=bad)

    def test_native_step_uses_current_state_without_root_reexecution(self):
        q=self.request()
        with m.Store(self.path,q) as store:
            with patch.object(m.runtime,'run',side_effect=AssertionError('full replay')),patch.object(m.annual.root,'run',side_effect=AssertionError('root replay')):
                self.assertEqual(store.advance(1)['cursor'],1)

    def test_unicode_input_and_return_values_are_isolated(self):
        q=m.runtime.request(x.inventory.root(),[x.inventory.sale('售出一件')]);before=m.canonical(q)
        with m.Store(self.path,q) as store:
            out=store.advance(1);out['result']['period_book']['after']['balances']['cash']='999/1'
            self.assertEqual(store.inspect()['result']['period_book']['after']['balances']['cash'],'467/1')
        self.assertEqual(m.canonical(q),before)
        with m.Store(self.path,q) as store:self.assertEqual(store.current,m.runtime.run(q))

    def test_json_preserves_unicode_and_rejects_ambiguous_numbers(self):
        self.assertEqual(m.strict_loads(m.canonical({'x':'é','y':'é'})),{'x':'é','y':'é'})
        for raw in ['{"a":1,"a":2}','{"a":1.0}','{"a":NaN}','{"a":-0}','{ "a":1}']:
            with self.assertRaises(ValueError):m.strict_loads(raw)

if __name__=='__main__':unittest.main()
