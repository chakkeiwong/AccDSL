"""Queue the approved uncertainty review after the bounded-handoff repair."""
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from run_accounting_master import Master, campaign_remaining, exclusive_lock, now, stable_hash
from accounting_master_support import atomic_json, digest, load_json, preserve_editable, verify_hashes
from check_accounting_proposal import check_proposal

master = Master(ROOT)
baseline = load_json(OUT / 'baseline.json')
prior = ROOT / 'data/accounting-master/runs/20261004T202513-2bc09c08/P16'
stage = OUT / 'pending-uncertainty-review'

with exclusive_lock(master.home / 'campaign.lock'):
    with exclusive_lock(master.home / 'runner.lock'):
        master.recover_process()
        master.reload_state()
        campaign = load_json(master.home / 'campaign.json')
        if (campaign['status'] != 'needs_supervisor_repair' or campaign.get('supervisor') is not None
                or campaign['deadline_monotonic'] != baseline['original_deadline_monotonic']
                or campaign_remaining(campaign) <= 0):
            raise RuntimeError('Campaign state/deadline needs investigation')
        errors = verify_hashes(ROOT, baseline['protected']) + verify_hashes(ROOT, baseline['external_sources'])
        for hashes in baseline['accepted'].values():
            errors += verify_hashes(ROOT, hashes)
        if errors:
            raise RuntimeError('Preservation failed: ' + json.dumps(errors))
        for name, count in [('controller-tests-final.log', 180), ('proposal-tests.log', 17)]:
            log = (OUT / name).read_text()
            if f'Ran {count} tests' not in log or not log.rstrip().endswith('OK'):
                raise RuntimeError('Required tests did not pass: ' + name)
        record = master.state['phases']['P16']
        if record['status'] != 'blocked_external' or record.get('outstanding_deletions'):
            raise RuntimeError('Unexpected P16 recovery state')
        checked = check_proposal(ROOT, 'P16')
        if checked['errors'] != ['whole architecture contracts']:
            raise RuntimeError('Unexpected current P16 structural failure: ' + json.dumps(checked['errors']))
        approved = load_json(prior / 'execution-3/approved-plan.json')
        if approved['plan_hash'] != stable_hash(approved['plan']) or approved['review']['verdict'] != 'AGREE':
            raise RuntimeError('The saved independent-review plan is not approved')
        work = load_json(prior / 'execution-2/repair-2.response.json')
        if work['verdict'] != 'PARTIAL':
            raise RuntimeError('Unexpected saved work result')
        stage.mkdir(exist_ok=False)
        atomic_json(stage / 'pre-edit-files.json', preserve_editable(ROOT, master.home / 'prior-bytes'))
        atomic_json(stage / 'checks.json', checked)
        shutil.copy2(prior / 'execution-3/approved-plan.json', stage / 'approved-plan.json')
        shutil.copy2(prior / 'execution-2/repair-2.response.json', stage / 'saved-work.response.json')

        # The old blocked attempt remains intact. Only current dispatch state changes.
        record.update(status='needs_review',
            issues=['Independent review of the saved uncertainty group is pending; the dispatch mismatch is repaired.'],
            next_actions=['Resume the approved independent uncertainty review read-only. If REVISE, repair the first material finding; if AGREE, plan accounting/state-transition specifications.'])
        record.pop('block_signature', None)
        record.pop('deferred_signature', None)
        master.run_id = 'supervisor-partial-review-handoff-20261005'
        master.state['last_outcome'] = dict(phase='P16', status='needs_review',
            stop_reason='bounded_review_dispatch_repaired',
            issues=record['issues'], prior_run='20261004T202513-2bc09c08')
        master.save()
        packet = dict(approved=approved, work=work, checks=checked,
            review_scope='bounded_partial_work',
            review_question='Independently assess the completed uncertainty contract, UC01–UC19, chaining and current assessment against the approved review plan. The assessment is author work, not an accepted independent verdict. Whole-phase incompleteness remains explicit.',
            current_limits='Five counterpart contracts, initial profile and fourteen decisions remain unfinished. Bounded AGREE cannot accept P16 or enable product implementation.',
            next_plan=master.refresh_worker_plan(),
            original_criteria=master.phases['P16']['criteria'],
            work_path=str((stage / 'saved-work.response.json').relative_to(ROOT)),
            approved_plan_path=str((stage / 'approved-plan.json').relative_to(ROOT)),
            preserved_inputs=str((stage / 'pre-edit-files.json').relative_to(ROOT)),
            check_path=str((stage / 'checks.json').relative_to(ROOT)),
            continuation=load_json(ROOT / record['continuation']))
        saved = master.save_pending_review(master.phases['P16'], record, packet, stage)
        if master.load_pending_review(master.phases['P16'], record) is None:
            raise RuntimeError('The prepared bounded review cannot resume')
        master.save_continuation(master.phases['P16'], record, stage, checked,
            'Controller routing repaired; current uncertainty evidence queued for the already-approved independent bounded review.', record['next_actions'])
        plan = master.refresh()
        if plan['next_phase'] != 'P16' or plan['proposal_gate']['ready']:
            raise RuntimeError('Unexpected phase eligibility or readiness')

        checkpoint = ROOT / 'docs/plans/accounting-master-checkpoint.md'
        old = checkpoint.read_text()
        header = ('\n## Current status — 5 October, bounded review handoff repaired\n\n'
            'The preceding run stopped at 05:55 Hong Kong after saving the uncertainty '
            'contract, its chaining repair and an author assessment. Four proposed P16 '
            'contracts now exist; five contracts, the initial profile and fourteen decisions '
            'remain unfinished. P17–P19 are pending. The earlier adoption status below is historical.\n\n'
            'The controller had gated bounded review on full-phase structural success and '
            'dispatched repair workers for the requested review. This routing failure is now '
            'repaired and tested: 180 controller tests and 17 proposal tests pass. Bounded '
            'reviews persist and resume read-only; their verdict cannot accept the full phase. '
            'Current P16 evidence is queued for the previously approved independent review. '
            'The changed controller still requires its ordinary startup review before phase work.\n\n'
            'See [the repair plan](accounting-master-partial-review-handoff-20261005.md) and '
            '`data/accounting-master/partial-review-handoff-20261005/` for preserved baseline, '
            'tests and pending-review hashes. The original campaign deadline is unchanged; '
            'use the same approved campaign command. Live state remains authoritative.\n')
        checkpoint.write_text(old.replace('# Accounting master checkpoint\n', '# Accounting master checkpoint\n' + header, 1))
        preservation = verify_hashes(ROOT, baseline['protected']) + verify_hashes(ROOT, baseline['external_sources'])
        for hashes in baseline['accepted'].values():
            preservation += verify_hashes(ROOT, hashes)
        preservation += verify_hashes(ROOT, saved['evidence_hashes'])
        if preservation or load_json(master.home / 'campaign.json')['deadline_monotonic'] != baseline['original_deadline_monotonic']:
            raise RuntimeError('Post-recovery evidence/deadline mismatch')
        git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
        receipt = dict(recorded_at=now(), status='prepared_for_startup_controller_review',
            phase='P16', next_phase=plan['next_phase'], acceptance=False,
            controller_review_pending=True, independent_uncertainty_review_pending=True,
            original_deadline_monotonic=campaign['deadline_monotonic'], remaining_seconds=campaign_remaining(campaign),
            preservation_errors=preservation, pending_review=record['pending_review'],
            pending_review_sha256=record['pending_review_sha256'], pending_evidence_files=len(saved['evidence_hashes']),
            checker={'tests':checked['tests'],'passed':checked['passed'],'errors':checked['errors']},
            manifest={'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable',
                'working_tree':'dirty; exact changed controls and test logs pinned',
                'environment':platform.python_implementation()+' '+platform.python_version(),
                'cpu_gpu':'CPU standard library; no GPU/framework import or detection', 'seeds':'N/A: deterministic control tests',
                'data_version':'Saved P16 uncertainty group and phase-scoped control test fixtures',
                'commands':['python3 -m unittest discover -s tests -p test_accounting_master.py',
                            'python3 -m unittest discover -s tests -p test_accounting_proposal.py'],
                'wall_time':'180 controller tests: see controller-tests-final.log; 17 proposal tests: see proposal-tests.log',
                'plan':'docs/plans/accounting-master-partial-review-handoff-20261005.md',
                'result':str((OUT/'recovery.json').relative_to(ROOT))},
            hashes={str(p.relative_to(ROOT)):digest(p) for p in [
                ROOT/'scripts/run_accounting_master.py',ROOT/'tests/test_accounting_master.py',
                ROOT/'docs/plans/accounting-master-program.md',
                ROOT/'docs/plans/accounting-master-partial-review-handoff-20261005.md',
                OUT/'controller-tests-final.log',OUT/'proposal-tests.log',Path(__file__).resolve()]})
        atomic_json(OUT / 'recovery.json', receipt)
        master.event('bounded_review_dispatch_recovered', phase='P16', pending_review=record['pending_review'])
        print(json.dumps(dict(prepared=True, next_phase='P16', pending_evidence_files=len(saved['evidence_hashes']),
            preservation_errors=preservation, remaining_hours=round(campaign_remaining(campaign)/3600,2))))
