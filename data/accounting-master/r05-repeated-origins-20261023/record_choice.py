"""One-time additive record of explicit user direction and unselected design."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: str(p.relative_to(R))
bind = lambda p: {'path': rel(p), 'sha256': sha(p)}


def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')


def main():
    assert all(not (U / name).exists() for name in ('choice.json', 'prerequisites.json', 'input-bindings.json'))
    sheets_path = B / 'r05-target-overlap-20261018/target-sheets.json'
    panel_path = R / 'data/financial-report-benchmark/target-panel-v2.json'
    vintage_path = B / 'r05-vintage-admission-20261018/reconciliation.json'
    sheets, panel, vintage = load(sheets_path), load(panel_path), load(vintage_path)
    sheet = next(s for s in sheets['sheets'] if s['id'] == 'repeated_origins')
    assert sheets['selected_design'] is None
    issuers = [{'issuer_id': row['issuer_id'], 'legal_name': row['legal_name'],
                'source_panel_family_label': row['standard_family'], 'financial_mapping_admitted': False}
               for row in panel['issuers']]
    assert len(issuers) == 9 and {i['issuer_id'] for i in issuers} == {f['issuer_id'] for f in vintage['families']}
    assert len(vintage['rows']) == 192 and all(v['selected_byte_available_at'] is None and v['as_of_admission'] is False for v in vintage['rows'])
    choice = {
        'schema': 'accdsl.documentary.e3_direction.v1', 'selected_design': 'repeated_origins',
        'authority': 'explicit user answer in this session on 23 October 2026 Asia/Shanghai',
        'user_answer_verbatim': 'Expected performance at future dates for the same named companies (recommended)',
        'question_context': 'Which forecast claim should AccDSL aim to test: finite historical cells, future dates for same companies, or future companies?',
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'predecessor_target_sheets': bind(sheets_path), 'active_panel': bind(panel_path),
        'selected_target_sheet': sheet, 'named_companies': issuers,
        'membership_resolution': 'Same named companies resolves to the existing active nine-company panel; does not select financial scope or future entry/exit rules',
        'unselected': dict(sheets['unselected']),
        'population_status': {'issuer_membership': 'selected fixed panel',
                              'future_origin_law': None, 'regime_or_stability': None,
                              'deployment_population_admitted': False},
        'forecast_task': {'interval': None, 'cutoff': None, 'origin_grouping': None,
                          'status': 'user preference requested; recommendation is next complete fiscal year with pre-start cutoff'},
        'issuer_weights': {'values': None, 'status': 'user preference requested; recommendation is equal company contribution after existing asset scaling'},
        'frozen_e3': sheets['frozen_e3'], 'historical_vintage_admissions': 0,
        'empirical_execution': False, 'future_issuer_generalization_selected': False,
        'no_inferred_authority': ['runtime', 'new probability law', 'numeric margin/confidence/sample size', 'forecast campaign', 'publication']}
    work = [
        ('E3-R01', 'direction', 'selected', 'user', [], 'User selected named-company repeated future origins; bind exact panel identities.'),
        ('E3-R02', 'forecast interval and cutoff purpose', 'pending_user_preference', 'user_with_concrete_proposal', ['E3-R01'], 'Choose full next fiscal year versus remainder/next interim task; exact per-issuer release/cutoff feasibility remains internal.'),
        ('E3-R03', 'issuer weighting purpose', 'pending_user_preference', 'user_with_concrete_proposal', ['E3-R01'], 'Equal-company recommendation, equal-cell and exposure alternatives compare different objectives; no outcome-driven weights.'),
        ('E3-R04', 'origin law and future regime', 'unresolved', 'internal_design_then_review', ['E3-R02'], 'Specify Q, future-origin process, regime and justified connection to available past evidence; stationarity is a hypothesis.'),
        ('E3-R05', 'eligibility, failure and refit policy', 'unresolved', 'internal_design', ['E3-R02', 'E3-R03'], 'Retain all eligible cells, full failure denominator, declared fallback/refusal, source availability and fitting/tuning history.'),
        ('E3-R06', 'exact-byte origins and first releases', 'unadmitted', 'internal_source_preparation', ['E3-R02'], '192 historical availability admissions stay false; use actual per-version evidence or explicitly different source/origin version.'),
        ('E3-R07', 'same-economics comparator and scores', 'existing_obligations_preserved', 'internal_design', ['E3-R02'], 'Retain full baseline ladder, same information/tuning cap, primary comparator lock, OCF/CRPS and conditional joint targets.'),
        ('E3-R08', 'matched primary inference theory', 'unselected', 'internal_research', ['E3-R03', 'E3-R04', 'E3-R05'], 'Check a theory for weighted panel-loss time dependence and the one-sided margin target; no issuer bootstrap or scalar package default by analogy.'),
        ('E3-R09', 'material improvement margin and decision loss', 'unselected', 'user_objective_then_internal_justification', ['E3-R02', 'E3-R03'], 'Identify use of forecast and cost of errors; derive a defensible margin before test data. Do not invent a business-value percent.'),
        ('E3-R10', 'confidence, multiplicity and sample/resource design', 'unselected', 'internal_design_then_budget_decision_if_needed', ['E3-R06', 'E3-R08', 'E3-R09'], 'Derive level/critical strata/replication and cost from target and error tolerance; source-file count is not sample size.'),
        ('E3-R11', 'future test and runtime execution', 'held', 'later_explicit_scope', ['E3-R05', 'E3-R06', 'E3-R07', 'E3-R08', 'E3-R09', 'E3-R10'], 'Require admitted inputs/design, exact environment, forecast locks and separate execution authority before campaigns.')]
    files = [sheets_path, panel_path, vintage_path,
             B / 'r05-target-overlap-20261018/specification.md',
             B / 'r05-target-overlap-20261018/result.md',
             B / 'r05-dependent-loss-source-20261018/derivation.md',
             B / 'r05-dependent-loss-source-20261018/admission-note.md',
             B / 'r05-dependent-loss-source-20261018/result.md',
             B / 'r05-vintage-admission-20261018/result.md',
             B / 'r05-extraction-profile-20261020/completion.json']
    write('choice.json', choice)
    write('prerequisites.json', {'rows': [{'id': i, 'topic': t, 'status': s, 'owner': o,
                                         'depends_on': deps, 'next_action': action}
                                        for i, t, s, o, deps, action in work],
                                'choice_is_not_empirical_admission': True,
                                'six_legacy_scientific_fields': 'deployment_population (origin law incomplete), weights, improvement_margin, confidence_level, inference_procedure, sample_size',
                                'global_continuation_veto': False})
    write('input-bindings.json', {'bindings': [bind(p) for p in files],
                                'source_use': 'Frozen technical/source notes reused; no new acquisition, original theorem reading or literature survey',
                                'new_mathematics': bind(U / 'derivation.md')})
    print(json.dumps({'selected_design': 'repeated_origins', 'named_companies': len(issuers),
                      'prerequisites': len(work), 'vintage_admissions': 0, 'empirical_execution': False}))


if __name__ == '__main__':
    main()
