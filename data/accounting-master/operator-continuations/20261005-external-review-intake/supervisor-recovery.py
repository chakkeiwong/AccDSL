"""Recover the recorded external-document interference; no controller edits."""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path('/home/chakwong/python/AccDSL')
sys.path.insert(0, str(ROOT / 'scripts'))
from run_accounting_master import Master, exclusive_lock, campaign_remaining, now
from accounting_master_support import atomic_json, digest, load_json, preserve_editable, verify_hashes
from check_accounting_proposal import check_proposal

master = Master(ROOT)
home = master.home
stage = home / 'operator-continuations/20261005-external-review-intake'
review_path = 'docs/plans/accounting-claude-suggestion-review-20261005.md'
actions = [
    'Read ' + review_path + '. Preserve the supplied Claude drafts as unaccepted review input; confirmed findings guide P16/P17/P18, not new product implementation or paid review.',
    'Create a reviewed plan for coherent remaining P16 contract groups. Next: integrate the uncertainty contract, including conditioning, duplicate-evidence handling, likelihood updates and conditional outcome payloads, with representative success/failure examples. Budget the group into substantive sections that can save and return PARTIAL within the enforced cutoff; do not try to write all contracts in one worker.',
    'The MA03a/MA04b, MA05c and scalar event_refs supplements are saved. Their count bookkeeping is repaired. Do not repeat them or make another standalone report for each malformed field. Group remaining schema/binding rejections in a common validation table and reserve separate fixtures for distinct semantic failure modes.',
    'Sequence accounting/state transitions, language/interfaces, persistence/failure behavior, then initial-profile and integration decisions. Reconcile the repaired extraction design with evidence/time contracts, preserve all mission domains and keep independent full-phase result review mandatory.',
]

