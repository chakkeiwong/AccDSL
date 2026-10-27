"""Control-plane fault injection; these tests make no accounting-validity claim."""
from contextlib import redirect_stdout
import io
import hashlib
import json
import os
import signal
import subprocess
from pathlib import Path
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from accounting_master_support import atomic_json, digest, load_json, local_path, run_phase_tests, preserve_editable, merge_hashes, phase_recovery
from run_accounting_master import (ACCEPTED, CATALOG, Master, MasterError, ContinuationVeto, bounded_process,
                                  exclusive_lock, rule_text, validate_catalog, validate_response,
                                  process_identity, terminate_group, worker_overrides,
                                  validate_internal, atomic_rule_publish, stop_recovered_group)
from run_accounting_master import catch_termination, boot_identity
from run_accounting_master import install_rule, worker_seconds, ProcessTimeout, git_provenance


def response(verdict, **kwargs):
    result = {'verdict': verdict, 'summary': 'Bounded control-plane test response',
              'steps': ['Perform the registered work'], 'assumptions': ['Synthetic test only'],
              'checks': ['Inspect actual generated value'], 'evidence': [], 'issues': [],
              'residuals': ['The wider mission remains open'], 'next_actions': ['Use observed evidence in the next plan']}
    result.update(kwargs)
    return result


class MasterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'tests').mkdir()
        schema = Path(__file__).resolve().parents[1] / 'scripts/accounting_master_response.schema.json'
        (self.root / 'scripts/accounting_master_response.schema.json').write_bytes(schema.read_bytes())
        self.catalog = {'limits': {'phase_seconds': 5, 'review_seconds': 5, 'plan_seconds': 5, 'max_repairs': 2}, 'phases': []}
        for i in range(3):
            self.catalog['phases'].append({'id': f'P0{i}', 'name': f'Phase {i}', 'kind': 'worker',
                'deps': [] if i == 0 else [f'P0{i-1}'], 'gaps': [f'G{x}' for x in range(1, 19)] if i == 0 else ['G1'],
                'requirements': ['MC34'], 'objective': 'Synthetic control-plane exercise',
                'criteria': ['The actual generated value equals repaired'], 'deliverables': ['result.json'],
                'output_dir': f'data/accounting-master/deliverables/P0{i}',
                'test_file': f'tests/test_phase_{i}.py'})
        self.catalog['workflow'] = {'mode': 'proposal', 'proposal_phases': ['P00', 'P01', 'P02'],
            'gate_phase': 'P02', 'phase_policy': {f'P0{i}': {'class': 'design', 'schedule': 'active',
                'write_scope': ['scripts/', 'tests/', 'docs/', 'data/accounting-master/deliverables/',
                                'project.config']} for i in range(3)}}
        atomic_json(self.root / CATALOG, self.catalog)
        self.calls = []
        self.checked = []

    def write_work(self, phase, value='repaired'):
        destination = self.root / phase['output_dir'] / 'result.json'
        atomic_json(destination, {'value': value})
        (self.root / phase['test_file']).write_text('# Test double; real check is injected in this control-plane test.\n')
        return [str(destination.relative_to(self.root))]

    def worker(self, role, phase, packet, folder, attempt):
        self.calls.append((role, phase['id'], attempt, packet))
        if role == 'plan':
            return response('PLAN')
        if role.startswith('review'):
            return response('AGREE')
        return response('IMPLEMENTED', evidence=self.write_work(phase))

    def check(self, phase, folder):
        self.checked.append(phase['id'])
        actual = load_json(self.root / phase['output_dir'] / 'result.json')
        return {'passed': actual['value'] == 'repaired', 'tests': 1, 'actual': actual}

    def master(self, worker=None, check=None):
        return Master(self.root, worker=worker or self.worker, check=check or self.check)

    def run_quiet(self, master, **kwargs):
        with redirect_stdout(io.StringIO()):
            return master.run(seconds=30, require_review=False, **kwargs)

    def test_git_provenance_observes_head_in_project_without_writes(self):
        for commit in ('a' * 40, 'b' * 64):
            with self.subTest(commit=commit), patch('run_accounting_master.subprocess.run') as command:
                command.return_value = SimpleNamespace(returncode=0, stdout=commit+'\n', stderr='')
                self.assertEqual(git_provenance(self.root), {'git_commit': commit, 'git_reason': None})
                command.assert_called_once_with(['git', 'rev-parse', '--verify', 'HEAD'], cwd=self.root,
                    capture_output=True, encoding='utf-8', errors='replace', timeout=5, check=False)

    def hold_product_phase(self):
        workflow = self.catalog['workflow']
        workflow['proposal_phases'] = ['P00', 'P01']
        workflow['gate_phase'] = 'P01'
        workflow['phase_policy']['P02'] = {'class': 'product_implementation', 'schedule': 'held', 'write_scope': []}
        atomic_json(self.root / CATALOG, self.catalog)

    def test_proposal_run_never_schedules_product_after_dependencies_pass(self):
        self.hold_product_phase()
        m = self.master()
        self.run_quiet(m, max_phases=3)
        self.assertEqual(m.state['phases']['P01']['status'], ACCEPTED)
        self.assertEqual(m.state['phases']['P02']['status'], 'pending')
        self.assertFalse(any(c[1] == 'P02' for c in self.calls))
        plan = load_json(m.home / 'next-plan.json')
        self.assertIsNone(plan['next_phase'])
        self.assertIn('blocked_by_proposal_gate', plan['blocked_phases']['P02'])

    def test_direct_product_execution_and_worker_cannot_bypass_scheduler(self):
        self.hold_product_phase()
        m = self.master()
        phase = m.phases['P02']
        folder = m.home / 'runs/forbidden'
        with self.assertRaisesRegex(ContinuationVeto, 'proposal_gate'):
            m.execute_phase(phase, folder)
        with self.assertRaisesRegex(ContinuationVeto, 'proposal_gate'):
            m.worker('implement', phase, {}, folder)
        self.assertFalse(folder.exists())
        self.assertEqual(self.calls, [])

    def test_forged_readiness_record_cannot_open_product_queue(self):
        self.hold_product_phase()
        m = self.master()
        atomic_json(m.home / 'proposal-ready.json', {'ready': True, 'implementation_enabled': True})
        m.refresh()
        gate = load_json(m.home / 'proposal-ready.json')
        self.assertFalse(gate['ready'])
        self.assertFalse(gate['implementation_enabled'])
        self.assertNotIn('P02', load_json(m.home / 'next-plan.json')['eligible_phases'])

    def test_proposal_policy_cannot_disappear_or_change_without_migration(self):
        m = self.master(); m.save()
        self.catalog['workflow']['phase_policy']['P00']['class'] = 'research'
        atomic_json(self.root / CATALOG, self.catalog)
        with self.assertRaisesRegex(ContinuationVeto, 'migration'):
            self.master()
        del self.catalog['workflow']
        with self.assertRaises(MasterError):
            validate_catalog(self.catalog)

    def test_missing_class_cyclic_proposal_dependency_and_unbounded_probe_rejected(self):
        import copy
        candidates = []
        d = copy.deepcopy(self.catalog); del d['workflow']['phase_policy']['P02']; candidates.append(d)
        d = copy.deepcopy(self.catalog); d['workflow']['phase_policy']['P00']['class'] = 'product_implementation'; candidates.append(d)
        d = copy.deepcopy(self.catalog); d['workflow']['phase_policy']['P00']['class'] = 'exploratory_probe'; candidates.append(d)
        for candidate in candidates:
            with self.assertRaises(MasterError): validate_catalog(candidate)

    def test_document_worker_cannot_edit_engine_even_if_it_returns_success(self):
        self.catalog['workflow']['phase_policy']['P00']['write_scope'] = ['docs/proposal/']
        atomic_json(self.root / CATALOG, self.catalog)
        def worker(*args):
            (self.root / 'scripts/engine.py').write_text('changed product code')
            return response('IMPLEMENTED')
        m = self.master(worker=worker)
        folder = m.home / 'runs/scope'; folder.mkdir(parents=True)
        with self.assertRaisesRegex(ContinuationVeto, 'write scope'):
            m.worker('implement', m.phases['P00'], {}, folder)
        self.assertTrue((folder / 'implement-0.integrity-failure.json').exists())

    def test_review_cannot_truncate_result_even_when_command_fails(self):
        path = self.root / 'docs/result.json'; path.parent.mkdir()
        path.write_text('{"preserve": true}')
        def worker(*args):
            path.write_text('')
            raise MasterError('review command failed after redirection')
        m = self.master(worker=worker)
        folder = m.home / 'runs/readonly'; folder.mkdir(parents=True)
        with self.assertRaisesRegex(ContinuationVeto, 'read-only'):
            m.phase_review('review_result', m.phases['P00'], {}, folder, 0)
        self.assertFalse((folder / 'review_result-retry-1').exists())

    def test_wrong_role_review_retries_in_fresh_directory_preserving_bad_response(self):
        folders = []
        def worker(role, phase, packet, folder, attempt):
            folders.append(folder)
            if len(folders) == 1:
                bad = response('PLAN')
                atomic_json(folder / f'{role}-{attempt}.response.json', bad)
                return bad
            return response('AGREE')
        m = self.master(worker=worker)
        folder = m.home / 'runs/roles'; folder.mkdir(parents=True)
        result, name = m.phase_review('review_plan', m.phases['P00'], {}, folder, 0)
        self.assertEqual(result['verdict'], 'AGREE')
        self.assertNotEqual(folders[0], folders[1])
        self.assertEqual(load_json(folder / 'review_plan-0.response.json')['verdict'], 'PLAN')
        self.assertIn('retry-1', name)

    def test_unhashable_review_verdicts_preserve_evidence_and_use_bounded_retry(self):
        from run_accounting_master import ReviewPending
        for index, invalid in enumerate(([], {})):
            for always_bad in (False, True):
                calls = []
                def malformed(role, phase, packet, folder, attempt):
                    calls.append(folder)
                    value = response(invalid if always_bad or len(calls) == 1 else 'AGREE')
                    atomic_json(folder / f'{role}-{attempt}.response.json', value)
                    return value
                m = self.master(worker=malformed)
                folder = m.home / f'runs/malformed-{index}-{always_bad}'
                folder.mkdir(parents=True)
                with redirect_stdout(io.StringIO()):
                    if always_bad:
                        with self.assertRaises(ReviewPending):
                            m.phase_review('review_result', m.phases['P00'], {}, folder, 0)
                    else:
                        result, _ = m.phase_review('review_result', m.phases['P00'], {}, folder, 0)
                        self.assertEqual(result['verdict'], 'AGREE')
                self.assertEqual(len(calls), 2)
                self.assertNotEqual(calls[0], calls[1])
                self.assertEqual(load_json(folder / 'review_result-0.response.json')['verdict'], invalid)

    def test_exit_first_observed_after_deadline_is_timeout_even_if_successful(self):
        for name, observations, clock_values in (
                ('between-polls', [None, object()], [0, .9, 1.1, 1.2]),
                ('slow-registration', [object()], [0, 1.1, 1.2])):
            log = self.root / (name + '.log')
            proc = SimpleNamespace(pid=424242, returncode=0)
            def launch(*args, **kwargs):
                kwargs['stdout'].write(b'Late successful output remains preserved\n')
                return proc
            with patch('run_accounting_master.subprocess.Popen', side_effect=launch), \
                 patch('run_accounting_master.process_identity', return_value={'pid': proc.pid}), \
                 patch('run_accounting_master.os.waitid', side_effect=observations), \
                 patch('run_accounting_master.time.monotonic', side_effect=clock_values), \
                 patch('run_accounting_master.time.sleep'), \
                 patch('run_accounting_master.terminate_group'):
                result = bounded_process(['synthetic'], self.root, log, 1, on_spawn=lambda p: None)
            self.assertEqual(result['reason'], 'timeout')
            self.assertEqual(result['exit_code'], 0)
            self.assertIn('preserved', log.read_text())

    def test_changed_pending_catalog_cannot_reuse_old_controller_review(self):
        old = self.master(); old.save()
        atomic_json(old.home / 'controller-review.json', {'verdict': 'AGREE', 'issues': [],
            'controller_hashes': old.controls, 'scope_reviews': [{'verdict': 'AGREE'}]})
        self.catalog['phases'][0]['criteria'] = ['New pending requirement needs current review']
        atomic_json(self.root / CATALOG, self.catalog)
        current = self.master()
        folder = current.home / 'runs/current-catalog'; folder.mkdir(parents=True)
        with patch.object(current, 'ensure_controller_tests'), \
             patch.object(current, 'worker', side_effect=MasterError('Fresh review required')) as worker:
            with self.assertRaisesRegex(MasterError, 'Fresh review required'):
                current.controller_review(folder)
        worker.assert_called_once()
        self.assertNotEqual(old.controls, current.controls)

    def test_stale_checker_input_cannot_be_rebased_into_acceptance(self):
        source = self.root / 'scripts/input.txt'; source.write_text('Old verified input')
        old_digest = digest(source)
        def check(phase, folder):
            source.write_text('New unverified input')
            return {'passed': True, 'tests': 1, 'input_hashes': {'scripts/input.txt': old_digest}}
        m = self.master(check=check)
        self.run_quiet(m, max_phases=1)
        record = m.state['phases']['P00']
        self.assertNotEqual(record['status'], ACCEPTED)
        self.assertNotIn('pending_review', record)
        self.assertNotIn('evidence_hashes', record)

    def test_recovery_retains_latest_failed_replan_and_distinguishes_proposal(self):
        m = self.master(); phase = m.phases['P00']
        attempt = m.home / 'runs/previous/P00'
        atomic_json(attempt / 'review_plan-0.response.json', response('AGREE'))
        atomic_json(attempt / 'approved-plan.json', {'plan': response('PLAN')})
        atomic_json(attempt / 'replan-1/plan-0.response.json', response('PLAN', summary='Latest proposed repair'))
        atomic_json(attempt / 'replan-1/review_plan-retry-1/review_plan-0.response.json',
                    response('REVISE', issues=['Latest repair still omits the needed source']))
        record = {'attempts': [str(attempt.relative_to(self.root)), 'data/accounting-master/runs/new/P00']}
        recovery = phase_recovery(self.root, phase, record)['recent_records']
        self.assertIn('Latest repair still omits', recovery['plan_review']['excerpt']['text'])
        self.assertIn('Latest proposed repair', recovery['proposed_plan']['excerpt']['text'])
        self.assertNotEqual(recovery['approved_plan']['path'], recovery['proposed_plan']['path'])

    def test_current_block_actions_replace_stale_instructions(self):
        for index, blocked_role in enumerate(('implement', 'review_result', 'plan', 'review_plan')):
            def work(role, phase, packet, folder, attempt):
                if role == blocked_role:
                    if role == 'implement': self.write_work(phase)
                    return response('BLOCKED', issues=['Evidence unavailable'], next_actions=['Restore exact source access'])
                return self.worker(role, phase, packet, folder, attempt)
            m = self.master(worker=work)
            record = m.state['phases']['P00']
            record.update(status='pending', next_actions=['Stale instructions'])
            record.pop('block_signature', None)
            m.save()
            self.run_quiet(m, max_phases=1, retry_blocked=True)
            self.assertEqual(m.state['phases']['P00']['next_actions'], ['Restore exact source access'])
            self.assertEqual(load_json(m.home / 'next-plan.json')['next_actions']['P00'], ['Restore exact source access'])

    def test_finalization_defers_interruption_until_terminal_evidence_is_saved(self):
        import run_accounting_master as controller
        original_atomic = controller.atomic_json
        for stage in ('refresh', 'manifest', 'second-interruption'):
            m = self.master()
            real_refresh = m.refresh
            calls = []
            signalled = []
            def refresh():
                calls.append(True)
                trigger = 3 if stage == 'second-interruption' else 2
                if len(calls) == trigger and stage != 'manifest':
                    os.kill(os.getpid(), signal.SIGTERM)
                return real_refresh()
            def write(path, value):
                if stage == 'manifest' and Path(path).name == 'manifest.json' and 'finished_at' in value and not signalled:
                    signalled.append(True)
                    os.kill(os.getpid(), signal.SIGTERM)
                return original_atomic(path, value)
            with patch.object(m, 'refresh', side_effect=refresh), \
                 patch.object(m, 'execute_phase', side_effect=KeyboardInterrupt('First stop')), \
                 patch('run_accounting_master.atomic_json', side_effect=write), catch_termination():
                with self.assertRaises(KeyboardInterrupt):
                    self.run_quiet(m, max_phases=1 if stage == 'second-interruption' else 0)
            manifest = load_json(self.root / m.state['runs'][-1] / 'manifest.json')
            self.assertIn('finished_at', manifest)
            self.assertIn('outcome', manifest)
            self.assertEqual(load_json(m.home / 'next-plan.json')['state_sha256'], digest(m.state_path))

    def test_worker_cannot_write_hidden_configuration_or_prior_run_record(self):
        for name in ('.codex/settings.toml', 'data/accounting-master/runs/earlier/checks.json'):
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('Original persistent evidence')
                def alter(*args):
                    path.write_text('Unexpected worker write')
                    return response('IMPLEMENTED')
                m = self.master(worker=alter)
                folder = m.home / ('runs/scope-' + str(len(name)))
                folder.mkdir(parents=True)
                with self.assertRaises(ContinuationVeto):
                    m.worker('implement', m.phases['P00'], {}, folder)

    def test_new_hidden_configuration_is_also_out_of_scope(self):
        def create(*args):
            p = self.root / '.agents/settings.json'
            atomic_json(p, {'unexpected': True})
            return response('IMPLEMENTED')
        m = self.master(worker=create)
        folder = m.home / 'runs/new-config'; folder.mkdir(parents=True)
        with self.assertRaises(ContinuationVeto):
            m.worker('implement', m.phases['P00'], {}, folder)

    def test_review_inventory_failure_is_a_veto_without_retry(self):
        m = self.master()
        folder = m.home / 'runs/unreadable'; folder.mkdir(parents=True)
        with patch('run_accounting_master.worker_inventory', side_effect=[{}, OSError('cannot read file')]):
            with self.assertRaisesRegex(ContinuationVeto, 'cannot read file'):
                m.phase_review('review_result', m.phases['P00'], {}, folder, 0)
        self.assertFalse((folder / 'review_result-retry-1').exists())
        self.assertTrue((folder / 'review_result-0.integrity-failure.json').exists())

    def test_review_introducing_symlink_vetoes_without_retry(self):
        def create(*args):
            (self.root / 'scripts/link.py').symlink_to('accounting_master_response.schema.json')
            return response('AGREE')
        m = self.master(worker=create)
        folder = m.home / 'runs/symlink'; folder.mkdir(parents=True)
        with self.assertRaisesRegex(ContinuationVeto, 'symlink'):
            m.phase_review('review_result', m.phases['P00'], {}, folder, 0)
        self.assertFalse((folder / 'review_result-retry-1').exists())

    def test_observed_checkpoint_loss_cannot_recreate_cached_state(self):
        m = self.master()
        m.reload_state()  # A genuinely new controller is valid.
        m.save()
        m.state_path.unlink()
        with self.assertRaisesRegex(ContinuationVeto, 'checkpoint disappeared'):
            m.reload_state()
        with self.assertRaises(ContinuationVeto):
            m.save()
        self.assertFalse(m.state_path.exists())

    def test_prior_boot_record_never_inspects_or_signals_current_processes(self):
        m = self.master()
        previous = {'pid': 424242, 'pgid': 424242, 'start_ticks': 10, 'boot_id': 'previous-boot'}
        atomic_json(m.home / 'active-process.json', {'status': 'running', 'identity': previous})
        with patch('run_accounting_master.process_identity') as inspect, \
             patch('run_accounting_master.stop_recovered_group') as stop, redirect_stdout(io.StringIO()):
            m.recover_process()
        inspect.assert_not_called(); stop.assert_not_called()
        self.assertEqual(load_json(m.home / 'active-process.json')['status'], 'finished')
        previous.pop('boot_id')
        atomic_json(m.home / 'active-process.json', {'status': 'running', 'identity': previous})
        with self.assertRaisesRegex(ContinuationVeto, 'no boot identity'):
            m.recover_process()

    def test_recovery_helper_rejects_different_boot_before_signalling(self):
        with patch('run_accounting_master.process_identity') as inspect:
            with self.assertRaisesRegex(ContinuationVeto, 'boot identity'):
                stop_recovered_group({'pid': 424242, 'boot_id': 'previous-boot'})
        inspect.assert_not_called()

    def test_readonly_preflight_preserves_overwrites_deletions_and_failed_writes(self):
        self.catalog['phases'][0]['checker'] = ['scripts/check.py']
        atomic_json(self.root / CATALOG, self.catalog)
        p = self.root / 'scripts/preserved.py'
        for action in ('overwrite', 'delete', 'fail_after_write'):
            with self.subTest(action=action):
                p.write_text('Original before preflight')
                original_hash = digest(p)
                def check(*args):
                    if action == 'delete': p.unlink()
                    else: p.write_text('Preflight corrupted input')
                    if action == 'fail_after_write': raise MasterError('failed after writing')
                    return {'passed': False, 'tests': 1}
                m = self.master(check=check)
                with self.assertRaisesRegex(ContinuationVeto, 'preflight changed'):
                    with redirect_stdout(io.StringIO()):
                        m.execute_phase(m.phases['P00'], m.home / ('runs/preflight-' + action))
                saved = m.home / 'prior-bytes' / original_hash
                self.assertEqual(saved.read_text(), 'Original before preflight')
                with self.assertRaisesRegex(ContinuationVeto, 'need restoration'):
                    m.execute_phase(m.phases['P00'], m.home / ('runs/blocked-resume-' + action))
                p.write_text('Original before preflight')
                m.state['phases']['P00'].pop('preflight_integrity')
                m.save()

    def test_partial_continuation_stales_on_declared_checker_input_change(self):
        m = self.master(); phase = m.phases['P00']; record = m.state['phases']['P00']
        record['contributed_files'] = []
        self.write_work(phase)
        source = self.root / 'scripts/research.txt'; source.write_text('Original source')
        checked = {'passed': True, 'tests': 1, 'input_hashes': {'scripts/research.txt': digest(source)}}
        stage = m.home / 'runs/partial'; stage.mkdir(parents=True)
        atomic_json(stage / 'checks.json', checked)
        m.save_continuation(phase, record, stage, checked, 'Partial work', ['Complete the design'])
        self.assertEqual(phase_recovery(self.root, phase, record)['continuation']['status'], 'checked_snapshot_not_acceptance')
        source.write_text('Changed source only')
        self.assertEqual(phase_recovery(self.root, phase, record)['continuation']['status'], 'stale_recheck_required')

    def test_failed_replanning_cannot_advance_with_unresolved_deletion(self):
        self.catalog['phases'][1]['deps'] = []
        atomic_json(self.root / CATALOG, self.catalog)
        preserved = self.root / 'scripts/preserved.py'; preserved.write_text('Keep me')
        def work(role, phase, packet, folder, attempt):
            if role == 'implement':
                evidence = self.write_work(phase)
                preserved.unlink()
                return response('IMPLEMENTED', evidence=evidence)
            if role == 'plan' and 'repair_findings' in packet:
                return response('BLOCKED', issues=['Replanning could not restore the file'])
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=work)
        self.assertEqual(self.run_quiet(m, max_phases=2), 'continuation_veto')
        self.assertFalse(any(c[1] == 'P01' for c in self.calls))
        self.assertIn('scripts/preserved.py', m.state['phases']['P00']['outstanding_deletions'])

    def test_role_specific_schema_excludes_planning_verdict_in_review(self):
        from run_accounting_master import role_verdicts
        self.assertEqual(role_verdicts('review_plan'), {'AGREE', 'REVISE', 'BLOCKED'})
        with self.assertRaises(MasterError): role_verdicts('unknown')

    def test_proposal_gate_rejects_legacy_acceptance_without_current_bindings(self):
        m = self.master()
        for record in m.state['phases'].values():
            record['status'] = ACCEPTED
        gate = m.proposal_gate()
        self.assertFalse(gate['ready'])
        self.assertIn('stale proposal phase', gate['reason'])

    def test_checker_capture_rejects_empty_declared_result_and_false_subcheck(self):
        script = self.root / 'scripts/check.py'
        script.write_text('import json\nprint(json.dumps({"passed":True,"tests":1,"checks":[{"passed":False}]}))\n')
        phase = {**self.catalog['phases'][0], 'checker': ['scripts/check.py']}
        self.assertFalse(run_phase_tests(self.root, phase, self.root / 'failed.json'))
        script.write_text('import json\nprint(json.dumps({"passed":True,"tests":1}))\n')
        empty = self.root / 'empty.json'; empty.write_text('')
        phase['evidence_artifacts'] = [{'path': 'empty.json', 'format': 'json', 'kind': 'checker_report'}]
        self.assertFalse(run_phase_tests(self.root, phase, self.root / 'empty-capture.json'))
        self.assertIn('empty', load_json(self.root / 'empty-capture.json')['artifact_errors'][0])

    def test_checker_capture_is_fresh_and_raw_hash_bound(self):
        script = self.root / 'scripts/check.py'
        script.write_text('import json\nprint(json.dumps({"passed":True,"tests":1}))\n')
        phase = {**self.catalog['phases'][0], 'checker': ['scripts/check.py']}
        out = self.root / 'capture.json'
        self.assertTrue(run_phase_tests(self.root, phase, out))
        checked = load_json(out)
        self.assertEqual(checked['checker_output_sha256'], digest(out.with_suffix('.checker.json')))
        before = out.read_bytes()
        with self.assertRaisesRegex(ValueError, 'not fresh'):
            run_phase_tests(self.root, phase, out)
        self.assertEqual(before, out.read_bytes())

    def test_timeout_checks_partial_bytes_then_reviews_a_new_plan(self):
        order = []
        def worker(role, phase, packet, folder, attempt):
            order.append(role)
            if role == 'implement':
                self.write_work(phase, 'broken')
                raise ProcessTimeout('lost model connection after partial write')
            if role == 'plan' and 'repair_findings' in packet:
                self.assertFalse(packet['repair_findings']['continuation']['checks']['passed'])
            return self.worker(role, phase, packet, folder, attempt)
        def checked(phase, folder):
            order.append('check')
            return self.check(phase, folder)
        m = self.master(worker=worker, check=checked)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(order, ['plan', 'review_plan', 'implement', 'check', 'plan', 'review_plan', 'repair', 'check', 'review_result'])
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)
        path = self.root / m.state['phases']['P00']['continuation']
        self.assertFalse(load_json(path)['acceptance'])

    def test_replanned_partial_work_can_use_real_internal_verification(self):
        import shutil
        project = Path(__file__).resolve().parents[1]
        for name in ('run_accounting_master.py', 'accounting_master_support.py'):
            shutil.copyfile(project / 'scripts' / name, self.root / 'scripts' / name)
        def worker(role, phase, packet, folder, attempt):
            if role in {'implement', 'repair'}:
                evidence = self.write_work(phase)
                (self.root / phase['test_file']).write_text(
                    'import unittest, json\nfrom pathlib import Path\n'
                    'class ActualResultTest(unittest.TestCase):\n'
                    ' def test_saved_result(self):\n'
                    f'  p=Path(__file__).resolve().parents[1]/{evidence[0]!r}\n'
                    '  self.assertEqual(json.loads(p.read_text())["value"], "repaired")\n')
                if role == 'implement':
                    raise ProcessTimeout('lost final response after valid outputs')
                return response('IMPLEMENTED', evidence=evidence)
            return self.worker(role, phase, packet, folder, attempt)
        def real_check(phase, folder):
            # Retain the isolated harness grant, but execute the actual locked
            # helper subprocess and its real state/capability validation.
            m.check_override = None
            try:
                return m.check_phase(phase, folder)
            finally:
                m.check_override = real_check
        m = self.master(worker=worker, check=real_check)
        self.run_quiet(m, max_phases=1)
        record = m.state['phases']['P00']
        self.assertEqual(record['status'], ACCEPTED)
        for stage in ('execution-0', 'execution-1'):
            checked = load_json(self.root / record['attempts'][-1] / stage / 'checks.json')
            self.assertTrue(checked['passed'])
            self.assertEqual(checked['tests'], 1)

    def test_stop_request_defers_checks_without_starting_a_helper(self):
        m = self.master()
        atomic_json(m.home / 'stop-request.json', {'requested': True})
        folder = m.home / 'stop-check'; folder.mkdir()
        with patch.object(m, 'process') as process:
            checked = m.check_phase(self.catalog['phases'][0], folder)
        process.assert_not_called()
        self.assertEqual(self.checked, [])
        self.assertEqual(checked, {'passed': False, 'tests': 0, 'verification_deferred': 'stop_requested'})

    def test_timeout_after_valid_outputs_never_becomes_implementation_response(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def worker(role, phase, packet, folder, attempt):
            if role == 'implement':
                self.write_work(phase)
                raise ProcessTimeout('no final response')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=worker)
        self.run_quiet(m, max_phases=1)
        record = m.state['phases']['P00']
        self.assertEqual(record['status'], 'needs_repair')
        self.assertTrue(load_json(self.root / record['continuation'])['checks']['passed'])
        self.assertFalse(any(c[0] == 'review_result' for c in self.calls))
        (self.root / 'data/accounting-master/deliverables/P00/result.json').write_text('{}')
        snapshot = phase_recovery(self.root, self.catalog['phases'][0], record)
        self.assertEqual(snapshot['continuation']['status'], 'stale_recheck_required')

    def test_partial_response_is_reviewed_but_never_phase_acceptance(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def worker(role, phase, packet, folder, attempt):
            if role == 'implement':
                return response('PARTIAL', evidence=self.write_work(phase), next_actions=['Implement remaining admitted lifecycle'])
            if role == 'review_result':
                self.assertEqual(packet['review_scope'], 'bounded_partial_work')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=worker)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
        self.assertTrue(any(c[0] == 'review_result' for c in self.calls))

    def test_incomplete_criterion_vetoes_even_agree(self):
        for result in ({'phase_criteria_complete': False}, {'acceptance': {'phase_criteria_complete': False}}):
            m = self.master(check=lambda p, f: {'passed': True, 'tests': 1, **result})
            self.run_quiet(m, max_phases=1)
            self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
            self.assertNotIn('pending_review', m.state['phases']['P00'])

    def test_registered_checker_requires_explicit_all_criteria(self):
        from run_accounting_master import acceptance_ready
        phase = {**self.catalog['phases'][0], 'checker': ['scripts/check.py']}
        for completion in ({}, {'phase_criteria_complete': True},
                           {'phase_criteria_complete': True, 'criteria': {'criterion_1': 'incomplete'}}):
            self.assertFalse(acceptance_ready(phase, {'passed': True, 'tests': 1, 'acceptance': completion}))
        self.assertTrue(acceptance_ready(phase, {'passed': True, 'tests': 1, 'acceptance': {
            'phase_criteria_complete': True, 'criteria': {'criterion_1': 'complete_bounded'}}}))

    def test_unchanged_timeout_defers_and_relevant_input_reopens(self):
        self.catalog['phases'][0]['retry_inputs'] = ['scripts/authority.json']
        atomic_json(self.root / CATALOG, self.catalog)
        def worker(role, phase, packet, folder, attempt):
            if role == 'implement':
                raise ProcessTimeout('unchanged missing handoff')
            return self.worker(role, phase, packet, folder, attempt)
        for _ in range(2):
            m = self.master(worker=worker)
            self.run_quiet(m, max_phases=1)
        self.assertIn('deferred_signature', m.state['phases']['P00'])
        self.calls.clear()
        self.run_quiet(self.master(worker=worker), max_phases=1)
        self.assertEqual(self.calls, [])
        atomic_json(self.root / 'scripts/authority.json', {'new': 'source'})
        self.run_quiet(self.master(), max_phases=1)
        self.assertTrue(self.calls)

    def test_external_block_fingerprint_includes_declared_research(self):
        self.catalog['phases'][0]['retry_inputs'] = ['docs/new-sources']
        atomic_json(self.root / CATALOG, self.catalog)
        m = self.master()
        before = m.input_fingerprint('P00')
        atomic_json(self.root / 'docs/new-sources/source.json', {'inspected': True})
        self.assertNotEqual(before, m.input_fingerprint('P00'))
        atomic_json(self.root / 'docs/unrelated.json', {})
        self.assertEqual(m.input_fingerprint('P01'), self.master().input_fingerprint('P01'))

    def test_editable_worker_reserves_supervisor_check_budget(self):
        self.catalog['limits']['verification_reserve_seconds'] = 300
        atomic_json(self.root / CATALOG, self.catalog)
        m = self.master()
        m.deadline = time.monotonic() + 200
        folder = m.home / 'reserve'; folder.mkdir()
        with self.assertRaisesRegex(MasterError, 'verification reserve'):
            m.worker('implement', self.catalog['phases'][0], {}, folder)
        self.assertEqual(self.calls, [])

    def test_literal_checker_executes_once_and_preserves_raw_result(self):
        script = self.root / 'scripts/check.py'
        script.write_text('import json\nprint(json.dumps({"passed": True, "tests": 2, "acceptance": {"phase_criteria_complete": False}}))\n')
        phase = {**self.catalog['phases'][0], 'checker': ['scripts/check.py']}
        out = self.root / 'checks.json'
        self.assertTrue(run_phase_tests(self.root, phase, out))
        self.assertFalse(load_json(out)['acceptance']['phase_criteria_complete'])
        self.assertTrue(out.with_suffix('.checker.json').exists())
        script.write_text('print("malformed output")\n')
        out = out.with_name('malformed.json')
        self.assertFalse(run_phase_tests(self.root, phase, out))
        self.assertEqual(load_json(out)['tests'], 0)

    def test_startup_queries_cannot_consume_verification_reserve(self):
        for delay, expected_launch in ((15, True), (31, False)):
            with self.subTest(delay=delay):
                self.catalog['limits'].update(phase_seconds=900, verification_reserve_seconds=40)
                atomic_json(self.root / CATALOG, self.catalog)
                m = self.master(); m.worker_override = None; m.deadline = 100
                atomic_json(m.home / 'authorization.json', {'sequential_workers': True})
                folder = m.home / f'startup-{delay}'; folder.mkdir()
                clock = [0.0]; queries = []; launches = []
                def query(argv, **kwargs):
                    queries.append(kwargs['timeout'])
                    clock[0] += delay
                    return SimpleNamespace(stdout='[]')
                def launch(argv, log, seconds, prompt):
                    launches.append(seconds)
                    self.assertLessEqual(seconds + clock[0], 60)
                    atomic_json(Path(argv[argv.index('-o')+1]), response('IMPLEMENTED'))
                with patch('run_accounting_master.time.monotonic', side_effect=lambda: clock[0]), \
                     patch('run_accounting_master.shutil.which', return_value='/fake/codex'), \
                     patch('run_accounting_master.subprocess.run', side_effect=query), \
                     patch.object(m, 'process', side_effect=launch):
                    if expected_launch:
                        m.worker('implement', self.catalog['phases'][0], {}, folder)
                        self.assertEqual(launches, [30])
                    else:
                        with self.assertRaisesRegex(MasterError, 'verification reserve'):
                            m.worker('implement', self.catalog['phases'][0], {}, folder)
                        self.assertEqual(launches, [])
                self.assertTrue(all(q <= 30 for q in queries))

    def test_accepted_contract_and_dependency_changes_invalidate_reuse(self):
        m = self.master(); self.run_quiet(m, max_phases=2)
        original = json.loads(json.dumps(m.state))
        m.state['phases']['P00']['evidence_hashes']['scripts/new-input.json'] = 'a'*64
        m.refresh()
        self.assertEqual(m.state['phases']['P01']['status'], 'stale')
        m.state = original; m.save()
        self.catalog['phases'][0]['criteria'].append('new obligation')
        atomic_json(self.root / CATALOG, self.catalog)
        changed = self.master(); changed.refresh()
        self.assertEqual(changed.state['phases']['P00']['status'], 'stale')
        self.assertEqual(changed.state['phases']['P01']['status'], 'stale')

    def test_legacy_acceptance_without_contract_binding_is_stale(self):
        m = self.master(); self.run_quiet(m, max_phases=1)
        m.state['phases']['P00'].pop('accepted_phase_hash')
        m.refresh()
        self.assertEqual(m.state['phases']['P00']['status'], 'stale')

    def test_final_refresh_veto_has_consistent_terminal_outcome(self):
        m = self.master()
        original = m.refresh
        def refresh():
            if m.state['phases']['P00']['status'] == ACCEPTED and m.state.get('last_outcome'):
                raise ContinuationVeto('late integrity failure')
            return original()
        with patch.object(m, 'refresh', side_effect=refresh):
            outcome = self.run_quiet(m, max_phases=1)
        manifest = load_json(m.home / 'runs' / m.run_id / 'manifest.json')
        self.assertEqual(outcome, 'continuation_veto')
        self.assertEqual(manifest['outcome'], outcome)
        self.assertEqual(load_json(m.home / 'next-plan.json')['status'], outcome)
        event = json.loads((m.home / 'events.jsonl').read_text().splitlines()[-1])
        self.assertEqual(event['outcome'], outcome)

    def test_initial_refresh_interruption_has_terminal_manifest_and_no_plan(self):
        m = self.master()
        with patch.object(m, 'refresh', side_effect=KeyboardInterrupt):
            outcome = self.run_quiet(m, max_phases=1)
        manifest = load_json(m.home / 'runs' / m.run_id / 'manifest.json')
        self.assertEqual(outcome, 'interrupted')
        self.assertIn('finished_at', manifest)
        self.assertIn(str((m.home / 'runs' / m.run_id).relative_to(self.root)), load_json(m.state_path)['runs'])
        self.assertEqual(load_json(m.home / 'next-plan.json')['eligible_phases'], [])
        self.assertEqual(self.calls, [])

    def test_every_ordinary_repair_has_fresh_plan_review(self):
        for failure in ('checks', 'review', 'missing-evidence'):
            order = []
            def worker(role, phase, packet, folder, attempt):
                order.append(role)
                value = self.worker(role, phase, packet, folder, attempt)
                if role == 'implement' and failure == 'missing-evidence':
                    value['evidence'] = ['absent.json']
                if role == 'review_result' and attempt == 0 and failure == 'review':
                    return response('REVISE', issues=['repair current result'])
                return value
            def check(phase, folder):
                return {'passed': failure != 'checks' or folder.name != 'execution-0', 'tests': 1}
            m = self.master(worker=worker, check=check)
            m.state['phases']['P00']['status'] = 'pending'; m.save()
            self.run_quiet(m, max_phases=1)
            index = order.index('repair')
            self.assertEqual(order[index-2:index], ['plan', 'review_plan'])
            self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)

    def test_partial_review_block_stops_editable_continuation(self):
        def worker(role, phase, packet, folder, attempt):
            if role == 'implement':
                return response('PARTIAL', evidence=self.write_work(phase))
            if role == 'review_result':
                return response('BLOCKED', issues=['primary provision unavailable'], next_actions=['Await declared source'])
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=worker); self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'blocked_external')
        self.assertFalse(any(c[0] == 'repair' for c in self.calls))
        self.assertEqual(m.state['phases']['P00']['next_actions'], ['Await declared source'])

    def test_all_source_types_and_root_configuration_are_preserved(self):
        from accounting_master_support import changes_since
        for name in ('src/schema.sql', 'src/settings.yaml', 'project.config'):
            path = self.root / name; path.parent.mkdir(exist_ok=True); path.write_text('original')
        before = preserve_editable(self.root, self.root / 'data/accounting-master/prior-bytes')
        for name in ('src/schema.sql', 'src/settings.yaml', 'project.config'):
            self.assertIn(name, before)
        (self.root / 'src/schema.sql').unlink()
        (self.root / 'project.config').write_text('changed')
        changed = changes_since(self.root, before)
        self.assertIn('src/schema.sql', changed['deleted'])
        self.assertIn('project.config', changed['changed'])

    def test_recovery_retains_invalid_json_without_aborting(self):
        phase = self.catalog['phases'][0]
        folder = self.root / 'data/accounting-master/runs/recovery/P00'
        (folder / 'execution-0').mkdir(parents=True)
        path = folder / 'execution-0/implement-0.response.json'
        record = {'attempts': [str(folder.relative_to(self.root))]}
        for text in ('{"verdict":', '[]', 'null'):
            path.write_text(text)
            recovered = phase_recovery(self.root, phase, record)
            self.assertEqual(recovered['recent_records']['work_response']['status'], 'invalid_recheck_required')
            self.assertEqual(path.read_text(), text)

    def test_git_provenance_retains_observed_failure_without_invented_head(self):
        cases = [(SimpleNamespace(returncode=128, stdout='', stderr='no repository'), 'no repository'),
                 (SimpleNamespace(returncode=0, stdout='not-a-commit', stderr=''), 'invalid commit'),
                 (FileNotFoundError('git missing'), 'FileNotFoundError'),
                 (subprocess.TimeoutExpired(['git'], 5), 'timed out')]
        for result, expected in cases:
            with self.subTest(expected=expected), patch('run_accounting_master.subprocess.run') as command:
                if isinstance(result, Exception):
                    command.side_effect = result
                else:
                    command.return_value = result
                observed = git_provenance(self.root)
                self.assertIsNone(observed['git_commit'])
                self.assertIn(expected, observed['git_reason'])

    def test_run_manifest_uses_observed_git_provenance_and_content_hashes(self):
        master = self.master()
        provenance = {'git_commit': 'c' * 40, 'git_reason': None}
        with patch('run_accounting_master.git_provenance', return_value=provenance) as probe:
            self.run_quiet(master, max_phases=1)
        probe.assert_called_once_with(self.root)
        manifest = load_json(master.home / 'runs' / master.run_id / 'manifest.json')
        self.assertEqual(manifest['git_commit'], provenance['git_commit'])
        self.assertIsNone(manifest['git_reason'])
        self.assertEqual(manifest['controller_hashes'], master.controls)
        self.assertEqual(manifest['catalog_sha256'], digest(self.root / CATALOG))

    def test_executes_real_repair_before_acceptance(self):
        def faulty(role, phase, packet, folder, attempt):
            self.calls.append((role, phase['id'], attempt, packet))
            if role == 'implement':
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            if role == 'repair':
                self.assertIn('repair_findings', packet)
                return response('IMPLEMENTED', evidence=self.write_work(phase))
            return response('PLAN' if role == 'plan' else 'AGREE')
        m = self.master(worker=faulty)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)
        self.assertEqual([c[0] for c in self.calls if c[0] in {'implement', 'repair'}], ['implement', 'repair'])
        self.assertEqual(self.checked, ['P00', 'P00'])
        value = load_json(self.root / 'data/accounting-master/deliverables/P00/result.json')
        self.assertEqual(value['value'], 'repaired')

    def test_review_timeout_retries_read_only_and_ignores_timed_out_agree(self):
        seen = []
        def intermittent(role, phase, packet, folder, attempt):
            if role == 'review_result':
                seen.append(folder)
                if len(seen) == 1:
                    atomic_json(folder / f'{role}-{attempt}.response.json', response('AGREE'))
                    raise ProcessTimeout('worker timeout after writing an unaccepted response')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=intermittent)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)
        self.assertEqual(len(seen), 2)
        self.assertNotEqual(seen[0], seen[1])
        self.assertEqual([c[0] for c in self.calls if c[0] in {'implement', 'repair'}], ['implement'])
        evidence = m.state['phases']['P00']['evidence_hashes']
        self.assertNotIn(str((seen[0] / 'review_result-0.response.json').relative_to(self.root)), evidence)
        self.assertIn(str((seen[1] / 'review_result-0.response.json').relative_to(self.root)), evidence)

    def pending_master(self):
        def unavailable(role, phase, packet, folder, attempt):
            if role == 'review_result':
                raise ProcessTimeout('review timeout')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=unavailable)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_review')
        self.assertFalse(any(c[0] == 'repair' for c in self.calls))
        return m

    def test_review_exhaustion_resumes_checks_and_review_without_reimplementation(self):
        m = self.pending_master()
        checkpoint = m.state['phases']['P00']['pending_review']
        self.assertTrue((self.root / checkpoint).is_file())
        self.calls.clear()
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertEqual(resumed.state['phases']['P00']['status'], ACCEPTED)
        self.assertEqual([c[0] for c in self.calls], ['review_result'])
        self.assertEqual(self.checked, ['P00', 'P00'])
        self.assertNotIn('pending_review', resumed.state['phases']['P00'])
        self.assertEqual(load_json(resumed.home / 'next-plan.json')['state_sha256'], digest(resumed.state_path))

    def test_changed_checked_work_invalidates_review_resume(self):
        self.pending_master()
        (self.root / 'tests/test_phase_0.py').write_text('changed test meaning\n')
        self.calls.clear()
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertIn('implement', [c[0] for c in self.calls])
        self.assertIn('pending_review_invalidated', (resumed.home / 'events.jsonl').read_text())

    def test_changed_phase_contract_invalidates_review_resume(self):
        self.pending_master()
        self.catalog['phases'][0]['criteria'].append('New substantive criterion')
        atomic_json(self.root / CATALOG, self.catalog)
        self.calls.clear()
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertIn('plan', [c[0] for c in self.calls])
        self.assertIn('implement', [c[0] for c in self.calls])

    def test_changed_prerequisite_evidence_invalidates_review_resume(self):
        def unavailable(role, phase, packet, folder, attempt):
            if role == 'review_result' and phase['id'] == 'P01':
                raise ProcessTimeout('review timeout')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=unavailable)
        self.run_quiet(m, max_phases=2)
        record = m.state['phases']['P01']
        self.assertEqual(record['status'], 'needs_review')
        m.state['phases']['P00']['evidence_hashes']['new-evidence.json'] = '1' * 64
        with redirect_stdout(io.StringIO()):
            self.assertIsNone(m.load_pending_review(self.catalog['phases'][1], record))
        self.assertNotIn('pending_review', record)

    def test_result_reviewer_cannot_accept_mutated_checked_files(self):
        def mutation(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'review_result':
                (self.root / phase['test_file']).write_text('changed after checking\n')
            return result
        m = self.master(worker=mutation)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertNotEqual(m.state['phases']['P00']['status'], ACCEPTED)

    def test_review_resume_revise_executes_actual_repair(self):
        self.pending_master()
        self.calls.clear()
        def finding(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'review_result' and attempt == 0:
                return response('REVISE', issues=['Add the missing recovery behaviour'])
            if role == 'repair':
                self.assertIn('Add the missing recovery behaviour', packet['repair_findings']['result_review']['issues'])
            return result
        resumed = self.master(worker=finding)
        self.run_quiet(resumed, max_phases=1)
        self.assertEqual([c[0] for c in self.calls], ['review_result', 'plan', 'review_plan', 'repair', 'review_result'])
        self.assertEqual(resumed.state['phases']['P00']['status'], ACCEPTED)

    def test_stop_during_review_does_not_launch_a_retry(self):
        reviews = []
        def stop(role, phase, packet, folder, attempt):
            if role == 'review_result':
                reviews.append(role)
                atomic_json(self.root / 'data/accounting-master/stop-request.json', {'stop': True})
                raise ProcessTimeout('review timeout concurrent with stop')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=stop)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(reviews, ['review_result'])
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_review')

    def test_short_remaining_budget_keeps_checked_work_without_launching_review(self):
        m = self.master()
        def near_deadline(phase, folder):
            result = self.check(phase, folder)
            m.deadline = time.monotonic() + .5
            return result
        m.check_override = near_deadline
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_review')
        self.assertFalse(any(c[0] in {'review_result', 'repair'} for c in self.calls))

    def test_failed_checks_cannot_become_pending_accepted_work(self):
        def timeout(role, phase, packet, folder, attempt):
            if role == 'review_result':
                raise ProcessTimeout('review timeout')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=timeout, check=lambda p, f: {'passed': False, 'tests': 1})
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
        self.assertNotIn('pending_review', m.state['phases']['P00'])
        self.assertEqual(sum(c[0] == 'repair' for c in self.calls), 2)

    def test_process_timeout_classification_retains_completed_process_record(self):
        m = self.master()
        log = self.root / 'classified-timeout.log'
        with self.assertRaises(ProcessTimeout):
            m.process([sys.executable, '-c', 'import time; time.sleep(3)'], log, .1)
        self.assertEqual(load_json(log.with_suffix('.process.json'))['reason'], 'timeout')

    def test_next_phase_plan_uses_actual_previous_result(self):
        m = self.master()
        self.run_quiet(m, max_phases=2)
        packets = [c[3] for c in self.calls if c[:2] == ('plan', 'P01')]
        self.assertEqual(packets[0]['next_plan']['last_outcome']['phase'], 'P00')
        self.assertEqual(packets[0]['next_plan']['phase_states']['P00'], ACCEPTED)
        next_plan = load_json(m.home / 'next-plan.json')
        self.assertEqual(next_plan['next_phase'], 'P02')

    def test_resume_does_not_repeat_accepted_work(self):
        m = self.master()
        self.run_quiet(m, max_phases=1)
        self.calls.clear()
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertFalse(any(c[1] == 'P00' for c in self.calls))
        self.assertEqual(resumed.state['phases']['P01']['status'], ACCEPTED)

    def test_changed_evidence_invalidates_dependents(self):
        m = self.master()
        self.run_quiet(m, max_phases=2)
        atomic_json(self.root / 'data/accounting-master/deliverables/P00/result.json', {'value': 'changed'})
        m.refresh()
        self.assertEqual(m.state['phases']['P00']['status'], 'stale')
        self.assertEqual(m.state['phases']['P01']['status'], 'stale')

    def test_zero_checks_cannot_pass_even_with_agree(self):
        m = self.master(check=lambda p, f: {'passed': True, 'tests': 0})
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
        self.assertEqual(sum(c[0] == 'repair' for c in self.calls), 2)

    def test_missing_evidence_cannot_be_accepted(self):
        def missing(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role in {'implement', 'repair'}:
                result['evidence'] = ['absent.json']
            return result
        m = self.master(worker=missing)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')

    def test_timeout_recovery_lists_current_work_without_reading_raw_logs(self):
        source = self.root / 'scripts/partial.py'
        raw_marker = 'NESTED_RAW_LOG_MUST_NOT_ENTER_RECOVERY'
        def timing_out(role, phase, packet, folder, attempt):
            if role == 'implement':
                source.write_text('PARTIAL = True\n')
                (folder / 'implement-0.log').write_text(raw_marker * 40000)
                atomic_json(folder / 'implement-0.process.json',
                            {'reason': 'timeout', 'exit_code': 0, 'wall_seconds': 5})
                raise MasterError('Command failed (timeout)')
            if role == 'repair':
                recovery = packet['recovery']
                self.assertIn('scripts/partial.py', recovery['current_changes']['text'])
                self.assertIn(phase['test_file'], recovery['missing_files'])
                self.assertIn('timeout', recovery['recent_records']['work_process']['excerpt']['text'])
                self.assertEqual(packet['original_criteria'], phase['criteria'])
                self.assertIn('Command failed (timeout)', packet['repair_findings']['continuation']['reason'])
                self.assertIn('checks', packet['repair_findings']['continuation'])
                self.assertNotIn(raw_marker, json.dumps(packet))
                self.assertLess(len(json.dumps(recovery)), 15000)
                self.assertTrue((self.root / recovery['full_record']).is_file())
            return self.worker(role, phase, packet, folder, attempt)
        original_open = Path.open
        def no_raw_logs(path, *args, **kwargs):
            mode = args[0] if args else kwargs.get('mode', 'r')
            if path.suffix == '.log' and 'r' in mode and 'b' not in mode:
                raise AssertionError('Recovery must not read raw logs')
            return original_open(path, *args, **kwargs)
        m = self.master(worker=timing_out)
        with patch.object(Path, 'open', no_raw_logs):
            self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)
        self.assertTrue(any(c[0] == 'repair' for c in self.calls))

    def test_recovery_survives_new_invocation_and_does_not_accept_partial_work(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def partial(role, phase, packet, folder, attempt):
            if role == 'implement':
                (self.root / 'scripts/resumable.py').write_text('PARTIAL = 1\n')
                atomic_json(folder / 'implement-0.process.json', {'reason': 'timeout'})
                raise MasterError('Command failed (timeout)')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=partial)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
        self.assertFalse(m.state['mission_complete'])
        observed = []
        def resume(role, phase, packet, folder, attempt):
            if role == 'plan':
                recovery = packet['recovery']
                observed.append(recovery)
                self.assertIn('scripts/resumable.py', recovery['current_changes']['text'])
                self.assertIn('timeout', recovery['recent_records']['work_process']['excerpt']['text'])
                self.assertTrue(recovery['missing_files'])
                self.assertIn('approved_plan', recovery['recent_records'])
                self.assertEqual(packet['original_criteria'], phase['criteria'])
            return self.worker(role, phase, packet, folder, attempt)
        resumed = self.master(worker=resume)
        self.run_quiet(resumed, max_phases=1)
        self.assertEqual(len(observed), 1)
        self.assertEqual(resumed.state['phases']['P00']['status'], ACCEPTED)
        self.assertTrue(self.checked)

    def test_recovery_retains_latest_failed_checks_and_actionable_review(self):
        phase = self.catalog['phases'][0]
        invocation = self.root / 'data/accounting-master/runs/recovery/P00'
        for attempt in range(2):
            folder = invocation / f'execution-{attempt}'
            atomic_json(folder / 'checks.json', {'passed': False, 'tests': attempt + 1,
                                               'error': f'failed check {attempt}'})
            atomic_json(folder / f'review_result-{attempt}.response.json',
                        response('REVISE', issues=[f'repair semantic condition {attempt}']))
        record = {'attempts': [str(invocation.relative_to(self.root))]}
        snapshot = phase_recovery(self.root, phase, record)
        self.assertIn('failed check 1', snapshot['recent_records']['checks']['excerpt']['text'])
        self.assertIn('repair semantic condition 1', snapshot['recent_records']['result_review']['excerpt']['text'])
        self.write_work(phase)
        self.assertEqual(phase_recovery(self.root, phase, record)['missing_files'], [])

    def test_worker_receives_actual_remaining_budget_and_bounded_change_excerpt(self):
        captured = []
        def inspect(role, phase, packet, folder, attempt):
            captured.append(packet)
            return response('PLAN')
        m = self.master(worker=inspect)
        m.deadline = time.monotonic() + 4
        folder = m.home / 'runs/budget/P00'
        folder.mkdir(parents=True)
        phase = self.catalog['phases'][0]
        m.state['phases']['P00']['entry_inventory_path'] = str((folder / 'entry.json').relative_to(self.root))
        atomic_json(folder / 'entry.json', {})
        for i in range(100):
            (self.root / 'scripts' / (f'partial_{i}_' + 'a' * 60 + '.py')).write_text('x = 1\n')
        m.worker('plan', phase, {}, folder)
        packet = captured[0]
        self.assertEqual(packet['budget']['worker_limit_seconds'], 5)
        self.assertLessEqual(packet['budget']['available_attempt_seconds'], 4)
        self.assertGreater(packet['budget']['reserve_for_checks_and_response_seconds'], 0)
        self.assertTrue(packet['recovery']['current_changes']['truncated'])
        self.assertLessEqual(len(packet['recovery']['current_changes']['text']), 2400)
        saved = load_json(self.root / packet['recovery']['full_record'])
        self.assertEqual(len(saved['current_changes']['added']), 102)
        prompt = m.prompt('plan', phase, packet)
        self.assertIn('Do not dump raw worker logs', prompt)
        self.assertIn('reserve_for_checks_and_response_seconds', prompt)

    def test_plan_review_repairs_before_implementation(self):
        def revise(role, phase, packet, folder, attempt):
            self.calls.append((role, phase['id'], attempt, packet))
            if role == 'review_plan' and attempt == 0:
                return response('REVISE', issues=['Wrong comparator; use the exact synthetic oracle'])
            if role == 'plan':
                if attempt:
                    self.assertIn('required_plan_repairs', packet)
                return response('PLAN')
            if role in {'implement', 'repair'}:
                return response('IMPLEMENTED', evidence=self.write_work(phase))
            return response('AGREE')
        m = self.master(worker=revise)
        self.run_quiet(m, max_phases=1)
        roles = [c[0] for c in self.calls]
        self.assertEqual(roles[:5], ['plan', 'review_plan', 'plan', 'review_plan', 'implement'])
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)

    def test_failed_plan_review_never_executes(self):
        def rejected(role, phase, packet, folder, attempt):
            self.calls.append((role, phase['id'], attempt, packet))
            return response('PLAN' if role == 'plan' else 'REVISE', issues=['Unsupported promotion criterion'])
        m = self.master(worker=rejected)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_plan_repair')
        self.assertFalse(any(c[0] in {'implement', 'repair'} for c in self.calls))

    def test_external_block_does_not_stop_independent_phase(self):
        self.catalog['phases'][2]['deps'] = []
        atomic_json(self.root / CATALOG, self.catalog)
        def blocked(role, phase, packet, folder, attempt):
            if phase['id'] == 'P00':
                return response('BLOCKED', issues=['Unavailable required external source'])
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=blocked)
        self.run_quiet(m, max_phases=3)
        self.assertEqual(m.state['phases']['P00']['status'], 'blocked_external')
        self.assertEqual(m.state['phases']['P01']['status'], 'pending')
        self.assertEqual(m.state['phases']['P02']['status'], ACCEPTED)

    def test_unchanged_external_block_is_not_retried_on_resume(self):
        def blocked(role, phase, packet, folder, attempt):
            self.calls.append((role, phase['id'], attempt, packet))
            return response('BLOCKED', issues=['External source unavailable'])
        m = self.master(worker=blocked)
        self.run_quiet(m, max_phases=1)
        self.calls.clear()
        self.run_quiet(self.master(worker=blocked), max_phases=1)
        self.assertEqual(self.calls, [])
        self.run_quiet(self.master(worker=blocked), max_phases=1, retry_blocked=True)
        self.assertEqual(len(self.calls), 1)

    def test_previous_next_actions_reach_next_phase_packet(self):
        m = self.master()
        self.run_quiet(m, max_phases=2)
        packet = next(c[3] for c in self.calls if c[:2] == ('plan', 'P01'))
        self.assertEqual(packet['next_plan']['next_actions']['P00'], ['Use observed evidence in the next plan'])

    def test_refresh_rebuilds_a_mismatched_plan_generation(self):
        m = self.master()
        m.refresh()
        atomic_json(m.home / 'next-plan.json', {'generation': -1, 'state_sha256': 'stale'})
        plan = m.refresh()
        self.assertEqual(plan['generation'], m.state['plan_generation'])
        self.assertEqual(plan['state_sha256'], digest(m.state_path))

    def test_corrupt_preserved_object_is_repaired_from_verified_original(self):
        source = self.root / 'scripts/preserved.py'
        source.write_text('VALUE = 7\n')
        store = self.root / 'objects'
        expected = digest(source)
        store.mkdir()
        (store / expected).write_bytes(b'truncated')
        preserved = preserve_editable(self.root, store)
        self.assertEqual(preserved['scripts/preserved.py'], expected)
        self.assertEqual(digest(store / expected), expected)
        self.assertTrue(list((store / 'incomplete').iterdir()))

    def test_conflicting_protection_hashes_are_not_overwritten(self):
        self.assertEqual(merge_hashes({'a': 'same'}, {'a': 'same'}), {'a': 'same'})
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            merge_hashes({'a': 'frozen'}, {'a': 'current'})

    def test_plan_review_external_block_is_not_sent_to_editable_repair(self):
        def blocked(role, phase, packet, folder, attempt):
            if role == 'review_plan':
                return response('BLOCKED', issues=['Required external evidence unavailable'])
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=blocked)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'blocked_external')
        self.assertFalse(any(c[0] in {'implement', 'repair'} for c in self.calls))

    def test_result_review_external_block_is_preserved(self):
        def blocked(role, phase, packet, folder, attempt):
            if role == 'review_result':
                return response('BLOCKED', issues=['A required adjudication source is unavailable'])
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=blocked)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'blocked_external')
        self.assertFalse(any(c[0] == 'repair' for c in self.calls))

    def test_deletion_obligation_survives_repair_and_resume(self):
        source = self.root / 'scripts/must-preserve.py'
        source.write_text('ORIGINAL = True\n')
        def deleting(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'implement':
                source.unlink(missing_ok=True)
            return result
        m = self.master(worker=deleting)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertNotEqual(m.state['phases']['P00']['status'], ACCEPTED)
        self.assertIn('scripts/must-preserve.py', m.state['phases']['P00']['outstanding_deletions'])
        def restoring(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role in {'implement', 'repair'}:
                source.write_text('ORIGINAL = True\n')
            return result
        resumed = self.master(worker=restoring)
        self.run_quiet(resumed, max_phases=1)
        self.assertEqual(resumed.state['phases']['P00']['status'], ACCEPTED)

    def test_missing_release_vetoes_real_adapter_execution(self):
        m = self.master()
        m.worker_override = None
        m.check_override = None
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        run = Path(m.state['runs'][-1])
        manifest = load_json(self.root / run / 'manifest.json')
        self.assertIn('release manifest', manifest['stop_reason'])

    def test_explicit_run_resumes_after_a_saved_stop_request(self):
        m = self.master()
        atomic_json(m.home / 'stop-request.json', {'requested_at': 'prior invocation'})
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)
        self.assertTrue(list((m.home / 'runs').rglob('prior-stop-request.json')))

    def test_existing_worker_response_cannot_be_reused(self):
        m = self.master()
        folder = m.home / 'runs/old-response'
        folder.mkdir(parents=True)
        atomic_json(folder / 'plan-0.response.json', response('PLAN'))
        with self.assertRaisesRegex(MasterError, 'not fresh'):
            m.worker('plan', self.catalog['phases'][0], {}, folder)
        self.assertFalse(self.calls)

    def test_preexisting_bytes_are_preserved_before_edit(self):
        source = self.root / 'scripts/existing.py'
        source.write_text('VALUE = 1\n')
        original = digest(source)
        def editing(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'implement':
                source.write_text('VALUE = 2\n')
            return result
        m = self.master(worker=editing)
        self.run_quiet(m, max_phases=1)
        self.assertEqual((m.home / 'prior-bytes' / original).read_text(), 'VALUE = 1\n')
        self.assertIn('scripts/existing.py', m.state['phases']['P00']['evidence_hashes'])

    def test_successful_slices_do_not_close_mission_or_gaps(self):
        m = self.master()
        self.assertEqual(self.run_quiet(m, max_phases=3), 'catalog_slices_accepted_mission_open')
        self.assertFalse(m.state['mission_complete'])
        self.assertEqual(set(m.state['gap_status'].values()), {'open'})

    def test_controller_mutation_is_continuation_veto(self):
        def mutate(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'implement':
                with (self.root / CATALOG).open('a') as stream:
                    stream.write('\n')
            return result
        m = self.master(worker=mutate)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertEqual(m.state['phases']['P00']['status'], 'interrupted')

    def test_implementation_cannot_rewrite_approved_plan(self):
        def mutate(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'implement':
                target = folder.parent / 'approved-plan.json'
                value = load_json(target)
                value['plan']['steps'] = ['Change the previously approved objective']
                atomic_json(target, value)
            return result
        m = self.master(worker=mutate)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')

    def test_worker_cannot_forge_supervisor_state(self):
        def mutate(role, phase, packet, folder, attempt):
            result = self.worker(role, phase, packet, folder, attempt)
            if role == 'implement':
                atomic_json(self.root / 'data/accounting-master/state.json', {'mission_complete': True})
            return result
        m = self.master(worker=mutate)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertFalse(load_json(m.state_path)['mission_complete'])

    def test_worker_failure_still_checks_integrity(self):
        def failed(role, phase, packet, folder, attempt):
            if role == 'implement':
                with (self.root / CATALOG).open('a') as stream:
                    stream.write('\n')
                raise MasterError('Deliberate worker failure after mutation')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=failed)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        reports = list((m.home / 'runs').rglob('*.integrity-failure.json'))
        self.assertTrue(reports)
        self.assertTrue(any('Deliberate worker failure' in load_json(p)['original_error'] for p in reports))
        self.assertFalse(any(c[0] == 'repair' for c in self.calls))

    def test_malformed_worker_response_still_checks_integrity(self):
        def failed(role, phase, packet, folder, attempt):
            if role == 'implement':
                atomic_json(self.root / 'data/accounting-master/state.json', {'mission_complete': True})
                return {'invalid': 'response'}
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=failed)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertFalse(load_json(m.state_path)['mission_complete'])

    def test_test_process_integrity_veto_is_not_downgraded_to_failed_check(self):
        m = self.master()
        m.check_override = None
        folder = m.home / 'runs/verification-test'
        folder.mkdir(parents=True)
        with patch.object(m, 'process', side_effect=ContinuationVeto('changed supervisor state')):
            with self.assertRaises(ContinuationVeto):
                m.check_phase(self.catalog['phases'][0], folder)

    def test_interrupted_phase_replans_before_resuming(self):
        m = self.master()
        m.state['phases']['P00']['status'] = 'running'
        m.save()
        self.run_quiet(m, max_phases=1)
        packet = next(c[3] for c in self.calls if c[0] == 'plan')
        self.assertIn('Prior process ended', packet['prior_issues'][0])
        self.assertEqual(m.state['phases']['P00']['status'], ACCEPTED)

    def test_exclusive_writer_lock(self):
        with exclusive_lock(self.root / 'lock'):
            with self.assertRaises(MasterError):
                with exclusive_lock(self.root / 'lock'):
                    self.fail('Second writer acquired the lock')

    def test_atomic_json_and_duplicate_key_rejection(self):
        path = self.root / 'value.json'
        atomic_json(path, {'value': 1})
        atomic_json(path, {'value': 2})
        self.assertEqual(load_json(path), {'value': 2})
        path.write_text('{"value":1,"value":2}')
        with self.assertRaises(ValueError):
            load_json(path)

    def test_evidence_path_escape_is_rejected(self):
        for name in ['../outside', '/etc/passwd']:
            with self.assertRaises(ValueError):
                local_path(self.root, name)

    def test_dependency_cycle_is_rejected(self):
        self.catalog['phases'][0]['deps'] = ['P02']
        with self.assertRaises(MasterError):
            validate_catalog(self.catalog)

    def test_schema_validity_does_not_accept_wrong_role_verdict(self):
        with self.assertRaises(MasterError):
            validate_response(response('IMPLEMENTED'), {'AGREE', 'REVISE'})

    def test_process_timeout_is_bounded(self):
        result = bounded_process([sys.executable, '-c', 'import time; time.sleep(60)'],
                                 self.root, self.root / 'timeout.log', 0.2)
        self.assertEqual(result['reason'], 'timeout')
        self.assertLess(result['wall_seconds'], 7)
        self.assertNotEqual(result['exit_code'], 0)

    def test_nonreading_process_cannot_block_large_prompt(self):
        result = bounded_process([sys.executable, '-c', 'import time; time.sleep(60)'],
                                 self.root, self.root / 'stdin.log', 0.2, prompt='x' * 1024 * 1024)
        self.assertEqual(result['reason'], 'timeout')

    def test_successful_parent_exit_also_terminates_descendant(self):
        log = self.root / 'descendant.log'
        code = 'import subprocess,sys; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(60)"]); print(p.pid,flush=True)'
        result = bounded_process([sys.executable, '-c', code], self.root, log, 5)
        self.assertEqual(result['exit_code'], 0)
        pid = int(log.read_text().strip())
        deadline = time.monotonic() + 2
        info = process_identity(pid)
        while info and info['state'] != 'Z' and time.monotonic() < deadline:
            time.sleep(.02)
            info = process_identity(pid)
        self.assertTrue(info is None or info['state'] == 'Z')

    def test_startup_identity_failure_cleans_created_child(self):
        created = []
        original_popen = subprocess.Popen
        original_identity = process_identity
        failed = False
        def launch(*args, **kwargs):
            proc = original_popen(*args, **kwargs)
            created.append(proc)
            return proc
        def identity(pid):
            nonlocal failed
            if not failed:
                failed = True
                raise OSError('Injected first identity-read failure')
            return original_identity(pid)
        with patch('run_accounting_master.subprocess.Popen', side_effect=launch), patch('run_accounting_master.process_identity', side_effect=identity):
            with self.assertRaisesRegex(OSError, 'identity-read'):
                bounded_process([sys.executable, '-c', 'import time; time.sleep(60)'], self.root, self.root / 'startup.log', 5)
        self.assertEqual(len(created), 1)
        self.assertIsNotNone(created[0].returncode)
        self.assertTrue(process_identity(created[0].pid) is None or process_identity(created[0].pid)['state'] == 'Z')

    def test_sigterm_during_registration_is_deferred_then_cleaned(self):
        scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        child_file = self.root / 'registered-child.json'
        completed = self.root / 'registration-completed'
        log = self.root / 'registration.log'
        code = ('import sys,json,os,signal\nfrom pathlib import Path\n'
                f'sys.path.insert(0,{scripts!r})\n'
                'from run_accounting_master import bounded_process,catch_termination\n'
                'def registered(p):\n'
                f' Path({str(child_file)!r}).write_text(json.dumps({{"pid":p.pid}}))\n'
                ' os.kill(os.getpid(),signal.SIGTERM)\n'
                f' Path({str(completed)!r}).write_text("yes")\n'
                'try:\n with catch_termination():\n'
                f'  bounded_process([sys.executable,"-c","import time; time.sleep(60)"],Path({str(self.root)!r}),Path({str(log)!r}),60,on_spawn=registered)\n'
                'except KeyboardInterrupt:\n pass\n')
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(completed.exists())
        info = process_identity(load_json(child_file)['pid'])
        self.assertTrue(info is None or info['state'] == 'Z')

    def test_unquiescent_group_after_escalation_vetoes_before_reaping(self):
        identity = {'pid': 424242, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 10, 'state': 'Z'}
        proc = SimpleNamespace(pid=identity['pid'], _master_identity=identity, wait=Mock())
        with patch('run_accounting_master.process_identity', return_value=identity), \
             patch('run_accounting_master.live_group_members', return_value=[{'pid': 424243}]), \
             patch('run_accounting_master.os.killpg') as send, \
             patch('run_accounting_master.time.monotonic', side_effect=[0, 4, 4, 8]):
            with self.assertRaisesRegex(ContinuationVeto, 'quiescent'):
                terminate_group(proc)
        proc.wait.assert_not_called()
        self.assertFalse(getattr(proc, '_master_cleanup_done', False))
        self.assertEqual(send.call_count, 2)

    def test_recovery_group_reuse_is_vetoed_before_signalling(self):
        original = {'pid': 424242, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 10, 'state': 'S'}
        member = {'pid': 424243, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 11, 'state': 'S'}
        replacement = {**original, 'start_ticks': 999}
        fd = os.open(os.devnull, os.O_RDONLY)
        try:
            with patch('run_accounting_master.process_identity', side_effect=[original, original, replacement]), \
                 patch('run_accounting_master.live_group_members', return_value=[member]), \
                 patch('run_accounting_master.open_pidfd', side_effect=lambda pid: os.dup(fd)), \
                 patch('run_accounting_master.signal.pidfd_send_signal') as send:
                with self.assertRaisesRegex(ContinuationVeto, 'lifetime changed'):
                    stop_recovered_group(original)
                send.assert_not_called()
        finally:
            os.close(fd)

    def test_repeated_shutdown_signals_are_deferred_through_cleanup(self):
        steps = []
        def cleanup(proc):
            os.kill(os.getpid(), signal.SIGTERM)
            steps.append('first deferred')
            os.kill(os.getpid(), signal.SIGTERM)
            steps.append('cleanup completed')
        with catch_termination(), patch('run_accounting_master._terminate_group', side_effect=cleanup):
            with self.assertRaises(KeyboardInterrupt):
                terminate_group(object())
        self.assertEqual(steps, ['first deferred', 'cleanup completed'])

    def test_recovery_identity_exception_closes_acquired_pidfd(self):
        leader = {'pid': 424242, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 10, 'state': 'S'}
        member = {'pid': 424243, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 11, 'state': 'S'}
        opened = []
        def acquire(pid):
            fd = os.open(os.devnull, os.O_RDONLY)
            opened.append(fd)
            return fd
        with patch('run_accounting_master.process_identity', side_effect=[leader, OSError('identity read failed')]), \
             patch('run_accounting_master.live_group_members', return_value=[member]), \
             patch('run_accounting_master.open_pidfd', side_effect=acquire):
            with self.assertRaisesRegex(OSError, 'identity read failed'):
                stop_recovered_group(leader)
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])

    def test_resume_terminates_identified_prior_worker(self):
        proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
        self.addCleanup(terminate_group, proc)
        m = self.master()
        atomic_json(m.home / 'active-process.json', {'status': 'running', 'identity': process_identity(proc.pid)})
        with redirect_stdout(io.StringIO()):
            m.recover_process()
        proc.wait(timeout=3)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(load_json(m.home / 'active-process.json')['status'], 'finished')

    def test_pid_reuse_does_not_signal_unrelated_process(self):
        m = self.master()
        current = process_identity(os.getpid())
        atomic_json(m.home / 'active-process.json', {'status': 'running', 'identity': {
            'pid': current['pid'], 'pgid': current['pid'], 'boot_id': current['boot_id'], 'start_ticks': current['start_ticks'] - 1}})
        with redirect_stdout(io.StringIO()), patch('run_accounting_master.live_group_members', return_value=[]):
            m.recover_process()
        self.assertIn('not signalled', load_json(m.home / 'active-process.json')['recovery'])

    def test_sigterm_of_supervisor_cleans_its_child(self):
        project_scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        child_file = self.root / 'spawned.json'
        log = self.root / 'sigterm.log'
        code = ('import sys,json\nfrom pathlib import Path\n'
                f'sys.path.insert(0,{project_scripts!r})\n'
                'from run_accounting_master import bounded_process,catch_termination\n'
                f'with catch_termination():\n bounded_process([sys.executable,"-c","import time; time.sleep(60)"],Path({str(self.root)!r}),Path({str(log)!r}),60,on_spawn=lambda p:Path({str(child_file)!r}).write_text(json.dumps({{"pid":p.pid}})))\n')
        proc = subprocess.Popen([sys.executable, '-c', code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(terminate_group, proc)
        deadline = time.monotonic() + 5
        while not child_file.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertTrue(child_file.exists())
        child = load_json(child_file)['pid']
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=6)
        info = process_identity(child)
        self.assertTrue(info is None or info['state'] == 'Z')

    def test_subprocess_shell_characters_are_literal_arguments(self):
        marker = self.root / 'must-not-exist'
        value = f'$(touch {marker}); echo ignored'
        log = self.root / 'argv.log'
        result = bounded_process([sys.executable, '-c', 'import sys; print(sys.argv[1])', value], self.root, log, 5)
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(log.read_text().strip(), value)
        self.assertFalse(marker.exists())

    def test_zero_test_suite_fails(self):
        path = self.root / 'tests/test_empty_control.py'
        path.write_text('import unittest\n')
        result = run_phase_tests(self.root, {'test_file': str(path.relative_to(self.root))}, self.root / 'test-result.json')
        self.assertFalse(result)

    def test_allow_rule_has_only_fixed_entrypoint(self):
        rule = rule_text(self.root)
        self.assertIn(repr(['python3', str(self.root / 'scripts/run_accounting_master.py')]), rule)
        self.assertNotIn('pattern=[\'python3\']', rule)
        self.assertIn('not_match=', rule)

    def test_worker_config_overrides_existing_bare_key(self):
        args = worker_overrides('read-only', {'mcp_servers': {'ExampleDocs': {}}})
        self.assertIn('mcp_servers.ExampleDocs.enabled=false', args)
        self.assertNotIn('mcp_servers."ExampleDocs".enabled=false', args)
        self.assertIn('model_reasoning_effort="high"', args)
        self.assertNotIn('model_reasoning_effort="high"', worker_overrides('workspace-write', {}))
        self.assertIn('model_reasoning_effort="medium"', worker_overrides('read-only', {}, 'review_controller'))

    def test_worker_config_rejects_ambiguous_override_key(self):
        with self.assertRaises(MasterError):
            worker_overrides('read-only', {'mcp_servers': {'ambiguous.key': {}}})

    def test_planning_uses_its_declared_independent_budget(self):
        limits = {'phase_seconds': 900, 'plan_seconds': 720, 'review_seconds': 240}
        self.assertEqual(worker_seconds('plan', limits), 720)
        self.assertEqual(worker_seconds('review_plan', limits), 240)
        self.assertEqual(worker_seconds('implement', limits), 900)

    def test_atomic_rule_publication_preserves_conflicting_rule(self):
        target = self.root / 'rules/master.rules'
        atomic_rule_publish(target, 'reviewed rule\n')
        atomic_rule_publish(target, 'reviewed rule\n')
        with self.assertRaises(MasterError):
            atomic_rule_publish(target, 'different rule\n')
        self.assertEqual(target.read_text(), 'reviewed rule\n')

    def test_rule_publication_failure_does_not_leave_partial_target(self):
        target = self.root / 'rules/master.rules'
        with patch('run_accounting_master.os.link', side_effect=OSError('Simulated publication interruption')):
            with self.assertRaises(OSError):
                atomic_rule_publish(target, 'complete rule\n')
        self.assertFalse(target.exists())
        atomic_rule_publish(target, 'complete rule\n')
        self.assertEqual(target.read_text(), 'complete rule\n')

    def test_direct_internal_invocation_is_rejected(self):
        m = self.master()
        args = SimpleNamespace(lock_fd=None, grant=None, capability=None)
        with self.assertRaisesRegex(MasterError, 'supervisor-issued'):
            validate_internal(m, args, m.home / 'runs/forged/result.json')

    def test_real_child_inherits_lock_and_consumes_grant_once(self):
        m = self.master()
        m.state['phases']['P00']['status'] = 'running'
        m.save()
        output = m.home / 'runs/child-test/result.json'
        grant = output.with_suffix('.capability.json')
        token = 'fixed-test-token'
        atomic_json(grant, {'parent': process_identity(os.getpid()), 'phase': 'P00',
                           'output': str(output), 'run_id': 'child-test', 'consumed': False,
                           'capability_sha256': hashlib.sha256(token.encode()).hexdigest()})
        scripts = str(Path(__file__).resolve().parents[1] / 'scripts')
        with exclusive_lock(m.home / 'runner.lock') as fd:
            code = ('import sys\nfrom pathlib import Path\nfrom types import SimpleNamespace\n'
                    f'sys.path.insert(0,{scripts!r})\n'
                    'from run_accounting_master import Master,validate_internal,MasterError\n'
                    f'm=Master(Path({str(self.root)!r}))\n'
                    f'a=SimpleNamespace(lock_fd={fd},grant={str(grant)!r},capability={token!r},phase="P00",action="_checks")\n'
                    f'validate_internal(m,a,Path({str(output)!r}))\n'
                    'try:\n'
                    f' validate_internal(m,a,Path({str(output)!r}))\n'
                    'except MasterError:\n print("one-use grant enforced")\n'
                    'else:\n raise AssertionError("reused grant accepted")\n')
            result = subprocess.run([sys.executable, '-c', code], pass_fds=(fd,), capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('one-use grant enforced', result.stdout)
            with self.assertRaises(MasterError):
                with exclusive_lock(m.home / 'runner.lock'):
                    self.fail('Child released the supervisor lock')
        self.assertTrue(load_json(grant)['consumed'])

    def test_unknown_or_incomplete_saved_state_is_rejected(self):
        m = self.master()
        m.save()
        original = load_json(m.state_path)
        for mutation in ['status', 'missing', 'hash']:
            state = json.loads(json.dumps(original))
            if mutation == 'status':
                state['phases']['P00']['status'] = 'probably-done'
            elif mutation == 'missing':
                del state['phases']['P00']['attempts']
            else:
                state['phases']['P00']['evidence_hashes'] = {'file': None}
            atomic_json(m.state_path, state)
            with self.assertRaises(ContinuationVeto):
                self.master()
            with self.assertRaises(ContinuationVeto):
                m.reload_state()

    def test_refresh_itself_rejects_changed_controller(self):
        m = self.master()
        with (self.root / CATALOG).open('a') as stream:
            stream.write('\n')
        with self.assertRaises(ContinuationVeto):
            m.refresh()
        self.assertFalse((m.home / 'next-plan.json').exists())

    def test_worker_cannot_create_previously_absent_controls(self):
        def creating(role, phase, packet, folder, attempt):
            atomic_json(folder.parents[1] / 'authorization.json', {'sequential_workers': True})
            return response('PLAN')
        m = self.master(worker=creating)
        folder = m.home / 'runs/guard-test'
        folder.mkdir(parents=True)
        with self.assertRaises(ContinuationVeto):
            m.worker('plan', self.catalog['phases'][0], {}, folder)

    def test_negative_structured_fields_preserve_all_details(self):
        m = self.master(worker=lambda *a: response('REVISE', evidence=[{'file': 'example', 'detail': [1, 2]}], issues=[{'failure': 'test'}]))
        folder = m.home / 'runs/negative-response'
        folder.mkdir(parents=True)
        result = m.worker('review_result', self.catalog['phases'][0], {}, folder)
        self.assertEqual(json.loads(result['evidence'][0]), {'file': 'example', 'detail': [1, 2]})
        self.assertTrue((folder / 'review_result-0.raw-negative-response.json').exists())

    def test_unexpected_controller_exception_vetoes_scheduling(self):
        m = self.master()
        with patch.object(m, 'execute_phase', side_effect=KeyError('broken invariant')):
            self.assertEqual(self.run_quiet(m), 'continuation_veto')
        manifest = load_json(self.root / m.state['runs'][-1] / 'manifest.json')
        self.assertIn('Unexpected controller failure', manifest['stop_reason'])
        self.assertEqual(manifest['phases_attempted'], ['P00'])

    def test_earlier_attempt_files_are_in_final_evidence(self):
        source = self.root / 'scripts/first-attempt.py'
        def earlier(role, phase, packet, folder, attempt):
            if role == 'implement':
                source.write_text('FIRST = 1\n')
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=earlier)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['evidence_hashes']['scripts/first-attempt.py'], digest(source))

    def test_resumed_attempt_files_are_in_final_evidence(self):
        source = self.root / 'scripts/earlier-run.py'
        def earlier(role, phase, packet, folder, attempt):
            if role in {'implement', 'repair'}:
                source.write_text('FIRST = 2\n')
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=earlier)
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertEqual(resumed.state['phases']['P00']['evidence_hashes']['scripts/earlier-run.py'], digest(source))

    def test_resume_excludes_unrelated_intervening_changes_but_retains_own_work(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        unrelated = self.root / 'scripts/other-phase.py'
        unrelated.write_text('VERSION = 0\n')
        owned = self.root / 'scripts/earlier-phase-work.py'
        def partial(role, phase, packet, folder, attempt):
            if role == 'implement':
                owned.write_text('OWNED = True\n')
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            return self.worker(role, phase, packet, folder, attempt)
        initial = self.master(worker=partial)
        self.run_quiet(initial, max_phases=1)
        unrelated.write_text('VERSION = 1\n')
        other_added = self.root / 'scripts/other-new.py'
        other_added.write_text('NEW = True\n')
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        record = resumed.state['phases']['P00']
        self.assertEqual(record['status'], ACCEPTED)
        self.assertIn('scripts/earlier-phase-work.py', record['evidence_hashes'])
        self.assertNotIn('scripts/other-phase.py', record['evidence_hashes'])
        self.assertNotIn('scripts/other-new.py', record['evidence_hashes'])
        unrelated.write_text('VERSION = 2\n')
        other_added.write_text('NEW = False\n')
        resumed.refresh()
        self.assertEqual(record['status'], ACCEPTED)
        owned.write_text('OWNED = False\n')
        resumed.refresh()
        self.assertEqual(record['status'], 'stale')

    def test_timeout_persists_actual_attempt_delta_for_resume(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def timeout(role, phase, packet, folder, attempt):
            if role == 'implement':
                (self.root / 'scripts/timed-out.py').write_text('PARTIAL = True\n')
                raise MasterError('Command failed (timeout)')
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=timeout)
        self.run_quiet(m, max_phases=1)
        record = m.state['phases']['P00']
        delta = load_json(self.root / record['attempts'][-1] / 'execution-0/changes.json')
        self.assertIn('scripts/timed-out.py', delta['added'])
        self.assertIn('scripts/timed-out.py', record['contributed_files'])

    def test_failed_check_contribution_survives_resume(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def failed_check(phase, folder):
            (self.root / 'scripts/check-created.py').write_text('VALUE = 1\n')
            raise MasterError('Test process failed after changing a file')
        m = self.master(check=failed_check)
        self.run_quiet(m, max_phases=1)
        self.assertIn('scripts/check-created.py', m.state['phases']['P00']['contributed_files'])
        resumed = self.master()
        self.run_quiet(resumed, max_phases=1)
        self.assertIn('scripts/check-created.py', resumed.state['phases']['P00']['evidence_hashes'])

    def test_legacy_resume_requires_recorded_attribution(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        def partial(role, phase, packet, folder, attempt):
            if role == 'implement':
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=partial)
        self.run_quiet(m, max_phases=1)
        del m.state['phases']['P00']['contributed_files']
        m.save()
        self.calls.clear()
        resumed = self.master()
        self.assertEqual(self.run_quiet(resumed, max_phases=1), 'continuation_veto')
        self.assertEqual(self.calls, [])
        manifest = load_json(self.root / resumed.state['runs'][-1] / 'manifest.json')
        self.assertIn('contribution attribution', manifest['stop_reason'])

    def test_phase_created_file_deleted_later_requires_restoration(self):
        self.catalog['limits']['max_repairs'] = 0
        atomic_json(self.root / CATALOG, self.catalog)
        source = self.root / 'scripts/created-earlier.py'
        def partial(role, phase, packet, folder, attempt):
            if role == 'implement':
                source.write_text('VALUE = 1\n')
                return response('IMPLEMENTED', evidence=self.write_work(phase, 'broken'))
            return self.worker(role, phase, packet, folder, attempt)
        m = self.master(worker=partial)
        self.run_quiet(m, max_phases=1)
        source.unlink()
        resumed = self.master()
        self.assertEqual(self.run_quiet(resumed, max_phases=1), 'continuation_veto')
        self.assertIn('scripts/created-earlier.py', resumed.state['phases']['P00']['outstanding_deletions'])
        source.write_text('VALUE = 1\n')
        restored = self.master()
        self.run_quiet(restored, max_phases=1)
        self.assertEqual(restored.state['phases']['P00']['status'], ACCEPTED)

    def test_test_side_effect_deletion_cannot_pass(self):
        source = self.root / 'scripts/test-deleted.py'
        source.write_text('PRESERVE = True\n')
        def deleting(phase, folder):
            source.unlink(missing_ok=True)
            return {'passed': True, 'tests': 1}
        m = self.master(check=deleting)
        self.assertEqual(self.run_quiet(m, max_phases=1), 'continuation_veto')
        self.assertIn('scripts/test-deleted.py', m.state['phases']['P00']['outstanding_deletions'])

    def test_test_side_effect_changes_reach_review_and_acceptance(self):
        source = self.root / 'scripts/test-changed.py'
        source.write_text('VALUE = 0\n')
        def modifying(phase, folder):
            source.write_text('VALUE = 1\n')
            return {'passed': True, 'tests': 1}
        m = self.master(check=modifying)
        self.run_quiet(m, max_phases=1)
        packet = next(c[3] for c in self.calls if c[0] == 'review_result')
        self.assertIn('scripts/test-changed.py', packet['actual_changes']['changed'])
        self.assertEqual(m.state['phases']['P00']['evidence_hashes']['scripts/test-changed.py'], digest(source))

    def test_builtin_status_alone_cannot_pass(self):
        self.catalog['phases'][0]['kind'] = 'builtin'
        atomic_json(self.root / CATALOG, self.catalog)
        m = self.master()
        m.builtin_override = lambda p, f: {'status': 'passed'}
        self.run_quiet(m, max_phases=1)
        self.assertEqual(m.state['phases']['P00']['status'], 'needs_repair')

    def test_passed_test_cache_does_not_skip_execution(self):
        m = self.master()
        folder = m.home / 'runs/test-cache'
        folder.mkdir(parents=True)
        atomic_json(m.home / 'controller-tests.json', {'passed': True, 'tests': 100, 'sha256': m.controls})
        def execute(argv, log, seconds):
            log.write_text('Ran 2 tests in 0.01s\n\nOK\n')
        with patch.object(m, 'process', side_effect=execute) as run, redirect_stdout(io.StringIO()):
            m.ensure_controller_tests(folder)
        run.assert_called_once()
        self.assertEqual(load_json(m.home / 'controller-tests.json')['tests'], 2)

    def test_supervisor_review_requires_current_evidence_and_fresh_tests(self):
        m = self.master()
        note = self.root / 'review-note.md'
        note.write_text('All specific findings inspected and verified.\n')
        receipt = {'verdict': 'AGREE', 'issues': [], 'controller_hashes': m.controls,
            'review_kind': 'supervisor_finding_adjudication',
            'finding_dispositions': [{'status': 'repaired_verified', 'reason': 'checked code and regression'}],
            'review_evidence_hashes': {'review-note.md': digest(note)}}
        atomic_json(m.home / 'controller-review.json', receipt)
        folder = m.home / 'runs/adjudication'
        folder.mkdir(parents=True)
        with patch.object(m, 'ensure_controller_tests') as tests, patch.object(m, 'worker') as worker, redirect_stdout(io.StringIO()):
            m.controller_review(folder)
            tests.assert_called_once()
            worker.assert_not_called()
        note.write_text('Changed after adjudication.\n')
        with patch.object(m, 'ensure_controller_tests'), patch.object(m, 'worker', side_effect=MasterError('fresh review required')) as worker:
            with self.assertRaisesRegex(MasterError, 'fresh review required'):
                m.controller_review(folder)
            worker.assert_called_once()

    def test_install_preserves_original_grant_across_repair(self):
        m = self.master()
        home = self.root / 'user-home'
        def policy(rule, command):
            return {'decision': 'allow' if command[:2] == ['python3', str(self.root / 'scripts/run_accounting_master.py')] else 'prompt'}
        with patch('run_accounting_master.Path.home', return_value=home), patch('run_accounting_master.check_rule', side_effect=policy), redirect_stdout(io.StringIO()):
            install_rule(m)
            original = digest(m.home / 'authorization.json')
            m.controls = {**m.controls, 'new-reviewed-control': '0' * 64}
            install_rule(m)
            self.assertEqual(digest(m.home / 'authorization.json'), original)
            receipt = load_json(m.home / 'installation.json')
            receipt['status'] = 'published'
            atomic_json(m.home / 'installation.json', receipt)
            install_rule(m)
            self.assertEqual(load_json(m.home / 'installation.json')['status'], 'complete')
            self.assertEqual(digest(m.home / 'authorization.json'), original)

    def test_recovery_rejects_changed_prepared_candidate(self):
        m = self.master()
        candidate = m.home / 'accdsl-master.rules'
        candidate.write_text('changed')
        atomic_json(m.home / 'installation.json', {'status': 'prepared', 'candidate_sha256': '0' * 64})
        with self.assertRaises(ContinuationVeto):
            install_rule(m)

    def test_pid_reuse_with_remaining_group_vetoes(self):
        m = self.master()
        prior = {'pid': 424242, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 10}
        atomic_json(m.home / 'active-process.json', {'status': 'running', 'identity': prior})
        with patch('run_accounting_master.process_identity', return_value={**prior, 'start_ticks': 99}), \
             patch('run_accounting_master.live_group_members', return_value=[{'pid': 424243}]), \
             patch('run_accounting_master.stop_recovered_group') as stop:
            with self.assertRaises(ContinuationVeto):
                m.recover_process()
            stop.assert_not_called()

    def test_recovery_discovers_late_child_and_polls_delayed_exit(self):
        leader = {'pid': 424242, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 10, 'state': 'S'}
        child = {'pid': 424243, 'pgid': 424242, 'boot_id': boot_identity(), 'start_ticks': 11, 'state': 'S'}
        stopped_leader, stopped_child = {**leader, 'state': 'T'}, {**child, 'state': 'T'}
        fd_members, signals = {}, []
        def acquire(pid):
            fd = os.open(os.devnull, os.O_RDONLY)
            fd_members[fd] = pid
            return fd
        def identity(pid):
            return stopped_leader if pid == leader['pid'] else stopped_child
        def send(fd, sig):
            signals.append((fd_members[fd], sig))
        scans = [[leader], [stopped_leader, child], [stopped_leader, child],
                 [stopped_leader, stopped_child], [stopped_child], [stopped_child], [], []]
        with patch('run_accounting_master.process_identity', side_effect=identity), \
             patch('run_accounting_master.live_group_members', side_effect=scans), \
             patch('run_accounting_master.open_pidfd', side_effect=acquire), \
             patch('run_accounting_master.signal.pidfd_send_signal', side_effect=send), \
             patch('run_accounting_master.time.sleep') as sleep:
            stop_recovered_group(leader)
        self.assertIn((child['pid'], signal.SIGSTOP), signals)
        self.assertIn((child['pid'], signal.SIGKILL), signals)
        self.assertGreaterEqual(sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()
