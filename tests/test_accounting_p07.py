"""Public API recovery/review tests, with actual P05 engine as comparator."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import json
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import company_persistence_v1 as p
from company_execution_v1 import Engine, ROOT, INPUT, event, execute_period, serial
from check_accounting_p05 import verify

SPEC = json.loads((ROOT / INPUT).read_text())
REVIEW = {'reviewer':'local-test-analyst', 'time':'2026-10-03T03:00:00+00:00',
          'rationale':'checked retained fixture literal', 'applicability':'synthetic Northstar revenue',
          'reconciliation':'direct literal/value equality; economic effects checked separately'}


def legacy_copy(source, destination):
    """Real schema-1 fixture: text payloads and digests, no canonical column."""
    src = sqlite3.connect(source); dst = sqlite3.connect(destination)
    dst.executescript(p.SCHEMA.replace(', canonical TEXT NOT NULL', ''))
    for table in ('nodes','edges','head','requests','runs','commits','migrations'):
        columns = [r[1] for r in src.execute('PRAGMA table_info('+table+')') if r[1] != 'canonical']
        names = ','.join(columns)
        for row in src.execute('SELECT '+names+' FROM '+table):
            dst.execute('INSERT INTO '+table+' ('+names+') VALUES('+','.join('?' for _ in row)+')', row)
    p.install_triggers(dst)
    dst.execute('PRAGMA user_version=1');dst.commit();src.close();dst.close()


class P07Tests(unittest.TestCase):
    def setUp(self):
        self.observations = []
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'store.db'
        self.store = p.Store(self.path); self.addCleanup(lambda: self.store.close())
        self.spec = deepcopy(SPEC)

    def create(self, **kw):
        return self.store.create_run(self.spec, **kw)['run_id']

    def complete(self, run):
        for period in self.spec['periods']:
            result = self.store.execute_period(run, period['id'])
            self.assertEqual(result['status'], 'Complete', result)
            self.assertTrue(verify(result)['passed'])
        return self.store.freeze_result(run)

    def reopen(self):
        self.store.close(); self.store = p.Store(self.path)

    def error(self, code, operation):
        with self.assertRaises(p.P07Error) as caught: operation()
        self.assertEqual(caught.exception.code, code)

    def reading(self, literal='120', value=None, **kw):
        file = Path(self.tmp.name) / ('source-'+literal+'.txt')
        file.write_text('Revenue '+literal+' units\n')
        source = self.store.add_source(file)
        return self.store.propose({'source':source,'start':8,'end':8+len(literal),'literal':literal,
            'value': value or literal, 'concept':'revenue','period':'2024H1','context':self.spec['context'],
            'lineage':'northstar-revenue','layer':'extraction','available':'2024-08-01T00:00:00+00:00',
            'ingested':'2024-08-02T00:00:00+00:00','historical_byte_vintage':'unknown', **kw})

    def accept(self, reading, action='Accepted', **kw):
        return self.store.review(reading, action, REVIEW, prior_view=self.store.view,
            request_id=p.identity('test-request',[reading,action,kw,self.store.view]), **kw)

    def test_full_company_matches_independent_p05_verifier_and_restarts(self):
        baseline = Engine(self.spec); expected = {}
        for period in self.spec['periods']:
            expected[period['id']] = execute_period(baseline, self.spec, period)
        run = self.create()
        for i in range(32):
            self.assertEqual(self.store.apply_event(run)['status'], 'Applied')
            self.reopen()
            self.assertEqual(self.store.resume_run(run)['cursor'], i+1)
        self.assertEqual(self.store.resume_run(run)['state'], baseline.snapshot())
        for period, reference in expected.items():
            actual = self.store.execute_period(run, period)
            for key in ('inputs','events','opening','journals','statements'):
                self.assertEqual(actual[key], reference[key], key)
            self.assertTrue(verify(actual)['passed'])
        self.assertEqual(self.store.integrity(), {'integrity':'ok','foreign_keys':[]})

    def test_every_transaction_component_rolls_back_and_replays(self):
        run = self.create(); before = self.store.resume_run(run)['state']
        for point in p.FAULT_POINTS[:-1]:
            count = self.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
            def fault(at):
                if at == point: raise RuntimeError('injected '+at)
            self.store.fault = fault
            outcome = self.store.apply_event(run)
            self.assertEqual(outcome['status'], 'InternalFailure')
            self.reopen()
            resumed = self.store.resume_run(run)
            self.assertEqual(resumed['state'], before)
            self.assertEqual(self.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0], count)
            self.observations.append({'fault':point,'status':outcome['status'],'cursor':resumed['cursor'],
                'before_state_sha256':p.identity('state',before),
                'after_state_sha256':p.identity('state',resumed['state']),
                'node_count_before':count,'node_count_after':self.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]})
        self.assertEqual(self.store.apply_event(run)['status'], 'Applied')

    def test_foreground_process_kill_before_and_after_commit(self):
        run = self.create(); lock = self.store.resume_run(run)['lock']
        script = """import os,signal,sys
