"""Exact, conditional design examples; not an issuer or legal classifier."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
from copy import deepcopy
import json
import os
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = OUT / 'apple-contract-source'

class Invalid(ValueError):
    pass

class Unsupported(ValueError):
    pass

def truth(f, key):
    value = f.get(key)
    if value is not None and type(value) is not bool:
        raise Invalid(key + ' must be a supplied Boolean finding or unknown')
    return value

def conjunction(*values):
    if False in values:
        return False
    return None if None in values else True

def number(f, key, unit_interval=False):
    value = f.get(key)
    if value is None:
        return None
    if type(value) not in (str, int):
        raise Invalid(key + ' requires an exact rational, not float/bool')
    try:
        q = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise Invalid(key + ' is not an exact rational')
    if q < 0 or (unit_interval and q > 1):
        raise Invalid(key + ' outside the declared domain')
    return q

def threshold(f):
    version = f.get('indenture')
    if version is None:
        return None
    if version not in ('2013', '2018'):
        raise Unsupported('No inspected rule for that indenture')
    return Fraction(25 if version == '2013' else 33, 100)

def authorized_notice(f):
    written = truth(f, 'written_notice')
    received = truth(f, 'required_recipients_received')
    valid = truth(f, 'notice_validity_established')
    actor = f.get('notice_actor')
    if actor == 'trustee':
        authority = True
    elif actor == 'holders':
        cut, share = threshold(f), number(f, 'holder_principal_fraction', True)
        authority = None if cut is None or share is None else share >= cut
    elif actor is None:
        authority = None
    else:
        raise Unsupported('Actor is outside the inspected notice routes')
    return conjunction(written, received, valid, authority)

def elapsed(f, key, limit):
    days = number(f, key)
    # No invented event order at the exact boundary in this dated abstraction.
    return None if days is None or days == limit else days > limit

def event_clause(f):
    kind = f.get('kind')
    applicable = truth(f, 'selected_clause_applicable')
    if kind in ('principal', 'premium'):
        value = conjunction(truth(f, 'due_and_payable'), truth(f, 'unpaid'))
    elif kind == 'interest':
        value = conjunction(truth(f, 'due_and_payable'),
                            truth(f, 'continuously_unpaid'), elapsed(f, 'days_after_due', 30))
    elif kind == 'covenant':
        value = conjunction(truth(f, 'eligible_covenant'), truth(f, 'breach_continuing'),
                            authorized_notice(f), elapsed(f, 'days_after_valid_notice', 90))
    elif kind == 'bankruptcy':
        # A finding about a specified legal event, not a ratio-based inference.
        value = truth(f, 'specified_qualifying_event_established')
    else:
        raise Unsupported('Uninspected default clause')
    return conjunction(applicable, value)

def new_acceleration(f):
    event = truth(f, 'event_occurs_and_continues')
    automatic = truth(f, 'specified_automatic_category')
    if automatic is True:
        route = True
    else:
        declaration = conjunction(truth(f, 'declaration_made'), authorized_notice(f))
        if automatic is False:
            route = declaration
        else:
            route = True if declaration is True else None
    return conjunction(truth(f, 'acceleration_rule_applicable'), event, route)

def after_rescission(f):
    existing = truth(f, 'existing_acceleration')
    consent = truth(f, 'requisite_majority_established')
    deposit = truth(f, 'required_deposit_established')
    cure = truth(f, 'all_relevant_events_cured_or_waived')
    other = truth(f, 'other_rescission_conditions_established')
    action = truth(f, 'rescission_effected')
    rescinded = conjunction(consent, deposit, cure, other, action)
    if existing is False:
        return False
    if rescinded is True:
        return False
    return conjunction(existing, None if rescinded is None else True)

def amendment_consent(f):
    if f.get('change') not in ('stated_maturity', 'principal', 'interest_rate',
                                'payment_currency', 'payment_suit_right',
                                'protected_vote_threshold', 'protected_conversion_right'):
        raise Unsupported('Other amendment routes require their own conditions')
    return conjunction(truth(f, 'protected_change_applies'),
                       truth(f, 'each_affected_holder_consented'))

def majority_waiver(f):
    excluded = truth(f, 'payment_or_individually_protected_default')
    permitted_kind = None if excluded is None else not excluded
    return conjunction(permitted_kind, truth(f, 'requisite_majority_established'),
                       truth(f, 'waiver_effected'), truth(f, 'other_waiver_conditions_established'))

def cross_series(f):
    # The source denies an automatic inference. It does not prove independence.
    return truth(f, 'target_series_event_established_from_own_terms')

METHODS = {'event_clause': event_clause, 'notice': authorized_notice,
           'new_acceleration': new_acceleration, 'after_rescission': after_rescission,
           'amendment_consent': amendment_consent, 'majority_waiver': majority_waiver,
           'cross_series': cross_series}

def evaluate(method, facts):
    try:
        result = METHODS[method](facts)
        return {True: 'satisfied', False: 'not_satisfied', None: 'unresolved'}[result]
    except Invalid:
        return 'invalid_input'
    except Unsupported:
        return 'unsupported'

def main():
    start = time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1', 'Run deliberately CPU-only'
    source_manifest = json.loads((SOURCE / 'manifest.json').read_text())
    checks = []
    def check(name, condition):
        checks.append({'id': name, 'passed': bool(condition)})
        assert condition, name
    def hashfile(p):
        return sha256(p.read_bytes()).hexdigest()
    check('retained_report_hash', hashfile(ROOT / source_manifest['source']) == source_manifest['sha256'])
    for page in source_manifest['extracted_pages']:
        check('page_text.' + str(page['pdf_page']), hashfile(ROOT / page['text']) == page['sha256'])
        if 'render' in page:
            check('page_render.' + str(page['pdf_page']), hashfile(ROOT / page['render']) == page['render_sha256'])
    cases = []
    def case(name, method, facts, expected, page, reason):
        original = deepcopy(facts)
        actual = evaluate(method, facts)
        check(name + '.classification', actual == expected)
        check(name + '.input_preserved', original == facts)
        cases.append({'id': name, 'method': method, 'facts': facts, 'expected': expected,
                      'actual': actual, 'pdf_pages': page, 'reason': reason,
                      'facts_are_hypothetical': True, 'actual_issuer_admission': False})
    principal = dict(kind='principal', selected_clause_applicable=True, due_and_payable=True, unpaid=True)
    interest = dict(kind='interest', selected_clause_applicable=True, due_and_payable=True, continuously_unpaid=True)
    notice = dict(written_notice=True, required_recipients_received=True, notice_validity_established=True,
                  notice_actor='holders', indenture='2013', holder_principal_fraction='1/4')
    cov = dict(notice, kind='covenant', selected_clause_applicable=True, eligible_covenant=True,
               breach_continuing=True, days_after_valid_notice=91)
    acc = dict(notice, acceleration_rule_applicable=True, event_occurs_and_continues=True,
               specified_automatic_category=False, declaration_made=True)
    resc = dict(existing_acceleration=True, requisite_majority_established=True,
                required_deposit_established=True, all_relevant_events_cured_or_waived=True,
                other_rescission_conditions_established=True, rescission_effected=True)
    case('principal_unpaid_due', 'event_clause', principal, 'satisfied', [69], 'Clause 2 has no imported interest grace interval.')
    case('premium_unpaid_due', 'event_clause', dict(principal, kind='premium'), 'satisfied', [69], 'Premium is separately included.')
    case('principal_not_due', 'event_clause', dict(principal, due_and_payable=False), 'not_satisfied', [69], 'This selected payment clause requires due status.')
    case('principal_due_unknown', 'event_clause', dict(principal, due_and_payable=None), 'unresolved', [69], 'An accounting date alone does not establish contractual due time.')
    case('principal_paid', 'event_clause', dict(principal, unpaid=False), 'not_satisfied', [69], 'Current clause only; history is retained separately.')
    case('actual_applicability_unknown', 'event_clause', dict(principal, selected_clause_applicable=None), 'unresolved', [63,69], 'Summary does not establish actual admission.')
    for days, expected in [(1,'not_satisfied'),(29,'not_satisfied'),(30,'unresolved'),(31,'satisfied')]:
        case('interest_day_' + str(days), 'event_clause', dict(interest, days_after_due=days), expected, [69], 'Exact boundary requires event ordering; interior case uses the supplied applicable clause.')
    case('interest_elapsed_unknown', 'event_clause', interest, 'unresolved', [69], 'Missing elapsed time is not zero.')
    case('interest_cured', 'event_clause', dict(interest, days_after_due=31, continuously_unpaid=False), 'not_satisfied', [69], 'The current continuous-payment-failure clause is unsatisfied; this does not erase a past event.')
    case('negative_elapsed_invalid', 'event_clause', dict(interest, days_after_due=-1), 'invalid_input', [69], 'Invalid interval is not evidence of no default.')
    case('floating_elapsed_invalid', 'event_clause', dict(interest, days_after_due=30.5), 'invalid_input', [69], 'The reference requires exact rational input.')
    case('covenant_2013_25_day91', 'event_clause', cov, 'satisfied', [69], 'Applicable 2013 threshold and notice period supplied.')
    case('covenant_2018_25_day91', 'event_clause', dict(cov, indenture='2018'), 'not_satisfied', [69], '25 percent is below this 33 percent threshold; no alternative trustee notice is assumed.')
    case('covenant_2018_33_day91', 'event_clause', dict(cov, indenture='2018', holder_principal_fraction='33/100'), 'satisfied', [69], 'At least 33 percent includes equality.')
    case('covenant_2013_below25', 'event_clause', dict(cov, holder_principal_fraction='249/1000'), 'not_satisfied', [69], 'Below-threshold holder route is not valid notice.')
    case('covenant_day89', 'event_clause', dict(cov, days_after_valid_notice=89), 'not_satisfied', [69], 'Notice period has not elapsed.')
    case('covenant_day90', 'event_clause', dict(cov, days_after_valid_notice=90), 'unresolved', [69], 'Day-level data cannot resolve boundary event order.')
    case('covenant_missing_notice', 'event_clause', dict(cov, written_notice=None), 'unresolved', [69], 'Missing evidence is not known absence.')
    case('covenant_known_no_notice', 'event_clause', dict(cov, written_notice=False), 'not_satisfied', [69], 'Known absence prevents this notice route.')
    case('covenant_wrong_recipients', 'event_clause', dict(cov, required_recipients_received=False), 'not_satisfied', [69], 'Delivery to the required recipients matters.')
    case('covenant_validity_unknown', 'event_clause', dict(cov, notice_validity_established=None), 'unresolved', [69], 'A text labelled notice is not an established valid notice.')
    case('covenant_series_mapping_unknown', 'event_clause', dict(cov, indenture=None), 'unresolved', [63,69], 'Do not choose the lower threshold.')
    case('covenant_trustee_route', 'event_clause', dict(cov, notice_actor='trustee', indenture=None, holder_principal_fraction=None), 'satisfied', [69], 'The supplied valid trustee notice does not require a holder threshold.')
    case('covenant_excluded_clause', 'event_clause', dict(cov, eligible_covenant=False), 'not_satisfied', [69], 'A separately treated or other-series covenant is excluded from this route.')
    case('covenant_unknown_clause_scope', 'event_clause', dict(cov, eligible_covenant=None), 'unresolved', [69], 'Clause scope must be established.')
    case('bad_fraction', 'notice', dict(notice, holder_principal_fraction='101/100'), 'invalid_input', [69], 'Outstanding-principal fraction cannot exceed one.')
    case('bad_boolean', 'notice', dict(notice, written_notice='yes'), 'invalid_input', [69], 'Strings do not become findings by truthiness.')
    case('unknown_indenture_edition', 'notice', dict(notice, indenture='2026'), 'unsupported', [63], 'No imported rule for an uninspected edition.')
    case('bankruptcy_ratio_not_finding', 'event_clause', dict(kind='bankruptcy', selected_clause_applicable=True, negative_equity=True), 'unresolved', [69,70], 'Balance-sheet distress does not establish a specified legal event.')
    case('bankruptcy_supplied_finding', 'event_clause', dict(kind='bankruptcy', selected_clause_applicable=True, specified_qualifying_event_established=True), 'satisfied', [69,70], 'Finding supplied conditionally; statutory tests are not implemented.')
    case('uninspected_clause', 'event_clause', dict(kind='other_series_specific', selected_clause_applicable=True), 'unsupported', [70], 'Other series-specific defaults remain open dependencies.')
    case('nonbankruptcy_declared', 'new_acceleration', acc, 'satisfied', [70], 'Continuing event plus valid declaration under the supplied rule.')
    case('nonbankruptcy_no_declaration', 'new_acceleration', dict(acc, declaration_made=False), 'not_satisfied', [70], 'An available right is not its exercise.')
    case('nonbankruptcy_unknown_declaration', 'new_acceleration', dict(acc, declaration_made=None), 'unresolved', [70], 'Missing declaration evidence cannot become no declaration.')
    case('acceleration_2018_below_threshold', 'new_acceleration', dict(acc, indenture='2018'), 'not_satisfied', [70], 'Holder authority is edition-specific here too.')
    case('acceleration_2018_at_threshold', 'new_acceleration', dict(acc, indenture='2018', holder_principal_fraction='33/100'), 'satisfied', [70], 'Equality satisfies the supplied threshold.')
    case('acceleration_event_cured', 'new_acceleration', dict(acc, event_occurs_and_continues=False), 'not_satisfied', [70], 'No new trigger from an event that no longer continues; existing acceleration has its own state.')
    case('automatic_qualified_event', 'new_acceleration', dict(acc, specified_automatic_category=True, declaration_made=False), 'satisfied', [70], 'The supplied specified automatic category does not require declaration.')
    case('automatic_without_notice_facts', 'new_acceleration', dict(acceleration_rule_applicable=True, event_occurs_and_continues=True, specified_automatic_category=True), 'satisfied', [70], 'An independently supplied automatic category does not require notice-route inputs.')
    case('automatic_ignores_unneeded_notice_edition', 'new_acceleration', dict(acc, specified_automatic_category=True, indenture='uninspected_notice_route'), 'satisfied', [70], 'A known applicable automatic rule does not evaluate an unused declaration route; applicability itself is still a supplied finding.')
    case('automatic_category_unknown', 'new_acceleration', dict(acc, specified_automatic_category=None, declaration_made=False), 'unresolved', [70], 'Do not map all distress into automatic acceleration.')
    case('rescission_complete', 'after_rescission', resc, 'not_satisfied', [70], 'Existing acceleration is removed only under the supplied complete rescission facts.')
    case('cure_without_rescission', 'after_rescission', dict(resc, rescission_effected=False), 'satisfied', [70], 'Cure alone does not undo an existing declaration.')
    case('rescission_deposit_missing', 'after_rescission', dict(resc, required_deposit_established=None), 'unresolved', [70], 'Required sums cannot be assumed deposited.')
    case('rescission_known_no_deposit', 'after_rescission', dict(resc, required_deposit_established=False), 'satisfied', [70], 'Incomplete conditions leave the existing state in this example.')
    case('amend_maturity_majority_only', 'amendment_consent', dict(change='stated_maturity', protected_change_applies=True, each_affected_holder_consented=False, majority_consented=True), 'not_satisfied', [71], 'A majority cannot substitute for each affected holder on this protected change.')
    case('amend_maturity_each_holder', 'amendment_consent', dict(change='stated_maturity', protected_change_applies=True, each_affected_holder_consented=True), 'satisfied', [71], 'Only this consent condition is checked, not the entire amendment.')
    case('amend_maturity_consent_unknown', 'amendment_consent', dict(change='stated_maturity', protected_change_applies=True), 'unresolved', [71], 'Absence of a vote record does not establish consent.')
    case('other_amendment_route', 'amendment_consent', dict(change='add_guarantee'), 'unsupported', [71,72], 'No-consent routes have different conditions; not universally forbidden.')
    waiver = dict(requisite_majority_established=True, waiver_effected=True, other_waiver_conditions_established=True)
    case('payment_default_majority_waiver', 'majority_waiver', dict(waiver, payment_or_individually_protected_default=True), 'not_satisfied', [72], 'General majority waiver excludes payment and individually protected defaults.')
    case('eligible_majority_waiver', 'majority_waiver', dict(waiver, payment_or_individually_protected_default=False), 'satisfied', [72], 'All supplied conditions apply only to this past default.')
    case('waiver_class_unknown', 'majority_waiver', waiver, 'unresolved', [72], 'Eligibility cannot be guessed.')
    case('other_series_unknown', 'cross_series', dict(first_series_event=True), 'unresolved', [70], 'Neither global default nor independence follows.')
    case('other_series_known_absent', 'cross_series', dict(first_series_event=True, target_series_event_established_from_own_terms=False), 'not_satisfied', [70], 'A separate supplied target-series finding permits this classification.')
    case('other_series_known_present', 'cross_series', dict(first_series_event=True, target_series_event_established_from_own_terms=True), 'satisfied', [70], 'An independently established target event may coexist.')
    # Illustrative wrong policies are compared with the independent expected table.
    by_id = {c['id']: c for c in cases}
    mutations = []
    for name, target, wrong in [
        ('interest_grace_for_principal','principal_unpaid_due','not_satisfied'),
        ('every_arrear_is_default','interest_day_1','satisfied'),
        ('unknown_notice_is_absent','covenant_missing_notice','not_satisfied'),
        ('one_threshold_for_both_indentures','covenant_2018_25_day91','satisfied'),
        ('event_implies_acceleration','nonbankruptcy_no_declaration','satisfied'),
        ('cure_erases_acceleration','cure_without_rescission','not_satisfied'),
        ('majority_can_change_maturity','amend_maturity_majority_only','satisfied'),
        ('majority_can_waive_payment','payment_default_majority_waiver','satisfied'),
        ('all_series_default_together','other_series_unknown','satisfied'),
        ('series_always_independent','other_series_unknown','not_satisfied'),
        ('arbitrary_boundary_order','interest_day_30','satisfied'),
        ('negative_equity_proves_bankruptcy','bankruptcy_ratio_not_finding','satisfied')]:
        detected = wrong != by_id[target]['expected']
        check('mutation.' + name, detected)
        mutations.append({'id':name,'case':target,'incorrect_result':wrong,'detected':detected,
                          'scope':'Contrary-policy output, not a mutation of an external legal engine'})
    check('unique_case_names', len(by_id) == len(cases))
    check('no_actual_issuer_admission', all(c['actual_issuer_admission'] is False for c in cases))
    result = {'status':'PASS','cases':cases,'mutations':mutations,'checks':checks,
              'scope':'Conditional selected-clause design reference; not complete legal admission or runtime integration',
              'unresolved_means':'Required facts or exact boundary order have not been established',
              'not_satisfied_means':'Only this selected clause/condition is unsatisfied under supplied facts'}
    (OUT/'contract-condition-results.json').write_text(json.dumps(result,indent=2)+chr(10))
    manifest = {'status':'PASS','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/gap-program-20261026/contract_conditions.py',
                'environment':{'python':sys.version,'platform':platform.platform(),'CUDA_VISIBLE_DEVICES':os.environ['CUDA_VISIBLE_DEVICES'],'gpu':'intentionally hidden; no GPU imports'},
                'git_commit':'unavailable: existing .git marker is unusable; preserved unchanged',
                'random_seeds':'N/A: exact deterministic cases','wall_seconds':time.monotonic()-start,
                'plan':'docs/plans/accounting-gap-program-20261026.md',
                'result':'data/accounting-master/gap-program-20261026/contract-conditions.md',
                'script_sha256':hashfile(Path(__file__)),
                'source_sha256':{source_manifest['source']:source_manifest['sha256'],str((SOURCE/'manifest.json').relative_to(ROOT)):hashfile(SOURCE/'manifest.json'),
                    'docs/design/cases/apple/manifest.json':hashfile(ROOT/'docs/design/cases/apple/manifest.json'),
                    'data/accounting-master/apple-2018-indenture-source-20261012/result.md':hashfile(ROOT/'data/accounting-master/apple-2018-indenture-source-20261012/result.md')},
                'results_sha256':hashfile(OUT/'contract-condition-results.json'),
                'cases':len(cases),'mutation_controls':len(mutations),'checks':len(checks)}
    (OUT/'contract-run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({k:manifest[k] for k in ['status','cases','mutation_controls','checks','wall_seconds']}))

if __name__ == '__main__':
    main()
