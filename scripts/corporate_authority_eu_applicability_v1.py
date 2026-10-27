"""Integrity checks for bounded EU applicability decisions, not legal approval."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from corporate_authority_eu_current import ROOT, REGISTER as PREPARATION, validate_disposition

REGISTER = 'docs/design/research/p08-v6/applicability-disposition.json'
ORIGINAL = 'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
ADDITIONAL = {'regulated_market_at_both_balance_sheet_dates': True,
              'ordinary_shares_have_no_cash_or_pro_rata_liquidation_obligation': True,
              'conversion_option_has_no_net_cash_settlement': True}
# Instrument identity is independent of free-form reasoning and source quotations.
EXPECTED = {
    'eu.adoption': ('Regulation (EU) 2023/1803', 'Article 1', 'conditional_adoption_basis'),
    'eu.entry_into_force': ('Regulation (EU) 2023/1803', 'Article 5', 'effective_before_both_periods'),
    'eu.reporting_scope': ('Regulation (EC) 1606/2002', 'Article 4', 'conditional_consolidated_reporting_scope'),
    'scope.date_correction': ('Corrigendum to Regulation (EU) 2023/1803, OJ L 239/39', 'Title and concluding formula', 'corrected_instrument_date'),
    'scope.2008_amendment': ('Regulation (EC) 297/2008', 'Articles 1 and 2', 'scope_unchanged_by_this_amendment'),
    'scope.2007_correction': ('Corrigendum to Regulation (EC) 1606/2002, OJ L 216/32 (Polish)', 'Correction item 3, Article 4', 'any_member_state_market'),
    'scope.2003_correction': ('Corrigendum 32002R1606R(01), OJ L 51/23 (Portuguese)', 'Recitals 7 and 9; Article 2', 'article_4_not_changed'),
    'eu.eligibility': ('Regulation (EU) 2023/1803 Annex, IAS 32', 'IAS 32.16', 'conditional_option_eligibility'),
    'eu.classification': ('Regulation (EU) 2023/1803 Annex, IAS 32', 'IAS 32.22', 'fixed_for_fixed_eligibility_only'),
    'eu.excluded_puttable': ('Regulation (EU) 2023/1803 Annex, IAS 32', 'IAS 32.22A', 'exception_not_triggered_on_assumptions'),
    'eu.group_terms': ('Regulation (EU) 2023/1803 Annex, IAS 32', 'IAS 32.AG29', 'conditional_group_terms_screen'),
    'eu.scope_equity': ('Regulation (EU) 2023/1803 Annex, IFRS 9', 'IFRS 9.2.1(d)', 'issuer_equity_exclusion_conditional'),
    **{'eligibility.settlement_' + str(n): ('Regulation (EU) 2023/1803 Annex, IAS 32', 'IAS 32.' + str(n), 'excluded_settlement_feature_absent') for n in (25, 26, 27)},
}
INSPECTIONS = {'scope.2008_amendment': 'scope-297-2008',
               'scope.2007_correction': 'scope-corr-2007',
               'scope.2003_correction': 'scope-corr-2003-portuguese'}
PENDING_GROUPS = {'classification_issuance', 'measurement_settlement_notes',
                  'actual_amendments_corrigenda', 'independent-applicability-review', 'eu-lifecycle'}
CLASSIFICATION = {'eu.compound_classification', 'eu.residual_equity', 'eu.initial_liability',
                  'eu.recognition', 'eu.initial_fair_value'}
EVENTS = {'issue', 'accrue-1', 'coupon-1', 'accrue-2', 'coupon-2', 'settlement:redeem', 'settlement:convert'}
NOTES = {'financing_carrying', 'financing_equity', 'financing_interest'}


def validate_applicability(root=ROOT, records=None):
    root = Path(root).resolve()
    preparation = validate_disposition(root)
    def local(name):
        if not isinstance(name, str) or not name:
            raise ValueError('invalid applicability source path')
        p = Path(name); target = root / p
        if p.is_absolute() or '..' in p.parts or p.as_posix() != name or target.is_symlink() or not target.resolve().is_relative_to(root):
            raise ValueError('unsafe applicability source path')
        return target
    def digest(name):
        return sha256(local(name).read_bytes()).hexdigest()
    d = json.loads(local(REGISTER).read_text()) if records is None else deepcopy(records)
    if d.get('schema_version') != 'accdsl.p08.eu_applicability.v1' or d.get('scope') != 'scope_eligibility_only':
        raise ValueError('applicability schema or scope')
    if d.get('admission_allowed') is not False or d.get('review_status') != 'independent_review_pending':
        raise ValueError('applicability cannot grant admission or review')
    if d.get('preparation') != {'path': PREPARATION, 'sha256': digest(PREPARATION)}:
        raise ValueError('stale preparation provenance')
    if d.get('reporting_context') != preparation['reporting_context'] or d.get('additional_assumptions') != ADDITIONAL:
        raise ValueError('contradictory reporting assumptions')
    if d.get('economics_sha256') != '3787c8a58c36667abf13eb0e2d0ebe972226b406509f339a0119fc0cdf256365':
        raise ValueError('changed economics')
    claims = {c['id']: c for c in preparation['claims']}
    inspections = {c['id']: c for c in preparation['inspections']}
    pins = {p['path']: p['sha256'] for p in preparation['source_pins']}
    def require_rows(rows, expected, label, key='id'):
        if not isinstance(rows, list) or len(rows) != len(expected) or {r[key] for r in rows} != set(expected):
            raise ValueError('missing or duplicate ' + label)
    require_rows(d.get('decisions'), EXPECTED, 'decisions')
    texts = {}
    for row in d['decisions']:
        cid = row['id']
        if tuple(row.get(k) for k in ('source_instrument', 'provision', 'decision')) != EXPECTED[cid]:
            raise ValueError('instrument/provision/decision mismatch: ' + cid)
        if row.get('group') != 'scope_eligibility' or row.get('periods') != ['2024', '2025']:
            raise ValueError('decision scope')
        assumptions = row.get('reporting_assumptions', [])
        if not assumptions or len(set(assumptions)) != len(assumptions) or not set(assumptions) <= preparation['reporting_context'].keys():
            raise ValueError('missing reporting assumption')
        for key in ('reasoning', 'transition_reasoning', 'operation_effect', 'unresolved_question'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('missing ' + key)
        dates = row.get('dates', {})
        if not {'publication', 'legal_effect', 'mandatory_application'} <= set(dates) or not dates.get('mandatory_application'):
            raise ValueError('missing effective/transition limits')
        if cid == 'eu.entry_into_force' and (dates['publication'], dates['legal_effect']) != ('2023-09-26', '2023-10-16'):
            raise ValueError('incorrect entry dates')
        if set(row.get('affected_events', [])) != EVENTS or set(row.get('affected_notes', [])) != NOTES:
            raise ValueError('missing affected operation/note dependencies')
        expected_kind = 'direct_issue_eligibility' if cid == 'eu.classification' else 'eligibility_dependency'
        if row.get('effect_kind') != expected_kind or set(row.get('dependencies', [])) != {'remaining-amendments', 'independent-applicability-review', 'eu-lifecycle'}:
            raise ValueError('missing eligibility/admission dependency')
        anchors = row.get('anchors', [])
        if not anchors:
            raise ValueError('missing primary anchor')
        # Existing primary anchors remain the baseline; supplementary passages may be added.
        prior = claims[cid]['anchor'] if cid in claims else inspections[INSPECTIONS[cid]]['anchors'][0] if cid in INSPECTIONS else None
        if prior and any(anchors[0].get(k) != v for k, v in prior.items()):
            raise ValueError('changed retained provision anchor')
        if cid.startswith('eligibility.settlement_') and (anchors[0].get('text'), anchors[0].get('paragraph'), anchors[0].get('pdf_page')) != (ORIGINAL, EXPECTED[cid][1], 214):
            raise ValueError('wrong settlement provision anchor')
        if cid == 'scope.date_correction' and anchors[0].get('text') != 'docs/design/research/p08-v3-preparation/eu-2023-1803-date-corrigendum.txt':
            raise ValueError('wrong date corrigendum')
        for a in anchors:
            name = a['text']
            if name not in pins or a.get('sha256') != pins[name] or a['sha256'] != digest(name):
                raise ValueError('stale source hash')
            if name not in texts:
                texts[name] = local(name).read_text()
            source = texts[name]
            if 'pdf_page' in a:
                pages = source.split('\f'); page = a['pdf_page']
                if type(page) is not int or not 1 <= page <= len(pages):
                    raise ValueError('invalid primary page')
                source = pages[page - 1]
            quote = a.get('quote', '')
            if not quote.strip() or ' '.join(quote.split()) not in ' '.join(source.split()):
                raise ValueError('altered primary quotation: ' + cid + ' ' + a.get('paragraph', ''))
    require_rows(d.get('coverage'), claims, 'coverage', 'claim_id')
    for c in d['coverage']:
        cid = c['claim_id']
        expected_status = 'eligibility_only_compound_pending' if cid == 'eu.classification' else 'conditional_decision_pending_review' if cid in EXPECTED else 'pending'
        group = 'scope_eligibility' if cid in EXPECTED else 'classification_issuance' if cid in CLASSIFICATION else 'actual_amendments_corrigenda' if cid.startswith('eu.amendment.') else 'measurement_settlement_notes'
        if (c.get('status'), c.get('group'), c.get('decision_id')) != (expected_status, group, cid if cid in EXPECTED else None):
            raise ValueError('premature or misassigned coverage')
    require_rows(d.get('unresolved_groups'), PENDING_GROUPS, 'unresolved groups')
    if any(not r.get('work', '').strip() for r in d['unresolved_groups']):
        raise ValueError('empty unresolved work')
    expected_relations = [r for r in preparation['relationships'] if any(r['object'].endswith('/L_' + s) for s in preparation['eea_citations'])]
    if d.get('eea_citations') != preparation['eea_citations'] or d.get('eea_relationships') != expected_relations or any(r['classification'] != 'citation' for r in d['eea_relationships']):
        raise ValueError('citation/amendment confusion')
    if not d.get('validation_boundary') or not d.get('eea_decision'):
        raise ValueError('missing evidence limits')
    return d