sys.path.insert(0,sys.argv[1])
from company_persistence_v1 import Store
def fault(point):
 if point==sys.argv[4]: os.kill(os.getpid(),signal.SIGKILL)
with Store(sys.argv[2],fault=fault) as db: db.apply_event(sys.argv[3])
"""
        for point, expected in [('before_commit',0),('after_commit',1)]:
            child = subprocess.run([sys.executable,'-B','-c',script,str(ROOT/'scripts'),str(self.path),run,point],
                timeout=15, capture_output=True, env={**os.environ,'CUDA_VISIBLE_DEVICES':'-1'})
            self.assertEqual(child.returncode,-signal.SIGKILL,child.stderr.decode())
            self.reopen();self.assertEqual(self.store.resume_run(run)['cursor'],expected)
            resumed = self.store.resume_run(run)
            self.observations.append({'fault':point,'process_returncode':child.returncode,
                'cursor':resumed['cursor'],'state_sha256':p.identity('state',resumed['state'])})
        retry = self.store.apply_event(run,lock['schedule'][0]['event_id'])
        self.assertEqual(retry['status'],'Duplicate');self.assertEqual(retry['receipt']['status'],'Applied')
        self.complete(run)

    def test_retry_conflict_locks_and_closed_period_no_mutation(self):
        run = self.create(); result = self.store.apply_event(run)
        before = self.store.resume_run(run)
        self.assertEqual(self.store.apply_event(run,result['event_id'])['receipt'],result['receipt'])
        changed = deepcopy(before['lock']['schedule'][0]['event']);changed['params']['units']='999'
        self.assertEqual(self.store.apply_event(run,result['event_id'],changed)['status'],'Conflict')
        lock = deepcopy(before['lock']);lock['scenario']='changed'
        self.error('Conflict',lambda:self.store.resume_run(run,expected_lock=lock))
        self.assertEqual(self.store.resume_run(run),before)
        schedule = [{'event':event(self.spec,'close','close',{}),'dynamic':None},
                    {'event':event(self.spec,'late','purchase',{'units':'1'},depends=['close']),'dynamic':None}]
        other=self.create(schedule=schedule);self.assertEqual(self.store.apply_event(other)['status'],'Applied')
        old=self.store.resume_run(other)['state'];self.assertEqual(self.store.apply_event(other)['status'],'Rejected')
        self.assertEqual(self.store.resume_run(other)['state'],old)

    def test_dynamic_settlements_resume_committed_payload(self):
        del self.spec['periods'][0]['tax_payment']
        run=self.create()
        for _ in range(13):self.assertEqual(self.store.apply_event(run)['status'],'Applied')
        rows=self.store.db.execute('SELECT event_id,payload FROM commits WHERE run_id=? ORDER BY seq',(run,)).fetchall()
        payment=json.loads(rows[10]['payload']);self.assertNotEqual(payment['params']['amount'],'0')
        self.reopen();self.assertEqual(self.store.apply_event(run,rows[10]['event_id'],payment)['status'],'Duplicate')
        self.complete(run)

    def test_schedule_conflicts_cycles_missing_and_ambiguous(self):
        a=event(self.spec,'a','purchase',{'units':'1'});b=event(self.spec,'b','purchase',{'units':'1'})
        def rows(*es):return [{'event':x,'dynamic':None} for x in es]
        self.error('Conflict',lambda:self.create(schedule=rows(a,a)))
        self.error('Unsupported',lambda:self.create(schedule=rows(a,b)))
        a['depends']=['b'];b['depends']=['a']
        self.error('Rejected',lambda:self.create(schedule=rows(a,b)))
        self.error('Rejected',lambda:self.create(schedule=rows(a)))
        self.error('MissingReference',lambda:self.store.add_node('calc',{},['missing']))
        x=self.store.add_node('calc',{},identifier='x');y=self.store.add_node('calc',{},[x],identifier='y')
        self.error('Conflict',lambda:self.store.add_node('calc',{},[y],identifier='x'))

    def test_funding_and_unsupported_operation_preserve_state(self):
        for op,params,status in [('dividend_declare',{'amount':'999'},'Applied'),('unsupported',{},'Unsupported')]:
            e=event(self.spec,op,op,params);run=self.create(schedule=[{'event':e,'dynamic':None}])
            before=self.store.resume_run(run)['state'];r=self.store.apply_event(run);self.assertEqual(r['status'],status)
            if status!='Applied':self.assertEqual(before,self.store.resume_run(run)['state'])
        a=event(self.spec,'declare','dividend_declare',{'amount':'999'})
        b=event(self.spec,'pay','dividend_pay',{'amount':'999'},depends=['declare'])
        run=self.create(schedule=[{'event':e,'dynamic':None} for e in [a,b]])
        self.store.apply_event(run);before=self.store.resume_run(run)['state']
        self.assertEqual(self.store.apply_event(run)['status'],'EconomicFundingDefault')
        self.assertEqual(before,self.store.resume_run(run)['state'])
        self.error('Rejected',lambda:self.store.freeze_result(run))

    def test_canonical_branch_event_stream_contract(self):
        self.assertEqual(p.canonical({'b':2,'a':'e\u0301'}),p.canonical({'a':'é','b':Fraction(4,2)}))
        self.assertEqual(p.identity('x',{'dependencies':['b','a']}),p.identity('x',{'dependencies':['a','b']}))
        for bad in ['{"x":1,"x":2}','{"x":-0}','{"x":1.5}','{"é":1,"é":2}']:
            self.error('CanonicalError',lambda b=bad:p.strict_loads(b))
        self.error('CanonicalError',lambda:p.canonical(1.2))
        self.error('CanonicalError',lambda:p.canonical({'dependencies':['a','a']}))
        branches=[{'h':'one'},{'h':'two'}]
        self.assertEqual(sorted(p.branch_identity(h,{'s':'up'}) for h in branches),sorted(p.branch_identity(h,{'s':'up'}) for h in reversed(branches)))
        a=event(self.spec,'alias','purchase',{'units':'1'});b=deepcopy(a);b['params']['units']='2'
        self.assertEqual(p.event_identity('Northstar','v1',a),p.event_identity('Northstar','v1',b))
        args=[7,'joint','Northstar','debt','2024-06-30','rate',0];u=p.reference_uniform(*args)
        self.assertTrue(0<u<1);self.assertEqual(u,p.reference_uniform(*args))
        args[-2]='default';self.assertNotEqual(u,p.reference_uniform(*args))
        self.assertEqual(self.store.create_run(self.spec,stream='monte-carlo')['status'],'Unsupported')
        ordered=p.make_schedule(self.spec)
        self.assertEqual(p.order_schedule(ordered),p.order_schedule(list(reversed(ordered))))

    def test_review_requirements_idempotency_and_invalid_transitions(self):
        reading=self.reading();prior=self.store.view
        self.error('Rejected',lambda:self.store.review(reading,'Accepted',{},prior_view=prior,request_id='bad'))
        self.error('Rejected',lambda:self.accept(reading,'AcceptedAlternative'))
        r=self.store.review(reading,'Accepted',REVIEW,prior_view=prior,request_id='ok')
        self.assertEqual(r,self.store.review(reading,'Accepted',REVIEW,prior_view=prior,request_id='ok'))
        self.error('Conflict',lambda:self.store.review(reading,'Rejected',REVIEW,prior_view=prior,request_id='ok'))
        self.error('Conflict',lambda:self.store.review(reading,'Rejected',REVIEW,prior_view=prior,request_id='stale'))
        self.error('Rejected',lambda:self.accept(reading,'Rejected'))
        interpreted=self.reading(layer='interpretation')
        self.error('Rejected',lambda:self.accept(interpreted))
        mismatch=self.reading(literal='120',start=0)
        self.error('Rejected',lambda:self.accept(mismatch))

    def test_self_supersession_rejected_without_mutation(self):
        reading = self.reading()
        self.accept(reading)
        view = self.store.view
        before = list(self.store.db.iterdump())
        self.error('Rejected', lambda: self.accept(reading, 'Superseded', replacement=reading))
        self.assertEqual(list(self.store.db.iterdump()), before)
        self.reopen()
        self.assertEqual(self.store.view, view)
        self.assertEqual(self.store.node(view)['states'][reading]['state'], 'Accepted')
        self.assertEqual(self.store.select(view, '2025-01-01T00:00:00+00:00')['selected_ids'], [reading])

    def test_extraction_repair_then_reported_correction_transitive_history(self):
        wrong=self.reading(value='720');self.error('Rejected',lambda:self.accept(wrong))
        derived=self.store.add_node('mapping',{'provisional':True},[wrong])
        repair=self.accept(wrong,'Rejected');self.assertIn(derived,repair['invalidated'])
        original=self.reading(correction_of=wrong);self.accept(original)
        oldview=self.store.view
        spec,calc=self.store.bind_reading(original,oldview,self.spec,'2024H1')
        oldspec=self.spec;self.spec=spec;run=self.create(dependencies=[calc]);report=self.complete(run);self.spec=oldspec
        unrelated=self.store.add_node('report',{'value':'unrelated'},identifier='unrelated')
        historical=self.store.result(report,oldview)
        corrected=self.reading('110',available='2025-03-01T00:00:00+00:00',ingested='2025-03-02T00:00:00+00:00')
        self.accept(corrected)
        before=self.store.descendants([original]);result=self.accept(original,'Superseded',replacement=corrected)
        self.assertEqual(set(before),set(result['invalidated']))
        self.assertIn(calc,result['invalidated']);self.assertIn(run,result['invalidated']);self.assertIn(report,result['invalidated'])
        self.assertNotIn(unrelated,result['invalidated']);self.assertEqual(self.store.result(unrelated),{'value':'unrelated'})
        self.error('StaleResult',lambda:self.store.result(report))
        late_report=self.store.add_node('report',{'late':True},[run])
        self.error('StaleResult',lambda:self.store.result(late_report))
        self.assertEqual(self.store.result(report,oldview),historical)
        self.assertEqual(self.store.resume_run(run)['state'],historical['state'])
        selection=self.store.select(self.store.view,'2024-09-01T00:00:00+00:00')
        self.assertEqual(selection['selected_ids'],[original]);self.assertTrue(selection['unresolved'])
        latest=self.store.select(self.store.view,'2025-04-01T00:00:00+00:00')
        self.assertEqual(latest['selected_ids'],[corrected])
        new_spec,new_calc=self.store.bind_reading(corrected,self.store.view,self.spec,'2024H1')
        self.spec=new_spec;newrun=self.create(dependencies=[new_calc]);newreport=self.complete(newrun)
        self.assertNotEqual(historical['periods']['2024H1']['statements'],self.store.result(newreport)['periods']['2024H1']['statements'])

    def test_alternatives_contradictions_and_unknown_availability(self):
        a=self.reading();b=self.reading('110');self.accept(a,'AcceptedAlternative',choice_group='revenue-choice');self.accept(b,'AcceptedAlternative',choice_group='revenue-choice')
        selected=self.store.select(self.store.view,'2025-04-01T00:00:00+00:00')
        self.assertEqual(selected['conflicts'],[sorted([a,b])]);self.assertEqual(len(selected['choice_groups']),2)
        c=self.reading('125',available=None);self.accept(c)
        selected=self.store.select(self.store.view,'2025-04-01T00:00:00+00:00')
        self.assertNotIn(c,selected['selected_ids']);self.assertTrue(any(x['id']==c for x in selected['unresolved']))

    def test_export_failure_preserves_prior_file_and_frozen_result(self):
        run=self.create();report=self.complete(run);target=Path(self.tmp.name)/'report.json'
        target.write_text('previous export')
        self.store.fault=lambda point: (_ for _ in ()).throw(RuntimeError('export interrupted')) if point=='export' else None
        with self.assertRaises(RuntimeError):self.store.export(report,target)
        self.assertEqual(target.read_text(),'previous export');self.assertFalse(target.with_name('report.json.partial').exists())
        self.store.fault=None;self.store.export(report,target)
        self.assertEqual(json.loads(target.read_text()),self.store.result(report))

    def test_migration_success_failure_repeat_and_replay(self):
        run=self.create();self.store.apply_event(run);expected=self.store.resume_run(run)
        legacy=Path(self.tmp.name)/'legacy.db';legacy_copy(self.path,legacy)
        self.error('MigrationRequired',lambda:p.Store(legacy))
        def fault(_):raise RuntimeError('migration interrupted')
        with self.assertRaises(RuntimeError):p.migrate(legacy,fault=fault)
        con=sqlite3.connect(legacy);self.assertEqual(con.execute('PRAGMA user_version').fetchone()[0],1)
        self.assertNotIn('canonical',[r[1] for r in con.execute('PRAGMA table_info(nodes)')]);con.close()
        with sqlite3.connect(legacy) as db:
            self.assertIsNotNone(db.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND name='immutable_nodes_UPDATE'").fetchone())
        self.error('SemanticChange',lambda:p.migrate(legacy,transform=lambda value:{'changed':value}))
        result=p.migrate(legacy);self.assertEqual(result['status'],'Migrated');self.assertTrue(result['mappings'])
        self.assertTrue(all(m['old_id']==m['new_id'] and m['original_payload'] for m in result['mappings']))
        self.assertEqual(p.migrate(legacy)['status'],'AlreadyCurrent')
        with p.Store(legacy) as store:
            self.assertEqual(store.resume_run(run),expected);self.assertEqual(store.integrity()['integrity'],'ok')
            self.assertEqual(store.apply_event(run)['status'],'Applied')
        unknown=Path(self.tmp.name)/'unknown.db';con=sqlite3.connect(unknown);con.execute('PRAGMA user_version=99');con.close()
        self.error('Unsupported',lambda:p.Store(unknown));self.error('Unsupported',lambda:p.migrate(unknown))

    def test_source_hash_and_immutable_store_guards(self):
        reading=self.reading();source=self.store.node(self.store.node(reading)['source'])
        with self.assertRaises(sqlite3.IntegrityError):self.store.db.execute('UPDATE nodes SET payload=? WHERE id=?',('{}',reading))
        Path(source['path']).write_text('altered')
        self.error('IntegrityFailure',self.store.verify_sources)

    def test_checker_missing_obligation_and_protected_hash_veto(self):
        from check_accounting_p07 import check_coverage, protected_check
        with self.assertRaises(AssertionError):check_coverage([],True)
        with self.assertRaises(AssertionError):check_coverage([],False)
        with self.assertRaises(AssertionError):protected_check({INPUT:'0'*64})
        report = protected_check({INPUT:p.file_hash(ROOT/INPUT),
            'scripts/check_accounting_p07.py':'0'*64})
        self.assertEqual(report['files_checked'], 1)
        self.assertEqual(report['inventory_entries'], 2)

    def test_git_provenance_available(self):
        from check_accounting_p07 import git_provenance
        command = ['git', 'rev-parse', '--verify', 'HEAD']
        for commit in ('a1' * 20, 'b2' * 32):
            with self.subTest(commit=commit), patch('check_accounting_p07.subprocess.run',
                    return_value=subprocess.CompletedProcess(command, 0, commit+'\n', '')) as run:
                self.assertEqual(git_provenance(), {'git_commit': commit, 'git_unavailable_reason': None})
                run.assert_called_once_with(command, cwd=ROOT, capture_output=True,
                    encoding='utf-8', errors='replace', timeout=5, check=False)

    def test_git_provenance_unavailable(self):
        from check_accounting_p07 import git_provenance
        command = ['git', 'rev-parse', '--verify', 'HEAD']
        cases = [
            (subprocess.CompletedProcess(command, 128, '', 'fatal: not a git repository\n'), 'exited 128: fatal: not a git repository'),
            (FileNotFoundError('git executable missing'), 'FileNotFoundError: git executable missing'),
            (subprocess.TimeoutExpired(command, 5), 'timed out after 5 seconds'),
            (subprocess.CompletedProcess(command, 0, '\n', ''), 'invalid commit ID'),
        ]
        for outcome, diagnostic in cases:
            with self.subTest(diagnostic=diagnostic), patch('check_accounting_p07.subprocess.run') as run:
                if isinstance(outcome, Exception):
                    run.side_effect = outcome
                else:
                    run.return_value = outcome
                actual = git_provenance()
                self.assertIsNone(actual['git_commit'])
                self.assertIn(diagnostic, actual['git_unavailable_reason'])

    def test_missing_lineage_is_detected_on_resume(self):
        run=self.create();self.store.apply_event(run)
        event_node=self.store.db.execute('SELECT event_node FROM commits WHERE run_id=?',(run,)).fetchone()[0]
        # Deliberate external corruption in a disposable store; normal API forbids deletion.
        self.store.db.execute('DROP TRIGGER immutable_edges_DELETE')
        self.store.db.execute('DELETE FROM edges WHERE parent=? AND child=?',(run,event_node))
        self.error('IntegrityFailure',lambda:self.store.resume_run(run))

    def test_checker_rejects_mutated_journal(self):
        run=self.create();record=self.store.execute_period(run,'2024H1')
        changed=deepcopy(record);changed['journals'][0]['postings'][0]['signed_amount']='999'
        with self.assertRaises(AssertionError):verify(changed)

    def test_rational_storage_and_phase_identity(self):
        value = {'rational': Fraction(-2, 6), 'integer': 7, 'numeric_string': '7'}
        key = self.store.add_node('calculation', value)
        self.reopen()
        self.assertEqual(self.store.node(key), value)
        self.assertEqual(self.store.integrity(), {'integrity':'ok', 'foreign_keys':[]})
        a = event(self.spec, 'same-alias', 'purchase', {'units':'1'})
        b = deepcopy(a); b['phase'] = 'adjustment'
        self.assertNotEqual(p.event_identity('owner','v1',a), p.event_identity('owner','v1',b))
        self.assertEqual(p.identity('fraction', Fraction(1,3)), p.identity('fraction', {'$rational':['2','6']}))

    def test_late_descendants_cannot_reuse_superseded_reading(self):
        old = self.reading(); self.accept(old); oldview = self.store.view
        new = self.reading('110'); self.accept(new)
        self.accept(old, 'Superseded', replacement=new)
        bound, calc = self.store.bind_reading(old, oldview, self.spec, '2024H1')
        before = self.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0]
        self.error('StaleResult', lambda:self.store.create_run(bound, dependencies=[calc]))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM nodes').fetchone()[0], before)
        late_report = self.store.add_node('report', {'late':True}, [old])
        self.error('StaleResult', lambda:self.store.result(late_report))
        self.assertEqual(self.store.result(late_report, oldview), {'late':True})
        run = self.store.create_run(bound, view=oldview, dependencies=[calc])['run_id']
        report = self.complete(run)
        self.assertEqual(self.store.result(report, oldview)['run'], run)
        self.error('StaleResult', lambda:self.store.result(report))

    def test_initialization_faults_roll_back_entire_schema(self):
        for point in ('initial_schema','initial_view','initial_before_commit'):
            path = Path(self.tmp.name)/(point+'.db')
            def fault(at):
                if at == point: raise RuntimeError('initialization interruption')
            with self.assertRaises(RuntimeError): p.Store(path, fault=fault)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 0)
                self.assertEqual(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [])
            with p.Store(path) as store:
                self.assertEqual(store.integrity(), {'integrity':'ok','foreign_keys':[]})
                run = store.create_run(self.spec)['run_id']
                self.assertEqual(store.apply_event(run)['status'], 'Applied')

    def test_output_lineage_and_unrelated_source_isolation(self):
        original = self.reading(); self.accept(original); oldview = self.store.view
        bound, calc = self.store.bind_reading(original, oldview, self.spec, '2024H1')
        run = self.store.create_run(bound, dependencies=[calc])['run_id']
        self.assertEqual(self.store.apply_event(run)['status'], 'Applied')
        row = self.store.db.execute('SELECT * FROM commits WHERE run_id=?',(run,)).fetchone()
        fresh = self.reading('110'); self.accept(fresh)
        correction = self.accept(original, 'Superseded', replacement=fresh)
        for key in ('state_id','journal_id','measurement_id','event_node'):
            self.assertIn(row[key], correction['invalidated'])
        independent = self.create()
        Path(self.store.node(self.store.node(fresh)['source'])['path']).write_text('unrelated damaged source')
        self.assertEqual(self.store.apply_event(independent)['status'], 'Applied')
        self.error('IntegrityFailure', self.store.verify_sources)
        self.store.db.execute('DROP TRIGGER immutable_edges_DELETE')
        self.store.db.execute('DELETE FROM edges WHERE child=?',(row['state_id'],))
        self.error('IntegrityFailure',lambda:self.store.resume_run(run))

    def test_migration_invalid_foreign_key_rolls_back(self):
        run = self.create(); self.store.apply_event(run)
        legacy = Path(self.tmp.name)/'invalid-legacy.db'; legacy_copy(self.path, legacy)
        with sqlite3.connect(legacy) as db:
            db.execute("INSERT INTO edges VALUES('missing-parent',?)", (run,))
        self.error('IntegrityFailure', lambda:p.migrate(legacy))
        with sqlite3.connect(legacy) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertNotIn('canonical', [r[1] for r in db.execute('PRAGMA table_info(nodes)')])

    def test_migration_missing_lineage_rolls_back(self):
        run = self.create(); self.store.apply_event(run)
        legacy = Path(self.tmp.name)/'missing-lineage.db'; legacy_copy(self.path, legacy)
        with sqlite3.connect(legacy) as db:
            db.execute('DROP TRIGGER immutable_edges_DELETE')
            db.execute('DELETE FROM edges WHERE parent=?', (run,))
        self.error('IntegrityFailure', lambda:p.migrate(legacy))
        with sqlite3.connect(legacy) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],1)

    def test_invalid_review_dates_preserve_view(self):
        reading = self.reading(); prior = self.store.view
        for value in ('invalid','2026-10-03T03:00:00', None):
            self.error('Rejected',lambda v=value:self.store.review(reading,'Rejected',
                {**REVIEW,'time':v},prior_view=prior,request_id='invalid-date'))
            self.assertEqual(self.store.view,prior)


if __name__=='__main__':unittest.main()
