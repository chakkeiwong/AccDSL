"""Selected issuer disclosures as reported measurements, never company opening."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import temporal_measurement_constraints_v1 as temporal

# These roles follow the inspected PDF table, not generic tag names alone.
ROLES = [
    ('f-942', 'principal', 'DebtInstrumentCarryingAmount', 'Total term debt principal', 1),
    ('f-944', 'unamortized_deduction', 'DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet', 'Unamortized premium/(discount) and issuance costs, net', -1),
    ('f-946', 'hedge_deduction', 'HedgeAccountingAdjustmentsRelatedToLongTermDebt', 'Hedge accounting fair value adjustments', -1),
    ('f-948', 'carrying', 'LongTermDebt', 'Total term debt', 1),
    ('f-950', 'current_carrying', 'LongTermDebtCurrent', 'Less: Current portion of term debt', -1),
    ('f-952', 'noncurrent_carrying', 'LongTermDebtNoncurrent', 'Total non-current portion of term debt', 1),
    ('f-955', 'principal_bucket_2025', 'LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths', '2025', 1),
    ('f-956', 'principal_bucket_2026', 'LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo', '2026', 1),
    ('f-957', 'principal_bucket_2027', 'LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree', '2027', 1),
    ('f-958', 'principal_bucket_2028', 'LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour', '2028', 1),
    ('f-959', 'principal_bucket_2029', 'LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive', '2029', 1),
    ('f-960', 'principal_bucket_thereafter', 'LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive', 'Thereafter', 1),
    ('f-961', 'principal', 'DebtInstrumentCarryingAmount', 'Total term debt principal', 1),
]
VALUE_TYPE = dict(kind='rational',
    context=dict(issuer_cik='0000320193', perimeter='reported_consolidated',
                 basis='Apple2024_as_reported', value_layer='displayed_reported_quantity'),
    dimensions={'currency:USD': 1}, scale='1000000/1')


def identity(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def need(test, why):
    if not test:
        raise ValueError(why)


def rational(value):
    q = Q(value)
    return f'{q.numerator}/{q.denominator}'


def premise(key, meaning):
    return dict(id=key, status='proposed', meaning=meaning)


def point(amount):
    return dict(lower=rational(amount), upper=rational(amount),
                lower_inclusive=True, upper_inclusive=True)


def construct(debt, timing, issuance, expected_identities, *, cutoff=None):
    """An audit-only reading; unknown availability cannot become as-of admission."""
    for key, value in [('debt', debt), ('timing', timing), ('issuance', issuance)]:
        need(identity(value) == expected_identities[key], 'input_identity:' + key)
    need(debt['issuer'] == 'Apple Inc.' and debt['as_of'] == '2024-09-28', 'issuer_date')
    need(debt['unit'] == 'reported USD million', 'reported_unit')
    need(debt['source_admission'] is False and debt['accounting_admission'] is False, 'unreviewed_admission')
    ns = {'x': 'http://www.xbrl.org/2003/instance'}
    context = E.fromstring(debt['context'])
    need(context.attrib == {'id': 'c-21'}, 'context_identity')
    identifier = context.find('x:entity/x:identifier', ns)
    need(identifier.text == '0000320193' and identifier.get('scheme') == 'http://www.sec.gov/CIK', 'source_entity')
    need(context.find('x:period/x:instant', ns).text == debt['as_of'], 'source_instant')
    need(context.find('x:entity/x:segment', ns) is None and context.find('x:scenario', ns) is None, 'context_dimensions')
    records = debt['facts']
    by_id = {f['id']: f for f in records}
    need(len(records) == len(by_id) == len(ROLES), 'fact_population')
    need(set(by_id) == {r[0] for r in ROLES}, 'fact_identities')
    need(timing['profile'] == 'RetainedIssuerTimingEvidence/1', 'timing_profile')
    need(timing['issuer'] == debt['issuer'], 'timing_issuer')
    source = issuance['source']
    need(source['binding']['archive_sha256'] == timing['xbrl_binding']['sha256'], 'archive_link')
    need(source['binding']['instance_sha256'] == debt['instance_sha256'], 'instance_link')
    need(source['issuer_identifier'] == '0000320193' and source['unit'] == 'USD', 'issuance_context')
    need(source['fact_id'] == 'f-325' and source['concept'] == '{http://fasb.org/us-gaap/2024}ProceedsFromIssuanceOfLongTermDebt', 'issuance_meaning')
    need(source['decimals'] == '-6' and source['reported_literal'] == '0', 'issuance_display')
    observations, provenance = {}, {}
    instant = dict(kind='instant', at=debt['as_of'])
    for occurrence, quantity, tag, caption, sign in ROLES:
        fact = by_id[occurrence]
        namespace = 'http://www.apple.com/20240928' if occurrence == 'f-946' else 'http://fasb.org/us-gaap/2024'
        need(fact['concept'] == '{' + namespace + '}' + tag, 'fact_concept:' + occurrence)
        need(fact['pdf_caption'] == caption and fact['pdf_reconciliation_sign'] == sign, 'financial_role:' + occurrence)
        need(fact['context'] == 'c-21' and fact['decimals'] == '-6', 'fact_context_precision:' + occurrence)
        need(Q(fact['reported_usd']) / 1000000 == Q(fact['reported_usd_million']), 'fact_scale:' + occurrence)
        amount = rational(fact['reported_usd_million'])
        if quantity in observations:
            need(observations[quantity]['interval'] == point(amount), 'duplicate_quantity_conflict')
        else:
            observations[quantity] = dict(
                type=dict(value_type=deepcopy(VALUE_TYPE), time=deepcopy(instant), quantity=quantity),
                interval=point(amount), interval_premise=premise('reported.' + quantity,
                    'Exact displayed quantity only; no assertion of exact unrounded economic amount.'),
                source_ref='retained-debt-card-sha256:' + expected_identities['debt'] + '#' + quantity)
        provenance.setdefault(quantity, []).append(deepcopy(fact))
    def relation(key, terms, meaning):
        return dict(id=key, kind='same_time',
                    terms=[dict(observation=q, coefficient=rational(a)) for q, a in terms],
                    rhs='0/1', identity_premise=premise('reported.identity.' + key, meaning))
    relations = [
        relation('principal_to_carrying', [('principal', 1), ('unamortized_deduction', -1),
                 ('hedge_deduction', -1), ('carrying', -1)],
                 'Inspected Note9 displayed principal less both adjustments equals total carrying debt.'),
        relation('current_noncurrent', [('current_carrying', 1), ('noncurrent_carrying', 1), ('carrying', -1)],
                 'Inspected Note9 displayed current and noncurrent carrying values partition total carrying debt.'),
        relation('principal_allocation', [(q, 1) for q in observations if q.startswith('principal_bucket_')] + [('principal', -1)],
                 'Inspected Note9 maturity classifications sum to displayed principal at the reporting instant; they are not realized future cash flows.')]
    definition = dict(profile=temporal.PROFILE, observations=observations, relations=relations)
    period = source['period']
    issuance_time = dict(kind='period', start=period['startDate'],
        end_exclusive=(date.fromisoformat(period['endDate']) + timedelta(days=1)).isoformat())
    independent = dict(type=dict(value_type=deepcopy(VALUE_TYPE), time=issuance_time,
                                quantity='reported_term_debt_issuance_proceeds_net'),
        interval=point(Q(source['reported_literal']) / 1000000),
        interval_premise=premise('reported.issuance', 'Selected reported-value reading only; the original dash and proposed rounding alternative remain in the source card.'),
        source_ref='retained-issuance-card-sha256:' + expected_identities['issuance'] + '#f-325')
    temporal.measurement_type(independent['type'])
    if cutoff is not None:
        need(type(cutoff) is str and date.fromisoformat(cutoff).isoformat() == cutoff, 'cutoff')
    return dict(profile='RetainedDebtMeasurementConstruction/1',
        status='historical_information_unresolved' if cutoff is not None else 'conditional_reported_measurements',
        definition=definition, source_mapping=provenance, independent_issuance=independent,
        independent_issuance_relation=None, source_cards=dict(debt=deepcopy(debt), timing=deepcopy(timing), issuance=deepcopy(issuance)),
        input_identities=deepcopy(expected_identities), requested_cutoff=cutoff,
        historical_information='unresolved; documented clock meanings and exact-byte access are absent',
        value_scope='displayed reported quantities, not latent exact economic amounts',
        exact_economic_zero=False, source_admission=False, accounting_admission=False,
        actual_actor_knowledge=False, forecast_admission=False, executable_opening=None,
        probability_model=None, policy_input=None,
        actual_history='unknown', unresolved=list(debt['missing']),
        remaining='Instrument/payment populations and accounting-history bindings require supporting evidence; no actual-company transition follows from these reported totals.')
