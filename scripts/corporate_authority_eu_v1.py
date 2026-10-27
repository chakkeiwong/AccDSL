"""Inspected EU source preparation; deliberately does not admit accounting treatment.

This validates evidence integrity and reports exact admission dependencies. The
original provisions alone cannot establish the complete applicable edition.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
REGISTER = 'docs/design/research/p08-v3/authority-register.json'
CLAIMS = frozenset('eu.' + x for x in (
    'adoption', 'entry_into_force', 'classification', 'compound_classification',
    'residual_equity', 'initial_liability', 'maturity_conversion', 'recognition',
    'cash_extinguishment', 'settlement_difference', 'subsequent_measurement',
    'initial_fair_value', 'amortised_cost', 'effective_interest', 'note_carrying',
    'note_interest', 'eligibility', 'excluded_puttable', 'scope_equity',
    'group_terms', 'no_conversion_gain', 'reporting_scope'))


class AuthorityDependencyError(ValueError):
    pass


class EUAuthorityPreparation:
    def __init__(self, root=ROOT, records=None):
        self.root = Path(root)
        self.records = deepcopy(records) if records is not None else json.loads(
            (self.root / REGISTER).read_text())
        self.validate()

    def path(self, value):
        p = Path(value)
        resolved = (self.root / p).resolve()
        if p.is_absolute() or '..' in p.parts or not resolved.is_relative_to(self.root.resolve()):
            raise AuthorityDependencyError('unsafe EU source path')
        return resolved

    def validate(self):
        d = self.records
        # The immutable source dossier is the reviewed input, not mutable caller flags.
        retained = json.loads((self.root / REGISTER).read_text())
        if d != retained:
            raise AuthorityDependencyError('EU preparation differs from retained inspection')
        if d.get('schema_version') != 'accdsl.p08.eu_authority_preparation.v1':
            raise AuthorityDependencyError('EU preparation schema')
        if d.get('admission_allowed') is not False or d.get('status') != 'prepared_unadmitted':
            raise AuthorityDependencyError('EU source preparation cannot grant admission')
        pins = d['source_pins']
        names = [p['path'] for p in pins]
        if len(names) != len(set(names)):
            raise AuthorityDependencyError('duplicate EU source pin')
        for pin in pins:
            try:
                actual = sha256(self.path(pin['path']).read_bytes()).hexdigest()
            except OSError as exc:
                raise AuthorityDependencyError('missing EU source') from exc
            if actual != pin['sha256']:
                raise AuthorityDependencyError('stale EU source hash')
        claims = d['claims']
        ids = [c['id'] for c in claims]
        if len(ids) != len(set(ids)) or not CLAIMS <= set(ids) or any(not x.startswith('eu.') for x in ids):
            raise AuthorityDependencyError('missing or mixed EU claim namespace')
        anchors = [c['anchor'] for c in claims] + [m['anchor'] for m in d['amendment_matrix']]
        anchors.append(d['corrected_regulation_date']['anchor'])
        texts = {}
        for a in anchors:
            if a['text'] not in names or not a['paragraph'] or not a['quote'].strip():
                raise AuthorityDependencyError('unpinned or empty EU anchor')
            if a['text'] not in texts:
                texts[a['text']] = self.path(a['text']).read_text().split('\f')
            pages = texts[a['text']]
            n = a['pdf_page']
            if type(n) is not int or not 1 <= n <= len(pages):
                raise AuthorityDependencyError('invalid EU anchor page')
            if ' '.join(a['quote'].split()) not in ' '.join(pages[n-1].split()):
                raise AuthorityDependencyError('unresolved EU quote')
        if {m['document'] for m in d['amendment_matrix']} != {'202302468','202302579','202302822','202401317'}:
            raise AuthorityDependencyError('incomplete retained amendment inspection')
        for links in list(d['operation_dependencies'].values()) + list(d['note_links'].values()):
            if not links or not set(links) <= set(ids):
                raise AuthorityDependencyError('EU operation/note claim dependency')
        blockers = {m['id'] for m in d['missing_authority'] if m['role'] == 'promotion_veto'}
        if not blockers or any(e['status'] != 'unresolved' or set(e['blocking_ids']) != blockers
                               for e in d['event_applicability']):
            raise AuthorityDependencyError('EU applicability omits unresolved authority')
        return True

    def require_admitted(self, contract):
        self.validate()
        from corporate_authority_eu_recovery_v1 import validate_recovery
        try:
            recovery = validate_recovery(self.root)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            raise AuthorityDependencyError('invalid EU source recovery: ' + str(exc)) from exc
        context = self.records['reporting_context']
        for key in ('basis','jurisdiction','tier','entity_scope','book'):
            if getattr(contract, key) != context[key]:
                raise AuthorityDependencyError('EU reporting context mismatch: ' + key)
        if contract.issue_date != '2024-01-01' or contract.years != 2:
            raise AuthorityDependencyError('EU preparation covers only 2024–2025')
        raise AuthorityDependencyError('EU applicable authority uninspected or unresolved: ' + '; '.join(recovery['open_dependencies']))
