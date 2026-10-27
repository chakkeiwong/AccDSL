#!/usr/bin/env python3
"""Executed, fail-closed P07 evidence; never writes prerequisite artifacts."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import tempfile
import time
import unittest
import sys
from datetime import datetime, timezone
from company_execution_v1 import Engine, ROOT, INPUT, execute_period
import company_persistence_v1 as p
from check_accounting_p05 import verify

FILES = ['scripts/company_persistence_v1.py','scripts/check_accounting_p07.py',
         'tests/test_accounting_p07.py','docs/design/spec/review-persistence-profile-v1.md']
OBLIGATIONS = {
 'exact_execution_recovery':['full_company_matches_independent_p05_verifier_and_restarts','dynamic_settlements_resume_committed_payload'],
 'atomic_writes':['every_transaction_component_rolls_back_and_replays','foreground_process_kill_before_and_after_commit','initialization_faults_roll_back_entire_schema'],
 'conflicts_and_failures':['retry_conflict_locks_and_closed_period_no_mutation','schedule_conflicts_cycles_missing_and_ambiguous','funding_and_unsupported_operation_preserve_state'],
 'review_and_invalidation':['review_requirements_idempotency_and_invalid_transitions','self_supersession_rejected_without_mutation','extraction_repair_then_reported_correction_transitive_history','alternatives_contradictions_and_unknown_availability','late_descendants_cannot_reuse_superseded_reading','output_lineage_and_unrelated_source_isolation','invalid_review_dates_preserve_view'],
 'identities_and_streams':['canonical_branch_event_stream_contract','rational_storage_and_phase_identity'],
 'migration':['migration_success_failure_repeat_and_replay','migration_invalid_foreign_key_rolls_back','migration_missing_lineage_rolls_back'],
 'source_and_export_integrity':['source_hash_and_immutable_store_guards','export_failure_preserves_prior_file_and_frozen_result','git_provenance_available','git_provenance_unavailable'],
 'checker_mutation_detection':['checker_rejects_mutated_journal','checker_missing_obligation_and_protected_hash_veto','missing_lineage_is_detected_on_resume']}


def check_coverage(test_ids, success):
    required = {'test_accounting_p07.P07Tests.test_'+n for names in OBLIGATIONS.values() for n in names}
    if not success or not required <= set(test_ids): raise AssertionError('failed tests or missing acceptance obligation')
    return {k:{'passed':True,'tests':['test_'+n for n in v]} for k,v in OBLIGATIONS.items()}


def protected_check(inventory):
    changes=[];checked=0
    for name, expected in inventory.items():
        path=ROOT/name
        if name in FILES or name.startswith('data/accounting-master/deliverables/P07/'): continue
        checked+=1
        if not path.is_file() or p.file_hash(path)!=expected: changes.append(name)
    if changes: raise AssertionError('protected/pre-existing files changed: '+str(changes[:12]))
    return {'passed':True,'files_checked':checked,'inventory_entries':len(inventory),'changed':changes}


def git_provenance():
    """Observe HEAD without changing the repository; file hashes cover dirty work."""
    command = ['git', 'rev-parse', '--verify', 'HEAD']
    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True,
                                   encoding='utf-8', errors='replace', timeout=5,
                                   check=False)
    except subprocess.TimeoutExpired:
        reason = 'git rev-parse --verify HEAD timed out after 5 seconds'
    except OSError as exc:
        reason = f'{type(exc).__name__}: {exc}'[:500]
    else:
        commit = completed.stdout.strip()
        if completed.returncode:
            detail = (completed.stderr.strip() or completed.stdout.strip() or 'no diagnostic')[:500]
            reason = f'git rev-parse --verify HEAD exited {completed.returncode}: {detail}'
        elif len(commit) not in (40, 64) or any(c not in '0123456789abcdefABCDEF' for c in commit):
            reason = f'git rev-parse returned an invalid commit ID: {commit[:100]!r}'
        else:
            return {'git_commit': commit, 'git_unavailable_reason': None}
    return {'git_commit': None, 'git_unavailable_reason': reason}


def suites():
    stream=io.StringIO();ids=[];observations={}
    class Recorded(unittest.TextTestResult):
        def startTest(self,test):ids.append(test.id());super().startTest(test)
        def addSuccess(self,test):
            if getattr(test,'observations',None): observations[test.id()] = test.observations
            super().addSuccess(test)
    suite=unittest.TestSuite()
    loader=unittest.TestLoader()
    for pattern in ('test_accounting_p07.py','test_accounting_p0[3-6].py'):
        suite.addTests(loader.discover(str(ROOT/'tests'),pattern=pattern))
    result=unittest.TextTestRunner(stream=stream,verbosity=1,resultclass=Recorded).run(suite)
    return {'count':result.testsRun,'passed':result.wasSuccessful() and not result.skipped,
            'test_ids':ids,'failures':[{'id':t.id(),'detail':e} for t,e in result.failures+result.errors],
            'skipped':[(t.id(),r) for t,r in result.skipped],'observations':observations},stream.getvalue()


def execution_evidence(directory):
    spec=json.loads((ROOT/INPUT).read_text());baseline=Engine(spec);expected={}
    for period in spec['periods']:expected[period['id']]=execute_period(baseline,spec,period)
    outputs=[];run_ids=[]
    for mode in ('uninterrupted','reopened'):
        path=directory/(mode+'.db');store=p.Store(path);run=store.create_run(spec)['run_id'];run_ids.append(run)
        for i in range(32):
            result=store.apply_event(run);assert result['status']=='Applied',result
            if mode=='reopened':store.close();store=p.Store(path)
        state=store.resume_run(run)['state'];assert state==baseline.snapshot()
        periods={pid:store.period_result(run,pid) for pid in expected}
        for pid, actual in periods.items():
            for key in ('inputs','events','opening','journals','statements'):assert actual[key]==expected[pid][key],key
            assert verify(actual)['passed']
        commits=[dict(r) for r in store.db.execute('SELECT * FROM commits ORDER BY seq')]
        edges=[list(r) for r in store.db.execute('SELECT parent,child FROM edges ORDER BY parent,child')]
        report=store.freeze_result(run);assert store.result(report)['state']==state
        outputs.append({'state':state,'periods':periods,'commits':commits,'lineage':edges,'integrity':store.integrity()})
        store.close()
    assert outputs[0]==outputs[1], 'uninterrupted/reopened receipts or lineage differ'
    # A real executed legacy fixture, not a marker-only schema bump.
    sys.path.insert(0,str(ROOT/'tests'))
    from test_accounting_p07 import legacy_copy, REVIEW
    legacy=directory/'legacy.db';legacy_copy(directory/'uninterrupted.db',legacy)
    migration=p.migrate(legacy)
    with p.Store(legacy) as store:
        assert store.resume_run(run_ids[0])['state']==baseline.snapshot()
        integrity=store.integrity()
    # Preserve an actual correction graph and computed P05 outcomes.
    with p.Store(directory/'review.db') as store:
        def reading(value, correction=None):
            sourcefile=directory/(value+'.txt');sourcefile.write_text(value)
            source=store.add_source(sourcefile)
            return store.propose({'source':source,'start':0,'end':len(value),'literal':value,'value':value,
                'context':spec['context'],'concept':'revenue','period':'2024H1','lineage':'revenue','layer':'extraction',
                'available':'2025-03-01T00:00:00+00:00' if correction else '2024-08-01T00:00:00+00:00',
                'correction_of':correction})
        old=reading('120');store.review(old,'Accepted',REVIEW,prior_view=store.view,request_id='accept-old')
        oldview=store.view;bound,calc=store.bind_reading(old,oldview,spec,'2024H1')
        oldrun=store.create_run(bound,dependencies=[calc])['run_id']
        for period in bound['periods']:store.execute_period(oldrun,period['id'])
        report=store.freeze_result(oldrun);historical=store.result(report,oldview)
        unrelated=store.add_node('report',{'unrelated':'retained'})
        new=reading('110',old);store.review(new,'Accepted',REVIEW,prior_view=store.view,request_id='accept-new')
        expected_closure=store.descendants([old])
        corrected=store.review(old,'Superseded',REVIEW,prior_view=store.view,request_id='supersede',replacement=new)
        assert corrected['invalidated']==expected_closure and report in expected_closure and unrelated not in expected_closure
        assert store.result(report,oldview)==historical
        try:store.result(report)
        except p.P07Error as exc:assert exc.code=='StaleResult'
        else:raise AssertionError('stale result reused')
        revised, newcalc = store.bind_reading(new, store.view, spec, '2024H1')
        revised_run = store.create_run(revised, dependencies=[newcalc])['run_id']
        revised_periods = {}
        for period in revised['periods']:
            actual = store.execute_period(revised_run, period['id'])
            assert actual['status'] == 'Complete' and verify(actual)['passed']
            revised_periods[period['id']] = actual
        revised_report = store.freeze_result(revised_run)
        assert store.result(revised_report)['periods'] == revised_periods
        assert historical['periods']['2024H1']['statements'] != revised_periods['2024H1']['statements']
        assert store.result(report, oldview) == historical
        correction={'old_reading':old,'new_reading':new,'old_view':oldview,'new_view':store.view,
            'mapping_calculation':calc,'run':oldrun,'report':report,'invalidated':corrected['invalidated'],
            'unrelated_retained':store.result(unrelated),'historical_sha256':p.identity('historical',historical),
            'corrected_run':revised_run,'corrected_report':revised_report,'corrected_periods':revised_periods,
            'corrected_result_sha256':p.identity('historical',store.result(revised_report))}
    return {'passed':True,'baseline_state_sha256':p.identity('state',baseline.snapshot()),
        'persistent_result_sha256':p.identity('comparison',outputs[0]),'interrupted_result_sha256':p.identity('comparison',outputs[1]),
        'event_count':32,'actual_result':outputs[0], 'migration':migration,'migration_integrity':integrity,'correction':correction}


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',default='data/accounting-master/deliverables/P07')
    parser.add_argument('--approved-plan',required=True);parser.add_argument('--execution-inventory',required=True)
    args=parser.parse_args(argv);started=time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU-only environment must hide GPUs'
    approved=ROOT/args.approved_plan;inventory=ROOT/args.execution_inventory
    plan=json.loads(approved.read_text());assert plan['review']['verdict']=='AGREE' and not plan['review']['issues']
    protected=protected_check(json.loads(inventory.read_text()))
    tests,log=suites();coverage=check_coverage(tests['test_ids'],tests['passed'])
    with tempfile.TemporaryDirectory(prefix='accdsl-p07-check-') as d:comparisons=execution_evidence(Path(d))
    protected_check(json.loads(inventory.read_text()))
    result={'schema_version':'accdsl.p07.recovery.v1','status':'passed','requirements':['MC04','MC25','MC27','MC34'],
      'obligation_coverage':coverage,'tests':tests,'comparison':comparisons,'protected_files':protected,
      'fault_outcomes':{'observed_tests':tests['observations'],
          'process_scope':'foreground SIGKILL, 15-second subprocess timeout'},
      'acceptance':{'engineering':'bounded conformance passed','accounting':'not established','forecast':'not established','human':'pending','G17_G18':'wider obligations remain'},
      'manifest':{**git_provenance(),
          'command':['CUDA_VISIBLE_DEVICES=-1',sys.executable,'-B','scripts/check_accounting_p07.py',*sys.argv[1:]],
          'python':sys.version,'platform':platform.platform(),'environment':sys.executable,
          'gpu':'intentionally hidden with CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A deterministic; reference tuple seed 7 is identity-only',
          'created_at':datetime.now(timezone.utc).isoformat(),'wall_seconds':round(time.monotonic()-started,3),
          'plan_file':args.approved_plan,'plan_sha256':p.file_hash(approved),'approved_plan_hash':plan['plan_hash'],
          'inventory_file':args.execution_inventory,'inventory_sha256':p.file_hash(inventory),
          'inputs':{INPUT:p.file_hash(ROOT/INPUT)},'changed_source_code_test_files':{f:p.file_hash(ROOT/f) for f in FILES},
          'output_artifacts':[str(Path(args.output_dir)/'recovery.json'),str(Path(args.output_dir)/'result.md')]}}
    out=ROOT/args.output_dir;out.mkdir(parents=True,exist_ok=True)
    (out/'recovery.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    git_note = (f"Git HEAD: `{result['manifest']['git_commit']}`."
                if result['manifest']['git_commit'] else
                f"Git HEAD unavailable: {result['manifest']['git_unavailable_reason']}.")
    (out/'result.md').write_text(f'''# P07 executed result

Bounded engineering conformance passed: {tests['count']} tests, exact P05 comparison,
32 reopened event boundaries, transaction faults and killed writers before/after
commit. SQLite integrity and foreign-key checks passed. The evidence file retains
actual state, ordered journals, receipts, dependency edges, migration mappings and
correction descendants. All {protected['files_checked']} protected pre-existing
files match the supplied {protected['inventory_entries']}-entry inventory; permitted
P07 phase files are excluded from the protection check.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Submit for independent review | Exact real P05/persistent/reopened equivalence passed | Rollback, retry, source hashes, stale reuse and migration checks passed | Filesystem/hardware failures beyond process interruption | Independent result review | Production durability, accounting or forecast validity |

The actual 120-to-110 correction preserves the original report and invalidates
its transitive dependents. Tests separately reject the 720 extraction against a
120 literal and retain its correction link. Accepted alternatives remain visible
as conflict sets, with explicit choice groups. Availability is selected by P06;
unknown source availability is not inferred. New descendants of stale runs are
also denied current-view reuse, including dependencies created after the review
decision directly from superseded readings. Historical replay remains available.
Self-supersession is rejected before mutation; the accepted reading and evidence
view remain usable after reopening the store.
State, journal and measurement nodes are included in the invalidation closure.
Canonical rational payloads survive persistence and reopening. Explicit phases
separate event identities; P05 events use the documented P05-period-step phase.

The schema-1 fixture contains a real executed run. Migration adds canonical
payloads transactionally, retaining original text, digests, IDs and mappings.
Injected failure and semantic changes roll back; repeated migration is idempotent.
Legacy immutable triggers are restored transactionally. Foreign-key failures and
missing execution lineage veto migration before commit. Interrupted initial store
creation rolls back the entire schema, and a subsequent open recovers normally.
Source verification follows each run's dependencies, preserving unrelated runs
when an unrelated retained source fails verification. Fault outcomes in the JSON
are observations captured from executed tests, including process exit codes,
committed cursors and before/after state hashes.
Production stochastic execution is Unsupported. Reference hash tuple checks
establish identity and domain separation only.

Strongest alternative explanation: the bounded P05 fixture omits many real-company
operations and shares its engine with the adapter. The independent journal and
statement verifier checks the economic outputs separately, but does not establish
professional treatment validity. A mismatch on another supported schedule, a
partial commit or historical payload drift would overturn acceptance. Hardware
power loss, multiple writers, general accounting, forecast validity and human
acceptance remain untested. No stochastic-method ranking is made.

Changed implementation files: {', '.join(FILES)}. Exact hashes, command,
environment, approved plan and input hashes are in recovery.json. No prior release
or master-control file was changed. MC01–MC35 and wider G1–G18 remain active.
{git_note} Content hashes identify the checked files, including uncommitted work;
HEAD alone does not identify the executed implementation.
''')
    print(json.dumps({'status':'passed','tests':tests['count'],'events':32,'artifacts':[str(out/'recovery.json'),str(out/'result.md')]}))
    return 0

if __name__=='__main__':raise SystemExit(main())
