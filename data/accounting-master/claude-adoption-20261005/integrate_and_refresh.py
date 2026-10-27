"""Integrate reviewed proposal additions and recover the external-input stop.

No worker launch, controller change, phase acceptance or budget extension.
"""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from run_accounting_master import Master, campaign_remaining, exclusive_lock, now
from accounting_master_support import (atomic_json, changes_since, digest, load_json,
                                       preserve_editable, verify_hashes)
from check_accounting_proposal import check_proposal

REGISTER = 'docs/design/proposal/architecture/claude-adoption-v1.md'
PLAN = 'docs/plans/accounting-claude-adoption-plan-20261005.md'
STAGE = OUT / 'integration'
PRIOR = 'data/accounting-master/runs/20261004T193930-c0aa467d'
COMMON = ('Read ' + REGISTER + ' and its repaired specifications. Original Claude drafts remain '
          'unaccepted review evidence. Adopt structure and checked local examples, not original '
          'pseudocode, unsupported acceptance labels, metrics, page/staffing quotas or paid-review requirements.')
ACTIONS = {
    'P16': [COMMON,
        'Next complete the coherent uncertainty contract: conditioning, duplicate-information protection, likelihood updates and conditional outcomes with representative success/failure examples. The preserved plan at ' + PRIOR + '/P16/plan-0.response.json is useful input but its interrupted review was not accepted; obtain a fresh ordinary plan review. Save substantive sections and return PARTIAL within the worker cutoff.',
        'Reuse completed MA03a/MA04b, MA05c and scalar event_refs supplements. Group routine malformed-field/binding cases in a validation table; do not spend each worker on another standalone malformed-field report.',
        'Then specify accounting/state transitions using methods/standards-mapping-v1.md; language/interfaces using architecture/extraction-contract-v1.md; persistence/failure semantics including replay and resumable frontier state; and the integrated initial profile/dependency order. Paths are relative to docs/design/proposal. These additions alone do not complete accounting or interfaces. Keep all nine contract requirements and independent full-phase result review.'],
    'P17': [COMMON,
        'Use docs/design/proposal/methods/standards-mapping-v1.md, standards-fixtures-v1.json and standards-source-register-v1.json as a checked starting point under their historical source/fact limits. Inspect exact applicable paragraphs and supply the missing lifecycle/exception methods; do not turn journal balance into accounting eligibility.',
        'Specify corporate operations including revenue, leases and tax; debt/equity, groups/FX, banks, insurers, IFRS/US GAAP/ASBE, forecasting and software reuse. Separate initial/later support without dropping mission obligations. Prepare precise proposed answers and checked consequences before any professional review.',
        'Integrate extraction adapter research/evaluation with the retained 192-report corpus and P16 context/time/identity/frontier rules. Compare pinned candidate tools on appropriate tasks; select no FinBERT, accuracy threshold, depth cap or model-ranking claim without target-specific evidence.'],
    'P18': [COMMON,
        'Integrate the repaired standards mapping, source-scoped examples and extraction contract into the governing LaTeX manuscript alongside the completed P16/P17 work. Preserve supported baseline mathematics and explicit content dispositions. Do not copy the defective original chapter formulas or incomplete main TeX as accepted design.',
        'Build one coherent manuscript, inspect the matching rendered PDF and retain exact build/source evidence. There is no 24-chapter or 410-page quota. Explain assumptions and examples in accounting language; ordinary human readability and independent domain acceptance remain separate.'],
    'P19': [COMMON,
        'Check the final manuscript against every adoption disposition in ' + REGISTER + ': repaired acquisition, rates and revenue/cost cases, exact authority/application support, immutable context, frontier/resume, unknowns and honest evidence statuses. Reconcile all MC01–MC35/G1–G18 obligations and the full initial profile with actual P16–P18 evidence.',
        'Require completed independent full-phase result review and no unresolved material proposal decision before readiness. Neither these illustrative checks nor Claude agreement establish production readiness, empirical forecast validity, human acceptance or implementation authorization. Product implementation stays held.'],
}