with exclusive_lock(home / 'campaign.lock'):
    with exclusive_lock(home / 'runner.lock'):
        master.recover_process()
        master.reload_state()
        campaign = load_json(home / 'campaign.json')
        if campaign['status'] != 'continuation_veto' or campaign.get('supervisor') is not None:
            raise RuntimeError('Unexpected campaign state; inspect before recovery')
        if campaign_remaining(campaign) <= 0:
            raise RuntimeError('The original campaign allowance has expired')
        original_deadline = campaign['deadline_monotonic']
        external = load_json(home / 'claude-suggestion-review-20261005/diagnostics.json')['inputs']
        baseline = load_json(home / 'campaign-20261005/baseline.json')
        receipt = load_json(home / 'controller-review.json')
        protection = {
            'original_protected': verify_hashes(ROOT, baseline['protected']),
            'controller': verify_hashes(ROOT, receipt['controller_hashes']),
            'controller_review': verify_hashes(ROOT, receipt['review_evidence_hashes']),
            'external_review': verify_hashes(ROOT, external),
            'accepted': {k: verify_hashes(ROOT, v['evidence_hashes']) for k, v in master.state['phases'].items() if v['status'] == 'accepted_internal'},
        }
        if any(protection[k] for k in ('original_protected', 'controller', 'controller_review', 'external_review')) or any(protection['accepted'].values()):
            raise RuntimeError('Recovery protection failed: ' + json.dumps(protection))
        stage.mkdir(parents=True, exist_ok=False)
        snapshot = preserve_editable(ROOT, home / 'prior-bytes')
        atomic_json(stage / 'pre-edit-files.json', snapshot)
        for name in ['data/accounting-master/state.json', 'data/accounting-master/campaign.json',
                     'data/accounting-master/next-plan.json', 'data/accounting-master/next-plan.md',
                     'data/accounting-master/deliverables/P16/architecture.json',
                     'data/accounting-master/deliverables/P16/result.md',
                     'data/accounting-master/deliverables/P16/progress.md',
                     'docs/plans/accounting-master-checkpoint.md']:
            destination = stage / 'before' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)
        atomic_json(stage / 'external-review-inputs.json', {'files': external, 'review': review_path, 'review_sha256': digest(ROOT / review_path), 'interpretation': 'External supplied draft; no source, accounting or design acceptance inferred'})
        original_run = home / 'runs/20261004T164123-d391f42d/P16/execution-2'
        original_changes = load_json(original_run / 'changes.json')
        scope = master.catalog['workflow']['phase_policy']['P16']['write_scope']
        def allowed(name):
            return any(name.startswith(s) if s.endswith('/') else name == s for s in scope)
        inside = [n for group in original_changes.values() for n in group if allowed(n)]
        outside = [n for group in original_changes.values() for n in group if not allowed(n)]
        if set(outside) != {n for n in original_changes['added'] if n.startswith('docs/design/claude_suggestion/')}:
            raise RuntimeError('Unexplained out-of-scope change')
        result = ROOT / 'data/accounting-master/deliverables/P16/result.md'
        old = ('stale-diagnostic hashes and 152 unchanged saved structural inputs. The remaining\n'
               'prior structural input was progress.md, intentionally updated at task start.')
        new = ('stale-diagnostic hashes and all 153 saved structural inputs at initial recovery.\n'
               'progress.md was not among those inputs. After the architecture/result edits,\n'
               '151 prior structural inputs remained unchanged, as the final integrity record states.')
        text = result.read_text()
        if old not in text:
            raise RuntimeError('Result text differs from reviewed correction')
        result.write_text(text.replace(old, new))
        progress = ROOT / 'data/accounting-master/deliverables/P16/progress.md'
        old = ('architecture pins, ten old diagnostic hashes and 152 unchanged structural inputs;\n'
               'progress.md was already intentionally edited.')
        new = ('architecture pins, ten old diagnostic hashes and all 153 prior structural inputs\n'
               'at initial recovery; progress.md was not among those inputs. After the\n'
               'architecture/result edits, 151 prior structural inputs remained unchanged.')
        text = progress.read_text()
        if old not in text:
            raise RuntimeError('Progress text differs from reviewed correction')
        progress.write_text(text.replace(old, new) + '\nSupervisor continuation, 5 October: the external-document interference was\ninspected and the recovery count corrected. Next planning follows\n' + review_path + '\nfor coherent contract sections and representative rejection cases. The ordinary\nindependent plan review and full P16 acceptance criteria still apply.\n')
        architecture = ROOT / 'data/accounting-master/deliverables/P16/architecture.json'
        value = load_json(architecture)
        prior_task = value['next_bounded_task']
        value['next_bounded_task'] = actions[1] + ' See ' + review_path + '. ' + actions[2]
        atomic_json(architecture, value)
        checkpoint = ROOT / 'docs/plans/accounting-master-checkpoint.md'
        addition = ('\n## Latest supervisor review — 5 October 2026\n\n'
                    'Claude\'s proposed Version 2 was inspected against current evidence. See\n'
                    '[the findings and planning correction](accounting-claude-suggestion-review-20261005.md).\n'
                    'Use its useful standards/extraction structure as draft material after repair;\n'
                    'do not adopt its Reviewed/complete labels, page quota or resource estimates.\n\n'
                    'The campaign stopped at 01:55 Hong Kong because five external Claude files\n'
                    'were added during P16 work, triggering the unchanged write-scope guard.\n'
                    'The third worker completed with exit 0 in 823.827 seconds and saved the\n'
                    'scalar event_refs comparison. Its 298 checks were independently rerun by\n'
                    'the supervisor. A disclosed recovery-count error is corrected; the old\n'
                    'bytes and exact interruption evidence are retained. Frozen, accepted-phase\n'
                    'and controller evidence pass preservation checks. Resume under the same\n'
                    '48-hour deadline after recovery; product implementation remains disabled.\n\n'
                    'Next planning should integrate substantive contract sections with representative\n'
                    'examples, beginning with uncertainty, conditioning and conditional outcomes.\n'
                    'Group remaining ordinary malformed-field cases instead of creating a separate\n'
                    'campaign deliverable for each. Full independent phase review remains required.\n'
                    'Concurrent authors should use a separate workspace and import between runs.\n'
                    'The state-at-campaign-entry and earlier next-task sections below are historical.\n')
        checkpoint.write_text(checkpoint.read_text().replace('# Accounting master checkpoint\n', '# Accounting master checkpoint\n' + addition, 1))
        checked = check_proposal(ROOT, 'P16')
        if checked.get('errors') != ['whole architecture contracts']:
            raise RuntimeError('Unexpected P16 validation outcome: ' + json.dumps(checked.get('errors')))
        atomic_json(stage / 'checks.json', checked)
        record = master.state['phases']['P16']
        record['contributed_files'] = sorted(set(record['contributed_files']) | set(inside))
        record.update(status='needs_repair', issues=['Six whole-product contracts and integrated profile remain unfinished. External-document interference was investigated; see ' + review_path], next_actions=actions)
        master.run_id = 'supervisor-external-review-intake-20261005'
        master.save_continuation(master.phases['P16'], record, stage, checked,
                                 'External additions reviewed and retained; saved P16 work rechecked, count corrected, contract-group replanning required.', actions)
        master.state['last_outcome'] = {'phase': 'P16', 'status': 'needs_repair', 'issues': record['issues'], 'stop_reason': 'supervisor_recovery_complete_replan_required', 'prior_run': '20261004T164123-d391f42d'}
        master.save()
        plan = master.refresh()
        if plan['next_phase'] != 'P16':
            raise RuntimeError('Unexpected next eligible phase')
        errors = verify_hashes(ROOT, baseline['protected']) + verify_hashes(ROOT, receipt['controller_hashes']) + verify_hashes(ROOT, receipt['review_evidence_hashes']) + verify_hashes(ROOT, external)
        for r in master.state['phases'].values():
            if r['status'] == 'accepted_internal':
                errors += verify_hashes(ROOT, r['evidence_hashes'])
        if errors or load_json(home / 'campaign.json')['deadline_monotonic'] != original_deadline:
            raise RuntimeError('Post-recovery protection/deadline verification failed')
        recovery = {'checked_at': now(), 'recovery_complete': True, 'acceptance': False,
                    'prior_run': '20261004T164123-d391f42d', 'external_changes': outside,
                    'p16_contributions_recovered': inside, 'prior_next_task': prior_task,
                    'next_actions': actions, 'protection': protection, 'post_protection_errors': errors,
                    'deadline_monotonic': original_deadline, 'remaining_seconds': campaign_remaining(campaign),
                    'p16_checker': {k:checked[k] for k in ('passed','tests','errors')},
                    'next_plan_generation': plan['generation'], 'review_path':review_path,
                    'external_snapshot':str((stage/'external-review-inputs.json').relative_to(ROOT)),
                    'preserved_original_work_process':str((original_run/'repair-2.process.json').relative_to(ROOT))}
        atomic_json(stage / 'recovery.json', recovery)
        master.event('supervisor_external_review_recovered', phase='P16', review=review_path, next_plan_generation=plan['generation'])
        print(json.dumps({'recovery_complete': True, 'errors': errors, 'checks':recovery['p16_checker'], 'remaining_hours':round(recovery['remaining_seconds']/3600,2),'next_phase':plan['next_phase']}))
