#!/usr/bin/env python3
"""Challenge the bounded debt validator using schema-valid semantic defects."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import jsonschema

from core_semantics import Invalid, strict_json, validate

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'docs/design'


def main():
    started = time.monotonic()
    inputs = [D/'fixtures/core-ir-demo.json', D/'fixtures/core-demo-registry.json',
              D/'spec/core-ir.schema.json']
    document, registry, schema = [strict_json(p.read_text()) for p in inputs]
    jsonschema.Draft202012Validator.check_schema(schema)
    structural = jsonschema.Draft202012Validator(schema)
    checks = []

    def node(d, section, identifier):
        return next(r for r in d[section] if r['id'] == identifier)

    def field(section, identifier, key, value):
        return lambda d, r: node(d, section, identifier).__setitem__(key, value)

    def negative(name, expected, change):
        d, r = deepcopy(document), deepcopy(registry)
        change(d, r)
        structural.validate(d)  # A structural failure must not masquerade as a semantic test.
        try:
            validate(d, r, schema, ROOT)
        except Invalid as exc:
            if exc.code != expected:
                raise AssertionError(f'{name}: expected {expected}, got {exc}') from exc
            checks.append(dict(name=name, kind='schema_valid_negative', expected=expected,
                               observed=exc.code, location=exc.location, passed=True))
        else:
            raise AssertionError(f'{name}: invalid input was accepted')

    def positive(name, change=lambda d, r: None):
        d, r = deepcopy(document), deepcopy(registry)
        change(d, r)
        result = validate(d, r, schema, ROOT)
        assert result['status'] == 'passed' and not result['coverage_claims_verified']
        checks.append(dict(name=name, kind='positive', passed=True, result=result))

    positive('authored_fixture')

    def reorder(d, r):
        for values in d.values():
            if isinstance(values, list):
                values.reverse()
        r['records'].reverse()

    positive('record_and_export_order_independent', reorder)
    positive('system_cutoff_at_exact_availability',
             field('evidenceViews', 'synthetic-2025-exact', 'system_as_of', '2026-01-01T00:00:00Z'))
    positive('equivalent_offset_timestamp',
             field('documents', 'synthetic-note-document', 'available', '2025-12-31T19:00:00-05:00'))

    def other_stress(d, r):
        node(d, 'expressions', 'rate.stress')['rational'] = dict(n='9', d='100')
        node(d, 'assumptions', 'admission.rateShock')['rationale'] = 'Illustrative 9% constant annual simple stress'

    positive('another_documented_nonnegative_stress', other_stress)

    negative('original_real_slot_limit', 'SlotLimitType',
             lambda d, r: d['modelScopes'][0]['slot_limits'][0].__setitem__('expression', 'one'))
    negative('unknown_reference', 'UnknownReference', field('expressions', 'alpha.ref', 'target', 'absent'))
    negative('wrong_reference_kind', 'ReferenceKind', field('expressions', 'alpha.ref', 'target', 'Local'))
    negative('duplicate_identifier', 'DuplicateID', lambda d, r: d['accounts'].append(deepcopy(d['accounts'][0])))
    negative('expression_self_cycle', 'ExpressionCycle', field('expressions', 'alpha.ref', 'target', 'alpha.ref'))
    negative('comparison_missing_operand', 'ArityMismatch', field('expressions', 'is.fixed', 'args', ['alpha.ref']))
    negative('unused_literal_payload', 'ExpressionPayload', field('expressions', 'is.fixed', 'text', 'extra'))
    negative('implicit_money_cast', 'ContractType', field('expressions', 'rate.fixed', 'type', 'Money<USD>'))
    negative('declared_currency_disagrees_with_context', 'TypeMismatch', field('expressions', 'debt.value', 'type', 'Money<EUR>'))
    negative('fractional_slot_count', 'TypeMismatch', field('expressions', 'slot.one', 'rational', dict(n='1', d='2')))
    negative('unreduced_rational', 'NoncanonicalRational', field('expressions', 'rate.fixed', 'rational', dict(n='2', d='40')))
    negative('negative_zero', 'NoncanonicalRational', field('expressions', 'zero', 'rational', dict(n='-0', d='1')))
    negative('impossible_gregorian_date', 'InvalidDate',
             lambda d, r: d['contexts'][0]['time'].__setitem__('start', '2025-02-30'))
    negative('empty_period', 'InvalidPeriod',
             lambda d, r: d['assumptions'][0]['valid'].__setitem__('end_exclusive', '2026-01-01'))
    negative('timezone_missing', 'MissingTimezone', field('documents', 'synthetic-note-document', 'available', '2026-01-01T00:00:00'))
    negative('reversed_domain', 'InvalidDomain', lambda d, r: d['symbols'][0]['domain'].__setitem__('lower', dict(n='2', d='1')))
    negative('empty_open_interval', 'InvalidDomain',
             lambda d, r: d['symbols'][0]['domain'].update(upper=dict(n='0', d='1'), lower_closed=False))
    negative('invented_admitted_value', 'ReadingValueMismatch',
             lambda d, r: d['observations'][0]['domain'].update(lower=dict(n='101', d='1'), upper=dict(n='101', d='1')))
    negative('invented_source_context', 'ReadingContextMismatch', field('contexts', 'debt-context', 'perimeter', 'OtherGroup'))
    negative('changed_source_literal', 'SourceLiteralMismatch', field('sourceSpans', 'synthetic-note-7', 'literal', 'Debt 101'))
    negative('changed_source_digest', 'SourceDigestMismatch', field('documents', 'synthetic-note-document', 'sha256', '0' * 64))
    negative('source_locator_mismatch', 'SourceLocatorMismatch', field('sourceSpans', 'synthetic-note-7', 'locator', 'fixture:wrong'))
    negative('source_evidence_absent', 'AdmissionEvidence', field('reviewDecisions', 'demo-review-1', 'evidence', []))
    negative('duplicate_dimension', 'DuplicateDimension', field('contexts', 'debt-context', 'dimensions', [dict(axis='region', member='A')] * 2))
    negative('money_unit_mismatch', 'ContextMismatch', field('contexts', 'debt-context', 'unit', 'EUR'))
    negative('wrong_book_currency', 'BookCurrency', field('books', 'Local', 'currency', 'EUR'))
    negative('assumption_reason_absent', 'MissingAssumptionReason', field('assumptions', 'admission.allFixed', 'rationale', ' '))
    negative('unearned_default_status', 'UnprovedDefaultReview', field('assumptions', 'admission.allFixed', 'role', 'ReviewedDefault'))
    negative('assumption_expires_before_horizon', 'AssumptionValidity',
             lambda d, r: d['assumptions'][0]['valid'].__setitem__('end_exclusive', '2026-07-01'))
    negative('future_assumption_information', 'FutureAssumption', field('assumptions', 'admission.allFixed', 'information_cutoff', '2026-01-02T00:00:00Z'))
    negative('conditional_provenance_absent', 'MissingAssumption',
             lambda d, r: d.__setitem__('assumptions', [a for a in d['assumptions'] if a['id'] != 'admission.allFixed']))
    negative('stress_provenance_absent', 'MissingAssumption',
             lambda d, r: d.__setitem__('assumptions', [a for a in d['assumptions'] if a['id'] != 'admission.rateShock']))
    negative('contract_rate_provenance_absent', 'MissingAssumption',
             lambda d, r: d.__setitem__('assumptions', [a for a in d['assumptions'] if a['id'] != 'admission.loans']))
    negative('future_public_evidence', 'FutureEvidence', field('documents', 'synthetic-note-document', 'available', '2026-01-02T00:00:00Z'))

    def future_system(d, r):
        d['evidenceViews'][0]['system_as_of'] = '2026-01-01T00:00:00Z'
        d['documents'][0]['ingested'] = '2026-01-02T00:00:00Z'

    negative('future_ingestion', 'FutureIngestion', future_system)

    def future_review(d, r):
        d['evidenceViews'][0]['system_as_of'] = '2026-01-01T00:00:00Z'
        d['reviewDecisions'][0]['date'] = '2026-01-02T00:00:00Z'

    negative('future_system_review', 'FutureReview', future_review)
    negative('view_omits_source', 'ViewMembership', field('evidenceViews', 'synthetic-2025-exact', 'documents', []))
    negative('view_omits_acceptance', 'ViewMembership', field('evidenceViews', 'synthetic-2025-exact', 'decisions', []))
    negative('view_omits_used_observation', 'ViewMembership', field('evidenceViews', 'synthetic-2025-exact', 'observations', []))
    negative('reviewer_reason_absent', 'MissingReviewReason', field('reviewDecisions', 'demo-review-1', 'reason', ''))
    negative('alternative_author_absent', 'MissingAlternativeReason', field('alternatives', 'allFixed', 'author', ''))
    negative('alternative_uses_other_condition', 'AlternativeScope', field('alternatives', 'allFixed', 'constraints', ['condition.floating']))
    negative('unbalanced_opening', 'UnbalancedState', lambda d, r: d['states'][0]['balances'][0].__setitem__('signed_amount', dict(n='96', d='1')))
    negative('duplicate_balance', 'DuplicateBalance', lambda d, r: d['states'][0]['balances'].append(deepcopy(d['states'][0]['balances'][0])))
    negative('omitted_explicit_zero', 'IncompleteState', lambda d, r: d['states'][0]['balances'].pop())

    def cross_book(d, r):
        book = deepcopy(d['books'][0]); book['id'] = 'OtherBook'; d['books'].append(book)
        d['accounts'][0]['book'] = 'OtherBook'

    negative('cross_book_balance', 'StateBook', cross_book)

    def balanced_but_wrong_opening(d, r):
        d['states'][0]['balances'][0]['signed_amount'] = dict(n='96', d='1')
        d['states'][0]['balances'][2]['signed_amount'] = dict(n='4', d='1')

    negative('balanced_but_wrong_opening', 'OpeningStateMismatch', balanced_but_wrong_opening)
    negative('opening_omits_active_contract', 'OpeningStateMismatch', field('states', 'after-2025-close', 'contracts', []))
    negative('wrong_account_role', 'AccountMapping', field('accounts', 'Debt', 'role', 'Asset'))
    def other_entity(d, r):
        d['entities'].append(dict(id='OtherIssuer', functional_currency='USD'))
        d['books'][0]['entity'] = 'OtherIssuer'
    negative('contract_uses_other_issuer_evidence', 'ContractContext', other_entity)
    negative('negative_interest_rate', 'ContractDomain', field('expressions', 'rate.fixed', 'rational', dict(n='-1', d='20')))
    negative('negative_reset_rate', 'ContractDomain', field('expressions', 'rate.stress', 'rational', dict(n='-1', d='100')))

    def excess_fraction(d, r):
        node(d, 'expressions', 'one')['rational'] = dict(n='2', d='1')
        d['contracts'][0]['fields'][1]['expression'] = 'one'

    negative('share_exceeds_one', 'ContractDomain', excess_fraction)
    negative('repeated_contract_field', 'ContractFields', lambda d, r: d['contracts'][0]['fields'].append(deepcopy(d['contracts'][0]['fields'][0])))
    negative('stale_package_digest', 'PackageDigestMismatch', field('packages', 'DemoDebt@1', 'digest', '0' * 64))
    negative('unearned_accounting_review', 'UnprovedDomainReview', field('packages', 'DemoDebt@1', 'review_status', 'domain_reviewed'))
    negative('package_expires_before_horizon', 'PackageValidity', lambda d, r: d['packages'][0]['effective'].__setitem__('end_exclusive', '2026-07-01'))
    negative('missing_export', 'MissingExport', lambda d, r: r['records'].pop())
    negative('stale_external_digest', 'StaleArtifact', lambda d, r: r['records'][0].__setitem__('sha256', '0' * 64))
    negative('rebound_export_pointer', 'RegistryBinding', lambda d, r: r['records'][-1].__setitem__('pointer', '/rounded'))
    negative('false_exact_coverage', 'FalseCoverage', field('historyFamilies', 'BorrowingFamily', 'unresolved_cells', 1))
    negative('exact_without_completed_cell', 'FalseCoverage', field('historyFamilies', 'BorrowingFamily', 'completed_cells', 0))
    negative('feasible_without_witness', 'MissingWitness', field('historyFamilies', 'BorrowingFamily', 'witnesses', []))
    negative('family_omits_shared_symbol', 'FamilyMembership', field('historyFamilies', 'BorrowingFamily', 'symbols', []))
    negative('model_omits_declarations', 'ModelMembership', field('models', 'BorrowingExample@1', 'declarations', []))
    negative('model_omits_package_lock', 'ModelMembership', field('models', 'BorrowingExample@1', 'package_lock', []))
    negative('wrong_report_close', 'ReportPolicy', field('reportMappings', 'statements', 'closing_policy', 'DemoDebt@1/reset'))
    negative('unsupported_scenario', 'UnsupportedScenario', field('scenarios', 'rateShock', 'kind', 'StructuralIntervention'))
    negative('unsupported_expression', 'UnsupportedExpression', field('expressions', 'is.fixed', 'op', 'multiply'))
    negative('unsupported_admission', 'UnsupportedAdmission', field('symbols', 'alpha', 'uncertainty_kind', 'FutureInnovation'))
    negative('unsupported_populated_section', 'UnsupportedSection', lambda d, r: d['measurements'].append(dict(
        id='unsupported.measure', value_expression='one', basis='DemoDebt@1', date='2026-01-01',
        information_view='synthetic-2025-exact', method='fixed', numerical_status='exact', error=None, provenance=[])))

    for name, text, expected in [('duplicate_json_key', '{"amount": 100, "amount": 101}', 'DuplicateJSONKey'),
                                 ('nonfinite_json_value', '{"amount": NaN}', 'InvalidJSONNumber')]:
        try:
            strict_json(text)
        except Invalid as exc:
            assert exc.code == expected
            checks.append(dict(name=name, kind='json_boundary', expected=expected, observed=exc.code, passed=True))
        else:
            raise AssertionError(name)

    files = inputs + [Path(__file__), ROOT/'scripts/core_semantics.py', ROOT/'scripts/build_demo_registry.py',
                      ROOT/'scripts/build_core_contract.py', D/'fixtures/demo-debt-package.json', D/'fixtures/borrowings.json']
    report = dict(status='passed', checks=checks, count=len(checks),
                  counts={k: sum(c['kind'] == k for c in checks) for k in ['positive', 'schema_valid_negative', 'json_boundary']},
                  command='python3 scripts/check_semantic_preparation.py',
                  timestamp_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-started,
                  scope='Authored debt profile only; structural admission is checked separately before every semantic rejection.',
                  not_established=['Full language/compiler conformance', 'Runtime execution', 'Independent accounting review',
                                   'Historical family coverage proof', 'Real-filing source truth or completeness'],
                  sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    out = D/'review/semantic-preparation-checks.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['status', 'count', 'counts', 'wall_seconds']}))


if __name__ == '__main__':
    main()