master = Master(ROOT)
baseline = load_json(OUT / 'baseline.json')
allowed_adoption = {
    PLAN, REGISTER, 'docs/design/proposal/architecture/extraction-contract-v1.md',
    'docs/design/proposal/architecture/extraction-fixtures-v1.json',
    'docs/design/proposal/methods/standards-mapping-v1.md',
    'docs/design/proposal/methods/standards-fixtures-v1.json',
    'docs/design/proposal/methods/standards-source-register-v1.json',
    'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.pdf',
    'docs/design/proposal/methods/sources/aasb15-compiled-dec2022.txt',
}


def preserve_checks():
    review = load_json(master.home / 'controller-review.json')
    result = dict(protected=verify_hashes(ROOT, baseline['protected']),
                  controls=verify_hashes(ROOT, baseline['controls']),
                  controller_review=verify_hashes(ROOT, review['review_evidence_hashes']),
                  external_sources=verify_hashes(ROOT, baseline['external_sources']),
                  accepted={k: verify_hashes(ROOT, v) for k, v in baseline['accepted'].items()})
    if any(result[k] for k in ('protected', 'controls', 'controller_review', 'external_sources')) or any(result['accepted'].values()):
        raise RuntimeError('Preservation failed: ' + json.dumps(result))
    return result


def ref(name, locator):
    return dict(path=name, sha256=digest(ROOT / name), locator=locator)


with exclusive_lock(master.home / 'campaign.lock'):
    with exclusive_lock(master.home / 'runner.lock'):
        master.recover_process()
        master.reload_state()
        campaign = load_json(master.home / 'campaign.json')
        if (campaign['status'] != 'continuation_veto' or campaign.get('supervisor') is not None
                or campaign['deadline_monotonic'] != baseline['original_deadline_monotonic']
                or campaign_remaining(campaign) <= 0):
            raise RuntimeError('Campaign ownership, status or original deadline needs investigation')
        pre_protection = preserve_checks()
        delta = changes_since(ROOT, baseline['snapshot'])
        if delta['deleted'] or any(name not in allowed_adoption for key in ('added', 'changed') for name in delta[key]):
            raise RuntimeError('Unexpected concurrent editable changes: ' + json.dumps(delta))
        diagnostic = load_json(OUT / 'diagnostics.json')
        if not diagnostic['passed'] or verify_hashes(ROOT, diagnostic['inputs']):
            raise RuntimeError('The checked adoption examples changed')
        failure = load_json(ROOT / PRIOR / 'P16/review_plan-0.integrity-failure.json')
        if failure['verification_error'] != 'Changed outside role/write scope: docs/design/claude_suggestion/RESPONSE_TO_CODEX_REVIEW.md':
            raise RuntimeError('The interrupted review has an unexplained finding')
        if (ROOT / PRIOR / 'P16/approved-plan.json').exists():
            raise RuntimeError('Unexpected approved plan at interrupted review')
        old_review_files = {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / PRIOR / 'P16').glob('review_plan-0.*')}
        STAGE.mkdir(exist_ok=False)
        atomic_json(STAGE / 'pre-edit-files.json', preserve_editable(ROOT, master.home / 'prior-bytes'))
        for name in ('data/accounting-master/state.json', 'data/accounting-master/campaign.json',
                     'data/accounting-master/next-plan.json', 'data/accounting-master/next-plan.md',
                     'data/accounting-master/deliverables/P16/architecture.json',
                     'data/accounting-master/deliverables/P16/result.md',
                     'data/accounting-master/deliverables/P16/progress.md',
                     'docs/plans/accounting-master-checkpoint.md'):
            destination = STAGE / 'before' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, destination)

        evidence = [ref(REGISTER, 'Adoption table; phase obligations and remaining acceptance'),
            ref('docs/design/proposal/architecture/extraction-contract-v1.md', 'Eight stages; context, clocks, frontier/resume, review and failure'),
            ref('docs/design/proposal/architecture/extraction-fixtures-v1.json', 'X01–X12 specified examples'),
            ref('docs/design/proposal/methods/standards-mapping-v1.md', 'Method structure; source scope; corrected transactions'),
            ref('docs/design/proposal/methods/standards-fixtures-v1.json', 'A01–A08, R01–R04, C01–C03, D01–D03 and negative controls'),
            ref('docs/design/proposal/methods/standards-source-register-v1.json', 'Exact retained S9/S15 versions, inspected paragraphs and limits'),
            ref('data/accounting-master/claude-adoption-20261005/diagnostics.json', '109 deterministic specification checks; no runtime acceptance')]
        for source in load_json(ROOT / 'docs/design/proposal/methods/standards-source-register-v1.json')['sources']:
            for kind in ('pdf', 'text'):
                evidence.append(ref(source[kind]['path'], source['id'] + ' retained source; see source register for inspected anchors'))
        p = ROOT / 'data/accounting-master/deliverables/P16/architecture.json'
        architecture = load_json(p)
        previous_contracts = architecture['contracts']
        previous_profile = architecture['initial_profile']
        known = {r['path'] for r in architecture['source_evidence']}
        architecture['source_evidence'].extend(r for r in evidence if r['path'] not in known)
        architecture['claude_adoption_bounded_work'] = dict(
            status='author_checked_proposed_additions_pending_full_phase_review', evidence=evidence,
            requirements=['MC01', 'MC02', 'MC03', 'MC04', 'MC05', 'MC06', 'MC07', 'MC08', 'MC10',
                          'MC16', 'MC17', 'MC20', 'MC21', 'MC22', 'MC23', 'MC25', 'MC27', 'MC28',
                          'MC29', 'MC30', 'MC32', 'MC33', 'MC34', 'MC35'],
            contract_registered=False, architecture_selected=False, product_implemented=False,
            human_acceptance='pending', integration_obligations=ACTIONS,
            interrupted_review_disposition='Preserved, not accepted; fresh ordinary plan review required')
        architecture['next_bounded_task'] = ACTIONS['P16'][1] + ' Follow ' + REGISTER + ' for subsequent groups.'
        architecture['limitations'] += (' Repaired extraction and standards-mapping additions are registered as partial work; '
                                       'they do not complete accounting/interfaces or resolve the initial profile.')
        if architecture['contracts'] != previous_contracts or architecture['initial_profile'] != previous_profile:
            raise RuntimeError('Adoption must not promote contract/profile status')
        atomic_json(p, architecture)

        p16 = ROOT / 'data/accounting-master/deliverables/P16'
        (p16 / 'result.md').write_text(
            '# P16 current result — Claude adoption intake, 5 October 2026\n\n'
            'P16 remains partial: three complete proposed rows (evidence, time, history families), '
            'six unfinished contracts, an unresolved initial profile and fourteen open decisions. '
            'Existing uncertainty supplements remain saved; no phase acceptance is asserted.\n\n'
            'The supervisor reviewed Claude\'s response and executed the audited adoption plan. '
            'Repaired extraction and standards-mapping specifications, fixtures and exact source '
            'registers are linked in architecture.json as partial work. The 109 deterministic '
            'example checks and 17 existing proposal tests pass. See ' + REGISTER + ' and '
            'data/accounting-master/claude-adoption-20261005/result.md for substance, sources, '
            'commands, skeptical review and limitations. These checks establish no runtime, '
            'professional accounting or empirical forecast validity.\n\n'
            'Run 20261004T193930-c0aa467d stopped because RESPONSE_TO_CODEX_REVIEW.md appeared '
            'during a read-only plan review. No editable worker ran. The returned AGREE remains '
            'unaccepted; the next invocation must obtain a fresh plan review. Both the old review '
            'and full prior result remain unchanged. The latter is retained at '
            'data/accounting-master/claude-adoption-20261005/before/data/accounting-master/'
            'deliverables/P16/result.md.\n\n'
            'Next: complete coherent uncertainty sections, then integrate accounting, extraction '
            'interfaces, persistence/failure behavior and profile decisions. Keep full independent '
            'P16 acceptance mandatory. E05 real-source conflict and all wider mission gaps remain '
            'open. Product implementation stays disabled.\n')
        (p16 / 'progress.md').write_text(
            '# P16 current progress — 5 October 2026\n\n'
            'The Claude adoption work is saved and checked; its active register is ' + REGISTER + '. '
            'Architecture now references the repaired extraction contract, standards template and '
            'examples without registering either accounting or interfaces as complete.\n\n'
            'Three complete proposed contract rows remain evidence, time and history_families. '
            'Uncertainty, accounting, language_ir, persistence, interfaces and failure_semantics '
            'remain unfinished, as do initial-profile selection and fourteen decisions.\n\n'
            'Next substantive task: integrated uncertainty semantics (conditioning, likelihood '
            'updates, duplicate-information protection and conditional outcomes). Obtain a fresh '
            'normal plan review; the prior AGREE was interrupted by an external file addition. '
            'Reuse saved MA03a/MA04b, MA05c and scalar event_refs supplements. Group routine '
            'schema failures and save substantive sections within the worker time budget.\n\n'
            'The bounded 109-check specification diagnostic and 17 proposal tests pass. '
            'Full P16 structural/independent acceptance remains pending. Prior progress/result '
            'bytes are preserved under data/accounting-master/claude-adoption-20261005/before/. '
            'The original campaign deadline and one initial attempt plus five retries remain. '
            'No product runtime, professional engagement or broad acceptance is authorized.\n')

        checkpoint = ROOT / 'docs/plans/accounting-master-checkpoint.md'
        checkpoint.write_text(
            '# Accounting master checkpoint\n\n'
            'Updated 5 October 2026 after review and repair of Claude\'s response. The active '
            'task is to finish the governing proposal before selecting product implementation. '
            '**P15 is accepted internally; P16 is partial; P17–P19 remain pending.**\n\n'
            '## Adopted changes and checked evidence\n\n'
            'Use the [adoption register](../design/proposal/architecture/claude-adoption-v1.md) '
            'and [audited plan](accounting-claude-adoption-plan-20261005.md). Repaired extraction '
            'and standards-mapping specifications are now P16 inputs and explicit P17–P19 '
            'obligations. Journals, rates, cumulative costs, receipt decisions, context and '
            'reference-frontier examples pass 109 deterministic checks; 17 proposal tests pass. '
            'See `data/accounting-master/claude-adoption-20261005/result.md` for commands, source '
            'scope and skeptical review. These are proposal checks, not product implementation '
            'or professional accounting acceptance. No page, staffing, model or performance '
            'quota from the original Claude drafts is adopted.\n\n'
            '## Recovery and next action\n\n'
            'Run `20261004T193930-c0aa467d` stopped at 19:52 UTC on 4 October because '
            '`RESPONSE_TO_CODEX_REVIEW.md` appeared during read-only review. No editable worker '
            'ran. Its returned AGREE was rejected by the integrity guard and remains unaccepted. '
            'The supervisor has incorporated the external input while the campaign is stopped; '
            'the next execution requires a fresh ordinary plan review. Original files, interrupted '
            'records, controller and accepted evidence are preserved. Integration/continuation '
            'checks are in `data/accounting-master/claude-adoption-20261005/integration/`.\n\n'
            'Next complete the coherent uncertainty contract: conditioning, likelihood updates, '
            'duplicate-information protection and conditional outcome payloads. Reuse completed '
            'supplements; group ordinary field errors. Then integrate accounting/state transitions, '
            'language/extraction interfaces, persistence/failure behavior and profile decisions. '
            'Three complete proposed contract rows remain evidence, time and history families; '
            'six contracts, the initial profile and fourteen decisions remain unfinished. '
            'E05 real-source conflict and full independent phase review remain open.\n\n'
            '## Existing authorization and execution\n\n'
            'The original 48-hour allowance began at 2026-10-04 16:29:46 UTC and ends nominally '
            'at 7 October 00:29 Hong Kong. Stored monotonic deadline `1940875.230219879` on boot '
            '`ffea3b13-9fd0-447f-87a1-8f419eed8a63` is authoritative; preparation consumes it and '
            'resume never resets it. One initial editable attempt plus five retries per execution '
            'remains the limit. Use the existing exact approved command:\n\n'
            '```text\npython3 /home/chakwong/python/AccDSL/scripts/run_accounting_master.py campaign --max-seconds 172800\n```\n\n'
            'Live status belongs to `data/accounting-master/campaign.json`, `state.json`, '
            '`active-process.json` and `next-plan.json`; check process ownership and locks before '
            'any restart. Do not start a second copy. Use one writer per worktree; a subdirectory '
            'does not isolate concurrent authoring. The campaign stops on invalid evidence, '
            'integrity failure, no-progress or exhausted budget. No completion-time promise is made.\n\n'
            'The frozen product checkpoint and 192-report corpus remain unchanged. All '
            'MC01–MC35/G1–G18 obligations survive staging. Product implementation remains '
            'disabled, and no paid review or external publication is authorized. The full prior '
            'master checkpoint is retained in `data/accounting-master/claude-adoption-20261005/'
            'before/docs/plans/accounting-master-checkpoint.md`.\n')

        checked = check_proposal(ROOT, 'P16')
        if checked['errors'] != ['whole architecture contracts']:
            raise RuntimeError('Unexpected structural check: ' + json.dumps(checked['errors']))
        atomic_json(STAGE / 'checks.json', checked)
        record = master.state['phases']['P16']
        record.update(status='needs_repair', issues=['Six whole-product contracts and integrated initial profile remain unfinished; repaired Claude additions are partial specifications.'], next_actions=ACTIONS['P16'])
        contributions = {REGISTER, 'docs/design/proposal/architecture/extraction-contract-v1.md',
            'docs/design/proposal/architecture/extraction-fixtures-v1.json',
            'data/accounting-master/deliverables/P16/architecture.json',
            'data/accounting-master/deliverables/P16/result.md', 'data/accounting-master/deliverables/P16/progress.md'}
        record['contributed_files'] = sorted(set(record.get('contributed_files', [])) | contributions)
        for phase in ('P17', 'P18', 'P19'):
            master.state['phases'][phase]['next_actions'] = list(dict.fromkeys(ACTIONS[phase] + master.state['phases'][phase].get('next_actions', [])))
        master.run_id = 'supervisor-claude-adoption-20261005'
        master.save_continuation(master.phases['P16'], record, STAGE, checked,
            'External response inspected; repaired adoption candidates checked and registered. Interrupted AGREE unaccepted; fresh plan review required.', ACTIONS['P16'])
        master.state['last_outcome'] = dict(phase='P16', status='needs_repair',
            issues=record['issues'], stop_reason='supervisor_adoption_complete_fresh_plan_review_required',
            prior_run=PRIOR, adoption=REGISTER)
        master.save()
        plan = master.refresh()
        if plan['next_phase'] != 'P16' or plan['proposal_gate']['ready']:
            raise RuntimeError('Unexpected next phase or readiness')
        protection = preserve_checks()
        review_errors = verify_hashes(ROOT, old_review_files)
        continuation = load_json(ROOT / record['continuation'])
        continuation_errors = verify_hashes(ROOT, continuation['evidence_hashes'])
        if (review_errors or continuation_errors or load_json(master.home / 'campaign.json')['deadline_monotonic'] != baseline['original_deadline_monotonic']):
            raise RuntimeError('Post-integration preservation/deadline failure')
        recovery = dict(recorded_at=now(), recovery_complete=True, acceptance=False,
            prior_run=PRIOR, interrupted_review_preserved=old_review_files, interrupted_review_accepted=False,
            adoption=REGISTER, next_actions=ACTIONS, protection=protection,
            continuation_errors=continuation_errors, protected_count=len(baseline['protected']),
            external_source_count=len(baseline['external_sources']), accepted_phases=list(baseline['accepted']),
            original_deadline_monotonic=campaign['deadline_monotonic'], remaining_seconds=campaign_remaining(campaign),
            next_phase=plan['next_phase'], plan_generation=plan['generation'],
            structural_check={k: checked[k] for k in ('passed', 'tests', 'errors')},
            structural_checks_passed=sum(c['passed'] for c in checked['checks']),
            product_implementation_enabled=False)
        atomic_json(STAGE / 'recovery.json', recovery)
        master.event('supervisor_claude_adoption_integrated', phase='P16', adoption=REGISTER,
                     continuation=record['continuation'], next_plan_generation=plan['generation'])
        print(json.dumps(dict(recovery_complete=True, next_phase=plan['next_phase'],
            checked=checked['tests'], errors=checked['errors'], preservation_errors=0,
            remaining_hours=round(recovery['remaining_seconds'] / 3600, 2))))
